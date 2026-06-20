from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

try:
    from utils import FEATURE_COLUMNS, clean_health_data
except ImportError:  # pragma: no cover - supports package execution
    from .utils import FEATURE_COLUMNS, clean_health_data


STD_FLOORS = {
    "heart_rate": 3.0,
    "resting_heart_rate": 2.0,
    "hrv": 4.0,
    "sleep_hours": 0.4,
    "sleep_score": 5.0,
    "steps": 1000.0,
    "active_minutes": 8.0,
    "calories_burned": 150.0,
    "spo2": 0.8,
    "respiratory_rate": 1.0,
    "stress_level": 6.0,
    "body_temperature": 0.15,
}


def _clip(value: Any, low: float = 0.0, high: float = 100.0) -> Any:
    return np.clip(value, low, high)


def _safe_std(series: pd.Series, column: str) -> float:
    std = float(pd.to_numeric(series, errors="coerce").std(ddof=0))
    if np.isnan(std) or std < STD_FLOORS[column]:
        return STD_FLOORS[column]
    return std


def build_personal_baseline(df: pd.DataFrame) -> dict[str, float]:
    baseline: dict[str, float] = {}
    for column in FEATURE_COLUMNS:
        baseline[f"{column}_mean"] = float(df[column].mean())
        baseline[f"{column}_std"] = _safe_std(df[column], column)
    return baseline


def _zscore(series: pd.Series, baseline: dict[str, float], column: str) -> pd.Series:
    return (series - baseline[f"{column}_mean"]) / baseline[f"{column}_std"]


def enrich_with_intelligence(
    df: pd.DataFrame,
    user_id: str | None = None,
    baseline_fraction: float = 0.8,
) -> tuple[pd.DataFrame, dict[str, float]]:
    """Create personalized health scores using the selected user's own baseline."""
    cleaned = clean_health_data(df, require_targets=False)
    if user_id is None:
        user_id = str(cleaned["user_id"].iloc[0])

    user_df = cleaned[cleaned["user_id"].astype(str) == str(user_id)].copy()
    if user_df.empty:
        raise ValueError(f"No rows found for user_id={user_id}")

    user_df = user_df.sort_values("date").reset_index(drop=True)
    baseline_count = max(7, int(len(user_df) * baseline_fraction))
    if len(user_df) <= 8:
        baseline_source = user_df
    else:
        baseline_source = user_df.iloc[: min(baseline_count, len(user_df) - 1)]

    baseline = build_personal_baseline(baseline_source)
    baseline["baseline_days"] = float(len(baseline_source))
    baseline["analysis_days"] = float(max(0, len(user_df) - len(baseline_source)))

    hrv_z = _zscore(user_df["hrv"], baseline, "hrv")
    sleep_z = _zscore(user_df["sleep_hours"], baseline, "sleep_hours")
    heart_z = _zscore(user_df["heart_rate"], baseline, "heart_rate")
    resting_z = _zscore(user_df["resting_heart_rate"], baseline, "resting_heart_rate")
    steps_z = _zscore(user_df["steps"], baseline, "steps")
    active_z = _zscore(user_df["active_minutes"], baseline, "active_minutes")
    temp_delta = (user_df["body_temperature"] - baseline["body_temperature_mean"]).abs()

    sleep_component = _clip(0.65 * user_df["sleep_score"] + 0.35 * (user_df["sleep_hours"] / 8.0) * 100)
    hrv_component = _clip(55 + hrv_z * 18)
    activity_component = _clip(92 - (steps_z.abs() * 9 + active_z.abs() * 6))
    spo2_component = _clip((user_df["spo2"] - 92) / 6 * 100)
    calm_component = _clip(100 - user_df["stress_level"])
    resting_penalty = _clip(resting_z, 0, 4) * 4.0
    temperature_penalty = _clip((temp_delta - 0.25) * 18, 0, 18)

    recovery_score = (
        0.28 * sleep_component
        + 0.25 * hrv_component
        + 0.17 * activity_component
        + 0.15 * spo2_component
        + 0.15 * calm_component
        - resting_penalty
        - temperature_penalty
    )

    stress_index = _clip(
        0.45 * user_df["stress_level"]
        + 0.20 * _clip(50 + heart_z * 14)
        + 0.20 * _clip(50 - hrv_z * 14)
        + 0.15 * _clip(50 - sleep_z * 12)
    )

    trend_short = stress_index.rolling(3, min_periods=1).mean()
    trend_long = stress_index.rolling(7, min_periods=1).mean().shift(1)
    trend_delta = (trend_short - trend_long).fillna(0)

    low_hrv = hrv_z < -0.75
    low_sleep = sleep_z < -0.65
    high_stress = (stress_index >= 62) | (user_df["stress_level"] >= 65)
    high_resting_hr = resting_z > 0.65
    low_spo2 = user_df["spo2"] < 94
    abnormal_temp = temp_delta > 0.45
    low_recovery = recovery_score < 52
    anomaly_count = (
        low_hrv.astype(int)
        + low_sleep.astype(int)
        + high_stress.astype(int)
        + high_resting_hr.astype(int)
        + low_spo2.astype(int)
        + abnormal_temp.astype(int)
    )

    states = np.select(
        [
            low_recovery | low_spo2 | (anomaly_count >= 3),
            high_stress & (high_resting_hr | low_hrv),
            low_sleep & low_hrv,
        ],
        ["Recovery Needed", "Stressed", "Fatigued"],
        default="Normal",
    )

    confidence = np.select(
        [
            states == "Recovery Needed",
            states == "Stressed",
            states == "Fatigued",
        ],
        [
            68 + anomaly_count * 7 + _clip(55 - recovery_score, 0, 28) * 0.6,
            64 + _clip(stress_index - 55, 0, 35) * 0.6 + anomaly_count * 5,
            62 + _clip(-hrv_z, 0, 3) * 7 + _clip(-sleep_z, 0, 3) * 6,
        ],
        default=72 + _clip(recovery_score - 60, 0, 30) * 0.5 - anomaly_count * 5,
    )

    user_df["cortex_recovery_score"] = np.round(_clip(recovery_score), 1)
    user_df["stress_index"] = np.round(stress_index, 1)
    user_df["stress_trend_delta"] = np.round(trend_delta, 1)
    user_df["stress_trend"] = np.select(
        [trend_delta > 4.5, trend_delta < -4.5],
        ["Increasing", "Decreasing"],
        default="Stable",
    )
    user_df["sleep_quality"] = np.select(
        [
            (user_df["sleep_hours"] >= 7.5) & (user_df["sleep_score"] >= 82),
            (user_df["sleep_hours"] >= 6.5) & (user_df["sleep_score"] >= 70),
            (user_df["sleep_hours"] >= 5.5) & (user_df["sleep_score"] >= 55),
        ],
        ["Excellent", "Good", "Fair"],
        default="Poor",
    )
    user_df["cortex_health_state"] = states
    user_df["health_state_confidence"] = np.round(_clip(confidence, 50, 96), 1)
    user_df["anomaly_count"] = anomaly_count.astype(int)
    user_df["hrv_vs_baseline"] = np.round(user_df["hrv"] - baseline["hrv_mean"], 1)
    user_df["sleep_vs_baseline"] = np.round(user_df["sleep_hours"] - baseline["sleep_hours_mean"], 1)
    user_df["resting_hr_vs_baseline"] = np.round(
        user_df["resting_heart_rate"] - baseline["resting_heart_rate_mean"], 1
    )
    user_df["stress_vs_baseline"] = np.round(user_df["stress_level"] - baseline["stress_level_mean"], 1)
    user_df["temperature_vs_baseline"] = np.round(
        user_df["body_temperature"] - baseline["body_temperature_mean"], 2
    )
    user_df["spo2_vs_baseline"] = np.round(user_df["spo2"] - baseline["spo2_mean"], 1)
    user_df["steps_vs_baseline"] = np.round(user_df["steps"] - baseline["steps_mean"], 0)
    return user_df, baseline


def detect_anomalies(row: pd.Series, baseline: dict[str, float]) -> list[str]:
    alerts: list[str] = []
    if row["hrv"] < baseline["hrv_mean"] - baseline["hrv_std"]:
        alerts.append("HRV is materially below the personal baseline.")
    if row["resting_heart_rate"] > baseline["resting_heart_rate_mean"] + baseline["resting_heart_rate_std"]:
        alerts.append("Resting heart rate is elevated against baseline.")
    if row["sleep_hours"] < baseline["sleep_hours_mean"] - baseline["sleep_hours_std"]:
        alerts.append("Sleep duration is below the user's normal range.")
    if row["stress_level"] > baseline["stress_level_mean"] + baseline["stress_level_std"]:
        alerts.append("Stress level is above the user's usual range.")
    if row["spo2"] < 94:
        alerts.append("SpO2 is lower than the wellness threshold used by this prototype.")
    if abs(row["body_temperature"] - baseline["body_temperature_mean"]) > 0.5:
        alerts.append("Body temperature is outside the user's normal band.")
    return alerts or ["No major anomaly detected in the latest record."]


def make_recommendations(row: pd.Series, baseline: dict[str, float]) -> list[str]:
    recommendations: list[str] = []
    if row["cortex_recovery_score"] < 55:
        recommendations.append("Prioritize recovery today: reduce intense activity and add rest.")
    if row["stress_trend"] == "Increasing" or row["stress_index"] > 60:
        recommendations.append("Stress trend is rising; add a breathing break or lighter schedule block.")
    if row["hrv"] < baseline["hrv_mean"]:
        recommendations.append("HRV is below baseline, so avoid stacking another high-load workout.")
    if row["sleep_quality"] in {"Fair", "Poor"}:
        recommendations.append("Improve sleep consistency tonight and keep caffeine late in the day low.")
    if row["steps"] < baseline["steps_mean"] * 0.65:
        recommendations.append("Activity is below baseline; add a light walk if energy feels normal.")
    if not recommendations:
        recommendations.append("Signals look stable; maintain your current recovery and activity rhythm.")
    return recommendations


def generate_report(row: pd.Series, baseline: dict[str, float], alerts: list[str], recommendations: list[str]) -> str:
    return "\n".join(
        [
            "CORTEX Personalized Health Intelligence Report",
            f"User: {row['user_id']}",
            f"Date: {pd.to_datetime(row['date']).strftime('%Y-%m-%d')}",
            "",
            f"Recovery Score: {row['cortex_recovery_score']}/100",
            f"Stress Trend: {row['stress_trend']} ({row['stress_index']}/100 stress index)",
            f"Sleep Quality: {row['sleep_quality']}",
            f"Health State: {row['cortex_health_state']}",
            f"Confidence: {row['health_state_confidence']}%",
            "",
            "Baseline Comparison:",
            f"- HRV: {row['hrv']} ms vs baseline {baseline['hrv_mean']:.1f} ms",
            f"- Sleep: {row['sleep_hours']} h vs baseline {baseline['sleep_hours_mean']:.1f} h",
            f"- Resting HR: {row['resting_heart_rate']} bpm vs baseline {baseline['resting_heart_rate_mean']:.1f} bpm",
            f"- Stress: {row['stress_level']}/100 vs baseline {baseline['stress_level_mean']:.1f}/100",
            f"- SpO2: {row['spo2']}% vs baseline {baseline['spo2_mean']:.1f}%",
            f"- Temperature: {row['body_temperature']} C vs baseline {baseline['body_temperature_mean']:.1f} C",
            "",
            "Anomaly Alerts:",
            *[f"- {alert}" for alert in alerts],
            "",
            "Recommendations:",
            *[f"- {item}" for item in recommendations],
            "",
            "Disclaimer: CORTEX is a wellness intelligence prototype and is not a medical diagnosis tool.",
        ]
    )


def analyze_health_data(df: pd.DataFrame, user_id: str | None = None) -> dict[str, Any]:
    enriched, baseline = enrich_with_intelligence(df, user_id=user_id)
    latest = enriched.iloc[-1]
    alerts = detect_anomalies(latest, baseline)
    recommendations = make_recommendations(latest, baseline)
    report = generate_report(latest, baseline, alerts, recommendations)
    return {
        "user_id": str(latest["user_id"]),
        "data": enriched,
        "baseline": baseline,
        "latest": latest.to_dict(),
        "alerts": alerts,
        "recommendations": recommendations,
        "report": report,
    }

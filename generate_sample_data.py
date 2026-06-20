from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "sample_health_data.csv"
RNG = np.random.default_rng(42)


def classify_state(recovery: float, stress: float, hrv: float, sleep: float, resting_hr: float, spo2: float) -> str:
    if recovery < 48 or spo2 < 94 or (stress > 72 and hrv < 36):
        return "Recovery Needed"
    if stress >= 64 and (resting_hr > 68 or hrv < 42):
        return "Stressed"
    if sleep < 6.1 and hrv < 45:
        return "Fatigued"
    return "Normal"


def main() -> None:
    rows = []
    start = pd.Timestamp("2025-10-01")
    users = [f"U{idx:03d}" for idx in range(1, 21)]
    for user_id in users:
        base_resting = RNG.normal(61, 5)
        base_hrv = RNG.normal(52, 10)
        base_sleep = RNG.normal(7.1, 0.55)
        base_steps = RNG.normal(8200, 1400)
        base_temp = RNG.normal(36.65, 0.12)
        base_stress = RNG.normal(34, 10)
        for day in range(75):
            date = start + pd.Timedelta(days=day)
            weekday_load = 1.0 if date.dayofweek < 5 else -0.35
            event = RNG.choice(["normal", "stress", "fatigue", "recovery"], p=[0.66, 0.14, 0.12, 0.08])
            stress_shift = {"normal": 0, "stress": 28, "fatigue": 12, "recovery": 24}[event]
            sleep_shift = {"normal": 0, "stress": -0.7, "fatigue": -1.2, "recovery": -1.6}[event]
            hrv_shift = {"normal": 0, "stress": -8, "fatigue": -10, "recovery": -16}[event]
            resting_shift = {"normal": 0, "stress": 5, "fatigue": 4, "recovery": 8}[event]

            sleep_hours = np.clip(base_sleep + sleep_shift + RNG.normal(0, 0.45), 3.8, 9.3)
            sleep_score = np.clip(54 + sleep_hours * 6.2 + RNG.normal(0, 5), 35, 98)
            hrv = np.clip(base_hrv + hrv_shift + RNG.normal(0, 6), 18, 105)
            resting_hr = np.clip(base_resting + resting_shift + RNG.normal(0, 3), 45, 88)
            heart_rate = np.clip(resting_hr + RNG.normal(12 + weekday_load * 2, 5), 55, 115)
            stress = np.clip(base_stress + stress_shift + weekday_load * 4 + RNG.normal(0, 8), 4, 96)
            steps = np.clip(base_steps + RNG.normal(0, 1800) - stress_shift * 35, 1800, 18000)
            active_minutes = np.clip((steps / 180) + RNG.normal(0, 10), 5, 120)
            calories = np.clip(1750 + steps * 0.06 + active_minutes * 4 + RNG.normal(0, 130), 1400, 3600)
            spo2 = np.clip(97.7 - (1.5 if event == "recovery" else 0) + RNG.normal(0, 0.65), 92, 100)
            respiratory_rate = np.clip(15.2 + stress / 45 + RNG.normal(0, 1.1), 11, 23)
            temperature = np.clip(base_temp + (0.45 if event == "recovery" else 0) + RNG.normal(0, 0.13), 36.0, 38.2)

            recovery = (
                0.28 * sleep_score
                + 0.24 * np.clip(55 + (hrv - base_hrv) * 1.8, 0, 100)
                + 0.18 * np.clip(100 - stress, 0, 100)
                + 0.12 * np.clip((spo2 - 92) / 6 * 100, 0, 100)
                + 0.10 * np.clip(100 - abs(steps - base_steps) / 90, 0, 100)
                + 0.08 * np.clip(100 - max(0, resting_hr - base_resting) * 7, 0, 100)
            )
            recovery = np.clip(recovery + RNG.normal(0, 2.2), 15, 98)
            state = classify_state(recovery, stress, hrv, sleep_hours, resting_hr, spo2)

            rows.append(
                {
                    "user_id": user_id,
                    "date": date.strftime("%Y-%m-%d"),
                    "heart_rate": round(float(heart_rate), 1),
                    "resting_heart_rate": round(float(resting_hr), 1),
                    "hrv": round(float(hrv), 1),
                    "sleep_hours": round(float(sleep_hours), 1),
                    "sleep_score": round(float(sleep_score), 1),
                    "steps": int(round(float(steps))),
                    "active_minutes": int(round(float(active_minutes))),
                    "calories_burned": int(round(float(calories))),
                    "spo2": round(float(spo2), 1),
                    "respiratory_rate": round(float(respiratory_rate), 1),
                    "stress_level": round(float(stress), 1),
                    "body_temperature": round(float(temperature), 2),
                    "recovery_score": round(float(recovery), 1),
                    "health_state": state,
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(df):,} rows to {OUTPUT}")
    print(df["health_state"].value_counts().to_dict())


if __name__ == "__main__":
    main()

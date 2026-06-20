from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


FEATURE_COLUMNS = [
    "heart_rate",
    "resting_heart_rate",
    "hrv",
    "sleep_hours",
    "sleep_score",
    "steps",
    "active_minutes",
    "calories_burned",
    "spo2",
    "respiratory_rate",
    "stress_level",
    "body_temperature",
]

BASE_COLUMNS = ["user_id", "date"]
TARGET_COLUMNS = ["recovery_score", "health_state"]
REQUIRED_COLUMNS = BASE_COLUMNS + FEATURE_COLUMNS

HEALTH_STATE_LABELS = ["Normal", "Stressed", "Fatigued", "Recovery Needed"]

COLUMN_ALIASES = {
    "userid": "user_id",
    "user": "user_id",
    "timestamp": "date",
    "day": "date",
    "daily_steps": "steps",
    "step_count": "steps",
    "daily_heart_rate": "heart_rate",
    "avg_heart_rate": "heart_rate",
    "average_heart_rate": "heart_rate",
    "daily_sleep_hours": "sleep_hours",
    "sleep_duration": "sleep_hours",
    "heart_rate_variability": "hrv",
    "daily_hrv": "hrv",
    "daily_active_minutes": "active_minutes",
    "daily_calories_burned": "calories_burned",
    "daily_stress_level": "stress_level",
    "oxygen_saturation": "spo2",
    "daily_oxygen_saturation": "spo2",
    "daily_resting_heart_rate": "resting_heart_rate",
    "temperature": "body_temperature",
}

DEFAULT_VALUES = {
    "heart_rate": 75.0,
    "resting_heart_rate": 62.0,
    "hrv": 45.0,
    "sleep_hours": 7.0,
    "sleep_score": 75.0,
    "steps": 7500.0,
    "active_minutes": 35.0,
    "calories_burned": 2200.0,
    "spo2": 97.0,
    "respiratory_rate": 16.0,
    "stress_level": 35.0,
    "body_temperature": 36.7,
    "recovery_score": 70.0,
}

RANGES = {
    "heart_rate": (35, 210),
    "resting_heart_rate": (35, 150),
    "hrv": (5, 200),
    "sleep_hours": (0, 14),
    "sleep_score": (0, 100),
    "steps": (0, 60000),
    "active_minutes": (0, 400),
    "calories_burned": (800, 6000),
    "spo2": (70, 100),
    "respiratory_rate": (6, 35),
    "stress_level": (0, 100),
    "body_temperature": (34, 41),
    "recovery_score": (0, 100),
}


@dataclass(frozen=True)
class ValidationResult:
    missing_required: list[str]
    optional_missing: list[str]
    available_columns: list[str]

    @property
    def is_valid(self) -> bool:
        return len(self.missing_required) == 0


def normalize_column_name(name: str) -> str:
    normalized = (
        str(name)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
    )
    return COLUMN_ALIASES.get(normalized, normalized)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = [normalize_column_name(col) for col in cleaned.columns]
    return cleaned


def validate_schema(df: pd.DataFrame, require_targets: bool = False) -> ValidationResult:
    normalized = normalize_columns(df)
    required = REQUIRED_COLUMNS + (TARGET_COLUMNS if require_targets else [])
    missing_required = [col for col in required if col not in normalized.columns]
    optional_missing = [col for col in TARGET_COLUMNS if col not in normalized.columns]
    return ValidationResult(
        missing_required=missing_required,
        optional_missing=optional_missing,
        available_columns=list(normalized.columns),
    )


def normalize_stress_level(series: pd.Series) -> pd.Series:
    """Normalize stress values from either 1-10 or 0-100 input scales."""
    values = pd.to_numeric(series, errors="coerce")
    non_null = values.dropna()
    if not non_null.empty and non_null.max() <= 10:
        values = values * 10
    return values.clip(0, 100)


def _fill_numeric_by_user(df: pd.DataFrame, column: str) -> pd.Series:
    values = pd.to_numeric(df[column], errors="coerce")
    if column == "stress_level":
        values = normalize_stress_level(values)

    def fill_group(series: pd.Series) -> pd.Series:
        median = series.median()
        if pd.isna(median):
            median = DEFAULT_VALUES.get(column, 0.0)
        return series.fillna(median)

    values = values.groupby(df["user_id"]).transform(fill_group)
    values = values.fillna(values.median()).fillna(DEFAULT_VALUES.get(column, 0.0))
    low, high = RANGES.get(column, (-np.inf, np.inf))
    return values.clip(lower=low, upper=high)


def _coerce_dates(series: pd.Series) -> pd.Series:
    dates = pd.to_datetime(series, errors="coerce")
    if dates.isna().any():
        fallback = pd.date_range("2024-01-01", periods=len(series), freq="D")
        dates = dates.fillna(pd.Series(fallback, index=series.index))
    return dates


def clean_health_data(df: pd.DataFrame, require_targets: bool = False) -> pd.DataFrame:
    """Normalize, validate, and clean wearable-health CSV data."""
    cleaned = normalize_columns(df)
    validation = validate_schema(cleaned, require_targets=require_targets)
    if not validation.is_valid:
        missing = ", ".join(validation.missing_required)
        raise ValueError(f"Missing required column(s): {missing}")

    cleaned = cleaned.copy()
    cleaned["user_id"] = cleaned["user_id"].astype(str).str.strip().replace("", "U001")
    cleaned["date"] = _coerce_dates(cleaned["date"])

    numeric_columns = FEATURE_COLUMNS + [col for col in ["recovery_score"] if col in cleaned.columns]
    for column in numeric_columns:
        cleaned[column] = _fill_numeric_by_user(cleaned, column)

    if "health_state" in cleaned.columns:
        state_map = {label.lower(): label for label in HEALTH_STATE_LABELS}
        cleaned["health_state"] = (
            cleaned["health_state"]
            .astype(str)
            .str.strip()
            .str.lower()
            .map(state_map)
            .fillna("Normal")
        )

    cleaned = cleaned.sort_values(["user_id", "date"]).reset_index(drop=True)
    return cleaned


def detect_range_outliers(df: pd.DataFrame) -> dict[str, int]:
    normalized = normalize_columns(df)
    outliers: dict[str, int] = {}
    for column, (low, high) in RANGES.items():
        if column not in normalized.columns:
            continue
        values = pd.to_numeric(normalized[column], errors="coerce")
        if column == "stress_level":
            values = normalize_stress_level(values)
        count = int(((values < low) | (values > high)).sum())
        if count:
            outliers[column] = count
    return outliers


def build_validation_report(df: pd.DataFrame) -> pd.DataFrame:
    """Return user-facing validation checks for the upload screen."""
    normalized = normalize_columns(df)
    schema = validate_schema(normalized, require_targets=False)
    missing_values = int(normalized.isna().sum().sum())
    date_values = pd.to_datetime(normalized["date"], errors="coerce") if "date" in normalized.columns else pd.Series(dtype="datetime64[ns]")
    invalid_dates = int(date_values.isna().sum()) if "date" in normalized.columns else len(normalized)
    outliers = detect_range_outliers(normalized)
    cleaned = clean_health_data(normalized, require_targets=False) if schema.is_valid else pd.DataFrame()
    min_baseline_days = int(cleaned.groupby("user_id").size().min()) if not cleaned.empty else 0

    checks = [
        {
            "Check": "File received",
            "Status": "Passed" if len(normalized) > 0 else "Failed",
            "Detail": f"{len(normalized):,} rows detected.",
        },
        {
            "Check": "Required columns",
            "Status": "Passed" if schema.is_valid else "Failed",
            "Detail": "All required columns found." if schema.is_valid else "Missing: " + ", ".join(schema.missing_required),
        },
        {
            "Check": "Date format",
            "Status": "Passed" if invalid_dates == 0 else "Fixed",
            "Detail": "All dates parsed." if invalid_dates == 0 else f"{invalid_dates:,} invalid date value(s) repaired.",
        },
        {
            "Check": "Missing values",
            "Status": "Passed" if missing_values == 0 else "Fixed",
            "Detail": "No missing values." if missing_values == 0 else f"{missing_values:,} missing value(s) filled by user medians.",
        },
        {
            "Check": "Outlier detection",
            "Status": "Passed" if not outliers else "Warning",
            "Detail": "No range outliers detected." if not outliers else ", ".join(f"{k}: {v}" for k, v in outliers.items()),
        },
        {
            "Check": "Stress scale",
            "Status": "Passed",
            "Detail": "Stress values normalized to a 0-100 scale.",
        },
        {
            "Check": "Baseline days",
            "Status": "Passed" if min_baseline_days >= 30 else "Warning",
            "Detail": f"Minimum history per user: {min_baseline_days} day(s).",
        },
        {
            "Check": "Analysis ready",
            "Status": "Passed" if schema.is_valid else "Failed",
            "Detail": "CORTEX engine can run." if schema.is_valid else "Fix schema before analysis.",
        },
    ]
    return pd.DataFrame(checks)


def summarize_dataset(df: pd.DataFrame) -> dict[str, object]:
    cleaned = clean_health_data(df, require_targets=False)
    date_min = cleaned["date"].min()
    date_max = cleaned["date"].max()
    label_counts = (
        cleaned["health_state"].value_counts().to_dict()
        if "health_state" in cleaned.columns
        else {}
    )
    return {
        "rows": int(len(cleaned)),
        "users": int(cleaned["user_id"].nunique()),
        "date_start": date_min.strftime("%Y-%m-%d"),
        "date_end": date_max.strftime("%Y-%m-%d"),
        "missing_values": int(cleaned[REQUIRED_COLUMNS].isna().sum().sum()),
        "health_state_counts": label_counts,
        "min_days_per_user": int(cleaned.groupby("user_id").size().min()),
        "max_days_per_user": int(cleaned.groupby("user_id").size().max()),
    }


def first_available(options: Iterable[str], columns: Iterable[str]) -> str | None:
    available = set(columns)
    for option in options:
        if option in available:
            return option
    return None

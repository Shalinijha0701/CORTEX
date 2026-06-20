from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from model import enrich_with_intelligence
from utils import FEATURE_COLUMNS, clean_health_data


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "sample_health_data.csv"
ARTIFACT_DIR = ROOT / "model_artifacts"


def time_based_split(df: pd.DataFrame, train_fraction: float = 0.8) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_parts = []
    test_parts = []
    for _, group in df.sort_values("date").groupby("user_id"):
        split_at = max(1, int(len(group) * train_fraction))
        train_parts.append(group.iloc[:split_at])
        test_parts.append(group.iloc[split_at:])
    train_df = pd.concat(train_parts).reset_index(drop=True)
    test_df = pd.concat(test_parts).reset_index(drop=True)
    return train_df, test_df


def rule_engine_metrics(df: pd.DataFrame) -> dict[str, object]:
    enriched_parts = []
    for user_id in df["user_id"].unique():
        enriched, _ = enrich_with_intelligence(df, user_id=user_id)
        enriched_parts.append(enriched)
    enriched_df = pd.concat(enriched_parts).reset_index(drop=True)

    metrics: dict[str, object] = {
        "mode": "personal_baseline_rule_engine",
        "rows_evaluated": int(len(enriched_df)),
    }
    if "recovery_score" in enriched_df.columns:
        mae = np.mean(np.abs(enriched_df["cortex_recovery_score"] - enriched_df["recovery_score"]))
        metrics["recovery_mae"] = round(float(mae), 3)
    if "health_state" in enriched_df.columns:
        accuracy = (enriched_df["cortex_health_state"] == enriched_df["health_state"]).mean()
        metrics["health_state_agreement"] = round(float(accuracy), 3)
    return metrics


def numpy_fallback_metrics(train_df: pd.DataFrame, test_df: pd.DataFrame) -> dict[str, object]:
    """Small dependency-free train/test baseline for environments without scikit-learn."""
    x_train = train_df[FEATURE_COLUMNS].to_numpy(dtype=float)
    x_test = test_df[FEATURE_COLUMNS].to_numpy(dtype=float)
    feature_mean = x_train.mean(axis=0)
    feature_std = x_train.std(axis=0)
    feature_std[feature_std < 1e-9] = 1.0

    x_train_scaled = (x_train - feature_mean) / feature_std
    x_test_scaled = (x_test - feature_mean) / feature_std

    design_train = np.c_[np.ones(len(x_train_scaled)), x_train_scaled]
    design_test = np.c_[np.ones(len(x_test_scaled)), x_test_scaled]
    coefficients = np.linalg.pinv(design_train) @ train_df["recovery_score"].to_numpy(dtype=float)
    recovery_predictions = design_test @ coefficients
    recovery_mae = np.mean(np.abs(recovery_predictions - test_df["recovery_score"].to_numpy(dtype=float)))

    labels = sorted(train_df["health_state"].unique())
    centroids = {
        label: x_train_scaled[train_df["health_state"].to_numpy() == label].mean(axis=0)
        for label in labels
    }
    state_predictions = [
        min(labels, key=lambda label: float(np.linalg.norm(row - centroids[label])))
        for row in x_test_scaled
    ]
    accuracy = (np.array(state_predictions) == test_df["health_state"].to_numpy()).mean()

    return {
        "mode": "numpy_linear_regression_and_nearest_centroid",
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "recovery_mae": round(float(recovery_mae), 3),
        "health_state_accuracy": round(float(accuracy), 3),
        "note": "scikit-learn is not installed, so a NumPy-only baseline model was trained and evaluated.",
    }


def sklearn_metrics(train_df: pd.DataFrame, test_df: pd.DataFrame) -> dict[str, object] | None:
    try:
        from joblib import dump
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        from sklearn.metrics import accuracy_score, mean_absolute_error
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
    except Exception:
        return None

    ARTIFACT_DIR.mkdir(exist_ok=True)
    x_train = train_df[FEATURE_COLUMNS]
    x_test = test_df[FEATURE_COLUMNS]

    regressor = Pipeline(
        [
            ("scale", StandardScaler()),
            ("model", RandomForestRegressor(n_estimators=180, random_state=42, min_samples_leaf=2)),
        ]
    )
    classifier = Pipeline(
        [
            ("scale", StandardScaler()),
            ("model", RandomForestClassifier(n_estimators=180, random_state=42, min_samples_leaf=2)),
        ]
    )

    regressor.fit(x_train, train_df["recovery_score"])
    classifier.fit(x_train, train_df["health_state"])

    recovery_predictions = regressor.predict(x_test)
    state_predictions = classifier.predict(x_test)

    dump(regressor, ARTIFACT_DIR / "recovery_regressor.joblib")
    dump(classifier, ARTIFACT_DIR / "health_state_classifier.joblib")

    return {
        "mode": "scikit_learn_random_forest",
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "recovery_mae": round(float(mean_absolute_error(test_df["recovery_score"], recovery_predictions)), 3),
        "health_state_accuracy": round(float(accuracy_score(test_df["health_state"], state_predictions)), 3),
        "saved_artifacts": [
            "model_artifacts/recovery_regressor.joblib",
            "model_artifacts/health_state_classifier.joblib",
        ],
    }


def main() -> None:
    df = clean_health_data(pd.read_csv(DATA_PATH), require_targets=True)
    train_df, test_df = time_based_split(df)
    metrics = sklearn_metrics(train_df, test_df)
    if metrics is None:
        metrics = numpy_fallback_metrics(train_df, test_df)
        metrics["rule_engine_reference"] = rule_engine_metrics(df)

    ARTIFACT_DIR.mkdir(exist_ok=True)
    output_path = ARTIFACT_DIR / "training_metrics.json"
    output_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    print(f"Saved metrics to {output_path}")


if __name__ == "__main__":
    main()

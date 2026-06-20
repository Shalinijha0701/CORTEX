from __future__ import annotations

from pathlib import Path

import pandas as pd

from model import analyze_health_data
from utils import REQUIRED_COLUMNS, clean_health_data, summarize_dataset


ROOT = Path(__file__).resolve().parent


def main() -> None:
    df = pd.read_csv(ROOT / "sample_health_data.csv")
    cleaned = clean_health_data(df, require_targets=True)
    assert set(REQUIRED_COLUMNS).issubset(cleaned.columns)
    assert cleaned[REQUIRED_COLUMNS].isna().sum().sum() == 0

    summary = summarize_dataset(cleaned)
    assert summary["rows"] >= 50
    assert summary["users"] >= 1

    first_user = cleaned["user_id"].iloc[0]
    result = analyze_health_data(cleaned, user_id=first_user)
    enriched = result["data"]
    assert "cortex_recovery_score" in enriched.columns
    assert enriched["cortex_recovery_score"].between(0, 100).all()
    assert result["latest"]["cortex_health_state"] in {
        "Normal",
        "Stressed",
        "Fatigued",
        "Recovery Needed",
    }
    assert result["recommendations"]
    assert result["alerts"]
    print("CORTEX smoke tests passed.")
    print(f"Rows: {summary['rows']} | Users: {summary['users']} | Latest user: {first_user}")


if __name__ == "__main__":
    main()

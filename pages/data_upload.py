from __future__ import annotations

import streamlit as st

from components import page_header, validation_step
from utils import REQUIRED_COLUMNS


def render(context: dict[str, object]) -> None:
    page_header(
        "Data Intake",
        "Upload Validation",
        "A practical validation pipeline for schema, missing values, outliers, baseline calibration, and analysis readiness.",
    )

    st.markdown(
        f"""
        <div class="cortex-card">
            <div class="card-label">Current file</div>
            <div class="card-value">{context['source_name']}</div>
            <div class="card-caption">Use the sidebar uploader to replace this dataset.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    report = context["validation_report"]
    progress = int((report["Status"].isin(["Passed", "Fixed", "Warning"]).mean()) * 100)
    st.progress(progress, text=f"Validation workflow {progress}% complete")

    workflow = [
        ("File received", "CSV file loaded into the session"),
        ("Schema validation", "Required columns are checked and aliases are normalized"),
        ("Missing value check", "Blank numeric signals are filled by user-level medians"),
        ("Outlier detection", "Health metrics are compared with safe prototype ranges"),
        ("Baseline calibration", "CORTEX builds each user's personal normal range"),
        ("Analysis ready", "Dashboard, reports, and clinician views can run"),
    ]
    cols = st.columns(3)
    for idx, (title, detail) in enumerate(workflow, start=1):
        with cols[(idx - 1) % 3]:
            status_row = report[report["Check"].str.lower() == title.lower()]
            status = status_row["Status"].iloc[0] if not status_row.empty else "Passed"
            validation_step(idx, title, detail, status)

    st.subheader("Validation Results")
    st.dataframe(report, width="stretch", hide_index=True)

    st.subheader("Expected Schema")
    st.code(",".join(REQUIRED_COLUMNS), language="text")

    if context["valid"]:
        st.download_button(
            "Download Cleaned CSV",
            data=context["cleaned_df"].to_csv(index=False),
            file_name="cortex_cleaned_health_data.csv",
            mime="text/csv",
        )

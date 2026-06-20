from __future__ import annotations

import streamlit as st

from components import baseline_dataframe, metric_card, page_header, simple_line_chart


def render(context: dict[str, object]) -> None:
    analysis = context["analysis"]
    latest = analysis["latest"]
    baseline = analysis["baseline"]
    enriched = analysis["data"]

    page_header(
        "Personal Calibration",
        "Profile & Baseline",
        "The baseline engine learns each user's own normal range before scoring recent records.",
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Baseline Days", f"{baseline['baseline_days']:.0f}", "First 80% of history", "#00685f")
    with c2:
        metric_card("Analysis Days", f"{baseline['analysis_days']:.0f}", "Latest 20% monitored", "#4b41e1")
    with c3:
        metric_card("Stress Delta", f"{latest['stress_vs_baseline']}", "0-100 normalized scale", "#b90538")
    with c4:
        metric_card("Temp Delta", f"{latest['temperature_vs_baseline']} C", "Personal body-temp band", "#008378")

    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("Baseline Table")
        st.dataframe(baseline_dataframe(analysis), width="stretch", hide_index=True)
    with right:
        st.subheader("Calibration Notes")
        st.markdown(
            """
            <div class="cortex-card">
                <div class="card-label">Baseline Method</div>
                <div class="card-caption">
                    CORTEX uses the first 70-80% of time-ordered records as the personal baseline.
                    The latest records are then compared against user-specific means and standard deviations.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    a, b = st.columns(2)
    with a:
        st.plotly_chart(simple_line_chart(enriched, "hrv", "HRV Calibration History", "#00685f"), width="stretch")
    with b:
        st.plotly_chart(simple_line_chart(enriched, "resting_heart_rate", "Resting HR History", "#b90538"), width="stretch")

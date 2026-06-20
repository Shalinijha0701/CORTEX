from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from components import alert_row, baseline_dataframe, hrv_stress_chart, load_training_metrics, metric_card, page_header
from reporting import build_report_pdf


def render(context: dict[str, object]) -> None:
    analysis = context["analysis"]
    latest = analysis["latest"]
    enriched = analysis["data"]

    page_header(
        "Signal Interpretation",
        "Intelligence Hub",
        "Anomaly detection, baseline comparison, model metrics, and exportable insights.",
    )

    a, b, c, d = st.columns(4)
    with a:
        metric_card("Health State", latest["cortex_health_state"], f"{latest['health_state_confidence']}% confidence", "#00685f")
    with b:
        metric_card("Anomalies", str(latest["anomaly_count"]), "Latest record", "#b90538")
    with c:
        metric_card("Stress Trend", latest["stress_trend"], f"{latest['stress_trend_delta']} delta", "#4b41e1")
    with d:
        metric_card("SpO2 Delta", f"{latest['spo2_vs_baseline']}%", "Against baseline", "#008378")

    left, right = st.columns([1.35, 1])
    with left:
        st.markdown('<div class="cortex-card">', unsafe_allow_html=True)
        st.plotly_chart(hrv_stress_chart(enriched), width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.subheader("Anomaly Alerts")
        for alert in analysis["alerts"]:
            alert_row(alert, "alert")
        st.subheader("Recommendations")
        for item in analysis["recommendations"]:
            alert_row(item, "recommendation")

    baseline_df = baseline_dataframe(analysis)
    st.subheader("Baseline Comparison")
    st.dataframe(baseline_df, width="stretch", hide_index=True)

    metrics = load_training_metrics(Path(__file__).resolve().parents[1])
    if metrics:
        st.subheader("Model Evaluation")
        model_table = pd.DataFrame([metrics])
        st.dataframe(model_table, width="stretch", hide_index=True)

    pdf_bytes = build_report_pdf(analysis)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "Download Health Report PDF",
            data=pdf_bytes,
            file_name=f"cortex_health_report_{context['selected_user']}.pdf",
            mime="application/pdf",
        )
    with col2:
        st.download_button(
            "Download Text Report",
            data=analysis["report"],
            file_name=f"cortex_report_{context['selected_user']}.txt",
            mime="text/plain",
        )
    with col3:
        st.download_button(
            "Download Baseline Summary",
            data=baseline_df.to_csv(index=False),
            file_name=f"cortex_baseline_{context['selected_user']}.csv",
            mime="text/csv",
        )

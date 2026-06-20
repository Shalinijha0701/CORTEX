from __future__ import annotations

import streamlit as st

from components import hrv_stress_chart, insight_card, metric_card, page_header, recovery_gauge, simple_line_chart


def render(context: dict[str, object]) -> None:
    analysis = context["analysis"]
    enriched = analysis["data"]
    latest = analysis["latest"]

    page_header(
        "Personalized Dashboard",
        "CORTEX Intelligence Hub",
        "Live wearable-health signals compared against the user's own baseline.",
    )

    gauge_col, card_col = st.columns([1.25, 1])
    with gauge_col:
        recovery_gauge(
            float(latest["cortex_recovery_score"]),
            str(latest["cortex_health_state"]),
            float(latest["health_state_confidence"]),
        )
    with card_col:
        top_a, top_b = st.columns(2)
        with top_a:
            metric_card("HRV Delta", f"{latest['hrv_vs_baseline']} ms", "Against personal baseline", "#00685f")
        with top_b:
            metric_card("Stress Level", f"{latest['stress_index']}/100", str(latest["stress_trend"]), "#b90538")
        bot_a, bot_b = st.columns(2)
        with bot_a:
            metric_card("Sleep Quality", str(latest["sleep_quality"]), f"{latest['sleep_hours']} hours", "#4b41e1")
        with bot_b:
            metric_card("Resting HR", f"{latest['resting_heart_rate']} bpm", f"{latest['resting_hr_vs_baseline']} vs baseline", "#008378")

    chart_col, insight_col = st.columns([1.55, 1])
    with chart_col:
        st.markdown('<div class="cortex-card">', unsafe_allow_html=True)
        st.plotly_chart(hrv_stress_chart(enriched), width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)
    with insight_col:
        insight_card("Intelligence Insight", analysis["recommendations"][0], "CORTEX Recommendation", "#00685f")
        st.write("")
        insight_card("Data Intelligence Hub", analysis["alerts"][0], "Anomaly Watch", "#b90538")

    lower_a, lower_b = st.columns(2)
    with lower_a:
        st.plotly_chart(simple_line_chart(enriched, "sleep_hours", "Sleep Trend", "#4b41e1"), width="stretch")
    with lower_b:
        st.plotly_chart(simple_line_chart(enriched, "cortex_recovery_score", "Recovery Score Trend", "#00685f"), width="stretch")

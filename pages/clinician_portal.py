from __future__ import annotations

import pandas as pd
import streamlit as st

from components import html_table, metric_card, page_header, status_chip
from model import analyze_health_data
from reporting import build_report_pdf


def build_patient_queue(cleaned: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for user_id in sorted(cleaned["user_id"].astype(str).unique()):
        analysis = analyze_health_data(cleaned, user_id=user_id)
        latest = analysis["latest"]
        rows.append(
            {
                "User ID": user_id,
                "Health State": latest["cortex_health_state"],
                "Confidence": latest["health_state_confidence"],
                "Recovery": latest["cortex_recovery_score"],
                "Stress": latest["stress_index"],
                "Sleep": latest["sleep_quality"],
                "Anomalies": latest["anomaly_count"],
            }
        )
    order = {"Recovery Needed": 0, "Stressed": 1, "Fatigued": 2, "Normal": 3}
    queue = pd.DataFrame(rows)
    queue["_order"] = queue["Health State"].map(order)
    return queue.sort_values(["_order", "Recovery"]).drop(columns="_order").reset_index(drop=True)


def render(context: dict[str, object]) -> None:
    cleaned = context["cleaned_df"]
    analysis = context["analysis"]
    queue = build_patient_queue(cleaned)

    page_header(
        "Care Team View",
        "Clinician Review Portal",
        "A multi-patient prototype view for prioritizing recovery risk and reviewing generated reports.",
    )

    critical = int((queue["Health State"] == "Recovery Needed").sum())
    stressed = int((queue["Health State"] == "Stressed").sum())
    stable = int((queue["Health State"] == "Normal").sum())
    avg_recovery = queue["Recovery"].mean()

    a, b, c, d = st.columns(4)
    with a:
        metric_card("Critical Recovery", str(critical), "Immediate review queue", "#b90538")
    with b:
        metric_card("High Stress", str(stressed), "Elevated stress profiles", "#9a4a00")
    with c:
        metric_card("Stable", str(stable), "Normal latest state", "#00685f")
    with d:
        metric_card("Avg Recovery", f"{avg_recovery:.0f}", "Across loaded users", "#4b41e1")

    st.subheader("Patient Queue")
    st.markdown(html_table(queue), unsafe_allow_html=True)

    st.subheader("Selected Patient")
    latest = analysis["latest"]
    st.markdown(
        f"""
        <div class="cortex-card">
            <div class="card-label">Review Summary</div>
            <h3>{context['selected_user']} &nbsp; {status_chip(latest['cortex_health_state'])}</h3>
            <div class="card-caption">
                Recovery {latest['cortex_recovery_score']}/100, stress {latest['stress_index']}/100,
                confidence {latest['health_state_confidence']}%, anomalies {latest['anomaly_count']}.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    note = st.text_area("Clinician note", placeholder="Prototype note only; not stored in a database.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save review note"):
            st.session_state[f"clinician_note_{context['selected_user']}"] = note
            st.success("Review note saved in the current prototype session.")
    with col2:
        st.download_button(
            "Export Selected Patient PDF",
            data=build_report_pdf(analysis),
            file_name=f"clinician_report_{context['selected_user']}.pdf",
            mime="application/pdf",
        )

from __future__ import annotations

import streamlit as st

from components import alert_row, metric_card, page_header


def render(context: dict[str, object]) -> None:
    analysis = context["analysis"]
    latest = analysis["latest"]

    page_header(
        "Patient Alerts",
        "Mobile Alert Center",
        "Prototype alert workflow for patient-facing recovery messages and action reminders.",
    )

    a, b, c = st.columns(3)
    with a:
        metric_card("Alert Priority", latest["cortex_health_state"], f"{latest['health_state_confidence']}% confidence", "#b90538")
    with b:
        metric_card("Recovery", f"{latest['cortex_recovery_score']}/100", "Today", "#00685f")
    with c:
        metric_card("Stress", f"{latest['stress_index']}/100", latest["stress_trend"], "#4b41e1")

    left, right = st.columns([1, 1])
    with left:
        st.subheader("Patient Messages")
        for item in analysis["recommendations"]:
            alert_row(item, "recommendation")
        if st.button("Mark alerts as reviewed"):
            st.session_state["alerts_reviewed"] = True
            st.success("Alerts marked as reviewed for this prototype session.")
    with right:
        st.subheader("Notification Controls")
        st.toggle("Morning recovery brief", value=True)
        st.toggle("High-stress warning", value=True)
        st.toggle("Sleep debt reminder", value=True)
        st.toggle("Clinician escalation when Recovery Needed", value=True)
        note = st.text_area("Patient note", placeholder="Add a short note for the next review.")
        if st.button("Save patient note"):
            st.session_state["patient_note"] = note
            st.success("Patient note saved in the current session.")

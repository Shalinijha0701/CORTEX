from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from components import render_sidebar_badge
from model import analyze_health_data
from pages import clinician_portal, dashboard, data_upload, intelligence_hub, mobile_alerts, profile_baseline
from styles import apply_global_styles
from utils import build_validation_report, clean_health_data, summarize_dataset, validate_schema


ROOT = Path(__file__).resolve().parent
SAMPLE_DATA = ROOT / "sample_health_data.csv"


st.set_page_config(
    page_title="CORTEX Health Intelligence",
    page_icon="CORTEX",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_global_styles()


@st.cache_data
def load_sample_data() -> pd.DataFrame:
    return pd.read_csv(SAMPLE_DATA)


def load_raw_data() -> tuple[pd.DataFrame, str]:
    uploaded = st.sidebar.file_uploader("Upload wearable CSV", type=["csv"], key="sidebar_csv")
    use_sample = st.sidebar.toggle("Use sample data", value=uploaded is None)
    if uploaded is not None and not use_sample:
        return pd.read_csv(uploaded), uploaded.name
    return load_sample_data(), "sample_health_data.csv"


def build_context(raw_df: pd.DataFrame, source_name: str, selected_user: str | None = None) -> dict[str, object]:
    validation = validate_schema(raw_df, require_targets=False)
    validation_report = build_validation_report(raw_df)
    if not validation.is_valid:
        return {
            "raw_df": raw_df,
            "source_name": source_name,
            "valid": False,
            "validation": validation,
            "validation_report": validation_report,
        }

    cleaned = clean_health_data(raw_df)
    users = sorted(cleaned["user_id"].astype(str).unique())
    user_id = selected_user or users[0]
    analysis = analyze_health_data(cleaned, user_id=user_id)
    return {
        "raw_df": raw_df,
        "cleaned_df": cleaned,
        "source_name": source_name,
        "valid": True,
        "validation": validation,
        "validation_report": validation_report,
        "summary": summarize_dataset(cleaned),
        "users": users,
        "selected_user": user_id,
        "analysis": analysis,
    }


PAGES = {
    "Dashboard": dashboard.render,
    "Intelligence Hub": intelligence_hub.render,
    "Data Upload Validation": data_upload.render,
    "Profile & Baseline": profile_baseline.render,
    "Patient Alerts": mobile_alerts.render,
    "Clinician Portal": clinician_portal.render,
}


with st.sidebar:
    st.markdown(
        """
        <div class="cortex-brand">
            <div class="brand-mark">CX</div>
            <div>
                <div class="brand-title">CORTEX</div>
                <div class="brand-subtitle">Health Intelligence</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

raw_data, source = load_raw_data()
context = build_context(raw_data, source)

with st.sidebar:
    st.divider()
    if context["valid"]:
        users = context["users"]
        selected_user = st.selectbox("Active profile", users, index=users.index(context["selected_user"]))
        if selected_user != context["selected_user"]:
            context = build_context(raw_data, source, selected_user=selected_user)
    else:
        st.error("Upload schema needs attention.")

    page_name = st.radio("Navigation", list(PAGES.keys()), label_visibility="collapsed")
    st.divider()
    if context["valid"]:
        summary = context["summary"]
        st.caption(f"{summary['rows']:,} rows | {summary['users']} users")
        st.caption(f"{summary['date_start']} to {summary['date_end']}")
    render_sidebar_badge("Live Sync Active", "Encrypted prototype session")

if not context["valid"] and page_name != "Data Upload Validation":
    st.error("The uploaded CSV is missing required columns. Open Data Upload Validation for details.")
    st.stop()

PAGES[page_name](context)

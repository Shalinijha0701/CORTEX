from __future__ import annotations

import json
import html
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


STATE_COLORS = {
    "Normal": "#00685f",
    "Stressed": "#9a4a00",
    "Fatigued": "#4b41e1",
    "Recovery Needed": "#b90538",
}


def state_color(state: str) -> str:
    return STATE_COLORS.get(state, "#00685f")


def chip_class(state: str) -> str:
    if state == "Recovery Needed":
        return "status-chip chip-critical"
    if state in {"Stressed", "Fatigued"}:
        return "status-chip chip-warning"
    return "status-chip"


def status_chip(state: str) -> str:
    return f'<span class="{chip_class(state)}"><span class="chip-dot"></span>{state}</span>'


def page_header(kicker: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="page-kicker">{kicker}</div>
        <div class="page-title">{title}</div>
        <div class="page-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, caption: str = "", accent: str = "#00685f") -> None:
    st.markdown(
        f"""
        <div class="cortex-card compact" style="--accent:{accent}">
            <div class="accent-line"></div>
            <div class="card-label">{label}</div>
            <div class="card-value">{value}</div>
            <div class="card-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_card(title: str, body: str, status: str = "Active", accent: str = "#00685f") -> None:
    st.markdown(
        f"""
        <div class="cortex-card" style="--accent:{accent}">
            <div class="accent-line"></div>
            <div class="card-label">{status}</div>
            <h3 style="margin: 5px 0 8px 0;">{title}</h3>
            <div class="card-caption">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def recovery_gauge(score: float, state: str, confidence: float) -> None:
    color = state_color(state)
    st.markdown(
        f"""
        <div class="cortex-card">
            <div class="gauge-wrap">
                <div class="recovery-gauge" style="--score:{score}; --gauge-color:{color};">
                    <div class="recovery-gauge-inner">
                        <div>
                            <div class="gauge-number">{score:.0f}</div>
                            <div class="gauge-label">Recovery</div>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="card-label">Holistic Health State</div>
                    <div style="margin: 8px 0 12px 0;">{status_chip(state)}</div>
                    <div class="card-caption">CORTEX confidence: <b>{confidence:.0f}%</b></div>
                    <div class="card-caption">Personal baseline analysis using HRV, sleep, stress, resting HR, SpO2, and temperature.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def validation_step(index: int, title: str, detail: str, status: str) -> None:
    accent = "#00685f" if status == "Passed" else "#9a4a00" if status in {"Warning", "Fixed"} else "#b90538"
    st.markdown(
        f"""
        <div class="validation-step">
            <div class="step-index" style="background:{accent};">{index}</div>
            <div>
                <b>{title}</b>
                <div class="muted small">{status}: {detail}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def alert_row(text: str, kind: str = "alert") -> None:
    accent = "#b90538" if kind == "alert" else "#00685f"
    st.markdown(
        f"""
        <div class="alert-row" style="border-left: 4px solid {accent};">
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_badge(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="sidebar-badge">
            <b>{title}</b>
            <div class="muted small">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hrv_stress_chart(enriched: pd.DataFrame) -> go.Figure:
    data = enriched.tail(14).copy()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data["date"],
            y=data["hrv"],
            name="HRV",
            mode="lines+markers",
            line=dict(color="#00685f", width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data["date"],
            y=data["stress_index"],
            name="Stress Index",
            mode="lines+markers",
            yaxis="y2",
            line=dict(color="#b90538", width=3),
        )
    )
    fig.update_layout(
        height=360,
        margin=dict(l=12, r=12, t=36, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(color="#17201f"),
        legend=dict(orientation="h", y=1.12, x=0),
        yaxis=dict(title="HRV", gridcolor="#e5efec"),
        yaxis2=dict(title="Stress", overlaying="y", side="right", range=[0, 100], gridcolor="#e5efec"),
        xaxis=dict(gridcolor="#eef5f3"),
    )
    return fig


def simple_line_chart(enriched: pd.DataFrame, y: str, title: str, color: str) -> go.Figure:
    data = enriched.tail(21).copy()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data["date"],
            y=data[y],
            mode="lines+markers",
            name=title,
            line=dict(color=color, width=3),
        )
    )
    fig.update_layout(
        title=title,
        height=285,
        margin=dict(l=12, r=12, t=50, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(color="#17201f"),
        yaxis=dict(gridcolor="#e5efec"),
        xaxis=dict(gridcolor="#eef5f3"),
    )
    return fig


def baseline_dataframe(analysis: dict[str, Any]) -> pd.DataFrame:
    latest = analysis["latest"]
    baseline = analysis["baseline"]
    rows = []
    for metric in [
        "hrv",
        "sleep_hours",
        "resting_heart_rate",
        "stress_level",
        "steps",
        "spo2",
        "body_temperature",
    ]:
        rows.append(
            {
                "Metric": metric,
                "Latest": round(float(latest[metric]), 2),
                "Baseline Mean": round(float(baseline[f"{metric}_mean"]), 2),
                "Delta": round(float(latest[metric] - baseline[f"{metric}_mean"]), 2),
            }
        )
    return pd.DataFrame(rows)


def load_training_metrics(root: Path) -> dict[str, Any] | None:
    path = root / "model_artifacts" / "training_metrics.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def html_table(df: pd.DataFrame) -> str:
    headers = "".join(f"<th>{html.escape(str(col))}</th>" for col in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = "".join(f"<td>{html.escape(str(value))}</td>" for value in row)
        rows.append(f"<tr>{cells}</tr>")
    return f"""
    <div class="table-shell">
        <table class="cortex-table">
            <thead><tr>{headers}</tr></thead>
            <tbody>{''.join(rows)}</tbody>
        </table>
    </div>
    """

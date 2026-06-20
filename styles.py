from __future__ import annotations

import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Lexend:wght@500;600;700&display=swap');
        :root {
            --cortex-teal: #00685f;
            --cortex-teal-bright: #008378;
            --cortex-indigo: #4b41e1;
            --cortex-rose: #b90538;
            --cortex-bg: #f5faf8;
            --cortex-card: #ffffff;
            --cortex-border: #d8e5e1;
            --cortex-muted: #5b6a67;
            --cortex-text: #17201f;
            --cortex-soft: #e7fbf6;
        }
        .stApp {
            background:
                linear-gradient(130deg, rgba(231, 251, 246, 0.95), rgba(248, 249, 255, 0.88)),
                var(--cortex-bg);
            color: var(--cortex-text);
            font-family: Inter, system-ui, sans-serif;
        }
        .stApp, .stApp p, .stApp span, .stApp label, .stApp div {
            color: var(--cortex-text);
        }
        h1, h2, h3, .brand-title, .card-value {
            font-family: Lexend, Inter, system-ui, sans-serif;
            letter-spacing: 0 !important;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #0b1c30 !important;
        }
        .block-container {
            padding-top: 1.35rem;
            padding-bottom: 3rem;
            max-width: 1180px;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        [data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid var(--cortex-border);
            backdrop-filter: blur(20px);
        }
        [data-testid="stSidebar"] * {
            color: #17201f !important;
        }
        [data-testid="stSidebar"] section,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p {
            color: #17201f !important;
        }
        [data-testid="stSidebar"] small,
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
        [data-testid="stSidebar"] .muted,
        [data-testid="stSidebar"] .small {
            color: #52615e !important;
        }
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
            background: #f7fbfa !important;
            border: 1px dashed #adcac3 !important;
            border-radius: 10px !important;
        }
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {
            color: #17201f !important;
        }
        [data-testid="stSidebar"] [data-testid="stSelectbox"] div,
        [data-testid="stSidebar"] [data-testid="stSelectbox"] input,
        [data-testid="stSidebar"] [data-baseweb="select"] > div {
            background: #ffffff !important;
            color: #17201f !important;
            border-color: #cfe2de !important;
        }
        [data-testid="stSidebar"] [data-testid="stToggle"] label,
        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            color: #17201f !important;
            opacity: 1 !important;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label {
            border: 1px solid transparent;
            border-radius: 8px;
            padding: 9px 10px;
            margin: 4px 0;
            background: #ffffff;
            color: #17201f !important;
            opacity: 1 !important;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: #eef9f6;
            border-color: #cbe7e1;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
            background: #e7fbf6;
            border-color: #8bd8cb;
            box-shadow: inset 3px 0 0 var(--cortex-teal);
        }
        div[data-testid="metric-container"] {
            background: var(--cortex-card);
            border: 1px solid var(--cortex-border);
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 10px 30px rgba(0, 104, 95, 0.06);
        }
        .cortex-brand {
            display: flex;
            gap: 12px;
            align-items: center;
            padding: 12px 4px 18px 4px;
        }
        .brand-mark {
            width: 44px;
            height: 44px;
            border-radius: 12px;
            display: grid;
            place-items: center;
            color: white;
            font-family: Lexend, sans-serif;
            font-weight: 800;
            background: linear-gradient(135deg, var(--cortex-teal), var(--cortex-indigo));
            box-shadow: 0 14px 30px rgba(0, 104, 95, 0.18);
        }
        .brand-title { font-size: 1.1rem; font-weight: 800; }
        .brand-subtitle { color: var(--cortex-muted); font-size: 0.82rem; }
        .page-kicker {
            color: var(--cortex-teal);
            font-weight: 800;
            text-transform: uppercase;
            font-size: 0.78rem;
            letter-spacing: 0.08em;
        }
        .page-title {
            font-family: Lexend, sans-serif;
            font-size: clamp(1.8rem, 3vw, 2.9rem);
            line-height: 1.08;
            margin: 4px 0 8px 0;
            color: #0b1c30;
        }
        .page-subtitle { color: var(--cortex-muted); max-width: 880px; margin-bottom: 20px; }
        .cortex-card {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid var(--cortex-border);
            border-radius: 8px;
            padding: 18px;
            box-shadow: 0 14px 34px rgba(0, 69, 63, 0.07);
            min-height: 120px;
            overflow: hidden;
        }
        .cortex-card.compact { min-height: 94px; padding: 16px; }
        .card-label {
            color: var(--cortex-muted);
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }
        .card-value {
            font-size: clamp(1.55rem, 2.3vw, 2.45rem);
            font-weight: 800;
            color: #0b1c30;
            margin-top: 4px;
        }
        .card-caption { color: var(--cortex-muted); font-size: 0.92rem; margin-top: 5px; }
        .accent-line {
            height: 4px;
            width: 48px;
            border-radius: 999px;
            background: var(--accent, var(--cortex-teal));
            margin-bottom: 12px;
        }
        .status-chip {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            border-radius: 999px;
            padding: 6px 11px;
            font-size: 0.82rem;
            font-weight: 800;
            border: 1px solid #b9efe4;
            color: var(--cortex-teal);
            background: #e7fbf6;
        }
        .chip-dot {
            width: 8px;
            height: 8px;
            border-radius: 999px;
            background: currentColor;
        }
        .chip-warning {
            background: #fff3e6;
            color: #9a4a00;
            border-color: #ffd4a8;
        }
        .chip-critical {
            background: #ffe8ee;
            color: var(--cortex-rose);
            border-color: #ffc1cf;
        }
        .gauge-wrap {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        .recovery-gauge {
            --score: 75;
            --gauge-color: var(--cortex-teal);
            width: 176px;
            height: 176px;
            min-width: 176px;
            border-radius: 50%;
            display: grid;
            place-items: center;
            background: conic-gradient(var(--gauge-color) calc(var(--score) * 1%), #e2ece9 0);
            box-shadow: inset 0 0 0 1px #cbded9, 0 18px 40px rgba(0,104,95,0.14);
        }
        .recovery-gauge-inner {
            width: 124px;
            height: 124px;
            border-radius: 50%;
            background: white;
            display: grid;
            place-items: center;
            text-align: center;
            border: 1px solid var(--cortex-border);
        }
        .gauge-number {
            font-family: Lexend, sans-serif;
            font-size: 2.35rem;
            font-weight: 800;
            line-height: 1;
            color: #0b1c30;
        }
        .gauge-label {
            color: var(--cortex-muted);
            font-size: 0.78rem;
            font-weight: 700;
        }
        .validation-step {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid var(--cortex-border);
            background: #ffffff;
        }
        .step-index {
            width: 28px;
            height: 28px;
            border-radius: 999px;
            display: grid;
            place-items: center;
            color: white;
            font-weight: 800;
            background: var(--cortex-teal);
        }
        .alert-row {
            padding: 12px 14px;
            border-radius: 8px;
            border: 1px solid var(--cortex-border);
            background: #ffffff;
            margin-bottom: 10px;
        }
        .sidebar-badge {
            border: 1px solid #b9efe4;
            border-radius: 8px;
            padding: 12px;
            background: #effbf8;
        }
        .table-shell {
            background: #ffffff;
            border: 1px solid var(--cortex-border);
            border-radius: 8px;
            overflow-x: auto;
            box-shadow: 0 14px 34px rgba(0, 69, 63, 0.05);
        }
        .cortex-table {
            width: 100%;
            border-collapse: collapse;
            min-width: 720px;
            font-size: 0.94rem;
        }
        .cortex-table th {
            background: #eef9f6;
            color: #31423f !important;
            text-align: left;
            padding: 12px 14px;
            border-bottom: 1px solid var(--cortex-border);
            font-weight: 800;
        }
        .cortex-table td {
            background: #ffffff;
            color: #17201f !important;
            padding: 12px 14px;
            border-bottom: 1px solid #edf3f1;
        }
        .cortex-table tr:nth-child(even) td {
            background: #f8fcfb;
        }
        .cortex-table tr:last-child td {
            border-bottom: none;
        }
        .muted { color: var(--cortex-muted); }
        .small { font-size: 0.88rem; }
        @media (max-width: 900px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            .gauge-wrap {
                flex-direction: column;
                align-items: flex-start;
            }
            .page-title {
                font-size: 2rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

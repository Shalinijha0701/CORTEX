from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd


def build_report_pdf(analysis: dict[str, Any]) -> bytes:
    """Create a compact PDF health report for download."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    latest = analysis["latest"]
    baseline = analysis["baseline"]
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title="CORTEX Health Report",
    )
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CortexTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            textColor=colors.HexColor("#00685f"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="CortexBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#17201f"),
        )
    )

    summary_rows = [
        ["User ID", str(latest["user_id"])],
        ["Analysis Date", pd.to_datetime(latest["date"]).strftime("%Y-%m-%d")],
        ["Recovery Score", f"{latest['cortex_recovery_score']}/100"],
        ["Stress Index", f"{latest['stress_index']}/100"],
        ["Sleep Quality", latest["sleep_quality"]],
        ["Health State", latest["cortex_health_state"]],
        ["Confidence", f"{latest['health_state_confidence']}%"],
    ]
    baseline_rows = [
        ["Metric", "Latest", "Baseline"],
        ["HRV", f"{latest['hrv']} ms", f"{baseline['hrv_mean']:.1f} ms"],
        ["Sleep", f"{latest['sleep_hours']} h", f"{baseline['sleep_hours_mean']:.1f} h"],
        ["Resting HR", f"{latest['resting_heart_rate']} bpm", f"{baseline['resting_heart_rate_mean']:.1f} bpm"],
        ["Stress", f"{latest['stress_level']}/100", f"{baseline['stress_level_mean']:.1f}/100"],
        ["SpO2", f"{latest['spo2']}%", f"{baseline['spo2_mean']:.1f}%"],
    ]

    def styled_table(rows: list[list[str]]) -> Table:
        table = Table(rows, colWidths=[1.8 * inch, 4.4 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e7fbf6")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#17201f")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d8e5e1")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fbfa")]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        return table

    story = [
        Paragraph("CORTEX Personalized Health Intelligence Report", styles["CortexTitle"]),
        Paragraph("Personalized wearable-data analysis against the user's own baseline.", styles["CortexBody"]),
        Spacer(1, 12),
        styled_table(summary_rows),
        Spacer(1, 14),
        Paragraph("Baseline Comparison", styles["Heading2"]),
        styled_table(baseline_rows),
        Spacer(1, 14),
        Paragraph("Anomaly Alerts", styles["Heading2"]),
    ]
    for alert in analysis["alerts"]:
        story.append(Paragraph(f"- {alert}", styles["CortexBody"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Recommendations", styles["Heading2"]))
    for item in analysis["recommendations"]:
        story.append(Paragraph(f"- {item}", styles["CortexBody"]))
    story.extend(
        [
            Spacer(1, 16),
            Paragraph(
                "Disclaimer: CORTEX is a wellness intelligence prototype and is not a medical diagnosis tool.",
                styles["CortexBody"],
            ),
        ]
    )
    doc.build(story)
    return buffer.getvalue()

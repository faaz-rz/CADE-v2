"""
Vendor PDF Report Generator — Creates comprehensive vendor analysis PDFs.

Uses ReportLab to generate multi-page reports with charts, tables, and summaries.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime


# ── Colors ──
NAVY = HexColor("#1a365d")
TEAL = HexColor("#0d9488")
GREEN = HexColor("#059669")
RED = HexColor("#dc2626")
AMBER = HexColor("#d97706")
LIGHT_GREY = HexColor("#f3f4f6")
MID_GREY = HexColor("#9ca3af")
DARK_GREY = HexColor("#374151")


def _fmt_currency(value: float) -> str:
    """Format as Indian currency."""
    if abs(value) >= 1e7:
        return f"₹{value/1e7:.2f}Cr"
    if abs(value) >= 1e5:
        return f"₹{value/1e5:.2f}L"
    return f"₹{value:,.0f}"


def _grade_color(grade: str) -> HexColor:
    if grade == "A":
        return GREEN
    if grade == "B":
        return HexColor("#2563eb")
    if grade == "C":
        return AMBER
    return RED


def generate_vendor_report(data: dict) -> bytes:
    """Generate a comprehensive vendor PDF report."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=25*mm,
        bottomMargin=20*mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "VendorTitle",
        parent=styles["Title"],
        fontSize=24,
        textColor=NAVY,
        spaceAfter=6,
    )
    header_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=NAVY,
        spaceBefore=16,
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "VendorBody",
        parent=styles["Normal"],
        fontSize=10,
        textColor=DARK_GREY,
        spaceAfter=4,
    )
    small_style = ParagraphStyle(
        "SmallText",
        parent=styles["Normal"],
        fontSize=8,
        textColor=MID_GREY,
    )

    elements = []
    vendor_name = data.get("vendor_name", "Unknown")
    category = data.get("category", "Unknown")
    grade = data.get("performance_score", {}).get("grade", "N/A")
    fs = data.get("financial_summary", {})

    # ════════════════════════════════════════
    # PAGE 1 — Vendor Overview
    # ════════════════════════════════════════
    elements.append(Paragraph("CADE Hospital", ParagraphStyle(
        "Brand", parent=styles["Normal"],
        fontSize=10, textColor=TEAL, spaceAfter=2,
    )))
    elements.append(Paragraph("Vendor Intelligence Report", title_style))
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        small_style,
    ))
    elements.append(Spacer(1, 8*mm))

    # Vendor info
    elements.append(Paragraph(f"<b>{vendor_name}</b>", ParagraphStyle(
        "VendorName", parent=styles["Heading1"],
        fontSize=20, textColor=NAVY,
    )))
    elements.append(Paragraph(
        f"Category: {category} &nbsp;|&nbsp; "
        f"Risk Level: {data.get('risk_level', 'N/A')} &nbsp;|&nbsp; "
        f"Grade: {grade}",
        body_style,
    ))
    elements.append(Spacer(1, 6*mm))

    # KPI boxes as table
    kpi_data = [
        ["Annual Spend", "Monthly Avg", "Category Share", "Performance Grade"],
        [
            _fmt_currency(fs.get("annual_spend", 0)),
            _fmt_currency(fs.get("monthly_avg", 0)),
            f"{fs.get('category_share_pct', 0):.1f}%",
            grade,
        ],
    ]
    kpi_table = Table(kpi_data, colWidths=[doc.width/4]*4)
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (-1, 1), LIGHT_GREY),
        ("FONTSIZE", (0, 1), (-1, 1), 14),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 1), (-1, 1), NAVY),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, MID_GREY),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 6*mm))

    # Performance Score
    perf = data.get("performance_score", {})
    elements.append(Paragraph("Performance Scorecard", header_style))

    score_data = [
        ["Component", "Score", "Rating"],
        ["Price Competitiveness", f"{perf.get('price_competitiveness', 0)*100:.0f}%",
         "Good" if perf.get("price_competitiveness", 0) > 0.6 else "Needs Improvement"],
        ["Price Stability", f"{perf.get('price_stability', 0)*100:.0f}%",
         "Good" if perf.get("price_stability", 0) > 0.6 else "Needs Improvement"],
        ["Spend Efficiency", f"{perf.get('spend_efficiency', 0)*100:.0f}%",
         "Good" if perf.get("spend_efficiency", 0) > 0.6 else "Needs Improvement"],
        ["Risk Profile", f"{perf.get('risk_score', 0)*100:.0f}%",
         "Good" if perf.get("risk_score", 0) > 0.6 else "Needs Improvement"],
    ]
    score_table = Table(score_data, colWidths=[doc.width*0.4, doc.width*0.25, doc.width*0.35])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GREY]),
        ("GRID", (0, 0), (-1, -1), 0.5, MID_GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 4*mm))

    # Executive summary
    elements.append(Paragraph("Executive Summary", header_style))
    elements.append(Paragraph(
        f"This report covers <b>{vendor_name}</b> procurement analysis. "
        f"Key findings: {len(data.get('product_breakdown', []))} products purchased, "
        f"total spend {_fmt_currency(fs.get('annual_spend', 0))}, "
        f"vendor performance grade <b>{grade}</b>. "
        f"{perf.get('grade_explanation', '')}",
        body_style,
    ))

    # ════════════════════════════════════════
    # PAGE 2 — Financial Analysis
    # ════════════════════════════════════════
    elements.append(PageBreak())
    elements.append(Paragraph("Financial Analysis", title_style))
    elements.append(Spacer(1, 4*mm))

    # Monthly spend table
    elements.append(Paragraph("Monthly Spend Trend", header_style))
    trend = fs.get("monthly_trend", [])
    if trend:
        trend_header = ["Month", "Spend", "Transactions"]
        trend_rows = [trend_header]
        for t in trend[-12:]:  # Last 12 months
            trend_rows.append([
                t["month"],
                _fmt_currency(t["spend"]),
                str(t["transaction_count"]),
            ])
        trend_table = Table(trend_rows, colWidths=[doc.width*0.3, doc.width*0.4, doc.width*0.3])
        trend_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GREY]),
            ("GRID", (0, 0), (-1, -1), 0.5, MID_GREY),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ]))
        elements.append(trend_table)

    elements.append(Spacer(1, 4*mm))

    # Growth analysis
    elements.append(Paragraph("Growth Analysis", header_style))
    growth_text = []
    if fs.get("growth_pct_3m") is not None:
        growth_text.append(f"3-month growth: {fs['growth_pct_3m']:+.1f}%")
    if fs.get("growth_pct_6m") is not None:
        growth_text.append(f"6-month growth: {fs['growth_pct_6m']:+.1f}%")
    growth_text.append(f"vs last month: {fs.get('spend_vs_last_month_pct', 0):+.1f}%")
    growth_text.append(f"YTD spend: {_fmt_currency(fs.get('ytd_spend', 0))}")
    for gt in growth_text:
        elements.append(Paragraph(f"• {gt}", body_style))

    # ════════════════════════════════════════
    # PAGE 3 — Product Analysis
    # ════════════════════════════════════════
    elements.append(PageBreak())
    elements.append(Paragraph("Product Analysis", title_style))
    elements.append(Spacer(1, 4*mm))

    products = data.get("product_breakdown", [])
    if products:
        elements.append(Paragraph(
            f"<b>{len(products)}</b> unique products identified",
            body_style,
        ))
        elements.append(Spacer(1, 3*mm))

        prod_header = ["Product", "Avg Price", "Market Price", "vs Market", "Trend"]
        prod_rows = [prod_header]
        for p in products[:15]:  # Top 15
            market = _fmt_currency(p["market_benchmark_price"]) if p["market_benchmark_price"] else "N/A"
            vs_mkt = f"{p['vs_market_pct']:+.1f}%" if p["vs_market_pct"] is not None else "—"
            prod_rows.append([
                p["product_name"][:30],
                _fmt_currency(p["avg_unit_price"]),
                market,
                vs_mkt,
                p["price_trend"],
            ])
        prod_table = Table(prod_rows, colWidths=[
            doc.width*0.30, doc.width*0.18, doc.width*0.18,
            doc.width*0.17, doc.width*0.17,
        ])
        prod_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GREY]),
            ("GRID", (0, 0), (-1, -1), 0.5, MID_GREY),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ]))
        elements.append(prod_table)

        # Overpayment summary
        overpaying = [p for p in products if p.get("overpaying")]
        if overpaying:
            elements.append(Spacer(1, 4*mm))
            total_overpay = sum(
                (p["avg_unit_price"] - (p["market_benchmark_price"] or 0)) * p["monthly_volume"] * 12
                for p in overpaying
                if p["market_benchmark_price"]
            )
            elements.append(Paragraph(
                f"⚠ Overpaying on {len(overpaying)} products vs market rates. "
                f"Potential saving: {_fmt_currency(total_overpay)}/year.",
                ParagraphStyle("Warning", parent=body_style, textColor=RED),
            ))
    else:
        elements.append(Paragraph(
            "No itemized product data available. Upload purchase register for breakdown.",
            body_style,
        ))

    # ════════════════════════════════════════
    # PAGE 4 — Competitive Analysis
    # ════════════════════════════════════════
    elements.append(PageBreak())
    elements.append(Paragraph("Competitive Analysis", title_style))
    elements.append(Spacer(1, 4*mm))

    comp = data.get("competitive_position", {})
    cat_vendors = comp.get("category_vendors", [])
    if cat_vendors:
        cv_header = ["Rank", "Vendor", "Annual Spend", "Current"]
        cv_rows = [cv_header]
        for v in cat_vendors:
            cv_rows.append([
                str(v["price_rank"]),
                v["vendor_name"][:25],
                _fmt_currency(v["annual_spend"]),
                "✓" if v["is_current_vendor"] else "",
            ])
        cv_table = Table(cv_rows, colWidths=[
            doc.width*0.1, doc.width*0.4, doc.width*0.3, doc.width*0.2,
        ])
        cv_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GREY]),
            ("GRID", (0, 0), (-1, -1), 0.5, MID_GREY),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (2, 0), (2, -1), "RIGHT"),
            ("ALIGN", (3, 0), (3, -1), "CENTER"),
        ]))
        elements.append(cv_table)

    elements.append(Spacer(1, 4*mm))
    elements.append(Paragraph(
        f"Switching Recommendation: {comp.get('switching_recommendation', 'N/A')}",
        body_style,
    ))
    if comp.get("potential_saving_if_switched", 0) > 0:
        elements.append(Paragraph(
            f"Estimated saving: {_fmt_currency(comp['potential_saving_if_switched'])}/year",
            ParagraphStyle("SaveGreen", parent=body_style, textColor=GREEN),
        ))

    # ════════════════════════════════════════
    # PAGE 5 — Risk and Actions
    # ════════════════════════════════════════
    elements.append(PageBreak())
    elements.append(Paragraph("Risk Analysis & Priority Actions", title_style))
    elements.append(Spacer(1, 4*mm))

    # Decisions
    decisions = data.get("decisions", [])
    if decisions:
        elements.append(Paragraph("Active CADE Decisions", header_style))
        for d in decisions:
            elements.append(Paragraph(
                f"• <b>{d['title']}</b> — {d['risk_level']} risk, "
                f"Impact: {_fmt_currency(d['annual_impact'])}, "
                f"Status: {d['status']}",
                body_style,
            ))
    elements.append(Spacer(1, 4*mm))

    # Priority actions
    actions = data.get("recommended_actions", [])
    if actions:
        elements.append(Paragraph("Priority Actions", header_style))
        for a in actions:
            saving_text = f" — Save {_fmt_currency(a['estimated_saving'])}" if a["estimated_saving"] > 0 else ""
            elements.append(Paragraph(
                f"[{a['priority']}] <b>{a['title']}</b>{saving_text}",
                body_style,
            ))
            elements.append(Paragraph(f"  {a['description']}", small_style))

    # ════════════════════════════════════════
    # PAGE 6 — Contract Information
    # ════════════════════════════════════════
    elements.append(PageBreak())
    elements.append(Paragraph("Contract & AMC Information", title_style))
    elements.append(Spacer(1, 4*mm))

    ci = data.get("contract_info", {})
    elements.append(Paragraph(
        f"Contract Type: <b>{ci.get('contract_type', 'Standard')}</b>",
        body_style,
    ))
    elements.append(Paragraph(
        f"Renewal Date: <b>{ci.get('renewal_date', 'N/A')}</b> "
        f"({ci.get('days_until_renewal', 0)} days)",
        body_style,
    ))

    if ci.get("is_amc"):
        elements.append(Spacer(1, 3*mm))
        elements.append(Paragraph("AMC Analysis", header_style))
        elements.append(Paragraph(
            f"Current AMC Rate: {ci.get('amc_rate_current', 0):.0%}",
            body_style,
        ))
        elements.append(Paragraph(
            f"Market AMC Rate: {ci.get('amc_rate_market', 0):.0%}",
            body_style,
        ))
        elements.append(Paragraph(
            f"Annual Saving Opportunity: "
            f"{_fmt_currency(ci.get('amc_saving_opportunity', 0))}",
            ParagraphStyle("AMCSaving", parent=body_style, textColor=GREEN),
        ))
        elements.append(Spacer(1, 3*mm))
        elements.append(Paragraph("Negotiation Checklist:", header_style))
        checklist = [
            "Obtain quotes from 2 alternative service providers",
            "Calculate cost of extended warranty vs AMC",
            "Review last year's service call frequency",
            "Prepare competitive tender document",
        ]
        for item in checklist:
            elements.append(Paragraph(f"☐ {item}", body_style))

    elements.append(Spacer(1, 6*mm))
    elements.append(Paragraph(ci.get("negotiation_tip", ""), body_style))

    # Footer
    elements.append(Spacer(1, 10*mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=MID_GREY))
    elements.append(Paragraph(
        f"CADE Hospital — Confidential Vendor Report — {datetime.now().strftime('%B %Y')}",
        ParagraphStyle("Footer", parent=small_style, alignment=TA_CENTER),
    ))

    doc.build(elements)
    return buffer.getvalue()

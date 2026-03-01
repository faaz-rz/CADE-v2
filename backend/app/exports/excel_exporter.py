"""
Excel Executive Report Exporter — 3-sheet workbook using openpyxl.

Sheet 1: Executive Summary (aggregated KPIs)
Sheet 2: Vendor Concentration (per-vendor exposure detail)
Sheet 3: Decision Log (full decision audit trail)
"""

from io import BytesIO
from datetime import datetime
from typing import List

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, numbers, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from app.models.exposure import FinancialExposure
from app.models.decision import Decision
from app.services.exposure_engine import calculate_all_exposures
from app.services.decision_store import DecisionStore


# --- Styling Constants ---
HEADER_FONT = Font(name="Calibri", bold=True, size=11, color="FFFFFF")
HEADER_FILL = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
HEADER_ALIGNMENT = Alignment(horizontal="center", vertical="center", wrap_text=True)
CURRENCY_FORMAT = '#,##0.00'
PERCENT_FORMAT = '0.00%'
THIN_BORDER = Border(
    left=Side(style="thin", color="D9D9D9"),
    right=Side(style="thin", color="D9D9D9"),
    top=Side(style="thin", color="D9D9D9"),
    bottom=Side(style="thin", color="D9D9D9"),
)


def _style_header_row(ws, num_cols: int):
    """Apply consistent header styling and freeze top row."""
    for col_idx in range(1, num_cols + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = HEADER_ALIGNMENT
        cell.border = THIN_BORDER
    ws.freeze_panes = "A2"


def _auto_size_columns(ws):
    """Auto-size column widths based on content."""
    for col_cells in ws.columns:
        max_length = 0
        col_letter = get_column_letter(col_cells[0].column)
        for cell in col_cells:
            if cell.value is not None:
                max_length = max(max_length, len(str(cell.value)))
        ws.column_dimensions[col_letter].width = min(max_length + 4, 40)


def _build_executive_summary(wb: Workbook, exposures: List[FinancialExposure], decisions: List[Decision]):
    """Sheet 1: Executive Summary KPIs."""
    ws = wb.active
    ws.title = "Executive Summary"

    headers = ["Metric", "Value"]
    ws.append(headers)

    total_exposure = sum(e.worst_case_exposure for e in exposures)
    total_spend = sum(e.annual_spend for e in exposures)
    high_risk_vendors = len([d for d in decisions if d.risk_level.value == "HIGH"])

    # Projected EBITDA impact = sum of all 10% shock ebitda deltas as baseline indicator
    projected_ebitda_impact = sum(e.estimated_ebitda_delta_10pct for e in exposures)

    total_opportunity = sum(d.annual_impact for d in decisions)

    kpis = [
        ("Total Identified Opportunity", total_opportunity),
        ("Total Vendor Spend", total_spend),
        ("Total Worst-Case Exposure", total_exposure),
        ("High Risk Vendors", high_risk_vendors),
        ("Projected EBITDA Impact (10% Shock)", projected_ebitda_impact),
        ("Report Generated", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")),
    ]

    for label, value in kpis:
        ws.append([label, value])

    # Format currency cells
    for row_idx in range(2, len(kpis) + 2):
        cell = ws.cell(row=row_idx, column=2)
        if isinstance(cell.value, (int, float)):
            cell.number_format = CURRENCY_FORMAT

    _style_header_row(ws, len(headers))
    _auto_size_columns(ws)


def _build_vendor_concentration(wb: Workbook, exposures: List[FinancialExposure]):
    """Sheet 2: Per-vendor concentration and exposure detail."""
    ws = wb.create_sheet("Vendor Concentration")

    headers = [
        "Vendor", "Category", "Annual Spend", "Share %",
        "Worst Case Exposure", "10% Shock Impact", "20% Shock Impact",
    ]
    ws.append(headers)

    for exp in sorted(exposures, key=lambda e: e.annual_spend, reverse=True):
        ws.append([
            exp.vendor_id,
            exp.category,
            exp.annual_spend,
            exp.vendor_share_pct,
            exp.worst_case_exposure,
            exp.price_shock_impact_10pct,
            exp.price_shock_impact_20pct,
        ])

    # Format columns
    for row_idx in range(2, ws.max_row + 1):
        # Currency columns: C, E, F, G (3, 5, 6, 7)
        for col_idx in [3, 5, 6, 7]:
            ws.cell(row=row_idx, column=col_idx).number_format = CURRENCY_FORMAT
        # Percentage column: D (4)
        ws.cell(row=row_idx, column=4).number_format = PERCENT_FORMAT

    _style_header_row(ws, len(headers))
    _auto_size_columns(ws)


def _build_decision_log(wb: Workbook, decisions: List[Decision]):
    """Sheet 3: Full decision log with events."""
    ws = wb.create_sheet("Decision Log")

    headers = [
        "Decision ID", "Vendor", "Recommendation", "Annual Impact",
        "Risk Level", "Status", "Created At",
    ]
    ws.append(headers)

    for d in decisions:
        ws.append([
            d.id,
            d.entity,
            d.recommended_action,
            d.annual_impact,
            d.risk_level.value,
            d.status.value,
            d.created_at.strftime("%Y-%m-%d %H:%M"),
        ])

    # Currency column: D (4)
    for row_idx in range(2, ws.max_row + 1):
        ws.cell(row=row_idx, column=4).number_format = CURRENCY_FORMAT

    _style_header_row(ws, len(headers))
    _auto_size_columns(ws)


def generate_executive_report() -> BytesIO:
    """
    Generate the full 3-sheet Executive Report workbook.
    Returns a BytesIO buffer containing the .xlsx file.
    """
    exposures = calculate_all_exposures()
    decisions = DecisionStore.get_all_decisions()

    # Enrich decisions with events
    for d in decisions:
        d.events = DecisionStore.get_events_for_decision(d.id)

    wb = Workbook()

    _build_executive_summary(wb, exposures, decisions)
    _build_vendor_concentration(wb, exposures)
    _build_decision_log(wb, decisions)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

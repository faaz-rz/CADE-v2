import logging
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse, JSONResponse

from app.exports.excel_exporter import generate_executive_report
from app.services.decision_store import DecisionStore
from app.services.exposure_engine import calculate_all_exposures, EBITDA_MARGIN
from app.services.ai_narrator import generate_board_narrative

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/executive_report")
async def export_executive_report(
    include_ai: bool = Query(True, description="Include AI-generated narrative"),
):
    """
    Generate and download the Executive Board Report as an Excel file.
    Pass ?include_ai=false to skip the Groq API call.
    """
    # ── Gather data ──
    decisions = DecisionStore.get_all_decisions()

    if not decisions:
        return JSONResponse(
            status_code=422,
            content={"error": "No data found. Please upload a file first."},
        )

    exposures = calculate_all_exposures()

    # ── Compute stats ──
    total_spend = sum(e.annual_spend for e in exposures)
    high_risk = [d for d in decisions if d.risk_level.value == "HIGH"]
    medium_risk = [d for d in decisions if d.risk_level.value == "MEDIUM"]

    top_vendor = max(exposures, key=lambda e: e.annual_spend) if exposures else None
    top_vendor_name = top_vendor.vendor_id if top_vendor else "N/A"
    top_vendor_spend = top_vendor.annual_spend if top_vendor else 0.0

    estimated_savings = sum(d.annual_impact for d in decisions)
    ebitda_at_risk = total_spend * 0.10 * EBITDA_MARGIN

    # ── AI Narrative ──
    narrative = None
    if include_ai:
        try:
            narrative = await generate_board_narrative(
                total_spend=total_spend,
                high_risk_count=len(high_risk),
                top_vendor_name=top_vendor_name,
                top_vendor_spend=top_vendor_spend,
                decision_count=len(decisions),
                estimated_savings=estimated_savings,
                ebitda_at_risk=ebitda_at_risk,
            )
        except Exception as e:
            logger.warning(f"AI narrative generation failed: {e}")
            narrative = None  # excel_exporter handles None gracefully

    # ── Generate workbook ──
    buffer = generate_executive_report(
        decisions=decisions,
        exposures=exposures,
        narrative=narrative,
        total_spend=total_spend,
        high_risk_count=len(high_risk),
        medium_risk_count=len(medium_risk),
        decision_count=len(decisions),
        estimated_savings=estimated_savings,
        ebitda_at_risk=ebitda_at_risk,
        vendor_count=len(exposures),
    )

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=executive_report.xlsx"
        },
    )

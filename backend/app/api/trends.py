"""
Trend Alerts API — vendor spend trend analysis and alerts.
"""

from fastapi import APIRouter
from app.services.trend_engine import calculate_vendor_trends, get_trend_alerts

router = APIRouter()


@router.get("/alerts")
async def get_alerts():
    """
    Returns trend-based alerts sorted by severity.
    Includes alert counts by severity level.
    """
    trends = calculate_vendor_trends()
    alerts = get_trend_alerts(trends)
    return {
        "alerts": alerts,
        "total": len(alerts),
        "high": len([a for a in alerts if a["severity"] == "HIGH"]),
        "medium": len([a for a in alerts if a["severity"] == "MEDIUM"]),
        "low": len([a for a in alerts if a["severity"] == "LOW"]),
    }


@router.get("/vendors")
async def get_vendor_trends():
    """
    Returns trend data for all vendors with monthly spend breakdowns.
    """
    trends = calculate_vendor_trends()
    return {
        "vendors": [t.model_dump() for t in trends],
        "total": len(trends),
    }

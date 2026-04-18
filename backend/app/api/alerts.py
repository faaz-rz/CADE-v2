"""
Hospital Alerts API — Serves procurement alerts for the notification system.

GET /api/alerts → all alerts with counts
"""

from fastapi import APIRouter
from dataclasses import asdict
from app.services.hospital_alerts import HospitalAlertsEngine

router = APIRouter()


@router.get("")
async def get_alerts():
    """Returns all hospital procurement alerts with severity counts."""
    alerts = HospitalAlertsEngine.generate_alerts()
    unread = [a for a in alerts if not a.is_read]

    return {
        "total": len(alerts),
        "unread": len(unread),
        "critical": len([a for a in alerts if a.severity == "CRITICAL"]),
        "high": len([a for a in alerts if a.severity == "HIGH"]),
        "medium": len([a for a in alerts if a.severity == "MEDIUM"]),
        "low": len([a for a in alerts if a.severity == "LOW"]),
        "alerts": [asdict(a) for a in alerts],
    }

"""
Contract Renewal Calendar — Simulated renewal dates for vendor contracts.

Uses a deterministic hash-based approach to assign renewal dates
since the system doesn't have real contract date data yet.
"""

import hashlib
from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.exposure_engine import calculate_all_exposures
from app.core.auth import verify_token

router = APIRouter()


def get_renewal_date(vendor_name: str) -> date:
    """
    Deterministic renewal date based on vendor name.
    Spreads renewals across next 12 months.
    """
    hash_val = int(hashlib.md5(vendor_name.encode()).hexdigest(), 16)
    days_ahead = (hash_val % 365) + 1
    return date.today() + timedelta(days=days_ahead)


class ContractRenewal(BaseModel):
    vendor_name: str
    category: str
    annual_spend: float
    renewal_date: date
    days_until_renewal: int
    recommended_action: str
    potential_savings: float


@router.get("/renewals")
def get_renewals(payload: dict = Depends(verify_token)):
    """
    Returns vendor contract renewals bucketed into urgent/upcoming/planned.
    """
    exposures = calculate_all_exposures()

    urgent: List[dict] = []
    upcoming: List[dict] = []
    planned: List[dict] = []

    for exp in exposures:
        renewal_date = get_renewal_date(exp.vendor_id)
        days_until = (renewal_date - date.today()).days

        if days_until > 90:
            continue

        if days_until <= 30:
            action = "Start negotiation immediately"
        elif days_until <= 60:
            action = "Schedule vendor review meeting"
        else:
            action = "Begin market comparison"

        potential_savings = round(exp.annual_spend * 0.15, 2)

        renewal = {
            "vendor_name": exp.vendor_id,
            "category": exp.category,
            "annual_spend": exp.annual_spend,
            "renewal_date": renewal_date.isoformat(),
            "days_until_renewal": days_until,
            "recommended_action": action,
            "potential_savings": potential_savings,
        }

        if days_until <= 30:
            urgent.append(renewal)
        elif days_until <= 60:
            upcoming.append(renewal)
        else:
            planned.append(renewal)

    # Sort each bucket by days ascending
    urgent.sort(key=lambda r: r["days_until_renewal"])
    upcoming.sort(key=lambda r: r["days_until_renewal"])
    planned.sort(key=lambda r: r["days_until_renewal"])

    total_savings = sum(r["potential_savings"] for r in urgent + upcoming + planned)

    return {
        "urgent": urgent,
        "upcoming": upcoming,
        "planned": planned,
        "total_renewals_90_days": len(urgent) + len(upcoming) + len(planned),
        "total_savings_opportunity": round(total_savings, 2),
    }

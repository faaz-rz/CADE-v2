"""
Trend Engine — Simplified time-series analysis.

Aggregates monthly spend per vendor, computes rolling averages,
and flags emerging risk based on percentage growth.

Simplified per user request: rolling average + % growth (no linear regression).
"""

import json
import os
from collections import defaultdict
from typing import List, Optional

from app.models.canonical import CanonicalFinancialRecord
from app.models.trend import VendorTrend, MonthlySpend

# Configurable threshold: if 3-month growth > this %, flag as emerging risk
EMERGING_RISK_THRESHOLD_PCT: float = 20.0


def _load_records() -> List[CanonicalFinancialRecord]:
    """Load canonical records from the persisted JSON file."""
    data_file = "data/transactions.json"
    if not os.path.exists(data_file):
        return []
    try:
        with open(data_file, "r") as f:
            raw = json.load(f)
        return [CanonicalFinancialRecord(**r) for r in raw]
    except Exception:
        return []


def _rolling_average(values: List[float], window: int) -> Optional[float]:
    """Calculate rolling average over the last `window` values."""
    if len(values) < window:
        return None
    return sum(values[-window:]) / window


def _growth_pct(values: List[float], window: int) -> Optional[float]:
    """
    Calculate % growth over the last `window` months.
    Compares average of last `window` months vs the `window` months before that.
    """
    if len(values) < window * 2:
        return None
    recent = sum(values[-window:]) / window
    earlier = sum(values[-window * 2:-window]) / window
    if earlier == 0:
        return None
    return ((recent - earlier) / earlier) * 100.0


def calculate_vendor_trends() -> List[VendorTrend]:
    """
    Calculate spend trends for all vendors.
    Deterministic for the same dataset.
    """
    records = _load_records()
    if not records:
        return []

    # Aggregate monthly spend per vendor
    # Key: (vendor, "YYYY-MM") → total spend
    monthly: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

    for r in records:
        month_key = r.date.strftime("%Y-%m")
        monthly[r.entity][month_key] += r.amount

    trends = []
    for vendor_id, month_data in sorted(monthly.items()):
        # Sort months chronologically
        sorted_months = sorted(month_data.keys())
        monthly_spends = [
            MonthlySpend(month=m, total_spend=month_data[m])
            for m in sorted_months
        ]
        spend_values = [ms.total_spend for ms in monthly_spends]

        avg_3m = _rolling_average(spend_values, 3)
        avg_6m = _rolling_average(spend_values, 6)
        growth_3m = _growth_pct(spend_values, 3)
        growth_6m = _growth_pct(spend_values, 6)

        is_emerging_risk = (
            growth_3m is not None and growth_3m > EMERGING_RISK_THRESHOLD_PCT
        )

        trends.append(VendorTrend(
            vendor_id=vendor_id,
            monthly_spends=monthly_spends,
            rolling_avg_3m=avg_3m,
            rolling_avg_6m=avg_6m,
            growth_pct_3m=growth_3m,
            growth_pct_6m=growth_6m,
            is_emerging_risk=is_emerging_risk,
        ))

    return trends


def get_trend_for_vendor(vendor_id: str) -> Optional[VendorTrend]:
    """Get trend data for a specific vendor."""
    trends = calculate_vendor_trends()
    return next((t for t in trends if t.vendor_id == vendor_id), None)


def get_trend_alerts(vendors: Optional[List[VendorTrend]] = None) -> List[dict]:
    """
    Generate actionable alerts from vendor trend data.

    Alert types:
      - RAPID_GROWTH:    3-month growth > 20%
      - EMERGING_RISK:   Flagged by is_emerging_risk threshold
      - DECLINING_SPEND: 3-month growth < -30%

    Returns list of alert dicts sorted by severity then |growth_rate|.
    """
    if vendors is None:
        vendors = calculate_vendor_trends()

    alerts: List[dict] = []

    for vendor in vendors:
        growth_3m = vendor.growth_pct_3m  # Percentage value: 25.0 = 25%
        avg_3m = vendor.rolling_avg_3m or 0.0
        avg_6m = vendor.rolling_avg_6m or 0.0

        # Alert 1: Rapid growth
        if growth_3m is not None and growth_3m > 20.0:
            growth_rate = growth_3m / 100.0  # Convert to ratio for display
            severity = "HIGH" if growth_3m > 50.0 else "MEDIUM"
            alerts.append({
                "vendor": vendor.vendor_id,
                "alert_type": "RAPID_GROWTH",
                "severity": severity,
                "title": f"{vendor.vendor_id} spend up {growth_rate:.0%} in 3 months",
                "message": (
                    f"Monthly spend has grown from "
                    f"${avg_6m:,.0f} to ${avg_3m:,.0f} average. "
                    f"Review usage before next billing cycle."
                ),
                "growth_rate": growth_rate,
                "avg_spend_3m": avg_3m,
                "avg_spend_6m": avg_6m,
            })

        # Alert 2: Emerging risk flag (may overlap with rapid growth)
        if vendor.is_emerging_risk and (growth_3m is None or growth_3m <= 20.0):
            growth_rate = (growth_3m / 100.0) if growth_3m is not None else 0.0
            alerts.append({
                "vendor": vendor.vendor_id,
                "alert_type": "EMERGING_RISK",
                "severity": "MEDIUM",
                "title": f"{vendor.vendor_id} flagged as emerging risk",
                "message": (
                    f"3-month growth trend indicates this vendor "
                    f"may become a material spend risk. "
                    f"Current average: ${avg_3m:,.0f}/month."
                ),
                "growth_rate": growth_rate,
                "avg_spend_3m": avg_3m,
            })

        # Alert 3: Declining spend (potential churn or unused tool)
        if growth_3m is not None and growth_3m < -30.0:
            growth_rate = growth_3m / 100.0
            alerts.append({
                "vendor": vendor.vendor_id,
                "alert_type": "DECLINING_SPEND",
                "severity": "LOW",
                "title": f"{vendor.vendor_id} spend declining sharply",
                "message": (
                    f"Spend dropped {abs(growth_rate):.0%} over 3 months. "
                    f"Verify this tool is still being used — if not, cancel the contract."
                ),
                "growth_rate": growth_rate,
            })

    # Sort by severity then growth rate magnitude
    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    alerts.sort(key=lambda x: (
        severity_order.get(x["severity"], 99),
        -abs(x.get("growth_rate", 0))
    ))
    return alerts

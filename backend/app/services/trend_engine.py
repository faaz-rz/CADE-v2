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

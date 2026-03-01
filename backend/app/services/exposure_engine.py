"""
Financial Exposure Engine — Deterministic exposure calculations.

All functions are pure: same inputs → same outputs, no randomness.
EBITDA_MARGIN is configurable but defaults to 0.25.
"""

from typing import List, Tuple
from app.models.exposure import FinancialExposure
from app.services.analytics import VendorStats, SpendingAnalyzer

# Configurable EBITDA Margin (default 25%)
EBITDA_MARGIN: float = 0.25


def calculate_shock_impact(annual_spend: float, shock_pct: float) -> Tuple[float, float]:
    """
    Reusable shock calculation.
    Returns: (price_shock_impact, estimated_ebitda_delta)
    """
    shock_impact = annual_spend * (shock_pct / 100.0)
    ebitda_delta = shock_impact * EBITDA_MARGIN
    return shock_impact, ebitda_delta


def calculate_exposure(vendor: VendorStats) -> FinancialExposure:
    """
    Calculate financial exposure for a single vendor.
    Deterministic: identical VendorStats → identical FinancialExposure.
    """
    annual_spend = vendor.total_spend
    vendor_share_pct = vendor.vendor_share_of_category
    worst_case_exposure = annual_spend * vendor_share_pct

    shock_10, ebitda_10 = calculate_shock_impact(annual_spend, 10.0)
    shock_20, ebitda_20 = calculate_shock_impact(annual_spend, 20.0)

    return FinancialExposure(
        vendor_id=vendor.entity,
        annual_spend=annual_spend,
        vendor_share_pct=vendor_share_pct,
        category=vendor.category,
        worst_case_exposure=worst_case_exposure,
        price_shock_impact_10pct=shock_10,
        price_shock_impact_20pct=shock_20,
        estimated_ebitda_delta_10pct=ebitda_10,
        estimated_ebitda_delta_20pct=ebitda_20,
    )


def calculate_all_exposures() -> List[FinancialExposure]:
    """
    Calculate exposure for every vendor in the current dataset.
    """
    vendor_stats = SpendingAnalyzer.get_vendor_stats()
    return [calculate_exposure(stats) for stats in vendor_stats.values()]


def get_exposure_for_vendor(vendor_id: str) -> FinancialExposure | None:
    """
    Calculate exposure for a specific vendor.
    Returns None if vendor not found.
    """
    vendor_stats = SpendingAnalyzer.get_vendor_stats()
    stats = vendor_stats.get(vendor_id)
    if stats is None:
        return None
    return calculate_exposure(stats)

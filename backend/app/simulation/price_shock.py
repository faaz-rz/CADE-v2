"""
Price Shock Simulator — Deterministic price shock impact analysis.

Reuses exposure_engine.calculate_shock_impact() for all shock math.
No duplication of logic.
"""

from pydantic import BaseModel
from app.services.exposure_engine import calculate_shock_impact, EBITDA_MARGIN
from app.services.analytics import SpendingAnalyzer
from app.services.policy_engine import policy_engine


class PriceShockRequest(BaseModel):
    vendor_id: str
    shock_percentage: float


class PriceShockResponse(BaseModel):
    base_spend: float
    shock_percentage: float
    new_spend: float
    delta_spend: float
    estimated_ebitda_delta: float
    risk_classification_shift: str


def simulate_price_shock(request: PriceShockRequest) -> PriceShockResponse:
    """
    Simulate a price shock for a given vendor.
    Deterministic: same (vendor_id, shock_percentage) → same result.
    """
    vendor_stats = SpendingAnalyzer.get_vendor_stats()
    stats = vendor_stats.get(request.vendor_id)
    if stats is None:
        raise ValueError(f"Vendor '{request.vendor_id}' not found in dataset")

    base_spend = stats.total_spend

    # Reuse exposure engine calculation — no duplication
    delta_spend, ebitda_delta = calculate_shock_impact(base_spend, request.shock_percentage)
    new_spend = base_spend + delta_spend

    # Risk classification shift logic:
    # If the shock pushes the new spend above the policy spend_threshold AND
    # the vendor concentration is high, classify as HIGH risk shift
    policy = policy_engine.get_policy(stats.category)
    spend_threshold = policy.get("spend_threshold", 5000)

    # Calculate post-shock worst-case exposure
    post_shock_exposure = new_spend * stats.vendor_share_of_category

    if spend_threshold > 0 and post_shock_exposure > (spend_threshold * 2):
        risk_shift = "HIGH"
    elif spend_threshold > 0 and post_shock_exposure > spend_threshold:
        risk_shift = "MEDIUM"
    else:
        risk_shift = "LOW"

    # Determine if this is actually a *shift* from the pre-shock state
    pre_shock_exposure = base_spend * stats.vendor_share_of_category
    if spend_threshold > 0 and pre_shock_exposure <= spend_threshold and post_shock_exposure > spend_threshold:
        risk_classification_shift = f"ESCALATED → {risk_shift}"
    elif spend_threshold > 0 and pre_shock_exposure <= (spend_threshold * 2) and post_shock_exposure > (spend_threshold * 2):
        risk_classification_shift = f"ESCALATED → {risk_shift}"
    else:
        risk_classification_shift = f"UNCHANGED ({risk_shift})"

    return PriceShockResponse(
        base_spend=base_spend,
        shock_percentage=request.shock_percentage,
        new_spend=new_spend,
        delta_spend=delta_spend,
        estimated_ebitda_delta=ebitda_delta,
        risk_classification_shift=risk_classification_shift,
    )

from pydantic import BaseModel


class FinancialExposure(BaseModel):
    """
    Financial exposure profile for a single vendor.
    All calculations are deterministic and reproducible.
    """
    vendor_id: str
    annual_spend: float
    vendor_share_pct: float
    category: str
    worst_case_exposure: float
    price_shock_impact_10pct: float
    price_shock_impact_20pct: float
    estimated_ebitda_delta_10pct: float
    estimated_ebitda_delta_20pct: float

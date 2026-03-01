from pydantic import BaseModel
from typing import List, Optional


class MonthlySpend(BaseModel):
    """Single month spend data point."""
    month: str  # Format: "YYYY-MM"
    total_spend: float


class VendorTrend(BaseModel):
    """
    Trend analysis for a single vendor.
    Simplified: rolling average + percentage growth.
    """
    vendor_id: str
    monthly_spends: List[MonthlySpend]
    rolling_avg_3m: Optional[float] = None
    rolling_avg_6m: Optional[float] = None
    growth_pct_3m: Optional[float] = None
    growth_pct_6m: Optional[float] = None
    is_emerging_risk: bool = False

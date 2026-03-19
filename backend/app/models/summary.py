from pydantic import BaseModel
from typing import Dict

class DecisionSummary(BaseModel):
    """
    Executive Summary of the current decision portfolio.
    """
    total_savings: float
    total_decisions: int
    pending_count: int
    pending_high_impact: int
    impact_breakdown: Dict[str, int] # e.g. {"HIGH": 5, "MEDIUM": 2, "LOW": 10}
    risk_breakdown: Dict[str, int]   # e.g. {"LOW": 15, "MEDIUM": 2}

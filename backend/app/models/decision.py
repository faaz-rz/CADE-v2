from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field

class DecisionScope(str, Enum):
    """
    Prevents accidental scope creep and makes future expansion explicit.
    """
    COST = "COST"
    VENDOR = "VENDOR"
    PROJECT = "PROJECT"

class DecisionType(str, Enum):
    VENDOR_REDUCE = "VENDOR_REDUCE"
    PROJECT_PAUSE = "PROJECT_PAUSE"
    SUBSCRIPTION_CANCEL = "SUBSCRIPTION_CANCEL"
    COST_ANOMALY = "COST_ANOMALY"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class DecisionStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class Decision(BaseModel):
    """
    First-class Decision object.
    Everything (UI, audit, integration) hangs off this.
    """
    id: str
    decision_type: DecisionType
    scope: DecisionScope
    entity: str = Field(..., description="Target entity name (e.g., Vendor Name, Project Name)")
    
    recommended_action: str
    explanation: str
    
    # Financial Impact
    expected_monthly_impact: float
    cost_of_inaction: float
    
    # Intelligence & Risk
    risk_level: RiskLevel
    risk_range: Dict[str, float] = Field(..., description="Dictionary with 'best_case' and 'worst_case' keys")
    confidence: float = Field(..., ge=0.0, le=1.0)
    
    # State
    status: DecisionStatus = DecisionStatus.PENDING
    rejection_reason: Optional[str] = None

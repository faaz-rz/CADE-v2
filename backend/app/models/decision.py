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
    VENDOR_CONSOLIDATE = "VENDOR_CONSOLIDATE"
    PROJECT_PAUSE = "PROJECT_PAUSE"
    SUBSCRIPTION_CANCEL = "SUBSCRIPTION_CANCEL"
    COST_ANOMALY = "COST_ANOMALY"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class ImpactLabel(str, Enum):
    HIGH = "HIGH"    # > $10k
    MEDIUM = "MEDIUM" # > $1k
    LOW = "LOW"      # <= $1k

class DecisionStatus(str, Enum):
    PENDING = "PENDING"
# ... (DecisionStatus enum content if any)

class DecisionContext(BaseModel):
    # ... (existing content)
    analysis_period: str
    rule_id: str
    thresholds: Dict[str, float]
    metrics: Dict[str, float] # Evidence used

class Decision(BaseModel):
    # ... (existing content)
    id: str
    decision_type: DecisionType
    scope: DecisionScope
    entity: str = Field(..., description="Target entity name (e.g., Vendor Name, Project Name)")
    
    recommended_action: str
    explanation: str
    
    # Context & Evidence (New Block)
    context: DecisionContext

    # Financial Impact
    expected_monthly_impact: float
    cost_of_inaction: float
    
    # Prioritization (New Block)
    annual_impact: float
    impact_label: ImpactLabel
    
    # Intelligence & Risk
    risk_level: RiskLevel
    risk_range: Dict[str, float] = Field(..., description="Dictionary with 'best_case' and 'worst_case' keys")
    confidence: float = Field(..., ge=0.0, le=1.0)
    
    # State
    status: DecisionStatus = DecisionStatus.PENDING
    rejection_reason: Optional[str] = None

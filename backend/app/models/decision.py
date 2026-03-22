from enum import Enum
from typing import Dict, Optional, List
from datetime import datetime
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
    COST_REDUCE = "COST_REDUCE"
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
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"

class DecisionEventType(str, Enum):
    CREATED = "CREATED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"
    REOPENED = "REOPENED"

class DecisionEvent(BaseModel):
    """
    Immutable Audit Log Entry.
    Source of truth for history.
    """
    id: str
    decision_id: str
    event_type: DecisionEventType
    previous_status: Optional[DecisionStatus]
    new_status: DecisionStatus
    actor_id: str = "system" # Default to system for now
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DecisionContext(BaseModel):
    """
    Structured context for the decision.
    Makes the decision auditable and reproducible.
    """
    analysis_period: str
    rule_id: str
    thresholds: Dict[str, float]
    metrics: Dict[str, float] # Evidence used
    vendor_share_of_category: float = 0.0
    rule_version: str = "v1.2-context-aware"
    applied_thresholds: Dict[str, float] = {}

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
    risk_score: int = 0
    risk_range: Dict[str, float] = Field(..., description="Dictionary with 'best_case' and 'worst_case' keys")
    confidence: float = Field(..., ge=0.0, le=1.0)
    
    # State
    status: DecisionStatus = DecisionStatus.PENDING
    rejection_reason: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Audit Entension
    events: List[DecisionEvent] = []
    
    # AI Narrative
    ai_narrative: Optional[str] = None

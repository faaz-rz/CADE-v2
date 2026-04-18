import uuid

from fastapi import APIRouter, HTTPException, Path, Depends
from typing import List, Optional
from pydantic import BaseModel
from app.models.decision import (
    Decision, DecisionStatus, DecisionEvent, DecisionEventType,
    DecisionType, DecisionScope, DecisionContext, ImpactLabel, RiskLevel,
)
from app.services.decision_engine import DecisionEngine
from app.services.decision_store import DecisionStore
from app.core.auth import verify_token

router = APIRouter()


@router.post("/manual")
async def create_manual_decision(request: dict):
    """
    Create a decision from a manual action (e.g. price mismatch SWITCH).
    Uses UUID5 deterministic ID from (entity + recommended_supplier + product).
    """
    vendor_id = request.get("entity", "UNKNOWN")
    recommended = request.get("recommended_supplier", "")
    product = request.get("product", "")
    saving = float(request.get("estimated_saving", 0))
    current_price = float(request.get("current_price", 0))
    best_price = float(request.get("best_price", 0))
    price_diff_pct = float(request.get("price_diff_pct", 0))

    # Deterministic UUID5
    seed = f"{vendor_id}_{recommended}_{product}"
    decision_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, seed))

    # Determine impact and risk
    if saving > 500000:
        impact_label = ImpactLabel.HIGH
        risk_level = RiskLevel.HIGH
        risk_score = 8
    elif saving > 100000:
        impact_label = ImpactLabel.MEDIUM
        risk_level = RiskLevel.MEDIUM
        risk_score = 5
    else:
        impact_label = ImpactLabel.LOW
        risk_level = RiskLevel.MEDIUM
        risk_score = 5

    context = DecisionContext(
        analysis_period="Manual — Price Mismatch Detection",
        rule_id="PRICE_MISMATCH",
        thresholds={"price_diff_threshold": 0.15},
        metrics={
            "current_price": current_price,
            "best_price": best_price,
        },
        vendor_share_of_category=0,
        rule_version="1.0",
    )

    decision = Decision(
        id=decision_id,
        entity=vendor_id,
        recommended_action=f"Switch {product} procurement to {recommended}",
        explanation=(
            f"Price difference detected: {price_diff_pct:.0%}. "
            f"Current supplier charges ₹{current_price:,.0f} "
            f"vs ₹{best_price:,.0f} from {recommended}. "
            f"Estimated annual saving: ₹{saving:,.0f}."
        ),
        annual_impact=saving,
        expected_monthly_impact=saving / 12,
        cost_of_inaction=saving,
        impact_label=impact_label,
        risk_level=risk_level,
        risk_score=risk_score,
        risk_range={
            "best_case": saving * 0.7,
            "worst_case": saving * 1.3,
        },
        confidence=0.85,
        status=DecisionStatus.PENDING,
        decision_type=DecisionType.COST_REDUCE,
        scope=DecisionScope.VENDOR,
        context=context,
    )

    DecisionStore.save_decision(decision)
    return {"status": "created", "decision_id": str(decision.id)}


@router.get("", response_model=List[Decision])
async def get_decisions(payload: dict = Depends(verify_token)):
    """
    Returns the current list of decisions from the System of Record.
    """
    # In v1, we check if store is empty, if so, we might trigger analysis or just return empty.
    # For user ease, if empty, we trigger analysis (auto-load).
    decisions = DecisionStore.get_all_decisions()
    if not decisions:
        decisions = await DecisionEngine.analyze_uploaded_data()
        
    # Enrich with events
    for d in decisions:
        d.events = DecisionStore.get_events_for_decision(d.id)
        
    return decisions

@router.get("/savings")
def get_savings_summary(payload: dict = Depends(verify_token)):
    """
    Returns a savings breakdown across all decisions:
    approved, pending, and rejected/deferred.
    """
    decisions = DecisionStore.get_all_decisions()

    approved_savings = 0.0
    pending_savings = 0.0
    rejected_savings = 0.0
    approved_count = 0
    pending_count = 0
    rejected_count = 0

    for d in decisions:
        if d.status == DecisionStatus.APPROVED:
            approved_savings += d.annual_impact
            approved_count += 1
        elif d.status == DecisionStatus.PENDING:
            pending_savings += d.annual_impact
            pending_count += 1
        elif d.status in (DecisionStatus.REJECTED, DecisionStatus.DEFERRED):
            rejected_savings += d.annual_impact
            rejected_count += 1

    total_identified = approved_savings + pending_savings + rejected_savings
    # ROI assumes $1,500/month subscription cost ($18,000/year)
    roi_multiple = round(approved_savings / 1500, 1) if approved_savings > 0 else 0.0

    return {
        "approved_savings": approved_savings,
        "pending_savings": pending_savings,
        "rejected_savings": rejected_savings,
        "total_identified": total_identified,
        "decisions_approved_count": approved_count,
        "decisions_pending_count": pending_count,
        "decisions_rejected_count": rejected_count,
        "roi_multiple": roi_multiple,
        "currency": "INR",
    }

@router.get("/{decision_id}", response_model=Decision)
def get_decision(decision_id: str, payload: dict = Depends(verify_token)):
    decision = DecisionStore.get_decision(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    decision.events = DecisionStore.get_events_for_decision(decision_id)
    return decision

# --- Lifecycle Endpoints ---

class ReviewNote(BaseModel):
    note: Optional[str] = None

@router.post("/{decision_id}/approve", response_model=Decision)
def approve_decision(decision_id: str, review: ReviewNote, payload: dict = Depends(verify_token)):
    decision = DecisionStore.get_decision(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    if decision.status != DecisionStatus.PENDING and decision.status != DecisionStatus.DEFERRED:
        raise HTTPException(status_code=400, detail=f"Cannot approve a decision in {decision.status} state")

    old_status = decision.status
    decision.status = DecisionStatus.APPROVED
    
    # Log Event
    event = DecisionEvent(
        id=str(decision_id) + "_evt_" + str(len(DecisionStore.get_events_for_decision(decision_id))),
        decision_id=decision_id,
        event_type=DecisionEventType.APPROVED,
        previous_status=old_status,
        new_status=DecisionStatus.APPROVED,
        note=review.note
    )
    DecisionStore.log_event(event)
    DecisionStore.save_decision(decision) # Persist State
    
    decision.events = DecisionStore.get_events_for_decision(decision_id)
    return decision

@router.post("/{decision_id}/reject", response_model=Decision)
def reject_decision(decision_id: str, review: ReviewNote, payload: dict = Depends(verify_token)):
    decision = DecisionStore.get_decision(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    if decision.status != DecisionStatus.PENDING and decision.status != DecisionStatus.DEFERRED:
        raise HTTPException(status_code=400, detail=f"Cannot reject a decision in {decision.status} state")

    if not review.note or not review.note.strip():
        raise HTTPException(status_code=400, detail="Rejection requires a reason note")

    old_status = decision.status
    decision.status = DecisionStatus.REJECTED
    
    # Log Event
    event = DecisionEvent(
        id=str(decision_id) + "_evt_" + str(len(DecisionStore.get_events_for_decision(decision_id))),
        decision_id=decision_id,
        event_type=DecisionEventType.REJECTED,
        previous_status=old_status,
        new_status=DecisionStatus.REJECTED,
        note=review.note
    )
    DecisionStore.log_event(event)
    DecisionStore.save_decision(decision)
    return decision

@router.post("/{decision_id}/defer", response_model=Decision)
def defer_decision(decision_id: str, review: ReviewNote, payload: dict = Depends(verify_token)):
    decision = DecisionStore.get_decision(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
        
    if decision.status != DecisionStatus.PENDING:
         raise HTTPException(status_code=400, detail=f"Cannot defer a decision in {decision.status} state")

    old_status = decision.status
    decision.status = DecisionStatus.DEFERRED

    event = DecisionEvent(
        id=str(decision_id) + "_evt_" + str(len(DecisionStore.get_events_for_decision(decision_id))),
        decision_id=decision_id,
        event_type=DecisionEventType.DEFERRED,
        previous_status=old_status,
        new_status=DecisionStatus.DEFERRED,
        note=review.note
    )
    DecisionStore.log_event(event)
    DecisionStore.save_decision(decision)
    return decision

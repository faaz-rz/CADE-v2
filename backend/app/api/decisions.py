from fastapi import APIRouter, HTTPException, Path, Depends
from typing import List, Optional
from pydantic import BaseModel
from app.models.decision import Decision, DecisionStatus, DecisionEvent, DecisionEventType
from app.services.decision_engine import DecisionEngine
from app.services.decision_store import DecisionStore
from app.core.auth import verify_token

router = APIRouter()

@router.get("", response_model=List[Decision])
def get_decisions(payload: dict = Depends(verify_token)):
    """
    Returns the current list of decisions from the System of Record.
    """
    # In v1, we check if store is empty, if so, we might trigger analysis or just return empty.
    # For user ease, if empty, we trigger analysis (auto-load).
    decisions = DecisionStore.get_all_decisions()
    if not decisions:
        decisions = DecisionEngine.analyze_uploaded_data()
        
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
        "currency": "USD",
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

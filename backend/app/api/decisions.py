from fastapi import APIRouter, HTTPException, Path
from typing import List, Optional
from pydantic import BaseModel
from app.models.decision import Decision, DecisionStatus, DecisionEvent, DecisionEventType
from app.services.decision_engine import DecisionEngine
from app.services.decision_store import DecisionStore

router = APIRouter()

@router.get("/", response_model=List[Decision])
def get_decisions():
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

@router.get("/{decision_id}", response_model=Decision)
def get_decision(decision_id: str):
    decision = DecisionStore.get_decision(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    decision.events = DecisionStore.get_events_for_decision(decision_id)
    return decision

# --- Lifecycle Endpoints ---

class ReviewNote(BaseModel):
    note: Optional[str] = None

@router.post("/{decision_id}/approve", response_model=Decision)
def approve_decision(decision_id: str, review: ReviewNote):
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
def reject_decision(decision_id: str, review: ReviewNote):
    decision = DecisionStore.get_decision(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    if decision.status != DecisionStatus.PENDING and decision.status != DecisionStatus.DEFERRED:
        raise HTTPException(status_code=400, detail=f"Cannot reject a decision in {decision.status} state")

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
def defer_decision(decision_id: str, review: ReviewNote):
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

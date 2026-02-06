from fastapi import APIRouter, HTTPException, Path, Body
from app.services.audit import AuditService
from app.services.decision_engine import DecisionEngine
from app.models.decision import Decision, DecisionStatus

router = APIRouter()

# In-memory store helper to find the dummy decision for the demo
def find_decision(id: str) -> Decision:
    all_decisions = DecisionEngine.generate_dummy_decisions()
    # In a real app, query DB. Here, we just fake it by finding it in the generated list if possible,
    # OR we just re-instantiate it since IDs are random in our dummy generator. 
    # To make the demo work with the specific ID sent from frontend, we might need a persistent store.
    # For now, let's just mocked "success" if the ID format is valid.
    
    # Mock retrieval
    return all_decisions[0] # Just return *a* decision for typing purposes in this mockup

@router.post("/{decision_id}/approve")
async def approve_decision(decision_id: str = Path(..., title="The ID of the decision to approve")):
    # 1. Fetch Decision (Mock)
    # decision = get_decision_by_id(decision_id)
    
    # 2. Log Audit
    AuditService.log_action(decision_id, "APPROVED", "User approved via API")
    
    return {"status": "success", "id": decision_id, "new_state": DecisionStatus.APPROVED}

@router.post("/{decision_id}/reject")
async def reject_decision(
    decision_id: str = Path(...), 
    reason: str = Body(..., embed=True)
):
    if not reason:
        raise HTTPException(status_code=400, detail="Rejection reason is mandatory")
        
    # 1. Fetch Decision (Mock)
    
    # 2. Log Audit
    AuditService.log_action(decision_id, "REJECTED", f"Reason: {reason}")
    
    return {"status": "success", "id": decision_id, "new_state": DecisionStatus.REJECTED}

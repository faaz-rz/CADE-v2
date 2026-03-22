from fastapi import APIRouter
from app.models.summary import DecisionSummary
from app.services.decision_engine import DecisionEngine

router = APIRouter()

@router.get("", response_model=DecisionSummary)
async def get_decision_summary():
    """
    Returns the Executive Dashboard Summary.
    Calculates real-time stats from the current decision set.
    """
    # v2 FIX: Get current state from store, DO NOT re-analyze (resets state)
    from app.services.decision_store import DecisionStore
    decisions = DecisionStore.get_all_decisions()
    
    if not decisions:
         # Only analyze if store is truly empty (first load after restart)
         decisions = await DecisionEngine.analyze_uploaded_data()
         
    summary = DecisionEngine.get_summary_stats(decisions)
    return summary

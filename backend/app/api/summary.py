from fastapi import APIRouter
from app.models.summary import DecisionSummary
from app.services.decision_engine import DecisionEngine

router = APIRouter()


def _detect_vertical() -> str:
    """Detect vertical from current transaction data categories."""
    import os
    import json

    HOSPITAL_CATEGORIES = {
        "medical equipment", "pharma and consumables",
        "medical consumables", "hospital it systems",
        "facility management", "insurance tpa",
        "lab reagents"
    }

    tx_file = os.path.join("data", "transactions.json")
    if not os.path.exists(tx_file):
        return "general"

    try:
        with open(tx_file, "r") as f:
            data = json.load(f)

        if not data:
            return "general"

        categories = {
            r.get("category", "").lower() for r in data
            if r.get("category")
        }
        overlap = categories & HOSPITAL_CATEGORIES
        if len(overlap) >= 2:
            return "hospital"
    except Exception:
        pass

    return "general"


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
         
    is_demo = DecisionStore.is_demo_mode()
    summary = DecisionEngine.get_summary_stats(decisions, is_demo=is_demo)
    summary.vertical = _detect_vertical()
    return summary

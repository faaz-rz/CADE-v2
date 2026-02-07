from fastapi import APIRouter
from app.models.summary import DecisionSummary
from app.services.decision_engine import DecisionEngine

router = APIRouter()

@router.get("/", response_model=DecisionSummary)
def get_decision_summary():
    """
    Returns the Executive Dashboard Summary.
    Calculates real-time stats from the current decision set.
    """
    # For v1, we re-analyze the uploaded data.
    # In v2, this would fetch from a database.
    decisions = DecisionEngine.analyze_uploaded_data()
    summary = DecisionEngine.get_summary_stats(decisions)
    return summary

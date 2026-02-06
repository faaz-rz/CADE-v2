from fastapi import APIRouter
from typing import List
from app.models.decision import Decision
from app.services.decision_engine import DecisionEngine

router = APIRouter()

@router.get("/", response_model=List[Decision])
async def get_decisions():
    """
    Get all pending decisions.
    For v1, this triggers the specific logic rules on dummy/loaded data.
    """
    # In a real app, this would query the DB. 
    # Here we generate fresh ones for the demo.
    return DecisionEngine.generate_dummy_decisions()

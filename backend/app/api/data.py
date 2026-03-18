from fastapi import APIRouter, Depends
from app.services.decision_store import DecisionStore
from app.core.auth import verify_token, require_role
from pathlib import Path

router = APIRouter()

@router.delete("/api/data/clear")
async def clear_all_data(payload: dict = Depends(require_role("ADMIN"))):
    DecisionStore.clear()
    transactions = Path("data/transactions.json")
    if transactions.exists():
        transactions.write_text("[]")
    else:
        # Create it if it doesn't exist
        transactions.parent.mkdir(parents=True, exist_ok=True)
        transactions.write_text("[]")
        
    return {
        "status": "cleared",
        "message": "All vendor data and decisions removed"
    }

@router.get("/api/data/status")
async def data_status(payload: dict = Depends(verify_token)):
    decisions = DecisionStore.get_all_decisions()
    transactions = Path("data/transactions.json")
    count = 0
    if transactions.exists():
        import json
        try:
            count = len(json.loads(transactions.read_text()))
        except:
            pass
    return {
        "decisions_count": len(decisions),
        "transactions_count": count,
        "has_data": len(decisions) > 0
    }

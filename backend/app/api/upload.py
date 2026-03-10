import traceback
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services.ingestion import IngestionService

router = APIRouter()

@router.post("")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
        
    content = await file.read()
    
    # Step 1: Clear in-memory cache and SQLite decisions
    from app.services.decision_store import DecisionStore
    DecisionStore.clear()
    
    # Step 2: Reset transactions.json
    from pathlib import Path
    transactions_path = Path("data/transactions.json")
    if not transactions_path.exists():
        transactions_path.parent.mkdir(parents=True, exist_ok=True)
    transactions_path.write_text("[]")
    
    try:
        result = IngestionService.ingest_file(content, file.filename)
        
        from app.services.decision_engine import DecisionEngine
        decisions = DecisionEngine.analyze_uploaded_data()
        result.decisions_generated = len(decisions)
        
        out = result.model_dump(exclude={"records"})
        out["filename"] = file.filename
        return out
    except Exception as e:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": str(e),
            "detail": traceback.format_exc()
        })

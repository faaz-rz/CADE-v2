from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ingestion import IngestionService

router = APIRouter()

@router.post("")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
        
    content = await file.read()
    
    try:
        result = IngestionService.process_file(content, file.filename)
        return {"status": "success", "filename": file.filename, "stats": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

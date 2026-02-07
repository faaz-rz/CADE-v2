from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import decisions, approvals, upload, summary

app = FastAPI(
    title="Capital Allocation Decision Engine",
    description="Overlay-first decision infrastructure for EBITDA optimization.",
    version="1.0.0"
)

# CORS Configuration (Allow Frontend)
origins = [
    "http://localhost:3000",
    "http://localhost:5173", # Vite default
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(decisions.router, prefix="/api/decisions", tags=["Decisions"])
app.include_router(approvals.router, prefix="/api/decisions", tags=["Approvals"]) # Nested under decisions for RESTful feel
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(summary.router, prefix="/api/summary", tags=["Summary"])

@app.get("/")
def health_check():
    return {"status": "running", "system": "Decision Engine v1"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import decisions, approvals, upload, summary, exposure, simulation, export
from app.db.database import init_db
from app.services.decision_store import DecisionStore

app = FastAPI(
    title="Capital Risk & Exposure Platform",
    description="Capital allocation decision engine with financial exposure analysis, price shock simulation, and executive reporting.",
    version="2.0.0",
    redirect_slashes=False
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
from app.api.data import router as data_router

app.include_router(decisions.router, prefix="/api/decisions", tags=["Decisions"])
app.include_router(approvals.router, prefix="/api/decisions", tags=["Approvals"]) # Nested under decisions for RESTful feel
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(summary.router, prefix="/api/summary", tags=["Summary"])
app.include_router(exposure.router, prefix="/api/exposure", tags=["Exposure"])
app.include_router(simulation.router, prefix="/simulate", tags=["Simulation"])
app.include_router(export.router, prefix="/export", tags=["Export"])
app.include_router(data_router, tags=["Data"])

@app.get("/")
def health_check():
    return {"status": "running", "system": "Capital Risk & Exposure Platform v2"}


@app.on_event("startup")
def on_startup():
    """Initialize database tables and load persisted state."""
    init_db()
    DecisionStore.enable_db()
    DecisionStore.load_from_db()
    
    import re
    decisions = DecisionStore.get_all_decisions()
    count_filtered = 0
    for d in decisions:
        if re.match(r"^Vendor_\d+$", d.entity):
            DecisionStore._decisions.pop(d.id, None)
            count_filtered += 1
            
    print(f"[STARTUP] Database initialized. Decisions loaded from SQLite. Filtered {count_filtered} stale test decisions on startup.")

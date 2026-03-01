from fastapi import APIRouter, HTTPException
from app.simulation.price_shock import (
    PriceShockRequest,
    PriceShockResponse,
    simulate_price_shock,
)

router = APIRouter()


@router.post("/price_shock", response_model=PriceShockResponse)
def run_price_shock_simulation(request: PriceShockRequest):
    """
    Simulate a price shock for a vendor.
    Returns: impact on spend, EBITDA delta, and risk classification shift.
    """
    try:
        return simulate_price_shock(request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

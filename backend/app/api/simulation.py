from fastapi import APIRouter, HTTPException
from app.simulation.price_shock import (
    PriceShockRequest,
    PriceShockResponse,
    simulate_price_shock,
)
from app.simulation.portfolio_shock import (
    PortfolioShockRequest,
    PortfolioShockResponse,
    ScenarioDefinition,
    simulate_portfolio_shock,
    get_predefined_scenarios,
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

@router.post("/portfolio_shock", response_model=PortfolioShockResponse)
def run_portfolio_shock_simulation(request: PortfolioShockRequest):
    """
    Simulate a price shock holistically across the entire portfolio matrix based on specific sector filters constraints.
    """
    try:
        return simulate_portfolio_shock(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/scenarios", response_model=list[ScenarioDefinition])
def get_scenarios():
    """
    List static macro-economic simulation test strategies.
    """
    return get_predefined_scenarios()

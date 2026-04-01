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
from app.simulation.monte_carlo import (
    run_single_vendor_simulation,
    run_portfolio_simulation,
)
from app.services.exposure_engine import calculate_all_exposures

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


@router.post("/monte_carlo/vendor")
async def simulate_vendor_monte_carlo(request: dict):
    """
    Run Monte Carlo simulation for a single vendor.
    Returns probabilistic impact distribution (percentiles, probability thresholds).
    """
    vendor_id = request.get("vendor_id")
    ebitda_margin = request.get("ebitda_margin", 0.25)
    simulations = request.get("simulations", 50000)
    distribution = request.get("distribution", "student_t")
    seed = request.get("seed", None)

    exposures = calculate_all_exposures()
    vendor = next(
        (v for v in exposures if v.vendor_id == vendor_id),
        None
    )
    if not vendor:
        raise HTTPException(status_code=404, detail=f"Vendor '{vendor_id}' not found")

    result = run_single_vendor_simulation(
        vendor_id=vendor_id,
        annual_spend=vendor.annual_spend,
        ebitda_margin=ebitda_margin,
        simulations=simulations,
        distribution=distribution,
        seed=seed,
    )
    return result.__dict__


@router.post("/monte_carlo/portfolio")
async def simulate_portfolio_monte_carlo(request: dict):
    """
    Run Monte Carlo simulation across the entire vendor portfolio.
    Supports correlated shocks for realistic portfolio risk modeling.
    """
    ebitda_margin = request.get("ebitda_margin", 0.25)
    simulations = request.get("simulations", 50000)
    correlated = request.get("correlated", True)
    vendor_ids = request.get("vendor_ids", None)
    distribution = request.get("distribution", "student_t")
    seed = request.get("seed", None)

    exposures = calculate_all_exposures()

    if vendor_ids:
        exposures = [v for v in exposures if v.vendor_id in vendor_ids]

    vendor_list = [
        {
            "vendor_id": v.vendor_id,
            "annual_spend": v.annual_spend,
            "category": v.category,
        }
        for v in exposures
    ]

    if not vendor_list:
        raise HTTPException(status_code=404, detail="No vendors found")

    result = run_portfolio_simulation(
        vendors=vendor_list,
        ebitda_margin=ebitda_margin,
        simulations=simulations,
        correlated=correlated,
        distribution=distribution,
        seed=seed,
    )

    # Serialize dataclass results
    response = result.__dict__.copy()
    response["vendor_results"] = [vr.__dict__ for vr in result.vendor_results]
    return response

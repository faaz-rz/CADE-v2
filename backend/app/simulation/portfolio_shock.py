from typing import List, Optional
from pydantic import BaseModel
from app.services.analytics import SpendingAnalyzer
from app.simulation.price_shock import simulate_price_shock, PriceShockRequest

class PortfolioShockRequest(BaseModel):
    category: Optional[str] = None
    vendor_ids: Optional[List[str]] = None
    shock_percentage: float
    ebitda_margin: float = 0.25

class PortfolioShockResponse(BaseModel):
    total_base_spend: float
    total_new_spend: float
    total_delta_spend: float
    total_ebitda_delta: float
    affected_vendors: int

class ScenarioDefinition(BaseModel):
    id: str
    name: str
    description: str
    shock_percentage: float
    ebitda_margin: float
    category_focus: str

def get_predefined_scenarios() -> List[ScenarioDefinition]:
    return [
        ScenarioDefinition(
            id="hyp_inf",
            name="Hyperinflation Spike",
            description="Broad 25% cost increase across all vendor contracts due to macro wage/CPI pressures.",
            shock_percentage=25.0,
            ebitda_margin=0.25,
            category_focus="All"
        ),
        ScenarioDefinition(
            id="cloud_monopoly",
            name="Cloud Monopoly Pricing",
            description="Leading SaaS and IaaS providers raise list prices by 15% unconditionally.",
            shock_percentage=15.0,
            ebitda_margin=0.25,
            category_focus="Cloud Infrastructure"
        ),
        ScenarioDefinition(
            id="saas_recession",
            name="Software Vendor Distress",
            description="Vendors attempt to extract 20% more value to survive funding droughts.",
            shock_percentage=20.0,
            ebitda_margin=0.25,
            category_focus="SaaS"
        ),
        ScenarioDefinition(
            id="baseline_stress",
            name="Baseline Erosion",
            description="A steady 5% across-the-board inflation stress test.",
            shock_percentage=5.0,
            ebitda_margin=0.25,
            category_focus="All"
        )
    ]

def simulate_portfolio_shock(request: PortfolioShockRequest) -> PortfolioShockResponse:
    vendor_stats = SpendingAnalyzer.get_vendor_stats()
    
    total_base = 0.0
    total_new = 0.0
    total_delta = 0.0
    total_ebitda = 0.0
    count = 0
    
    for v_id, stats in vendor_stats.items():
        # Apply filters
        if request.category and stats.category != request.category and request.category.lower() not in ["all", "all vendors"]:
            continue
        if request.vendor_ids and v_id not in request.vendor_ids:
            continue
            
        # Run shock mathematically just using standard single shock block to guarantee deduplication
        req = PriceShockRequest(vendor_id=v_id, shock_percentage=request.shock_percentage)
        res = simulate_price_shock(req)
        
        total_base += res.base_spend
        total_new += res.new_spend
        total_delta += res.delta_spend
        # Overwrite standard engine EBITDA margin using the custom Portfolio constraint if needed
        # Or standard single shock uses 0.25 natively inside calculate_shock_impact
        ebitda_delta = res.delta_spend * request.ebitda_margin
        total_ebitda += ebitda_delta
        count += 1
        
    return PortfolioShockResponse(
        total_base_spend=total_base,
        total_new_spend=total_new,
        total_delta_spend=total_delta,
        total_ebitda_delta=total_ebitda,
        affected_vendors=count
    )

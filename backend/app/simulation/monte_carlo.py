"""
Monte Carlo Simulation Engine — Probabilistic risk analysis.

Runs N simulations (default 10,000) with triangular shock distributions
to produce percentile-based impact ranges and probability thresholds.
"""

from dataclasses import dataclass, field
import random
import math
from typing import List


@dataclass
class MonteCarloResult:
    vendor_id: str
    simulations: int
    mean_impact: float
    std_deviation: float
    percentile_10: float  # best case (10th percentile)
    percentile_50: float  # median
    percentile_90: float  # worst case (90th percentile)
    probability_exceeds_50k: float
    probability_exceeds_100k: float
    probability_exceeds_500k: float
    risk_rating: str  # LOW / MEDIUM / HIGH / CRITICAL


@dataclass
class PortfolioMonteCarloResult:
    simulations: int
    vendors_analyzed: int
    mean_portfolio_impact: float
    std_deviation: float
    percentile_10: float
    percentile_50: float
    percentile_90: float
    probability_exceeds_100k: float
    probability_exceeds_500k: float
    probability_exceeds_1m: float
    worst_case_vendor: str
    worst_case_amount: float
    risk_rating: str
    vendor_results: List[MonteCarloResult] = field(default_factory=list)


def run_single_vendor_simulation(
    vendor_id: str,
    annual_spend: float,
    ebitda_margin: float = 0.25,
    simulations: int = 10000,
    min_shock: float = 0.0,
    max_shock: float = 0.30,
) -> MonteCarloResult:
    """
    Run Monte Carlo simulation for a single vendor.
    Uses triangular distribution (mode=8%) for realistic shock modeling.
    """
    impacts = []
    for _ in range(simulations):
        # Random shock between min and max
        # Using triangular distribution — more realistic than uniform
        # Most likely shock is around 8%
        shock = random.triangular(min_shock, max_shock, 0.08)
        impact = annual_spend * shock * ebitda_margin
        impacts.append(impact)

    impacts.sort()
    n = len(impacts)

    mean = sum(impacts) / n
    variance = sum((x - mean) ** 2 for x in impacts) / n
    std_dev = math.sqrt(variance)

    p10 = impacts[int(n * 0.10)]
    p50 = impacts[int(n * 0.50)]
    p90 = impacts[int(n * 0.90)]

    prob_50k = len([x for x in impacts if x > 50000]) / n
    prob_100k = len([x for x in impacts if x > 100000]) / n
    prob_500k = len([x for x in impacts if x > 500000]) / n

    if p90 > 500000:
        rating = "CRITICAL"
    elif p90 > 100000:
        rating = "HIGH"
    elif p90 > 50000:
        rating = "MEDIUM"
    else:
        rating = "LOW"

    return MonteCarloResult(
        vendor_id=vendor_id,
        simulations=simulations,
        mean_impact=round(mean, 2),
        std_deviation=round(std_dev, 2),
        percentile_10=round(p10, 2),
        percentile_50=round(p50, 2),
        percentile_90=round(p90, 2),
        probability_exceeds_50k=round(prob_50k, 4),
        probability_exceeds_100k=round(prob_100k, 4),
        probability_exceeds_500k=round(prob_500k, 4),
        risk_rating=rating,
    )


def run_portfolio_simulation(
    vendors: List[dict],
    ebitda_margin: float = 0.25,
    simulations: int = 10000,
    correlated: bool = True,
) -> PortfolioMonteCarloResult:
    """
    Run Monte Carlo simulation across a portfolio of vendors.
    correlated=True means vendors experience correlated market shocks.
    """
    portfolio_impacts = []
    vendor_results = []

    # Run individual simulations first
    for vendor in vendors:
        result = run_single_vendor_simulation(
            vendor_id=vendor["vendor_id"],
            annual_spend=vendor["annual_spend"],
            ebitda_margin=ebitda_margin,
            simulations=simulations,
        )
        vendor_results.append(result)

    # Portfolio simulation with correlation
    for i in range(simulations):
        total_impact = 0.0

        if correlated:
            # Market shock affects all vendors
            market_shock = random.gauss(0.05, 0.03)
            market_shock = max(0, min(0.30, market_shock))

        for vendor in vendors:
            if correlated:
                # Individual vendor shock + market component
                idio_shock = random.triangular(0, 0.15, 0.05)
                shock = (market_shock * 0.6) + (idio_shock * 0.4)
            else:
                shock = random.triangular(0, 0.30, 0.08)

            impact = vendor["annual_spend"] * shock * ebitda_margin
            total_impact += impact

        portfolio_impacts.append(total_impact)

    portfolio_impacts.sort()
    n = len(portfolio_impacts)

    mean = sum(portfolio_impacts) / n
    variance = sum((x - mean) ** 2 for x in portfolio_impacts) / n
    std_dev = math.sqrt(variance)

    p10 = portfolio_impacts[int(n * 0.10)]
    p50 = portfolio_impacts[int(n * 0.50)]
    p90 = portfolio_impacts[int(n * 0.90)]

    prob_100k = len([x for x in portfolio_impacts if x > 100000]) / n
    prob_500k = len([x for x in portfolio_impacts if x > 500000]) / n
    prob_1m = len([x for x in portfolio_impacts if x > 1000000]) / n

    worst_vendor = max(vendor_results, key=lambda x: x.percentile_90)

    if p90 > 1000000:
        rating = "CRITICAL"
    elif p90 > 500000:
        rating = "HIGH"
    elif p90 > 100000:
        rating = "MEDIUM"
    else:
        rating = "LOW"

    return PortfolioMonteCarloResult(
        simulations=simulations,
        vendors_analyzed=len(vendors),
        mean_portfolio_impact=round(mean, 2),
        std_deviation=round(std_dev, 2),
        percentile_10=round(p10, 2),
        percentile_50=round(p50, 2),
        percentile_90=round(p90, 2),
        probability_exceeds_100k=round(prob_100k, 4),
        probability_exceeds_500k=round(prob_500k, 4),
        probability_exceeds_1m=round(prob_1m, 4),
        worst_case_vendor=worst_vendor.vendor_id,
        worst_case_amount=worst_vendor.percentile_90,
        risk_rating=rating,
        vendor_results=vendor_results,
    )

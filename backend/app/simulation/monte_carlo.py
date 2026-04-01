"""
Monte Carlo Simulation Engine — Production-grade probabilistic risk analysis.

Features:
  - Vectorized NumPy operations (~100x faster than Python loops)
  - Student-t distribution for fat-tail modeling (default df=4)
  - Cholesky-decomposed correlation for portfolio simulation
  - Seed management for full reproducibility
  - Convergence diagnostics (standard error, confidence intervals)

All simulations use np.random.default_rng (PCG64 generator).
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import numpy as np

from app.simulation.distributions import (
    generate_shocks,
    build_correlation_matrix,
    apply_cholesky_correlation,
)


@dataclass
class MonteCarloResult:
    vendor_id: str
    simulations: int
    mean_impact: float
    std_deviation: float
    percentile_05: float   # extreme best case
    percentile_10: float   # best case (10th percentile)
    percentile_50: float   # median
    percentile_90: float   # worst case (90th percentile)
    percentile_95: float   # extreme worst case
    probability_exceeds_50k: float
    probability_exceeds_100k: float
    probability_exceeds_500k: float
    risk_rating: str       # LOW / MEDIUM / HIGH / CRITICAL
    seed: int
    distribution_type: str
    convergence_score: float
    confidence_interval_95: Tuple[float, float]


@dataclass
class PortfolioMonteCarloResult:
    simulations: int
    vendors_analyzed: int
    mean_portfolio_impact: float
    std_deviation: float
    percentile_05: float
    percentile_10: float
    percentile_50: float
    percentile_90: float
    percentile_95: float
    probability_exceeds_100k: float
    probability_exceeds_500k: float
    probability_exceeds_1m: float
    worst_case_vendor: str
    worst_case_amount: float
    risk_rating: str
    seed: int
    distribution_type: str
    convergence_score: float
    confidence_interval_95: Tuple[float, float]
    correlation_method: str
    vendor_results: List[MonteCarloResult] = field(default_factory=list)


def _compute_convergence(impacts: np.ndarray) -> Tuple[float, Tuple[float, float]]:
    """
    Compute convergence diagnostics.

    Returns
    -------
    (convergence_score, (ci_lower, ci_upper))
    """
    mean = float(np.mean(impacts))
    std = float(np.std(impacts, ddof=1))
    n = len(impacts)
    se = std / np.sqrt(n)

    # Convergence score: 1 - (SE / |mean|), clamped to [0, 1]
    if abs(mean) > 1e-9:
        score = max(0.0, min(1.0, 1.0 - (se / abs(mean))))
    else:
        score = 1.0 if std < 1e-9 else 0.0

    ci_lower = mean - 1.96 * se
    ci_upper = mean + 1.96 * se
    return round(score, 6), (round(ci_lower, 2), round(ci_upper, 2))


def _classify_risk(p90: float) -> str:
    """Risk rating from 90th percentile impact."""
    if p90 > 500_000:
        return "CRITICAL"
    elif p90 > 100_000:
        return "HIGH"
    elif p90 > 50_000:
        return "MEDIUM"
    return "LOW"


def _classify_portfolio_risk(p90: float) -> str:
    """Portfolio-level risk rating from 90th percentile."""
    if p90 > 1_000_000:
        return "CRITICAL"
    elif p90 > 500_000:
        return "HIGH"
    elif p90 > 100_000:
        return "MEDIUM"
    return "LOW"


def run_single_vendor_simulation(
    vendor_id: str,
    annual_spend: float,
    ebitda_margin: float = 0.25,
    simulations: int = 50000,
    min_shock: float = 0.0,
    max_shock: float = 0.30,
    distribution: str = "student_t",
    seed: Optional[int] = None,
) -> MonteCarloResult:
    """
    Run Monte Carlo simulation for a single vendor.

    Fully vectorized — generates all shocks in a single NumPy call.
    Uses PCG64 RNG with optional seed for reproducibility.
    """
    # Initialize RNG
    if seed is None:
        seed = int(np.random.SeedSequence().entropy % (2**31))
    rng = np.random.default_rng(seed)

    # Generate all shocks at once (vectorized)
    shocks = generate_shocks(
        rng=rng,
        n=simulations,
        method=distribution,
        location=0.08,
        scale=0.06,
        min_clamp=min_shock,
        max_clamp=max_shock,
    )

    # Vectorized impact calculation
    impacts = annual_spend * shocks * ebitda_margin

    # Percentiles (vectorized)
    p05, p10, p50, p90, p95 = np.percentile(impacts, [5, 10, 50, 90, 95])

    # Statistics
    mean = float(np.mean(impacts))
    std_dev = float(np.std(impacts, ddof=1))

    # Probability thresholds (vectorized boolean ops)
    n = simulations
    prob_50k = float(np.sum(impacts > 50_000) / n)
    prob_100k = float(np.sum(impacts > 100_000) / n)
    prob_500k = float(np.sum(impacts > 500_000) / n)

    # Convergence
    conv_score, ci_95 = _compute_convergence(impacts)

    return MonteCarloResult(
        vendor_id=vendor_id,
        simulations=simulations,
        mean_impact=round(mean, 2),
        std_deviation=round(std_dev, 2),
        percentile_05=round(float(p05), 2),
        percentile_10=round(float(p10), 2),
        percentile_50=round(float(p50), 2),
        percentile_90=round(float(p90), 2),
        percentile_95=round(float(p95), 2),
        probability_exceeds_50k=round(prob_50k, 4),
        probability_exceeds_100k=round(prob_100k, 4),
        probability_exceeds_500k=round(prob_500k, 4),
        risk_rating=_classify_risk(float(p90)),
        seed=seed,
        distribution_type=distribution,
        convergence_score=conv_score,
        confidence_interval_95=ci_95,
    )


def run_portfolio_simulation(
    vendors: List[dict],
    ebitda_margin: float = 0.25,
    simulations: int = 50000,
    correlated: bool = True,
    distribution: str = "student_t",
    seed: Optional[int] = None,
) -> PortfolioMonteCarloResult:
    """
    Run Monte Carlo simulation across a portfolio of vendors.

    When correlated=True, uses Cholesky decomposition on a category-based
    correlation matrix. Same-category vendors get ρ=0.7, cross-category ρ=0.2.

    All operations are fully vectorized over a (simulations × n_vendors) matrix.
    """
    n_vendors = len(vendors)

    # Initialize RNG
    if seed is None:
        seed = int(np.random.SeedSequence().entropy % (2**31))
    rng = np.random.default_rng(seed)

    # --- Individual vendor simulations (independent, for per-vendor stats) ---
    vendor_results = []
    for vendor in vendors:
        # Each vendor gets a deterministic child seed from the master
        child_seed = int(rng.integers(0, 2**31))
        result = run_single_vendor_simulation(
            vendor_id=vendor["vendor_id"],
            annual_spend=vendor["annual_spend"],
            ebitda_margin=ebitda_margin,
            simulations=simulations,
            distribution=distribution,
            seed=child_seed,
        )
        vendor_results.append(result)

    # --- Portfolio simulation (correlated or independent) ---
    # Re-seed for portfolio-level simulation so it's deterministic
    portfolio_rng = np.random.default_rng(seed + 1)

    # Generate raw shocks matrix: (simulations, n_vendors)
    raw_shocks = np.column_stack([
        generate_shocks(
            rng=portfolio_rng,
            n=simulations,
            method=distribution,
            location=0.08,
            scale=0.06,
            min_clamp=0.0,
            max_clamp=0.30,
        )
        for _ in range(n_vendors)
    ])

    if correlated and n_vendors > 1:
        # Build category-based correlation matrix
        categories = [v.get("category", "Unknown") for v in vendors]
        corr_matrix = build_correlation_matrix(categories)

        # Standardize to unit normal for Cholesky, then re-scale
        # We work with normalized shocks, apply correlation, then denormalize
        means = np.mean(raw_shocks, axis=0, keepdims=True)
        stds = np.std(raw_shocks, axis=0, keepdims=True)
        stds = np.where(stds < 1e-9, 1.0, stds)  # guard division by zero

        normalized = (raw_shocks - means) / stds
        correlated_normalized = apply_cholesky_correlation(
            portfolio_rng, normalized, corr_matrix
        )
        # Denormalize back
        correlated_shocks = correlated_normalized * stds + means
        # Re-clamp after correlation transform
        np.clip(correlated_shocks, 0.0, 0.30, out=correlated_shocks)
        shocks_matrix = correlated_shocks
        correlation_method = "cholesky"
    else:
        shocks_matrix = raw_shocks
        correlation_method = "independent"

    # Vectorized impact: (simulations, n_vendors)
    annual_spends = np.array([v["annual_spend"] for v in vendors])
    impacts_matrix = shocks_matrix * annual_spends[np.newaxis, :] * ebitda_margin

    # Portfolio total impact per simulation
    portfolio_impacts = np.sum(impacts_matrix, axis=1)

    # Statistics
    mean = float(np.mean(portfolio_impacts))
    std_dev = float(np.std(portfolio_impacts, ddof=1))
    p05, p10, p50, p90, p95 = np.percentile(portfolio_impacts, [5, 10, 50, 90, 95])

    n = simulations
    prob_100k = float(np.sum(portfolio_impacts > 100_000) / n)
    prob_500k = float(np.sum(portfolio_impacts > 500_000) / n)
    prob_1m = float(np.sum(portfolio_impacts > 1_000_000) / n)

    # Convergence
    conv_score, ci_95 = _compute_convergence(portfolio_impacts)

    # Worst vendor by 90th percentile
    worst_vendor = max(vendor_results, key=lambda x: x.percentile_90)

    return PortfolioMonteCarloResult(
        simulations=simulations,
        vendors_analyzed=n_vendors,
        mean_portfolio_impact=round(mean, 2),
        std_deviation=round(std_dev, 2),
        percentile_05=round(float(p05), 2),
        percentile_10=round(float(p10), 2),
        percentile_50=round(float(p50), 2),
        percentile_90=round(float(p90), 2),
        percentile_95=round(float(p95), 2),
        probability_exceeds_100k=round(prob_100k, 4),
        probability_exceeds_500k=round(prob_500k, 4),
        probability_exceeds_1m=round(prob_1m, 4),
        worst_case_vendor=worst_vendor.vendor_id,
        worst_case_amount=worst_vendor.percentile_90,
        risk_rating=_classify_portfolio_risk(float(p90)),
        seed=seed,
        distribution_type=distribution,
        convergence_score=conv_score,
        confidence_interval_95=ci_95,
        correlation_method=correlation_method,
        vendor_results=vendor_results,
    )

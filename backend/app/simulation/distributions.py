"""
Distribution utilities for Monte Carlo simulation.

Encapsulates shock-generation logic so the main engine stays clean.
All functions return NumPy arrays of shape (n,) representing random shocks.
"""

import numpy as np
from numpy.random import Generator


def generate_shocks(
    rng: Generator,
    n: int,
    method: str = "student_t",
    location: float = 0.08,
    scale: float = 0.06,
    min_clamp: float = 0.0,
    max_clamp: float = 0.30,
    df: int = 4,
) -> np.ndarray:
    """
    Generate an array of random shocks.

    Parameters
    ----------
    rng : numpy Generator instance (for reproducibility)
    n : number of samples
    method : "student_t" | "normal" | "triangular"
    location : center/mode of the distribution
    scale : spread parameter (std-like)
    min_clamp : floor clamp (no shock below this)
    max_clamp : ceiling clamp (no shock above this)
    df : degrees of freedom for Student-t (lower = fatter tails)

    Returns
    -------
    np.ndarray of shape (n,) with shock values in [min_clamp, max_clamp]
    """
    # Degenerate case: zero-width range → constant shock
    if max_clamp <= min_clamp:
        return np.full(n, min_clamp)

    if method == "student_t":
        # Student-t with `df` degrees of freedom, scaled and shifted
        raw = rng.standard_t(df=df, size=n)
        shocks = location + scale * raw
    elif method == "normal":
        shocks = rng.normal(loc=location, scale=scale, size=n)
    elif method == "triangular":
        # Triangular with mode at `location`
        left = min_clamp
        right = max_clamp
        mode = np.clip(location, left + 1e-9, right - 1e-9)
        shocks = rng.triangular(left=left, mode=mode, right=right, size=n)
    else:
        raise ValueError(f"Unknown distribution method: {method}")

    # Clamp to valid range
    np.clip(shocks, min_clamp, max_clamp, out=shocks)
    return shocks


def build_correlation_matrix(categories: list[str]) -> np.ndarray:
    """
    Build a correlation matrix from vendor categories.

    Same category → ρ = 0.7 (co-move in sector stress)
    Different category → ρ = 0.2 (mild market-wide correlation)
    Diagonal → 1.0

    Returns a positive-definite correlation matrix suitable for Cholesky.
    """
    n = len(categories)
    corr = np.full((n, n), 0.2)  # baseline cross-sector correlation
    for i in range(n):
        for j in range(n):
            if i == j:
                corr[i, j] = 1.0
            elif categories[i] == categories[j]:
                corr[i, j] = 0.7
    return corr


def apply_cholesky_correlation(
    rng: Generator,
    uncorrelated: np.ndarray,
    corr_matrix: np.ndarray,
) -> np.ndarray:
    """
    Apply Cholesky decomposition to introduce correlation.

    Parameters
    ----------
    rng : Generator (unused but kept for API symmetry)
    uncorrelated : shape (simulations, n_vendors) of independent draws
    corr_matrix : shape (n_vendors, n_vendors) correlation matrix

    Returns
    -------
    np.ndarray of shape (simulations, n_vendors) with correlated draws
    """
    L = np.linalg.cholesky(corr_matrix)
    # Each row of uncorrelated is multiplied by L^T to introduce correlation
    correlated = uncorrelated @ L.T
    return correlated

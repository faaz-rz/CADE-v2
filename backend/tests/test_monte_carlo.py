"""
Tests for Production-Grade Monte Carlo Simulation Engine.

Independent test file — does NOT modify any existing test files.
Tests are self-contained using direct function calls (no mock dependencies on DB/analytics).
"""

import unittest
import numpy as np
from app.simulation.monte_carlo import (
    run_single_vendor_simulation,
    run_portfolio_simulation,
    MonteCarloResult,
    PortfolioMonteCarloResult,
)
from app.simulation.distributions import (
    generate_shocks,
    build_correlation_matrix,
    apply_cholesky_correlation,
)


class TestZeroVolatility(unittest.TestCase):
    """If volatility (max_shock) is 0, all impacts must be exactly 0."""

    def test_zero_shock_range_produces_zero_impact(self):
        result = run_single_vendor_simulation(
            vendor_id="ZERO_TEST",
            annual_spend=1_000_000,
            ebitda_margin=0.25,
            simulations=1000,
            min_shock=0.0,
            max_shock=0.0,
            distribution="triangular",
            seed=42,
        )
        self.assertEqual(result.mean_impact, 0.0)
        self.assertEqual(result.std_deviation, 0.0)
        self.assertEqual(result.percentile_90, 0.0)
        self.assertEqual(result.percentile_10, 0.0)

    def test_zero_spend_produces_zero_impact(self):
        result = run_single_vendor_simulation(
            vendor_id="ZERO_SPEND",
            annual_spend=0.0,
            ebitda_margin=0.25,
            simulations=1000,
            seed=42,
        )
        self.assertEqual(result.mean_impact, 0.0)


class TestNoNegativeImpacts(unittest.TestCase):
    """No simulation path should produce negative impact values."""

    def test_single_vendor_no_negatives(self):
        result = run_single_vendor_simulation(
            vendor_id="POS_TEST",
            annual_spend=500_000,
            simulations=10000,
            min_shock=0.0,
            max_shock=0.30,
            seed=123,
        )
        # All percentiles must be >= 0
        self.assertGreaterEqual(result.percentile_05, 0.0)
        self.assertGreaterEqual(result.percentile_10, 0.0)
        self.assertGreaterEqual(result.percentile_50, 0.0)
        self.assertGreaterEqual(result.percentile_90, 0.0)
        self.assertGreaterEqual(result.percentile_95, 0.0)
        self.assertGreaterEqual(result.mean_impact, 0.0)

    def test_student_t_no_negatives(self):
        """Student-t can generate extreme values, but clamping prevents negatives."""
        result = run_single_vendor_simulation(
            vendor_id="TAIL_POS",
            annual_spend=1_000_000,
            simulations=50000,
            distribution="student_t",
            seed=999,
        )
        self.assertGreaterEqual(result.percentile_05, 0.0)


class TestSeedReproducibility(unittest.TestCase):
    """Same seed must produce bitwise identical results."""

    def test_same_seed_same_result(self):
        r1 = run_single_vendor_simulation(
            vendor_id="SEED_TEST", annual_spend=100_000, seed=42, simulations=5000,
        )
        r2 = run_single_vendor_simulation(
            vendor_id="SEED_TEST", annual_spend=100_000, seed=42, simulations=5000,
        )
        self.assertEqual(r1.mean_impact, r2.mean_impact)
        self.assertEqual(r1.std_deviation, r2.std_deviation)
        self.assertEqual(r1.percentile_90, r2.percentile_90)
        self.assertEqual(r1.percentile_10, r2.percentile_10)
        self.assertEqual(r1.seed, r2.seed)

    def test_different_seeds_differ(self):
        r1 = run_single_vendor_simulation(
            vendor_id="DIFF_SEED", annual_spend=100_000, seed=42, simulations=5000,
        )
        r2 = run_single_vendor_simulation(
            vendor_id="DIFF_SEED", annual_spend=100_000, seed=999, simulations=5000,
        )
        # Extremely unlikely to be identical with different seeds
        self.assertNotEqual(r1.mean_impact, r2.mean_impact)

    def test_portfolio_seed_reproducibility(self):
        vendors = [
            {"vendor_id": "V1", "annual_spend": 200000, "category": "SaaS"},
            {"vendor_id": "V2", "annual_spend": 300000, "category": "Cloud"},
        ]
        r1 = run_portfolio_simulation(vendors, seed=42, simulations=5000)
        r2 = run_portfolio_simulation(vendors, seed=42, simulations=5000)
        self.assertEqual(r1.mean_portfolio_impact, r2.mean_portfolio_impact)
        self.assertEqual(r1.std_deviation, r2.std_deviation)
        self.assertEqual(r1.seed, r2.seed)


class TestConvergence(unittest.TestCase):
    """Standard error should decrease as simulation count increases."""

    def test_convergence_improves_with_more_simulations(self):
        results = {}
        for n in [1000, 10000, 50000]:
            r = run_single_vendor_simulation(
                vendor_id="CONV_TEST",
                annual_spend=500_000,
                simulations=n,
                seed=42,
            )
            results[n] = r

        # Convergence score should increase with more simulations
        self.assertGreater(
            results[50000].convergence_score,
            results[1000].convergence_score,
        )
        # CI width should shrink
        ci_1k = results[1000].confidence_interval_95
        ci_50k = results[50000].confidence_interval_95
        width_1k = ci_1k[1] - ci_1k[0]
        width_50k = ci_50k[1] - ci_50k[0]
        self.assertLess(width_50k, width_1k)

    def test_high_simulation_converges(self):
        r = run_single_vendor_simulation(
            vendor_id="HIGH_CONV",
            annual_spend=500_000,
            simulations=100000,
            seed=42,
        )
        # 100k sims should give very good convergence
        self.assertGreater(r.convergence_score, 0.95)


class TestFatTails(unittest.TestCase):
    """Student-t should produce more extreme values than Normal."""

    def test_student_t_has_fatter_tails_than_normal(self):
        rng = np.random.default_rng(42)
        n = 500_000

        t_shocks = generate_shocks(
            rng=np.random.default_rng(42),
            n=n, method="student_t",
            location=0.08, scale=0.06,
            min_clamp=0.0, max_clamp=0.50,  # wide clamp to see tails
        )
        normal_shocks = generate_shocks(
            rng=np.random.default_rng(42),
            n=n, method="normal",
            location=0.08, scale=0.06,
            min_clamp=0.0, max_clamp=0.50,
        )

        # Count extreme values (beyond 99th percentile of the normal)
        normal_p99 = np.percentile(normal_shocks, 99)
        t_extreme_count = np.sum(t_shocks > normal_p99)
        normal_extreme_count = np.sum(normal_shocks > normal_p99)

        # Student-t should have significantly more extreme values
        # (at least 1.5x more beyond the normal's 99th percentile)
        self.assertGreater(t_extreme_count, normal_extreme_count * 1.5)


class TestCorrelation(unittest.TestCase):
    """Correlated portfolio should have different risk profile than independent."""

    def test_correlation_matrix_same_category(self):
        categories = ["SaaS", "SaaS", "Cloud"]
        corr = build_correlation_matrix(categories)

        # Same category → high correlation
        self.assertAlmostEqual(corr[0, 1], 0.7)
        # Different category → low correlation
        self.assertAlmostEqual(corr[0, 2], 0.2)
        # Diagonal → 1.0
        self.assertAlmostEqual(corr[0, 0], 1.0)

    def test_cholesky_preserves_shape(self):
        rng = np.random.default_rng(42)
        n_sims, n_vendors = 1000, 3
        uncorrelated = rng.standard_normal((n_sims, n_vendors))
        corr = build_correlation_matrix(["SaaS", "SaaS", "Cloud"])
        correlated = apply_cholesky_correlation(rng, uncorrelated, corr)
        self.assertEqual(correlated.shape, (n_sims, n_vendors))

    def test_correlated_portfolio_differs_from_independent(self):
        vendors = [
            {"vendor_id": f"V{i}", "annual_spend": 200_000, "category": "SaaS"}
            for i in range(5)
        ]
        corr_result = run_portfolio_simulation(
            vendors, simulations=10000, correlated=True, seed=42,
        )
        indep_result = run_portfolio_simulation(
            vendors, simulations=10000, correlated=False, seed=42,
        )
        # Correlated same-category vendors should have higher portfolio std
        # because they all move together (less diversification benefit)
        self.assertGreater(corr_result.std_deviation, indep_result.std_deviation)

    def test_cross_category_less_correlated(self):
        """Mixed-category portfolio should have lower std than same-category."""
        same_cat = [
            {"vendor_id": f"S{i}", "annual_spend": 200_000, "category": "SaaS"}
            for i in range(5)
        ]
        mixed_cat = [
            {"vendor_id": "M0", "annual_spend": 200_000, "category": "SaaS"},
            {"vendor_id": "M1", "annual_spend": 200_000, "category": "Cloud"},
            {"vendor_id": "M2", "annual_spend": 200_000, "category": "Hardware"},
            {"vendor_id": "M3", "annual_spend": 200_000, "category": "Consulting"},
            {"vendor_id": "M4", "annual_spend": 200_000, "category": "Logistics"},
        ]
        same_r = run_portfolio_simulation(same_cat, simulations=20000, correlated=True, seed=42)
        mixed_r = run_portfolio_simulation(mixed_cat, simulations=20000, correlated=True, seed=42)

        # Same-category portfolio should have higher std (more correlated risk)
        self.assertGreater(same_r.std_deviation, mixed_r.std_deviation)


class TestDistributions(unittest.TestCase):
    """Test all distribution methods produce valid output."""

    def test_all_methods_produce_correct_shape(self):
        rng = np.random.default_rng(42)
        for method in ["student_t", "normal", "triangular"]:
            shocks = generate_shocks(rng=np.random.default_rng(42), n=1000, method=method)
            self.assertEqual(shocks.shape, (1000,))
            self.assertTrue(np.all(shocks >= 0.0))
            self.assertTrue(np.all(shocks <= 0.30))

    def test_invalid_method_raises(self):
        rng = np.random.default_rng(42)
        with self.assertRaises(ValueError):
            generate_shocks(rng=rng, n=100, method="invalid_dist")


class TestLargeSimulation(unittest.TestCase):
    """1M simulations should complete without OOM or error."""

    def test_1m_single_vendor_completes(self):
        result = run_single_vendor_simulation(
            vendor_id="LARGE_TEST",
            annual_spend=1_000_000,
            simulations=1_000_000,
            seed=42,
        )
        self.assertIsInstance(result, MonteCarloResult)
        self.assertEqual(result.simulations, 1_000_000)
        self.assertGreater(result.convergence_score, 0.99)


class TestResponseBackwardCompatibility(unittest.TestCase):
    """Verify all original fields are still present in results."""

    def test_single_vendor_has_all_original_fields(self):
        result = run_single_vendor_simulation(
            vendor_id="COMPAT",
            annual_spend=100_000,
            simulations=1000,
            seed=42,
        )
        # Original fields
        self.assertIsNotNone(result.vendor_id)
        self.assertIsNotNone(result.simulations)
        self.assertIsNotNone(result.mean_impact)
        self.assertIsNotNone(result.std_deviation)
        self.assertIsNotNone(result.percentile_10)
        self.assertIsNotNone(result.percentile_50)
        self.assertIsNotNone(result.percentile_90)
        self.assertIsNotNone(result.probability_exceeds_50k)
        self.assertIsNotNone(result.probability_exceeds_100k)
        self.assertIsNotNone(result.probability_exceeds_500k)
        self.assertIsNotNone(result.risk_rating)
        # New fields
        self.assertIsNotNone(result.seed)
        self.assertIsNotNone(result.distribution_type)
        self.assertIsNotNone(result.convergence_score)
        self.assertIsNotNone(result.confidence_interval_95)
        self.assertIsNotNone(result.percentile_05)
        self.assertIsNotNone(result.percentile_95)

    def test_portfolio_has_all_original_fields(self):
        vendors = [
            {"vendor_id": "V1", "annual_spend": 100_000, "category": "SaaS"},
            {"vendor_id": "V2", "annual_spend": 200_000, "category": "Cloud"},
        ]
        result = run_portfolio_simulation(vendors, simulations=1000, seed=42)
        # Original fields
        self.assertIsNotNone(result.simulations)
        self.assertIsNotNone(result.vendors_analyzed)
        self.assertIsNotNone(result.mean_portfolio_impact)
        self.assertIsNotNone(result.std_deviation)
        self.assertIsNotNone(result.percentile_10)
        self.assertIsNotNone(result.percentile_50)
        self.assertIsNotNone(result.percentile_90)
        self.assertIsNotNone(result.probability_exceeds_100k)
        self.assertIsNotNone(result.probability_exceeds_500k)
        self.assertIsNotNone(result.probability_exceeds_1m)
        self.assertIsNotNone(result.worst_case_vendor)
        self.assertIsNotNone(result.worst_case_amount)
        self.assertIsNotNone(result.risk_rating)
        self.assertIsNotNone(result.vendor_results)
        # New fields
        self.assertIsNotNone(result.seed)
        self.assertIsNotNone(result.distribution_type)
        self.assertIsNotNone(result.convergence_score)
        self.assertIsNotNone(result.confidence_interval_95)
        self.assertIsNotNone(result.correlation_method)


if __name__ == "__main__":
    unittest.main()

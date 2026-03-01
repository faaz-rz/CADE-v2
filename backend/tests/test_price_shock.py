"""
Tests for Price Shock Simulator.
"""

import unittest
from unittest.mock import patch
from app.simulation.price_shock import (
    PriceShockRequest,
    simulate_price_shock,
)
from app.services.analytics import VendorStats


MOCK_POLICIES = {
    "categories": {},
    "default": {
        "spend_threshold": 5000,
        "frequency_threshold": 5,
        "savings_rate": 0.10,
        "regulatory_sensitive": False,
        "operational_critical": False,
    },
}


class TestPriceShockSimulator(unittest.TestCase):

    def setUp(self):
        self.policy_patcher = patch("app.simulation.price_shock.policy_engine.get_policy")
        self.mock_policy = self.policy_patcher.start()
        self.mock_policy.return_value = MOCK_POLICIES["default"]

        self.stats_patcher = patch("app.simulation.price_shock.SpendingAnalyzer.get_vendor_stats")
        self.mock_stats = self.stats_patcher.start()

    def tearDown(self):
        self.policy_patcher.stop()
        self.stats_patcher.stop()

    def _set_vendor(self, entity="Acme", total_spend=50000, share=0.3):
        self.mock_stats.return_value = {
            entity: VendorStats(
                entity=entity,
                total_spend=total_spend,
                transaction_count=10,
                avg_value=total_spend / 10,
                category="SaaS",
                vendor_share_of_category=share,
            )
        }

    def test_basic_shock(self):
        self._set_vendor(total_spend=100000)
        req = PriceShockRequest(vendor_id="Acme", shock_percentage=10.0)
        result = simulate_price_shock(req)

        self.assertEqual(result.base_spend, 100000.0)
        self.assertEqual(result.shock_percentage, 10.0)
        self.assertEqual(result.delta_spend, 10000.0)
        self.assertEqual(result.new_spend, 110000.0)
        self.assertAlmostEqual(result.estimated_ebitda_delta, 2500.0)  # 10000 * 0.25

    def test_vendor_not_found(self):
        self.mock_stats.return_value = {}
        req = PriceShockRequest(vendor_id="NonExistent", shock_percentage=10.0)
        with self.assertRaises(ValueError):
            simulate_price_shock(req)

    def test_zero_shock(self):
        self._set_vendor(total_spend=50000)
        req = PriceShockRequest(vendor_id="Acme", shock_percentage=0.0)
        result = simulate_price_shock(req)
        self.assertEqual(result.delta_spend, 0.0)
        self.assertEqual(result.new_spend, 50000.0)

    def test_determinism(self):
        self._set_vendor(total_spend=80000)
        req = PriceShockRequest(vendor_id="Acme", shock_percentage=15.0)
        r1 = simulate_price_shock(req)
        r2 = simulate_price_shock(req)
        self.assertEqual(r1.model_dump(), r2.model_dump())

    def test_risk_escalation(self):
        """When shock pushes exposure above threshold, should escalate."""
        # Pre-shock: spend=4000, share=0.5 → exposure=2000 (below 5000 threshold)
        # After 200% shock: new_spend=12000, exposure=6000 (above 5000) → ESCALATED
        self._set_vendor(total_spend=4000, share=0.5)
        self.mock_policy.return_value = {"spend_threshold": 5000}
        req = PriceShockRequest(vendor_id="Acme", shock_percentage=200.0)
        result = simulate_price_shock(req)
        self.assertIn("ESCALATED", result.risk_classification_shift)


if __name__ == "__main__":
    unittest.main()

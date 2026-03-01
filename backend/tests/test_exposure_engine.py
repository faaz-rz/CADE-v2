"""
Tests for Exposure Engine — deterministic financial exposure calculations.
"""

import unittest
from app.services.exposure_engine import (
    calculate_exposure,
    calculate_shock_impact,
    EBITDA_MARGIN,
)
from app.services.analytics import VendorStats


class TestCalculateShockImpact(unittest.TestCase):
    """Tests for the reusable shock impact calculator."""

    def test_10pct_shock(self):
        impact, ebitda = calculate_shock_impact(100000, 10.0)
        self.assertEqual(impact, 10000.0)
        self.assertEqual(ebitda, 10000.0 * EBITDA_MARGIN)

    def test_20pct_shock(self):
        impact, ebitda = calculate_shock_impact(100000, 20.0)
        self.assertEqual(impact, 20000.0)
        self.assertEqual(ebitda, 20000.0 * EBITDA_MARGIN)

    def test_zero_shock(self):
        impact, ebitda = calculate_shock_impact(50000, 0.0)
        self.assertEqual(impact, 0.0)
        self.assertEqual(ebitda, 0.0)

    def test_determinism(self):
        """Same inputs must produce identical outputs."""
        r1 = calculate_shock_impact(75000, 15.0)
        r2 = calculate_shock_impact(75000, 15.0)
        self.assertEqual(r1, r2)


class TestCalculateExposure(unittest.TestCase):
    """Tests for per-vendor exposure calculation."""

    def _make_vendor(self, **kwargs) -> VendorStats:
        defaults = dict(
            entity="TestVendor",
            total_spend=50000.0,
            transaction_count=10,
            avg_value=5000.0,
            category="SaaS",
            vendor_share_of_category=0.3,
        )
        defaults.update(kwargs)
        return VendorStats(**defaults)

    def test_basic_exposure(self):
        vendor = self._make_vendor(total_spend=100000, vendor_share_of_category=0.5)
        exp = calculate_exposure(vendor)

        self.assertEqual(exp.vendor_id, "TestVendor")
        self.assertEqual(exp.annual_spend, 100000.0)
        self.assertEqual(exp.vendor_share_pct, 0.5)
        self.assertEqual(exp.worst_case_exposure, 50000.0)  # 100k * 0.5
        self.assertEqual(exp.price_shock_impact_10pct, 10000.0)
        self.assertEqual(exp.price_shock_impact_20pct, 20000.0)
        self.assertEqual(exp.estimated_ebitda_delta_10pct, 10000.0 * EBITDA_MARGIN)
        self.assertEqual(exp.estimated_ebitda_delta_20pct, 20000.0 * EBITDA_MARGIN)

    def test_zero_share(self):
        vendor = self._make_vendor(vendor_share_of_category=0.0)
        exp = calculate_exposure(vendor)
        self.assertEqual(exp.worst_case_exposure, 0.0)

    def test_full_concentration(self):
        vendor = self._make_vendor(total_spend=200000, vendor_share_of_category=1.0)
        exp = calculate_exposure(vendor)
        self.assertEqual(exp.worst_case_exposure, 200000.0)

    def test_determinism(self):
        """Identical VendorStats → identical FinancialExposure."""
        vendor = self._make_vendor()
        e1 = calculate_exposure(vendor)
        e2 = calculate_exposure(vendor)
        self.assertEqual(e1.model_dump(), e2.model_dump())


if __name__ == "__main__":
    unittest.main()

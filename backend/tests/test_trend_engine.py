"""
Tests for Trend Engine — rolling averages and growth percentage.
"""

import unittest
from app.services.trend_engine import _rolling_average, _growth_pct, EMERGING_RISK_THRESHOLD_PCT


class TestRollingAverage(unittest.TestCase):

    def test_basic_3m(self):
        values = [100, 200, 300]
        result = _rolling_average(values, 3)
        self.assertAlmostEqual(result, 200.0)

    def test_not_enough_data(self):
        values = [100, 200]
        result = _rolling_average(values, 3)
        self.assertIsNone(result)

    def test_longer_series(self):
        values = [10, 20, 30, 40, 50]
        result = _rolling_average(values, 3)
        self.assertAlmostEqual(result, 40.0)  # avg of [30, 40, 50]


class TestGrowthPct(unittest.TestCase):

    def test_basic_growth(self):
        # Earlier 3m: [100, 100, 100] avg=100, Recent 3m: [200, 200, 200] avg=200
        values = [100, 100, 100, 200, 200, 200]
        result = _growth_pct(values, 3)
        self.assertAlmostEqual(result, 100.0)  # 100% growth

    def test_no_growth(self):
        values = [500, 500, 500, 500, 500, 500]
        result = _growth_pct(values, 3)
        self.assertAlmostEqual(result, 0.0)

    def test_decline(self):
        values = [200, 200, 200, 100, 100, 100]
        result = _growth_pct(values, 3)
        self.assertAlmostEqual(result, -50.0)  # 50% decline

    def test_not_enough_data(self):
        values = [100, 200, 300]
        result = _growth_pct(values, 3)
        self.assertIsNone(result)

    def test_earlier_zero_spend(self):
        values = [0, 0, 0, 100, 100, 100]
        result = _growth_pct(values, 3)
        self.assertIsNone(result)  # Division by zero → None


class TestEmergingRiskThreshold(unittest.TestCase):

    def test_threshold_value(self):
        self.assertEqual(EMERGING_RISK_THRESHOLD_PCT, 20.0)


if __name__ == "__main__":
    unittest.main()

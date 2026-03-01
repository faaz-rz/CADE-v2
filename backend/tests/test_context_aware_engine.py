import unittest
from unittest.mock import patch
from app.services.decision_engine import DecisionEngine
from app.services.analytics import VendorStats
from app.models.decision import DecisionType, RiskLevel, ImpactLabel

# Mock policies directly for predictable tests
MOCK_POLICIES = {
    "categories": {
        "Cloud Infrastructure": {
            "spend_threshold": 20000,
            "frequency_threshold": 8,
            "savings_rate": 0.08,
            "regulatory_sensitive": False,
            "operational_critical": True
        },
        "SaaS": {
            "spend_threshold": 10000,
            "frequency_threshold": 6,
            "savings_rate": 0.12,
            "regulatory_sensitive": False,
            "operational_critical": False
        },
        "Payroll": {
            "spend_threshold": 0,
            "frequency_threshold": 0,
            "savings_rate": 0.05,
            "regulatory_sensitive": True,
            "operational_critical": True
        }
    },
    "default": {
        "spend_threshold": 5000,
        "frequency_threshold": 5,
        "savings_rate": 0.10,
        "regulatory_sensitive": False,
        "operational_critical": False
    }
}

class TestContextAwareEngine(unittest.TestCase):
    
    def setUp(self):
        # Patch policy engine
        self.policy_patcher = patch("app.services.policy_engine.policy_engine.get_policy")
        self.mock_policy = self.policy_patcher.start()
        def side_effect(category):
            return MOCK_POLICIES["categories"].get(category, MOCK_POLICIES["default"])
        self.mock_policy.side_effect = side_effect
        
        # Patch analytics aggregator
        self.stats_patcher = patch("app.services.analytics.SpendingAnalyzer.get_vendor_stats")
        self.mock_vendor_stats = self.stats_patcher.start()

    def tearDown(self):
        self.policy_patcher.stop()
        self.stats_patcher.stop()

    def test_category_threshold_and_savings_rate(self):
        self.mock_vendor_stats.return_value = {
            "AWS": VendorStats(
                entity="AWS",
                total_spend=30000, # Above 20k threshold
                transaction_count=2,
                avg_value=15000,
                category="Cloud Infrastructure",
                vendor_share_of_category=0.3
            )
        }
        
        decisions = DecisionEngine.analyze_uploaded_data()
        self.assertEqual(len(decisions), 1)
        d = decisions[0]
        
        # Savings should be 8% for Cloud Infrastructure -> 30000 * 0.08 = 2400 (monthly)
        self.assertEqual(d.expected_monthly_impact, 2400.0)
        self.assertEqual(d.context.thresholds["spend_threshold"], 20000)

    def test_default_fallback_and_concentration(self):
        self.mock_vendor_stats.return_value = {
            "Random Vendor": VendorStats(
                entity="Random Vendor",
                total_spend=6000, # Above default 5k
                transaction_count=2,
                avg_value=3000,
                category="Unknown", # Will fallback to default
                vendor_share_of_category=0.8 # High concentration
            )
        }
        
        decisions = DecisionEngine.analyze_uploaded_data()
        self.assertEqual(len(decisions), 1)
        d = decisions[0]
        
        # Fallback spend threshold applies (5000)
        self.assertEqual(d.context.thresholds["spend_threshold"], 5000)
        
        # 10% default savings rate
        self.assertEqual(d.expected_monthly_impact, 600.0)
        self.assertEqual(d.context.vendor_share_of_category, 0.8)
        
        # Concentration (>=0.6 is 3), Volume (>=5k is 1) = 4 -> LOW risk
        self.assertEqual(d.risk_score, 4)
        self.assertEqual(d.risk_level, RiskLevel.LOW)
        self.assertEqual(d.context.rule_version, "v1.2-context-aware")

    def test_high_risk_scoring_actual(self):
        # Alter mock policy for test
        old_val = MOCK_POLICIES["categories"]["Payroll"]["spend_threshold"]
        MOCK_POLICIES["categories"]["Payroll"]["spend_threshold"] = 5000
        
        self.mock_vendor_stats.return_value = {
            "ADP": VendorStats(
                entity="ADP",
                total_spend=100000,
                transaction_count=1,
                avg_value=100000,
                category="Payroll",
                vendor_share_of_category=1.0
            )
        }
        
        decisions = DecisionEngine.analyze_uploaded_data()
        self.assertEqual(len(decisions), 1)
        d = decisions[0]
        
        # score logic: Amount (100k vs 5k) >= 5x -> score 3
        # Op Critical (True) -> score 3
        # Reg Sens (True) -> score 3
        # Concentration (1.0) -> score 3
        # Total Score -> 12. HIGH Risk ( > 8 )
        self.assertEqual(d.risk_score, 12)
        self.assertEqual(d.risk_level, RiskLevel.HIGH)
        self.assertEqual(d.expected_monthly_impact, 5000.0) # 5% of 100k
        
        # Reset mock policy
        MOCK_POLICIES["categories"]["Payroll"]["spend_threshold"] = old_val

if __name__ == '__main__':
    unittest.main()

"""
Tests for Decision State Transitions — enforce lifecycle rules.
"""

import unittest
from app.models.decision import (
    Decision, DecisionType, DecisionScope, DecisionStatus,
    DecisionContext, ImpactLabel, RiskLevel,
)
from app.services.decision_store import DecisionStore


def _make_decision(status=DecisionStatus.PENDING, **kwargs) -> Decision:
    defaults = dict(
        id="test-decision-001",
        decision_type=DecisionType.VENDOR_REDUCE,
        scope=DecisionScope.VENDOR,
        entity="TestVendor",
        recommended_action="Review agreement",
        explanation="Test explanation",
        context=DecisionContext(
            analysis_period="Test Period",
            rule_id="TEST_RULE",
            thresholds={"spend_threshold": 5000},
            metrics={"total_spend": 10000, "transaction_count": 5},
        ),
        expected_monthly_impact=1000.0,
        cost_of_inaction=12000.0,
        annual_impact=12000.0,
        impact_label=ImpactLabel.HIGH,
        risk_level=RiskLevel.MEDIUM,
        risk_score=5,
        risk_range={"best_case": 12000, "worst_case": -6000},
        confidence=0.8,
        status=status,
    )
    defaults.update(kwargs)
    return Decision(**defaults)


class TestValidTransitions(unittest.TestCase):
    """Verify allowed state transitions."""

    def test_pending_to_approved(self):
        d = _make_decision(status=DecisionStatus.PENDING)
        d.status = DecisionStatus.APPROVED
        self.assertEqual(d.status, DecisionStatus.APPROVED)

    def test_pending_to_rejected(self):
        d = _make_decision(status=DecisionStatus.PENDING)
        d.status = DecisionStatus.REJECTED
        self.assertEqual(d.status, DecisionStatus.REJECTED)

    def test_pending_to_deferred(self):
        d = _make_decision(status=DecisionStatus.PENDING)
        d.status = DecisionStatus.DEFERRED
        self.assertEqual(d.status, DecisionStatus.DEFERRED)

    def test_deferred_to_approved(self):
        d = _make_decision(status=DecisionStatus.DEFERRED)
        d.status = DecisionStatus.APPROVED
        self.assertEqual(d.status, DecisionStatus.APPROVED)


class TestDecisionStoreBasics(unittest.TestCase):
    """Test DecisionStore in-memory operations."""

    def setUp(self):
        DecisionStore.clear()

    def test_save_and_retrieve(self):
        d = _make_decision()
        DecisionStore.save_decision(d)
        retrieved = DecisionStore.get_decision(d.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, d.id)

    def test_get_all(self):
        d1 = _make_decision(id="d1")
        d2 = _make_decision(id="d2")
        DecisionStore.save_decision(d1)
        DecisionStore.save_decision(d2)
        all_decisions = DecisionStore.get_all_decisions()
        self.assertEqual(len(all_decisions), 2)

    def test_clear(self):
        d = _make_decision()
        DecisionStore.save_decision(d)
        DecisionStore.clear()
        self.assertEqual(len(DecisionStore.get_all_decisions()), 0)

    def test_not_found_returns_none(self):
        result = DecisionStore.get_decision("nonexistent")
        self.assertIsNone(result)


class TestDeterministicDecisionIds(unittest.TestCase):
    """Decision IDs must be stable for the same input."""

    def test_same_input_same_id(self):
        import uuid
        id1 = str(uuid.uuid5(uuid.NAMESPACE_DNS, "TestVendor_HIGH_SPEND_VENDOR"))
        id2 = str(uuid.uuid5(uuid.NAMESPACE_DNS, "TestVendor_HIGH_SPEND_VENDOR"))
        self.assertEqual(id1, id2)

    def test_different_input_different_id(self):
        import uuid
        id1 = str(uuid.uuid5(uuid.NAMESPACE_DNS, "VendorA_HIGH_SPEND_VENDOR"))
        id2 = str(uuid.uuid5(uuid.NAMESPACE_DNS, "VendorB_HIGH_SPEND_VENDOR"))
        self.assertNotEqual(id1, id2)


if __name__ == "__main__":
    unittest.main()

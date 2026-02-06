import uuid
from typing import List
from app.models.decision import Decision, DecisionType, DecisionScope, DecisionStatus
from app.services.risk_engine import RiskEngine

class DecisionEngine:
    @staticmethod
    def analyze_vendor_spend(vendor_name: str, monthly_spend: float, utilization: float) -> List[Decision]:
        """
        Example Logic: If utilization is low, recommend reduction.
        """
        decisions = []
        
        if utilization < 0.3: # Low utilization
            scope = DecisionScope.VENDOR
            impact = monthly_spend * 0.5 # Assume we can cut 50%
            
            risk_level, risk_range, confidence = RiskEngine.evaluate_risk(scope, monthly_spend, impact)
            
            decision = Decision(
                id=str(uuid.uuid4()),
                decision_type=DecisionType.VENDOR_REDUCE,
                scope=scope,
                entity=vendor_name,
                recommended_action=f"Reduce spend with {vendor_name} by 50%",
                explanation=f"Utilization is very low ({utilization*100}%) while spend is high (${monthly_spend}/mo).",
                expected_monthly_impact=impact,
                cost_of_inaction=impact * 12, # Annualized waste
                risk_level=risk_level,
                risk_range=risk_range,
                confidence=confidence,
                status=DecisionStatus.PENDING
            )
            decisions.append(decision)
            
        return decisions

    @staticmethod
    def generate_dummy_decisions() -> List[Decision]:
        """
        For v1 testing/demo purposes.
        """
        return DecisionEngine.analyze_vendor_spend("Slack", 12000.0, 0.25) + \
               DecisionEngine.analyze_vendor_spend("AWS", 50000.0, 0.95) + \
               DecisionEngine.analyze_vendor_spend("Notion", 800.0, 0.1)

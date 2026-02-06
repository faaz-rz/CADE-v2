from typing import Dict, Tuple
from app.models.decision import RiskLevel, DecisionScope

class RiskEngine:
    @staticmethod
    def evaluate_risk(scope: DecisionScope, amount: float, impact: float) -> Tuple[RiskLevel, Dict[str, float], float]:
        """
        Returns: (RiskLevel, RiskRange, Confidence)
        
        Logic:
        - Higher impact removals are generally riskier.
        - Vendor logic: Cutting small vendors is low risk. Cutting large ones is high risk.
        """
        
        # Default Baseline
        risk_level = RiskLevel.LOW
        confidence = 0.9
        worst_case = 0.0
        
        if scope == DecisionScope.VENDOR:
            # Heuristic: If we cut a vendor, worst case is we have to re-onboard them at a premium + lost productivity
            if impact > 10000:
                risk_level = RiskLevel.MEDIUM
                confidence = 0.8
                worst_case = - (impact * 0.5) # Losing 50% more than the savings in productivity
                
            if impact > 50000:
                risk_level = RiskLevel.HIGH
                confidence = 0.6
                worst_case = - (impact * 1.5) # Major disruption risk
                
        elif scope == DecisionScope.PROJECT:
            # Project pauses are inherently riskier than vendor cuts
            risk_level = RiskLevel.MEDIUM
            confidence = 0.75
            worst_case = - (impact * 0.2)
            
            if impact > 20000:
                risk_level = RiskLevel.HIGH
                confidence = 0.6
                worst_case = - impact # Worst case: project fails, money wasted
                
        return risk_level, {"best_case": impact, "worst_case": worst_case}, confidence

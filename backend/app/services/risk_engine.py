from typing import Dict, Tuple, Any
from app.models.decision import RiskLevel, DecisionScope

class RiskEngine:
    @staticmethod
    def evaluate_risk(
        scope: DecisionScope, 
        amount: float, 
        impact: float, 
        policy: Dict[str, Any], 
        vendor_share: float = 0.0
    ) -> Tuple[RiskLevel, int, Dict[str, float], float]:
        """
        Returns: (RiskLevel, RiskScore, RiskRange, Confidence)
        
        Risk Factors (0-3 each):
        1. Spend Volume (vs threshold)
        2. Operational Criticality
        3. Regulatory Sensitivity
        4. Vendor Concentration
        """
        score = 0
        threshold = policy.get("spend_threshold", 5000)
        
        # 1. Spend Volume
        if threshold > 0:
            if amount >= 5 * threshold:
                score += 3
            elif amount >= 2 * threshold:
                score += 2
            elif amount >= threshold:
                score += 1
                
        # 2. Operational Criticality
        if policy.get("operational_critical", False):
            score += 3
            
        # 3. Regulatory Sensitivity
        if policy.get("regulatory_sensitive", False):
            score += 3
            
        # 4. Vendor Concentration
        if vendor_share >= 0.6:
            score += 3
        elif vendor_share >= 0.4:
            score += 2
        elif vendor_share >= 0.25:
            score += 1
            
        # Map Score -> Risk Level
        if score <= 4:
            risk_level = RiskLevel.LOW
            worst_case = 0.0
            confidence = 0.9
        elif score <= 8:
            risk_level = RiskLevel.MEDIUM
            worst_case = - (impact * 0.5)
            confidence = 0.8
        else:
            risk_level = RiskLevel.HIGH
            worst_case = - impact
            confidence = 0.6
            
        return risk_level, score, {"best_case": impact, "worst_case": worst_case}, confidence

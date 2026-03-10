import uuid
from typing import List
from app.models.decision import Decision, DecisionType, DecisionScope, DecisionStatus, RiskLevel
from app.services.risk_engine import RiskEngine

class DecisionEngine:
    @staticmethod
    def analyze_uploaded_data() -> List[Decision]:
        """
        Generates decisions based on actual uploaded transaction data.
        Uses Standard Templates and Structured Context.
        """
        from app.services.analytics import SpendingAnalyzer
        from app.core.decision_templates import get_template, TEMPLATES
        from app.models.decision import DecisionContext, ImpactLabel
        from app.services.policy_engine import policy_engine
        
        # Custom Import to avoid circular dependency
        from app.services.decision_store import DecisionStore
        
        # Reset Store for "Upload" workflow (v1 behavior)
        DecisionStore.clear()

        vendor_stats = SpendingAnalyzer.get_vendor_stats()
        decisions = []
        
        # Hardcoded for v1, in real app this comes from filter selection
        analysis_period = "Uploaded Period" 

        for vendor, stats in vendor_stats.items():
            
            policy = policy_engine.get_policy(stats.category)
            
            savings_rate = policy.get("savings_rate", 0.10)
            
            estimated_monthly_savings = stats.total_spend * savings_rate
            annual_impact = estimated_monthly_savings * 12

            if annual_impact >= 10000:
                impact_label = ImpactLabel.HIGH
            elif annual_impact >= 1000:
                impact_label = ImpactLabel.MEDIUM
            else:
                impact_label = ImpactLabel.LOW

            spend_threshold = policy.get("spend_threshold", 100)
            frequency_threshold = policy.get("frequency_threshold", 1)

            # Risk Evaluation
            risk_level, risk_score, risk_range, confidence = RiskEngine.evaluate_risk(
                scope=DecisionScope.VENDOR,
                amount=stats.total_spend,
                impact=annual_impact,
                policy=policy,
                vendor_share=stats.vendor_share_of_category
            )

            # ONE DECISION PER VENDOR RULE: Prioritize Spend > Frequency
            
            # Rule 1: High Spend
            if spend_threshold > 0 and stats.total_spend >= spend_threshold:
                template = TEMPLATES["HIGH_SPEND"]
                
                applied_thresholds = {
                    "spend_threshold": spend_threshold,
                    "frequency_threshold": frequency_threshold
                }

                context = DecisionContext(
                    analysis_period=analysis_period,
                    rule_id=template.rule_id,
                    thresholds={"spend_threshold": spend_threshold},
                    metrics={
                        "total_spend": stats.total_spend,
                        "transaction_count": float(stats.transaction_count)
                    },
                    vendor_share_of_category=stats.vendor_share_of_category,
                    rule_version="v1.2-context-aware",
                    applied_thresholds=applied_thresholds
                )

                # DETERMINISTIC ID: Ensure ID is stable across restarts for the same vendor/rule
                decision_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{vendor}_{template.rule_id}"))

                decision = Decision(
                     id=decision_id,
                     decision_type=DecisionType.VENDOR_REDUCE,
                     scope=DecisionScope.VENDOR,
                     entity=vendor,
                     recommended_action=template.render_action(),
                     explanation=template.render_explanation(
                         entity=vendor, 
                         total_spend=stats.total_spend, 
                         threshold=spend_threshold
                     ),
                     context=context,
                     expected_monthly_impact=estimated_monthly_savings,
                     cost_of_inaction=annual_impact,
                     annual_impact=annual_impact,
                     impact_label=impact_label,
                     risk_level=risk_level,
                     risk_score=risk_score,
                     risk_range=risk_range,
                     confidence=confidence,
                     status=DecisionStatus.PENDING
                )
                decisions.append(decision)
                continue 
            
            # Rule 2: High Frequency
            if frequency_threshold > 0 and stats.transaction_count > frequency_threshold:
                template = TEMPLATES["HIGH_FREQUENCY"]

                applied_thresholds = {
                    "spend_threshold": spend_threshold,
                    "frequency_threshold": frequency_threshold
                }

                context = DecisionContext(
                    analysis_period=analysis_period,
                    rule_id=template.rule_id,
                    thresholds={"frequency_threshold": frequency_threshold},
                    metrics={
                        "total_spend": stats.total_spend,
                        "transaction_count": float(stats.transaction_count)
                    },
                    vendor_share_of_category=stats.vendor_share_of_category,
                    rule_version="v1.2-context-aware",
                    applied_thresholds=applied_thresholds
                )

                # DETERMINISTIC ID
                decision_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{vendor}_{template.rule_id}"))

                decision = Decision(
                     id=decision_id,
                     decision_type=DecisionType.VENDOR_CONSOLIDATE,
                     scope=DecisionScope.VENDOR,
                     entity=vendor,
                     recommended_action=template.render_action(),
                     explanation=template.render_explanation(
                         entity=vendor, 
                         transaction_count=stats.transaction_count
                     ),
                     context=context,
                     expected_monthly_impact=estimated_monthly_savings,
                     cost_of_inaction=annual_impact,
                     annual_impact=annual_impact,
                     impact_label=impact_label,
                     risk_level=risk_level,
                     risk_score=risk_score,
                     risk_range=risk_range,
                     confidence=confidence,
                     status=DecisionStatus.PENDING
                )
                decisions.append(decision)

        # SORTING: High Impact First
        decisions.sort(key=lambda d: d.annual_impact, reverse=True)
        
        # PERSISTENCE: Save to Store
        from app.services.decision_store import DecisionStore
        for d in decisions:
            DecisionStore.save_decision(d)
            
        return decisions

    @staticmethod
    def get_summary_stats(decisions: List[Decision]):
        """
        Aggregates stats for the Executive Portfolio View.
        """
        from app.models.summary import DecisionSummary
        
        total_savings = sum(d.annual_impact for d in decisions)
        # Count Pending Actions
        pending_count = len([d for d in decisions if d.status == DecisionStatus.PENDING])
        # Count Pending High Impact
        from app.models.decision import ImpactLabel
        pending_high_impact = len([d for d in decisions if d.status == DecisionStatus.PENDING and d.impact_label == ImpactLabel.HIGH])

        impact_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

        for d in decisions:
            if d.impact_label.value in impact_counts:
                impact_counts[d.impact_label.value] += 1
            
            if d.risk_level.value in risk_counts:
                risk_counts[d.risk_level.value] += 1

        return DecisionSummary(
            total_savings=total_savings,
            total_decisions=len(decisions),
            pending_count=pending_count,
            pending_high_impact=pending_high_impact,
            impact_breakdown=impact_counts,
            risk_breakdown=risk_counts
        )

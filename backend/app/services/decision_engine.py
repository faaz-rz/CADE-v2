import uuid
from typing import List, Dict, Optional
from collections import defaultdict
from app.models.decision import Decision, DecisionType, DecisionScope, DecisionStatus, RiskLevel
from app.services.risk_engine import RiskEngine

class DecisionEngine:
    @staticmethod
    def analyze_uploaded_data() -> List[Decision]:
        """
        Generates decisions based on actual uploaded transaction data.
        Uses 7 prioritized rules — each vendor gets at most ONE decision.

        Priority Order:
          1. CONCENTRATION_RISK   — vendor_share >= 40%
          2. RAPID_GROWTH         — 3-month growth > 20%
          3. HIGH_ABSOLUTE_SPEND  — spend >= 5x threshold
          4. CONTRACT_RENEWAL     — SaaS category at threshold
          5. DUPLICATE_VENDOR_CAT — 3+ vendors in same category (once per category)
          6. HIGH_SPEND           — spend >= threshold  (existing rule)
          7. HIGH_FREQUENCY       — transactions > freq threshold (existing fallback)
        """
        from app.services.analytics import SpendingAnalyzer
        from app.core.decision_templates import TEMPLATES
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

        # ── Pre-compute trend data (for RAPID_GROWTH rule) ──
        trend_lookup: Dict[str, dict] = {}
        try:
            from app.services.trend_engine import calculate_vendor_trends
            trends = calculate_vendor_trends()
            for t in trends:
                trend_lookup[t.vendor_id] = {
                    "growth_pct_3m": t.growth_pct_3m,
                    "rolling_avg_3m": t.rolling_avg_3m,
                    "rolling_avg_6m": t.rolling_avg_6m,
                    "monthly_spends": t.monthly_spends,
                }
        except Exception:
            pass  # Trend data unavailable — skip RAPID_GROWTH rule

        # ── Pre-compute category vendor counts (for DUPLICATE_VENDOR_CATEGORY rule) ──
        category_vendors: Dict[str, List[str]] = defaultdict(list)
        for vendor, stats in vendor_stats.items():
            cat = getattr(stats, 'category', 'Uncategorized')
            category_vendors[cat].append(vendor)

        # Track which categories already had a DUPLICATE decision fired
        categories_with_dup_decision: set = set()

        # Track vendors that received a decision (for ONE-DECISION-PER-VENDOR rule)
        decided_vendors: set = set()

        for vendor, stats in vendor_stats.items():
            if vendor in decided_vendors:
                continue

            policy = policy_engine.get_policy(getattr(stats, 'category', 'Uncategorized'))

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
                vendor_share=getattr(stats, 'vendor_share_of_category', 0.0)
            )

            vendor_share = getattr(stats, 'vendor_share_of_category', 0.0)
            category = getattr(stats, 'category', 'Uncategorized')

            # Helper to build a decision and mark vendor as decided
            def _make_decision(template_key, decision_type, action_kwargs=None, explanation_kwargs=None, rule_thresholds=None):
                template = TEMPLATES[template_key]
                applied_thresholds = {
                    "spend_threshold": spend_threshold,
                    "frequency_threshold": frequency_threshold
                }

                context = DecisionContext(
                    analysis_period=analysis_period,
                    rule_id=template.rule_id,
                    thresholds=rule_thresholds or {"spend_threshold": spend_threshold},
                    metrics={
                        "total_spend": stats.total_spend,
                        "transaction_count": float(stats.transaction_count)
                    },
                    vendor_share_of_category=vendor_share,
                    rule_version="v1.2-context-aware",
                    applied_thresholds=applied_thresholds
                )

                # DETERMINISTIC ID: Ensure ID is stable across restarts for the same vendor/rule
                decision_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{vendor}_{template.rule_id}"))

                decision = Decision(
                    id=decision_id,
                    decision_type=decision_type,
                    scope=DecisionScope.VENDOR,
                    entity=vendor,
                    recommended_action=template.render_action(**(action_kwargs or {})),
                    explanation=template.render_explanation(**(explanation_kwargs or {})),
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
                decided_vendors.add(vendor)

            # ═══════════════════════════════════════════
            # RULE 1: CONCENTRATION_RISK
            # ═══════════════════════════════════════════
            if vendor_share >= 0.40:
                _make_decision(
                    template_key="CONCENTRATION_RISK",
                    decision_type=DecisionType.VENDOR_REDUCE,
                    explanation_kwargs={"entity": vendor, "vendor_share": vendor_share},
                    rule_thresholds={"spend_threshold": spend_threshold, "concentration_threshold": 0.40},
                )
                continue

            # ═══════════════════════════════════════════
            # RULE 2: RAPID_GROWTH
            # ═══════════════════════════════════════════
            trend_data = trend_lookup.get(vendor)
            if trend_data and trend_data.get("growth_pct_3m") is not None:
                growth_pct = trend_data["growth_pct_3m"]  # e.g. 25.0 = 25%
                if growth_pct > 20.0:
                    growth_rate = growth_pct / 100.0  # Convert to ratio for formatting
                    num_months = len(trend_data.get("monthly_spends", []))
                    months_of_data = max(num_months, 1)
                    monthly_rate = stats.total_spend / months_of_data
                    projected_quarter = monthly_rate * (1 + growth_rate) * 3
                    budget_quarter = monthly_rate * 3
                    overspend = projected_quarter - budget_quarter

                    _make_decision(
                        template_key="RAPID_GROWTH",
                        decision_type=DecisionType.COST_REDUCE,
                        explanation_kwargs={
                            "entity": vendor,
                            "growth": growth_rate,
                            "overspend": overspend,
                        },
                        rule_thresholds={"growth_threshold_pct": 20.0},
                    )
                    continue

            # ═══════════════════════════════════════════
            # RULE 3: HIGH_ABSOLUTE_SPEND
            # ═══════════════════════════════════════════
            if spend_threshold > 0 and stats.total_spend >= spend_threshold * 5:
                multiple = stats.total_spend / spend_threshold
                savings = annual_impact

                _make_decision(
                    template_key="HIGH_ABSOLUTE_SPEND",
                    decision_type=DecisionType.VENDOR_REDUCE,
                    explanation_kwargs={
                        "entity": vendor,
                        "total_spend": stats.total_spend,
                        "multiple": multiple,
                        "threshold": spend_threshold,
                        "savings": savings,
                    },
                    rule_thresholds={"spend_threshold": spend_threshold},
                )
                continue

            # ═══════════════════════════════════════════
            # RULE 4: CONTRACT_RENEWAL_WINDOW
            # ═══════════════════════════════════════════
            if category == "SaaS" and spend_threshold > 0 and stats.total_spend >= spend_threshold:
                # SaaS renewal discount estimate: 15-20%, use 0.175 midpoint
                saas_savings = stats.total_spend * 0.175

                _make_decision(
                    template_key="CONTRACT_RENEWAL",
                    decision_type=DecisionType.COST_REDUCE,
                    explanation_kwargs={
                        "entity": vendor,
                        "total_spend": stats.total_spend,
                        "savings": saas_savings,
                    },
                    rule_thresholds={"spend_threshold": spend_threshold},
                )
                continue

            # ═══════════════════════════════════════════
            # RULE 5: DUPLICATE_VENDOR_CATEGORY
            # ═══════════════════════════════════════════
            vendors_in_cat = category_vendors.get(category, [])
            if (len(vendors_in_cat) >= 3
                    and category not in categories_with_dup_decision
                    and category != "Uncategorized"):
                # Only fire for the smallest vendor in this category
                smallest_vendor = min(
                    vendors_in_cat,
                    key=lambda v: vendor_stats[v].total_spend
                )
                if vendor == smallest_vendor:
                    total_cat_spend = sum(vendor_stats[v].total_spend for v in vendors_in_cat)
                    consolidation_savings = total_cat_spend * 0.25  # 20-30% midpoint

                    categories_with_dup_decision.add(category)
                    _make_decision(
                        template_key="DUPLICATE_VENDOR_CATEGORY",
                        decision_type=DecisionType.VENDOR_REDUCE,
                        explanation_kwargs={
                            "vendor_count": len(vendors_in_cat),
                            "category": category,
                            "savings": consolidation_savings,
                        },
                        rule_thresholds={"min_vendors_in_category": 3},
                    )
                    continue

            # ═══════════════════════════════════════════
            # RULE 6: HIGH_SPEND_BASELINE (existing rule)
            # ═══════════════════════════════════════════
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
                    vendor_share_of_category=vendor_share,
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
                decided_vendors.add(vendor)
                continue

            # ═══════════════════════════════════════════
            # RULE 7: HIGH_FREQUENCY (existing fallback)
            # ═══════════════════════════════════════════
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
                    vendor_share_of_category=vendor_share,
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
                decided_vendors.add(vendor)

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

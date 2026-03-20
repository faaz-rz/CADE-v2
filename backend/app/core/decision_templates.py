
from typing import Dict, Any
from pydantic import BaseModel

class DecisionTemplate(BaseModel):
    """
    Standardized template for a decision type.
    Ensures consisent language across the system.
    """
    rule_id: str
    action_template: str
    explanation_template: str
    
    def render_action(self, **kwargs) -> str:
        return self.action_template.format(**kwargs)

    def render_explanation(self, **kwargs) -> str:
        return self.explanation_template.format(**kwargs)

# Registry of Templates
# "Same facts -> same language -> every time."

TEMPLATES = {
    "CONCENTRATION_RISK": DecisionTemplate(
        rule_id="CONCENTRATION_RISK",
        action_template="Critical vendor concentration risk",
        explanation_template="{entity} represents {vendor_share:.0%} of total spend — single vendor dependency is dangerous. Identify and qualify at least one alternative supplier."
    ),
    "RAPID_GROWTH": DecisionTemplate(
        rule_id="RAPID_GROWTH",
        action_template="Vendor spend growing unsustainably fast",
        explanation_template="{entity} spend has grown {growth:.0%} over the last 3 months. At this rate you will exceed budget by ${overspend:,.0f} this quarter. Review usage and negotiate a volume cap."
    ),
    "HIGH_ABSOLUTE_SPEND": DecisionTemplate(
        rule_id="HIGH_ABSOLUTE_SPEND",
        action_template="Vendor spend significantly above threshold",
        explanation_template="Total spend with {entity} (${total_spend:,.0f}) is {multiple:.1f}x above the ${threshold:,.0f} review threshold. Renegotiate contract or consolidate usage — estimated savings: ${savings:,.0f}."
    ),
    "CONTRACT_RENEWAL": DecisionTemplate(
        rule_id="CONTRACT_RENEWAL_WINDOW",
        action_template="SaaS contract review opportunity",
        explanation_template="{entity} is a SaaS vendor at ${total_spend:,.0f}/period. SaaS contracts typically offer 15-20% discount at renewal. Initiate renegotiation now to capture estimated savings of ${savings:,.0f}."
    ),
    "DUPLICATE_VENDOR_CATEGORY": DecisionTemplate(
        rule_id="DUPLICATE_VENDOR_CATEGORY",
        action_template="Vendor consolidation opportunity",
        explanation_template="You have {vendor_count} vendors in {category}. Consolidating to 1-2 preferred vendors could reduce spend by 20-30% through volume discounts. Estimated savings: ${savings:,.0f}."
    ),
    "HIGH_SPEND": DecisionTemplate(
        rule_id="HIGH_SPEND_VENDOR",
        action_template="Review vendor agreement due to high cumulative spend",
        explanation_template="Total spend with {entity} (${total_spend:,.2f}) over the analysis period is significantly higher than the threshold (${threshold:,.0f})."
    ),
    "HIGH_FREQUENCY": DecisionTemplate(
        rule_id="HIGH_FREQUENCY_VENDOR",
        action_template="Consolidate transactions to reduce overhead",
        explanation_template="High frequency of transactions ({transaction_count}) with {entity} indicates potential for consolidation to reduce administrative overhead."
    )
}

def get_template(rule_id: str) -> DecisionTemplate:
    if rule_id not in TEMPLATES:
         raise ValueError(f"Template not found for rule: {rule_id}")
    return TEMPLATES[rule_id]


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

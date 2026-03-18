"""
AI Narrator — Groq-powered executive narrative generator.

Uses llama-3.1-70b-versatile to create 4-sentence CFO board summaries.
Falls back to template narrative if GROQ_API_KEY is missing or API fails.
"""

import os
import logging
from groq import Groq

logger = logging.getLogger(__name__)


async def generate_board_narrative(
    total_spend: float,
    high_risk_count: int,
    top_vendor_name: str,
    top_vendor_spend: float,
    decision_count: int,
    estimated_savings: float,
    ebitda_at_risk: float,
) -> str:
    """
    Generate a 4-sentence executive summary using Groq LLM.
    Returns fallback narrative if API key is missing or call fails.
    """
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return _fallback_narrative(
            total_spend, high_risk_count, top_vendor_name,
            top_vendor_spend, decision_count, estimated_savings,
        )

    try:
        client = Groq(api_key=api_key)
        prompt = f"""You are writing the executive summary \
for a CFO board report. Write exactly 4 sentences. \
Be specific. Use dollar figures. \
Lead with the most important vendor risk. \
No jargon. No bullet points. \
Sound like a senior CFO advisor.

Data for this period:
- Total vendor spend: ${total_spend:,.0f}
- Vendors flagged HIGH risk: {high_risk_count}
- Highest risk vendor: {top_vendor_name} \
at ${top_vendor_spend:,.0f} per year
- Capital allocation decisions made: {decision_count}
- Estimated savings identified: ${estimated_savings:,.0f}
- EBITDA at risk (10% shock): ${ebitda_at_risk:,.0f}

Write the 4-sentence executive summary:"""

        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            temperature=0.3,
            max_tokens=350,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.warning(f"Groq API failed: {e} — using fallback")
        return _fallback_narrative(
            total_spend, high_risk_count, top_vendor_name,
            top_vendor_spend, decision_count, estimated_savings,
        )


def _fallback_narrative(
    total_spend: float,
    high_risk_count: int,
    top_vendor_name: str,
    top_vendor_spend: float,
    decision_count: int,
    estimated_savings: float,
) -> str:
    """Template-based fallback when Groq is unavailable."""
    return (
        f"Total vendor spend this period reached "
        f"${total_spend:,.0f} across all tracked categories. "
        f"{high_risk_count} vendor(s) have been flagged as "
        f"HIGH risk, with {top_vendor_name} representing the "
        f"greatest exposure at ${top_vendor_spend:,.0f} annually. "
        f"The platform generated {decision_count} capital "
        f"allocation decision(s) this period for management review. "
        f"Implementing the recommended actions could yield "
        f"estimated savings of ${estimated_savings:,.0f}."
    )

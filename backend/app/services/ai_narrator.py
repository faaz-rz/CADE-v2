"""
AI Narrator — Groq-powered executive narrative generator.

Uses llama-3.1-70b-versatile to create 4-sentence CFO board summaries.
Falls back to template narrative if GROQ_API_KEY is missing or API fails.
"""

import os
import logging
from groq import Groq

logger = logging.getLogger(__name__)

async def generate_decision_narrative(
    vendor_name: str,
    annual_spend: float,
    risk_level: str,
    decision_type: str,
    rule_id: str,
    vendor_share: float,
    category: str,
    estimated_savings: float,
    worst_case_risk: float,
) -> str:
    """
    Generate a 3-sentence risk assessment using Groq LLM.
    Returns fallback narrative if API key is missing or call fails.
    """
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return _fallback_decision_narrative(
            vendor_name, annual_spend, risk_level, estimated_savings
        )

    try:
        client = Groq(api_key=api_key)
        prompt = f"""You are a senior CFO advisor writing a 
concise risk assessment for a capital allocation decision.

Write exactly 3 sentences. Be specific. Use dollar figures.
Sound like a senior finance professional, not a software tool.
No bullet points. No headers. Plain paragraph only.

Decision data:
- Vendor: {vendor_name}
- Annual spend: ${annual_spend:,.0f}
- Risk level: {risk_level}
- Rule triggered: {rule_id}
- Vendor share of category: {vendor_share:.0%}
- Category: {category}
- Estimated savings if acted on: ${estimated_savings:,.0f}
- Worst case exposure: ${worst_case_risk:,.0f}

Write the 3-sentence advisor assessment now:"""

        import hashlib
        import sqlite3
        
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        cache_db_path = os.path.join("data", "ai_cache.db")
        os.makedirs("data", exist_ok=True)
        
        with sqlite3.connect(cache_db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS cache (hash TEXT PRIMARY KEY, response TEXT)")
            cursor = conn.cursor()
            cursor.execute("SELECT response FROM cache WHERE hash = ?", (prompt_hash,))
            row = cursor.fetchone()
            if row:
                logger.info(f"AI narrative CACHE HIT for {vendor_name}")
                return row[0]

        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            temperature=0.0,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        narrative = response.choices[0].message.content.strip()
        
        with sqlite3.connect(cache_db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO cache (hash, response) VALUES (?, ?)", (prompt_hash, narrative))
            
        logger.info(f"AI narrative generated (and cached) for {vendor_name}")
        return narrative

    except Exception as e:
        logger.warning(f"Groq failed for {vendor_name}: {e}")
        return _fallback_decision_narrative(
            vendor_name, annual_spend, risk_level, estimated_savings
        )

def _fallback_decision_narrative(
    vendor_name: str,
    annual_spend: float,
    risk_level: str,
    estimated_savings: float,
) -> str:
    return (
        f"{vendor_name} has been flagged as {risk_level} risk "
        f"with ${annual_spend:,.0f} in annual spend. "
        f"Immediate review of this vendor relationship is "
        f"recommended to protect EBITDA. "
        f"Implementing the recommended action could yield "
        f"estimated savings of ${estimated_savings:,.0f}."
    )



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

        import hashlib
        import sqlite3
        
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        cache_db_path = os.path.join("data", "ai_cache.db")
        os.makedirs("data", exist_ok=True)
        
        with sqlite3.connect(cache_db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS cache (hash TEXT PRIMARY KEY, response TEXT)")
            cursor = conn.cursor()
            cursor.execute("SELECT response FROM cache WHERE hash = ?", (prompt_hash,))
            row = cursor.fetchone()
            if row:
                logger.info("AI board narrative CACHE HIT")
                return row[0]

        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            temperature=0.0,
            max_tokens=350,
            messages=[{"role": "user", "content": prompt}],
        )
        narrative = response.choices[0].message.content.strip()
        
        with sqlite3.connect(cache_db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO cache (hash, response) VALUES (?, ?)", (prompt_hash, narrative))
            
        logger.info("AI board narrative generated (and cached)")
        return narrative

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


async def generate_hospital_board_narrative(
    total_vendor_spend: float,
    pharma_spend: float,
    equipment_spend: float,
    high_risk_count: int,
    top_vendor: str,
    estimated_savings: float,
    amc_savings_opportunity: float,
    price_comparison_savings: float,
) -> str:
    """
    Generate a 4-sentence hospital CFO board summary using Groq LLM.
    Uses Indian Rupees. Falls back to template if API key is missing.
    """
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return _fallback_hospital_narrative(
            total_vendor_spend, pharma_spend, equipment_spend,
            high_risk_count, top_vendor, estimated_savings,
            amc_savings_opportunity, price_comparison_savings,
        )

    try:
        client = Groq(api_key=api_key)
        prompt = f"""You are writing the procurement summary \
for a hospital CFO board report in India.
Write exactly 4 sentences. Use Indian Rupees (₹).
Be specific about medical procurement.
Sound like a senior hospital finance advisor.
No bullet points. Plain paragraph only.

Hospital procurement data:
- Total annual vendor spend: ₹{total_vendor_spend:,.0f}
- Pharma and consumables spend: ₹{pharma_spend:,.0f}
- Medical equipment spend: ₹{equipment_spend:,.0f}
- High risk vendors: {high_risk_count}
- Highest risk vendor: {top_vendor}
- Total savings identified: ₹{estimated_savings:,.0f}
- AMC renegotiation opportunity: ₹{amc_savings_opportunity:,.0f}
- Supplier consolidation savings: ₹{price_comparison_savings:,.0f}

Write the 4-sentence hospital CFO board summary:"""

        import hashlib
        import sqlite3

        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        cache_db_path = os.path.join("data", "ai_cache.db")
        os.makedirs("data", exist_ok=True)

        with sqlite3.connect(cache_db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS cache (hash TEXT PRIMARY KEY, response TEXT)")
            cursor = conn.cursor()
            cursor.execute("SELECT response FROM cache WHERE hash = ?", (prompt_hash,))
            row = cursor.fetchone()
            if row:
                logger.info("Hospital board narrative CACHE HIT")
                return row[0]

        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            temperature=0.0,
            max_tokens=350,
            messages=[{"role": "user", "content": prompt}],
        )
        narrative = response.choices[0].message.content.strip()

        with sqlite3.connect(cache_db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO cache (hash, response) VALUES (?, ?)", (prompt_hash, narrative))

        logger.info("Hospital board narrative generated (and cached)")
        return narrative

    except Exception as e:
        logger.warning(f"Groq API failed for hospital narrative: {e} — using fallback")
        return _fallback_hospital_narrative(
            total_vendor_spend, pharma_spend, equipment_spend,
            high_risk_count, top_vendor, estimated_savings,
            amc_savings_opportunity, price_comparison_savings,
        )


def _fallback_hospital_narrative(
    total_vendor_spend: float,
    pharma_spend: float,
    equipment_spend: float,
    high_risk_count: int,
    top_vendor: str,
    estimated_savings: float,
    amc_savings_opportunity: float,
    price_comparison_savings: float,
) -> str:
    """Template-based fallback for hospital board narrative."""
    return (
        f"Total hospital vendor spend this period reached "
        f"₹{total_vendor_spend:,.0f}, with pharma and consumables "
        f"accounting for ₹{pharma_spend:,.0f} and medical equipment "
        f"at ₹{equipment_spend:,.0f}. "
        f"{high_risk_count} vendor(s) have been flagged as HIGH risk, "
        f"with {top_vendor} representing the greatest procurement "
        f"exposure requiring immediate management attention. "
        f"The platform identified ₹{estimated_savings:,.0f} in total "
        f"savings through vendor consolidation, contract renegotiation, "
        f"and competitive tendering. "
        f"Additional opportunities include ₹{amc_savings_opportunity:,.0f} "
        f"in AMC renegotiation and ₹{price_comparison_savings:,.0f} "
        f"through supplier price optimization."
    )

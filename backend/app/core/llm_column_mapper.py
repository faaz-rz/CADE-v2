import os
import json

async def map_columns_with_llm(columns: list[str], sample_values: dict) -> dict:
    """
    LAYER 3 — LLM COLUMN MAPPER
    Uses Groq Llama 3.1 to guess columns if deterministic fuzzy tools fail.
    """
    try:
        from groq import Groq
    except ImportError:
        return {}
        
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return {}

    prompt = f"""
I have a financial spreadsheet with columns: {columns}
Sample values from first 3 rows: {sample_values}

Map each column to one of these canonical fields or null:
entity, amount, date, category, currency, gl_code, cost_center, po_number, description, invoice_id

Rules:
- Only map if confident
- One canonical field per column maximum
- Return valid JSON only: {{"original_column": "canonical_field"}}
- Use null for uncertain columns
"""
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            temperature=0,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        # Small cleanup in case LLM added markdown backticks
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        return json.loads(content)
    except Exception as e:
        print(f"LLM Mapping error: {e}")
        return {}

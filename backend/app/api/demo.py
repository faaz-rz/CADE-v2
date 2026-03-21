"""
Demo Mode — Seed realistic vendor data so the dashboard is populated on first visit.

POST /api/demo/load  → writes synthetic transactions, runs DecisionEngine, returns count
DELETE /api/demo/clear → wipes demo data, returns to empty state
"""

import json
import os
from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends
from app.models.canonical import CanonicalFinancialRecord
from app.core.auth import verify_token

router = APIRouter()

# ── Demo vendor definitions (exact names and amounts from spec) ──
DEMO_VENDORS = [
    {"entity": "SALESFORCE",             "amount": 210000, "category": "SaaS",                  "currency": "USD"},
    {"entity": "AMAZON WEB SERVICES",    "amount": 340000, "category": "Cloud Infrastructure",  "currency": "USD"},
    {"entity": "WORKDAY",                "amount": 180000, "category": "SaaS",                  "currency": "USD"},
    {"entity": "SNOWFLAKE",              "amount": 95000,  "category": "Cloud Infrastructure",  "currency": "USD"},
    {"entity": "HUBSPOT",                "amount": 72000,  "category": "SaaS",                  "currency": "USD"},
    {"entity": "SLACK",                  "amount": 48000,  "category": "SaaS",                  "currency": "USD"},
    {"entity": "ZENDESK",                "amount": 36000,  "category": "SaaS",                  "currency": "USD"},
    {"entity": "DOCUSIGN",               "amount": 24000,  "category": "SaaS",                  "currency": "USD"},
]

# Number of monthly transactions to create per vendor (spreads the total evenly)
MONTHS = 12


def _build_demo_records() -> List[CanonicalFinancialRecord]:
    """
    Turn DEMO_VENDORS into CanonicalFinancialRecord objects —
    one transaction per month per vendor, amount split evenly.
    """
    records: List[CanonicalFinancialRecord] = []
    base_date = date(2025, 1, 15)

    for vendor in DEMO_VENDORS:
        monthly_amount = vendor["amount"] / MONTHS
        for month_offset in range(MONTHS):
            txn_date = base_date + timedelta(days=30 * month_offset)
            records.append(
                CanonicalFinancialRecord(
                    date=txn_date,
                    amount=round(monthly_amount, 2),
                    category=vendor["category"],
                    entity=vendor["entity"],
                    currency=vendor["currency"],
                    source_file="demo_data.csv",
                )
            )

    return records


@router.post("")
async def load_demo_data(payload: dict = Depends(verify_token)):
    """
    Load realistic demo data into the decision store.
    Wipes existing data first, then generates decisions through the real engine.
    """
    from app.services.decision_store import DecisionStore
    from app.services.decision_engine import DecisionEngine

    # 1. Clear existing state
    DecisionStore.clear()

    # 2. Write demo transactions to data/transactions.json
    records = _build_demo_records()
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    output_data = [r.model_dump(mode="json") for r in records]
    with open(os.path.join(data_dir, "transactions.json"), "w") as f:
        json.dump(output_data, f, indent=2)

    # 3. Run the real DecisionEngine (reads transactions.json → generates decisions)
    decisions = DecisionEngine.analyze_uploaded_data()

    return {"status": "loaded", "decisions_generated": len(decisions)}


@router.delete("")
async def clear_demo_data(payload: dict = Depends(verify_token)):
    """
    Wipe all demo data and return to empty state.
    """
    from app.services.decision_store import DecisionStore

    DecisionStore.clear()

    # Reset transactions.json
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, "transactions.json"), "w") as f:
        json.dump([], f)

    return {"status": "cleared"}

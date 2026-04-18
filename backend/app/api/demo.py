"""
Demo Mode — Seed realistic hospital vendor data so the dashboard
is populated on first visit.

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

# ── Hospital vendors (25 vendors, 7 categories) ──
HOSPITAL_VENDORS = [
    # ═══ MEDICAL EQUIPMENT (5 vendors — GE dominant = concentration risk) ═══
    {
        "entity": "GE HEALTHCARE INDIA",
        "amount": 4200000,
        "category": "Medical Equipment",
        "currency": "INR",
        "monthly_amounts": [320000, 340000, 360000,
                           380000, 400000, 420000,
                           380000, 400000, 410000,
                           420000, 430000, 440000]
    },
    {
        "entity": "SIEMENS HEALTHINEERS",
        "amount": 2800000,
        "category": "Medical Equipment",
        "currency": "INR",
        "monthly_amounts": [220000, 225000, 230000,
                           235000, 240000, 245000,
                           240000, 238000, 242000,
                           245000, 248000, 252000]
    },
    {
        "entity": "PHILIPS INDIA",
        "amount": 1400000,
        "category": "Medical Equipment",
        "currency": "INR",
        "monthly_amounts": [110000, 112000, 115000,
                           118000, 120000, 122000,
                           118000, 115000, 118000,
                           120000, 122000, 110000]
    },
    {
        "entity": "MINDRAY MEDICAL INDIA",
        "amount": 960000,
        "category": "Medical Equipment",
        "currency": "INR",
        "monthly_amounts": [70000, 72000, 75000,
                           78000, 80000, 82000,
                           85000, 88000, 90000,
                           92000, 95000, 133000]
    },
    {
        "entity": "DRAGER INDIA",
        "amount": 720000,
        "category": "Medical Equipment",
        "currency": "INR",
        "monthly_amounts": [55000, 56000, 58000,
                           60000, 62000, 64000,
                           60000, 58000, 62000,
                           60000, 62000, 63000]
    },

    # ═══ PHARMA AND CONSUMABLES (5 vendors — Abbott+Cipla dominant) ═══
    {
        "entity": "ABBOTT INDIA",
        "amount": 3800000,
        "category": "Pharma and Consumables",
        "currency": "INR",
        "monthly_amounts": [280000, 290000, 300000,
                           310000, 320000, 340000,
                           360000, 350000, 330000,
                           340000, 350000, 380000]
    },
    {
        "entity": "CIPLA LIMITED",
        "amount": 2200000,
        "category": "Pharma and Consumables",
        "currency": "INR",
        "monthly_amounts": [160000, 165000, 170000,
                           175000, 182000, 188000,
                           192000, 196000, 198000,
                           200000, 205000, 169000]
    },
    {
        "entity": "SUN PHARMA",
        "amount": 1500000,
        "category": "Pharma and Consumables",
        "currency": "INR",
        "monthly_amounts": [110000, 115000, 120000,
                           125000, 128000, 130000,
                           132000, 130000, 128000,
                           130000, 132000, 140000]
    },
    {
        "entity": "DR REDDYS LABS",
        "amount": 980000,
        "category": "Pharma and Consumables",
        "currency": "INR",
        "monthly_amounts": [75000, 78000, 80000,
                           82000, 82000, 84000,
                           82000, 80000, 82000,
                           84000, 85000, 86000]
    },
    {
        "entity": "BIOCON LIMITED",
        "amount": 680000,
        "category": "Pharma and Consumables",
        "currency": "INR",
        "monthly_amounts": [50000, 52000, 55000,
                           56000, 58000, 58000,
                           60000, 58000, 56000,
                           58000, 60000, 109000]
    },

    # ═══ MEDICAL CONSUMABLES (4 vendors) ═══
    {
        "entity": "3M INDIA",
        "amount": 1800000,
        "category": "Medical Consumables",
        "currency": "INR",
        "monthly_amounts": [140000, 145000, 148000,
                           150000, 152000, 155000,
                           158000, 160000, 155000,
                           152000, 155000, 160000]
    },
    {
        "entity": "BECTON DICKINSON",
        "amount": 1600000,
        "category": "Medical Consumables",
        "currency": "INR",
        "monthly_amounts": [120000, 125000, 130000,
                           135000, 138000, 140000,
                           142000, 145000, 148000,
                           150000, 152000, 155000]
    },
    {
        "entity": "MEDTRONIC INDIA",
        "amount": 1200000,
        "category": "Medical Consumables",
        "currency": "INR",
        "monthly_amounts": [90000, 92000, 95000,
                           98000, 100000, 102000,
                           105000, 108000, 110000,
                           112000, 95000, 93000]
    },
    {
        "entity": "JOHNSON AND JOHNSON MED",
        "amount": 950000,
        "category": "Medical Consumables",
        "currency": "INR",
        "monthly_amounts": [72000, 74000, 76000,
                           78000, 80000, 82000,
                           80000, 78000, 82000,
                           84000, 86000, 78000]
    },

    # ═══ HOSPITAL IT SYSTEMS (3 vendors) ═══
    {
        "entity": "ORACLE HEALTH",
        "amount": 980000,
        "category": "Hospital IT Systems",
        "currency": "INR",
        "monthly_amounts": [80000, 80000, 82000,
                           82000, 82000, 82000,
                           82000, 82000, 82000,
                           84000, 84000, 84000]
    },
    {
        "entity": "EPIC SYSTEMS INDIA",
        "amount": 1100000,
        "category": "Hospital IT Systems",
        "currency": "INR",
        "monthly_amounts": [85000, 88000, 90000,
                           92000, 92000, 94000,
                           94000, 92000, 94000,
                           94000, 96000, 99000]
    },
    {
        "entity": "PRACTO TECHNOLOGIES",
        "amount": 420000,
        "category": "Hospital IT Systems",
        "currency": "INR",
        "monthly_amounts": [30000, 32000, 34000,
                           35000, 35000, 36000,
                           36000, 36000, 38000,
                           38000, 38000, 42000]
    },

    # ═══ FACILITY MANAGEMENT (3 vendors) ═══
    {
        "entity": "MEDIFIT FACILITY SERVICES",
        "amount": 1200000,
        "category": "Facility Management",
        "currency": "INR",
        "monthly_amounts": [95000, 98000, 100000,
                           100000, 102000, 102000,
                           100000, 100000, 102000,
                           102000, 100000, 99000]
    },
    {
        "entity": "BVG INDIA HOUSEKEEPING",
        "amount": 840000,
        "category": "Facility Management",
        "currency": "INR",
        "monthly_amounts": [65000, 66000, 68000,
                           70000, 70000, 72000,
                           72000, 72000, 72000,
                           72000, 70000, 71000]
    },
    {
        "entity": "SODEXO INDIA",
        "amount": 960000,
        "category": "Facility Management",
        "currency": "INR",
        "monthly_amounts": [75000, 76000, 78000,
                           80000, 80000, 82000,
                           82000, 82000, 82000,
                           82000, 80000, 81000]
    },

    # ═══ INSURANCE TPA (2 vendors) ═══
    {
        "entity": "STAR HEALTH TPA",
        "amount": 620000,
        "category": "Insurance TPA",
        "currency": "INR",
        "monthly_amounts": [50000, 50000, 52000,
                           52000, 52000, 54000,
                           54000, 54000, 52000,
                           52000, 54000, 54000]
    },
    {
        "entity": "MEDI ASSIST TPA",
        "amount": 480000,
        "category": "Insurance TPA",
        "currency": "INR",
        "monthly_amounts": [38000, 38000, 40000,
                           40000, 40000, 42000,
                           40000, 40000, 40000,
                           40000, 42000, 40000]
    },

    # ═══ LAB REAGENTS (3 vendors — rising spend trend) ═══
    {
        "entity": "ROCHE DIAGNOSTICS INDIA",
        "amount": 1350000,
        "category": "Lab Reagents",
        "currency": "INR",
        "monthly_amounts": [80000, 85000, 90000,
                           95000, 100000, 110000,
                           115000, 120000, 125000,
                           130000, 135000, 165000]
    },
    {
        "entity": "ABBOTT DIAGNOSTICS",
        "amount": 920000,
        "category": "Lab Reagents",
        "currency": "INR",
        "monthly_amounts": [60000, 62000, 65000,
                           68000, 72000, 78000,
                           80000, 84000, 88000,
                           92000, 96000, 175000]
    },
    {
        "entity": "SIEMENS DIAGNOSTICS",
        "amount": 780000,
        "category": "Lab Reagents",
        "currency": "INR",
        "monthly_amounts": [55000, 58000, 60000,
                           62000, 64000, 66000,
                           68000, 68000, 70000,
                           70000, 72000, 67000]
    },
]

# ── Item-level procurement data: same items from different vendors at different prices ──
# This enables CADE to detect "same medicine, different price" and recommend switching
HOSPITAL_PROCUREMENT_ITEMS = [
    # ═══ PHARMA — same medicines from Abbott vs Cipla vs Sun vs Dr Reddys ═══
    # Paracetamol 500mg — huge volume item
    {"item_name": "Paracetamol 500mg",      "item_code": "PARA-500",    "vendor": "ABBOTT INDIA",       "unit_price": 2.50,  "unit": "tablet",  "monthly_qty": 50000, "category": "Pharma and Consumables"},
    {"item_name": "Paracetamol 500mg",      "item_code": "PARA-500",    "vendor": "CIPLA LIMITED",      "unit_price": 1.80,  "unit": "tablet",  "monthly_qty": 30000, "category": "Pharma and Consumables"},
    {"item_name": "Paracetamol 500mg",      "item_code": "PARA-500",    "vendor": "SUN PHARMA",         "unit_price": 1.95,  "unit": "tablet",  "monthly_qty": 10000, "category": "Pharma and Consumables"},
    # Amoxicillin 500mg — antibiotic
    {"item_name": "Amoxicillin 500mg",      "item_code": "AMOX-500",    "vendor": "CIPLA LIMITED",      "unit_price": 4.20,  "unit": "capsule", "monthly_qty": 25000, "category": "Pharma and Consumables"},
    {"item_name": "Amoxicillin 500mg",      "item_code": "AMOX-500",    "vendor": "DR REDDYS LABS",     "unit_price": 3.50,  "unit": "capsule", "monthly_qty": 15000, "category": "Pharma and Consumables"},
    {"item_name": "Amoxicillin 500mg",      "item_code": "AMOX-500",    "vendor": "SUN PHARMA",         "unit_price": 3.80,  "unit": "capsule", "monthly_qty": 8000,  "category": "Pharma and Consumables"},
    # Metformin 500mg — diabetes
    {"item_name": "Metformin 500mg",        "item_code": "METF-500",    "vendor": "ABBOTT INDIA",       "unit_price": 3.80,  "unit": "tablet",  "monthly_qty": 20000, "category": "Pharma and Consumables"},
    {"item_name": "Metformin 500mg",        "item_code": "METF-500",    "vendor": "CIPLA LIMITED",      "unit_price": 2.10,  "unit": "tablet",  "monthly_qty": 12000, "category": "Pharma and Consumables"},
    # Atorvastatin 10mg — cholesterol
    {"item_name": "Atorvastatin 10mg",      "item_code": "ATOR-10",     "vendor": "SUN PHARMA",         "unit_price": 5.50,  "unit": "tablet",  "monthly_qty": 15000, "category": "Pharma and Consumables"},
    {"item_name": "Atorvastatin 10mg",      "item_code": "ATOR-10",     "vendor": "DR REDDYS LABS",     "unit_price": 4.20,  "unit": "tablet",  "monthly_qty": 8000,  "category": "Pharma and Consumables"},
    {"item_name": "Atorvastatin 10mg",      "item_code": "ATOR-10",     "vendor": "BIOCON LIMITED",     "unit_price": 4.80,  "unit": "tablet",  "monthly_qty": 5000,  "category": "Pharma and Consumables"},
    # Pantoprazole 40mg — gastro
    {"item_name": "Pantoprazole 40mg",      "item_code": "PANT-40",     "vendor": "ABBOTT INDIA",       "unit_price": 6.20,  "unit": "tablet",  "monthly_qty": 12000, "category": "Pharma and Consumables"},
    {"item_name": "Pantoprazole 40mg",      "item_code": "PANT-40",     "vendor": "CIPLA LIMITED",      "unit_price": 4.50,  "unit": "tablet",  "monthly_qty": 6000,  "category": "Pharma and Consumables"},
    # Ceftriaxone 1g injection — high value
    {"item_name": "Ceftriaxone 1g Inj",     "item_code": "CEFT-1G",     "vendor": "ABBOTT INDIA",       "unit_price": 85.00, "unit": "vial",    "monthly_qty": 3000,  "category": "Pharma and Consumables"},
    {"item_name": "Ceftriaxone 1g Inj",     "item_code": "CEFT-1G",     "vendor": "CIPLA LIMITED",      "unit_price": 62.00, "unit": "vial",    "monthly_qty": 2000,  "category": "Pharma and Consumables"},
    {"item_name": "Ceftriaxone 1g Inj",     "item_code": "CEFT-1G",     "vendor": "DR REDDYS LABS",     "unit_price": 58.00, "unit": "vial",    "monthly_qty": 1500,  "category": "Pharma and Consumables"},

    # ═══ MEDICAL CONSUMABLES — same items from 3M vs BD vs J&J ═══
    # Surgical gloves
    {"item_name": "Surgical Gloves (Sterile)", "item_code": "GLOVE-S",  "vendor": "3M INDIA",           "unit_price": 12.00, "unit": "pair",    "monthly_qty": 15000, "category": "Medical Consumables"},
    {"item_name": "Surgical Gloves (Sterile)", "item_code": "GLOVE-S",  "vendor": "BECTON DICKINSON",   "unit_price": 9.50,  "unit": "pair",    "monthly_qty": 10000, "category": "Medical Consumables"},
    {"item_name": "Surgical Gloves (Sterile)", "item_code": "GLOVE-S",  "vendor": "JOHNSON AND JOHNSON MED", "unit_price": 14.00, "unit": "pair", "monthly_qty": 5000,  "category": "Medical Consumables"},
    # IV Cannula
    {"item_name": "IV Cannula 20G",         "item_code": "IVC-20G",     "vendor": "BECTON DICKINSON",   "unit_price": 18.00, "unit": "piece",   "monthly_qty": 8000,  "category": "Medical Consumables"},
    {"item_name": "IV Cannula 20G",         "item_code": "IVC-20G",     "vendor": "MEDTRONIC INDIA",    "unit_price": 22.00, "unit": "piece",   "monthly_qty": 5000,  "category": "Medical Consumables"},
    # Surgical sutures
    {"item_name": "Vicryl Suture 3-0",      "item_code": "SUTR-30",     "vendor": "JOHNSON AND JOHNSON MED", "unit_price": 180.00, "unit": "piece", "monthly_qty": 2000, "category": "Medical Consumables"},
    {"item_name": "Vicryl Suture 3-0",      "item_code": "SUTR-30",     "vendor": "MEDTRONIC INDIA",    "unit_price": 145.00, "unit": "piece",  "monthly_qty": 1500,  "category": "Medical Consumables"},
    # Syringes
    {"item_name": "Disposable Syringe 5ml", "item_code": "SYR-5ML",     "vendor": "BECTON DICKINSON",   "unit_price": 4.50,  "unit": "piece",   "monthly_qty": 20000, "category": "Medical Consumables"},
    {"item_name": "Disposable Syringe 5ml", "item_code": "SYR-5ML",     "vendor": "3M INDIA",           "unit_price": 5.80,  "unit": "piece",   "monthly_qty": 12000, "category": "Medical Consumables"},

    # ═══ LAB REAGENTS — same test kits from Roche vs Abbott vs Siemens ═══
    # CBC reagent
    {"item_name": "CBC Reagent Kit",        "item_code": "CBC-KIT",     "vendor": "ROCHE DIAGNOSTICS INDIA", "unit_price": 45.00, "unit": "test", "monthly_qty": 8000,  "category": "Lab Reagents"},
    {"item_name": "CBC Reagent Kit",        "item_code": "CBC-KIT",     "vendor": "ABBOTT DIAGNOSTICS",      "unit_price": 38.00, "unit": "test", "monthly_qty": 5000,  "category": "Lab Reagents"},
    {"item_name": "CBC Reagent Kit",        "item_code": "CBC-KIT",     "vendor": "SIEMENS DIAGNOSTICS",     "unit_price": 42.00, "unit": "test", "monthly_qty": 3000,  "category": "Lab Reagents"},
    # HbA1c test
    {"item_name": "HbA1c Test Kit",         "item_code": "HBA1C",       "vendor": "ROCHE DIAGNOSTICS INDIA", "unit_price": 120.00, "unit": "test", "monthly_qty": 3000, "category": "Lab Reagents"},
    {"item_name": "HbA1c Test Kit",         "item_code": "HBA1C",       "vendor": "ABBOTT DIAGNOSTICS",      "unit_price": 95.00,  "unit": "test", "monthly_qty": 2000, "category": "Lab Reagents"},
    # Lipid Panel
    {"item_name": "Lipid Panel Reagent",    "item_code": "LIPID-P",     "vendor": "SIEMENS DIAGNOSTICS",     "unit_price": 65.00,  "unit": "test", "monthly_qty": 4000, "category": "Lab Reagents"},
    {"item_name": "Lipid Panel Reagent",    "item_code": "LIPID-P",     "vendor": "ROCHE DIAGNOSTICS INDIA", "unit_price": 78.00,  "unit": "test", "monthly_qty": 3000, "category": "Lab Reagents"},
]


# Number of monthly transactions to create per vendor (spreads the total evenly)
MONTHS = 12


def _build_demo_records() -> List[CanonicalFinancialRecord]:
    """
    Build hospital demo records using realistic per-month amounts.
    Creates 12 months of data going back from today.
    """
    records: List[CanonicalFinancialRecord] = []
    today = date.today()

    for vendor in HOSPITAL_VENDORS:
        monthly_amounts = vendor["monthly_amounts"]
        for month_offset in range(MONTHS):
            months_back = MONTHS - 1 - month_offset
            txn_date = today - timedelta(days=30 * months_back)
            records.append(
                CanonicalFinancialRecord(
                    date=txn_date,
                    amount=monthly_amounts[month_offset],
                    category=vendor["category"],
                    entity=vendor["entity"],
                    currency=vendor["currency"],
                    source_file="demo_hospital_data.csv",
                )
            )

    return records


@router.post("")
async def load_demo_data(
    payload: dict = Depends(verify_token),
):
    """
    Load hospital procurement demo data into the decision store.
    Wipes existing data first, then generates decisions through the real engine.
    """
    from app.services.decision_store import DecisionStore
    from app.services.decision_engine import DecisionEngine
    from app.services.item_price_engine import ItemPriceEngine

    # 1. Clear existing state
    DecisionStore.clear()

    # 2. Build hospital records
    records = _build_demo_records()

    # 3. Write transactions to data/transactions.json
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    output_data = [r.model_dump(mode="json") for r in records]
    with open(os.path.join(data_dir, "transactions.json"), "w") as f:
        json.dump(output_data, f, indent=2)

    # 4. Write item-level procurement data
    items_with_spend = []
    for item in HOSPITAL_PROCUREMENT_ITEMS:
        entry = dict(item)
        entry["monthly_spend"] = round(entry["unit_price"] * entry["monthly_qty"], 2)
        items_with_spend.append(entry)
    with open(os.path.join(data_dir, "procurement_items.json"), "w") as f:
        json.dump(items_with_spend, f, indent=2)
    item_mismatch_count = len(ItemPriceEngine.find_price_mismatches())

    # 5. Run the real DecisionEngine
    decisions = await DecisionEngine.analyze_uploaded_data()

    # 6. Return response
    return {
        "status": "loaded",
        "vertical": "hospital",
        "vendors": len(HOSPITAL_VENDORS),
        "decisions_generated": len(decisions),
        "months_of_data": MONTHS,
        "item_price_mismatches": item_mismatch_count,
    }


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

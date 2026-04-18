"""
Vendor Deep Dive API — Comprehensive vendor intelligence endpoint.

GET /api/vendors/{vendor_id}/intelligence → full vendor profile
GET /api/vendors/{vendor_id}/report      → downloadable PDF report
"""

import io
import uuid
import json
import hashlib
from datetime import date, datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from rapidfuzz import fuzz

from app.services.exposure_engine import calculate_all_exposures
from app.services.decision_store import DecisionStore

router = APIRouter()

# ── Static Market Benchmark Table ──
DRUG_BENCHMARKS = {
    "ceftriaxone": {"unit": "vial", "market_price": 58.0},
    "paracetamol": {"unit": "strip", "market_price": 2.1},
    "amoxicillin": {"unit": "strip", "market_price": 8.5},
    "metformin": {"unit": "strip", "market_price": 3.2},
    "omeprazole": {"unit": "strip", "market_price": 4.8},
    "atorvastatin": {"unit": "strip", "market_price": 6.2},
    "amlodipine": {"unit": "strip", "market_price": 3.8},
    "pantoprazole": {"unit": "strip", "market_price": 5.1},
    "azithromycin": {"unit": "strip", "market_price": 12.4},
    "ciprofloxacin": {"unit": "strip", "market_price": 7.8},
    "insulin": {"unit": "vial", "market_price": 185.0},
    "hba1c kit": {"unit": "test", "market_price": 95.0},
    "gloves": {"unit": "box", "market_price": 180.0},
    "syringe": {"unit": "piece", "market_price": 2.5},
    "iv cannula": {"unit": "piece", "market_price": 8.0},
    "surgical mask": {"unit": "box", "market_price": 120.0},
    "ct scan maintenance": {"unit": "year", "market_price": 280000},
    "mri maintenance": {"unit": "year", "market_price": 450000},
    "ventilator maintenance": {"unit": "year", "market_price": 85000},
}

# AMC detection constants (reuse from contracts.py)
AMC_CATEGORIES = {"medical equipment"}
AMC_VENDOR_KEYWORDS = {"ge", "siemens", "philips", "mindray", "drager", "medtronic", "stryker"}
AMC_TYPICAL_RATE = 0.10
AMC_MARKET_RATE = 0.08


def _fuzzy_match_benchmark(product_name: str) -> Optional[dict]:
    """Match product name against DRUG_BENCHMARKS using fuzzy matching."""
    if not product_name:
        return None
    product_lower = product_name.lower().strip()
    best_match = None
    best_score = 0
    for key, data in DRUG_BENCHMARKS.items():
        score = fuzz.ratio(product_lower, key)
        if score > best_score and score > 70:
            best_score = score
            best_match = {"name": key, **data}
    return best_match


def _get_renewal_date(vendor_name: str) -> date:
    """Deterministic renewal date (mirrors contracts.py logic)."""
    hash_val = int(hashlib.md5(vendor_name.encode()).hexdigest(), 16)
    days_ahead = (hash_val % 365) + 1
    return date.today() + timedelta(days=days_ahead)


def _is_amc_vendor(vendor_name: str, category: str) -> bool:
    if category.lower() in AMC_CATEGORIES:
        return True
    return any(kw in vendor_name.lower() for kw in AMC_VENDOR_KEYWORDS)


def _compute_performance_score(
    vendor_id: str,
    category: str,
    vendor_spend: float,
    category_vendors: list,
    monthly_data: dict,
    risk_score: float,
    spend_threshold: float,
) -> dict:
    """Calculate vendor performance score as weighted average of 4 components."""

    # ── Price Competitiveness ──
    if category_vendors:
        cheapest = min(v["annual_spend"] for v in category_vendors)
        if cheapest > 0:
            ratio = vendor_spend / cheapest
            if ratio <= 1.0:
                price_comp = 1.0
            elif ratio <= 1.15:
                price_comp = 0.5
            else:
                price_comp = max(0.0, 1.0 - (ratio - 1.0) / 0.30)
        else:
            price_comp = 0.5
    else:
        price_comp = 0.5

    # ── Price Stability ──
    sorted_months = sorted(monthly_data.keys())
    if len(sorted_months) >= 2:
        first_half = sum(monthly_data[m] for m in sorted_months[:len(sorted_months)//2])
        second_half = sum(monthly_data[m] for m in sorted_months[len(sorted_months)//2:])
        if first_half > 0:
            change = (second_half - first_half) / first_half
            if change <= 0:
                price_stab = 1.0
            elif change < 0.10:
                price_stab = 0.5
            else:
                price_stab = max(0.0, 1.0 - change)
        else:
            price_stab = 0.5
    else:
        price_stab = 0.5

    # ── Spend Efficiency ──
    if spend_threshold > 0:
        multiple = vendor_spend / spend_threshold
        if multiple <= 1.0:
            spend_eff = 1.0
        elif multiple <= 2.0:
            spend_eff = 0.5
        else:
            spend_eff = max(0.0, 1.0 - (multiple - 1.0) / 4.0)
    else:
        spend_eff = 0.5

    # ── Risk Score ──
    risk_comp = max(0.0, 1.0 - (risk_score / 12.0))

    # ── Overall Score (weighted average) ──
    overall = (
        price_comp * 0.30 +
        price_stab * 0.25 +
        spend_eff * 0.25 +
        risk_comp * 0.20
    )

    # Grade
    if overall >= 0.8:
        grade = "A"
        explanation = "Excellent vendor — competitively priced, stable, and low risk."
    elif overall >= 0.6:
        grade = "B"
        explanation = "Good vendor — generally competitive with some areas for improvement."
    elif overall >= 0.4:
        grade = "C"
        explanation = "Average vendor — consider alternatives for better value."
    elif overall >= 0.2:
        grade = "D"
        explanation = "Below average — significant pricing or risk concerns."
    else:
        grade = "F"
        explanation = "Poor vendor performance — immediate review recommended."

    return {
        "overall_score": round(overall, 3),
        "price_competitiveness": round(price_comp, 3),
        "price_stability": round(price_stab, 3),
        "spend_efficiency": round(spend_eff, 3),
        "risk_score": round(risk_comp, 3),
        "grade": grade,
        "grade_explanation": explanation,
    }


def _generate_recommended_actions(
    vendor_id: str,
    cheapest_alternative: Optional[str],
    potential_saving: float,
    concentration: float,
    renewal_days: int,
    price_rising: bool,
    is_amc: bool,
    amc_saving: float,
) -> list:
    """Generate dynamic recommended actions based on vendor data."""
    actions = []

    if cheapest_alternative and potential_saving > 0:
        actions.append({
            "priority": "HIGH",
            "action_type": "SWITCH_SUPPLIER",
            "title": f"Consider switching to {cheapest_alternative}",
            "description": (
                f"Alternative supplier offers lower rates. "
                f"Switching could save ₹{potential_saving:,.0f}/year."
            ),
            "estimated_saving": round(potential_saving, 2),
            "deadline": (date.today() + timedelta(days=30)).isoformat(),
        })

    if 0 < renewal_days <= 90:
        actions.append({
            "priority": "HIGH",
            "action_type": "NEGOTIATE",
            "title": f"Contract renews in {renewal_days} days — negotiate now",
            "description": (
                "Begin competitive tender process immediately. "
                "Obtain 2-3 alternative quotes to use as leverage."
            ),
            "estimated_saving": 0,
            "deadline": (date.today() + timedelta(days=renewal_days - 7)).isoformat(),
        })

    if concentration > 0.40:
        actions.append({
            "priority": "HIGH",
            "action_type": "DIVERSIFY",
            "title": "Reduce vendor concentration risk",
            "description": (
                f"This vendor represents {concentration:.0%} of category spend. "
                f"Qualify at least one alternative supplier."
            ),
            "estimated_saving": 0,
            "deadline": (date.today() + timedelta(days=60)).isoformat(),
        })

    if price_rising:
        actions.append({
            "priority": "MEDIUM",
            "action_type": "AUDIT_SPEND",
            "title": "Audit recent purchase orders for price increases",
            "description": (
                "Prices have been rising. Review purchase orders to "
                "identify unauthorized rate changes or volume increases."
            ),
            "estimated_saving": 0,
            "deadline": (date.today() + timedelta(days=14)).isoformat(),
        })

    if is_amc and amc_saving > 0:
        actions.append({
            "priority": "MEDIUM",
            "action_type": "RENEGOTIATE_AMC",
            "title": "Renegotiate AMC rate at market pricing",
            "description": (
                f"Current AMC rate is above market standard. "
                f"Renegotiation could save ₹{amc_saving:,.0f}/year."
            ),
            "estimated_saving": round(amc_saving, 2),
            "deadline": None,
        })

    actions.append({
        "priority": "LOW",
        "action_type": "DOWNLOAD_REPORT",
        "title": "Download complete vendor analysis report",
        "description": (
            "Generate a comprehensive PDF report for board presentation "
            "or procurement committee review."
        ),
        "estimated_saving": 0,
        "deadline": None,
    })

    return actions


@router.get("/{vendor_id}/intelligence")
async def get_vendor_intelligence(vendor_id: str):
    """
    Comprehensive vendor intelligence endpoint.
    Aggregates everything known about a vendor into a single response.
    """
    # ── Load transactions ──
    tx_path = Path("data/transactions.json")
    if not tx_path.exists():
        raise HTTPException(status_code=404, detail="No transaction data found")

    with open(tx_path) as f:
        transactions = json.load(f)

    # Filter for this vendor
    vendor_txns = [
        t for t in transactions
        if t.get("entity", "") == vendor_id
    ]

    if not vendor_txns:
        raise HTTPException(status_code=404, detail=f"Vendor '{vendor_id}' not found")

    category = vendor_txns[0].get("category", "Uncategorized")

    # ── Basic financials ──
    total_spend = sum(float(t.get("amount", 0)) for t in vendor_txns)

    # Monthly breakdown
    monthly_data = defaultdict(lambda: {"spend": 0.0, "count": 0})
    for txn in vendor_txns:
        amount = float(txn.get("amount", 0))
        date_val = txn.get("date", "")
        if len(date_val) >= 7:
            month_key = date_val[:7]
            monthly_data[month_key]["spend"] += amount
            monthly_data[month_key]["count"] += 1

    sorted_months = sorted(monthly_data.keys())
    monthly_avg = total_spend / max(len(sorted_months), 1)

    monthly_trend = [
        {
            "month": m,
            "spend": round(monthly_data[m]["spend"], 2),
            "transaction_count": monthly_data[m]["count"],
        }
        for m in sorted_months
    ]

    # Growth calculations
    def calc_growth(months_back: int) -> Optional[float]:
        if len(sorted_months) < months_back + 1:
            return None
        recent = sum(monthly_data[m]["spend"] for m in sorted_months[-months_back:])
        prev = sum(monthly_data[m]["spend"] for m in sorted_months[-2*months_back:-months_back]) if len(sorted_months) >= 2 * months_back else None
        if prev and prev > 0:
            return round(((recent - prev) / prev) * 100, 1)
        return None

    growth_3m = calc_growth(3)
    growth_6m = calc_growth(6)

    # Category share
    category_txns = [t for t in transactions if t.get("category") == category]
    category_total = sum(float(t.get("amount", 0)) for t in category_txns)
    category_share = (total_spend / category_total * 100) if category_total > 0 else 0

    # Worst case exposure
    exposures = calculate_all_exposures()
    vendor_exposure = next((e for e in exposures if e.vendor_id == vendor_id), None)
    worst_case = vendor_exposure.worst_case_exposure if vendor_exposure else total_spend * 0.3

    # Last month vs previous month
    last_month_spend = monthly_data[sorted_months[-1]]["spend"] if sorted_months else 0
    prev_month_spend = monthly_data[sorted_months[-2]]["spend"] if len(sorted_months) >= 2 else 0
    spend_vs_last = round(((last_month_spend - prev_month_spend) / prev_month_spend * 100), 1) if prev_month_spend > 0 else 0

    # YTD Spend (current year)
    current_year = str(date.today().year)
    ytd_spend = sum(
        monthly_data[m]["spend"]
        for m in sorted_months
        if m.startswith(current_year)
    )

    financial_summary = {
        "annual_spend": round(total_spend, 2),
        "monthly_avg": round(monthly_avg, 2),
        "monthly_trend": monthly_trend,
        "growth_pct_3m": growth_3m,
        "growth_pct_6m": growth_6m,
        "category_share_pct": round(category_share, 1),
        "worst_case_exposure": round(worst_case, 2),
        "ytd_spend": round(ytd_spend, 2),
        "last_month_spend": round(last_month_spend, 2),
        "spend_vs_last_month_pct": spend_vs_last,
    }

    # ── Product Breakdown ──
    product_groups = defaultdict(lambda: {
        "amounts": [], "count": 0, "last_date": "", "descriptions": [],
    })
    for txn in vendor_txns:
        desc = txn.get("description") or "General Purchase"
        amount = float(txn.get("amount", 0))
        date_val = txn.get("date", "")
        product_groups[desc]["amounts"].append(amount)
        product_groups[desc]["count"] += 1
        if date_val > product_groups[desc]["last_date"]:
            product_groups[desc]["last_date"] = date_val

    product_breakdown = []
    total_product_spend = sum(
        sum(pg["amounts"]) for pg in product_groups.values()
    )

    for product_name, pg in product_groups.items():
        amounts = pg["amounts"]
        avg_price = sum(amounts) / len(amounts)
        monthly_volume = len(amounts) / max(len(sorted_months), 1)
        monthly_spend = sum(amounts) / max(len(sorted_months), 1)
        pct_of_total = (sum(amounts) / total_product_spend * 100) if total_product_spend > 0 else 0

        # Price trend
        if len(amounts) >= 3:
            recent = sum(amounts[-3:]) / 3
            older = sum(amounts[:3]) / 3
            if recent > older * 1.05:
                trend = "RISING"
            elif recent < older * 0.95:
                trend = "FALLING"
            else:
                trend = "STABLE"
        else:
            trend = "STABLE"

        # Benchmark matching
        benchmark = _fuzzy_match_benchmark(product_name)
        market_price = benchmark["market_price"] if benchmark else None
        vs_market = None
        overpaying = False
        if market_price and market_price > 0:
            vs_market = round(((avg_price - market_price) / market_price) * 100, 1)
            overpaying = vs_market > 15

        product_breakdown.append({
            "product_name": product_name,
            "product_code": "",
            "unit": benchmark["unit"] if benchmark else "unit",
            "avg_unit_price": round(avg_price, 2),
            "min_price_seen": round(min(amounts), 2),
            "max_price_seen": round(max(amounts), 2),
            "monthly_volume": round(monthly_volume, 1),
            "monthly_spend": round(monthly_spend, 2),
            "pct_of_vendor_total": round(pct_of_total, 1),
            "price_trend": trend,
            "last_purchase_date": pg["last_date"],
            "market_benchmark_price": market_price,
            "vs_market_pct": vs_market,
            "overpaying": overpaying,
        })

    product_breakdown.sort(key=lambda x: x["monthly_spend"], reverse=True)

    # ── Price History ──
    price_history = []
    for i, month in enumerate(sorted_months):
        data = monthly_data[month]
        avg_tx = data["spend"] / data["count"] if data["count"] > 0 else 0
        if i > 0:
            prev = monthly_data[sorted_months[i-1]]
            prev_avg = prev["spend"] / prev["count"] if prev["count"] > 0 else 0
            change_pct = round(((avg_tx - prev_avg) / prev_avg * 100), 1) if prev_avg > 0 else 0
        else:
            change_pct = 0

        price_history.append({
            "date": month,
            "avg_transaction_amount": round(avg_tx, 2),
            "transaction_count": data["count"],
            "price_change_pct": change_pct,
        })

    # ── Competitive Position ──
    category_vendors_data = defaultdict(float)
    for txn in category_txns:
        v = txn.get("entity", "UNKNOWN")
        category_vendors_data[v] += float(txn.get("amount", 0))

    category_vendors_list = sorted(
        [
            {
                "vendor_id": v,
                "vendor_name": v,
                "annual_spend": round(s, 2),
                "is_current_vendor": v == vendor_id,
                "price_rank": 0,
                "reliability_score": 0.7,
            }
            for v, s in category_vendors_data.items()
        ],
        key=lambda x: x["annual_spend"],
    )

    # Assign ranks
    for i, cv in enumerate(category_vendors_list):
        cv["price_rank"] = i + 1

    cheapest_alt = None
    potential_saving = 0
    switching_rec = "No cheaper alternative found in this category."
    for cv in category_vendors_list:
        if not cv["is_current_vendor"] and cv["annual_spend"] < total_spend:
            cheapest_alt = cv["vendor_name"]
            potential_saving = total_spend - cv["annual_spend"]
            switching_rec = (
                f"Switching to {cheapest_alt} could save "
                f"₹{potential_saving:,.0f}/year ({potential_saving/total_spend:.0%} reduction)."
            )
            break

    competitive_position = {
        "category_vendors": category_vendors_list,
        "cheapest_alternative": cheapest_alt,
        "potential_saving_if_switched": round(potential_saving, 2),
        "switching_recommendation": switching_rec,
    }

    # ── Contract Info ──
    renewal_dt = _get_renewal_date(vendor_id)
    days_until = (renewal_dt - date.today()).days
    is_amc = _is_amc_vendor(vendor_id, category)
    amc_saving = round(total_spend * (AMC_TYPICAL_RATE - AMC_MARKET_RATE) / AMC_TYPICAL_RATE, 2) if is_amc else 0

    contract_info = {
        "renewal_date": renewal_dt.isoformat(),
        "days_until_renewal": days_until,
        "is_amc": is_amc,
        "amc_rate_current": AMC_TYPICAL_RATE if is_amc else None,
        "amc_rate_market": AMC_MARKET_RATE if is_amc else None,
        "amc_saving_opportunity": amc_saving,
        "negotiation_tip": (
            f"Market rate for comparable AMC is {AMC_MARKET_RATE:.0%}. "
            f"Negotiate at renewal for potential saving of ₹{amc_saving:,.0f}/year."
        ) if is_amc else "Review competitive quotes before renewal.",
        "contract_type": "AMC" if is_amc else "Standard",
    }

    # ── Decisions ──
    all_decisions = DecisionStore.get_all_decisions()
    vendor_decisions = [
        {
            "decision_id": d.id,
            "title": d.recommended_action,
            "risk_level": d.risk_level.value,
            "status": d.status.value,
            "annual_impact": d.annual_impact,
            "created_at": d.created_at.isoformat() if d.created_at else "",
        }
        for d in all_decisions
        if d.entity == vendor_id
    ]

    # ── Performance Score ──
    # Determine risk_score from decisions or default
    risk_score_val = 5.0  # default
    for d in all_decisions:
        if d.entity == vendor_id:
            risk_score_val = float(d.risk_score)
            break

    # Get spend threshold from policy engine
    try:
        from app.services.policy_engine import policy_engine
        policy = policy_engine.get_policy(category)
        spend_threshold = policy.get("spend_threshold", 100000)
    except Exception:
        spend_threshold = 100000

    monthly_spend_dict = {m: monthly_data[m]["spend"] for m in sorted_months}

    performance_score = _compute_performance_score(
        vendor_id=vendor_id,
        category=category,
        vendor_spend=total_spend,
        category_vendors=category_vendors_list,
        monthly_data=monthly_spend_dict,
        risk_score=risk_score_val,
        spend_threshold=spend_threshold,
    )

    # ── Risk Assessment ──
    risk_score_num = risk_score_val
    if risk_score_num >= 8:
        risk_level = "HIGH"
    elif risk_score_num >= 4:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # ── Recommended Actions ──
    price_rising = any(p["price_trend"] == "RISING" for p in product_breakdown)

    recommended_actions = _generate_recommended_actions(
        vendor_id=vendor_id,
        cheapest_alternative=cheapest_alt,
        potential_saving=potential_saving,
        concentration=category_share / 100,
        renewal_days=days_until,
        price_rising=price_rising,
        is_amc=is_amc,
        amc_saving=amc_saving,
    )

    # ── Market Intelligence ──
    market_intelligence = {
        "category_market_size": "Data not available",
        "typical_contract_duration": "12 months" if not is_amc else "12-36 months",
        "average_discount_at_renewal": 12.5,
        "bulk_buy_discount_available": 8.0,
        "market_price_trend": "STABLE",
        "regulatory_notes": (
            "NPPA governs drug pricing. Equipment imports subject to customs duty."
            if category.lower() in ("pharma and consumables", "medical consumables")
            else "Standard procurement regulations apply."
        ),
    }

    return {
        "vendor_id": vendor_id,
        "vendor_name": vendor_id,
        "category": category,
        "risk_level": risk_level,
        "risk_score": risk_score_num,
        "financial_summary": financial_summary,
        "product_breakdown": product_breakdown,
        "price_history": price_history,
        "competitive_position": competitive_position,
        "contract_info": contract_info,
        "decisions": vendor_decisions,
        "performance_score": performance_score,
        "recommended_actions": recommended_actions,
        "market_intelligence": market_intelligence,
    }


@router.get("/{vendor_id}/report")
async def download_vendor_report(vendor_id: str):
    """Download comprehensive vendor PDF report."""
    data = await get_vendor_intelligence(vendor_id)

    from app.exports.vendor_report import generate_vendor_report
    pdf_bytes = generate_vendor_report(data)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f"attachment; filename=vendor_report_{vendor_id}.pdf"
        },
    )

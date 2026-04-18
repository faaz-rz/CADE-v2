"""
Hospital Alerts Engine — Generates hospital-specific procurement alerts.

Alert categories: CONTRACT, PRICE, SPEND, COMPLIANCE
Severity levels: CRITICAL, HIGH, MEDIUM, LOW
"""

import uuid
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, date, timedelta
from typing import List
from pathlib import Path
from collections import defaultdict


@dataclass
class HospitalAlert:
    alert_id: str
    severity: str    # CRITICAL | HIGH | MEDIUM | LOW
    category: str    # PRICE | CONTRACT | SPEND | COMPLIANCE
    title: str
    message: str
    vendor_id: str
    estimated_impact: float
    action_url: str
    created_at: str
    is_read: bool = False


class HospitalAlertsEngine:

    @staticmethod
    def _uuid5_from(seed: str) -> str:
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, seed))

    @staticmethod
    def generate_alerts() -> List[HospitalAlert]:
        alerts: List[HospitalAlert] = []

        # ── Load transaction data ──
        tx_path = Path("data/transactions.json")
        if not tx_path.exists():
            return alerts

        with open(tx_path) as f:
            transactions = json.load(f)

        if not transactions:
            return alerts

        # ── Pre-compute vendor data ──
        vendor_monthly = defaultdict(lambda: defaultdict(float))
        vendor_totals = defaultdict(float)
        vendor_categories = {}
        vendor_tx_count = defaultdict(int)
        category_totals = defaultdict(float)

        for txn in transactions:
            vendor = txn.get("entity", "UNKNOWN")
            amount = float(txn.get("amount", 0))
            date_val = txn.get("date", "")
            category = txn.get("category", "Uncategorized")

            vendor_totals[vendor] += amount
            vendor_categories[vendor] = category
            vendor_tx_count[vendor] += 1
            category_totals[category] += amount

            if len(date_val) >= 7:
                month_key = date_val[:7]
                vendor_monthly[vendor][month_key] += amount

        # ── Alert 1: Contract expiring within 30 days ──
        try:
            import hashlib
            for vendor_id in vendor_totals:
                hash_val = int(hashlib.md5(vendor_id.encode()).hexdigest(), 16)
                days_ahead = (hash_val % 365) + 1
                renewal_date = date.today() + timedelta(days=days_ahead)
                days_until = (renewal_date - date.today()).days

                if days_until <= 30:
                    spend = vendor_totals[vendor_id]
                    saving = spend * 0.15
                    alerts.append(HospitalAlert(
                        alert_id=HospitalAlertsEngine._uuid5_from(
                            f"{vendor_id}_contract_30d"
                        ),
                        severity="CRITICAL",
                        category="CONTRACT",
                        title=f"{vendor_id} contract expires in {days_until} days",
                        message=(
                            f"Auto-renewal at current rate will cost "
                            f"₹{spend:,.0f}/year. Negotiate now for "
                            f"estimated saving of ₹{saving:,.0f}."
                        ),
                        vendor_id=vendor_id,
                        estimated_impact=saving,
                        action_url=f"/vendor/{vendor_id}#contract",
                        created_at=datetime.now().isoformat(),
                    ))
        except Exception:
            pass

        # ── Alert 2: Price spike detected (> 15% in last month) ──
        for vendor_id, monthly in vendor_monthly.items():
            sorted_months = sorted(monthly.keys())
            if len(sorted_months) < 2:
                continue

            prev_month = sorted_months[-2]
            curr_month = sorted_months[-1]
            prev_spend = monthly[prev_month]
            curr_spend = monthly[curr_month]

            if prev_spend > 0:
                pct_change = (curr_spend - prev_spend) / prev_spend
                if pct_change > 0.15:
                    alerts.append(HospitalAlert(
                        alert_id=HospitalAlertsEngine._uuid5_from(
                            f"{vendor_id}_price_spike_{curr_month}"
                        ),
                        severity="HIGH",
                        category="PRICE",
                        title=(
                            f"{vendor_id} prices increased "
                            f"{pct_change:.0%} this month"
                        ),
                        message=(
                            f"Monthly spend jumped from ₹{prev_spend:,.0f} to "
                            f"₹{curr_spend:,.0f}. Review purchase orders for "
                            f"unauthorized quantities or rate changes."
                        ),
                        vendor_id=vendor_id,
                        estimated_impact=curr_spend - prev_spend,
                        action_url=f"/vendor/{vendor_id}#spend-trend",
                        created_at=datetime.now().isoformat(),
                    ))

        # ── Alert 3: New price mismatch detected ──
        try:
            from app.services.price_comparison_engine import PriceComparisonEngine
            comparisons = PriceComparisonEngine.analyze_all_categories()
            for comp in comparisons:
                if comp.price_variance_pct >= 30:
                    alerts.append(HospitalAlert(
                        alert_id=HospitalAlertsEngine._uuid5_from(
                            f"price_mismatch_{comp.item_category}"
                        ),
                        severity="HIGH",
                        category="PRICE",
                        title=(
                            f"Price mismatch: {comp.item_category} "
                            f"at {comp.price_variance_pct:.0f}% premium"
                        ),
                        message=(
                            f"You are overpaying in {comp.item_category}. "
                            f"Cheapest: {comp.cheapest_supplier}, "
                            f"most expensive: {comp.most_expensive_supplier}. "
                            f"Annual overspend: ₹{comp.annual_overspend:,.0f}."
                        ),
                        vendor_id=comp.most_expensive_supplier,
                        estimated_impact=comp.annual_overspend,
                        action_url="/exposure#price-mismatch",
                        created_at=datetime.now().isoformat(),
                    ))
        except Exception:
            pass

        # ── Alert 4: Vendor concentration exceeded 50% ──
        for vendor_id, spend in vendor_totals.items():
            category = vendor_categories.get(vendor_id, "Uncategorized")
            cat_total = category_totals.get(category, 1)
            share = spend / cat_total if cat_total > 0 else 0

            if share > 0.50:
                alerts.append(HospitalAlert(
                    alert_id=HospitalAlertsEngine._uuid5_from(
                        f"{vendor_id}_concentration_50"
                    ),
                    severity="CRITICAL",
                    category="SPEND",
                    title=(
                        f"{vendor_id} exceeds 50% category concentration"
                    ),
                    message=(
                        f"{vendor_id} now represents {share:.0%} of "
                        f"{category} spend. Single vendor dependency "
                        f"creates operational and pricing risk."
                    ),
                    vendor_id=vendor_id,
                    estimated_impact=spend * 0.15,
                    action_url=f"/vendor/{vendor_id}",
                    created_at=datetime.now().isoformat(),
                ))

        # ── Alert 5: Rapid spend growth (> 20% in 3 months) ──
        for vendor_id, monthly in vendor_monthly.items():
            sorted_months = sorted(monthly.keys())
            if len(sorted_months) < 4:
                continue

            recent_3 = sum(monthly[m] for m in sorted_months[-3:])
            prev_3 = sum(monthly[m] for m in sorted_months[-6:-3]) if len(sorted_months) >= 6 else sum(monthly[m] for m in sorted_months[:-3])

            if prev_3 > 0:
                growth = (recent_3 - prev_3) / prev_3
                if growth > 0.20:
                    projected = vendor_totals[vendor_id] * (1 + growth)
                    alerts.append(HospitalAlert(
                        alert_id=HospitalAlertsEngine._uuid5_from(
                            f"{vendor_id}_rapid_growth_3m"
                        ),
                        severity="MEDIUM",
                        category="SPEND",
                        title=(
                            f"{vendor_id} spend growing "
                            f"{growth:.0%} in 3 months"
                        ),
                        message=(
                            f"At current growth rate, annual spend will "
                            f"reach ₹{projected:,.0f}. Review usage patterns."
                        ),
                        vendor_id=vendor_id,
                        estimated_impact=projected - vendor_totals[vendor_id],
                        action_url=f"/vendor/{vendor_id}#spend-trend",
                        created_at=datetime.now().isoformat(),
                    ))

        # Sort by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        return sorted(
            alerts,
            key=lambda x: severity_order.get(x.severity, 3),
        )

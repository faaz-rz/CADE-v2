"""
Bulk Buy Intelligence Engine — Analyzes purchase patterns to recommend
bulk purchasing when prices are trending upward.

Factors in storage costs to calculate net savings from forward buying.
"""

from dataclasses import dataclass
from typing import List
import json
from pathlib import Path
from collections import defaultdict


@dataclass
class BulkBuyRecommendation:
    vendor_id: str
    product_name: str
    category: str
    current_unit_price: float
    price_trend_3m: float
    recommended_order_months: int
    current_monthly_spend: float
    bulk_order_amount: float
    estimated_price_saving: float
    storage_cost_estimate: float
    net_saving: float
    confidence: float
    reasoning: str
    urgency: str  # "BUY NOW" | "CONSIDER" | "MONITOR"


class BulkBuyEngine:

    STORAGE_COST_RATE = 0.02  # 2% of order value per month for storage

    @staticmethod
    def analyze(transactions_path: str = "data/transactions.json") -> List[BulkBuyRecommendation]:
        path = Path(transactions_path)
        if not path.exists():
            return []

        with open(path) as f:
            transactions = json.load(f)

        # Group transactions by vendor, then by month
        vendor_monthly = defaultdict(lambda: defaultdict(list))
        vendor_categories = {}

        for txn in transactions:
            vendor = txn.get("entity", "UNKNOWN")
            amount = float(txn.get("amount", 0))
            date_val = txn.get("date", "")
            category = txn.get("category", "Uncategorized")

            if not date_val or amount <= 0:
                continue

            # Extract month key (YYYY-MM)
            month_key = date_val[:7] if len(date_val) >= 7 else date_val
            vendor_monthly[vendor][month_key].append(amount)
            vendor_categories[vendor] = category

        recommendations = []

        for vendor, monthly_data in vendor_monthly.items():
            if len(monthly_data) < 3:
                continue  # Need at least 3 months of data

            # Sort months chronologically
            sorted_months = sorted(monthly_data.keys())

            # Calculate monthly average amounts (proxy for unit price trend)
            monthly_avgs = []
            monthly_volumes = []
            for month in sorted_months:
                amounts = monthly_data[month]
                monthly_avgs.append(sum(amounts) / len(amounts))
                monthly_volumes.append(len(amounts))

            # Calculate price trend from last 3 months
            if len(monthly_avgs) >= 3:
                recent_3 = monthly_avgs[-3:]
                if recent_3[0] > 0:
                    price_change_3m = (recent_3[-1] - recent_3[0]) / recent_3[0]
                else:
                    price_change_3m = 0.0
            else:
                price_change_3m = 0.0

            # Only recommend if prices are rising
            if price_change_3m <= 0.02:  # < 2% increase — not worth it
                continue

            current_price = monthly_avgs[-1]
            avg_monthly_volume = sum(monthly_volumes) / len(monthly_volumes)
            current_monthly_spend = current_price * avg_monthly_volume

            # Calculate monthly price increase rate
            monthly_increase_rate = price_change_3m / 3.0

            # Determine recommended forward-buy months
            if monthly_increase_rate > 0.08:
                recommended_months = 3
            elif monthly_increase_rate > 0.03:
                recommended_months = 2
            else:
                recommended_months = 1

            # Calculate savings from buying now vs buying later
            total_forward_volume = avg_monthly_volume * recommended_months
            future_prices = [
                current_price * (1 + monthly_increase_rate) ** (m + 1)
                for m in range(recommended_months)
            ]
            cost_if_bought_later = sum(
                fp * avg_monthly_volume for fp in future_prices
            )
            cost_if_bought_now = current_price * total_forward_volume
            price_saving = cost_if_bought_later - cost_if_bought_now

            # Storage cost
            storage_cost = 0.0
            for m in range(recommended_months):
                # Each month's stock held for (recommended_months - m) months
                months_stored = recommended_months - m
                storage_cost += (
                    current_price * avg_monthly_volume
                    * BulkBuyEngine.STORAGE_COST_RATE * months_stored
                )

            net_saving = price_saving - storage_cost

            if net_saving <= 0:
                continue  # Not worth it after storage costs

            bulk_order_amount = cost_if_bought_now

            # Calculate net saving percentage
            if cost_if_bought_later > 0:
                net_saving_pct = net_saving / cost_if_bought_later
            else:
                net_saving_pct = 0.0

            # Urgency rules
            if monthly_increase_rate > 0.08 and net_saving_pct > 0.10:
                urgency = "BUY NOW"
                confidence = 0.85
            elif monthly_increase_rate > 0.03 and net_saving_pct > 0.05:
                urgency = "CONSIDER"
                confidence = 0.70
            else:
                urgency = "MONITOR"
                confidence = 0.55

            # Generate reasoning
            reasoning = (
                f"Prices from {vendor} have increased {price_change_3m:.0%} over "
                f"the past 3 months ({monthly_increase_rate:.1%}/month). "
                f"Buying {recommended_months} months' supply now at current rates "
                f"saves ₹{price_saving:,.0f} vs projected prices. "
                f"After storage costs of ₹{storage_cost:,.0f}, "
                f"net saving is ₹{net_saving:,.0f} ({net_saving_pct:.0%})."
            )

            category = vendor_categories.get(vendor, "Uncategorized")
            description = transactions[0].get("description", vendor)

            recommendations.append(BulkBuyRecommendation(
                vendor_id=vendor,
                product_name=description if description else vendor,
                category=category,
                current_unit_price=round(current_price, 2),
                price_trend_3m=round(price_change_3m * 100, 1),
                recommended_order_months=recommended_months,
                current_monthly_spend=round(current_monthly_spend, 2),
                bulk_order_amount=round(bulk_order_amount, 2),
                estimated_price_saving=round(price_saving, 2),
                storage_cost_estimate=round(storage_cost, 2),
                net_saving=round(net_saving, 2),
                confidence=confidence,
                reasoning=reasoning,
                urgency=urgency,
            ))

        return sorted(
            recommendations,
            key=lambda x: x.net_saving,
            reverse=True,
        )

"""
Price Comparison Engine — Cross-supplier price intelligence for hospital procurement.

Analyzes transaction data to identify which suppliers offer the best value
for the same procurement category, and calculates overspend from sub-optimal sourcing.
"""

from dataclasses import dataclass
from typing import Optional
import json
from pathlib import Path


@dataclass
class SupplierPrice:
    supplier_name: str
    unit_price: float
    last_purchase_date: str
    total_purchased: float
    purchase_count: int
    price_trend: str  # "RISING" | "STABLE" | "FALLING"
    reliability_score: float  # 0-1 based on purchase frequency


@dataclass
class PriceComparisonResult:
    item_category: str
    suppliers: list[SupplierPrice]
    cheapest_supplier: str
    most_expensive_supplier: str
    price_variance_pct: float
    annual_overspend: float
    recommended_primary_supplier: str
    recommended_backup_supplier: Optional[str]
    estimated_annual_savings: float
    bulk_buy_recommended: bool
    bulk_buy_reasoning: str
    consolidation_recommended: bool


class PriceComparisonEngine:

    @staticmethod
    def analyze_category_suppliers(
        category: str,
        transactions_path: str = "data/transactions.json"
    ) -> Optional[PriceComparisonResult]:

        path = Path(transactions_path)
        if not path.exists():
            return None

        with open(path) as f:
            transactions = json.load(f)

        # Filter transactions for this category
        category_txns = [
            t for t in transactions
            if t.get("category", "").lower() == category.lower()
        ]

        if not category_txns:
            return None

        # Group by entity (supplier)
        supplier_data = {}
        for txn in category_txns:
            supplier = txn.get("entity", "UNKNOWN")
            amount = float(txn.get("amount", 0))
            date_val = txn.get("date", "")

            if supplier not in supplier_data:
                supplier_data[supplier] = {
                    "amounts": [],
                    "dates": [],
                    "total": 0,
                    "count": 0
                }

            supplier_data[supplier]["amounts"].append(amount)
            supplier_data[supplier]["dates"].append(date_val)
            supplier_data[supplier]["total"] += amount
            supplier_data[supplier]["count"] += 1

        if len(supplier_data) < 2:
            return None  # Need at least 2 suppliers to compare

        # Build SupplierPrice objects
        suppliers = []
        for name, data in supplier_data.items():
            amounts = sorted(data["amounts"])
            avg_amount = sum(amounts) / len(amounts)

            # Detect price trend
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

            reliability = min(1.0, data["count"] / 12)

            suppliers.append(SupplierPrice(
                supplier_name=name,
                unit_price=avg_amount,
                last_purchase_date=max(data["dates"]) if data["dates"] else "",
                total_purchased=data["total"],
                purchase_count=data["count"],
                price_trend=trend,
                reliability_score=reliability
            ))

        # Find cheapest and most expensive
        suppliers_by_price = sorted(
            suppliers, key=lambda x: x.unit_price
        )
        cheapest = suppliers_by_price[0]
        most_expensive = suppliers_by_price[-1]

        # Calculate price variance
        if cheapest.unit_price > 0:
            price_variance = (
                (most_expensive.unit_price - cheapest.unit_price)
                / cheapest.unit_price
            )
        else:
            price_variance = 0.0

        # Calculate annual overspend
        # (what they are paying vs what they could pay
        # if all purchases were from cheapest supplier)
        total_spend = sum(s.total_purchased for s in suppliers)
        total_purchases = sum(s.purchase_count for s in suppliers)
        if total_purchases > 0:
            avg_price_paid = total_spend / total_purchases
            if avg_price_paid > 0:
                optimal_spend = total_spend * (
                    cheapest.unit_price / avg_price_paid
                )
            else:
                optimal_spend = total_spend
        else:
            optimal_spend = total_spend
        annual_overspend = max(0, total_spend - optimal_spend)

        # Determine recommended primary supplier
        # Balance: price (60%) + reliability (40%)
        def score_supplier(s):
            max_price = max(x.unit_price for x in suppliers)
            if max_price > 0:
                price_score = 1 - (s.unit_price / max_price)
            else:
                price_score = 0
            return (price_score * 0.6) + (s.reliability_score * 0.4)

        scored = sorted(
            suppliers,
            key=score_supplier,
            reverse=True
        )
        recommended_primary = scored[0].supplier_name
        recommended_backup = (
            scored[1].supplier_name
            if len(scored) > 1 else None
        )

        estimated_savings = annual_overspend * 0.7

        # Bulk buy recommendation
        rising_suppliers = [
            s for s in suppliers if s.price_trend == "RISING"
        ]
        bulk_buy_recommended = len(rising_suppliers) > 0
        bulk_buy_reasoning = (
            f"Price trend is rising for {len(rising_suppliers)} "
            f"supplier(s). Locking in current prices through "
            f"bulk purchase could save 8-12% vs projected prices."
            if bulk_buy_recommended
            else "Prices are stable. No immediate bulk buy advantage."
        )

        return PriceComparisonResult(
            item_category=category,
            suppliers=suppliers,
            cheapest_supplier=cheapest.supplier_name,
            most_expensive_supplier=most_expensive.supplier_name,
            price_variance_pct=round(price_variance * 100, 1),
            annual_overspend=round(annual_overspend, 2),
            recommended_primary_supplier=recommended_primary,
            recommended_backup_supplier=recommended_backup,
            estimated_annual_savings=round(estimated_savings, 2),
            bulk_buy_recommended=bulk_buy_recommended,
            bulk_buy_reasoning=bulk_buy_reasoning,
            consolidation_recommended=len(suppliers) >= 3
        )

    @staticmethod
    def analyze_all_categories(
        transactions_path: str = "data/transactions.json"
    ) -> list[PriceComparisonResult]:

        path = Path(transactions_path)
        if not path.exists():
            return []

        with open(path) as f:
            transactions = json.load(f)

        categories = list(set(
            t.get("category", "") for t in transactions
            if t.get("category")
        ))

        results = []
        for category in categories:
            result = PriceComparisonEngine.analyze_category_suppliers(
                category, transactions_path
            )
            if result:
                results.append(result)

        return sorted(
            results,
            key=lambda x: x.annual_overspend,
            reverse=True
        )

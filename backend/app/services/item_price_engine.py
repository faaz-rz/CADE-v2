"""
Item-Level Price Intelligence — Detects same items sold by multiple 
suppliers at different prices and generates switching recommendations.

This is SEPARATE from the CanonicalFinancialRecord model.
It uses a parallel item-level dataset (data/procurement_items.json)
that captures what each vendor actually sells at what unit price.
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ItemPriceEntry:
    """One supplier's price for one specific item."""
    item_name: str
    item_code: str           # e.g., "PARA-500" — normalized key
    vendor: str
    unit_price: float        # per unit in INR
    unit: str                # "tablet", "vial", "box", "test", "strip"
    monthly_qty: int         # how many units/month
    category: str
    monthly_spend: float     # unit_price * monthly_qty


@dataclass
class ItemPriceMismatch:
    """Two+ suppliers sell the same item at different prices."""
    item_name: str
    item_code: str
    category: str
    unit: str
    cheapest_vendor: str
    cheapest_price: float
    expensive_vendor: str
    expensive_price: float
    price_diff_pct: float
    monthly_qty_at_expensive: int
    monthly_savings: float
    annual_savings: float
    recommendation: str


class ItemPriceEngine:
    """Analyze item-level procurement data for same-item price mismatches."""

    ITEMS_PATH = "data/procurement_items.json"

    @classmethod
    def _load_items(cls) -> list[dict]:
        path = Path(cls.ITEMS_PATH)
        if not path.exists():
            return []
        with open(path) as f:
            return json.load(f)

    @classmethod
    def find_price_mismatches(cls, min_diff_pct: float = 5.0) -> list[ItemPriceMismatch]:
        """
        Find items where 2+ vendors supply the same item at different prices.
        Only surfaces mismatches above min_diff_pct threshold.
        """
        items = cls._load_items()
        if not items:
            return []

        # Group by item_code
        by_item: dict[str, list[dict]] = {}
        for entry in items:
            code = entry.get("item_code", "").upper()
            if code not in by_item:
                by_item[code] = []
            by_item[code].append(entry)

        mismatches = []
        for code, entries in by_item.items():
            if len(entries) < 2:
                continue

            # Sort by unit price
            sorted_entries = sorted(entries, key=lambda x: x["unit_price"])
            cheapest = sorted_entries[0]
            most_expensive = sorted_entries[-1]

            price_diff_pct = (
                (most_expensive["unit_price"] - cheapest["unit_price"])
                / cheapest["unit_price"]
            ) * 100

            if price_diff_pct < min_diff_pct:
                continue

            # Calculate savings if we switch expensive vendor's qty to cheapest
            monthly_qty = most_expensive["monthly_qty"]
            monthly_savings = (
                most_expensive["unit_price"] - cheapest["unit_price"]
            ) * monthly_qty
            annual_savings = monthly_savings * 12

            recommendation = (
                f"Switch {most_expensive['item_name']} procurement from "
                f"{most_expensive['vendor']} (₹{most_expensive['unit_price']:.2f}/{most_expensive['unit']}) "
                f"to {cheapest['vendor']} (₹{cheapest['unit_price']:.2f}/{cheapest['unit']}). "
                f"Price difference: {price_diff_pct:.0f}%. "
                f"Estimated annual savings: ₹{annual_savings:,.0f}."
            )

            mismatches.append(ItemPriceMismatch(
                item_name=most_expensive["item_name"],
                item_code=code,
                category=most_expensive.get("category", ""),
                unit=most_expensive["unit"],
                cheapest_vendor=cheapest["vendor"],
                cheapest_price=cheapest["unit_price"],
                expensive_vendor=most_expensive["vendor"],
                expensive_price=most_expensive["unit_price"],
                price_diff_pct=round(price_diff_pct, 1),
                monthly_qty_at_expensive=monthly_qty,
                monthly_savings=round(monthly_savings, 2),
                annual_savings=round(annual_savings, 2),
                recommendation=recommendation,
            ))

        # Sort by annual savings descending
        return sorted(mismatches, key=lambda x: x.annual_savings, reverse=True)

    @classmethod
    def get_summary(cls) -> dict:
        """Return summary of all item-level price intelligence."""
        mismatches = cls.find_price_mismatches()
        total_annual = sum(m.annual_savings for m in mismatches)

        return {
            "total_mismatches": len(mismatches),
            "total_annual_savings": round(total_annual, 2),
            "mismatches": [asdict(m) for m in mismatches],
        }

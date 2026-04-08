"""
Procurement Intelligence API — Supplier price comparison, bulk buy alerts.

GET /api/procurement/price-comparison         → all categories
GET /api/procurement/price-comparison/{cat}    → single category
GET /api/procurement/bulk-buy-alerts           → bulk buy opportunities
"""

from fastapi import APIRouter, HTTPException
from app.services.price_comparison_engine import PriceComparisonEngine
from app.services.item_price_engine import ItemPriceEngine

router = APIRouter()


@router.get("/price-comparison")
async def get_price_comparison():
    """Compare supplier pricing across all categories with 2+ suppliers."""
    results = PriceComparisonEngine.analyze_all_categories()

    total_overspend = sum(r.annual_overspend for r in results)
    total_savings = sum(r.estimated_annual_savings for r in results)
    categories_with_multiple = len([
        r for r in results if len(r.suppliers) >= 2
    ])

    return {
        "categories_analyzed": len(results),
        "categories_with_multiple_suppliers": categories_with_multiple,
        "total_annual_overspend": round(total_overspend, 2),
        "total_estimated_savings": round(total_savings, 2),
        "comparisons": [
            {
                "category": r.item_category,
                "supplier_count": len(r.suppliers),
                "suppliers": [
                    {
                        "name": s.supplier_name,
                        "avg_purchase_amount": round(s.unit_price, 2),
                        "total_purchased": round(s.total_purchased, 2),
                        "purchase_count": s.purchase_count,
                        "price_trend": s.price_trend,
                        "reliability_score": round(
                            s.reliability_score, 2
                        ),
                    }
                    for s in sorted(
                        r.suppliers,
                        key=lambda x: x.unit_price
                    )
                ],
                "cheapest_supplier": r.cheapest_supplier,
                "price_variance_pct": r.price_variance_pct,
                "annual_overspend": r.annual_overspend,
                "recommended_primary": r.recommended_primary_supplier,
                "recommended_backup": r.recommended_backup_supplier,
                "estimated_savings": r.estimated_annual_savings,
                "bulk_buy_recommended": r.bulk_buy_recommended,
                "bulk_buy_reasoning": r.bulk_buy_reasoning,
                "consolidation_recommended": r.consolidation_recommended,
            }
            for r in results
        ]
    }


@router.get("/price-comparison/{category}")
async def get_category_price_comparison(category: str):
    """Compare suppliers within a single procurement category."""
    result = PriceComparisonEngine.analyze_category_suppliers(
        category.replace("-", " ")
    )
    if not result:
        raise HTTPException(
            404,
            f"No multi-supplier data found for category: {category}"
        )
    return {
        "category": result.item_category,
        "supplier_count": len(result.suppliers),
        "suppliers": [
            {
                "name": s.supplier_name,
                "avg_purchase_amount": round(s.unit_price, 2),
                "total_purchased": round(s.total_purchased, 2),
                "purchase_count": s.purchase_count,
                "price_trend": s.price_trend,
                "reliability_score": round(s.reliability_score, 2),
            }
            for s in sorted(result.suppliers, key=lambda x: x.unit_price)
        ],
        "cheapest_supplier": result.cheapest_supplier,
        "price_variance_pct": result.price_variance_pct,
        "annual_overspend": result.annual_overspend,
        "recommended_primary": result.recommended_primary_supplier,
        "recommended_backup": result.recommended_backup_supplier,
        "estimated_savings": result.estimated_annual_savings,
        "bulk_buy_recommended": result.bulk_buy_recommended,
        "bulk_buy_reasoning": result.bulk_buy_reasoning,
        "consolidation_recommended": result.consolidation_recommended,
    }


@router.get("/bulk-buy-alerts")
async def get_bulk_buy_alerts():
    """Identify categories where bulk purchasing is recommended due to rising prices."""
    results = PriceComparisonEngine.analyze_all_categories()
    alerts = [r for r in results if r.bulk_buy_recommended]

    return {
        "total_alerts": len(alerts),
        "total_savings_opportunity": round(
            sum(r.estimated_annual_savings for r in alerts), 2
        ),
        "alerts": [
            {
                "category": r.item_category,
                "reasoning": r.bulk_buy_reasoning,
                "estimated_savings": r.estimated_annual_savings,
                "recommended_supplier": r.recommended_primary_supplier,
            }
            for r in alerts
        ]
    }


@router.get("/item-price-mismatches")
async def get_item_price_mismatches():
    """
    Find items where multiple suppliers sell the SAME item at different prices.
    Returns switching recommendations with per-item savings calculations.
    """
    return ItemPriceEngine.get_summary()

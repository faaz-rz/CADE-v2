import React, { useEffect, useState } from 'react';
import { ProcurementService, ItemPriceMismatch, ItemPriceMismatchResponse } from '../services/api';
import { ArrowRightLeft, TrendingDown, AlertTriangle, Package, ChevronDown, ChevronUp } from 'lucide-react';

const formatCurrency = (value: number): string => {
    if (value >= 1_000_000) return `₹${(value / 1_000_000).toFixed(1)}M`;
    if (value >= 1_000) return `₹${Math.round(value / 1_000).toLocaleString('en-IN')}K`;
    return `₹${value.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

const SeverityBadge: React.FC<{ pct: number }> = ({ pct }) => {
    if (pct >= 30) return <span className="text-xs font-bold text-red-700 bg-red-100 px-2 py-0.5 rounded-full">{pct}% overpay</span>;
    if (pct >= 15) return <span className="text-xs font-bold text-orange-700 bg-orange-100 px-2 py-0.5 rounded-full">{pct}% overpay</span>;
    return <span className="text-xs font-bold text-amber-700 bg-amber-100 px-2 py-0.5 rounded-full">{pct}% overpay</span>;
};

const MismatchCard: React.FC<{ mismatch: ItemPriceMismatch }> = ({ mismatch }) => {
    const [expanded, setExpanded] = useState(false);

    const borderColor = mismatch.price_diff_pct >= 30 ? 'border-red-200' : mismatch.price_diff_pct >= 15 ? 'border-orange-200' : 'border-amber-200';
    const bgColor = mismatch.price_diff_pct >= 30 ? 'bg-red-50/50' : mismatch.price_diff_pct >= 15 ? 'bg-orange-50/50' : 'bg-amber-50/50';

    return (
        <div className={`rounded-xl border ${borderColor} ${bgColor} overflow-hidden transition-shadow hover:shadow-md`}>
            {/* Header */}
            <div
                className="px-5 py-4 cursor-pointer flex items-center justify-between"
                onClick={() => setExpanded(!expanded)}
            >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                    <Package className="w-5 h-5 text-gray-400 flex-shrink-0" />
                    <div className="min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                            <h4 className="text-sm font-bold text-gray-900">{mismatch.item_name}</h4>
                            <span className="text-[10px] font-mono text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">{mismatch.item_code}</span>
                            <SeverityBadge pct={mismatch.price_diff_pct} />
                        </div>
                        <p className="text-xs text-gray-500 mt-0.5">{mismatch.category}</p>
                    </div>
                </div>
                <div className="flex items-center gap-4 flex-shrink-0">
                    <div className="text-right">
                        <div className="text-sm font-bold text-emerald-700">Save {formatCurrency(mismatch.annual_savings)}/yr</div>
                        <div className="text-[10px] text-gray-400">{formatCurrency(mismatch.monthly_savings)}/mo</div>
                    </div>
                    {expanded ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
                </div>
            </div>

            {/* Expanded detail */}
            {expanded && (
                <div className="px-5 pb-4 border-t border-gray-100">
                    {/* Price comparison visual */}
                    <div className="mt-3 flex items-center gap-3">
                        {/* Expensive vendor */}
                        <div className="flex-1 bg-red-50 border border-red-200 rounded-lg p-3 text-center">
                            <div className="text-[10px] text-red-500 font-semibold uppercase tracking-wide mb-1">Currently Paying</div>
                            <div className="text-lg font-bold text-red-700">₹{mismatch.expensive_price.toFixed(2)}<span className="text-xs font-normal text-red-400">/{mismatch.unit}</span></div>
                            <div className="text-xs text-gray-600 mt-1 font-medium">{mismatch.expensive_vendor}</div>
                            <div className="text-[10px] text-gray-400 mt-0.5">{mismatch.monthly_qty_at_expensive.toLocaleString('en-IN')} {mismatch.unit}s/mo</div>
                        </div>

                        {/* Arrow */}
                        <div className="flex flex-col items-center gap-1">
                            <ArrowRightLeft className="w-5 h-5 text-emerald-600" />
                            <span className="text-[10px] font-bold text-emerald-700">SWITCH</span>
                        </div>

                        {/* Cheap vendor */}
                        <div className="flex-1 bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-center">
                            <div className="text-[10px] text-emerald-600 font-semibold uppercase tracking-wide mb-1">Best Price</div>
                            <div className="text-lg font-bold text-emerald-700">₹{mismatch.cheapest_price.toFixed(2)}<span className="text-xs font-normal text-emerald-500">/{mismatch.unit}</span></div>
                            <div className="text-xs text-gray-600 mt-1 font-medium">{mismatch.cheapest_vendor}</div>
                        </div>
                    </div>

                    {/* Recommendation */}
                    <div className="mt-3 bg-white border border-gray-200 rounded-lg p-3">
                        <div className="flex items-start gap-2">
                            <TrendingDown className="w-4 h-4 text-emerald-600 mt-0.5 flex-shrink-0" />
                            <p className="text-xs text-gray-700 leading-relaxed">{mismatch.recommendation}</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export const ItemPriceMismatchPanel: React.FC = () => {
    const [data, setData] = useState<ItemPriceMismatchResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);

    useEffect(() => {
        ProcurementService.getItemPriceMismatches()
            .then(setData)
            .catch(() => setError(true))
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return (
            <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
                <div className="h-6 w-48 bg-gray-100 rounded animate-pulse mb-4" />
                <div className="space-y-3">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="h-20 bg-gray-50 rounded-xl animate-pulse" />
                    ))}
                </div>
            </div>
        );
    }

    if (error || !data || data.total_mismatches === 0) {
        return null; // Don't show panel if no mismatches (IT vertical won't have item data)
    }

    // Sort: highest savings first
    const sorted = [...data.mismatches].sort((a, b) => b.annual_savings - a.annual_savings);

    return (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-orange-50 rounded-lg">
                        <AlertTriangle className="w-5 h-5 text-orange-600" />
                    </div>
                    <div>
                        <h3 className="text-base font-bold text-gray-900">Same Item, Different Price</h3>
                        <p className="text-xs text-gray-500">Items purchased from multiple vendors at different unit prices</p>
                    </div>
                </div>
                <div className="text-right">
                    <div className="text-lg font-bold text-emerald-700">{formatCurrency(data.total_annual_savings)}</div>
                    <div className="text-[10px] text-gray-400 uppercase tracking-wide">Annual Savings</div>
                </div>
            </div>

            {/* Summary bar */}
            <div className="px-6 py-3 bg-gradient-to-r from-orange-50/50 to-emerald-50/50 border-b border-gray-100 flex items-center justify-between">
                <span className="text-xs text-gray-600">
                    <span className="font-bold text-gray-900">{data.total_mismatches}</span> items with price mismatches detected
                </span>
                <div className="flex gap-3">
                    <span className="text-[10px] text-red-600 bg-red-50 px-2 py-0.5 rounded-full font-medium border border-red-100">
                        {sorted.filter(m => m.price_diff_pct >= 30).length} severe (30%+)
                    </span>
                    <span className="text-[10px] text-orange-600 bg-orange-50 px-2 py-0.5 rounded-full font-medium border border-orange-100">
                        {sorted.filter(m => m.price_diff_pct >= 15 && m.price_diff_pct < 30).length} moderate (15-30%)
                    </span>
                    <span className="text-[10px] text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full font-medium border border-amber-100">
                        {sorted.filter(m => m.price_diff_pct < 15).length} minor (&lt;15%)
                    </span>
                </div>
            </div>

            {/* Cards */}
            <div className="p-4 space-y-3">
                {sorted.map((m) => (
                    <MismatchCard key={m.item_code} mismatch={m} />
                ))}
            </div>
        </div>
    );
};

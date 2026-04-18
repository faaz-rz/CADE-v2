import React, { useEffect, useState } from 'react';
import { ProcurementService, PriceComparisonResponse, PriceComparisonCategory, ManualDecisionService, ProcurementExportService } from '../services/api';
import { TrendingUp, TrendingDown, Minus, AlertTriangle, Package, DollarSign, Loader2, ArrowRight, Download, CheckCircle } from 'lucide-react';

const formatCurrency = (value: number): string => {
    if (value >= 10_000_000) return `₹${(value / 10_000_000).toFixed(1)}Cr`;
    if (value >= 100_000) return `₹${(value / 100_000).toFixed(1)}L`;
    if (value >= 1_000) return `₹${Math.round(value / 1_000).toLocaleString('en-IN')}K`;
    return `₹${Math.round(value).toLocaleString('en-IN')}`;
};

const TrendIcon: React.FC<{ trend: string }> = ({ trend }) => {
    if (trend === 'RISING') return <span className="inline-flex items-center gap-1 text-red-600 text-xs font-medium"><TrendingUp className="w-3 h-3" />Rising</span>;
    if (trend === 'FALLING') return <span className="inline-flex items-center gap-1 text-green-600 text-xs font-medium"><TrendingDown className="w-3 h-3" />Falling</span>;
    return <span className="inline-flex items-center gap-1 text-gray-500 text-xs font-medium"><Minus className="w-3 h-3" />Stable</span>;
};

const CategoryCard: React.FC<{ comparison: PriceComparisonCategory }> = ({ comparison }) => {
    const [switched, setSwitched] = useState(false);
    const [switching, setSwitching] = useState(false);

    const mostExpensiveSupplier = comparison.suppliers.length > 1
        ? comparison.suppliers.reduce((a, b) => a.avg_purchase_amount > b.avg_purchase_amount ? a : b).name
        : '';

    const handleSwitch = async () => {
        if (switching || switched) return;
        setSwitching(true);
        try {
            await ManualDecisionService.createFromPriceMismatch({
                entity: mostExpensiveSupplier,
                recommended_supplier: comparison.cheapest_supplier,
                product: comparison.category,
                current_price: comparison.suppliers.find(s => s.name === mostExpensiveSupplier)?.avg_purchase_amount || 0,
                best_price: comparison.suppliers.find(s => s.name === comparison.cheapest_supplier)?.avg_purchase_amount || 0,
                price_diff_pct: comparison.price_variance_pct / 100,
                estimated_saving: comparison.estimated_savings,
                category: comparison.category,
            });
            setSwitched(true);
        } catch (e) {
            console.error('Failed to create decision', e);
        } finally {
            setSwitching(false);
        }
    };

    return (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            {/* Header */}
            <div className="px-5 py-4 border-b border-gray-100 bg-gray-50/50">
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="text-base font-bold text-gray-900">{comparison.category}</h3>
                        <p className="text-xs text-gray-500 mt-0.5">{comparison.supplier_count} suppliers</p>
                    </div>
                    {comparison.annual_overspend > 0 && (
                        <span className="text-xs font-bold text-red-700 bg-red-50 px-2.5 py-1 rounded-full border border-red-100">
                            {formatCurrency(comparison.annual_overspend)} overspend
                        </span>
                    )}
                </div>
            </div>

            {/* Supplier Table */}
            <div className="overflow-x-auto">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b border-gray-100">
                            <th className="text-left px-5 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Supplier</th>
                            <th className="text-right px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Avg Purchase</th>
                            <th className="text-center px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Trend</th>
                            <th className="text-right px-5 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Reliability</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50">
                        {comparison.suppliers.map((s, idx) => {
                            const isCheapest = s.name === comparison.cheapest_supplier;
                            const isExpensive = idx === comparison.suppliers.length - 1 && comparison.suppliers.length > 1;
                            return (
                                <tr
                                    key={s.name}
                                    className={
                                        isCheapest ? 'bg-green-50/60' :
                                        isExpensive ? 'bg-red-50/40' :
                                        'hover:bg-gray-50'
                                    }
                                >
                                    <td className="px-5 py-2.5 font-medium text-gray-900 flex items-center gap-2">
                                        {s.name}
                                        {isCheapest && <span className="text-[10px] font-bold text-green-700 bg-green-100 px-1.5 py-0.5 rounded">BEST</span>}
                                    </td>
                                    <td className="text-right px-4 py-2.5 font-mono text-gray-900">{formatCurrency(s.avg_purchase_amount)}</td>
                                    <td className="text-center px-4 py-2.5"><TrendIcon trend={s.price_trend} /></td>
                                    <td className="text-right px-5 py-2.5">
                                        <div className="flex items-center justify-end gap-2">
                                            <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-blue-500 rounded-full"
                                                    style={{ width: `${s.reliability_score * 100}%` }}
                                                />
                                            </div>
                                            <span className="text-xs text-gray-500 font-mono">{(s.reliability_score * 100).toFixed(0)}%</span>
                                        </div>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>

            {/* Recommendation */}
            <div className="px-5 py-3 bg-blue-50/60 border-t border-blue-100">
                <div className="flex items-start gap-3">
                    <div className="flex-1 space-y-1">
                        <p className="text-xs text-blue-900">
                            <span className="font-semibold">Recommended Primary:</span> {comparison.recommended_primary}
                        </p>
                        {comparison.recommended_backup && (
                            <p className="text-xs text-blue-700">
                                <span className="font-semibold">Backup:</span> {comparison.recommended_backup}
                            </p>
                        )}
                    </div>
                    <span className="text-sm font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200 whitespace-nowrap">
                        Save {formatCurrency(comparison.estimated_savings)}/yr
                    </span>
                </div>
                {comparison.estimated_savings > 0 && comparison.cheapest_supplier !== mostExpensiveSupplier && (
                    <button
                        onClick={handleSwitch}
                        disabled={switching || switched}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                            switched
                                ? 'bg-emerald-100 text-emerald-700 border border-emerald-200'
                                : 'bg-teal-600 text-white hover:bg-teal-700'
                        }`}
                    >
                        {switched ? (
                            <><CheckCircle className="w-3.5 h-3.5" /> Decision Created</>
                        ) : switching ? (
                            <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Creating...</>
                        ) : (
                            <><ArrowRight className="w-3.5 h-3.5" /> SWITCH to {comparison.cheapest_supplier}</>
                        )}
                    </button>
                )}
            </div>

            {/* Bulk Buy Alert */}
            {comparison.bulk_buy_recommended && (
                <div className="px-5 py-3 bg-amber-50/80 border-t border-amber-100 flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                    <div>
                        <p className="text-xs font-semibold text-amber-800">Bulk Buy Opportunity</p>
                        <p className="text-xs text-amber-700 mt-0.5">{comparison.bulk_buy_reasoning}</p>
                    </div>
                </div>
            )}

            {/* Consolidation Alert */}
            {comparison.consolidation_recommended && (
                <div className="px-5 py-2.5 bg-purple-50/60 border-t border-purple-100 flex items-center gap-2">
                    <Package className="w-3.5 h-3.5 text-purple-500" />
                    <p className="text-xs text-purple-700 font-medium">
                        {comparison.supplier_count} suppliers detected — consolidation recommended
                    </p>
                </div>
            )}
        </div>
    );
};


export const PriceComparisonPanel: React.FC = () => {
    const [data, setData] = useState<PriceComparisonResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [severityFilter, setSeverityFilter] = useState<'ALL' | 'SEVERE' | 'MODERATE' | 'LOW'>('ALL');
    const [reportLoading, setReportLoading] = useState(false);

    useEffect(() => {
        const load = async () => {
            try {
                const result = await ProcurementService.getPriceComparison();
                setData(result);
            } catch (e) {
                console.error('Failed to load price comparison data', e);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    const handleDownloadReport = async () => {
        setReportLoading(true);
        try {
            await ProcurementExportService.downloadPriceMismatchReport();
        } catch (e) {
            console.error('Report download failed', e);
        } finally {
            setReportLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-8">
                <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
            </div>
        );
    }

    if (!data || data.comparisons.length === 0) {
        return null;
    }

    return (
        <div>
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-teal-50 rounded-lg">
                        <DollarSign className="w-5 h-5 text-teal-600" />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-gray-900">Supplier Price Intelligence</h2>
                        <p className="text-sm text-gray-500">Categories where you buy from multiple suppliers</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    {data.total_estimated_savings > 0 && (
                        <span className="text-sm font-bold text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-200">
                            {formatCurrency(data.total_estimated_savings)} savings identified
                        </span>
                    )}
                    <button
                        onClick={handleDownloadReport}
                        disabled={reportLoading}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg text-xs font-medium hover:bg-gray-200 transition-colors disabled:opacity-50"
                    >
                        {reportLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
                        Export Excel
                    </button>
                </div>
            </div>

            {/* Severity Filter */}
            <div className="flex gap-1.5 mb-4">
                {(['ALL', 'SEVERE', 'MODERATE', 'LOW'] as const).map(s => (
                    <button
                        key={s}
                        onClick={() => setSeverityFilter(s)}
                        className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${severityFilter === s
                            ? s === 'SEVERE' ? 'bg-red-600 text-white'
                                : s === 'MODERATE' ? 'bg-amber-500 text-white'
                                : s === 'LOW' ? 'bg-emerald-600 text-white'
                                : 'bg-gray-900 text-white'
                            : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
                        }`}
                    >
                        {s}
                    </button>
                ))}
            </div>

            {/* Category Cards */}
            <div className="grid gap-4">
                {data.comparisons
                    .filter(comp => {
                        if (severityFilter === 'SEVERE') return comp.price_variance_pct >= 30;
                        if (severityFilter === 'MODERATE') return comp.price_variance_pct >= 15 && comp.price_variance_pct < 30;
                        if (severityFilter === 'LOW') return comp.price_variance_pct < 15;
                        return true;
                    })
                    .map((comp) => (
                    <CategoryCard key={comp.category} comparison={comp} />
                ))}
            </div>

            {/* Bottom Summary */}
            <div className="mt-4 bg-white rounded-xl border border-gray-200 px-5 py-3 flex items-center justify-between shadow-sm">
                <span className="text-sm text-gray-600">
                    Total identified across <span className="font-semibold">{data.categories_analyzed}</span> categories
                </span>
                <span className="text-sm font-bold text-emerald-700">
                    {formatCurrency(data.total_estimated_savings)} potential savings
                </span>
            </div>
        </div>
    );
};

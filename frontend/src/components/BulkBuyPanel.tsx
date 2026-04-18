import React, { useEffect, useState } from 'react';
import { BulkBuyService, BulkBuyRecommendation } from '../services/api';
import { TrendingUp, ShoppingCart, Loader2, AlertTriangle } from 'lucide-react';

const fmt = (val: number) =>
    new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(val);

const urgencyStyle = (u: string) => {
    switch (u) {
        case 'BUY NOW': return 'bg-red-100 text-red-700 border-red-200';
        case 'CONSIDER': return 'bg-amber-100 text-amber-700 border-amber-200';
        default: return 'bg-gray-100 text-gray-600 border-gray-200';
    }
};

export const BulkBuyPanel: React.FC = () => {
    const [recs, setRecs] = useState<BulkBuyRecommendation[]>([]);
    const [loading, setLoading] = useState(true);
    const [totalSaving, setTotalSaving] = useState(0);
    const [urgentCount, setUrgentCount] = useState(0);

    useEffect(() => {
        const load = async () => {
            try {
                const data = await BulkBuyService.getRecommendations();
                setRecs(data.recommendations);
                setTotalSaving(data.total_net_saving);
                setUrgentCount(data.urgent_count);
            } catch (e) {
                console.error('Failed to load bulk buy recommendations', e);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    if (loading) {
        return (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div className="flex items-center gap-2 mb-4">
                    <ShoppingCart className="w-5 h-5 text-teal-600" />
                    <h3 className="text-base font-bold text-gray-900">Bulk Buy Intelligence</h3>
                </div>
                <div className="flex justify-center py-8">
                    <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
                </div>
            </div>
        );
    }

    if (recs.length === 0) {
        return (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div className="flex items-center gap-2 mb-4">
                    <ShoppingCart className="w-5 h-5 text-teal-600" />
                    <h3 className="text-base font-bold text-gray-900">Bulk Buy Intelligence</h3>
                </div>
                <p className="text-sm text-gray-500 text-center py-4">No bulk buy opportunities detected. Prices are stable.</p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <ShoppingCart className="w-5 h-5 text-teal-600" />
                    <h3 className="text-base font-bold text-gray-900">Bulk Buy Intelligence</h3>
                </div>
                <div className="flex items-center gap-3 text-sm">
                    {urgentCount > 0 && (
                        <span className="flex items-center gap-1 text-red-600 font-medium">
                            <AlertTriangle className="w-3.5 h-3.5" />
                            {urgentCount} urgent
                        </span>
                    )}
                    <span className="text-emerald-600 font-medium">
                        Total saving: {fmt(totalSaving)}
                    </span>
                </div>
            </div>

            <div className="space-y-3">
                {recs.slice(0, 5).map((r, i) => (
                    <div key={i} className="border border-gray-100 rounded-lg p-4">
                        <div className="flex items-start justify-between">
                            <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                    <h4 className="text-sm font-semibold text-gray-900">{r.vendor_id}</h4>
                                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${urgencyStyle(r.urgency)}`}>
                                        {r.urgency}
                                    </span>
                                </div>
                                <p className="text-xs text-gray-500">{r.category}</p>
                                <div className="flex items-center gap-4 mt-2 text-xs text-gray-600">
                                    <span className="flex items-center gap-1">
                                        <TrendingUp className="w-3 h-3 text-red-500" />
                                        +{r.price_trend_3m}% in 3mo
                                    </span>
                                    <span>Buy {r.recommended_order_months}mo supply</span>
                                    <span>Order: {fmt(r.bulk_order_amount)}</span>
                                </div>
                            </div>
                            <div className="text-right flex-shrink-0 ml-4">
                                <p className="text-sm font-bold text-emerald-600">{fmt(r.net_saving)}</p>
                                <p className="text-[10px] text-gray-400">net saving</p>
                                <p className="text-[10px] text-gray-400 mt-0.5">
                                    Storage: {fmt(r.storage_cost_estimate)}
                                </p>
                            </div>
                        </div>
                        <p className="text-xs text-gray-500 mt-2 bg-gray-50 rounded p-2">{r.reasoning}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

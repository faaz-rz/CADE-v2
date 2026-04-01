import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Loader2, Dice5, AlertTriangle, TrendingUp, Shield } from 'lucide-react';

interface MonteCarloVendorResult {
    vendor_id: string;
    simulations: number;
    mean_impact: number;
    std_deviation: number;
    percentile_10: number;
    percentile_50: number;
    percentile_90: number;
    probability_exceeds_50k: number;
    probability_exceeds_100k: number;
    probability_exceeds_500k: number;
    risk_rating: string;
}

interface MonteCarloPortfolioResult {
    simulations: number;
    vendors_analyzed: number;
    mean_portfolio_impact: number;
    std_deviation: number;
    percentile_10: number;
    percentile_50: number;
    percentile_90: number;
    probability_exceeds_100k: number;
    probability_exceeds_500k: number;
    probability_exceeds_1m: number;
    worst_case_vendor: string;
    worst_case_amount: number;
    risk_rating: string;
    vendor_results: MonteCarloVendorResult[];
}

interface MonteCarlopanelProps {
    vendorId?: string;
    vendorName?: string;
}

const fmt = (val: number): string =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

const pctFmt = (val: number): string => `${(val * 100).toFixed(1)}%`;

const ratingStyles: Record<string, string> = {
    CRITICAL: 'bg-red-600 text-white',
    HIGH: 'bg-orange-500 text-white',
    MEDIUM: 'bg-amber-400 text-gray-900',
    LOW: 'bg-emerald-500 text-white',
};

const ratingMetricColor: Record<string, string> = {
    CRITICAL: 'text-red-600',
    HIGH: 'text-orange-600',
    MEDIUM: 'text-amber-600',
    LOW: 'text-emerald-600',
};

export const MonteCarloPanel: React.FC<MonteCarlopanelProps> = ({ vendorId, vendorName }) => {
    const [vendorResult, setVendorResult] = useState<MonteCarloVendorResult | null>(null);
    const [portfolioResult, setPortfolioResult] = useState<MonteCarloPortfolioResult | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const isVendorMode = !!vendorId;

    useEffect(() => {
        const run = async () => {
            setLoading(true);
            setError(null);
            try {
                if (vendorId) {
                    const res = await api.post('/simulate/monte_carlo/vendor', {
                        vendor_id: vendorId,
                        simulations: 10000,
                    });
                    setVendorResult(res.data);
                } else {
                    const res = await api.post('/simulate/monte_carlo/portfolio', {
                        simulations: 10000,
                        correlated: true,
                    });
                    setPortfolioResult(res.data);
                }
            } catch (e: any) {
                setError(e?.response?.data?.detail || 'Simulation failed');
            } finally {
                setLoading(false);
            }
        };
        run();
    }, [vendorId]);

    if (loading) {
        return (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8 flex flex-col items-center justify-center min-h-[300px]">
                <Loader2 className="w-8 h-8 animate-spin text-purple-500 mb-3" />
                <p className="text-sm text-gray-500 font-medium">Running 10,000 simulations...</p>
                <p className="text-xs text-gray-400 mt-1">Calculating probability distributions</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-white rounded-xl border border-red-200 shadow-sm p-8 flex flex-col items-center justify-center min-h-[200px]">
                <AlertTriangle className="w-6 h-6 text-red-500 mb-2" />
                <p className="text-sm text-red-600 font-medium">{error}</p>
            </div>
        );
    }

    // Unify the data shape for rendering
    const result = isVendorMode ? vendorResult : portfolioResult;
    if (!result) return null;

    const p10 = isVendorMode ? vendorResult!.percentile_10 : portfolioResult!.percentile_10;
    const p50 = isVendorMode ? vendorResult!.percentile_50 : portfolioResult!.percentile_50;
    const p90 = isVendorMode ? vendorResult!.percentile_90 : portfolioResult!.percentile_90;
    const rating = isVendorMode ? vendorResult!.risk_rating : portfolioResult!.risk_rating;
    const sims = isVendorMode ? vendorResult!.simulations : portfolioResult!.simulations;

    // Probability bars
    const probBars = isVendorMode
        ? [
            { label: 'Impact exceeds $50K', prob: vendorResult!.probability_exceeds_50k, color: 'bg-red-500' },
            { label: 'Impact exceeds $100K', prob: vendorResult!.probability_exceeds_100k, color: 'bg-amber-500' },
            { label: 'Impact exceeds $500K', prob: vendorResult!.probability_exceeds_500k, color: 'bg-gray-400' },
        ]
        : [
            { label: 'Impact exceeds $100K', prob: portfolioResult!.probability_exceeds_100k, color: 'bg-red-500' },
            { label: 'Impact exceeds $500K', prob: portfolioResult!.probability_exceeds_500k, color: 'bg-amber-500' },
            { label: 'Impact exceeds $1M', prob: portfolioResult!.probability_exceeds_1m, color: 'bg-gray-400' },
        ];

    return (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            {/* Header */}
            <div className="px-5 py-4 border-b border-gray-100 bg-gradient-to-r from-purple-50 to-indigo-50">
                <div className="flex items-center gap-2">
                    <Dice5 className="w-5 h-5 text-purple-600" />
                    <h3 className="text-sm font-bold text-gray-900">Probability Risk Analysis</h3>
                </div>
                <p className="text-xs text-gray-500 mt-0.5">
                    Based on {sims.toLocaleString()} simulations
                    {vendorName ? ` — ${vendorName}` : ' — Full Portfolio'}
                </p>
            </div>

            <div className="p-5 space-y-6">
                {/* Main metric */}
                <div className="text-center py-4 bg-gradient-to-br from-gray-50 to-white rounded-xl border border-gray-100">
                    <p className="text-xs text-gray-500 font-medium uppercase tracking-wide mb-1">
                        Worst Case Impact
                    </p>
                    <p className={`text-4xl font-black ${ratingMetricColor[rating] || 'text-gray-900'}`}>
                        {fmt(p90)}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                        90th percentile — 1 in 10 chance of exceeding this
                    </p>
                </div>

                {/* Probability bars */}
                <div className="space-y-3">
                    <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wide">Probability Thresholds</h4>
                    {probBars.map((bar, i) => (
                        <div key={i}>
                            <div className="flex justify-between items-center mb-1">
                                <span className="text-xs text-gray-600 font-medium">{bar.label}</span>
                                <span className="text-xs font-bold text-gray-900">{pctFmt(bar.prob)}</span>
                            </div>
                            <div className="w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
                                <div
                                    className={`h-full rounded-full transition-all duration-500 ${bar.color}`}
                                    style={{ width: `${Math.max(bar.prob * 100, 1)}%` }}
                                />
                            </div>
                        </div>
                    ))}
                </div>

                {/* Scenario table */}
                <div>
                    <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Impact Scenarios</h4>
                    <div className="bg-gray-50 rounded-xl border border-gray-100 overflow-hidden">
                        <table className="w-full text-sm">
                            <tbody className="divide-y divide-gray-100">
                                <tr className="hover:bg-emerald-50/50 transition-colors">
                                    <td className="px-4 py-3 text-emerald-700 font-medium flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-emerald-500" />
                                        Best Case (10th)
                                    </td>
                                    <td className="px-4 py-3 text-right font-bold text-emerald-700 font-mono">{fmt(p10)}</td>
                                    <td className="px-4 py-3 text-right text-xs text-gray-400">Unlikely favorable</td>
                                </tr>
                                <tr className="hover:bg-blue-50/50 transition-colors">
                                    <td className="px-4 py-3 text-blue-700 font-medium flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-blue-500" />
                                        Most Likely (median)
                                    </td>
                                    <td className="px-4 py-3 text-right font-bold text-blue-700 font-mono">{fmt(p50)}</td>
                                    <td className="px-4 py-3 text-right text-xs text-gray-400">Expected outcome</td>
                                </tr>
                                <tr className="hover:bg-red-50/50 transition-colors">
                                    <td className="px-4 py-3 text-red-700 font-medium flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-red-500" />
                                        Worst Case (90th)
                                    </td>
                                    <td className="px-4 py-3 text-right font-bold text-red-700 font-mono">{fmt(p90)}</td>
                                    <td className="px-4 py-3 text-right text-xs text-gray-400">Prepare for this</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Portfolio-only: Worst vendor */}
                {!isVendorMode && portfolioResult && (
                    <div className="bg-orange-50 border border-orange-200 rounded-xl p-4">
                        <div className="flex items-center gap-2 mb-1">
                            <Shield className="w-4 h-4 text-orange-600" />
                            <span className="text-xs font-bold text-orange-800 uppercase tracking-wide">Highest Risk Vendor</span>
                        </div>
                        <p className="text-lg font-bold text-gray-900">{portfolioResult.worst_case_vendor}</p>
                        <p className="text-sm text-orange-700">
                            Potential exposure: <span className="font-bold">{fmt(portfolioResult.worst_case_amount)}</span>
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                            {portfolioResult.vendors_analyzed} vendors analyzed across portfolio
                        </p>
                    </div>
                )}

                {/* Risk rating badge */}
                <div className="flex justify-center pt-2">
                    <span className={`inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider ${ratingStyles[rating] || 'bg-gray-200 text-gray-700'}`}>
                        <TrendingUp className="w-3.5 h-3.5" />
                        {rating} Risk Rating
                    </span>
                </div>
            </div>
        </div>
    );
};

import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Loader2, Dice5, AlertTriangle, TrendingUp, Shield, CheckCircle2, Info } from 'lucide-react';

interface MonteCarloVendorResult {
    vendor_id: string;
    simulations: number;
    mean_impact: number;
    std_deviation: number;
    percentile_05: number;
    percentile_10: number;
    percentile_50: number;
    percentile_90: number;
    percentile_95: number;
    probability_exceeds_50k: number;
    probability_exceeds_100k: number;
    probability_exceeds_500k: number;
    risk_rating: string;
    seed: number;
    distribution_type: string;
    convergence_score: number;
    confidence_interval_95: [number, number];
}

interface MonteCarloPortfolioResult {
    simulations: number;
    vendors_analyzed: number;
    mean_portfolio_impact: number;
    std_deviation: number;
    percentile_05: number;
    percentile_10: number;
    percentile_50: number;
    percentile_90: number;
    percentile_95: number;
    probability_exceeds_100k: number;
    probability_exceeds_500k: number;
    probability_exceeds_1m: number;
    worst_case_vendor: string;
    worst_case_amount: number;
    risk_rating: string;
    seed: number;
    distribution_type: string;
    convergence_score: number;
    confidence_interval_95: [number, number];
    correlation_method: string;
    vendor_results: MonteCarloVendorResult[];
}

interface MonteCarlopanelProps {
    vendorId?: string;
    vendorName?: string;
}

const fmt = (val: number): string =>
    new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(val);

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

const distributionLabels: Record<string, string> = {
    student_t: 'Student-t (Fat Tails)',
    normal: 'Normal (Gaussian)',
    triangular: 'Triangular (Legacy)',
};

export const MonteCarloPanel: React.FC<MonteCarlopanelProps> = ({ vendorId, vendorName }) => {
    const [vendorResult, setVendorResult] = useState<MonteCarloVendorResult | null>(null);
    const [portfolioResult, setPortfolioResult] = useState<MonteCarloPortfolioResult | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [distribution, setDistribution] = useState<string>('student_t');
    const [hdMode, setHdMode] = useState(false);

    const isVendorMode = !!vendorId;
    const simCount = hdMode ? 200000 : 50000;

    useEffect(() => {
        const run = async () => {
            setLoading(true);
            setError(null);
            try {
                if (vendorId) {
                    const res = await api.post('/simulate/monte_carlo/vendor', {
                        vendor_id: vendorId,
                        simulations: simCount,
                        distribution,
                    });
                    setVendorResult(res.data);
                } else {
                    const res = await api.post('/simulate/monte_carlo/portfolio', {
                        simulations: simCount,
                        correlated: true,
                        distribution,
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
    }, [vendorId, distribution, hdMode]);

    if (loading) {
        return (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8 flex flex-col items-center justify-center min-h-[300px]">
                <Loader2 className="w-8 h-8 animate-spin text-purple-500 mb-3" />
                <p className="text-sm text-gray-500 font-medium">Running {simCount.toLocaleString()} simulations...</p>
                <p className="text-xs text-gray-400 mt-1">Calculating probability distributions ({distributionLabels[distribution] || distribution})</p>
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

    const p05 = isVendorMode ? vendorResult!.percentile_05 : portfolioResult!.percentile_05;
    const p10 = isVendorMode ? vendorResult!.percentile_10 : portfolioResult!.percentile_10;
    const p50 = isVendorMode ? vendorResult!.percentile_50 : portfolioResult!.percentile_50;
    const p90 = isVendorMode ? vendorResult!.percentile_90 : portfolioResult!.percentile_90;
    const p95 = isVendorMode ? vendorResult!.percentile_95 : portfolioResult!.percentile_95;
    const rating = isVendorMode ? vendorResult!.risk_rating : portfolioResult!.risk_rating;
    const sims = isVendorMode ? vendorResult!.simulations : portfolioResult!.simulations;
    const convergence = isVendorMode ? vendorResult!.convergence_score : portfolioResult!.convergence_score;
    const ci95 = isVendorMode ? vendorResult!.confidence_interval_95 : portfolioResult!.confidence_interval_95;
    const seed = isVendorMode ? vendorResult!.seed : portfolioResult!.seed;
    const distType = isVendorMode ? vendorResult!.distribution_type : portfolioResult!.distribution_type;

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

    const converged = convergence >= 0.95;

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

                {/* Controls row */}
                <div className="flex items-center gap-3 mt-3">
                    {/* Distribution selector */}
                    <select
                        value={distribution}
                        onChange={e => setDistribution(e.target.value)}
                        className="text-xs border border-gray-200 rounded-lg px-2 py-1.5 bg-white text-gray-700 focus:outline-none focus:ring-1 focus:ring-purple-400"
                    >
                        <option value="student_t">Student-t (Fat Tails)</option>
                        <option value="normal">Normal (Gaussian)</option>
                        <option value="triangular">Triangular (Legacy)</option>
                    </select>

                    {/* HD Mode toggle */}
                    <label className="flex items-center gap-1.5 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={hdMode}
                            onChange={e => setHdMode(e.target.checked)}
                            className="w-3.5 h-3.5 rounded text-purple-600 focus:ring-purple-400"
                        />
                        <span className="text-xs text-gray-600 font-medium">HD Mode (200K)</span>
                    </label>
                </div>
            </div>

            <div className="p-5 space-y-6">
                {/* Convergence indicator */}
                <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium ${converged ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'}`}>
                    {converged
                        ? <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                        : <AlertTriangle className="w-4 h-4 text-amber-500" />
                    }
                    <span>
                        Convergence: {(convergence * 100).toFixed(2)}%
                        {converged ? ' — Results are stable' : ' — Consider increasing simulations'}
                    </span>
                </div>

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
                    {/* 95% CI of the mean */}
                    {ci95 && (
                        <p className="text-xs text-gray-400 mt-1 flex items-center justify-center gap-1">
                            <Info className="w-3 h-3" />
                            Mean 95% CI: {fmt(ci95[0])} – {fmt(ci95[1])}
                        </p>
                    )}
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

                {/* Scenario table — expanded with 5th/95th */}
                <div>
                    <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Impact Scenarios</h4>
                    <div className="bg-gray-50 rounded-xl border border-gray-100 overflow-hidden">
                        <table className="w-full text-sm">
                            <tbody className="divide-y divide-gray-100">
                                <tr className="hover:bg-emerald-50/50 transition-colors">
                                    <td className="px-4 py-3 text-emerald-700 font-medium flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-emerald-400" />
                                        Extreme Best (5th)
                                    </td>
                                    <td className="px-4 py-3 text-right font-bold text-emerald-600 font-mono">{fmt(p05)}</td>
                                    <td className="px-4 py-3 text-right text-xs text-gray-400">Highly unlikely favorable</td>
                                </tr>
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
                                <tr className="hover:bg-red-50/50 transition-colors">
                                    <td className="px-4 py-3 text-red-800 font-medium flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-red-700" />
                                        Extreme Worst (95th)
                                    </td>
                                    <td className="px-4 py-3 text-right font-bold text-red-800 font-mono">{fmt(p95)}</td>
                                    <td className="px-4 py-3 text-right text-xs text-gray-400">Tail risk scenario</td>
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
                            {portfolioResult.vendors_analyzed} vendors analyzed
                            {portfolioResult.correlation_method === 'cholesky' && ' · Cholesky-correlated'}
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

                {/* Reproducibility footer */}
                <div className="border-t border-gray-100 pt-3 flex items-center justify-between text-[10px] text-gray-400">
                    <span>Seed: {seed} · {distributionLabels[distType] || distType}</span>
                    <span>Reproduce: POST with seed={seed}</span>
                </div>
            </div>
        </div>
    );
};

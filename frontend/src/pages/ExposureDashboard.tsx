import React, { useEffect, useState } from 'react';
import { FinancialExposure, ExposureService, ExportService } from '../services/api';
import { Shield, Download, AlertTriangle, TrendingUp, BarChart3 } from 'lucide-react';
import { Link } from 'react-router-dom';

export const ExposureDashboard: React.FC = () => {
    const [exposures, setExposures] = useState<FinancialExposure[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadExposures = async () => {
            setLoading(true);
            try {
                const data = await ExposureService.getAllExposures();
                setExposures(data);
            } catch (e: any) {
                setError(e?.response?.data?.detail || 'Failed to load exposure data. Upload a dataset first.');
            } finally {
                setLoading(false);
            }
        };
        loadExposures();
    }, []);

    const fmt = (val: number) =>
        new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

    const pct = (val: number) => `${(val * 100).toFixed(1)}%`;

    const totalExposure = exposures.reduce((s, e) => s + e.worst_case_exposure, 0);
    const totalSpend = exposures.reduce((s, e) => s + e.annual_spend, 0);
    const totalEbitdaDelta10 = exposures.reduce((s, e) => s + e.estimated_ebitda_delta_10pct, 0);

    // Concentration heatmap: color-code by vendor_share_pct
    const getHeatColor = (share: number): string => {
        if (share >= 0.6) return 'bg-red-500 text-white';
        if (share >= 0.4) return 'bg-orange-400 text-white';
        if (share >= 0.25) return 'bg-yellow-300 text-gray-900';
        return 'bg-green-200 text-gray-900';
    };

    return (
        <div className="max-w-6xl mx-auto px-4 py-8">
            {/* Header */}
            <header className="mb-8 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 tracking-tight flex items-center gap-3">
                        <Shield className="w-8 h-8 text-orange-500" />
                        Exposure Dashboard
                    </h1>
                    <p className="text-gray-500 mt-1">Financial exposure analysis &amp; vendor concentration</p>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={() => ExportService.downloadExecutiveReport()}
                        className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-sm font-medium shadow-sm"
                    >
                        <Download className="w-4 h-4" />
                        Export Report
                    </button>
                    <Link
                        to="/"
                        className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                        ← Decisions
                    </Link>
                </div>
            </header>

            {/* Error State */}
            {error && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center mb-6">
                    <AlertTriangle className="w-8 h-8 text-red-500 mx-auto mb-2" />
                    <p className="text-red-700 font-medium">{error}</p>
                    <Link to="/upload" className="text-red-600 underline text-sm mt-2 inline-block">
                        Upload a dataset
                    </Link>
                </div>
            )}

            {/* Loading State */}
            {loading && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8 animate-pulse">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="h-32 bg-gray-200 rounded-xl"></div>
                    ))}
                </div>
            )}

            {!loading && !error && exposures.length > 0 && (
                <>
                    {/* Top KPI Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                            <div className="flex items-center gap-3 text-gray-500 mb-2">
                                <div className="p-2 bg-orange-50 rounded-lg">
                                    <Shield className="w-5 h-5 text-orange-600" />
                                </div>
                                <span className="text-sm font-medium uppercase tracking-wide">Total Exposure</span>
                            </div>
                            <span className="text-3xl font-bold text-gray-900 block">{fmt(totalExposure)}</span>
                            <span className="text-sm text-gray-500">Worst-case scenario</span>
                        </div>

                        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                            <div className="flex items-center gap-3 text-gray-500 mb-2">
                                <div className="p-2 bg-blue-50 rounded-lg">
                                    <BarChart3 className="w-5 h-5 text-blue-600" />
                                </div>
                                <span className="text-sm font-medium uppercase tracking-wide">Total Spend</span>
                            </div>
                            <span className="text-3xl font-bold text-gray-900 block">{fmt(totalSpend)}</span>
                            <span className="text-sm text-gray-500">Across {exposures.length} vendors</span>
                        </div>

                        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                            <div className="flex items-center gap-3 text-gray-500 mb-2">
                                <div className="p-2 bg-red-50 rounded-lg">
                                    <TrendingUp className="w-5 h-5 text-red-600" />
                                </div>
                                <span className="text-sm font-medium uppercase tracking-wide">EBITDA at Risk</span>
                            </div>
                            <span className="text-3xl font-bold text-red-600 block">{fmt(totalEbitdaDelta10)}</span>
                            <span className="text-sm text-gray-500">10% shock scenario</span>
                        </div>
                    </div>

                    {/* Vendor Concentration Heatmap */}
                    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 mb-8">
                        <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                            <BarChart3 className="w-5 h-5 text-gray-400" />
                            Vendor Concentration Heatmap
                        </h2>
                        <div className="flex gap-2 mb-4 text-xs">
                            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-green-200"></span>Low (&lt;25%)</span>
                            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-yellow-300"></span>Moderate (25-40%)</span>
                            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-orange-400"></span>High (40-60%)</span>
                            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-red-500"></span>Critical (&gt;60%)</span>
                        </div>
                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
                            {exposures
                                .sort((a, b) => b.vendor_share_pct - a.vendor_share_pct)
                                .map(exp => (
                                    <div
                                        key={exp.vendor_id}
                                        className={`rounded-lg p-3 ${getHeatColor(exp.vendor_share_pct)} transition-transform hover:scale-105 cursor-default`}
                                        title={`${exp.vendor_id}: ${pct(exp.vendor_share_pct)} of ${exp.category}`}
                                    >
                                        <div className="text-sm font-bold truncate">{exp.vendor_id}</div>
                                        <div className="text-xs opacity-80 truncate">{exp.category}</div>
                                        <div className="text-lg font-bold mt-1">{pct(exp.vendor_share_pct)}</div>
                                        <div className="text-xs opacity-70">{fmt(exp.annual_spend)}</div>
                                    </div>
                                ))
                            }
                        </div>
                    </div>

                    {/* Detailed Exposure Table */}
                    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                        <div className="p-6 pb-3">
                            <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                                <Shield className="w-5 h-5 text-gray-400" />
                                Vendor Exposure Detail
                            </h2>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="bg-gray-50 border-y border-gray-200">
                                        <th className="text-left px-6 py-3 font-semibold text-gray-600 uppercase tracking-wider text-xs">Vendor</th>
                                        <th className="text-left px-4 py-3 font-semibold text-gray-600 uppercase tracking-wider text-xs">Category</th>
                                        <th className="text-right px-4 py-3 font-semibold text-gray-600 uppercase tracking-wider text-xs">Spend</th>
                                        <th className="text-right px-4 py-3 font-semibold text-gray-600 uppercase tracking-wider text-xs">Share</th>
                                        <th className="text-right px-4 py-3 font-semibold text-gray-600 uppercase tracking-wider text-xs">Exposure</th>
                                        <th className="text-right px-4 py-3 font-semibold text-gray-600 uppercase tracking-wider text-xs">10% Shock</th>
                                        <th className="text-right px-6 py-3 font-semibold text-gray-600 uppercase tracking-wider text-xs">20% Shock</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100">
                                    {exposures.map(exp => (
                                        <tr key={exp.vendor_id} className="hover:bg-gray-50 transition-colors">
                                            <td className="px-6 py-3 font-medium text-gray-900">{exp.vendor_id}</td>
                                            <td className="px-4 py-3 text-gray-600">{exp.category}</td>
                                            <td className="px-4 py-3 text-right font-mono text-gray-900">{fmt(exp.annual_spend)}</td>
                                            <td className="px-4 py-3 text-right">
                                                <span className={`inline-block px-2 py-0.5 rounded text-xs font-bold ${getHeatColor(exp.vendor_share_pct)}`}>
                                                    {pct(exp.vendor_share_pct)}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3 text-right font-mono text-red-600">{fmt(exp.worst_case_exposure)}</td>
                                            <td className="px-4 py-3 text-right font-mono text-orange-600">{fmt(exp.price_shock_impact_10pct)}</td>
                                            <td className="px-6 py-3 text-right font-mono text-red-600">{fmt(exp.price_shock_impact_20pct)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

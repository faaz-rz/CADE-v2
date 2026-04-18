import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { VendorDetailService, VendorIntelligence } from '../services/api';
import {
    ArrowLeft, TrendingUp, TrendingDown, Minus, Shield, Package, Calendar,
    BarChart3, Award, AlertTriangle, Download, Loader2, ChevronRight,
    Target, Zap, FileText, Mail, Copy, CheckCircle, DollarSign, Activity
} from 'lucide-react';
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    LineChart, Line, BarChart, Bar, ReferenceLine, Cell
} from 'recharts';
import { MonteCarloPanel } from '../components/MonteCarloPanel';

const fmt = (val: number) =>
    new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(val);

const fmtLakh = (val: number) => {
    if (val >= 1e7) return `₹${(val / 1e7).toFixed(1)}Cr`;
    if (val >= 1e5) return `₹${(val / 1e5).toFixed(1)}L`;
    if (val >= 1e3) return `₹${(val / 1e3).toFixed(1)}K`;
    return `₹${Math.round(val)}`;
};

const gradeColor = (grade: string) => {
    switch (grade) {
        case 'A': return 'bg-emerald-500 text-white';
        case 'B': return 'bg-blue-500 text-white';
        case 'C': return 'bg-amber-500 text-white';
        default: return 'bg-red-500 text-white';
    }
};

const riskBadge = (level: string) => {
    switch (level) {
        case 'HIGH': return 'bg-red-100 text-red-700 border-red-200';
        case 'MEDIUM': return 'bg-amber-100 text-amber-700 border-amber-200';
        default: return 'bg-emerald-100 text-emerald-700 border-emerald-200';
    }
};

const SECTIONS = [
    { id: 'overview', label: 'Overview' },
    { id: 'spend-trend', label: 'Spend Trend' },
    { id: 'products', label: 'Products' },
    { id: 'price-intelligence', label: 'Price Intelligence' },
    { id: 'competitive', label: 'Competitive Analysis' },
    { id: 'performance', label: 'Performance Score' },
    { id: 'contract', label: 'Contract Status' },
    { id: 'decisions', label: 'Active Decisions' },
    { id: 'monte-carlo', label: 'Monte Carlo' },
    { id: 'actions', label: 'Actions' },
];

export const VendorDeepDive: React.FC = () => {
    const { vendorId } = useParams<{ vendorId: string }>();
    const [data, setData] = useState<VendorIntelligence | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [activeSection, setActiveSection] = useState('overview');
    const [reportLoading, setReportLoading] = useState(false);
    const [showNegotiateModal, setShowNegotiateModal] = useState(false);
    const [copied, setCopied] = useState(false);

    useEffect(() => {
        if (!vendorId) return;
        const load = async () => {
            setLoading(true);
            try {
                const result = await VendorDetailService.getIntelligence(vendorId);
                setData(result);
            } catch (e: any) {
                setError(e?.response?.data?.detail || 'Failed to load vendor data');
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [vendorId]);

    const scrollTo = (id: string) => {
        setActiveSection(id);
        document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };

    const handleDownloadReport = async () => {
        if (!vendorId) return;
        setReportLoading(true);
        try {
            await VendorDetailService.downloadReport(vendorId);
        } catch { } finally {
            setReportLoading(false);
        }
    };

    const emailTemplate = data ? `Dear ${data.vendor_name},\n\nOur current ${data.contract_info.contract_type} contract expires on ${data.contract_info.renewal_date}.\nWe are evaluating renewal options and have received competitive quotes.\nWe would like to discuss revised terms before renewal.\n\nPlease provide your best renewal proposal by [DATE].\n\nRegards,\nProcurement Team` : '';

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <Loader2 className="w-8 h-8 text-teal-500 animate-spin mx-auto mb-3" />
                    <p className="text-gray-500 text-sm">Loading vendor intelligence...</p>
                </div>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="max-w-4xl mx-auto px-4 py-16 text-center">
                <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-3" />
                <h2 className="text-xl font-bold text-gray-900 mb-2">Vendor Not Found</h2>
                <p className="text-gray-500 mb-4">{error}</p>
                <Link to="/exposure" className="text-teal-600 hover:underline text-sm">← Back to Procurement Intelligence</Link>
            </div>
        );
    }

    const fs = data.financial_summary;
    const perf = data.performance_score;
    const ci = data.contract_info;
    const comp = data.competitive_position;

    return (
        <div className="flex min-h-screen bg-gray-50">
            {/* Left Sidebar */}
            <aside className="hidden lg:block w-52 bg-white border-r border-gray-200 fixed top-16 bottom-0 overflow-y-auto">
                <nav className="py-4 px-3 space-y-0.5">
                    {SECTIONS.map(s => (
                        <button
                            key={s.id}
                            onClick={() => scrollTo(s.id)}
                            className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${activeSection === s.id
                                ? 'bg-teal-50 text-teal-700 font-semibold'
                                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                }`}
                        >
                            {s.label}
                        </button>
                    ))}
                </nav>
            </aside>

            {/* Main Content */}
            <main className="flex-1 lg:ml-52 max-w-5xl mx-auto px-4 py-6">

                {/* ─── OVERVIEW ─── */}
                <section id="overview" className="mb-10">
                    <Link to="/exposure" className="text-sm text-teal-600 hover:underline flex items-center gap-1 mb-4">
                        <ArrowLeft className="w-3.5 h-3.5" /> Back to Procurement Intelligence
                    </Link>

                    <div className="flex items-start justify-between mb-6">
                        <div>
                            <h1 className="text-2xl font-bold text-gray-900">{data.vendor_name}</h1>
                            <div className="flex items-center gap-2 mt-2">
                                <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700 border border-gray-200">{data.category}</span>
                                <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${riskBadge(data.risk_level)}`}>{data.risk_level} Risk</span>
                                <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${gradeColor(perf.grade)}`}>Grade {perf.grade}</span>
                            </div>
                        </div>
                        <button
                            onClick={handleDownloadReport}
                            disabled={reportLoading}
                            className="flex items-center gap-2 px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors text-sm font-medium disabled:opacity-50"
                        >
                            {reportLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
                            Export Report
                        </button>
                    </div>

                    {/* Stat Cards */}
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                        <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
                            <p className="text-xs text-gray-500 font-medium uppercase">Annual Spend</p>
                            <p className="text-xl font-bold text-gray-900 mt-1">{fmtLakh(fs.annual_spend)}</p>
                        </div>
                        <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
                            <p className="text-xs text-gray-500 font-medium uppercase">Monthly Avg</p>
                            <p className="text-xl font-bold text-gray-900 mt-1">{fmtLakh(fs.monthly_avg)}</p>
                        </div>
                        <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
                            <p className="text-xs text-gray-500 font-medium uppercase">Category Share</p>
                            <p className="text-xl font-bold text-gray-900 mt-1">{fs.category_share_pct.toFixed(1)}%</p>
                        </div>
                        <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
                            <p className="text-xs text-gray-500 font-medium uppercase">Worst Case</p>
                            <p className="text-xl font-bold text-red-600 mt-1">{fmtLakh(fs.worst_case_exposure)}</p>
                        </div>
                        <div className={`rounded-xl border p-4 shadow-sm ${gradeColor(perf.grade)}`}>
                            <p className="text-xs font-medium uppercase opacity-80">Grade</p>
                            <p className="text-3xl font-bold mt-1">{perf.grade}</p>
                        </div>
                    </div>
                </section>

                {/* ─── SPEND TREND ─── */}
                <section id="spend-trend" className="mb-10">
                    <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <Activity className="w-5 h-5 text-blue-500" />
                        12-Month Spend Trajectory
                    </h2>
                    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
                        <ResponsiveContainer width="100%" height={280}>
                            <AreaChart data={fs.monthly_trend}>
                                <defs>
                                    <linearGradient id="spendGrad" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.15} />
                                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                <XAxis dataKey="month" tick={{ fontSize: 11 }} tickFormatter={(v: string) => {
                                    const [y, m] = v.split('-');
                                    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                                    return `${months[parseInt(m) - 1]} ${y.slice(2)}`;
                                }} />
                                <YAxis tick={{ fontSize: 11 }} tickFormatter={(v: number) => fmtLakh(v)} />
                                <Tooltip formatter={(v: any) => [fmt(v as number), 'Spend']} labelFormatter={(l: any) => `Month: ${l}`} />
                                <ReferenceLine y={fs.monthly_avg} stroke="#9ca3af" strokeDasharray="4 4" label={{ value: `Avg: ${fmtLakh(fs.monthly_avg)}`, position: 'right', fontSize: 10, fill: '#6b7280' }} />
                                <Area type="monotone" dataKey="spend" stroke="#3b82f6" strokeWidth={2} fill="url(#spendGrad)" />
                            </AreaChart>
                        </ResponsiveContainer>
                        <div className="flex gap-6 mt-3 text-sm">
                            {fs.growth_pct_3m !== null && (
                                <span className={fs.growth_pct_3m > 0 ? 'text-red-600' : 'text-emerald-600'}>
                                    3-month: {fs.growth_pct_3m > 0 ? '+' : ''}{fs.growth_pct_3m}%
                                </span>
                            )}
                            {fs.growth_pct_6m !== null && (
                                <span className={fs.growth_pct_6m > 0 ? 'text-red-600' : 'text-emerald-600'}>
                                    6-month: {fs.growth_pct_6m > 0 ? '+' : ''}{fs.growth_pct_6m}%
                                </span>
                            )}
                            <span className={fs.spend_vs_last_month_pct > 0 ? 'text-red-600' : 'text-emerald-600'}>
                                vs last month: {fs.spend_vs_last_month_pct > 0 ? '+' : ''}{fs.spend_vs_last_month_pct}%
                            </span>
                        </div>
                    </div>
                </section>

                {/* ─── PRODUCTS ─── */}
                <section id="products" className="mb-10">
                    <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <Package className="w-5 h-5 text-purple-500" />
                        Products &amp; Items Purchased
                    </h2>

                    {data.product_breakdown.length > 0 ? (
                        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                            <div className="px-5 py-3 bg-gray-50 border-b border-gray-100 text-sm text-gray-600">
                                <span className="font-semibold">{data.product_breakdown.length}</span> unique products
                                &nbsp;|&nbsp; <span className="font-semibold">{fmt(fs.annual_spend)}</span> total spend
                                &nbsp;|&nbsp; <span className="font-semibold">{data.product_breakdown.filter(p => p.market_benchmark_price).length}</span> with market price data
                            </div>
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                    <thead>
                                        <tr className="border-b border-gray-100">
                                            <th className="text-left px-5 py-2.5 text-xs font-semibold text-gray-500 uppercase">Product</th>
                                            <th className="text-right px-3 py-2.5 text-xs font-semibold text-gray-500 uppercase">Avg Price</th>
                                            <th className="text-right px-3 py-2.5 text-xs font-semibold text-gray-500 uppercase">Market</th>
                                            <th className="text-center px-3 py-2.5 text-xs font-semibold text-gray-500 uppercase">vs Market</th>
                                            <th className="text-right px-3 py-2.5 text-xs font-semibold text-gray-500 uppercase">Monthly Spend</th>
                                            <th className="text-right px-3 py-2.5 text-xs font-semibold text-gray-500 uppercase">% Total</th>
                                            <th className="text-center px-3 py-2.5 text-xs font-semibold text-gray-500 uppercase">Trend</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {data.product_breakdown.map((p, i) => (
                                            <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'}>
                                                <td className="px-5 py-2.5 font-medium text-gray-900">{p.product_name}</td>
                                                <td className="text-right px-3 py-2.5 font-mono text-gray-700">{fmtLakh(p.avg_unit_price)}</td>
                                                <td className="text-right px-3 py-2.5 font-mono text-gray-500">
                                                    {p.market_benchmark_price ? fmtLakh(p.market_benchmark_price) : '—'}
                                                </td>
                                                <td className="text-center px-3 py-2.5">
                                                    {p.vs_market_pct !== null ? (
                                                        p.vs_market_pct > 15 ? (
                                                            <span className="inline-block px-2 py-0.5 rounded text-xs font-bold bg-red-100 text-red-700">Overpaying {p.vs_market_pct.toFixed(0)}%</span>
                                                        ) : p.vs_market_pct < -5 ? (
                                                            <span className="inline-block px-2 py-0.5 rounded text-xs font-bold bg-emerald-100 text-emerald-700">Below market</span>
                                                        ) : (
                                                            <span className="text-xs text-gray-500">{p.vs_market_pct > 0 ? '+' : ''}{p.vs_market_pct.toFixed(0)}%</span>
                                                        )
                                                    ) : '—'}
                                                </td>
                                                <td className="text-right px-3 py-2.5 font-mono text-gray-700">{fmtLakh(p.monthly_spend)}</td>
                                                <td className="text-right px-3 py-2.5 text-gray-600">{p.pct_of_vendor_total.toFixed(1)}%</td>
                                                <td className="text-center px-3 py-2.5">
                                                    {p.price_trend === 'RISING' ? <TrendingUp className="w-4 h-4 text-red-500 inline" /> :
                                                        p.price_trend === 'FALLING' ? <TrendingDown className="w-4 h-4 text-emerald-500 inline" /> :
                                                            <Minus className="w-4 h-4 text-gray-400 inline" />}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                            {data.product_breakdown.some(p => p.overpaying) && (
                                <div className="px-5 py-3 bg-amber-50 border-t border-amber-200 text-sm text-amber-800">
                                    ⚠️ You are overpaying on <b>{data.product_breakdown.filter(p => p.overpaying).length}</b> products vs market rates.
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 text-center">
                            <Package className="w-8 h-8 text-blue-400 mx-auto mb-2" />
                            <p className="text-sm text-blue-800 font-medium">Upload itemized purchase register to see product breakdown.</p>
                            <p className="text-xs text-blue-600 mt-1">Your current data shows total spend per vendor only.</p>
                        </div>
                    )}
                </section>

                {/* ─── PRICE INTELLIGENCE ─── */}
                <section id="price-intelligence" className="mb-10">
                    <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <DollarSign className="w-5 h-5 text-teal-500" />
                        Price History &amp; Market Benchmarks
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
                            <h3 className="text-sm font-semibold text-gray-700 mb-3">Price History</h3>
                            <ResponsiveContainer width="100%" height={220}>
                                <LineChart data={data.price_history}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                    <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                                    <YAxis tick={{ fontSize: 10 }} tickFormatter={(v: number) => fmtLakh(v)} />
                                    <Tooltip formatter={(v: any) => [fmt(v as number), 'Avg Amount']} />
                                    <Line type="monotone" dataKey="avg_transaction_amount" stroke="#0d9488" strokeWidth={2} dot={{ r: 3 }} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
                            <h3 className="text-sm font-semibold text-gray-700 mb-3">Market Benchmark Comparison</h3>
                            {data.product_breakdown.filter(p => p.market_benchmark_price).length > 0 ? (
                                <div className="space-y-2">
                                    {data.product_breakdown.filter(p => p.market_benchmark_price).map((p, i) => (
                                        <div key={i} className="flex items-center justify-between text-sm border-b border-gray-50 pb-2">
                                            <span className="text-gray-700 truncate max-w-[120px]">{p.product_name}</span>
                                            <div className="flex items-center gap-3">
                                                <span className="text-gray-500 font-mono text-xs">{fmtLakh(p.avg_unit_price)}</span>
                                                <span className="text-gray-400">→</span>
                                                <span className="text-gray-500 font-mono text-xs">{fmtLakh(p.market_benchmark_price!)}</span>
                                                <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${p.vs_market_pct! > 30 ? 'bg-red-100 text-red-700' :
                                                    p.vs_market_pct! > 10 ? 'bg-amber-100 text-amber-700' :
                                                        'bg-emerald-100 text-emerald-700'
                                                    }`}>
                                                    {p.vs_market_pct! > 30 ? 'Critical' : p.vs_market_pct! > 10 ? 'Overpaying' : 'Competitive'}
                                                </span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-sm text-gray-400 text-center py-8">No benchmark data available for this vendor's products</p>
                            )}
                            <p className="text-[10px] text-gray-400 mt-3">Market prices based on NPPA MRP data and procurement benchmarks.</p>
                        </div>
                    </div>
                </section>

                {/* ─── COMPETITIVE ANALYSIS ─── */}
                <section id="competitive" className="mb-10">
                    <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <BarChart3 className="w-5 h-5 text-indigo-500" />
                        Competitive Supplier Analysis
                    </h2>
                    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
                        {comp.category_vendors.length > 0 && (
                            <ResponsiveContainer width="100%" height={Math.max(150, comp.category_vendors.length * 40)}>
                                <BarChart data={comp.category_vendors} layout="vertical" margin={{ left: 20 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                    <XAxis type="number" tickFormatter={(v: number) => fmtLakh(v)} tick={{ fontSize: 10 }} />
                                    <YAxis type="category" dataKey="vendor_name" tick={{ fontSize: 11 }} width={140} />
                                    <Tooltip formatter={(v: any) => [fmt(v as number), 'Annual Spend']} />
                                    <Bar dataKey="annual_spend" radius={[0, 4, 4, 0]}>
                                        {comp.category_vendors.map((v, i) => (
                                            <Cell key={i} fill={v.is_current_vendor ? '#3b82f6' : v.price_rank === 1 ? '#10b981' : '#d1d5db'} />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        )}
                        {comp.cheapest_alternative && comp.potential_saving_if_switched > 0 && (
                            <div className="mt-4 bg-emerald-50 border border-emerald-200 rounded-lg p-4">
                                <p className="text-sm text-emerald-800">
                                    <span className="font-bold">Switching to {comp.cheapest_alternative}</span> could save{' '}
                                    <span className="font-bold">{fmtLakh(comp.potential_saving_if_switched)}/year</span>
                                </p>
                                <p className="text-xs text-emerald-600 mt-1">{comp.switching_recommendation}</p>
                            </div>
                        )}
                    </div>
                </section>

                {/* ─── PERFORMANCE SCORE ─── */}
                <section id="performance" className="mb-10">
                    <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <Award className="w-5 h-5 text-yellow-500" />
                        Vendor Performance Scorecard
                    </h2>
                    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                        <div className="text-center mb-6">
                            <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full text-3xl font-bold ${gradeColor(perf.grade)}`}>
                                {perf.grade}
                            </div>
                            <p className="text-sm text-gray-600 mt-2 max-w-md mx-auto">{perf.grade_explanation}</p>
                        </div>
                        <div className="space-y-4 max-w-lg mx-auto">
                            {[
                                { label: 'Price Competitiveness', value: perf.price_competitiveness, desc: 'Pricing vs alternatives' },
                                { label: 'Price Stability', value: perf.price_stability, desc: 'Price consistency over time' },
                                { label: 'Spend Efficiency', value: perf.spend_efficiency, desc: 'Spend within budget thresholds' },
                                { label: 'Risk Profile', value: perf.risk_score, desc: 'Overall risk assessment' },
                            ].map((item, i) => (
                                <div key={i}>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="font-medium text-gray-700">{item.label}</span>
                                        <span className={`font-bold ${item.value > 0.7 ? 'text-emerald-600' : item.value > 0.4 ? 'text-amber-600' : 'text-red-600'}`}>
                                            {(item.value * 100).toFixed(0)}%
                                        </span>
                                    </div>
                                    <div className="w-full h-2.5 bg-gray-100 rounded-full overflow-hidden">
                                        <div
                                            className={`h-full rounded-full transition-all ${item.value > 0.7 ? 'bg-emerald-500' : item.value > 0.4 ? 'bg-amber-500' : 'bg-red-500'}`}
                                            style={{ width: `${item.value * 100}%` }}
                                        />
                                    </div>
                                    <p className="text-xs text-gray-400 mt-0.5">{item.desc}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* ─── CONTRACT STATUS ─── */}
                <section id="contract" className="mb-10">
                    <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <Calendar className="w-5 h-5 text-blue-500" />
                        Contract &amp; AMC Status
                    </h2>
                    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                        <div className="flex items-center gap-6 mb-4">
                            <div className={`text-center px-6 py-3 rounded-xl ${ci.days_until_renewal < 30 ? 'bg-red-50 text-red-700' :
                                ci.days_until_renewal < 60 ? 'bg-amber-50 text-amber-700' : 'bg-emerald-50 text-emerald-700'
                                }`}>
                                <p className="text-3xl font-bold">{ci.days_until_renewal}</p>
                                <p className="text-xs font-medium">days until renewal</p>
                            </div>
                            <div className="space-y-1 text-sm">
                                <p><span className="text-gray-500">Renewal date:</span> <span className="font-medium">{ci.renewal_date}</span></p>
                                <p><span className="text-gray-500">Contract type:</span> <span className="font-medium">{ci.contract_type}</span></p>
                                <p><span className="text-gray-500">Annual value:</span> <span className="font-medium">{fmt(fs.annual_spend)}</span></p>
                            </div>
                        </div>

                        {ci.is_amc && (
                            <div className="mt-4 border-t border-gray-100 pt-4">
                                <h3 className="text-sm font-bold text-gray-800 mb-3">AMC Details</h3>
                                <div className="grid grid-cols-3 gap-3 text-sm mb-4">
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-500">Current Rate</p>
                                        <p className="font-bold text-gray-900">{((ci.amc_rate_current || 0) * 100).toFixed(0)}%</p>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-500">Market Rate</p>
                                        <p className="font-bold text-emerald-600">{((ci.amc_rate_market || 0) * 100).toFixed(0)}%</p>
                                    </div>
                                    <div className="bg-emerald-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-500">Annual Saving</p>
                                        <p className="font-bold text-emerald-700">{fmtLakh(ci.amc_saving_opportunity)}</p>
                                    </div>
                                </div>
                                <div className="space-y-2 text-sm text-gray-600 mb-4">
                                    {['Obtain quotes from 2 alternative service providers',
                                        'Calculate cost of extended warranty vs AMC',
                                        'Review last year\'s service call frequency',
                                        'Prepare competitive tender document'].map((item, i) => (
                                            <label key={i} className="flex items-center gap-2 cursor-pointer">
                                                <input type="checkbox" className="rounded border-gray-300 text-teal-600" />
                                                <span>{item}</span>
                                            </label>
                                        ))}
                                </div>
                                <button
                                    onClick={() => setShowNegotiateModal(true)}
                                    className="px-4 py-2 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors"
                                >
                                    <Mail className="w-4 h-4 inline mr-1.5" />Start Negotiation
                                </button>
                            </div>
                        )}
                    </div>
                </section>

                {/* ─── DECISIONS ─── */}
                <section id="decisions" className="mb-10">
                    <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <Shield className="w-5 h-5 text-orange-500" />
                        CADE Risk Decisions
                    </h2>
                    {data.decisions.length > 0 ? (
                        <div className="space-y-3">
                            {data.decisions.map(d => (
                                <div key={d.decision_id} className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex items-center justify-between">
                                    <div className="flex-1">
                                        <p className="font-medium text-gray-900 text-sm">{d.title}</p>
                                        <div className="flex items-center gap-3 mt-1.5">
                                            <span className={`px-2 py-0.5 rounded text-xs font-bold border ${riskBadge(d.risk_level)}`}>{d.risk_level}</span>
                                            <span className="px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">{d.status}</span>
                                            <span className="text-xs text-gray-500">Impact: {fmtLakh(d.annual_impact)}</span>
                                        </div>
                                    </div>
                                    <Link to="/" className="text-sm text-teal-600 hover:underline flex items-center gap-1">
                                        View <ChevronRight className="w-3.5 h-3.5" />
                                    </Link>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8 bg-white rounded-xl border border-gray-200">
                            <CheckCircle className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                            <p className="text-sm text-gray-500">No active risk decisions for this vendor</p>
                        </div>
                    )}
                </section>

                {/* ─── MONTE CARLO ─── */}
                <section id="monte-carlo" className="mb-10">
                    <h2 className="text-lg font-bold text-gray-900 mb-2 flex items-center gap-2">
                        <Target className="w-5 h-5 text-purple-500" />
                        Probabilistic Risk Analysis
                    </h2>
                    <p className="text-sm text-gray-500 mb-4">What could go wrong — mathematically</p>
                    <MonteCarloPanel vendorId={vendorId} />
                </section>

                {/* ─── RECOMMENDED ACTIONS ─── */}
                <section id="actions" className="mb-10">
                    <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <Zap className="w-5 h-5 text-amber-500" />
                        Priority Actions
                    </h2>
                    <div className="space-y-3">
                        {data.recommended_actions
                            .sort((a, b) => {
                                const pri = { HIGH: 0, MEDIUM: 1, LOW: 2 };
                                return (pri[a.priority as keyof typeof pri] ?? 2) - (pri[b.priority as keyof typeof pri] ?? 2);
                            })
                            .map((a, i) => (
                                <div key={i} className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex items-start gap-3">
                                    <div className={`w-2.5 h-2.5 rounded-full mt-1.5 flex-shrink-0 ${a.priority === 'HIGH' ? 'bg-red-500' : a.priority === 'MEDIUM' ? 'bg-amber-500' : 'bg-gray-300'}`} />
                                    <div className="flex-1">
                                        <p className="font-medium text-gray-900 text-sm">{a.title}</p>
                                        <p className="text-xs text-gray-500 mt-1">{a.description}</p>
                                        {a.deadline && <p className="text-xs text-gray-400 mt-1">Deadline: {a.deadline}</p>}
                                    </div>
                                    {a.estimated_saving > 0 && (
                                        <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200 whitespace-nowrap">
                                            Save {fmtLakh(a.estimated_saving)}
                                        </span>
                                    )}
                                </div>
                            ))}
                    </div>

                    <div className="mt-6">
                        <button
                            onClick={handleDownloadReport}
                            disabled={reportLoading}
                            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition-colors text-sm font-medium disabled:opacity-50"
                        >
                            {reportLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
                            Export Complete Vendor Report (PDF)
                        </button>
                    </div>
                </section>
            </main>

            {/* Negotiate Modal */}
            {showNegotiateModal && (
                <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={() => setShowNegotiateModal(false)}>
                    <div className="bg-white rounded-2xl shadow-xl max-w-lg w-full p-6" onClick={e => e.stopPropagation()}>
                        <h3 className="text-lg font-bold text-gray-900 mb-3">Negotiation Email Template</h3>
                        <textarea
                            value={emailTemplate}
                            readOnly
                            className="w-full h-48 p-3 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-700 resize-none"
                        />
                        <div className="flex gap-3 mt-4">
                            <button
                                onClick={() => {
                                    navigator.clipboard.writeText(emailTemplate);
                                    setCopied(true);
                                    setTimeout(() => setCopied(false), 2000);
                                }}
                                className="flex items-center gap-2 px-4 py-2 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700"
                            >
                                {copied ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                                {copied ? 'Copied!' : 'Copy Email'}
                            </button>
                            <button onClick={() => setShowNegotiateModal(false)} className="px-4 py-2 text-gray-600 text-sm">Close</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

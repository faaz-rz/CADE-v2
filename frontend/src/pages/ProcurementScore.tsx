import React, { useEffect, useState } from 'react';
import { ProcurementScoreService, ProcurementScoreResponse } from '../services/api';
import { Award, Loader2, TrendingUp, Target, Zap } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const gradeColor = (grade: string) => {
    switch (grade) {
        case 'A': return { bg: 'bg-emerald-500', text: 'text-emerald-600', ring: 'ring-emerald-200' };
        case 'B': return { bg: 'bg-blue-500', text: 'text-blue-600', ring: 'ring-blue-200' };
        case 'C': return { bg: 'bg-amber-500', text: 'text-amber-600', ring: 'ring-amber-200' };
        default: return { bg: 'bg-red-500', text: 'text-red-600', ring: 'ring-red-200' };
    }
};

const scoreColor = (score: number) => {
    if (score >= 70) return '#10b981';
    if (score >= 40) return '#f59e0b';
    return '#ef4444';
};

export const ProcurementScorePage: React.FC = () => {
    const [data, setData] = useState<ProcurementScoreResponse | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const result = await ProcurementScoreService.getScore();
                setData(result);
            } catch (e) {
                console.error('Failed to load procurement score', e);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <Loader2 className="w-6 h-6 text-teal-500 animate-spin" />
            </div>
        );
    }

    if (!data) return null;

    const gc = gradeColor(data.grade);
    const components = [
        { key: 'price_competitiveness', label: 'Price Competitiveness', desc: 'Are you paying market rates?', icon: '💰' },
        { key: 'vendor_diversification', label: 'Vendor Diversification', desc: 'Are you too dependent on single vendors?', icon: '🔀' },
        { key: 'contract_management', label: 'Contract Management', desc: 'Are you managing renewals proactively?', icon: '📋' },
        { key: 'spend_control', label: 'Spend Control', desc: 'Is vendor spend growing within budget?', icon: '📊' },
        { key: 'savings_capture', label: 'Savings Capture', desc: 'Are you acting on identified savings?', icon: '✅' },
    ];

    const benchmarkData = [
        { name: 'Your Score', value: data.benchmarks.your_score, fill: scoreColor(data.benchmarks.your_score) },
        { name: 'Industry Avg', value: data.benchmarks.industry_average, fill: '#9ca3af' },
        { name: 'Top Quartile', value: data.benchmarks.top_quartile, fill: '#3b82f6' },
    ];

    return (
        <div className="max-w-5xl mx-auto px-4 py-8">
            <header className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 tracking-tight flex items-center gap-3">
                    <Award className="w-8 h-8 text-amber-500" />
                    Procurement Health Score
                </h1>
                <p className="text-gray-500 mt-1">Your hospital's procurement efficiency assessment</p>
            </header>

            {/* Overall Score Gauge */}
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 text-center mb-8">
                <div className={`inline-flex items-center justify-center w-32 h-32 rounded-full ring-8 ${gc.ring} ${gc.bg} text-white mb-4`}>
                    <div>
                        <p className="text-4xl font-bold">{Math.round(data.overall_score)}</p>
                        <p className="text-xs opacity-80">/ 100</p>
                    </div>
                </div>
                <div className="mb-3">
                    <span className={`inline-block px-4 py-1.5 rounded-full text-lg font-bold ${gc.bg} text-white`}>
                        Grade {data.grade}
                    </span>
                </div>
                <p className="text-sm text-gray-500 max-w-md mx-auto">
                    Your procurement efficiency score based on 5 key performance indicators
                </p>
            </div>

            {/* Score Breakdown */}
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Target className="w-5 h-5 text-blue-500" />
                Score Breakdown
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
                {components.map(comp => {
                    const score = data.components[comp.key as keyof typeof data.components];
                    return (
                        <div key={comp.key} className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
                            <div className="flex items-center gap-2 mb-2">
                                <span className="text-xl">{comp.icon}</span>
                                <h3 className="text-sm font-bold text-gray-800">{comp.label}</h3>
                            </div>
                            <p className="text-xs text-gray-500 mb-3">{comp.desc}</p>
                            <div className="flex items-center gap-3">
                                <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
                                    <div
                                        className="h-full rounded-full transition-all duration-700"
                                        style={{ width: `${score}%`, backgroundColor: scoreColor(score) }}
                                    />
                                </div>
                                <span className="text-sm font-bold" style={{ color: scoreColor(score) }}>
                                    {score.toFixed(0)}
                                </span>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Benchmark Comparison */}
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-emerald-500" />
                How Does Your Hospital Compare?
            </h2>
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 mb-8">
                <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={benchmarkData} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} />
                        <YAxis type="category" dataKey="name" tick={{ fontSize: 12, fontWeight: 600 }} width={110} />
                        <Tooltip formatter={(v: any) => [`${(v as number).toFixed(1)}`, 'Score']} />
                        <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={28}>
                            {benchmarkData.map((entry, i) => (
                                <Cell key={i} fill={entry.fill} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
                <p className="text-xs text-gray-400 mt-2 text-center">
                    Industry benchmarks based on similar-sized hospitals. Your data remains confidential.
                </p>
            </div>

            {/* Improvement Roadmap */}
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Zap className="w-5 h-5 text-amber-500" />
                Top 3 Actions to Improve Your Score
            </h2>
            <div className="space-y-3">
                {data.improvement_roadmap.map((item, i) => (
                    <div key={i} className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 flex items-start gap-4">
                        <div className="w-8 h-8 rounded-full bg-teal-100 text-teal-700 flex items-center justify-center font-bold text-sm flex-shrink-0">
                            {i + 1}
                        </div>
                        <div className="flex-1">
                            <h3 className="text-sm font-bold text-gray-900">{item.action}</h3>
                            <p className="text-xs text-gray-500 mt-1">
                                Component: {item.component} (current: {item.current_score.toFixed(0)})
                            </p>
                        </div>
                        <div className="text-right flex-shrink-0">
                            <p className="text-sm font-bold text-emerald-600">+{item.expected_improvement} pts</p>
                            <p className="text-xs text-gray-400">{item.effort} effort</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

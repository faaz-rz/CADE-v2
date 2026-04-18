import React, { useEffect, useState } from 'react';
import { AlertsService, HospitalAlert } from '../services/api';
import { Bell, AlertTriangle, Shield, DollarSign, FileText, Loader2, CheckCircle, Filter } from 'lucide-react';
import { Link } from 'react-router-dom';

const severityDot = (sev: string) => {
    switch (sev) {
        case 'CRITICAL': return 'bg-red-500';
        case 'HIGH': return 'bg-orange-500';
        case 'MEDIUM': return 'bg-amber-400';
        default: return 'bg-gray-300';
    }
};

const severityBadge = (sev: string) => {
    switch (sev) {
        case 'CRITICAL': return 'bg-red-100 text-red-700 border-red-200';
        case 'HIGH': return 'bg-orange-100 text-orange-700 border-orange-200';
        case 'MEDIUM': return 'bg-amber-100 text-amber-700 border-amber-200';
        default: return 'bg-gray-100 text-gray-600 border-gray-200';
    }
};

const categoryIcon = (cat: string) => {
    switch (cat) {
        case 'PRICE': return <DollarSign className="w-4 h-4" />;
        case 'CONTRACT': return <FileText className="w-4 h-4" />;
        case 'SPEND': return <AlertTriangle className="w-4 h-4" />;
        default: return <Shield className="w-4 h-4" />;
    }
};

const fmt = (val: number) =>
    new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(val);

export const AlertsPage: React.FC = () => {
    const [alerts, setAlerts] = useState<HospitalAlert[]>([]);
    const [loading, setLoading] = useState(true);
    const [counts, setCounts] = useState({ total: 0, critical: 0, high: 0, medium: 0, low: 0 });
    const [filterSeverity, setFilterSeverity] = useState<string>('ALL');
    const [filterCategory, setFilterCategory] = useState<string>('ALL');
    const [readAlerts, setReadAlerts] = useState<Set<string>>(new Set());

    useEffect(() => {
        const load = async () => {
            try {
                const data = await AlertsService.getAlerts();
                setAlerts(data.alerts);
                setCounts({
                    total: data.total,
                    critical: data.critical,
                    high: data.high,
                    medium: data.medium,
                    low: data.low,
                });
            } catch (e) {
                console.error('Failed to load alerts', e);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    const markAsRead = (id: string) => {
        setReadAlerts(prev => new Set(prev).add(id));
    };

    const filtered = alerts.filter(a => {
        if (filterSeverity !== 'ALL' && a.severity !== filterSeverity) return false;
        if (filterCategory !== 'ALL' && a.category !== filterCategory) return false;
        return true;
    });

    const categories = [...new Set(alerts.map(a => a.category))];

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <Loader2 className="w-6 h-6 text-teal-500 animate-spin" />
            </div>
        );
    }

    return (
        <div className="max-w-5xl mx-auto px-4 py-8">
            <header className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 tracking-tight flex items-center gap-3">
                    <Bell className="w-8 h-8 text-amber-500" />
                    Procurement Alerts
                </h1>
                <p className="text-gray-500 mt-1">Real-time alerts for pricing, contracts, and spend anomalies</p>
            </header>

            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
                <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                    <p className="text-xs text-red-600 font-medium uppercase">Critical</p>
                    <p className="text-2xl font-bold text-red-700">{counts.critical}</p>
                </div>
                <div className="bg-orange-50 border border-orange-200 rounded-xl p-4">
                    <p className="text-xs text-orange-600 font-medium uppercase">High</p>
                    <p className="text-2xl font-bold text-orange-700">{counts.high}</p>
                </div>
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                    <p className="text-xs text-amber-600 font-medium uppercase">Medium</p>
                    <p className="text-2xl font-bold text-amber-700">{counts.medium}</p>
                </div>
                <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
                    <p className="text-xs text-gray-500 font-medium uppercase">Total</p>
                    <p className="text-2xl font-bold text-gray-800">{counts.total}</p>
                </div>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap gap-3 mb-6">
                <div className="flex items-center gap-2">
                    <Filter className="w-4 h-4 text-gray-400" />
                    <span className="text-sm text-gray-500">Severity:</span>
                    {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(s => (
                        <button
                            key={s}
                            onClick={() => setFilterSeverity(s)}
                            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${filterSeverity === s
                                ? 'bg-gray-900 text-white shadow-sm'
                                : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
                                }`}
                        >
                            {s}
                        </button>
                    ))}
                </div>
                <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-500">Category:</span>
                    <button
                        onClick={() => setFilterCategory('ALL')}
                        className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${filterCategory === 'ALL'
                            ? 'bg-gray-900 text-white shadow-sm'
                            : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
                            }`}
                    >
                        All
                    </button>
                    {categories.map(c => (
                        <button
                            key={c}
                            onClick={() => setFilterCategory(c)}
                            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${filterCategory === c
                                ? 'bg-gray-900 text-white shadow-sm'
                                : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
                                }`}
                        >
                            {c}
                        </button>
                    ))}
                </div>
            </div>

            {/* Alert List */}
            <div className="space-y-3">
                {filtered.length > 0 ? filtered.map(alert => (
                    <div
                        key={alert.alert_id}
                        className={`bg-white rounded-xl border shadow-sm p-4 transition-all ${readAlerts.has(alert.alert_id) ? 'border-gray-100 opacity-70' : 'border-gray-200'
                            }`}
                    >
                        <div className="flex items-start gap-3">
                            <div className={`w-2.5 h-2.5 rounded-full mt-1.5 flex-shrink-0 ${severityDot(alert.severity)}`} />
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${severityBadge(alert.severity)}`}>
                                        {alert.severity}
                                    </span>
                                    <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-gray-100 text-gray-600 text-[10px] font-medium">
                                        {categoryIcon(alert.category)}
                                        {alert.category}
                                    </span>
                                </div>
                                <h3 className="text-sm font-medium text-gray-900">{alert.title}</h3>
                                <p className="text-xs text-gray-500 mt-1">{alert.message}</p>
                                {alert.estimated_impact > 0 && (
                                    <p className="text-xs font-medium text-emerald-600 mt-1">
                                        Estimated impact: {fmt(alert.estimated_impact)}
                                    </p>
                                )}
                            </div>
                            <div className="flex flex-col gap-2 flex-shrink-0">
                                <Link
                                    to={alert.action_url}
                                    className="px-3 py-1.5 bg-teal-50 text-teal-700 rounded-lg text-xs font-medium hover:bg-teal-100 transition-colors text-center"
                                >
                                    View
                                </Link>
                                {!readAlerts.has(alert.alert_id) && (
                                    <button
                                        onClick={() => markAsRead(alert.alert_id)}
                                        className="px-3 py-1.5 bg-gray-50 text-gray-500 rounded-lg text-xs font-medium hover:bg-gray-100 transition-colors"
                                    >
                                        Mark Read
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>
                )) : (
                    <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
                        <CheckCircle className="w-10 h-10 text-emerald-400 mx-auto mb-2" />
                        <p className="text-gray-500">No alerts matching your filters</p>
                    </div>
                )}
            </div>
        </div>
    );
};

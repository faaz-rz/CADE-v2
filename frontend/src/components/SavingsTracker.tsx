import React, { useEffect, useState } from 'react';
import { SavingsService, SavingsSummary } from '../services/api';
import { TrendingUp, CheckCircle, Clock, XCircle } from 'lucide-react';

interface SavingsTrackerProps {
    /** Trigger a refresh — increment this value after approve/reject actions */
    refreshKey?: number;
}

const formatCurrency = (value: number): string => {
    if (value >= 1_000_000) return `₹${(value / 1_000_000).toFixed(1)}M`;
    if (value >= 1_000) return `₹${Math.round(value / 1_000).toLocaleString('en-IN')}K`;
    return `₹${Math.round(value).toLocaleString('en-IN')}`;
};

export const SavingsTracker: React.FC<SavingsTrackerProps> = ({ refreshKey = 0 }) => {
    const [savings, setSavings] = useState<SavingsSummary | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            try {
                const data = await SavingsService.getSavings();
                setSavings(data);
            } catch (e) {
                console.error('Failed to load savings', e);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [refreshKey]);

    if (loading) {
        return (
            <div className="mb-6 h-28 bg-gray-50 rounded-xl animate-pulse border border-gray-200" />
        );
    }

    if (!savings || savings.total_identified === 0) {
        return null;
    }

    const hasApprovedSavings = savings.approved_savings > 0;

    return (
        <div className="mb-6 bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            {/* Header */}
            <div className="px-5 py-3 bg-gradient-to-r from-gray-50 to-white border-b border-gray-100 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-emerald-600" />
                    <span className="text-sm font-semibold text-gray-800 tracking-wide uppercase">
                        Savings Identified by CADE
                    </span>
                </div>
                {hasApprovedSavings && (
                    <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
                        ROI: {savings.roi_multiple}x
                    </span>
                )}
            </div>

            {/* Metrics */}
            <div className="px-5 py-4 grid grid-cols-3 gap-4">
                {/* Approved */}
                <div className="bg-emerald-50 rounded-lg p-3 border border-emerald-100">
                    <div className="flex items-center gap-1.5 mb-1">
                        <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                        <span className="text-xs font-medium text-emerald-700">Approved</span>
                        <span className="text-xs text-emerald-500 ml-auto">
                            {savings.decisions_approved_count}
                        </span>
                    </div>
                    {hasApprovedSavings ? (
                        <span className="text-lg font-bold text-emerald-800">
                            {formatCurrency(savings.approved_savings)}
                        </span>
                    ) : (
                        <span className="text-xs text-emerald-600 leading-tight block">
                            Approve decisions to start tracking savings
                        </span>
                    )}
                </div>

                {/* Pending */}
                <div className="bg-blue-50 rounded-lg p-3 border border-blue-100">
                    <div className="flex items-center gap-1.5 mb-1">
                        <Clock className="w-3.5 h-3.5 text-blue-600" />
                        <span className="text-xs font-medium text-blue-700">Pending</span>
                        <span className="text-xs text-blue-500 ml-auto">
                            {savings.decisions_pending_count}
                        </span>
                    </div>
                    <span className="text-lg font-bold text-blue-800">
                        {formatCurrency(savings.pending_savings)}
                    </span>
                </div>

                {/* Passed On */}
                <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                    <div className="flex items-center gap-1.5 mb-1">
                        <XCircle className="w-3.5 h-3.5 text-gray-500" />
                        <span className="text-xs font-medium text-gray-600">Passed On</span>
                        <span className="text-xs text-gray-400 ml-auto">
                            {savings.decisions_rejected_count}
                        </span>
                    </div>
                    <span className="text-lg font-bold text-gray-700">
                        {formatCurrency(savings.rejected_savings)}
                    </span>
                </div>
            </div>

            {/* Footer — total identified */}
            <div className="px-5 py-2.5 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
                <span className="text-xs text-gray-500">
                    Total identified: <span className="font-semibold text-gray-700">{formatCurrency(savings.total_identified)}</span>
                </span>
                {hasApprovedSavings && (
                    <span className="text-xs text-gray-400">
                        {savings.currency}
                    </span>
                )}
            </div>
        </div>
    );
};

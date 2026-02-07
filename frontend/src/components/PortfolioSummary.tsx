import React from 'react';
import { DecisionSummary } from '../services/api';
import { DollarSign, Activity, BarChart3 } from 'lucide-react';

interface PortfolioSummaryProps {
    summary: DecisionSummary | null;
    isLoading: boolean;
}

export const PortfolioSummary: React.FC<PortfolioSummaryProps> = ({ summary, isLoading }) => {
    if (isLoading || !summary) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8 animate-pulse">
                {[1, 2, 3].map((i) => (
                    <div key={i} className="h-32 bg-gray-200 rounded-xl"></div>
                ))}
            </div>
        );
    }

    const formatMoney = (val: number) => {
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);
    };

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            {/* Total Opportunity */}
            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col justify-between">
                <div className="flex items-center gap-3 text-gray-500 mb-2">
                    <div className="p-2 bg-brand-50 rounded-lg">
                        <DollarSign className="w-5 h-5 text-brand-600" />
                    </div>
                    <span className="text-sm font-medium uppercase tracking-wide">Total Opportunity</span>
                </div>
                <div>
                    <span className="text-3xl font-bold text-gray-900 block mb-1">
                        {formatMoney(summary.total_savings)}
                    </span>
                    <span className="text-sm text-gray-500">Annualized Savings</span>
                </div>
            </div>

            {/* Impact Breakdown */}
            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col justify-between">
                <div className="flex items-center gap-3 text-gray-500 mb-2">
                    <div className="p-2 bg-purple-50 rounded-lg">
                        <Activity className="w-5 h-5 text-purple-600" />
                    </div>
                    <span className="text-sm font-medium uppercase tracking-wide">High Impact</span>
                </div>
                <div className="flex items-end gap-2">
                    <span className="text-3xl font-bold text-gray-900">
                        {summary.pending_high_impact}
                    </span>
                    <span className="text-sm text-gray-500 mb-1">Decisions Pending</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-1.5 mt-3">
                    <div
                        className="bg-purple-600 h-1.5 rounded-full"
                        style={{ width: `${summary.pending_count > 0 ? (summary.pending_high_impact / summary.pending_count) * 100 : 0}%` }}
                    ></div>
                </div>
            </div>

            {/* Decision Status */}
            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col justify-between">
                <div className="flex items-center gap-3 text-gray-500 mb-2">
                    <div className="p-2 bg-blue-50 rounded-lg">
                        <BarChart3 className="w-5 h-5 text-blue-600" />
                    </div>
                    <span className="text-sm font-medium uppercase tracking-wide">Pending Actions</span>
                </div>
                <div className="flex items-end gap-2">
                    <span className="text-3xl font-bold text-gray-900">
                        {summary.pending_count}
                    </span>
                    <span className="text-sm text-gray-500 mb-1">Actions Required</span>
                </div>
                <div className="flex gap-2 mt-3 text-xs">
                    <span className="px-2 py-1 bg-gray-100 rounded text-gray-600">
                        {summary.risk_breakdown['LOW'] || 0} Low Risk
                    </span>
                    <span className="px-2 py-1 bg-yellow-50 rounded text-yellow-700">
                        {summary.impact_breakdown['MEDIUM'] || 0} Med Impact
                    </span>
                </div>
            </div>
        </div>
    );
};

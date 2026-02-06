import React, { useState } from 'react';
import { clsx } from 'clsx';

import { Decision, DecisionService } from '../services/api';
import { RiskBadge } from './RiskBadge';
import { ArrowRight, Check, X, Loader2, DollarSign } from 'lucide-react';

interface DecisionCardProps {
    decision: Decision;
    onUpdate: () => void;
}

export const DecisionCard: React.FC<DecisionCardProps> = ({ decision, onUpdate }) => {
    const [processing, setProcessing] = useState(false);
    const [showRejectForm, setShowRejectForm] = useState(false);
    const [rejectReason, setRejectReason] = useState('');

    const handleApprove = async () => {
        if (!confirm('Confirm approval? This will log an audit entry.')) return;
        setProcessing(true);
        try {
            await DecisionService.approve(decision.id);
            onUpdate();
        } catch (e) {
            alert('Failed to approve');
        } finally {
            setProcessing(false);
        }
    };

    const handleReject = async () => {
        if (!rejectReason) return;
        setProcessing(true);
        try {
            await DecisionService.reject(decision.id, rejectReason);
            onUpdate();
        } catch (e) {
            alert('Failed to reject');
        } finally {
            setProcessing(false);
        }
    };

    const formatMoney = (val: number) => {
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(Math.abs(val));
    };

    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 transition-all hover:shadow-md">
            {/* Header */}
            <div className="flex justify-between items-start mb-4">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-bold text-gray-500 tracking-wider uppercase">{decision.scope}</span>
                        <RiskBadge level={decision.risk_level} />
                    </div>
                    <h3 className="text-xl font-bold text-gray-900">{decision.recommended_action}</h3>
                </div>
                <div className="text-right">
                    <p className="text-sm text-gray-500">Monthly Impact</p>
                    <p className="text-lg font-bold text-green-600">+{formatMoney(decision.expected_monthly_impact)}</p>
                </div>
            </div>

            {/* Rationale */}
            <div className="mb-6 bg-slate-50 p-4 rounded-lg border border-slate-100">
                <h4 className="text-sm font-semibold text-gray-700 mb-1">Why this?</h4>
                <p className="text-gray-600 text-sm leading-relaxed">{decision.explanation}</p>

                <div className="mt-3 flex gap-4 text-sm">
                    <div>
                        <span className="text-gray-500 block text-xs">Worst Case Risk</span>
                        <span className="font-medium text-red-600">{formatMoney(decision.risk_range.worst_case)}</span>
                    </div>
                    <div>
                        <span className="text-gray-500 block text-xs">Cost of Inaction (1yr)</span>
                        <span className="font-medium text-gray-900">{formatMoney(decision.cost_of_inaction)}</span>
                    </div>
                </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end items-center gap-3">
                {decision.status === 'PENDING' ? (
                    !showRejectForm ? (
                        <>
                            <button
                                onClick={() => setShowRejectForm(true)}
                                disabled={processing}
                                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg border border-transparent hover:border-gray-200 transition-colors"
                            >
                                <X className="w-4 h-4" /> Reject
                            </button>
                            <button
                                onClick={handleApprove}
                                disabled={processing}
                                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-brand-600 hover:bg-brand-700 rounded-lg shadow-sm transition-colors"
                            >
                                {processing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                                Approve Recommendation
                            </button>
                        </>
                    ) : (
                        <div className="flex-1 flex gap-2 animate-in fade-in slide-in-from-right-2 duration-200">
                            <input
                                type="text"
                                placeholder="Reason for rejection (mandatory)..."
                                className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 outline-none"
                                value={rejectReason}
                                onChange={(e) => setRejectReason(e.target.value)}
                                autoFocus
                            />
                            <button
                                onClick={handleReject}
                                disabled={!rejectReason || processing}
                                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg"
                            >
                                Confirm Reject
                            </button>
                            <button
                                onClick={() => setShowRejectForm(false)}
                                className="px-3 py-2 text-sm text-gray-500 hover:bg-gray-100 rounded-lg"
                            >
                                Cancel
                            </button>
                        </div>
                    )
                ) : (
                    <div className={clsx(
                        "px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2",
                        decision.status === 'APPROVED' ? "bg-green-50 text-green-700" : "bg-gray-100 text-gray-600"
                    )}>
                        {decision.status === 'APPROVED' ? <Check className="w-4 h-4" /> : <X className="w-4 h-4" />}
                        {decision.status}
                    </div>
                )}
            </div>
        </div>
    );
};

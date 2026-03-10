import React, { useState } from 'react';
import { clsx } from 'clsx';

import { Decision, DecisionService } from '../services/api';
import { RiskBadge } from './RiskBadge';
import { ArrowRight, Check, X, Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import { usePermission } from '../hooks/usePermission';
import { formatCurrency } from '../utils/formatters';

interface DecisionCardProps {
    decision: Decision;
    onUpdate: () => void;
    onViewDetails: () => void;
}

export const DecisionCard: React.FC<DecisionCardProps> = ({ decision, onUpdate, onViewDetails }) => {
    const [processing, setProcessing] = useState(false);
    const [showRejectForm, setShowRejectForm] = useState(false);
    const [showDoubleCheck, setShowDoubleCheck] = useState(false);
    const [rejectReason, setRejectReason] = useState('');
    const hasApprovePermission = usePermission('APPROVER');

    const handleApprove = async () => {
        if (!showDoubleCheck) {
            setShowDoubleCheck(true);
            return;
        }

        setProcessing(true);
        try {
            await DecisionService.approve(decision.id);
            // Wait a moment for UX
            setTimeout(() => onUpdate(), 500);
        } catch (e) {
            alert('Failed to approve');
            setShowDoubleCheck(false);
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
                    <p className="text-lg font-bold text-green-600">+{formatCurrency(decision.expected_monthly_impact)}</p>
                </div>
            </div>

            {/* Rationale */}
            <div className="mb-6 bg-slate-50 p-4 rounded-lg border border-slate-100">
                <h4 className="text-sm font-semibold text-gray-700 mb-1">Why this?</h4>
                <p className="text-gray-600 text-sm leading-relaxed">{decision.explanation}</p>

                <div className="mt-3 flex gap-4 text-sm">
                    <div>
                        <span className="text-gray-500 block text-xs">Worst Case Risk</span>
                        <span className="font-medium text-red-600">{formatCurrency(decision.risk_range.worst_case)}</span>
                    </div>
                    <div>
                        <span className="text-gray-500 block text-xs">Cost of Inaction (1yr)</span>
                        <span className="font-medium text-gray-900">{formatCurrency(decision.cost_of_inaction)}</span>
                    </div>
                </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end items-center gap-3">
                {decision.status === 'PENDING' ? (
                    hasApprovePermission ? (
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
                                    className={clsx(
                                        "flex items-center gap-2 px-4 py-2 text-sm font-medium text-white rounded-lg shadow-sm transition-colors",
                                        processing ? "bg-brand-400 cursor-not-allowed" :
                                            showDoubleCheck ? "bg-red-600 hover:bg-red-700 animate-pulse" : "bg-brand-600 hover:bg-brand-700"
                                    )}
                                >
                                    {processing ? <Loader2 className="w-4 h-4 animate-spin" /> :
                                        showDoubleCheck ? <AlertCircle className="w-4 h-4" /> : <Check className="w-4 h-4" />}
                                    {showDoubleCheck ? "Confirm: IRREVERSIBLE" : "Approve"}
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
                                    className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg whitespace-nowrap"
                                >
                                    Confirm Reject
                                </button>
                                <button
                                    onClick={() => setShowRejectForm(false)}
                                    className="px-3 py-2 text-sm text-gray-500 hover:bg-gray-100 rounded-lg"
                                >
                                    Cancel
                                </button>
                                <span className="text-xs text-red-500 flex items-center ml-2">
                                    <AlertCircle className="w-3 h-3 mr-1" /> Irreversible
                                </span>
                            </div>
                        )
                    ) : (
                        <div className="px-4 py-2 bg-gray-50 text-gray-500 border border-gray-200 rounded-lg text-sm font-medium flex items-center gap-2 opacity-75 cursor-default">
                            <div className="w-3 h-3 rounded-full bg-yellow-400" /> Pending Approval (Read-Only)
                        </div>
                    )
                ) : (
                    <div className={clsx(
                        "px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 opacity-75 cursor-default",
                        decision.status === 'APPROVED' ? "bg-green-50 text-green-700 border border-green-100" :
                            decision.status === 'REJECTED' ? "bg-red-50 text-red-700 border border-red-100" :
                                "bg-gray-100 text-gray-600"
                    )}>
                        {decision.status === 'APPROVED' ? <CheckCircle className="w-4 h-4" /> :
                            decision.status === 'REJECTED' ? <X className="w-4 h-4" /> :
                                <div className="w-4 h-4 rounded-full bg-gray-400" />}
                        {decision.status}
                    </div>
                )}
            </div>

            <button
                onClick={onViewDetails}
                className="w-full mt-4 py-2 text-xs font-medium text-gray-400 hover:text-brand-600 hover:bg-brand-50 rounded-lg transition-colors border border-transparent hover:border-brand-100 flex items-center justify-center gap-1"
            >
                View Full Context & Audit Log <ArrowRight className="w-3 h-3" />
            </button>
        </div>
    );
};

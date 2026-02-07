import React from 'react';
import { Decision } from '../services/api';
import { X, Calendar, Hash, FileText, User } from 'lucide-react';

interface DecisionDetailProps {
    decision: Decision;
    onClose: () => void;
}

export const DecisionDetail: React.FC<DecisionDetailProps> = ({ decision, onClose }) => {
    if (!decision) return null;

    const formatDate = (dateStr: string) => {
        return new Date(dateStr).toLocaleString();
    };

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
            <div className="bg-white w-full max-w-2xl rounded-2xl shadow-2xl max-h-[90vh] overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-200">

                {/* Header */}
                <div className="p-6 border-b border-gray-100 flex justify-between items-start bg-gray-50/50">
                    <div>
                        <div className="flex gap-2 mb-2">
                            <span className="px-2 py-0.5 rounded text-xs font-bold bg-gray-200 text-gray-600 uppercase tracking-wide">
                                {decision.decision_type}
                            </span>
                            <span className="px-2 py-0.5 rounded text-xs font-bold bg-gray-200 text-gray-600 uppercase tracking-wide">
                                {decision.scope}
                            </span>
                        </div>
                        <h2 className="text-2xl font-bold text-gray-900 leading-tight">
                            {decision.recommended_action}
                        </h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-gray-200 rounded-full transition-colors"
                    >
                        <X className="w-5 h-5 text-gray-500" />
                    </button>
                </div>

                {/* Rejection Alert */}
                {decision.status === 'REJECTED' && (
                    <div className="px-6 pt-6 pb-0">
                        {(() => {
                            const lastEvent = decision.events?.slice().reverse().find(e => e.event_type === 'REJECTED');
                            return lastEvent?.note ? (
                                <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3">
                                    <div className="flex-shrink-0">
                                        <X className="w-5 h-5 text-red-600" />
                                    </div>
                                    <div>
                                        <h3 className="text-sm font-bold text-red-800 uppercase tracking-wide mb-1">
                                            Rejection Reason
                                        </h3>
                                        <p className="text-red-700 text-sm italic">
                                            "{lastEvent.note}"
                                        </p>
                                    </div>
                                </div>
                            ) : null;
                        })()}
                    </div>
                )}

                <div className="overflow-y-auto p-6 space-y-8">

                    {/* Context Section */}
                    {decision.context && (
                        <section>
                            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-3 flex items-center gap-2">
                                <Hash className="w-4 h-4 text-gray-400" /> Decision Context
                            </h3>
                            <div className="bg-slate-50 rounded-xl p-4 border border-slate-100 grid grid-cols-2 gap-4">
                                <div>
                                    <span className="text-xs text-gray-500 block mb-1">Analysis Period</span>
                                    <span className="text-sm font-medium text-gray-900 block">{decision.context.analysis_period}</span>
                                </div>
                                <div>
                                    <span className="text-xs text-gray-500 block mb-1">Applied Rule ID</span>
                                    <span className="text-sm font-medium text-gray-900 font-mono block">{decision.context.rule_id}</span>
                                </div>
                                {Object.entries(decision.context.metrics).map(([key, value]) => (
                                    <div key={key}>
                                        <span className="text-xs text-gray-500 block mb-1 capitalize">{key.replace(/_/g, ' ')}</span>
                                        <span className="text-sm font-medium text-gray-900 block">
                                            {typeof value === 'number' && key.includes('spend')
                                                ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)
                                                : value
                                            }
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </section>
                    )}

                    {/* Explanation */}
                    <section>
                        <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-2 flex items-center gap-2">
                            <FileText className="w-4 h-4 text-gray-400" /> Rationale
                        </h3>
                        <p className="text-gray-600 leading-relaxed text-sm">
                            {decision.explanation}
                        </p>
                    </section>

                    {/* Audit Log */}
                    {decision.events && decision.events.length > 0 && (
                        <section>
                            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-4 flex items-center gap-2">
                                <Calendar className="w-4 h-4 text-gray-400" /> Audit Trail
                            </h3>
                            <div className="relative border-l-2 border-gray-100 ml-2 space-y-6">
                                {decision.events.map((event) => (
                                    <div key={event.id} className="ml-6 relative">
                                        {/* Timeline Dot */}
                                        <div className={`absolute -left-[31px] top-0 w-4 h-4 rounded-full border-2 border-white shadow-sm
                                            ${event.event_type === 'APPROVED' ? 'bg-green-500' :
                                                event.event_type === 'REJECTED' ? 'bg-red-500' : 'bg-gray-300'}
                                        `} />

                                        <div className="bg-white border border-gray-100 rounded-lg p-3 shadow-sm hover:shadow-md transition-shadow">
                                            <div className="flex justify-between items-start mb-1">
                                                <span className={`text-xs font-bold px-2 py-0.5 rounded
                                                    ${event.event_type === 'APPROVED' ? 'bg-green-100 text-green-700' :
                                                        event.event_type === 'REJECTED' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600'}
                                                `}>
                                                    {event.event_type}
                                                </span>
                                                <span className="text-xs text-gray-400 font-mono">
                                                    {formatDate(event.created_at)}
                                                </span>
                                            </div>

                                            {event.note && (
                                                <p className="text-sm text-gray-700 mt-2 bg-gray-50 p-2 rounded border border-gray-100 italic">
                                                    "{event.note}"
                                                </p>
                                            )}

                                            <div className="mt-2 flex items-center gap-1 text-xs text-gray-400">
                                                <User className="w-3 h-3" />
                                                Action by: <span className="font-medium text-gray-600">{event.actor_id}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </section>
                    )}
                </div>

                <div className="p-4 border-t border-gray-100 bg-gray-50/50 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
};

import React, { useEffect, useState } from 'react';
import { Decision, DecisionService, DecisionSummary, ExportService } from '../services/api';
import { DecisionCard } from '../components/DecisionCard';
import { DecisionDetail } from '../components/DecisionDetail';
import { PortfolioSummary } from '../components/PortfolioSummary';
import { UploadDataButton } from '../components/UploadDataButton';
import { RefreshCw, Filter, CheckCircle, Shield, Download } from 'lucide-react';
import { Link } from 'react-router-dom';

export const DecisionsPage: React.FC = () => {
    const [decisions, setDecisions] = useState<Decision[]>([]);
    const [summary, setSummary] = useState<DecisionSummary | null>(null);
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [viewMode, setViewMode] = useState<'pending' | 'history'>('pending');

    const selectedDecision = decisions.find(d => d.id === selectedId) || null;

    const pendingDecisions = decisions.filter(d => d.status === 'PENDING');
    const historyDecisions = decisions.filter(d => d.status !== 'PENDING');

    const displayedDecisions = viewMode === 'pending' ? pendingDecisions : historyDecisions;
    const pendingCount = pendingDecisions.length;
    const historyCount = historyDecisions.length;

    const loadData = async () => {
        setLoading(true);
        try {
            const [data, summaryData] = await Promise.all([
                DecisionService.getDecisions(),
                DecisionService.getSummary()
            ]);
            setDecisions(data);
            setSummary(summaryData);
        } catch (e) {
            console.error('Failed to load data', e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    return (
        <div className="max-w-5xl mx-auto px-4 py-8">
            <header className="mb-8 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Decision Inbox</h1>
                    <p className="text-gray-500 mt-1">AI-Recommended Capital Allocation Actions</p>
                </div>
                <div className="flex gap-3">
                    <Link
                        to="/exposure"
                        className="flex items-center gap-2 px-3 py-2 bg-orange-50 text-orange-700 border border-orange-200 rounded-lg hover:bg-orange-100 transition-colors text-sm font-medium"
                    >
                        <Shield className="w-4 h-4" />
                        Exposure
                    </Link>
                    <button
                        onClick={() => ExportService.downloadExecutiveReport()}
                        className="flex items-center gap-2 px-3 py-2 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-lg hover:bg-emerald-100 transition-colors text-sm font-medium"
                    >
                        <Download className="w-4 h-4" />
                        Export
                    </button>
                    <UploadDataButton onUploadComplete={loadData} />
                    <button
                        onClick={loadData}
                        className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
                        title="Refresh Data"
                    >
                        <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </header>

            {/* Portfolio Summary Dashboard */}
            <PortfolioSummary summary={summary} isLoading={loading} />

            <h2 className="text-lg font-semibold text-gray-800">
                {viewMode === 'pending' ? `Pending Decisions (${pendingCount})` : `Decision History (${historyCount})`}
            </h2>
            <div className="flex bg-gray-100 p-1 rounded-lg">
                <button
                    onClick={() => setViewMode('pending')}
                    className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${viewMode === 'pending' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
                        }`}
                >
                    Pending
                </button>
                <button
                    onClick={() => setViewMode('history')}
                    className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${viewMode === 'history' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
                        }`}
                >
                    History
                </button>
            </div>

            {loading ? (
                <div className="space-y-4 mt-8">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="h-48 bg-gray-100 rounded-xl animate-pulse" />
                    ))}
                </div>
            ) : (
                <div className="space-y-4 mt-8">
                    {displayedDecisions.length > 0 ? (
                        displayedDecisions.map((decision) => (
                            <DecisionCard
                                key={decision.id}
                                decision={decision}
                                onUpdate={loadData}
                                onViewDetails={() => setSelectedId(decision.id)}
                            />
                        ))
                    ) : (
                        <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
                            {viewMode === 'pending' ? (
                                <>
                                    <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
                                    <h3 className="text-lg font-medium text-gray-900">All Caught Up!</h3>
                                    <p className="text-gray-500">No pending decisions found.</p>
                                </>
                            ) : (
                                <>
                                    <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3 text-gray-400">
                                        <Filter className="w-6 h-6" />
                                    </div>
                                    <h3 className="text-lg font-medium text-gray-900">No History Yet</h3>
                                    <p className="text-gray-500">Decisions you process will appear here.</p>
                                </>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* Detail Modal */}
            {selectedDecision && (
                <DecisionDetail
                    decision={selectedDecision}
                    onClose={() => setSelectedId(null)}
                />
            )}
        </div >
    );
};

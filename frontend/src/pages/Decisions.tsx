import React, { useEffect, useState } from 'react';
import { Decision, DecisionService, DecisionSummary, ExportService, DemoService } from '../services/api';
import { DecisionCard } from '../components/DecisionCard';
import { DecisionDetail } from '../components/DecisionDetail';
import { PortfolioSummary } from '../components/PortfolioSummary';
import { SavingsTracker } from '../components/SavingsTracker';
import { TrendAlerts } from '../components/TrendAlerts';
import { UploadDataButton } from '../components/UploadDataButton';
import { RefreshCw, Filter, CheckCircle, Shield, Download, AlertTriangle, X, Loader2, Info, Upload } from 'lucide-react';
import { Link } from 'react-router-dom';
import { sampleData } from '../data/sampleData';

export const DecisionsPage: React.FC = () => {
    const [decisions, setDecisions] = useState<Decision[]>([]);
    const [summary, setSummary] = useState<DecisionSummary | null>(null);
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [viewMode, setViewMode] = useState<'pending' | 'history'>('pending');
    const [isDemoMode, setIsDemoMode] = useState(false);
    const [exportLoading, setExportLoading] = useState(false);
    const [exportError, setExportError] = useState<string | null>(null);
    const [demoBannerDismissed, setDemoBannerDismissed] = useState(false);
    const [savingsRefreshKey, setSavingsRefreshKey] = useState(0);

    const selectedDecision = decisions.find(d => d.id === selectedId) || null;

    const pendingDecisions = decisions.filter(d => d.status === 'PENDING');
    const historyDecisions = decisions.filter(d => d.status !== 'PENDING');

    const displayedDecisions = viewMode === 'pending' ? pendingDecisions : historyDecisions;
    const pendingCount = pendingDecisions.length;
    const historyCount = historyDecisions.length;

    const loadData = async () => {
        setLoading(true);
        setSavingsRefreshKey(k => k + 1);
        try {
            const [data, summaryData] = await Promise.all([
                DecisionService.getDecisions(),
                DecisionService.getSummary()
            ]);

            if (data.length === 0) {
                // No data — auto-load demo
                try {
                    await DemoService.loadDemo();
                    // Refetch after demo load
                    const [demoData, demoSummary] = await Promise.all([
                        DecisionService.getDecisions(),
                        DecisionService.getSummary()
                    ]);
                    setDecisions(demoData.length > 0 ? demoData : sampleData);
                    setSummary(demoSummary);
                    setIsDemoMode(true);
                    setDemoBannerDismissed(false);
                } catch {
                    // Demo load failed — fall back to client-side sample data
                    setDecisions(sampleData);
                    setIsDemoMode(true);
                    setDemoBannerDismissed(false);
                }
            } else {
                setDecisions(data);
                setIsDemoMode(false);
            }
            if (data.length > 0) {
                setSummary(summaryData);
            }
        } catch (e) {
            console.error('Failed to load data', e);
        } finally {
            setLoading(false);
        }
    };

    const handleExport = async () => {
        setExportLoading(true);
        setExportError(null);
        try {
            await ExportService.downloadExecutiveReport();
        } catch (e) {
            console.error('Export failed', e);
            setExportError('Export failed — please try again');
            setTimeout(() => setExportError(null), 5000);
        } finally {
            setExportLoading(false);
        }
    };

    useEffect(() => {
        const storedVendor = localStorage.getItem('selectedVendor');
        if (storedVendor && /^Vendor_\d+/.test(storedVendor)) {
            localStorage.removeItem('selectedVendor');
        }
        loadData();
    }, []);

    return (
        <div className="max-w-5xl mx-auto px-4 py-8">
            {/* Export Error Banner */}
            {exportError && (
                <div className="mb-6 bg-red-50 border-l-4 border-red-400 p-4 rounded-md flex justify-between items-center shadow-sm">
                    <div className="flex items-center">
                        <AlertTriangle className="h-5 w-5 text-red-400 mr-3" />
                        <span className="text-sm font-medium text-red-800">{exportError}</span>
                    </div>
                    <button
                        onClick={() => setExportError(null)}
                        className="text-red-500 hover:text-red-600 focus:outline-none"
                    >
                        <X className="h-4 w-4" />
                    </button>
                </div>
            )}

            {/* Demo Mode Banner */}
            {isDemoMode && !demoBannerDismissed && (
                <div className="mb-6 bg-blue-50 border-l-4 border-blue-400 p-4 rounded-md flex justify-between items-start shadow-sm">
                    <div className="flex items-start">
                        <Info className="h-5 w-5 text-blue-500 mt-0.5 mr-3 flex-shrink-0" />
                        <div>
                            <h3 className="text-sm font-medium text-blue-800">You are viewing demo data</h3>
                            <p className="mt-1 text-sm text-blue-700">
                                Upload your own file to analyze real vendor spend.
                            </p>
                            <Link
                                to="/upload"
                                className="mt-2 inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 text-white text-xs font-medium rounded-md hover:bg-blue-700 transition-colors"
                            >
                                <Upload className="w-3.5 h-3.5" />
                                Upload Now
                            </Link>
                        </div>
                    </div>
                    <button
                        onClick={() => setDemoBannerDismissed(true)}
                        className="text-blue-400 hover:text-blue-600 focus:outline-none"
                    >
                        <X className="h-5 w-5" />
                    </button>
                </div>
            )}

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
                        onClick={handleExport}
                        disabled={exportLoading}
                        className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-sm font-medium ${
                            exportLoading
                                ? 'bg-emerald-100 text-emerald-400 border border-emerald-200 cursor-not-allowed'
                                : 'bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100'
                        }`}
                    >
                        {exportLoading ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                            <Download className="w-4 h-4" />
                        )}
                        {exportLoading ? 'Generating...' : 'Export Board Report'}
                    </button>
                    <UploadDataButton onUploadComplete={async () => {
                        setDecisions([]);
                        setSelectedId(null);
                        setIsDemoMode(false);
                        setDemoBannerDismissed(false);
                        await loadData();
                        setSavingsRefreshKey(k => k + 1);
                    }} />
                    <button
                        onClick={loadData}
                        className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
                        title="Refresh Data"
                    >
                        <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </header>

            {/* Savings Tracker — below demo banner, above KPI cards */}
            <SavingsTracker refreshKey={savingsRefreshKey} />

            {/* Trend Alerts — above dashboard if any exist */}
            <TrendAlerts />

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

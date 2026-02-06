import React, { useEffect, useState } from 'react';
import { Decision, DecisionService } from '../services/api';
import { DecisionCard } from '../components/DecisionCard';
import { LayoutDashboard, Loader2, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';

export const DecisionsPage: React.FC = () => {
    const [decisions, setDecisions] = useState<Decision[]>([]);
    const [loading, setLoading] = useState(true);

    const loadData = async () => {
        setLoading(true);
        try {
            const data = await DecisionService.getDecisions();
            setDecisions(data);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    // Helper: Sort pending first
    const sortedDecisions = [...decisions].sort((a, b) => {
        if (a.status === 'PENDING' && b.status !== 'PENDING') return -1;
        if (a.status !== 'PENDING' && b.status === 'PENDING') return 1;
        return 0;
    });

    const pendingCount = decisions.filter(d => d.status === 'PENDING').length;

    return (
        <div className="max-w-4xl mx-auto py-10 px-4">
            <header className="flex justify-between items-center mb-10">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Decision Inbox</h1>
                    <p className="text-gray-500 mt-1">
                        You have <span className="font-semibold text-brand-600">{pendingCount} pending decisions</span> requiring attention.
                    </p>
                </div>
                <div className="flex gap-3">
                    <Link to="/upload" className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                        Upload Data
                    </Link>
                    <button onClick={loadData} className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition-colors">
                        <RefreshCw className="w-5 h-5" />
                    </button>
                </div>
            </header>

            {loading ? (
                <div className="flex justify-center py-20">
                    <Loader2 className="w-8 h-8 animate-spin text-gray-300" />
                </div>
            ) : (
                <div className="space-y-6">
                    {sortedDecisions.map(d => (
                        <DecisionCard key={d.id} decision={d} onUpdate={loadData} />
                    ))}

                    {decisions.length === 0 && (
                        <div className="text-center py-20 bg-white rounded-xl border border-dashed border-gray-300">
                            <LayoutDashboard className="w-10 h-10 text-gray-300 mx-auto mb-3" />
                            <p className="text-gray-500">No decisions generated yet.</p>
                            <Link to="/upload" className="text-brand-600 font-medium hover:underline text-sm mt-2 block">Upload data to start</Link>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

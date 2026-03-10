import React, { useEffect, useState } from 'react';
import { FinancialExposure, ExposureService } from '../services/api';
import { Shield, TrendingUp, AlertTriangle } from 'lucide-react';
import { formatCurrency, formatPct } from '../utils/formatters';

interface ExposurePanelProps {
    vendorId: string;
}

export const ExposurePanel: React.FC<ExposurePanelProps> = ({ vendorId }) => {
    const [exposure, setExposure] = useState<FinancialExposure | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchExposure = async () => {
            setLoading(true);
            setError(null);
            try {
                const data = await ExposureService.getVendorExposure(vendorId);
                setExposure(data);
            } catch (e: any) {
                setError(e?.response?.data?.detail || 'Failed to load exposure data');
            } finally {
                setLoading(false);
            }
        };
        fetchExposure();
    }, [vendorId]);

    if (loading) {
        return (
            <div className="bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl p-4 animate-pulse">
                <div className="h-4 bg-slate-200 rounded w-1/3 mb-3"></div>
                <div className="h-6 bg-slate-200 rounded w-1/2"></div>
            </div>
        );
    }

    if (error || !exposure) {
        return (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-600">
                <AlertTriangle className="w-4 h-4 inline mr-1" />
                {error || 'No exposure data available'}
            </div>
        );
    }

    return (
        <section>
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-3 flex items-center gap-2">
                <Shield className="w-4 h-4 text-orange-500" /> Financial Exposure
            </h3>
            <div className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-xl p-4 border border-orange-100 space-y-4">
                {/* Top KPIs */}
                <div className="grid grid-cols-3 gap-3">
                    <div>
                        <span className="text-xs text-gray-500 block mb-0.5">Annual Spend</span>
                        <span className="text-lg font-bold text-gray-900">{formatCurrency(exposure.annual_spend)}</span>
                    </div>
                    <div>
                        <span className="text-xs text-gray-500 block mb-0.5">Category Share</span>
                        <span className="text-lg font-bold text-gray-900">{formatPct(exposure.vendor_share_pct)}</span>
                    </div>
                    <div>
                        <span className="text-xs text-gray-500 block mb-0.5">Worst Case</span>
                        <span className="text-lg font-bold text-red-600">{formatCurrency(exposure.worst_case_exposure)}</span>
                    </div>
                </div>

                {/* Shock Impact Table */}
                <div className="bg-white/60 rounded-lg p-3 border border-orange-100">
                    <div className="flex items-center gap-1 mb-2 text-xs font-semibold text-gray-700 uppercase tracking-wide">
                        <TrendingUp className="w-3 h-3" /> Price Shock Impact
                    </div>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                        <div className="space-y-1">
                            <span className="text-xs text-gray-500 block">10% Shock</span>
                            <span className="font-semibold text-orange-700">{formatCurrency(exposure.price_shock_impact_10pct)}</span>
                            <span className="text-xs text-gray-500 block">EBITDA Δ: <span className="text-red-600 font-medium">{formatCurrency(exposure.estimated_ebitda_delta_10pct)}</span></span>
                        </div>
                        <div className="space-y-1">
                            <span className="text-xs text-gray-500 block">20% Shock</span>
                            <span className="font-semibold text-red-700">{formatCurrency(exposure.price_shock_impact_20pct)}</span>
                            <span className="text-xs text-gray-500 block">EBITDA Δ: <span className="text-red-600 font-medium">{formatCurrency(exposure.estimated_ebitda_delta_20pct)}</span></span>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};

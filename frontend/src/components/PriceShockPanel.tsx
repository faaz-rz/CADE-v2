import React, { useState, useCallback } from 'react';
import { PriceShockResponse, SimulationService } from '../services/api';
import { Zap, ArrowRight, TrendingDown } from 'lucide-react';

interface PriceShockPanelProps {
    vendorId: string;
}

const PRESET_SHOCKS = [5, 10, 15];

export const PriceShockPanel: React.FC<PriceShockPanelProps> = ({ vendorId }) => {
    const [shockPct, setShockPct] = useState(10);
    const [result, setResult] = useState<PriceShockResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const runSimulation = useCallback(async (pct: number) => {
        setLoading(true);
        setError(null);
        try {
            const data = await SimulationService.runPriceShock(vendorId, pct);
            setResult(data);
        } catch (e: any) {
            setError(e?.response?.data?.detail || 'Simulation failed');
            setResult(null);
        } finally {
            setLoading(false);
        }
    }, [vendorId]);

    const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = parseFloat(e.target.value);
        setShockPct(val);
        runSimulation(val);
    };

    const handlePresetClick = (pct: number) => {
        setShockPct(pct);
        runSimulation(pct);
    };

    const fmt = (val: number) =>
        new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

    return (
        <section>
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-3 flex items-center gap-2">
                <Zap className="w-4 h-4 text-purple-500" /> Price Shock Simulator
            </h3>
            <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl p-4 border border-purple-100 space-y-4">
                {/* Preset Buttons */}
                <div className="flex gap-2">
                    {PRESET_SHOCKS.map(pct => (
                        <button
                            key={pct}
                            onClick={() => handlePresetClick(pct)}
                            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                                ${shockPct === pct
                                    ? 'bg-purple-600 text-white shadow-sm'
                                    : 'bg-white text-purple-700 border border-purple-200 hover:bg-purple-100'
                                }`}
                        >
                            +{pct}%
                        </button>
                    ))}
                </div>

                {/* Custom Slider */}
                <div className="space-y-1">
                    <div className="flex justify-between items-center">
                        <span className="text-xs text-gray-500 font-medium">Custom Shock</span>
                        <span className="text-sm font-bold text-purple-700 bg-purple-100 px-2 py-0.5 rounded">
                            +{shockPct}%
                        </span>
                    </div>
                    <input
                        type="range"
                        min={1}
                        max={50}
                        step={1}
                        value={shockPct}
                        onChange={handleSliderChange}
                        className="w-full h-2 bg-purple-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
                    />
                    <div className="flex justify-between text-[10px] text-gray-400">
                        <span>1%</span>
                        <span>25%</span>
                        <span>50%</span>
                    </div>
                </div>

                {/* Error */}
                {error && (
                    <div className="text-sm text-red-600 bg-red-50 rounded-lg p-2 border border-red-100">
                        {error}
                    </div>
                )}

                {/* Results */}
                {loading && (
                    <div className="text-center py-3">
                        <div className="w-5 h-5 border-2 border-purple-300 border-t-purple-600 rounded-full animate-spin mx-auto"></div>
                    </div>
                )}

                {result && !loading && (
                    <div className="bg-white/70 rounded-lg p-3 border border-purple-100 space-y-3">
                        <div className="grid grid-cols-3 gap-3 text-sm">
                            <div>
                                <span className="text-xs text-gray-500 block mb-0.5">Base Spend</span>
                                <span className="font-semibold text-gray-900">{fmt(result.base_spend)}</span>
                            </div>
                            <div className="flex items-center justify-center">
                                <ArrowRight className="w-4 h-4 text-purple-400" />
                            </div>
                            <div>
                                <span className="text-xs text-gray-500 block mb-0.5">New Spend</span>
                                <span className="font-semibold text-red-700">{fmt(result.new_spend)}</span>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-3 text-sm pt-2 border-t border-purple-100">
                            <div>
                                <span className="text-xs text-gray-500 block mb-0.5">Spend Delta</span>
                                <span className="font-bold text-orange-600 flex items-center gap-1">
                                    <TrendingDown className="w-3 h-3" />
                                    +{fmt(result.delta_spend)}
                                </span>
                            </div>
                            <div>
                                <span className="text-xs text-gray-500 block mb-0.5">EBITDA Impact</span>
                                <span className="font-bold text-red-600 text-lg">
                                    {fmt(result.estimated_ebitda_delta)}
                                </span>
                            </div>
                        </div>

                        {/* Risk Shift Badge */}
                        <div className="pt-2 border-t border-purple-100">
                            <span className="text-xs text-gray-500 block mb-1">Risk Classification</span>
                            <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold
                                ${result.risk_classification_shift.includes('ESCALATED')
                                    ? 'bg-red-100 text-red-700'
                                    : 'bg-green-100 text-green-700'
                                }`
                            }>
                                {result.risk_classification_shift}
                            </span>
                        </div>
                    </div>
                )}

                {/* Initial prompt */}
                {!result && !loading && !error && (
                    <div className="text-center py-3 text-sm text-gray-500">
                        Click a preset or drag the slider to simulate a price shock
                    </div>
                )}
            </div>
        </section>
    );
};

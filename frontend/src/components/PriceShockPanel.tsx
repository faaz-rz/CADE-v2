import React, { useState, useEffect, useCallback } from 'react';
import {
    PriceShockResponse,
    SimulationService,
    PortfolioShockResponse,
    ScenarioDefinition
} from '../services/api';
import {
    Zap, Target, TrendingDown, Layers, Briefcase, Activity, ShieldAlert, CheckCircle, RefreshCw
} from 'lucide-react';
import { formatCurrency, formatPct } from '../utils/formatters';

interface PriceShockPanelProps {
    vendorId: string; // Maintain strict compatibility for DecisionDetail.tsx
}

const PRESET_SHOCKS = [5, 10, 15, 20, 25];

export const PriceShockPanel: React.FC<PriceShockPanelProps> = ({ vendorId }) => {
    const [activeTab, setActiveTab] = useState<'single' | 'portfolio' | 'scenarios'>('single');

    // Core Single Vendor State
    const [shockPct, setShockPct] = useState(10);
    const [margin, setMargin] = useState(0.25);
    const [result, setResult] = useState<PriceShockResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Portfolio State
    const [portCategory, setPortCategory] = useState<string>('SaaS');
    const [portResult, setPortResult] = useState<PortfolioShockResponse | null>(null);
    const [portLoading, setPortLoading] = useState(false);

    // Scenarios State
    const [scenarios, setScenarios] = useState<ScenarioDefinition[]>([]);
    const [scenariosLoading, setScenariosLoading] = useState(false);
    const [activeScenario, setActiveScenario] = useState<string | null>(null);

    // Dynamic Categories State
    const [categories, setCategories] = useState<string[]>(['All Vendors']);

    // Initial Load for scenarios
    useEffect(() => {
        if (activeTab === 'scenarios' && scenarios.length === 0) {
            setScenariosLoading(true);
            SimulationService.getScenarios()
                .then(data => setScenarios(data))
                .catch(err => console.error("Failed to load scenarios", err))
                .finally(() => setScenariosLoading(false));
        }
    }, [activeTab, scenarios.length]);

    // Make sure we load the initial run for Single
    useEffect(() => {
        if (activeTab === 'single' && !result && !loading && !error) {
            runSimulation(10, 0.25);
        }

        if (activeTab === 'portfolio' && categories.length === 1) {
            import('../services/api').then(({ ExposureService }) => {
                ExposureService.getAllExposures().then(exposures => {
                    const uniqueCats = Array.from(new Set(exposures.map(e => e.category).filter(Boolean)));
                    setCategories(['All Vendors', ...uniqueCats]);
                }).catch(err => console.error("Failed to fetch exposures for categories", err));
            });
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [activeTab]);

    const runSimulation = useCallback(async (pct: number, mgn: number) => {
        if (!vendorId || /^Vendor_\d+$/.test(vendorId)) return;
        setLoading(true);
        setError(null);
        try {
            const data = await SimulationService.runPriceShock(vendorId, pct, mgn);
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
        runSimulation(val, margin);
    };

    const handlePresetClick = (pct: number) => {
        setShockPct(pct);
        runSimulation(pct, margin);
    };

    const handleMarginChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const val = parseFloat(e.target.value);
        setMargin(val);
        runSimulation(shockPct, val);
    };

    const runPortfolio = async () => {
        setPortLoading(true);
        try {
            const data = await SimulationService.runPortfolioShock({
                category: portCategory !== 'All Vendors' ? portCategory : null,
                shock_percentage: shockPct,
                ebitda_margin: margin
            });
            setPortResult(data);
        } catch (e) {
            console.error(e);
        } finally {
            setPortLoading(false);
        }
    };

    const applyScenario = async (s: ScenarioDefinition) => {
        setActiveScenario(s.id);
        setActiveTab('portfolio');
        setShockPct(s.shock_percentage);
        setMargin(s.ebitda_margin);
        setPortCategory(s.category_focus);

        setPortLoading(true);
        try {
            const data = await SimulationService.runPortfolioShock({
                category: s.category_focus !== 'All' && s.category_focus !== 'All Vendors' ? s.category_focus : null,
                shock_percentage: s.shock_percentage,
                ebitda_margin: s.ebitda_margin
            });
            setPortResult(data);
        } catch (e) {
            console.error(e);
        } finally {
            setPortLoading(false);
        }
    };

    return (
        <section className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            {/* 3-Tab Header */}
            <div className="flex border-b border-gray-100 bg-gray-50/50">
                <button
                    onClick={() => setActiveTab('single')}
                    className={`flex-1 py-3 text-sm font-medium border-b-2 flex items-center justify-center gap-2 transition-colors ${activeTab === 'single' ? 'border-purple-600 text-purple-700 bg-white' : 'border-transparent text-gray-500 hover:bg-gray-50 hover:text-gray-700'}`}
                >
                    <Zap className="w-4 h-4" /> Single Vendor
                </button>
                <button
                    onClick={() => setActiveTab('portfolio')}
                    className={`flex-1 py-3 text-sm font-medium border-b-2 flex items-center justify-center gap-2 transition-colors ${activeTab === 'portfolio' ? 'border-blue-600 text-blue-700 bg-white' : 'border-transparent text-gray-500 hover:bg-gray-50 hover:text-gray-700'}`}
                >
                    <Layers className="w-4 h-4" /> Portfolio View
                </button>
                <button
                    onClick={() => setActiveTab('scenarios')}
                    className={`flex-1 py-3 text-sm font-medium border-b-2 flex items-center justify-center gap-2 transition-colors ${activeTab === 'scenarios' ? 'border-emerald-600 text-emerald-700 bg-white' : 'border-transparent text-gray-500 hover:bg-gray-50 hover:text-gray-700'}`}
                >
                    <Briefcase className="w-4 h-4" /> Scenarios
                </button>
            </div>

            <div className="p-5 bg-gradient-to-br from-slate-50 to-white">
                {/* TAB 1: SINGLE VENDOR */}
                {activeTab === 'single' && (
                    <div className="space-y-6">
                        <div className="flex flex-col md:flex-row gap-6">
                            {/* Controls Left */}
                            <div className="md:w-1/2 space-y-5">
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-gray-500 uppercase tracking-wide">Target Shock Intensity</label>
                                    <div className="flex flex-wrap gap-2">
                                        {PRESET_SHOCKS.map(pct => (
                                            <button
                                                key={pct}
                                                onClick={() => handlePresetClick(pct)}
                                                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all shadow-sm border
                                                    ${shockPct === pct
                                                        ? 'bg-purple-600 text-white border-purple-700'
                                                        : 'bg-white text-purple-700 border-purple-200 hover:bg-purple-50'
                                                    }`}
                                            >
                                                +{pct}%
                                            </button>
                                        ))}
                                    </div>
                                    <div className="mt-4">
                                        <div className="flex justify-between items-center mb-1">
                                            <span className="text-xs text-gray-500 font-medium">Custom Range</span>
                                            <span className="text-sm font-bold text-purple-700 bg-purple-100 px-2 py-0.5 rounded">
                                                {shockPct > 0 ? '+' : ''}{shockPct}%
                                            </span>
                                        </div>
                                        <input
                                            type="range" min={1} max={50} step={1}
                                            value={shockPct}
                                            onChange={handleSliderChange}
                                            className="w-full h-2 bg-purple-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-gray-500 uppercase tracking-wide">EBITDA Margin Assumption</label>
                                    <select
                                        value={margin}
                                        onChange={handleMarginChange}
                                        className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-purple-500 shadow-sm text-gray-800"
                                    >
                                        <option value={0.10}>10% (Low Margin)</option>
                                        <option value={0.25}>25% (Standard)</option>
                                        <option value={0.40}>40% (High Margin)</option>
                                        <option value={0.65}>65% (Ultra Growth)</option>
                                    </select>
                                </div>
                            </div>

                            {/* Output Right */}
                            <div className="md:w-1/2">
                                {loading && (
                                    <div className="h-full min-h-[200px] flex items-center justify-center border border-purple-100 bg-purple-50/50 rounded-xl">
                                        <RefreshCw className="w-6 h-6 animate-spin text-purple-600" />
                                    </div>
                                )}
                                {error && (
                                    <div className="h-full min-h-[200px] flex gap-2 items-center justify-center border border-red-100 bg-red-50 rounded-xl text-red-600 p-4 text-center text-sm font-medium">
                                        {error}
                                    </div>
                                )}
                                {result && !loading && !error && (
                                    <div className="bg-white rounded-xl p-4 border border-purple-100 shadow-sm flex flex-col h-full text-sm">
                                        <div className="flex gap-2 items-center mb-4">
                                            <Activity className="w-4 h-4 text-purple-600" />
                                            <span className="font-bold text-gray-900 border-b border-gray-100 flex-1 pb-1">Impact Analysis</span>
                                        </div>
                                        <div className="grid grid-cols-2 gap-4 mb-4">
                                            <div>
                                                <span className="text-gray-500 text-xs block mb-1">New Spend Forecast</span>
                                                <span className="text-lg font-bold text-gray-900">{formatCurrency(result.new_spend)}</span>
                                            </div>
                                            <div>
                                                <span className="text-gray-500 text-xs block mb-1">Spend Growth</span>
                                                <span className="text-lg font-bold text-orange-600 flex items-center gap-1">
                                                    <TrendingDown className="w-4 h-4" /> +{formatCurrency(result.delta_spend)}
                                                </span>
                                            </div>
                                            <div className="col-span-2 bg-red-50 p-3 rounded-lg border border-red-100 flex justify-between items-center">
                                                <span className="text-red-800 font-semibold tracking-wide">EBITDA Delta</span>
                                                <span className="text-2xl font-black text-red-600">-{formatCurrency(result.estimated_ebitda_delta)}</span>
                                            </div>
                                        </div>

                                        <div className="flex justify-between items-center mb-4">
                                            <span className="text-xs text-gray-500 font-medium">Risk Assessment Shift</span>
                                            <span className={`inline-block px-3 py-1 rounded-full text-[10px] uppercase font-bold tracking-wider
                                                ${result.risk_classification_shift.includes('ESCALATED')
                                                    ? 'bg-red-100 text-red-800 border-red-200 border'
                                                    : 'bg-green-100 text-green-800 border-green-200 border'
                                                }`
                                            }>
                                                {result.risk_classification_shift}
                                            </span>
                                        </div>

                                        {/* Mitigations */}
                                        {result.mitigations && result.mitigations.length > 0 && (
                                            <div className="mt-auto border-t border-gray-100 pt-3">
                                                <span className="text-xs text-gray-500 font-bold block mb-2 uppercase">Possible Mitigations</span>
                                                <div className="space-y-2">
                                                    {result.mitigations.map((m, i) => (
                                                        <div key={i} className="flex justify-between items-center text-xs bg-gray-50 px-3 py-2 rounded-lg border border-gray-100">
                                                            <span className="font-medium text-gray-700 flex items-center gap-1.5">
                                                                <CheckCircle className="w-3 h-3 text-emerald-500" /> {m.strategy}
                                                            </span>
                                                            <span className="font-bold text-emerald-600 block">
                                                                Recovers {formatCurrency(m.estimated_savings)}
                                                            </span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}

                {/* TAB 2: PORTFOLIO VIEW */}
                {activeTab === 'portfolio' && (
                    <div className="space-y-5">
                        <div className="flex flex-col md:flex-row gap-4 items-end bg-blue-50/50 p-4 rounded-xl border border-blue-100">
                            <div className="w-full md:w-1/3">
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1 block">Category Filter</label>
                                <select
                                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 bg-white"
                                    value={portCategory}
                                    onChange={(e) => setPortCategory(e.target.value)}
                                >
                                    {categories.map(c => (
                                        <option key={c} value={c}>{c}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="w-full md:w-1/3">
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1 block">Shock (%)</label>
                                <input
                                    type="number" className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white"
                                    value={shockPct} onChange={(e) => setShockPct(parseFloat(e.target.value) || 0)}
                                />
                            </div>
                            <div className="w-full md:w-1/3">
                                <button onClick={runPortfolio} disabled={portLoading} className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition-colors flex items-center justify-center gap-2 shadow-sm">
                                    {portLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Target className="w-4 h-4" />} Simulate Portfolio Focus
                                </button>
                            </div>
                        </div>

                        {portResult && (
                            <div className="bg-white border flex flex-col items-center border-blue-100 rounded-xl p-6 shadow-sm animate-in fade-in slide-in-from-bottom-2">
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-6 w-full text-center">
                                    <div className="space-y-1">
                                        <span className="text-xs text-gray-500 font-medium uppercase block">Vendors Hit</span>
                                        <span className="text-2xl font-black text-gray-900">{portResult.affected_vendors}</span>
                                    </div>
                                    <div className="space-y-1">
                                        <span className="text-xs text-gray-500 font-medium uppercase block">Original Spend</span>
                                        <span className="text-xl font-bold text-gray-700">{formatCurrency(portResult.total_base_spend)}</span>
                                    </div>
                                    <div className="space-y-1">
                                        <span className="text-xs text-gray-500 font-medium uppercase block">New Spend</span>
                                        <span className="text-xl font-bold text-blue-700">{formatCurrency(portResult.total_new_spend)}</span>
                                    </div>
                                    <div className="space-y-1 bg-red-50 rounded-lg flex flex-col justify-center items-center shadow-inner border border-red-100 px-4 py-2">
                                        <span className="text-[10px] text-red-800 font-bold uppercase block mb-1 tracking-wider flex items-center gap-1"><ShieldAlert className="w-3 h-3" /> Mass EBITDA Impact</span>
                                        <span className="text-2xl font-black text-red-600">-{formatCurrency(portResult.total_ebitda_delta)}</span>
                                    </div>
                                </div>
                            </div>
                        )}
                        {!portResult && !portLoading && (
                            <div className="py-8 text-center text-gray-400 text-sm">
                                Define filters and click Simulate to calculate portfolio wide damage paths.
                            </div>
                        )}
                    </div>
                )}

                {/* TAB 3: MACRO SCENARIOS */}
                {activeTab === 'scenarios' && (
                    <div className="space-y-4">
                        <p className="text-sm text-gray-600 mb-4 bg-emerald-50 px-4 py-3 rounded-lg border border-emerald-100">
                            Apply predefined macro-economic events instantly to your portfolio matrix to measure structural resiliency.
                        </p>

                        {scenariosLoading ? (
                            <div className="flex items-center justify-center p-8">
                                <RefreshCw className="w-6 h-6 animate-spin text-emerald-600" />
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {scenarios.map(scen => (
                                    <div key={scen.id}
                                        onClick={() => applyScenario(scen)}
                                        className={`bg-white border rounded-xl p-5 cursor-pointer transition-all hover:shadow-md hover:border-emerald-300
                                            ${activeScenario === scen.id ? 'border-emerald-500 ring-2 ring-emerald-100' : 'border-gray-200'}
                                        `}
                                    >
                                        <div className="flex justify-between items-start mb-2">
                                            <h4 className="font-bold text-gray-900">{scen.name}</h4>
                                            <span className={`px-2 py-0.5 rounded text-xs font-bold ${scen.shock_percentage > 0 ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'}`}>
                                                {scen.shock_percentage > 0 ? '+' : ''}{scen.shock_percentage}% Shock
                                            </span>
                                        </div>
                                        <p className="text-xs text-gray-500 mb-3 min-h-[40px] leading-relaxed">
                                            {scen.description}
                                        </p>
                                        <div className="flex gap-2 text-[10px] font-medium text-gray-600 mt-auto uppercase tracking-wider">
                                            <span className="bg-gray-100 px-2 py-1 rounded">Margin: {formatPct(scen.ebitda_margin)}</span>
                                            <span className="bg-gray-100 px-2 py-1 rounded w-full truncate">Focus: {scen.category_focus}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </section>
    );
};

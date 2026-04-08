import React, { useEffect, useState } from 'react';
import { ContractService, ContractRenewal, RenewalsResponse, AMCContract } from '../services/api';
import { Calendar, AlertCircle, Clock, CheckCircle2, DollarSign, Wrench } from 'lucide-react';

const formatCurrency = (value: number): string => {
    if (value >= 1_000_000) return `₹${(value / 1_000_000).toFixed(1)}M`;
    if (value >= 1_000) return `₹${Math.round(value / 1_000).toLocaleString('en-IN')}K`;
    return `₹${Math.round(value).toLocaleString('en-IN')}`;
};

const RenewalCard: React.FC<{ renewal: ContractRenewal; urgency: 'urgent' | 'upcoming' | 'planned' }> = ({ renewal, urgency }) => {
    const colorMap = {
        urgent: {
            border: 'border-red-200',
            bg: 'bg-red-50',
            badge: 'bg-red-100 text-red-700',
            daysColor: 'text-red-700',
            icon: <AlertCircle className="w-4 h-4 text-red-500" />,
        },
        upcoming: {
            border: 'border-amber-200',
            bg: 'bg-amber-50',
            badge: 'bg-amber-100 text-amber-700',
            daysColor: 'text-amber-700',
            icon: <Clock className="w-4 h-4 text-amber-500" />,
        },
        planned: {
            border: 'border-emerald-200',
            bg: 'bg-emerald-50',
            badge: 'bg-emerald-100 text-emerald-700',
            daysColor: 'text-emerald-700',
            icon: <CheckCircle2 className="w-4 h-4 text-emerald-500" />,
        },
    };

    const colors = colorMap[urgency];

    return (
        <div className={`rounded-lg border ${colors.border} ${colors.bg} p-4 transition-shadow hover:shadow-md`}>
            <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                    {colors.icon}
                    <h4 className="text-sm font-semibold text-gray-900">{renewal.vendor_name}</h4>
                </div>
                <span className={`text-lg font-bold ${colors.daysColor}`}>
                    {renewal.days_until_renewal}d
                </span>
            </div>
            <p className="text-xs text-gray-500 mb-2">{renewal.category}</p>
            <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                    {formatCurrency(renewal.annual_spend)}/yr
                </span>
                <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${colors.badge}`}>
                    Save up to {formatCurrency(renewal.potential_savings)}
                </span>
            </div>
            <p className="text-xs text-gray-600 italic">{renewal.recommended_action}</p>
        </div>
    );
};

const AMCCard: React.FC<{ amc: AMCContract }> = ({ amc }) => {
    return (
        <div className="rounded-lg border border-indigo-200 bg-indigo-50 p-4 transition-shadow hover:shadow-md">
            <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                    <Wrench className="w-4 h-4 text-indigo-500" />
                    <h4 className="text-sm font-semibold text-gray-900">{amc.vendor_name}</h4>
                </div>
                <span className="text-xs font-bold text-indigo-700 bg-indigo-100 px-2 py-0.5 rounded-full">
                    AMC
                </span>
            </div>
            <p className="text-xs text-gray-500 mb-2">{amc.amc_type}</p>
            <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                    {formatCurrency(amc.annual_spend)}/yr
                </span>
                <div className="text-right">
                    <div className="text-xs text-gray-500">
                        Current: {amc.typical_amc_rate} → Market: {amc.market_amc_rate}
                    </div>
                    <span className="text-xs font-bold text-emerald-700">
                        Save {formatCurrency(amc.potential_saving)}/yr
                    </span>
                </div>
            </div>
            <p className="text-xs text-gray-600 mt-2 bg-white/60 p-2 rounded border border-indigo-100">
                {amc.negotiation_tip}
            </p>
        </div>
    );
};

interface BucketSectionProps {
    title: string;
    emoji: string;
    subtitle: string;
    renewals: ContractRenewal[];
    urgency: 'urgent' | 'upcoming' | 'planned';
    accentColor: string;
}

const BucketSection: React.FC<BucketSectionProps> = ({ title, emoji, subtitle, renewals, urgency, accentColor }) => {
    if (renewals.length === 0) return null;

    return (
        <div>
            <div className="flex items-center gap-2 mb-3">
                <span className="text-lg">{emoji}</span>
                <h3 className={`text-sm font-semibold ${accentColor} uppercase tracking-wide`}>{title}</h3>
                <span className="text-xs text-gray-400">{subtitle}</span>
                <span className="ml-auto text-xs font-medium text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
                    {renewals.length}
                </span>
            </div>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {renewals.map((r) => (
                    <RenewalCard key={r.vendor_name} renewal={r} urgency={urgency} />
                ))}
            </div>
        </div>
    );
};

export const ContractCalendar: React.FC = () => {
    const [data, setData] = useState<RenewalsResponse | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const result = await ContractService.getRenewals();
                setData(result);
            } catch (e) {
                console.error('Failed to load renewals', e);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    if (loading) {
        return (
            <div className="max-w-5xl mx-auto px-4 py-8">
                <div className="h-10 w-64 bg-gray-100 rounded animate-pulse mb-6" />
                <div className="space-y-4">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="h-32 bg-gray-100 rounded-xl animate-pulse" />
                    ))}
                </div>
            </div>
        );
    }

    const hasRenewals = data && data.total_renewals_90_days > 0;
    const hasAMC = data && data.amc_contracts && data.amc_contracts.length > 0;

    if (!hasRenewals && !hasAMC) {
        return (
            <div className="max-w-5xl mx-auto px-4 py-8">
                <header className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Contract Renewals</h1>
                    <p className="text-gray-500 mt-1">Upcoming vendor contract renewal windows</p>
                </header>
                <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
                    <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <h3 className="text-lg font-medium text-gray-900">No Upcoming Renewals</h3>
                    <p className="text-gray-500 mt-1">Upload vendor data to see projected contract renewal dates.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-5xl mx-auto px-4 py-8">
            <header className="mb-8 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Contract Renewals</h1>
                    <p className="text-gray-500 mt-1">Upcoming vendor contract renewal windows</p>
                </div>
                <div className="flex items-center gap-3">
                    {hasRenewals && (
                        <span className="text-sm font-medium text-gray-500 bg-gray-100 px-3 py-1.5 rounded-lg">
                            <Calendar className="w-4 h-4 inline-block mr-1.5 -mt-0.5" />
                            {data!.total_renewals_90_days} renewal{data!.total_renewals_90_days !== 1 ? 's' : ''} in 90 days
                        </span>
                    )}
                </div>
            </header>

            <div className="space-y-8">
                {data && (
                    <>
                        <BucketSection
                            title="Urgent"
                            emoji="🔴"
                            subtitle="Next 30 days"
                            renewals={data.urgent}
                            urgency="urgent"
                            accentColor="text-red-700"
                        />
                        <BucketSection
                            title="Upcoming"
                            emoji="🟡"
                            subtitle="31–60 days"
                            renewals={data.upcoming}
                            urgency="upcoming"
                            accentColor="text-amber-700"
                        />
                        <BucketSection
                            title="Planned"
                            emoji="🟢"
                            subtitle="61–90 days"
                            renewals={data.planned}
                            urgency="planned"
                            accentColor="text-emerald-700"
                        />
                    </>
                )}

                {/* AMC Section */}
                {hasAMC && (
                    <div>
                        <div className="flex items-center gap-2 mb-3">
                            <span className="text-lg">🔧</span>
                            <h3 className="text-sm font-semibold text-indigo-700 uppercase tracking-wide">Annual Maintenance Contracts</h3>
                            <span className="text-xs text-gray-400">Medical Equipment AMCs</span>
                            <span className="ml-auto text-xs font-medium text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
                                {data!.amc_contracts.length}
                            </span>
                        </div>
                        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                            {data!.amc_contracts.map((amc) => (
                                <AMCCard key={amc.vendor_name} amc={amc} />
                            ))}
                        </div>
                        {data!.amc_savings_opportunity > 0 && (
                            <div className="mt-3 text-right">
                                <span className="text-sm font-bold text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-200">
                                    {formatCurrency(data!.amc_savings_opportunity)} AMC savings opportunity
                                </span>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Bottom summary bar */}
            <div className="mt-8 bg-white rounded-xl border border-gray-200 px-5 py-4 flex items-center justify-between shadow-sm">
                <div className="flex items-center gap-2">
                    <DollarSign className="w-5 h-5 text-emerald-600" />
                    <span className="text-sm text-gray-700">
                        <span className="font-semibold">{data?.total_renewals_90_days || 0} renewal{(data?.total_renewals_90_days || 0) !== 1 ? 's' : ''}</span> in the next 90 days
                        {hasAMC && (
                            <span className="text-gray-500"> + {data!.amc_contracts.length} AMC{data!.amc_contracts.length !== 1 ? 's' : ''}</span>
                        )}
                    </span>
                </div>
                <span className="text-sm font-bold text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-200">
                    {formatCurrency((data?.total_savings_opportunity || 0) + (data?.amc_savings_opportunity || 0))} total savings opportunity
                </span>
            </div>
        </div>
    );
};

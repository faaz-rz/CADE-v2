import React, { useEffect, useState } from 'react';
import { TrendAlertsResponse, TrendService } from '../services/api';
import { AlertTriangle, TrendingUp, TrendingDown, ChevronDown, ChevronUp } from 'lucide-react';

const SEVERITY_STYLES: Record<string, { border: string; bg: string; badge: string; text: string }> = {
    HIGH: {
        border: 'border-l-red-500',
        bg: 'bg-red-50',
        badge: 'bg-red-100 text-red-700',
        text: 'text-red-600',
    },
    MEDIUM: {
        border: 'border-l-amber-500',
        bg: 'bg-amber-50',
        badge: 'bg-amber-100 text-amber-700',
        text: 'text-amber-600',
    },
    LOW: {
        border: 'border-l-gray-400',
        bg: 'bg-gray-50',
        badge: 'bg-gray-100 text-gray-600',
        text: 'text-gray-500',
    },
};

const GrowthBadge: React.FC<{ rate: number }> = ({ rate }) => {
    const isPositive = rate >= 0;
    const color = isPositive ? 'text-red-600' : 'text-green-600';
    const Icon = isPositive ? TrendingUp : TrendingDown;
    return (
        <span className={`inline-flex items-center gap-1 text-sm font-semibold ${color}`}>
            <Icon className="w-3.5 h-3.5" />
            {isPositive ? '+' : ''}{(rate * 100).toFixed(0)}%
        </span>
    );
};

export const TrendAlerts: React.FC = () => {
    const [data, setData] = useState<TrendAlertsResponse | null>(null);
    const [expanded, setExpanded] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        TrendService.getAlerts()
            .then(setData)
            .catch(() => setData(null))
            .finally(() => setLoading(false));
    }, []);

    // Don't render anything if loading, no data, or empty alerts
    if (loading || !data || data.alerts.length === 0) {
        return null;
    }

    const { alerts, high, medium } = data;

    return (
        <div className="mb-6">
            {/* Panel Header */}
            <button
                onClick={() => setExpanded(!expanded)}
                className="w-full flex items-center justify-between px-4 py-3 bg-orange-50 border border-orange-200 rounded-lg hover:bg-orange-100 transition-colors"
            >
                <div className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-orange-500" />
                    <span className="text-sm font-semibold text-orange-800">
                        {high > 0 && `${high} critical alert${high > 1 ? 's' : ''}`}
                        {high > 0 && medium > 0 && ', '}
                        {medium > 0 && `${medium} warning${medium > 1 ? 's' : ''}`}
                        {high === 0 && medium === 0 && `${data.low} notice${data.low > 1 ? 's' : ''}`}
                    </span>
                </div>
                {expanded
                    ? <ChevronUp className="w-4 h-4 text-orange-500" />
                    : <ChevronDown className="w-4 h-4 text-orange-500" />
                }
            </button>

            {/* Alert Cards */}
            {expanded && (
                <div className="mt-2 space-y-2">
                    {alerts.map((alert, i) => {
                        const style = SEVERITY_STYLES[alert.severity] || SEVERITY_STYLES.LOW;
                        return (
                            <div
                                key={`${alert.vendor}-${alert.alert_type}-${i}`}
                                className={`flex items-start justify-between p-3 rounded-lg border-l-4 ${style.border} ${style.bg} border border-gray-200`}
                            >
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                        <h4 className="text-sm font-semibold text-gray-900 truncate">{alert.title}</h4>
                                        <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${style.badge}`}>
                                            {alert.severity}
                                        </span>
                                    </div>
                                    <p className="text-xs text-gray-500 leading-relaxed">{alert.message}</p>
                                </div>
                                <div className="ml-4 flex-shrink-0">
                                    <GrowthBadge rate={alert.growth_rate} />
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

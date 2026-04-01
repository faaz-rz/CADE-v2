import React, { useEffect, useState } from 'react';
import {
    LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts';
import { TrendService, VendorTrend } from '../../services/api';
import { TrendingUp, TrendingDown, Minus, Loader2 } from 'lucide-react';

interface SpendTrendChartProps {
    vendorId: string;
    vendorName: string;
}

const formatMonth = (month: string): string => {
    const [year, m] = month.split('-');
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const idx = parseInt(m, 10) - 1;
    return `${months[idx] || m} ${year.slice(2)}`;
};

const formatCurrency = (val: number): string =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

export const SpendTrendChart: React.FC<SpendTrendChartProps> = ({ vendorId, vendorName }) => {
    const [trend, setTrend] = useState<VendorTrend | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            try {
                const data = await TrendService.getVendorTrends();
                const match = data.vendors.find(v => v.vendor_id === vendorId);
                setTrend(match || null);
            } catch (e: any) {
                setError('Failed to load trend data');
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [vendorId]);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[300px] bg-gray-50 rounded-xl border border-gray-200">
                <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
            </div>
        );
    }

    if (error || !trend || !trend.monthly_spends || trend.monthly_spends.length < 2) {
        return (
            <div className="flex items-center justify-center h-[300px] bg-gray-50 rounded-xl border border-dashed border-gray-300">
                <p className="text-gray-400 text-sm">Not enough data for trend</p>
            </div>
        );
    }

    const chartData = trend.monthly_spends.map(ms => ({
        month: formatMonth(ms.month),
        spend: ms.total_spend,
    }));

    const growth = trend.growth_pct_3m;
    let growthBadge = null;
    if (growth !== null && growth !== undefined) {
        const isNegative = growth < 0;
        const isHigh = growth > 20;
        const color = isNegative
            ? 'bg-emerald-100 text-emerald-700 border-emerald-200'
            : isHigh
                ? 'bg-red-100 text-red-700 border-red-200'
                : 'bg-gray-100 text-gray-600 border-gray-200';
        const Icon = isNegative ? TrendingDown : isHigh ? TrendingUp : Minus;

        growthBadge = (
            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-bold border ${color}`}>
                <Icon className="w-3 h-3" />
                {growth > 0 ? '+' : ''}{growth.toFixed(1)}% (3mo)
            </span>
        );
    }

    return (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
            <div className="flex items-center justify-between mb-4">
                <h4 className="text-sm font-bold text-gray-800 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-blue-500" />
                    {vendorName} — Monthly Spend
                </h4>
                {growthBadge}
            </div>
            <div style={{ height: 300, width: '100%' }}>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis
                            dataKey="month"
                            tick={{ fontSize: 11, fill: '#6b7280' }}
                            tickLine={false}
                            axisLine={{ stroke: '#e5e7eb' }}
                        />
                        <YAxis
                            tickFormatter={(val: number) => `$${(val / 1000).toFixed(0)}K`}
                            tick={{ fontSize: 11, fill: '#6b7280' }}
                            tickLine={false}
                            axisLine={{ stroke: '#e5e7eb' }}
                            width={55}
                        />
                        <Tooltip
                            formatter={(value: any) => [formatCurrency(value as number), 'Spend']}
                            labelStyle={{ color: '#374151', fontWeight: 600 }}
                            contentStyle={{
                                backgroundColor: '#fff',
                                border: '1px solid #e5e7eb',
                                borderRadius: '8px',
                                boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)',
                            }}
                        />
                        <Line
                            type="monotone"
                            dataKey="spend"
                            stroke="#2563EB"
                            strokeWidth={2.5}
                            dot={{ r: 4, fill: '#2563EB', strokeWidth: 2, stroke: '#fff' }}
                            activeDot={{ r: 6, fill: '#2563EB', stroke: '#fff', strokeWidth: 2 }}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

import React, { useEffect, useState } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, CartesianGrid
} from 'recharts';
import { ExposureService, FinancialExposure } from '../../services/api';
import { Loader2 } from 'lucide-react';

interface CategoryData {
    category: string;
    totalSpend: number;
    vendorCount: number;
    color: string;
}

const getBarColor = (spend: number): string => {
    if (spend > 500000) return '#DC2626';
    if (spend > 100000) return '#D97706';
    return '#2563EB';
};

const formatCurrency = (val: number): string =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

export const SpendCategoryChart: React.FC = () => {
    const [data, setData] = useState<CategoryData[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            try {
                const exposures = await ExposureService.getAllExposures();
                const filtered = exposures.filter((e: FinancialExposure) => !/^Vendor_\d+$/.test(e.vendor_id));

                // Group by category
                const categoryMap = new Map<string, { spend: number; count: number }>();
                for (const exp of filtered) {
                    const cat = exp.category || 'Uncategorized';
                    const existing = categoryMap.get(cat) || { spend: 0, count: 0 };
                    existing.spend += exp.annual_spend;
                    existing.count += 1;
                    categoryMap.set(cat, existing);
                }

                const categories: CategoryData[] = Array.from(categoryMap.entries())
                    .map(([category, { spend, count }]) => ({
                        category,
                        totalSpend: spend,
                        vendorCount: count,
                        color: getBarColor(spend),
                    }))
                    .sort((a, b) => b.totalSpend - a.totalSpend)
                    .slice(0, 8);

                setData(categories);
            } catch {
                // Silent fail — show empty state
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[300px] bg-gray-50 rounded-xl border border-gray-200">
                <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
            </div>
        );
    }

    if (data.length === 0) {
        return (
            <div className="flex items-center justify-center h-[300px] bg-gray-50 rounded-xl border border-dashed border-gray-300">
                <p className="text-gray-400 text-sm">No category data available</p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
            <div style={{ height: 300, width: '100%' }}>
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                        data={data}
                        layout="vertical"
                        margin={{ top: 5, right: 30, bottom: 5, left: 5 }}
                    >
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={false} />
                        <XAxis
                            type="number"
                            tickFormatter={(val: number) => `$${(val / 1000).toFixed(0)}K`}
                            tick={{ fontSize: 11, fill: '#6b7280' }}
                            tickLine={false}
                            axisLine={{ stroke: '#e5e7eb' }}
                        />
                        <YAxis
                            type="category"
                            dataKey="category"
                            tick={{ fontSize: 11, fill: '#374151', fontWeight: 500 }}
                            tickLine={false}
                            axisLine={{ stroke: '#e5e7eb' }}
                            width={120}
                        />
                        <Tooltip
                            formatter={(value: any, _name: any, props: any) => [
                                `${formatCurrency(value as number)} (${props.payload.vendorCount} vendors)`,
                                'Total Spend',
                            ]}
                            contentStyle={{
                                backgroundColor: '#fff',
                                border: '1px solid #e5e7eb',
                                borderRadius: '8px',
                                boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)',
                                fontSize: '12px',
                            }}
                        />
                        <Bar dataKey="totalSpend" radius={[0, 4, 4, 0]} barSize={20}>
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

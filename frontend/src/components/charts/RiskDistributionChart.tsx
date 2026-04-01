import React, { useEffect, useState } from 'react';
import {
    PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { DecisionService, DecisionSummary } from '../../services/api';
import { Loader2 } from 'lucide-react';

const RISK_COLORS: Record<string, string> = {
    HIGH: '#DC2626',
    MEDIUM: '#D97706',
    LOW: '#16A34A',
};

const RISK_LABELS: Record<string, string> = {
    HIGH: 'High Risk',
    MEDIUM: 'Medium Risk',
    LOW: 'Low Risk',
};

interface ChartEntry {
    name: string;
    value: number;
    color: string;
    key: string;
}

export const RiskDistributionChart: React.FC = () => {
    const [summary, setSummary] = useState<DecisionSummary | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        DecisionService.getSummary()
            .then(data => setSummary(data))
            .catch(() => {})
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[250px] bg-gray-50 rounded-xl border border-gray-200">
                <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
            </div>
        );
    }

    if (!summary) {
        return (
            <div className="flex items-center justify-center h-[250px] bg-gray-50 rounded-xl border border-dashed border-gray-300">
                <p className="text-gray-400 text-sm">No data available</p>
            </div>
        );
    }

    const data: ChartEntry[] = ['HIGH', 'MEDIUM', 'LOW']
        .filter(key => (summary.risk_breakdown[key] || 0) > 0)
        .map(key => ({
            name: RISK_LABELS[key],
            value: summary.risk_breakdown[key] || 0,
            color: RISK_COLORS[key],
            key,
        }));

    const total = data.reduce((s, d) => s + d.value, 0);

    if (total === 0) {
        return (
            <div className="flex items-center justify-center h-[250px] bg-gray-50 rounded-xl border border-dashed border-gray-300">
                <p className="text-gray-400 text-sm">No decisions to display</p>
            </div>
        );
    }

    const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, value }: any) => {
        const RADIAN = Math.PI / 180;
        const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
        const x = cx + radius * Math.cos(-midAngle * RADIAN);
        const y = cy + radius * Math.sin(-midAngle * RADIAN);
        const pct = ((value / total) * 100).toFixed(0);

        return (
            <text x={x} y={y} textAnchor="middle" dominantBaseline="central" className="text-xs font-bold fill-white">
                {value} ({pct}%)
            </text>
        );
    };

    return (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
            <div style={{ height: 250, width: '100%', position: 'relative' }}>
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={data}
                            cx="50%"
                            cy="45%"
                            innerRadius={50}
                            outerRadius={85}
                            dataKey="value"
                            labelLine={false}
                            label={renderCustomLabel}
                            strokeWidth={2}
                            stroke="#fff"
                        >
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                        </Pie>
                        <Tooltip
                            formatter={(value: any, name: any) => [
                                `${value} decisions`,
                                name,
                            ]}
                            contentStyle={{
                                backgroundColor: '#fff',
                                border: '1px solid #e5e7eb',
                                borderRadius: '8px',
                                boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)',
                                fontSize: '12px',
                            }}
                        />
                        <Legend
                            verticalAlign="bottom"
                            align="center"
                            iconType="circle"
                            iconSize={8}
                            formatter={(value: string) => (
                                <span className="text-xs text-gray-600 font-medium">{value}</span>
                            )}
                        />
                    </PieChart>
                </ResponsiveContainer>
                {/* Center label */}
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none" style={{ marginTop: '-15px' }}>
                    <div className="text-center">
                        <div className="text-2xl font-black text-gray-900">{total}</div>
                        <div className="text-[10px] text-gray-500 font-medium uppercase tracking-wide">Decisions</div>
                    </div>
                </div>
            </div>
        </div>
    );
};

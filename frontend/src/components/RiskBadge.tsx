import React from 'react';
import { clsx } from 'clsx';
import { AlertTriangle, ShieldCheck, AlertOctagon } from 'lucide-react';

interface RiskBadgeProps {
    level: 'LOW' | 'MEDIUM' | 'HIGH';
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level }) => {
    const styles = {
        LOW: 'bg-green-100 text-green-700 font-bold border-green-200',
        MEDIUM: 'bg-amber-100 text-amber-700 font-bold border-amber-200',
        HIGH: 'bg-red-100 text-red-700 font-bold border-red-200',
    };

    const icons = {
        LOW: ShieldCheck,
        MEDIUM: AlertTriangle,
        HIGH: AlertOctagon,
    };

    const Icon = icons[level];

    return (
        <div className={clsx(
            'flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold border',
            styles[level]
        )}>
            <Icon className="w-3.5 h-3.5" />
            <span>{level} RISK</span>
        </div>
    );
};

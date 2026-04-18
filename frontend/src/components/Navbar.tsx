import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Stethoscope, Bell, Award, BarChart3, Calendar, Upload, Activity } from 'lucide-react';
import { AlertsService } from '../services/api';

export const Navbar: React.FC = () => {
    const location = useLocation();
    const [alertCount, setAlertCount] = useState(0);
    const [criticalCount, setCriticalCount] = useState(0);

    useEffect(() => {
        const loadAlerts = async () => {
            try {
                const data = await AlertsService.getAlerts();
                setAlertCount(data.total);
                setCriticalCount(data.critical);
            } catch { }
        };
        loadAlerts();
        const interval = setInterval(loadAlerts, 60000);
        return () => clearInterval(interval);
    }, []);

    const isActive = (path: string) =>
        location.pathname === path
            ? 'bg-white/20 text-white font-semibold'
            : 'text-teal-100 hover:text-white hover:bg-white/10';

    return (
        <nav className="bg-gradient-to-r from-teal-700 via-teal-600 to-teal-700 shadow-lg sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-16">

                {/* Left: Logo */}
                <Link to="/" className="flex items-center gap-2.5">
                    <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur">
                        <Stethoscope className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <span className="text-lg font-bold text-white tracking-tight">CADE</span>
                        <span className="ml-1.5 text-[10px] bg-white/25 text-white px-1.5 py-0.5 rounded font-semibold uppercase tracking-wider">Hospital</span>
                    </div>
                </Link>

                {/* Center: Navigation */}
                <div className="hidden md:flex items-center gap-1">
                    <Link to="/" className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-colors ${isActive('/')}`}>
                        <Activity className="w-3.5 h-3.5" />
                        Dashboard
                    </Link>
                    <Link to="/exposure" className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-colors ${isActive('/exposure')}`}>
                        <BarChart3 className="w-3.5 h-3.5" />
                        Procurement
                    </Link>
                    <Link to="/contracts" className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-colors ${isActive('/contracts')}`}>
                        <Calendar className="w-3.5 h-3.5" />
                        Renewals
                    </Link>
                    <Link to="/score" className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-colors ${isActive('/score')}`}>
                        <Award className="w-3.5 h-3.5" />
                        Score
                    </Link>
                    <Link to="/upload" className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-colors ${isActive('/upload')}`}>
                        <Upload className="w-3.5 h-3.5" />
                        Upload
                    </Link>
                </div>

                {/* Right: Alerts + Dev Mode */}
                <div className="flex items-center gap-3">
                    <Link
                        to="/alerts"
                        className="relative p-2 rounded-lg text-teal-100 hover:text-white hover:bg-white/10 transition-colors"
                        title={`${alertCount} alerts`}
                    >
                        <Bell className="w-5 h-5" />
                        {alertCount > 0 && (
                            <span className={`absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] flex items-center justify-center rounded-full text-[10px] font-bold ${criticalCount > 0
                                ? 'bg-red-500 animate-pulse'
                                : 'bg-amber-400'
                                } text-white px-1`}>
                                {alertCount > 99 ? '99+' : alertCount}
                            </span>
                        )}
                    </Link>
                    <span className="hidden sm:inline-block text-[10px] bg-cyan-500/25 text-cyan-200 px-2 py-0.5 rounded font-medium">
                        Dev Mode
                    </span>
                </div>
            </div>
        </nav>
    );
};

import { useEffect, useState } from 'react';
// import { useAuth0 } from '@auth0/auth0-react';
import { Link } from 'react-router-dom';
import { DecisionService } from '../services/api';
import { Stethoscope } from 'lucide-react';

export const Navbar = () => {
    // Auth0 commented out for local dev
    // const { isAuthenticated, loginWithRedirect, logout, user } = useAuth0();
    const [vertical, setVertical] = useState<string>('general');

    useEffect(() => {
        DecisionService.getSummary()
            .then((s) => setVertical(s.vertical || 'general'))
            .catch(() => {});
    }, []);

    return (
        <nav className="bg-white shadow-sm px-6 py-4 flex items-center justify-between border-b border-gray-200">
            <div className="flex items-center space-x-6">
                <Link to="/" className="flex flex-col">
                    <div className="flex items-center gap-2">
                        <span className="text-xl font-semibold text-gray-900">CADE</span>
                        {vertical === 'hospital' && (
                            <span className="inline-flex items-center gap-1 text-[10px] font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded-full border border-teal-200 uppercase tracking-wide">
                                <Stethoscope className="w-3 h-3" />
                                Hospital
                            </span>
                        )}
                    </div>
                    <span className="text-xs text-gray-400 -mt-0.5">
                        {vertical === 'hospital' ? 'Hospital Procurement Intelligence' : 'Capital Allocation Decision Engine'}
                    </span>
                </Link>
                <div className="hidden md:flex space-x-4">
                    <Link to="/" className="text-gray-600 hover:text-gray-900">Decisions</Link>
                    <Link to="/upload" className="text-gray-600 hover:text-gray-900">Upload</Link>
                    <Link to="/exposure" className="text-gray-600 hover:text-gray-900">Exposure</Link>
                    <Link to="/contracts" className="text-gray-600 hover:text-gray-900">Renewals</Link>
                </div>
            </div>

            <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600 font-medium">Dev Mode</span>
                <span className="text-xs px-2 py-1 bg-indigo-100 text-indigo-700 rounded-full font-mono uppercase border border-indigo-200">
                    ADMIN
                </span>
            </div>
        </nav>
    );
};

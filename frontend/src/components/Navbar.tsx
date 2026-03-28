import { useAuth0 } from '@auth0/auth0-react';
import { Link } from 'react-router-dom';

export const Navbar = () => {
    const { isAuthenticated, loginWithRedirect, logout, user } = useAuth0();

    return (
        <nav className="bg-white shadow-sm px-6 py-4 flex items-center justify-between border-b border-gray-200">
            <div className="flex items-center space-x-6">
                <Link to="/" className="flex flex-col">
                    <span className="text-xl font-semibold text-gray-900">CADE</span>
                    <span className="text-xs text-gray-400 -mt-0.5">Capital Allocation Decision Engine</span>
                </Link>
                {isAuthenticated && (
                    <div className="hidden md:flex space-x-4">
                        <Link to="/" className="text-gray-600 hover:text-gray-900">Decisions</Link>
                        <Link to="/upload" className="text-gray-600 hover:text-gray-900">Upload</Link>
                        <Link to="/exposure" className="text-gray-600 hover:text-gray-900">Exposure</Link>
                        <Link to="/contracts" className="text-gray-600 hover:text-gray-900">Renewals</Link>
                    </div>
                )}
            </div>

            <div className="flex items-center space-x-4">
                {isAuthenticated ? (
                    <>
                        <span className="text-sm text-gray-600 font-medium">
                            {user?.email}
                        </span>
                        
                        {/* Role Override Toggle for Admins */}
                        {user?.['https://capitalrisk.app/role'] === 'ADMIN' && (
                            <button
                                onClick={() => {
                                    const currentOverride = localStorage.getItem('demo_role_override');
                                    if (currentOverride === 'ANALYST') {
                                        localStorage.removeItem('demo_role_override');
                                    } else {
                                        localStorage.setItem('demo_role_override', 'ANALYST');
                                    }
                                    window.dispatchEvent(new Event('storage')); // trigger update if needed, though react state is better. For this simple app, page reload or state update is fine.
                                    window.location.reload();
                                }}
                                className="text-xs px-2 py-1 bg-indigo-100 text-indigo-700 hover:bg-indigo-200 rounded-full font-mono uppercase cursor-pointer border border-indigo-200 transition-colors flex flex-col items-center leading-none"
                                title="Click to toggle view"
                            >
                                <span className="opacity-70 text-[10px] uppercase font-bold tracking-wider mb-0.5 mt-0.5">Viewing As</span>
                                <span>{localStorage.getItem('demo_role_override') === 'ANALYST' ? 'ANALYST' : 'ADMIN'}</span>
                            </button>
                        )}
                        
                        {user?.['https://capitalrisk.app/role'] !== 'ADMIN' && (
                            <span className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full font-mono uppercase">
                                {user?.['https://capitalrisk.app/role'] || 'VIEWER'}
                            </span>
                        )}

                        <button
                            onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
                            className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium px-4 py-2 rounded transition-colors text-sm"
                        >
                            Log Out
                        </button>
                    </>
                ) : (
                    <button
                        onClick={() => loginWithRedirect()}
                        className="bg-brand-600 hover:bg-brand-700 text-white font-medium px-4 py-2 rounded shadow-sm transition-colors text-sm"
                    >
                        Log In
                    </button>
                )}
            </div>
        </nav>
    );
};

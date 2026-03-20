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
                    </div>
                )}
            </div>

            <div className="flex items-center space-x-4">
                {isAuthenticated ? (
                    <>
                        <span className="text-sm text-gray-600 font-medium">
                            {user?.email}
                        </span>
                        <span className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full font-mono uppercase">
                            {user?.['https://capitalrisk.app/role'] || 'VIEWER'}
                        </span>
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

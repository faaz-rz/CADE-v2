import { useEffect, useRef } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import { DecisionsPage } from './pages/Decisions';
import { UploadPage } from './pages/Upload';
import { ExposureDashboard } from './pages/ExposureDashboard';
import { ContractsPage } from './pages/Contracts';
import { Navbar } from './components/Navbar';
import { setAuthTokenGetter } from './services/api';

function App() {
    const { isAuthenticated, isLoading, loginWithRedirect, getAccessTokenSilently, error } = useAuth0();
    const hasRedirected = useRef(false);

    // Register the token getter so all API calls get Bearer tokens
    useEffect(() => {
        if (isAuthenticated) {
            setAuthTokenGetter(() =>
                getAccessTokenSilently({
                    authorizationParams: {
                        audience: import.meta.env.VITE_AUTH0_AUDIENCE,
                    },
                })
            );
        }
    }, [isAuthenticated, getAccessTokenSilently]);

    // Show loading spinner while Auth0 initializes or processes callback
    if (isLoading) {
        return (
            <div className="flex h-screen items-center justify-center bg-gray-50">
                <div className="text-center">
                    <div className="w-8 h-8 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-gray-500 text-sm">Loading...</p>
                </div>
            </div>
        );
    }

    // Show Auth0 error clearly — no redirect loop
    if (error) {
        return (
            <div className="flex h-screen items-center justify-center bg-gray-50">
                <div className="text-center max-w-md px-6">
                    <div className="text-red-500 text-4xl mb-4">⚠</div>
                    <h2 className="text-xl font-semibold text-gray-900 mb-2">Authentication Error</h2>
                    <p className="text-gray-600 text-sm mb-6">{error.message}</p>
                    <button
                        onClick={() => {
                            hasRedirected.current = false;
                            loginWithRedirect();
                        }}
                        className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-2 rounded-lg transition-colors text-sm"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    // Redirect to Auth0 login if not authenticated (only once)
    if (!isAuthenticated) {
        if (!hasRedirected.current) {
            hasRedirected.current = true;
            loginWithRedirect();
        }
        return (
            <div className="flex h-screen items-center justify-center bg-gray-50">
                <div className="text-center">
                    <div className="w-8 h-8 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-gray-500 text-sm">Redirecting to login...</p>
                </div>
            </div>
        );
    }

    return (
        <BrowserRouter>
            <div className="min-h-screen bg-gray-50 text-gray-900 font-sans selection:bg-brand-100 selection:text-brand-900">
                <Navbar />
                <Routes>
                    <Route path="/" element={<DecisionsPage />} />
                    <Route path="/upload" element={<UploadPage />} />
                    <Route path="/exposure" element={<ExposureDashboard />} />
                    <Route path="/contracts" element={<ContractsPage />} />
                </Routes>
            </div>
        </BrowserRouter>
    );
}

export default App;

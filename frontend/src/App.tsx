// import { useEffect, useRef } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
// import { useAuth0 } from '@auth0/auth0-react';
import { DecisionsPage } from './pages/Decisions';
import { UploadPage } from './pages/Upload';
import { ExposureDashboard } from './pages/ExposureDashboard';
import { ContractsPage } from './pages/Contracts';
import { HospitalLanding } from './pages/HospitalLanding';
import { Navbar } from './components/Navbar';
// import { setAuthTokenGetter } from './services/api';

function AuthenticatedApp() {
    // Auth0 commented out for local dev — will re-enable for production
    // const { isAuthenticated, isLoading, loginWithRedirect, getAccessTokenSilently, error } = useAuth0();
    // const hasRedirected = useRef(false);

    // useEffect(() => {
    //     if (isAuthenticated) {
    //         setAuthTokenGetter(() =>
    //             getAccessTokenSilently({
    //                 authorizationParams: {
    //                     audience: import.meta.env.VITE_AUTH0_AUDIENCE,
    //                 },
    //             })
    //         );
    //     }
    // }, [isAuthenticated, getAccessTokenSilently]);

    return (
        <div className="min-h-screen bg-gray-50 text-gray-900 font-sans selection:bg-brand-100 selection:text-brand-900">
            <Navbar />
            <Routes>
                <Route path="/" element={<DecisionsPage />} />
                <Route path="/upload" element={<UploadPage />} />
                <Route path="/exposure" element={<ExposureDashboard />} />
                <Route path="/contracts" element={<ContractsPage />} />
            </Routes>
        </div>
    );
}

function App() {
    return (
        <BrowserRouter>
            <Routes>
                {/* Hospital landing — public, no auth required */}
                <Route path="/hospital" element={<HospitalLanding />} />
                {/* All other routes — auth disabled for local dev */}
                <Route path="/*" element={<AuthenticatedApp />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;

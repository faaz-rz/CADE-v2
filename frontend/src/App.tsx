import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { DecisionsPage } from './pages/Decisions';
import { UploadPage } from './pages/Upload';
import { ExposureDashboard } from './pages/ExposureDashboard';

function App() {
    return (
        <BrowserRouter>
            <div className="min-h-screen bg-gray-50 text-gray-900 font-sans selection:bg-brand-100 selection:text-brand-900">
                <Routes>
                    <Route path="/" element={<DecisionsPage />} />
                    <Route path="/upload" element={<UploadPage />} />
                    <Route path="/exposure" element={<ExposureDashboard />} />
                </Routes>
            </div>
        </BrowserRouter>
    );
}

export default App;

import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { DecisionsPage } from './pages/Decisions';
import { UploadPage } from './pages/Upload';
import { ExposureDashboard } from './pages/ExposureDashboard';
import { ContractsPage } from './pages/Contracts';
import { VendorDeepDive } from './pages/VendorDeepDive';
import { AlertsPage } from './pages/Alerts';
import { ProcurementScorePage } from './pages/ProcurementScore';
import { Navbar } from './components/Navbar';

function App() {
    return (
        <BrowserRouter>
            <Navbar />
            <Routes>
                <Route path="/" element={<DecisionsPage />} />
                <Route path="/upload" element={<UploadPage />} />
                <Route path="/exposure" element={<ExposureDashboard />} />
                <Route path="/contracts" element={<ContractsPage />} />
                <Route path="/vendor/:vendorId" element={<VendorDeepDive />} />
                <Route path="/alerts" element={<AlertsPage />} />
                <Route path="/score" element={<ProcurementScorePage />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;

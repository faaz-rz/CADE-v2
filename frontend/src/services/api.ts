import axios from 'axios';

const API_URL = 'http://localhost:8000/api';
const BASE_URL = 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_URL,
});

export interface Decision {
    id: string;
    decision_type: string;
    scope: 'COST' | 'VENDOR' | 'PROJECT';
    entity: string;
    recommended_action: string;
    explanation: string;
    expected_monthly_impact: number;
    cost_of_inaction: number;
    annual_impact: number;
    impact_label: 'HIGH' | 'MEDIUM' | 'LOW';
    risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
    risk_score: number;
    risk_range: {
        best_case: number;
        worst_case: number;
    };
    confidence: number;
    status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'DEFERRED';
    context?: {
        analysis_period: string;
        rule_id: string;
        metrics: Record<string, number>;
        vendor_share_of_category?: number;
    };
    events?: Array<{
        id: string;
        event_type: 'CREATED' | 'APPROVED' | 'REJECTED' | 'DEFERRED' | 'REOPENED';
        new_status: string;
        actor_id: string;
        note?: string;
        created_at: string;
    }>;
}

export interface DecisionSummary {
    total_savings: number;
    total_decisions: number;
    pending_count: number;
    pending_high_impact: number;
    impact_breakdown: Record<string, number>;
    risk_breakdown: Record<string, number>;
}

export interface FinancialExposure {
    vendor_id: string;
    annual_spend: number;
    vendor_share_pct: number;
    category: string;
    worst_case_exposure: number;
    price_shock_impact_10pct: number;
    price_shock_impact_20pct: number;
    estimated_ebitda_delta_10pct: number;
    estimated_ebitda_delta_20pct: number;
}

export interface MitigationOption {
    strategy: string;
    estimated_savings: number;
    residual_ebitda_delta: number;
}

export interface PriceShockResponse {
    base_spend: number;
    shock_percentage: number;
    new_spend: number;
    delta_spend: number;
    estimated_ebitda_delta: number;
    risk_classification_shift: string;
    mitigations?: MitigationOption[];
}

export interface PortfolioShockRequest {
    category?: string | null;
    vendor_ids?: string[] | null;
    shock_percentage: number;
    ebitda_margin: number;
}

export interface PortfolioShockResponse {
    total_base_spend: number;
    total_new_spend: number;
    total_delta_spend: number;
    total_ebitda_delta: number;
    affected_vendors: number;
}

export interface ScenarioDefinition {
    id: string;
    name: string;
    description: string;
    shock_percentage: number;
    ebitda_margin: number;
    category_focus: string;
}

export interface VendorTrend {
    vendor_id: string;
    monthly_spends: Array<{ month: string; total_spend: number }>;
    rolling_avg_3m: number | null;
    rolling_avg_6m: number | null;
    growth_pct_3m: number | null;
    growth_pct_6m: number | null;
    is_emerging_risk: boolean;
}

export const DecisionService = {
    getDecisions: async () => {
        const response = await api.get<Decision[]>('/decisions');
        return response.data;
    },

    getSummary: async () => {
        const response = await api.get<DecisionSummary>('/summary');
        return response.data;
    },

    approve: async (id: string) => {
        const response = await api.post(`/decisions/${id}/approve`, { note: "Approved via Web UI" });
        return response.data;
    },

    reject: async (id: string, reason: string) => {
        const response = await api.post(`/decisions/${id}/reject`, { note: reason });
        return response.data;
    },

    upload: async (file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post('/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },
};

export const ExposureService = {
    getAllExposures: async () => {
        const response = await api.get<FinancialExposure[]>('/exposure/vendors');
        return response.data;
    },

    getVendorExposure: async (vendorId: string) => {
        const response = await api.get<FinancialExposure>(`/exposure/vendors/${encodeURIComponent(vendorId)}`);
        return response.data;
    },
};

export const SimulationService = {
    runPriceShock: async (vendorId: string, shockPercentage: number, ebitdaMargin: number = 0.25) => {
        const response = await axios.post<PriceShockResponse>(
            `${BASE_URL}/simulate/price_shock`,
            { vendor_id: vendorId, shock_percentage: shockPercentage, ebitda_margin: ebitdaMargin }
        );
        return response.data;
    },
    runPortfolioShock: async (request: PortfolioShockRequest) => {
        const response = await axios.post<PortfolioShockResponse>(
            `${BASE_URL}/simulate/portfolio_shock`,
            request
        );
        return response.data;
    },
    getScenarios: async () => {
        const response = await axios.get<ScenarioDefinition[]>(
            `${BASE_URL}/simulate/scenarios`
        );
        return response.data;
    }
};

export const ExportService = {
    downloadExecutiveReport: async () => {
        const response = await axios.get(`${BASE_URL}/export/executive_report`, {
            responseType: 'blob',
        });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'executive_report.xlsx');
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
    },
};

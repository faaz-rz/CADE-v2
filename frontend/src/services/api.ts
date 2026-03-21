import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/api` : 'http://localhost:8000/api';
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_URL,
});

// ── Auth Token Management ──
let _getAccessToken: (() => Promise<string>) | null = null;

/**
 * Called once from App.tsx to register the Auth0 token getter.
 * The interceptor will call this before every request.
 */
export const setAuthTokenGetter = (getter: () => Promise<string>) => {
    _getAccessToken = getter;
};

// Attach Bearer token to every request via interceptor
api.interceptors.request.use(async (config) => {
    if (_getAccessToken) {
        try {
            const token = await _getAccessToken();
            config.headers.Authorization = `Bearer ${token}`;
        } catch (e) {
            // Token fetch failed — request goes without auth
            console.warn('Failed to get access token', e);
        }
    }
    return config;
});

// Also create an authenticated axios instance for non-api calls (simulate, export)
const authenticatedAxios = axios.create();
authenticatedAxios.interceptors.request.use(async (config) => {
    if (_getAccessToken) {
        try {
            const token = await _getAccessToken();
            config.headers.Authorization = `Bearer ${token}`;
        } catch (e) {
            console.warn('Failed to get access token', e);
        }
    }
    return config;
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
        const response = await authenticatedAxios.post<PriceShockResponse>(
            `${BASE_URL}/simulate/price_shock`,
            { vendor_id: vendorId, shock_percentage: shockPercentage, ebitda_margin: ebitdaMargin }
        );
        return response.data;
    },
    runPortfolioShock: async (request: PortfolioShockRequest) => {
        const response = await authenticatedAxios.post<PortfolioShockResponse>(
            `${BASE_URL}/simulate/portfolio_shock`,
            request
        );
        return response.data;
    },
    getScenarios: async () => {
        const response = await authenticatedAxios.get<ScenarioDefinition[]>(
            `${BASE_URL}/simulate/scenarios`
        );
        return response.data;
    }
};

export const ExportService = {
    downloadExecutiveReport: async () => {
        const response = await authenticatedAxios.get(`${BASE_URL}/export/executive_report`, {
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

export interface TrendAlert {
    vendor: string;
    alert_type: 'RAPID_GROWTH' | 'EMERGING_RISK' | 'DECLINING_SPEND';
    severity: 'HIGH' | 'MEDIUM' | 'LOW';
    title: string;
    message: string;
    growth_rate: number;
    avg_spend_3m?: number;
    avg_spend_6m?: number;
}

export interface TrendAlertsResponse {
    alerts: TrendAlert[];
    total: number;
    high: number;
    medium: number;
    low: number;
}

export const TrendService = {
    getAlerts: async () => {
        const response = await api.get<TrendAlertsResponse>('/trends/alerts');
        return response.data;
    },
    getVendorTrends: async () => {
        const response = await api.get<{ vendors: VendorTrend[]; total: number }>('/trends/vendors');
        return response.data;
    },
};

export interface SavingsSummary {
    approved_savings: number;
    pending_savings: number;
    rejected_savings: number;
    total_identified: number;
    decisions_approved_count: number;
    decisions_pending_count: number;
    decisions_rejected_count: number;
    roi_multiple: number;
    currency: string;
}

export const SavingsService = {
    getSavings: async () => {
        const response = await api.get<SavingsSummary>('/decisions/savings');
        return response.data;
    },
};

export interface ContractRenewal {
    vendor_name: string;
    category: string;
    annual_spend: number;
    renewal_date: string;
    days_until_renewal: number;
    recommended_action: string;
    potential_savings: number;
}

export interface RenewalsResponse {
    urgent: ContractRenewal[];
    upcoming: ContractRenewal[];
    planned: ContractRenewal[];
    total_renewals_90_days: number;
    total_savings_opportunity: number;
}

export const ContractService = {
    getRenewals: async () => {
        const response = await api.get<RenewalsResponse>('/contracts/renewals');
        return response.data;
    },
};

export const DemoService = {
    loadDemo: async () => {
        const response = await api.post<{ status: string; decisions_generated: number }>('/demo');
        return response.data;
    },
    clearDemo: async () => {
        const response = await api.delete<{ status: string }>('/demo');
        return response.data;
    },
};

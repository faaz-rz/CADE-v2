import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

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
    risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
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

// ... existing interfaces ...

export interface DecisionSummary {
    total_savings: number;
    total_decisions: number;
    pending_count: number;
    pending_high_impact: number;
    impact_breakdown: Record<string, number>;
    risk_breakdown: Record<string, number>;
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
        // Backend expects ReviewNote: { note: string }
        const response = await api.post(`/decisions/${id}/approve`, { note: "Approved via Web UI" });
        return response.data;
    },
    // ... rest of the file ...

    reject: async (id: string, reason: string) => {
        // Backend expects ReviewNote: { note: string }
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
    }
};

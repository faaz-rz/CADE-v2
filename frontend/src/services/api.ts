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
    status: 'PENDING' | 'APPROVED' | 'REJECTED';
}

export const DecisionService = {
    getDecisions: async () => {
        const response = await api.get<Decision[]>('/decisions');
        return response.data;
    },

    approve: async (id: string) => {
        const response = await api.post(`/decisions/${id}/approve`);
        return response.data;
    },

    reject: async (id: string, reason: string) => {
        const response = await api.post(`/decisions/${id}/reject`, { reason });
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

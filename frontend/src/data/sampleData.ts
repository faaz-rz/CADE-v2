import { Decision } from '../services/api';

// Realistic sample data for demo purposes mimicking decision_engine.py output
export const sampleData: Decision[] = [
    {
        id: "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
        decision_type: "VENDOR_REDUCE",
        scope: "VENDOR",
        entity: "AWS",
        recommended_action: "Reduce AWS usage due to high spend exceeding $5000",
        explanation: "AWS total spend is $340000.0, which exceeds the threshold of $5000.",
        context: {
            analysis_period: "Uploaded Period",
            rule_id: "RULE_001",
            metrics: {
                total_spend: 340000.0,
                transaction_count: 72
            },
            vendor_share_of_category: 0.41,
        },
        expected_monthly_impact: 28333.33,
        cost_of_inaction: 340000.0,
        annual_impact: 340000.0,
        impact_label: "HIGH",
        risk_level: "HIGH",
        risk_score: 9,
        risk_range: {
            best_case: 170000.0,
            worst_case: 510000.0
        },
        confidence: 0.95,
        status: "PENDING",
        events: []
    },
    {
        id: "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
        decision_type: "VENDOR_REDUCE",
        scope: "VENDOR",
        entity: "Salesforce",
        recommended_action: "Reduce Salesforce usage due to high spend exceeding $5000",
        explanation: "Salesforce total spend is $210000.0, which exceeds the threshold of $5000.",
        context: {
            analysis_period: "Uploaded Period",
            rule_id: "RULE_001",
            metrics: {
                total_spend: 210000.0,
                transaction_count: 24
            },
            vendor_share_of_category: 0.38,
        },
        expected_monthly_impact: 17500.0,
        cost_of_inaction: 210000.0,
        annual_impact: 210000.0,
        impact_label: "HIGH",
        risk_level: "HIGH",
        risk_score: 8,
        risk_range: {
            best_case: 105000.0,
            worst_case: 315000.0
        },
        confidence: 0.90,
        status: "PENDING",
        events: []
    },
    {
        id: "c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f",
        decision_type: "VENDOR_REDUCE",
        scope: "VENDOR",
        entity: "Snowflake",
        recommended_action: "Reduce Snowflake usage due to high spend exceeding $5000",
        explanation: "Snowflake total spend is $95000.0, which exceeds the threshold of $5000.",
        context: {
            analysis_period: "Uploaded Period",
            rule_id: "RULE_001",
            metrics: {
                total_spend: 95000.0,
                transaction_count: 12
            },
            vendor_share_of_category: 0.15,
        },
        expected_monthly_impact: 7916.66,
        cost_of_inaction: 95000.0,
        annual_impact: 95000.0,
        impact_label: "HIGH",
        risk_level: "MEDIUM",
        risk_score: 6,
        risk_range: {
            best_case: 47500.0,
            worst_case: 142500.0
        },
        confidence: 0.85,
        status: "PENDING",
        events: []
    },
    {
        id: "d4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f90",
        decision_type: "VENDOR_REDUCE",
        scope: "VENDOR",
        entity: "HubSpot",
        recommended_action: "Reduce HubSpot usage due to high spend exceeding $5000",
        explanation: "HubSpot total spend is $72000.0, which exceeds the threshold of $5000.",
        context: {
            analysis_period: "Uploaded Period",
            rule_id: "RULE_001",
            metrics: {
                total_spend: 72000.0,
                transaction_count: 12
            },
            vendor_share_of_category: 0.12,
        },
        expected_monthly_impact: 6000.0,
        cost_of_inaction: 72000.0,
        annual_impact: 72000.0,
        impact_label: "HIGH",
        risk_level: "MEDIUM",
        risk_score: 5,
        risk_range: {
            best_case: 36000.0,
            worst_case: 108000.0
        },
        confidence: 0.88,
        status: "PENDING",
        events: []
    },
    {
        id: "e5f6a7b8-c9d0-1e2f-3a4b-5c6d7e8f9012",
        decision_type: "VENDOR_REDUCE",
        scope: "VENDOR",
        entity: "Slack",
        recommended_action: "Reduce Slack usage due to high spend exceeding $5000",
        explanation: "Slack total spend is $48000.0, which exceeds the threshold of $5000.",
        context: {
            analysis_period: "Uploaded Period",
            rule_id: "RULE_001",
            metrics: {
                total_spend: 48000.0,
                transaction_count: 12
            },
            vendor_share_of_category: 0.08,
        },
        expected_monthly_impact: 4000.0,
        cost_of_inaction: 48000.0,
        annual_impact: 48000.0,
        impact_label: "HIGH",
        risk_level: "LOW",
        risk_score: 3,
        risk_range: {
            best_case: 24000.0,
            worst_case: 72000.0
        },
        confidence: 0.92,
        status: "PENDING",
        events: []
    },
    {
        id: "f6a7b8c9-d0e1-2f3a-4b5c-6d7e8f901234",
        decision_type: "VENDOR_REDUCE",
        scope: "VENDOR",
        entity: "Stripe",
        recommended_action: "Reduce Stripe usage due to high spend exceeding $5000",
        explanation: "Stripe total spend is $38000.0, which exceeds the threshold of $5000.",
        context: {
            analysis_period: "Uploaded Period",
            rule_id: "RULE_001",
            metrics: {
                total_spend: 38000.0,
                transaction_count: 12
            },
            vendor_share_of_category: 0.06,
        },
        expected_monthly_impact: 3166.66,
        cost_of_inaction: 38000.0,
        annual_impact: 38000.0,
        impact_label: "HIGH",
        risk_level: "LOW",
        risk_score: 2,
        risk_range: {
            best_case: 19000.0,
            worst_case: 57000.0
        },
        confidence: 0.94,
        status: "PENDING",
        events: []
    },
    {
        id: "a7b8c9d0-e1f2-3a4b-5c6d-7e8f90123456",
        decision_type: "VENDOR_REDUCE",
        scope: "VENDOR",
        entity: "Twilio",
        recommended_action: "Reduce Twilio usage due to high spend exceeding $5000",
        explanation: "Twilio total spend is $29000.0, which exceeds the threshold of $5000.",
        context: {
            analysis_period: "Uploaded Period",
            rule_id: "RULE_001",
            metrics: {
                total_spend: 29000.0,
                transaction_count: 12
            },
            vendor_share_of_category: 0.04,
        },
        expected_monthly_impact: 2416.66,
        cost_of_inaction: 29000.0,
        annual_impact: 29000.0,
        impact_label: "HIGH",
        risk_level: "MEDIUM",
        risk_score: 4,
        risk_range: {
            best_case: 14500.0,
            worst_case: 43500.0
        },
        confidence: 0.82,
        status: "PENDING",
        events: []
    },
    {
        id: "b8c9d0e1-f2a3-4b5c-6d7e-8f9012345678",
        decision_type: "VENDOR_REDUCE",
        scope: "VENDOR",
        entity: "Cloudflare",
        recommended_action: "Reduce Cloudflare usage due to high spend exceeding $5000",
        explanation: "Cloudflare total spend is $18000.0, which exceeds the threshold of $5000.",
        context: {
            analysis_period: "Uploaded Period",
            rule_id: "RULE_001",
            metrics: {
                total_spend: 18000.0,
                transaction_count: 12
            },
            vendor_share_of_category: 0.03,
        },
        expected_monthly_impact: 1500.0,
        cost_of_inaction: 18000.0,
        annual_impact: 18000.0,
        impact_label: "HIGH",
        risk_level: "LOW",
        risk_score: 2,
        risk_range: {
            best_case: 9000.0,
            worst_case: 27000.0
        },
        confidence: 0.89,
        status: "PENDING",
        events: []
    }
];

import { Decision } from '../services/api';

// Realistic sample data for demo purposes — matches the 8 demo vendors
export const sampleData: Decision[] = [
    {
        id: "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
        decision_type: "VENDOR_REDUCE",
        scope: "VENDOR",
        entity: "AMAZON WEB SERVICES",
        recommended_action: "Reduce AWS spend — concentration risk at 41% of Cloud Infrastructure category",
        explanation: "AMAZON WEB SERVICES accounts for 41% of Cloud Infrastructure spend ($340,000), exceeding the 40% concentration threshold.",
        context: {
            analysis_period: "Uploaded Period",
            rule_id: "RULE_001",
            metrics: {
                total_spend: 340000.0,
                transaction_count: 12
            },
            vendor_share_of_category: 0.78,
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
        entity: "SALESFORCE",
        recommended_action: "Negotiate Salesforce renewal — high absolute SaaS spend at $210,000",
        explanation: "SALESFORCE total spend is $210,000, which is 42x the category threshold. Estimated annual savings: $21,000.",
        context: {
            analysis_period: "Uploaded Period",
            rule_id: "RULE_003",
            metrics: {
                total_spend: 210000.0,
                transaction_count: 12
            },
            vendor_share_of_category: 0.37,
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
        decision_type: "COST_REDUCE",
        scope: "VENDOR",
        entity: "WORKDAY",
        recommended_action: "Review Workday contract — SaaS renewal window for $180,000 spend",
        explanation: "WORKDAY is a SaaS vendor with $180,000 in total spend. Contract renewal negotiation could save an estimated $31,500.",
        context: {
            analysis_period: "Uploaded Period",
            rule_id: "RULE_004",
            metrics: {
                total_spend: 180000.0,
                transaction_count: 12
            },
            vendor_share_of_category: 0.32,
        },
        expected_monthly_impact: 15000.0,
        cost_of_inaction: 180000.0,
        annual_impact: 180000.0,
        impact_label: "HIGH",
        risk_level: "MEDIUM",
        risk_score: 6,
        risk_range: {
            best_case: 90000.0,
            worst_case: 270000.0
        },
        confidence: 0.87,
        status: "PENDING",
        events: []
    },
    {
        id: "d4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f90",
        decision_type: "VENDOR_REDUCE",
        scope: "VENDOR",
        entity: "SNOWFLAKE",
        recommended_action: "Optimize Snowflake usage — growing Cloud Infrastructure spend at $95,000",
        explanation: "SNOWFLAKE total spend is $95,000 across Cloud Infrastructure. Usage-based pricing optimization recommended.",
        context: {
            analysis_period: "Uploaded Period",
            rule_id: "RULE_003",
            metrics: {
                total_spend: 95000.0,
                transaction_count: 12
            },
            vendor_share_of_category: 0.22,
        },
        expected_monthly_impact: 7916.67,
        cost_of_inaction: 95000.0,
        annual_impact: 95000.0,
        impact_label: "HIGH",
        risk_level: "MEDIUM",
        risk_score: 5,
        risk_range: {
            best_case: 47500.0,
            worst_case: 142500.0
        },
        confidence: 0.85,
        status: "PENDING",
        events: []
    },
    {
        id: "e5f6a7b8-c9d0-1e2f-3a4b-5c6d7e8f9012",
        decision_type: "COST_REDUCE",
        scope: "VENDOR",
        entity: "HUBSPOT",
        recommended_action: "Review HubSpot contract renewal — $72,000 SaaS spend",
        explanation: "HUBSPOT is a SaaS vendor with $72,000 in total spend. Contract renewal negotiation could save an estimated $12,600.",
        context: {
            analysis_period: "Uploaded Period",
            rule_id: "RULE_004",
            metrics: {
                total_spend: 72000.0,
                transaction_count: 12
            },
            vendor_share_of_category: 0.13,
        },
        expected_monthly_impact: 6000.0,
        cost_of_inaction: 72000.0,
        annual_impact: 72000.0,
        impact_label: "HIGH",
        risk_level: "MEDIUM",
        risk_score: 4,
        risk_range: {
            best_case: 36000.0,
            worst_case: 108000.0
        },
        confidence: 0.88,
        status: "PENDING",
        events: []
    },
    {
        id: "f6a7b8c9-d0e1-2f3a-4b5c-6d7e8f901234",
        decision_type: "COST_REDUCE",
        scope: "VENDOR",
        entity: "SLACK",
        recommended_action: "Review Slack contract renewal — $48,000 SaaS spend",
        explanation: "SLACK is a SaaS vendor with $48,000 in total spend. Contract renewal negotiation could save an estimated $8,400.",
        context: {
            analysis_period: "Uploaded Period",
            rule_id: "RULE_004",
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
        id: "a7b8c9d0-e1f2-3a4b-5c6d-7e8f90123456",
        decision_type: "COST_REDUCE",
        scope: "VENDOR",
        entity: "ZENDESK",
        recommended_action: "Review Zendesk contract renewal — $36,000 SaaS spend",
        explanation: "ZENDESK is a SaaS vendor with $36,000 in total spend. Contract renewal negotiation could save an estimated $6,300.",
        context: {
            analysis_period: "Uploaded Period",
            rule_id: "RULE_004",
            metrics: {
                total_spend: 36000.0,
                transaction_count: 12
            },
            vendor_share_of_category: 0.06,
        },
        expected_monthly_impact: 3000.0,
        cost_of_inaction: 36000.0,
        annual_impact: 36000.0,
        impact_label: "HIGH",
        risk_level: "LOW",
        risk_score: 2,
        risk_range: {
            best_case: 18000.0,
            worst_case: 54000.0
        },
        confidence: 0.90,
        status: "PENDING",
        events: []
    },
    {
        id: "b8c9d0e1-f2a3-4b5c-6d7e-8f9012345678",
        decision_type: "COST_REDUCE",
        scope: "VENDOR",
        entity: "DOCUSIGN",
        recommended_action: "Review DocuSign contract renewal — $24,000 SaaS spend",
        explanation: "DOCUSIGN is a SaaS vendor with $24,000 in total spend. Contract renewal negotiation could save an estimated $4,200.",
        context: {
            analysis_period: "Uploaded Period",
            rule_id: "RULE_004",
            metrics: {
                total_spend: 24000.0,
                transaction_count: 12
            },
            vendor_share_of_category: 0.04,
        },
        expected_monthly_impact: 2000.0,
        cost_of_inaction: 24000.0,
        annual_impact: 24000.0,
        impact_label: "HIGH",
        risk_level: "LOW",
        risk_score: 2,
        risk_range: {
            best_case: 12000.0,
            worst_case: 36000.0
        },
        confidence: 0.89,
        status: "PENDING",
        events: []
    }
];

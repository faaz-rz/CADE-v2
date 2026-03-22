
import sys
from app.services.decision_engine import DecisionEngine
from app.services.analytics import SpendingAnalyzer
from app.models.decision import ImpactLabel, RiskLevel
from dataclasses import dataclass

# Mocking the SpendingAnalyzer dependencies
@dataclass
class MockStats:
    total_spend: float
    transaction_count: int

def run_test():
    """
    Verifies the Decision Summary Logic.
    """
    print("Running Decision Summary Logic Test...")
    
    # Mock Data: 
    # High Impact: 1 (TechStore) -> $39,600
    # Medium Impact: 2 (CloudNine, SoftCorp) -> $6000 + $2880 = $8880
    # Total Savings: 39600 + 8880 = 48480
    
    mock_stats = {
        "TechStore": MockStats(total_spend=33000.0, transaction_count=3), # High
        "CloudNine": MockStats(total_spend=5000.0, transaction_count=2),  # Med
        "SoftCorp": MockStats(total_spend=2400.0, transaction_count=6),   # Med
    }

    original_get_stats = SpendingAnalyzer.get_vendor_stats
    SpendingAnalyzer.get_vendor_stats = lambda: mock_stats

    try:
        import asyncio
        # 1. Run Analysis
        decisions = asyncio.run(DecisionEngine.analyze_uploaded_data())
        
        # 2. Get Summary
        summary = DecisionEngine.get_summary_stats(decisions)
        
        print(f"Summary Generated: Total Savings=${summary.total_savings:,.2f}, Count={summary.total_decisions}")
        print(f"Impact Breakdown: {summary.impact_breakdown}")
        print(f"Risk Breakdown: {summary.risk_breakdown}")

        # Assertions
        expected_savings = 39600.0 + 6000.0 + 2880.0
        if summary.total_savings != expected_savings:
             print(f"FAIL: Expected savings {expected_savings}, got {summary.total_savings}")
             sys.exit(1)
             
        if summary.total_decisions != 3:
             print(f"FAIL: Expected 3 decisions, got {summary.total_decisions}")
             sys.exit(1)

        if summary.impact_breakdown["HIGH"] != 1 or summary.impact_breakdown["MEDIUM"] != 2:
             print(f"FAIL: Impact breakdown mismatch. Expected {{'HIGH': 1, 'MEDIUM': 2}}, got {summary.impact_breakdown}")
             sys.exit(1)

        print("PASS: Decision Summary Verified")

    finally:
        SpendingAnalyzer.get_vendor_stats = original_get_stats

if __name__ == "__main__":
    run_test()

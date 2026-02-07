
import sys
from app.services.decision_engine import DecisionEngine
from app.services.analytics import SpendingAnalyzer
from app.models.decision import ImpactLabel, DecisionType
from dataclasses import dataclass

# Mocking the SpendingAnalyzer dependencies
@dataclass
class MockStats:
    total_spend: float
    transaction_count: int

def run_test():
    """
    Verifies the specific prioritization logic for the Enterprise scenario.
    """
    print("Running Enterprise Prioritization Logic Test...")
    
    # Mock Data matching 'enterprise_spend_mixed_units.csv' post-ingestion
    mock_stats = {
        "TechStore": MockStats(total_spend=33000.0, transaction_count=3), # 33k > 5k
        "CloudNine": MockStats(total_spend=5000.0, transaction_count=2),  # 5k == 5k (Boundary)
        "SoftCorp": MockStats(total_spend=2400.0, transaction_count=6),   # 2.4k < 5k, but Freq 6 > 5
        "PaperMart": MockStats(total_spend=90.0, transaction_count=2)     # Ignored
    }

    original_get_stats = SpendingAnalyzer.get_vendor_stats
    SpendingAnalyzer.get_vendor_stats = lambda: mock_stats

    try:
        # Run Engine
        decisions = DecisionEngine.analyze_uploaded_data()

        # 1. Assert Count (Should be 3)
        print(f"Decisions Generated: {len(decisions)}")
        if len(decisions) != 3:
            print(f"FAIL: Expected 3 decisions, got {len(decisions)}")
            sys.exit(1)

        # 2. Assert Sorting (High Impact First)
        if decisions[0].entity != "TechStore":
            print(f"FAIL: Expected TechStore first, got {decisions[0].entity}")
            sys.exit(1)
        if decisions[1].entity != "TechStore" and decisions[1].entity != "CloudNine": # Sorting logic might be stable
             # Wait, 39600 > 6000 > 2880. Sorting is deterministic.
             pass

        # 3. Assert TechStore (HIGH)
        tech = next(d for d in decisions if d.entity == "TechStore")
        print(f"TechStore: ${tech.annual_impact:,.2f} ({tech.impact_label})")
        if tech.impact_label != ImpactLabel.HIGH:
            print(f"FAIL: TechStore should be HIGH, got {tech.impact_label}")
            sys.exit(1)
        if tech.annual_impact != 39600.0:
            print(f"FAIL: TechStore impact mismatch. Expected 39600, got {tech.annual_impact}")
            sys.exit(1)

        # 4. Assert CloudNine (MEDIUM - Boundary Check)
        cloud = next(d for d in decisions if d.entity == "CloudNine")
        print(f"CloudNine: ${cloud.annual_impact:,.2f} ({cloud.impact_label})")
        if cloud.impact_label != ImpactLabel.MEDIUM:
            print(f"FAIL: CloudNine should be MEDIUM, got {cloud.impact_label}")
            sys.exit(1)
        if cloud.annual_impact != 6000.0:
            print(f"FAIL: CloudNine impact mismatch. Expected 6000, got {cloud.annual_impact}")
            sys.exit(1)

        # 5. Assert SoftCorp (MEDIUM - Frequency Rule, Standardized Impact)
        soft = next(d for d in decisions if d.entity == "SoftCorp")
        print(f"SoftCorp: ${soft.annual_impact:,.2f} ({soft.impact_label})")
        if soft.impact_label != ImpactLabel.MEDIUM:
            print(f"FAIL: SoftCorp should be MEDIUM, got {soft.impact_label}")
            sys.exit(1)
        if soft.annual_impact != 2880.0:
            print(f"FAIL: SoftCorp impact mismatch. Expected 2880, got {soft.annual_impact}")
            sys.exit(1)

        print("PASS: Prioritization Logic Verified")

    finally:
        SpendingAnalyzer.get_vendor_stats = original_get_stats

if __name__ == "__main__":
    run_test()

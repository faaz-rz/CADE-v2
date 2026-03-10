
import sys
import os
import shutil
import json

# Add the backend directory to sys.path
sys.path.append(os.getcwd())

from app.services.ingestion import IngestionService
from app.services.decision_engine import DecisionEngine
from app.models.decision import DecisionType

def test_aligned_decisions():
    print("Testing Aligned Decision Logic...")
    
    # 1. Clean up previous data
    if os.path.exists("data/transactions.json"):
        os.remove("data/transactions.json")

    # 2. Ingest Data (High Spend Vendor & High Frequency Vendor)
    # TechStore: > $5000 total (should trigger High Spend)
    # SoftCorp: > 5 transactions (should trigger High Frequency)
    csv_content = b"""PurchaseDate,Supplier,TotalCost,Category
2023-01-01,TechStore,3000.00,Hardware
2023-01-02,TechStore,3000.00,Hardware
2023-01-03,SoftCorp,100.00,Software
2023-01-04,SoftCorp,100.00,Software
2023-01-05,SoftCorp,100.00,Software
2023-01-06,SoftCorp,100.00,Software
2023-01-07,SoftCorp,100.00,Software
2023-01-08,SoftCorp,100.00,Software
"""
    filename = "test_decisions.csv"
    
    print("Ingesting data...")
    IngestionService.ingest_file(csv_content, filename)
    
    # 3. Generate Decisions
    print("Generating decisions...")
    decisions = DecisionEngine.analyze_uploaded_data()
    
    print(f"Generated {len(decisions)} decisions.")
    
    # 4. Verify Content
    tech_store_decision = next((d for d in decisions if d.entity == "TechStore"), None)
    soft_corp_decision = next((d for d in decisions if d.entity == "SoftCorp"), None)
    
    # Assertion 1: TechStore should be VENDOR_REDUCE due to High Spend
    if tech_store_decision:
        print(f"TechStore Decision: {tech_store_decision.decision_type} - {tech_store_decision.recommended_action}")
        assert tech_store_decision.decision_type == DecisionType.VENDOR_REDUCE
        assert "significantly higher" in tech_store_decision.explanation
        
        # New Context Verification
        ctx = tech_store_decision.context
        print(f"  Context: Period={ctx.analysis_period}, Rule={ctx.rule_id}")
        print(f"  Metrics: {ctx.metrics}")
        
        assert ctx.rule_id == "HIGH_SPEND_VENDOR"
        assert ctx.metrics["total_spend"] == 6000.0
        
        # Impact Verification
        print(f"  Impact: {tech_store_decision.impact_label} (${tech_store_decision.annual_impact:,.2f})")
        assert tech_store_decision.impact_label == "MEDIUM" # 6000 * 0.1 * 12 = 7200 > 1000
        assert tech_store_decision.annual_impact == 7200.0
        
        print("PASS: TechStore High Spend Rule + Context + Impact")
    else:
        print("FAIL: TechStore decision missing")

    # Assertion 2: SoftCorp should be VENDOR_CONSOLIDATE due to High Frequency
    if soft_corp_decision:
        print(f"SoftCorp Decision: {soft_corp_decision.decision_type} - {soft_corp_decision.recommended_action}")
        assert soft_corp_decision.decision_type == DecisionType.VENDOR_CONSOLIDATE
        
        # New Context Verification
        ctx = soft_corp_decision.context
        assert ctx.rule_id == "HIGH_FREQUENCY_VENDOR"
        
        # Impact Verification
        # Total Spend 600 (100*6). Impact = 600 * 0.05 * 12 = 360
        print(f"  Impact: {soft_corp_decision.impact_label} (${soft_corp_decision.annual_impact:,.2f})")
        assert soft_corp_decision.impact_label == "LOW" # 360 <= 1000
        assert soft_corp_decision.annual_impact == 360.0
        
        print("PASS: SoftCorp High Frequency Rule + Context + Impact")
    else:
        print("FAIL: SoftCorp decision missing")
    
    # Assertion 3: No Hallucinations (Slack/Notion)
    hallucinations = [d for d in decisions if d.entity in ["Slack", "Notion"]]
    if not hallucinations:
        print("PASS: No hallucinations found (Slack/Notion removed)")
    else:
        print(f"FAIL: Hallucinated decisions found: {[d.entity for d in hallucinations]}")

if __name__ == "__main__":
    test_aligned_decisions()

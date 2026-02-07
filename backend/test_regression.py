
import sys
import os
import json
import pandas as pd
from app.services.ingestion import IngestionService

# Add the backend directory to sys.path
sys.path.append(os.getcwd())

def test_regression():
    print("Testing Regression: Ensuring Standard Datasets are UNAFFECTED...")
    
    # Mock Standard Dataset (e.g. Spend Analysis)
    # Header matches default_mapping.yaml: Supplier, TotalCost
    csv_content = b"""Supplier,TotalCost,PurchaseDate,Category
Staples,100.00,2023-01-01,Office
"""
    
    filename = "standard_dataset.csv"
    
    try:
        # We expect it to auto-detect default_mapping.yaml (or heuristics if config matching fails)
        # But let's be explicit and force the issue: The system should NOT multiply this by 1000.
        
        # Note: In `IngestionService`, we loop through configs. 
        # `default_mapping.yaml` maps "Supplier", "TotalCost".
        # So it should be detected.
        
        result = IngestionService.process_file(csv_content, filename)
        print("Ingestion Result:", result)
        
        # Verify Output
        with open("data/transactions.json", "r") as f:
            data = json.load(f)
            
        record = data[0]
        print("Record:", record)
        
        # Assertions
        assert record['entity'] == "Staples"
        
        # CRITICAL CHECK: value should be 100.0, NOT 100000.0
        assert record['amount'] == 100.0 
        
        print("PASS: Standard dataset value (100.0) preserved (No Multiplier applied).")

    except Exception as e:
        print(f"FAIL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_regression()

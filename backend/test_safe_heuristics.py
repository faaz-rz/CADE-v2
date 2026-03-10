
import sys
import os
import json
import pandas as pd
from app.services.ingestion import IngestionService

# Add the backend directory to sys.path
sys.path.append(os.getcwd())

def test_safe_heuristics():
    print("=== Testing Safe Heuristics ===")
    
    # CASE 1: High Confidence (Should Pass)
    print("\n[TEST 1] High Confidence Dataset")
    ds_high_conf = b"""Vendor,Total Cost,Transaction Date,Description
Uber,25.50,2023-05-01,Travel
Amazon,120.00,2023-05-02,Office Supplies
"""
    try:
        result = IngestionService.ingest_file(ds_high_conf, "high_conf_test.csv")
        print("SUCCESS: Ingestion proceeded as expected.")
        print(result)
    except Exception as e:
        print(f"FAIL: Unexpected error: {e}")

    # CASE 2: Ambiguous/Low Confidence (Should Fail)
    print("\n[TEST 2] Low Confidence/Ambiguous Dataset")
    ds_low_conf = b"""Payee Name,Val,When,What
Uber,25.50,2023-05-01,Travel
"""
    # "Val" might match "Value" (0.8) -> Amount
    # "Payee Name" might match "Payee" (0.9) -> Entity
    # "When" (0.6) -> Date
    # BUT let's see if it passes the threshold of 0.8 average for required.
    
    # Actually, "Val" is not in my keywords. "Value" is. "Val" is not.
    # So "Amount" will be missing.
    
    try:
        IngestionService.ingest_file(ds_low_conf, "low_conf_test.csv")
        print("FAIL: Should have refused ingestion!")
    except ValueError as e:
        print(f"SUCCESS: System refused ingestion as expected.")
        print(f"Error Message: {e}")
    except Exception as e:
        print(f"FAIL: Wrong error type: {type(e)} - {e}")

if __name__ == "__main__":
    test_safe_heuristics()

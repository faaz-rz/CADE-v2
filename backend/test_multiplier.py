
import sys
import os
import json
import pandas as pd
from app.services.ingestion import IngestionService

# Add the backend directory to sys.path
sys.path.append(os.getcwd())

def test_multiplier_ingestion():
    print("Testing Ingestion with Unit Multipliers...")
    
    # Mock CSV Content matching companies_clean.csv header
    # Marketing_Spend is 33 -> Should become 33,000
    csv_content = b"""Company_ID,Marketing_Spend (K\xc5\xa6),Campaign_Type
C001,33,SEM
C002,12.5,Content Marketing
"""
    # Note: K₺ symbol handling in header matching
    # The header in mapping_sales.yaml is "Marketing_Spend (K₺)"
    # I need to ensure the byte string matches that encoding or just use the approximate text if my heuristic was running.
    # But here I am testing the Explicit Mapping "mapping_sales.yaml".
    # So the header MUST match what's in the YAML: "Marketing_Spend (K₺)"
    
    # Constructing header with correct encoding for ₺ (U+20BA)
    # UTF-8 for ₺ is 0xE2 0x82 0xBA
    header = "Company_ID,Marketing_Spend (K₺),Campaign_Type\n"
    row1 = "C001,33,SEM\n"
    row2 = "C002,12.5,Content Marketing\n"
    full_csv = (header + row1 + row2).encode('utf-8')
    
    filename = "test_sales_multiplier.csv"
    
    try:
        # Load the config explicitly to ensure we use the sales mapping
        import yaml
        with open("config/mapping_sales.yaml", "r", encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        result = IngestionService.ingest_file(full_csv, filename, mapping_config=config)
        print("Ingestion Result:", result)
        
        # Verify Output
        with open("data/transactions.json", "r") as f:
            data = json.load(f)
            
        first_record = data[0]
        print("First Record:", first_record)
        
        # Verify Scaling
        # 33 * 1000 = 33000.0
        assert first_record['amount'] == 33000.0
        print("PASS: Amount 33 scaled to 33000.0")
        
        second_record = data[1]
        # 12.5 * 1000 = 12500.0
        assert second_record['amount'] == 12500.0
        print("PASS: Amount 12.5 scaled to 12500.0")

    except Exception as e:
        print(f"FAIL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_multiplier_ingestion()

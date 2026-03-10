
import sys
import os
import json
import pandas as pd

# Add the backend directory to sys.path
sys.path.append(os.getcwd())

from app.services.ingestion import IngestionService

def test_new_ingestion():
    print("Testing New Dataset Ingestion (Companies Sales Data)...")
    
    # Mock CSV Content matching companies_clean.csv header
    csv_content = b"""Company_ID,Industry,Company_Size,Marketing_Spend (K\xc5\xa6),Campaign_Type
C001,Mining,Small,33,SEM
C002,Space,Medium,12,Content Marketing
"""
    # Note: K₺ symbol might cause encoding issues in mock if not handled carefully.
    # I used \xc5\xa6 (₺ is U+20BA). Actually pandas read_csv defaults to utf-8.
    # Let's try simple ASCII if possible, or ensure encoding.
    # The header in the file view was `Marketing_Spend (K₺)`.
    
    # Retrying with utf-8 encoded bytes
    header = "Company_ID,Industry,Company_Size,Marketing_Spend (K₺),Campaign_Type\n"
    row1 = "C001,Mining,Small,33,SEM\n"
    row2 = "C002,Space,Medium,12,Content Marketing\n"
    full_csv = (header + row1 + row2).encode('utf-8')
    
    filename = "test_companies.csv"
    
    try:
        result = IngestionService.ingest_file(full_csv, filename)
        print("Ingestion Result:", result)
        
        # Verify Output
        with open("data/transactions.json", "r") as f:
            data = json.load(f)
            
        print(f"Generated {len(data)} records.")
        
        first_record = data[0]
        print("First Record:", first_record)
        
        assert first_record['entity'] == "C001"
        assert first_record['amount'] == 33.0
        assert first_record['category'] == "SEM"
        assert first_record['date'] == "2023-01-01" # Default
        
        print("PASS: New dataset mapping detected and processed correctly.")
        
    except Exception as e:
        print(f"FAIL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_ingestion()

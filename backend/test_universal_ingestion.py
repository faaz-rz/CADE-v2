
import sys
import os
import yaml
import pandas as pd
from datetime import date

# Add the backend directory to sys.path
sys.path.append(os.getcwd())

from app.services.ingestion import IngestionService
from app.models.canonical import CanonicalFinancialRecord

def test_universal_ingestion():
    print("Testing Universal Ingestion Adapter...")

    # 1. Create a mock CSV matching strict "Spend Analysis" format
    # Note: 'Category' is missing to test default behavior, 'Supplier' -> entity, 'TotalCost' -> amount
    csv_content = b"PurchaseDate,Supplier,TotalCost\n2023-01-01,TechStore,100.00\n2023-01-02,SoftCorp,500.50"
    filename = "test_universal.csv"

    # 2. Load Default Config
    with open("config/default_mapping.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    print(f"Loaded Config: {config}")

    try:
        # 3. Process
        result = IngestionService.process_file(csv_content, filename, mapping_config=config)
        print("Success:", result)
        
        # Verify result content (mocking internal check)
        assert result['processed_canonical'] == 2
        assert result['errors'] == 0
        print("Verification PASSED: Processed 2 records successfully.")

    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

def test_custom_mapping():
    print("\nTesting Custom Mapping (New Company)...")
    
    # Custom CSV format
    csv_content = b"trx_date,vendor_name,expense_amt,type\n2023-05-01,CloudAWS,1200.00,Hosting"
    filename = "new_company.csv"
    
    # Custom Config
    custom_config = {
        "column_mapping": {
            "date": "trx_date",
            "entity": "vendor_name",
            "amount": "expense_amt",
            "category": "type"
        },
        "date_format": "%Y-%m-%d",
        "defaults": {
            "currency": "EUR"
        }
    }

    try:
        result = IngestionService.process_file(csv_content, filename, mapping_config=custom_config)
        print("Custom Mapping Success:", result)
        assert result['processed_canonical'] == 1
        print("Verification PASSED: Processed custom dataset successfully.")
    except Exception as e:
        print(f"Custom Mapping FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_universal_ingestion()
    test_custom_mapping()

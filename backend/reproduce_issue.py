
import sys
import os

# Add the backend directory to sys.path to allow importing app modules
sys.path.append(os.getcwd())

from app.services.ingestion import IngestionService

def test_missing_category():
    # CSV content without 'category' column
    csv_content = b"PurchaseDate,Supplier,TotalCost\n2023-01-01,TechStore,100.00"
    filename = "test.csv"

    print(f"Testing ingestion with content: {csv_content}")
    try:
        result = IngestionService.ingest_file(csv_content, filename)
        print("Success:", result)
    except Exception as e:
        print(f"Caught expected error: {e}")

if __name__ == "__main__":
    test_missing_category()

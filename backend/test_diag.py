import asyncio
import traceback
import sys
import os

sys.path.append(os.getcwd())

from app.services.ingestion import IngestionService
from app.services.decision_engine import DecisionEngine
from app.services.decision_store import DecisionStore

async def main():
    try:
        with open("large_demo_dataset.xlsx", "rb") as f:
            content = f.read()
        
        print("Starting ingestion...")
        DecisionStore.clear()
        
        # We need mapping_config if any? In upload.py it passes none.
        result = IngestionService.ingest_file(content, "large_demo_dataset.xlsx")
        print(f"Ingestion processed {result.rows_accepted} rows.")
        
        print("Calling analyze_uploaded_data...")
        decisions = await DecisionEngine.analyze_uploaded_data()
        print(f"Success! {len(decisions)} decisions generated.")
    except Exception as e:
        print("!!! ERROR OCCURRED !!!")
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())

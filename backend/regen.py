import asyncio
import sys
import os

sys.path.append(os.getcwd())
from app.services.decision_engine import DecisionEngine
from app.services.decision_store import DecisionStore

async def main():
    DecisionStore.enable_db()
    DecisionStore.clear()
    decisions = await DecisionEngine.analyze_uploaded_data()
    print(f"Generated {len(decisions)} decisions")

if __name__ == "__main__":
    asyncio.run(main())

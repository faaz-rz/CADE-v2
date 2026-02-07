
import json
import os
from typing import Dict, List, Optional
from pydantic import BaseModel
from app.models.canonical import CanonicalFinancialRecord

# Constants for Decision Logic
HIGH_SPEND_THRESHOLD = 5000.0  # If total spend > $5k -> Flag
HIGH_FREQUENCY_THRESHOLD = 5   # If transactions > 5 -> Flag

class VendorStats(BaseModel):
    entity: str
    total_spend: float
    transaction_count: int
    avg_value: float
    spend_period: str = "Uploaded Period" # Explicit window

class SpendingAnalyzer:
    DATA_FILE = "data/transactions.json"

    @staticmethod
    def get_vendor_stats() -> Dict[str, VendorStats]:
        """
        Reads persisted transactions and aggregates spend by vendor.
        Returns: Dict[VendorName, VendorStats]
        """
        if not os.path.exists(SpendingAnalyzer.DATA_FILE):
            return {}

        try:
            with open(SpendingAnalyzer.DATA_FILE, "r") as f:
                raw_data = json.load(f)
            
            records = [CanonicalFinancialRecord(**r) for r in raw_data]
        except Exception as e:
            print(f"Error loading transactions: {e}")
            return {}

        stats_map: Dict[str, VendorStats] = {}

        for r in records:
            if r.entity not in stats_map:
                stats_map[r.entity] = VendorStats(
                    entity=r.entity,
                    total_spend=0.0,
                    transaction_count=0,
                    avg_value=0.0
                )
            
            stats = stats_map[r.entity]
            stats.total_spend += r.amount
            stats.transaction_count += 1
        
        # Calculate averages
        for entity, stats in stats_map.items():
            if stats.transaction_count > 0:
                stats.avg_value = stats.total_spend / stats.transaction_count
                
        return stats_map

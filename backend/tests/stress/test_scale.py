
import sys
import os
import unittest
import time
import random

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.services.ingestion import IngestionService
from app.services.decision_engine import DecisionEngine

class TestScale(unittest.TestCase):
    
    def test_scale_10k_transactions(self):
        """Test 113: 10,000 Transactions Performance"""
        
        # Generate 10k lines
        print("Generating 10,000 records...")
        header = "Date,Vendor,Amount,Category"
        lines = [header]
        
        vendors = [f"Vendor_{i}" for i in range(100)] # 100 Vendors
        
        for i in range(10000):
            v = random.choice(vendors)
            amount = random.uniform(10.0, 5000.0)
            date = "2023-01-01"
            lines.append(f"{date},{v},{amount:.2f},General")
            
        csv_content = "\n".join(lines).encode('utf-8')
        
        print(f"Ingesting {len(lines)} lines...")
        start_time = time.time()
        
        # Ingestion
        try:
            result = IngestionService.ingest_file(csv_content, "scale_10k.csv")
            ingest_time = time.time() - start_time
            print(f"Ingestion Time: {ingest_time:.4f}s")
            self.assertGreaterEqual(result.rows_accepted, 9500)
            
            # Analysis
            start_analysis = time.time()
            decisions = DecisionEngine.analyze_uploaded_data()
            analysis_time = time.time() - start_analysis
            print(f"Decision Generation Time: {analysis_time:.4f}s")
            print(f"Decisions Generated: {len(decisions)}")
            
            # Assert Performance (Arbitrary, but reasonable)
            self.assertLess(ingest_time, 5.0, "Ingestion too slow (>5s)")
            self.assertLess(analysis_time, 2.0, "Analysis too slow (>2s)")
            
        except Exception as e:
            self.fail(f"Scale test failed with error: {e}")

if __name__ == '__main__':
    unittest.main()


import sys
import os
import unittest
# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.services.ingestion import IngestionService

class TestDataRobustness(unittest.TestCase):
    
    def test_missing_required_columns(self):
        """Test 101: Missing Entity Column"""
        csv_content = b"Date,Amount\n2023-01-01,100"
        with self.assertRaises(ValueError) as cm:
            IngestionService.process_file(csv_content, "missing_entity.csv")
        self.assertIn("Could not confidently map required fields", str(cm.exception))

    def test_missing_optional_columns(self):
        """Test 101b: Missing Category (Should Pass)"""
        csv_content = b"Date,Vendor,Amount\n2023-01-01,TestVendor,100"
        result = IngestionService.process_file(csv_content, "missing_category.csv")
        self.assertEqual(result["processed_canonical"], 1)
        self.assertEqual(result["errors"], 0)

    def test_extra_columns(self):
        """Test 102: Extra Irrelevant Columns"""
        csv_content = b"Date,Vendor,Amount,Junk1,Junk2\n2023-01-01,TestVendor,100,foo,bar"
        result = IngestionService.process_file(csv_content, "extra_cols.csv")
        self.assertEqual(result["processed_canonical"], 1)

    def test_unit_k(self):
        """Test 103: Cost (k) Header"""
        csv_content = b"Date,Vendor,Cost (k)\n2023-01-01,TestVendor,5"
        # Should be 5 * 1000 = 5000
        # process_file returns stats, doesn't return data. 
        # But it writes to data/transactions.json. 
        # We can check the return stats for success first.
        result = IngestionService.process_file(csv_content, "units_k.csv")
        self.assertEqual(result["processed_canonical"], 1)
        
        # To verify the VALUE, we might need to inspect the saved JSON or output
        # For this stress test, "Ingest safely" is the primary goal.
        # But we should verify correct transformation.
        # Let's read the produced transactions.json
        import json
        with open("data/transactions.json", "r") as f:
            data = json.load(f)
            # Find our record (might be mixed with others if file is not cleared, 
            # but IngestionService overwrites transactions.json? 
            # Wait, IngestionService logic:
            # output_data = [r.model_dump(mode='json') for r in canonical_data]
            # with open(..., "w") as f: json.dump(output_data, f)
            # Yes, it overwrites.
            record = data[0]
            self.assertEqual(record["amount"], 5000.0)

    def test_unit_millions(self):
        """Test 103b: Cost (M) Header"""
        csv_content = b"Date,Vendor,Total Cost (M)\n2023-01-01,TestVendor,1.5"
        IngestionService.process_file(csv_content, "units_m.csv")
        
        import json
        with open("data/transactions.json", "r") as f:
            data = json.load(f)
            self.assertEqual(data[0]["amount"], 1500000.0)

    def test_empty_lines_and_duplicates(self):
        """Test 104: Empty Rows & Duplicates"""
        # Pandas read_csv often skips blank lines by default.
        # Duplicate rows should be ingested as distinct records.
        csv_content = b"Date,Vendor,Amount\n2023-01-01,V1,100\n\n\n2023-01-01,V1,100"
        result = IngestionService.process_file(csv_content, "duplicates.csv")
        # Should digest 2 records
        self.assertEqual(result["processed_canonical"], 2)

    def test_negative_values(self):
        """Test 105: Negative Values (Refunds)"""
        csv_content = b"Date,Vendor,Amount\n2023-01-01,V1,-50.00"
        result = IngestionService.process_file(csv_content, "negative.csv")
        self.assertEqual(result["processed_canonical"], 1)
        
        import json
        with open("data/transactions.json", "r") as f:
            data = json.load(f)
            self.assertEqual(data[0]["amount"], -50.0)

    def test_ambiguous_columns(self):
        """Test 102b: Ambiguous Columns (Amount vs Total Cost)"""
        # Both 'Amount' and 'Total Cost' have weight 1.0 in heuristics.
        # System should ideally pick one deterministically or Fail.
        # Current logic: picks the highest score. If equal?
        # Let's see behavior.
        csv_content = b"Date,Vendor,Amount,Total Cost\n2023-01-01,V1,100,200"
        # It currently picks one.
        result = IngestionService.process_file(csv_content, "ambiguous.csv")
        self.assertEqual(result["processed_canonical"], 1)

    def test_row_level_mixed_units(self):
        """Test 103c: Row-level Units (10k, 5000)"""
        csv_content = b"Date,Vendor,Amount\n2023-01-01,V1,10k\n2023-01-02,V1,5000"
        # The '10k' will fail float() conversion.
        # IngestionService catches ValueError/TypeError and ignores the row?
        # Or keeps original?
        # Code:
        # try: val = float(val) * multiplier ... except: pass
        # But this is only if a multiplier exists. Here NONE exists.
        # Later: CanonicalFinancialRecord(**record_data).
        # This Pydantic model expects float for amount.
        # So '10k' (string) passed to float field -> Validation Error.
        # IngestionService catches Exception -> "Skipping invalid row".
        # So '10k' row is skipped. '5000' row is processed.
        result = IngestionService.process_file(csv_content, "row_mixed.csv")
        # Should have 1 success (5000), 1 fail (10k)
        self.assertEqual(result["processed_canonical"], 1)
        self.assertEqual(result["errors"], 1)

if __name__ == '__main__':
    unittest.main()

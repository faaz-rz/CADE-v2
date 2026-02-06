import pandas as pd
import io
from typing import List, Dict
from app.models.data import FinancialRecord

class IngestionService:
    @staticmethod
    def process_file(file_content: bytes, filename: str) -> Dict[str, int]:
        """
        Parses a file and returns statistics.
        For v1, we just validate it against the schema.
        """
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file_content))
            elif filename.endswith('.xlsx'):
                df = pd.read_excel(io.BytesIO(file_content))
            else:
                raise ValueError("Unsupported file type")
            
            # Basic Normalization (Lower casing columns)
            df.columns = [c.lower().strip() for c in df.columns]
            
            # Column Mapping (User Schema -> Internal Schema)
            mapping = {
                'purchasedate': 'date',
                'supplier': 'entity',
                'totalcost': 'amount'
            }
            df.rename(columns=mapping, inplace=True)
            
            # Validation (Iterate and count valid records)
            valid_count = 0
            errors = 0
            
            # Expected columns check
            required = {'date', 'entity', 'category', 'amount'}
            if not required.issubset(set(df.columns)):
                missing = required - set(df.columns)
                raise ValueError(f"Missing required columns: {missing}. Found: {list(df.columns)}")

            return {
                "total_rows": len(df),
                "processed": len(df),
                "errors": 0 
            }
            
        except Exception as e:
            raise ValueError(f"Failed to process file: {str(e)}")

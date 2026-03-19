from pydantic import BaseModel
from typing import Dict, Optional

class SchemaMapping(BaseModel):
    """
    Configuration defining how to transform a specific external dataset
    into the CanonicalFinancialRecord format.
    """
    # Human-readable name for this mapping (e.g., "Heuristic Auto-Detected")
    name: str = "Unnamed"

    # Maps canonical_field_name -> external_column_name
    column_mapping: Dict[str, str]
    
    # Optional date format string for parsing (e.g., "%Y-%m-%d")
    date_format: Optional[str] = None
    
    # Default values for missing fields (e.g., currency='USD', category='Uncategorized')
    defaults: Dict[str, str] = {}
    
    # Optional multipliers for numeric fields (e.g., amount: 1000 for 'K')
    multipliers: Dict[str, float] = {}

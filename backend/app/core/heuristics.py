
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel
from app.core.mappings import SchemaMapping

class HeuristicMatch(BaseModel):
    canonical_field: str
    source_column: str
    confidence: float
    reason: str

class HeuristicResult(BaseModel):
    is_valid: bool
    mapping: Optional[SchemaMapping]
    matches: List[HeuristicMatch]
    missing_required: List[str]
    confidence_score: float # Overall score

class HeuristicMapper:
    """
    Smartly guesses the schema mapping based on column names using keyword matching.
    Returns confidence scores to ensure safety.
    """
    
    # Vocabulary for semantic matching with weights
    # (keyword, weight) - Weight 1.0 = Strong, 0.8 = Medium
    KEYWORDS = {
        "entity": [
            ("entity", 1.0), ("vendor", 1.0), ("supplier", 1.0), ("merchant", 1.0), 
            ("company", 0.9), ("payee", 0.9), ("business", 0.8), ("source", 0.7), ("name", 0.6)
        ],
        "amount": [
            ("amount", 1.0), ("total cost", 1.0), ("total_cost", 1.0), ("price", 0.9), 
            ("value", 0.8), ("spend", 0.9), ("payment", 0.8), ("expenses", 0.8), ("cost", 0.8)
        ],
        "date": [
            ("date", 1.0), ("time", 0.8), ("day", 0.8), ("period", 0.7), 
            ("when", 0.6), ("transaction_date", 1.0), ("purchase_date", 1.0)
        ],
        "category": [
            ("category", 1.0), ("type", 0.9), ("class", 0.8), 
            ("description", 0.7), ("industry", 0.7), ("segment", 0.6), ("campaign", 0.7)
        ],
    }

    REQUIRED_FIELDS = ["entity", "amount"]
    CONFIDENCE_THRESHOLD = 0.8

    @staticmethod
    def analyze_columns(columns: List[str]) -> HeuristicResult:
        """
        Analyzes columns and returns a detailed heuristic report.
        """
        columns_lower = {col.lower(): col for col in columns}
        used_columns = set()
        matches: List[HeuristicMatch] = []
        mapping_dict = {}

        def find_best_match(target_field: str) -> Optional[HeuristicMatch]:
            # 1. Exact Name Match (Confidence 1.0)
            if target_field in columns_lower:
                return HeuristicMatch(
                    canonical_field=target_field,
                    source_column=columns_lower[target_field],
                    confidence=1.0,
                    reason="Exact Match"
                )

            # 2. Keyword Search
            best_match = None
            best_score = 0.0

            for keyword, weight in HeuristicMapper.KEYWORDS.get(target_field, []):
                for col_lower, original_col in columns_lower.items():
                    if col_lower in used_columns:
                        continue
                    
                    if keyword in col_lower:
                        # Bonus for exact keyword match vs substring?
                        # For now simple containment
                        if weight > best_score:
                            best_score = weight
                            best_match = original_col
            
            if best_match:
                return HeuristicMatch(
                    canonical_field=target_field,
                    source_column=best_match,
                    confidence=best_score,
                    reason=f"Matched keyword '{best_match}'"
                )
            return None

        # Process Required Fields
        missing = []
        for field in HeuristicMapper.REQUIRED_FIELDS:
            match = find_best_match(field)
            if match and match.confidence >= HeuristicMapper.CONFIDENCE_THRESHOLD:
                matches.append(match)
                mapping_dict[field] = match.source_column
                used_columns.add(match.source_column.lower())
            else:
                missing.append(field)

        # Process Optional Fields
        for field in ["date", "category"]:
            match = find_best_match(field)
            if match and match.confidence >= 0.6: # Lower threshold for optional
                matches.append(match)
                mapping_dict[field] = match.source_column
                used_columns.add(match.source_column.lower())

        # Validation
        if missing:
             return HeuristicResult(
                 is_valid=False,
                 mapping=None,
                 matches=matches,
                 missing_required=missing,
                 confidence_score=0.0
             )
        
        # Calculate avg confidence of required fields
        avg_confidence = sum(m.confidence for m in matches if m.canonical_field in HeuristicMapper.REQUIRED_FIELDS) / len(HeuristicMapper.REQUIRED_FIELDS)
        
        # Build Schema Object
        defaults = {"currency": "USD"}
        if "date" not in mapping_dict:
             defaults["date"] = "2023-01-01" # Default snapshot
        if "category" not in mapping_dict:
             defaults["category"] = "Uncategorized"

        multipliers = {}
        # Unit Detection for Amount
        if "amount" in mapping_dict:
            src_col = mapping_dict["amount"]
            src_lower = src_col.lower()
            
            if "(k" in src_lower or " thousands" in src_lower or "(000)" in src_lower:
                multipliers["amount"] = 1000.0
            elif "(m" in src_lower or " millions" in src_lower:
                multipliers["amount"] = 1000000.0

        schema = SchemaMapping(
            name="Heuristic Auto-Detected",
            column_mapping=mapping_dict,
            defaults=defaults,
            multipliers=multipliers
        )

        return HeuristicResult(
            is_valid=True,
            mapping=schema,
            matches=matches,
            missing_required=[],
            confidence_score=avg_confidence
        )

    @staticmethod
    def detect_mapping(columns: List[str]) -> Optional[SchemaMapping]:
        """
        Legacy wrapper for backward compatibility, but strictly validates now.
        """
        result = HeuristicMapper.analyze_columns(columns)
        if result.is_valid and result.confidence_score >= HeuristicMapper.CONFIDENCE_THRESHOLD:
            return result.mapping
        return None

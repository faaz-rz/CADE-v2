
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel
import pandas as pd
from rapidfuzz import fuzz
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
            
            if "(k" in src_lower or " thousands" in src_lower or "(thousands)" in src_lower or "000s" in src_lower or "(000)" in src_lower:
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

def find_header_row(df: pd.DataFrame) -> int:
    """Finds the best header row."""
    best_row = 0
    best_score = 0
    
    limit = min(20, len(df))
    for i in range(limit):
        row = df.iloc[i]
        
        total_cells = len(row)
        non_null_str = 0
        has_large_number = False
        has_date_like = False
        
        for val in row:
            if pd.isna(val): continue
            s = str(val).strip()
            if not s: continue
            
            non_null_str += 1
            if any(char.isdigit() for char in s):
                if '-' in s or '/' in s:
                    has_date_like = True
                else:
                    digits = sum(1 for c in s if c.isdigit())
                    if digits > 3 and digits / len(s) > 0.5:
                        has_large_number = True
                        
        score = 0
        
        # Penalize sparse rows early
        if 0 < non_null_str <= 1 and total_cells > 2:
            score -= 5
            
        # Add points per keyword matched
        row_str = " ".join([str(v).lower() for v in row if not pd.isna(v)])
        matched_kws = sum(1 for kw in ["amount", "cost", "spend", "vendor", "date", "category", "total", "who we paid"] if kw in row_str.split() or kw in row_str)
        if matched_kws > 0:
            score += matched_kws * 2
            
        if total_cells > 0 and (non_null_str / total_cells) > 0.6:
            score += 2
            
        if has_large_number: score -= 2
        if has_date_like: score -= 1
        
        if score > best_score:
            best_score = score
            best_row = i
            
    if best_score <= 1:
        return 0
    return best_row

async def map_columns(columns: List[str], df_sample: pd.DataFrame, explicit_config: dict = None) -> tuple[SchemaMapping, str, float]:
    """5-tier pipeline mapping"""
    # 1. Explicit
    if explicit_config:
        return SchemaMapping(**explicit_config), "explicit", 1.0
        
    # 2. YAML
    import os, yaml
    config_dir = "config"
    if os.path.exists(config_dir):
        for filename in os.listdir(config_dir):
            if filename.endswith((".yaml", ".yml")):
                try:
                    with open(os.path.join(config_dir, filename), "r") as f:
                        candidate = yaml.safe_load(f)
                        if not candidate or "column_mapping" not in candidate: continue
                        req_cols = [c for fld, c in candidate["column_mapping"].items() if fld in ["entity", "amount"]]
                        if all(c in columns for c in req_cols):
                            return SchemaMapping(**candidate), "yaml", 1.0
                except Exception:
                    continue
                    
    # 3. Fuzzy
    FUZZY_ALIASES = {
        "entity": ['vendor', 'supplier', 'vendor name', 'supplier name', 'company',
                   'payee', 'merchant', 'counterparty', 'entity', 'vendor_name',
                   'beneficiary', 'paid to', 'recipient', 'business name',
                   'contractor', 'service provider', 'creditor', 'who we paid'],
        "amount": ['amount', 'spend', 'cost', 'total', 'value', 'payment',
                   'invoice amount', 'net amount', 'gross amount', 'total amount',
                   'transaction amount', 'debit', 'charge', 'fee', 'price',
                   'subtotal', 'net', 'gross', 'amt', 'sum', 'expenditure',
                   'actual spend', 'actual cost', 'total cost', 'billed amount', 'how much'],
        "date": ['date', 'transaction date', 'invoice date', 'payment date',
                 'posting date', 'value date', 'booking date', 'tx date',
                 'txn date', 'period', 'month', 'year', 'fiscal period',
                 'bill date', 'purchase date', 'created date', 'date paid', 'when'],
        "category": ['category', 'type', 'expense type', 'spend category',
                     'cost category', 'gl category', 'account type', 'department',
                     'cost center', 'division', 'team', 'business unit', 'segment',
                     'expense category', 'classification', 'class', 'group', 'which team'],
        "gl_code": ['gl code', 'gl account', 'account code', 'account number',
                    'ledger code', 'account', 'chart of accounts', 'coa',
                    'account id', 'natural account', 'cost account', 'gl#'],
        "currency": ['currency', 'ccy', 'currency code', 'iso code'],
        "po_number": ['po number', 'po#', 'purchase order', 'order number',
                      'po ref', 'order ref', 'order id', 'purchase order number']
    }
    
    mapping_dict = {}
    confidence_sum = 0
    matched_fields = 0
    
    for field, aliases in FUZZY_ALIASES.items():
        best_col = None
        best_score = 0
        for col in columns:
            if col in mapping_dict.values(): continue
            for alias in aliases:
                score = fuzz.token_set_ratio(col.lower(), alias.lower())
                if score > best_score:
                    best_score = score
                    best_col = col
                    
        if best_score > 80:
            mapping_dict[field] = best_col
            confidence_sum += best_score / 100.0
            matched_fields += 1
            
    multipliers = {}
    if "amount" in mapping_dict:
        src_lower = mapping_dict["amount"].lower()
        if "(k" in src_lower or " thousands" in src_lower or "(thousands)" in src_lower or "000s" in src_lower or "(000)" in src_lower:
            multipliers["amount"] = 1000.0
        elif "(m" in src_lower or " millions" in src_lower:
            multipliers["amount"] = 1000000.0
            
    if "entity" in mapping_dict and "amount" in mapping_dict:
        avg_conf = (confidence_sum / matched_fields) if matched_fields > 0 else 0
        return SchemaMapping(name="Fuzzy Auto-Detected", column_mapping=mapping_dict, defaults={"currency": "USD", "category": "Uncategorized"}, multipliers=multipliers), "fuzzy", avg_conf
        
    # 4. LLM
    from app.core.llm_column_mapper import map_columns_with_llm
    sample_values = {}
    for col in columns:
        sample_values[col] = df_sample[col].dropna().head(3).tolist()
        
    llm_map = await map_columns_with_llm(columns, sample_values)
    if llm_map:
        clean_map = {v: k for k, v in llm_map.items() if v in ["entity", "amount", "date", "category", "currency", "gl_code", "cost_center", "po_number"] and k in columns}
        if "entity" in clean_map.values() and "amount" in clean_map.values():
            flipped = {v:k for k,v in clean_map.items()}
            return SchemaMapping(name="LLM Fallback", column_mapping=flipped, defaults={"currency": "USD", "category": "Uncategorized"}, multipliers={}), "llm", 0.9
            
    return None, "none", 0.0

import pandas as pd
import io
import json
import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.models.canonical import CanonicalFinancialRecord
from app.core.file_detector import detect_file_type
from app.core.heuristics import find_header_row, map_columns
from app.core.value_cleaners import clean_amount, clean_date, clean_vendor_name, clean_currency

class RejectionReason(BaseModel):
    row: int
    reason: str
    raw: str

class IngestResult(BaseModel):
    status: str = "success"
    rows_total: int = 0
    rows_accepted: int = 0
    rows_rejected: int = 0
    sheets_processed: List[str] = []
    mapping_method: str = "none"
    confidence_score: float = 0.0
    column_mapping: Dict[str, str] = {}
    rejections_summary: List[RejectionReason] = []
    decisions_generated: int = 0
    warnings: List[str] = []
    records: List[CanonicalFinancialRecord] = []

class IngestError(ValueError):
    pass

class IngestionService:
    @staticmethod
    def _ingest_sheet(df_raw: pd.DataFrame, sheet_name: str, filename: str, mapping_config: dict = None) -> tuple[List[CanonicalFinancialRecord], List[RejectionReason], Dict[str, str], str, float, List[str]]:
        # 3. find_header_row()
        header_idx = find_header_row(df_raw)
        
        if header_idx >= 0:
            df = df_raw.iloc[header_idx:].copy()
            new_cols = []
            for c in df.iloc[0]:
                new_cols.append(str(c).strip() if pd.notna(c) else f"Unnamed_{len(new_cols)}")
            df.columns = new_cols
            df = df.iloc[1:].reset_index(drop=True)
        else:
            # Fallback if somehow negative (though find_header_row returns 0 min)
            df = df_raw.copy()
            df.columns = [str(c).strip() if pd.notna(c) else f"Unnamed_{i}" for i, c in enumerate(df.columns)]
            
        columns = df.columns.tolist()
        print("COLUMNS: ", columns)
        
        # 4. map_columns() -> YAML -> fuzzy -> LLM fallback
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                mapping, method, conf = pool.submit(asyncio.run, map_columns(columns, df.head(10), explicit_config=mapping_config)).result()
        except RuntimeError:
            mapping, method, conf = asyncio.run(map_columns(columns, df.head(10), explicit_config=mapping_config))
        
        # 5. check confidence >= 0.80, raise IngestError if below
        if not mapping or conf < 0.8:
            raise IngestError(f"Ambiguous Dataset Structure. Confidence score ({conf:.2f}) below threshold (0.80). System refused to guess.")
            
        # 6. per row: clean all values, skip if vendor or amount is None
        records = []
        rejections = []
        warnings = []
        
        currency_default = mapping.defaults.get("currency", "INR")
        category_default = mapping.defaults.get("category", "Uncategorized")
        
        for idx, row in df.iterrows():
            row_num = idx + 2 + header_idx
            raw_vals = row.to_dict()
            
            raw_amt = row.get(mapping.column_mapping.get("amount", ""))
            raw_entity = row.get(mapping.column_mapping.get("entity", ""))
            raw_date = row.get(mapping.column_mapping.get("date", ""))
            raw_cat = row.get(mapping.column_mapping.get("category", ""))
            raw_ccy = row.get(mapping.column_mapping.get("currency", ""))
            raw_gl = row.get(mapping.column_mapping.get("gl_code", ""))
            raw_cc = row.get(mapping.column_mapping.get("cost_center", ""))
            raw_po = row.get(mapping.column_mapping.get("po_number", ""))
            raw_desc = row.get(mapping.column_mapping.get("description", ""))
            
            amt = clean_amount(raw_amt)
            entity = clean_vendor_name(raw_entity)
            dt = clean_date(raw_date)
            
            if amt is None:
                rejections.append(RejectionReason(row=row_num, reason="amount could not be parsed or is zero", raw=str(raw_amt)))
                continue
                
            if entity == "UNKNOWN" or not raw_entity or pd.isna(raw_entity):
                rejections.append(RejectionReason(row=row_num, reason="missing vendor name", raw=str(raw_entity)))
                continue
                
            if dt is None:
                if "date" in mapping.column_mapping:
                    rejections.append(RejectionReason(row=row_num, reason="date could not be parsed", raw=str(raw_date)))
                    continue
                else:
                    from datetime import date
                    dt = date(2023, 1, 1)
                    
            ccy = clean_currency(raw_ccy) if "currency" in mapping.column_mapping else currency_default
            if "currency" not in mapping.column_mapping:
                warnings.append("No currency column found — defaulted to INR")
                
            cat = str(raw_cat).strip() if pd.notna(raw_cat) and "category" in mapping.column_mapping else category_default
            
            if "amount" in mapping.multipliers and amt is not None:
                amt = float(amt) * mapping.multipliers["amount"]

            try:
                rec = CanonicalFinancialRecord(
                    date=dt,
                    amount=amt,
                    category=cat,
                    entity=entity,
                    currency=ccy,
                    gl_code=str(raw_gl).strip() if pd.notna(raw_gl) else None,
                    cost_center=str(raw_cc).strip() if pd.notna(raw_cc) else None,
                    po_number=str(raw_po).strip() if pd.notna(raw_po) else None,
                    description=str(raw_desc).strip() if pd.notna(raw_desc) else None,
                    source_file=f"{filename} - {sheet_name}" if sheet_name != "default" else filename
                )
                records.append(rec)
            except Exception as e:
                rejections.append(RejectionReason(row=row_num, reason=str(e), raw=str(raw_vals)))
                
        unique_warnings = list(set(warnings))
        return records, rejections, mapping.column_mapping, method, conf, unique_warnings

    @staticmethod
    def ingest_file(file_content: bytes, filename: str, mapping_config: dict = None) -> IngestResult:
        """LAYER 5 \u2014 MULTI-SHEET HANDLER & MAIN INGESTION REWRITE"""
        import tempfile
        import os
        
        fd, temp_path = tempfile.mkstemp(suffix=f"_{filename}")
        with os.fdopen(fd, 'wb') as f:
            f.write(file_content)
            
        try:
            # 1. detect_file_type()
            file_meta = detect_file_type(temp_path)
            
            all_records = []
            all_rejections = []
            all_warnings = []
            final_mapping = {}
            final_method = "none"
            final_conf = 0.0
            sheets_processed = []

            # 2. if multi-sheet Excel -> ingest_multi_sheet() natively embedded here
            if file_meta["format"] in ['xlsx', 'xls', 'ods']:
                sheets_to_process = file_meta["recommended_sheets"] or file_meta["sheet_names"][:1]
                xls = pd.ExcelFile(temp_path)
                try:
                    for sheet in sheets_to_process:
                        df_raw = pd.read_excel(xls, sheet_name=sheet, header=None)
                        try:
                            recs, rejs, col_map, method, conf, warns = IngestionService._ingest_sheet(df_raw, sheet, filename, mapping_config=mapping_config)
                            all_records.extend(recs)
                            all_rejections.extend(rejs)
                            all_warnings.extend(warns)
                            final_mapping = col_map
                            final_method = method
                            final_conf = conf
                            sheets_processed.append(sheet)
                        except IngestError as e:
                            all_warnings.append(f"Skipped sheet '{sheet}': {str(e)}")
                finally:
                    xls.close()
                if not sheets_processed:
                    raise IngestError("All recommended sheets failed to parse or fell below confidence threshholds.")
            else:
                enc = file_meta.get("encoding", "utf-8")
                df_raw = pd.read_csv(temp_path, encoding=enc, header=None)
                recs, rejs, col_map, method, conf, warns = IngestionService._ingest_sheet(df_raw, "default", filename, mapping_config=mapping_config)
                all_records.extend(recs)
                all_rejections.extend(rejs)
                all_warnings.extend(warns)
                final_mapping = col_map
                final_method = method
                final_conf = conf
                sheets_processed.append("default")
                
            # 7. deduplicate by (vendor_name, amount, transaction_date)
            dedup_records = []
            seen = set()
            for r in all_records:
                key = (r.entity, r.amount, r.date)
                if key not in seen:
                    seen.add(key)
                    dedup_records.append(r)
            
            duplicates_removed = len(all_records) - len(dedup_records)
            if duplicates_removed > 0:
                all_warnings.append(f"Removed {duplicates_removed} duplicate row(s) across sheets.")
                
            # 8. persist to database (existing logic unchanged)
            data_dir = "data"
            os.makedirs(data_dir, exist_ok=True)
            output_data = [r.model_dump(mode='json') for r in dedup_records]
            
            with open(os.path.join(data_dir, "transactions.json"), "w") as f:
                json.dump(output_data, f, indent=2)

            # 9. return IngestResult
            res = IngestResult(
                status="success",
                rows_total=file_meta.get("estimated_row_count", 0) if file_meta else 0,
                rows_accepted=len(dedup_records),
                rows_rejected=len(all_rejections),
                sheets_processed=sheets_processed,
                mapping_method=final_method,
                confidence_score=final_conf,
                column_mapping=final_mapping,
                rejections_summary=all_rejections[:10],
                decisions_generated=len(dedup_records),
                warnings=all_warnings,
                records=dedup_records
            )
            return res
            
        finally:
            os.remove(temp_path)

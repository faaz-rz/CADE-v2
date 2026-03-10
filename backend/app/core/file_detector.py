import os
import pandas as pd
import chardet

def detect_file_type(filepath: str) -> dict:
    meta = {
        "format": "csv",
        "encoding": "utf-8",
        "sheet_names": [],
        "recommended_sheets": [],
        "estimated_row_count": 0
    }
    
    ext = filepath.lower().split(".")[-1]
    if ext in ["xlsx", "xls", "ods"]:
        meta["format"] = ext
        try:
            with pd.ExcelFile(filepath) as xls:
                meta["sheet_names"] = xls.sheet_names
                # Recommend sheets based on naming heuristics
                for sheet in xls.sheet_names:
                    name_lower = sheet.lower()
                    if any(x in name_lower for x in ["data", "expense", "transaction", "export", "sheet1", "report", "spend", "cost", "invoice", "vendor"]):
                        meta["recommended_sheets"].append(sheet)
                if not meta["recommended_sheets"] and xls.sheet_names:
                    meta["recommended_sheets"].append(xls.sheet_names[0])
            meta["estimated_row_count"] = 0 # Can't efficiently know without reading
        except Exception:
            pass
    else:
        # Detect encoding
        try:
            with open(filepath, 'rb') as f:
                raw = f.read(10000)
                res = chardet.detect(raw)
                meta["encoding"] = res["encoding"] or "utf-8"
            
            # Estimate row count
            with open(filepath, 'r', encoding=meta["encoding"]) as f:
                meta["estimated_row_count"] = sum(1 for _ in f)
        except Exception:
            pass
            
    return meta

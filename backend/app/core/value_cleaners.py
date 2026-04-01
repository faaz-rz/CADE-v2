import pandas as pd
import re
from dateutil import parser
from datetime import date

def clean_amount(val) -> float | None:
    if pd.isna(val) or val is None or val == "":
        return None
        
    s = str(val).strip().lower()
    # Check for accounting negative format (500.00)
    is_negative = False
    if s.startswith('(') and s.endswith(')'):
        is_negative = True
        s = s[1:-1]
    elif s.startswith('-'):
        is_negative = True
        s = s[1:]
        
    # Extract multiplier
    multiplier = 1.0
    if s.endswith('k'):
        multiplier = 1000.0
        s = s[:-1]
    elif s.endswith('m'):
        multiplier = 1000000.0
        s = s[:-1]
        
    # Remove chars
    s = re.sub(r'[^0-9.]', '', s)
    if not s:
        return None
        
    try:
        amt = float(s) * multiplier
        if is_negative:
            amt = -amt
        if amt == 0.0:
            return None # Reject zero amount
        return amt
    except ValueError:
        return None

def clean_date(val) -> date | None:
    if pd.isna(val) or val is None or val == "":
        return None
    s = str(val).strip()
    
    # Handle excel integer dates (e.g. 44941)
    if s.isdigit():
        try:
            # Excel epoch is 1899-12-30 usually
            return pd.to_datetime(int(s), unit='D', origin='1899-12-30').date()
        except:
            pass
            
    from datetime import datetime
    for fmt in ["%B %y", "%b %y", "%B %Y", "%b %Y"]:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass

    try:
        dt = parser.parse(s)
        return dt.date()
    except Exception:
        return None
        
def clean_vendor_name(val) -> str:
    if pd.isna(val) or val is None or str(val).strip() == "":
        return "UNKNOWN"
    s = str(val).strip().upper()
    # Remove suffixes
    for suffix in [", INC.", " INC.", ", LLC", " LLC", " CORP.", " CORP", " LTD.", " LTD"]:
        if s.endswith(suffix):
            s = s[:-len(suffix)]
    return s.strip()

def clean_currency(val) -> str:
    if pd.isna(val) or val is None:
        return "INR"
    s = str(val).strip().upper()
    if len(s) == 3 and s.isalpha():
        return s
    return "INR"

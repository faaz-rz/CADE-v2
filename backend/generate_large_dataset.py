import pandas as pd
import numpy as np
from datetime import date, timedelta
import random

def generate_large_dataset(filename="mock_enterprise_spend.csv", num_records=5000):
    np.random.seed(42)
    random.seed(42)
    
    categories = {
        "Cloud Infrastructure": ["AWS", "AZURE", "GOOGLE CLOUD", "SNOWFLAKE", "DATADOG"],
        "SaaS": ["SALESFORCE", "WORKDAY", "ZENDESK", "HUBSPOT", "SLACK", "DOCUSIGN", "NOTION", "ASANA", "GTLAB"],
        "Payroll": ["ADP", "GUSTO", "PAYCHEX", "DEEL", "RIPPLING"],
        "Professional Services": ["MCKINSEY", "DELOITTE", "PWC", "EY", "KPMG", "ACCENTURE", "SLALOM"],
        "Logistics": ["FEDEX", "UPS", "DHL", "XPO", "RYDER", "MAERSK"],
        "Marketing": ["GOOGLE ADS", "FACEBOOK ADS", "LINKEDIN ADS", "HUBSPOT", "MARKETO", "MAILCHIMP"],
        "Office Supplies": ["AMAZON BUSINESS", "STAPLES", "WBMASON", "OFFICE DEPOT"],
        "Travel & Expenses": ["DELTA", "UNITED", "AMERICAN AIRLINES", "MARRIOTT", "HILTON", "UBER", "LYFT"],
        "Legal": ["LATHAM & WATKINS", "KIRKLAND & ELLIS", "SKADDEN", "COOLEY", "WILSON SONSINI"]
    }

    # Generate dates across the last 2 years
    base_date = date(2023, 1, 1)
    dates = [base_date + timedelta(days=random.randint(0, 730)) for _ in range(num_records)]
    
    # Pre-select category & entity
    records = []
    
    for d in dates:
        cat = random.choice(list(categories.keys()))
        entity = random.choice(categories[cat])
        
        # Determine amount distributions by category
        if cat in ["Cloud Infrastructure", "Payroll"]:
            amount = round(np.random.lognormal(mean=10, sigma=1.5), 2)
        elif cat in ["Professional Services", "Legal"]:
            amount = round(np.random.normal(loc=25000, scale=8000), 2)
        elif cat == "SaaS":
            amount = round(np.random.lognormal(mean=8, sigma=1), 2)
        elif cat == "Marketing":
            amount = round(np.random.uniform(1000, 50000), 2)
        else:
            amount = round(np.random.uniform(50, 5000), 2)
            
        # Ensure positive
        if amount <= 0:
            amount = 100.0
            
        records.append({
            "date": d.isoformat(),
            "amount": amount,
            "category": cat,
            "entity": entity,
            "currency": "INR",
            "gl_code": f"GL-{random.randint(1000, 9999)}",
            "cost_center": f"CC-{random.randint(10, 99)}",
            "source_file": filename
        })
        
    df = pd.DataFrame(records)
    
    # Sort chronologically
    df.sort_values(by="date", inplace=True)
    df.to_csv(filename, index=False)
    print(f"Successfully generated {num_records} records into {filename}")

if __name__ == "__main__":
    generate_large_dataset()

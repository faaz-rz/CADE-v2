import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

NUM_ROWS = 5000

categories = ["SaaS", "Cloud Infrastructure", "Payroll", "Marketing", "Logistics", "Professional Services", "Office Supplies"]
vendors_by_cat = {
    "SaaS": ["Salesforce", "Workday", "Zendesk", "Slack", "HubSpot", "DocuSign", "Zoom"],
    "Cloud Infrastructure": ["AWS", "Google Cloud", "Azure", "Snowflake", "Datadog"],
    "Payroll": ["ADP", "Gusto", "Paychex"],
    "Marketing": ["Google Ads", "Facebook Ads", "LinkedIn Ads"],
    "Logistics": ["FedEx", "UPS", "DHL"],
    "Professional Services": ["McKinsey", "Deloitte", "LegalCorp"],
    "Office Supplies": ["Staples", "Amazon Business", "WBMason"]
}

data = []
start_date = datetime(2023, 1, 1)

for i in range(NUM_ROWS):
    cat = random.choice(categories)
    vendor = random.choice(vendors_by_cat[cat])
    
    # Generate realistic amounts
    if cat == "Cloud Infrastructure":
        amount = round(random.uniform(5000, 50000), 2)
    elif cat == "Payroll":
        amount = round(random.uniform(10000, 100000), 2)
    else:
        amount = round(random.uniform(100, 10000), 2)
        
    date = start_date + timedelta(days=random.randint(0, 365))
    
    data.append({
        "Date": date.strftime("%Y-%m-%d"),
        "Vendor": vendor,
        "Amount": amount,
        "Category": cat,
        "Currency": "USD"
    })

df = pd.DataFrame(data)
df.to_excel("large_demo_dataset.xlsx", index=False)
print("Successfully generated large_demo_dataset.xlsx with", NUM_ROWS, "rows.")

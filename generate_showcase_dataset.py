import os
import csv
from datetime import date, timedelta
import random

# Re-using the optimal showcase data logic from CADE's demo engine
from backend.app.api.demo import _build_demo_records, HOSPITAL_PROCUREMENT_ITEMS

def create_showcase_dataset():
    output_dir = "Showcase_Dataset"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Generate the Financial Ledger (Transactions) CSV
    print("Generating Financial Ledger...")
    records = _build_demo_records()
    records.sort(key=lambda x: x.date, reverse=True)
    
    ledger_file = os.path.join(output_dir, "CADE_Financial_Ledger.csv")
    with open(ledger_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Transaction_ID", "Date", "Amount", "Currency", "Vendor_Name", "Category", "Description", "GL_Code"])
        
        for i, r in enumerate(records):
            writer.writerow([
                f"TXN-{random.randint(10000, 99999)}-{i}",
                r.date.isoformat(),
                round(r.amount, 2),
                r.currency,
                r.entity,
                r.category,
                f"Monthly billing for {r.category}",
                f"GL-{random.randint(100, 900)}"
            ])
            
    # 2. Generate the Itemized Procurement CSV
    print("Generating Itemized Procurement Data...")
    items_file = os.path.join(output_dir, "CADE_Itemized_Procurement.csv")
    with open(items_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Item_Code", "Item_Name", "Vendor", "Category", "Unit_Type", "Unit_Price_INR", "Monthly_Quantity", "Total_Monthly_Spend"])
        
        for item in HOSPITAL_PROCUREMENT_ITEMS:
            monthly_spend = round(item["unit_price"] * item["monthly_qty"], 2)
            writer.writerow([
                item["item_code"],
                item["item_name"],
                item["vendor"],
                item["category"],
                item["unit"],
                item["unit_price"],
                item["monthly_qty"],
                monthly_spend
            ])
            
    # 3. Create a README
    readme_file = os.path.join(output_dir, "README.txt")
    with open(readme_file, "w", encoding="utf-8") as f:
        f.write("""CADE Showcase Dataset
=====================

This folder contains two datasets designed to perfectly demonstrate CADE's intelligence features.

1. CADE_Financial_Ledger.csv
Contains 12 months of simulated hospital spend data across 25 major vendors.
Features this highlights:
- Vendor Concentration Heatmaps (e.g., GE Healthcare dominance)
- Spend Trajectory & Benchmarking
- Financial Exposure limits

2. CADE_Itemized_Procurement.csv
Contains granular line-item purchasing data across multiple competing hospital vendors.
Features this highlights:
- Price Mismatch Engine (e.g., discovering Cipla sells Paracetamol cheaper than Abbott)
- Bulk Buy Intelligence (forward buying recommendations)
- Procurement Health Scorecard

To showcase the platform effortlessly:
-> Go to the CADE Dashboard.
-> The UI requires both files to be synchronized. 
-> You can upload the Ledger CSV via the 'Upload' tab, but to populate BOTH ledger and item-level data instantly for a full demo, simply click the "Load Demo" button in the application!
""")

    print(f"Success! Showcase dataset created in the '{output_dir}' folder.")

if __name__ == "__main__":
    import sys
    # Add project root to path so backend imports work
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    create_showcase_dataset()

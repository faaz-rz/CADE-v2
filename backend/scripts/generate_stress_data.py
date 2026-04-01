import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def generate_stress_dataset(num_rows=100000, num_vendors=500):
    print(f"Generating stress test dataset with {num_rows} rows and {num_vendors} vendors...")
    
    # Predefined categories and cost centers
    categories = [
        "Cloud Services", "IT Hardware", "Software Licensing", 
        "External Contractors", "Marketing & Advertising", 
        "Office Rent", "Travel & Entertainment", "Professional Services",
        "Utilities", "Logistics", "Office Supplies", "Insurance"
    ]
    
    cost_centers = ["Engineering", "Sales", "Marketing", "HR", "Operations", "Legal", "Finance"]
    
    # Generate unique vendor names
    vendor_names = [f"Vendor_{i:03d}_{random.choice(['Solutions', 'Inc', 'Group', 'Global', 'Technologies'])}" for i in range(num_vendors)]
    
    # Mapping vendors to specific categories for consistency
    vendor_category_map = {v: random.choice(categories) for v in vendor_names}
    
    # Generate data
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2026, 3, 31)
    date_range = (end_date - start_date).days
    
    data = []
    
    # Progress indicator
    chunk_size = num_rows // 10
    
    for i in range(num_rows):
        if i % chunk_size == 0:
            print(f"Progress: {(i / num_rows) * 100:.0f}%")
            
        vendor = random.choice(vendor_names)
        
        # Log-normal distribution for amounts (some very large transactions, many small)
        # mean=8 (exp(8)~3000), sigma=1.5
        amount = np.random.lognormal(mean=8, sigma=1.5)
        amount = round(max(5.0, min(amount, 5000000.0)), 2)
        
        # Random date
        random_days = random.randint(0, date_range)
        txn_date = (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")
        
        data.append({
            "Date": txn_date,
            "Supplier": vendor,
            "Total Spend": amount,
            "Category": vendor_category_map[vendor],
            "Cost Center": random.choice(cost_centers),
            "Currency": "USD",
            "Description": f"Recurring payment for {vendor_category_map[vendor]} - REF-{random.randint(10000, 99999)}"
        })
        
    df = pd.DataFrame(data)
    
    output_path = os.path.join(os.getcwd(), "stress_test_data.csv")
    df.to_csv(output_path, index=False)
    
    print(f"Successfully generated {num_rows} rows.")
    print(f"File saved to: {output_path}")
    print(f"Total Portfolio Spend: ${df['Total Spend'].sum():,.2f}")

if __name__ == "__main__":
    generate_stress_dataset()

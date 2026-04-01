import pandas as pd
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta

def generate_trend_dataset():
    # Set seed for reproducible realistic trends
    np.random.seed(42)
    
    vendors = {
        "AWS": {"category": "Cloud Infrastructure", "start_amount": 15000, "growth_rate": 1.02, "volatility": 0.05, "start_date": "2021-01-01"},
        "Salesforce": {"category": "SaaS", "start_amount": 8000, "growth_rate": 1.01, "volatility": 0.02, "start_date": "2021-01-01"},
        "Gusto": {"category": "Payroll", "start_amount": 12000, "growth_rate": 1.015, "volatility": 0.01, "start_date": "2021-01-01"},
        "Datadog": {"category": "Cloud Infrastructure", "start_amount": 3000, "growth_rate": 1.05, "volatility": 0.08, "start_date": "2023-06-01"},
        "Google Ads": {"category": "Marketing", "start_amount": 25000, "growth_rate": 1.00, "volatility": 0.20, "start_date": "2021-01-01"},
        "LinkedIn Ads": {"category": "Marketing", "start_amount": 5000, "growth_rate": 1.00, "volatility": 0.15, "start_date": "2022-03-01"},
        "McKinsey": {"category": "Professional Services", "start_amount": 50000, "growth_rate": 1.00, "volatility": 0.00, "start_date": "2024-01-01", "frequency": "quarterly"},
        "Zendesk": {"category": "SaaS", "start_amount": 4000, "growth_rate": 1.02, "volatility": 0.03, "start_date": "2021-01-01"},
        "Slack": {"category": "SaaS", "start_amount": 6000, "growth_rate": 1.005, "volatility": 0.01, "start_date": "2021-01-01"},
        "FedEx": {"category": "Logistics", "start_amount": 20000, "growth_rate": 1.00, "volatility": 0.10, "start_date": "2021-01-01"},
        "Uber": {"category": "Travel & Expenses", "start_amount": 3000, "growth_rate": 1.03, "volatility": 0.12, "start_date": "2022-01-01"},
        "WeWork": {"category": "Real Estate", "start_amount": 15000, "growth_rate": 1.00, "volatility": 0.00, "start_date": "2021-01-01"},
        "DocuSign": {"category": "SaaS", "start_amount": 1500, "growth_rate": 1.00, "volatility": 0.05, "start_date": "2021-01-01"},
        "Zoom": {"category": "SaaS", "start_amount": 2500, "growth_rate": 0.98, "volatility": 0.02, "start_date": "2021-01-01"},
        "Okta": {"category": "SaaS", "start_amount": 5000, "growth_rate": 1.01, "volatility": 0.03, "start_date": "2022-06-01"}
    }
    
    records = []
    end_date = date(2026, 4, 1)
    
    for v_name, v_data in vendors.items():
        curr_date = date.fromisoformat(v_data["start_date"])
        curr_amount = v_data["start_amount"]
        freq = v_data.get("frequency", "monthly")
        
        while curr_date <= end_date:
            # Add natural volatility to the spend
            noise = np.random.normal(0, v_data["volatility"])
            actual_amount = curr_amount * (1 + noise)
            
            # Add seasonal Q4 spike for marketing/logistics/cloud
            if curr_date.month in [11, 12]:
                if v_data["category"] in ["Marketing", "Logistics", "Cloud Infrastructure"]:
                    actual_amount *= 1.3
                    
            records.append({
                "date": curr_date.isoformat(),
                "amount": round(actual_amount, 2),
                "category": v_data["category"],
                "entity": v_name,
                "currency": "USD",
                "gl_code": f"GL-{1000 + list(vendors.keys()).index(v_name)}",
                "cost_center": "CC-01",
                "source_file": "trend_demo_data.csv"
            })
            
            # Step forward in time
            if freq == "monthly":
                curr_date += relativedelta(months=1)
                curr_amount *= v_data["growth_rate"]
            elif freq == "quarterly":
                curr_date += relativedelta(months=3)
                curr_amount *= (v_data["growth_rate"] ** 3)
                
    df = pd.DataFrame(records)
    # Sort chronologically
    df.sort_values(by="date", inplace=True)
    df.to_csv("trend_demo_data.csv", index=False)
    print(f"✅ Successfully generated {len(df)} records for {len(vendors)} vendors over a 5-year timeline. Saved to 'trend_demo_data.csv'")
    
if __name__ == "__main__":
    generate_trend_dataset()

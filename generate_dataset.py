import csv
from app.api.demo import _build_demo_records

def main():
    records = _build_demo_records()
    
    # Sort by date descending
    records.sort(key=lambda x: x.date, reverse=True)
    
    filename = "cade_hospital_dataset.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(["Date", "Amount", "Currency", "Vendor Name", "Category", "Description", "PO_Number"])
        
        for r in records:
            writer.writerow([
                r.date.isoformat(),
                r.amount,
                r.currency,
                r.entity,
                r.category,
                r.description or "",
                r.po_number or ""
            ])
            
    print(f"Successfully generated {filename} with {len(records)} records.")

if __name__ == "__main__":
    main()

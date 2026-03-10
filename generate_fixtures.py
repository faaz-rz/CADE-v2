import os
import pandas as pd

def generate_fixtures():
    fixtures_dir = "backend/tests/fixtures"
    os.makedirs(fixtures_dir, exist_ok=True)
    
    # 1. headers_row5.xlsx
    # Rows 1-2: company logo text
    # Row 3: blank
    # Row 4: "Q3 2025 Vendor Report"
    # Row 5: actual column headers
    # Row 6+: transaction data
    df_h5 = pd.DataFrame([
        ["ACME Corp Logo Text", None, None, None],
        ["Confidential - Do Not Distribute", None, None, None],
        [None, None, None, None],
        ["Q3 2025 Vendor Report", None, None, None],
        ["Supplier", "Invoice Date", "Total Spend", "Cost Center"],
        ["AWS", "2025-01-15", "50000", "Engineering"],
        ["Google", "2025-01-20", "25000", "Marketing"]
    ])
    df_h5.to_excel(os.path.join(fixtures_dir, "headers_row5.xlsx"), index=False, header=False)
    
    # 2. multi_sheet.xlsx
    # Sheet1 "Summary": totals only
    # Sheet2 "Jan Transactions": real data
    # Sheet3 "Feb Transactions": real data
    with pd.ExcelWriter(os.path.join(fixtures_dir, "multi_sheet.xlsx"), engine='openpyxl') as writer:
        pd.DataFrame([["Total Spend", "100000"], ["Top Vendor", "AWS"]]).to_excel(writer, sheet_name="Summary", index=False, header=False)
        pd.DataFrame([
            {"Vendor": "Datadog", "Amount": "1000", "Date": "2025-01-05"},
            {"Vendor": "Github", "Amount": "500", "Date": "2025-01-15"}
        ]).to_excel(writer, sheet_name="Jan Transactions", index=False)
        pd.DataFrame([
            {"Vendor": "Datadog", "Amount": "1000", "Date": "2025-02-05"},
            {"Vendor": "Github", "Amount": "500", "Date": "2025-02-15"}
        ]).to_excel(writer, sheet_name="Feb Transactions", index=False)
        
    # 3. messy_amounts.csv
    # "$2,100,000.00", "(48,500)", "1.2M", "€95.000,00", "N/A", ""
    df_messy = pd.DataFrame([
        {"Entity": "A", "Cost": "$2,100,000.00"},
        {"Entity": "B", "Cost": "(48,500)"},
        {"Entity": "C", "Cost": "1.2M"},
        {"Entity": "D", "Cost": "€95.000,00"},
        {"Entity": "E", "Cost": "N/A"},
        {"Entity": "F", "Cost": ""}
    ])
    df_messy.to_csv(os.path.join(fixtures_dir, "messy_amounts.csv"), index=False)
    
    # 4. date_chaos.csv
    # "15/01/2025", "Jan-25", "44941", "2025-01", "January 15 2025"
    df_dates = pd.DataFrame([
        {"Entity": "A", "Amount": "100", "When": "15/01/2025"},
        {"Entity": "B", "Amount": "100", "When": "Jan-25"},
        {"Entity": "C", "Amount": "100", "When": "44941"}, # roughly 2023-01-15 in excel
        {"Entity": "D", "Amount": "100", "When": "2025-01"},
        {"Entity": "E", "Amount": "100", "When": "January 15 2025"}
    ])
    df_dates.to_csv(os.path.join(fixtures_dir, "date_chaos.csv"), index=False)
    
    # 5. vendor_noise.csv
    # "Amazon Web Services, Inc.", "AMAZON WEB SERVICES", "AWS EMEA SARL", "Salesforce.com, Inc.", "SALESFORCE"
    df_vendors = pd.DataFrame([
        {"Supplier Name": "Amazon Web Services, Inc.", "Spend": "100"},
        {"Supplier Name": "AMAZON WEB SERVICES", "Spend": "100"},
        {"Supplier Name": "AWS EMEA SARL", "Spend": "100"},
        {"Supplier Name": "Salesforce.com, Inc.", "Spend": "100"},
        {"Supplier Name": "SALESFORCE", "Spend": "200"}
    ])
    df_vendors.to_csv(os.path.join(fixtures_dir, "vendor_noise.csv"), index=False)
    
    # 6. no_standard_headers.xlsx
    # Columns: "Who We Paid", "How Much", "When", "Which Team" -> triggers LLM fallback
    df_nostandard = pd.DataFrame([
        {"Who We Paid": "Anthropic", "How Much": "5000", "When": "2024-11-01", "Which Team": "AI Research"}
    ])
    df_nostandard.to_excel(os.path.join(fixtures_dir, "no_standard_headers.xlsx"), index=False)
    print("Fixtures generated successfully.")

if __name__ == "__main__":
    generate_fixtures()

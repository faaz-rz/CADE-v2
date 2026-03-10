import pandas as pd
import os

def generate_exhaustive_test_file():
    filepath = "d:/Workfllow/test_universal_ingestion_exhaustive.xlsx"
    
    # Sheet 1: The "Messy Manual" template (Tests all value cleaners, header detection, and fuzzy mapping)
    # Tests:
    # 1. Header detection at row 5
    # 2. Fuzzy column mapping ("Who We Paid" -> entity, "How Much" -> amount, etc.)
    # 3. Currency cleaning ($2,100.00 -> 2100.0)
    # 4. Negative value parsing ((500.00) -> -500.0)
    # 5. K/M multiplier parsing (1.2K -> 1200.0, 1.5M -> 1500000.0)
    # 6. Various date formats (Jan-25, 15/01/25, 2025-01)
    # 7. Vendor noise normalization (Amazon Web Services, Inc. -> AMAZON WEB SERVICES)
    sheet1_data = [
        ["INTERNAL EXPENSE REPORT - CONFIDENTIAL", None, None, None, None],
        ["Generated: 2025-01-01", None, None, None, None],
        [None, None, None, None, None],
        [None, None, None, None, None],
        ["Who We Paid", "How Much", "When", "Which Team", "Notes"],
        ["Amazon Web Services, Inc.", "$2,100.00", "Jan-25", "Engineering", "Cloud hosting"],
        ["Salesforce.com, Inc.", "(500.00)", "15/01/25", "Sales", "Refund"],
        ["SLACK TECHNOLOGIES LLC", "1.2K", "2025-01", "Product", "Chat licenses"],
        ["ATLASSIAN PTY LTD", "1.5M", "March 25", "Engineering", "Jira renewal"],
        ["Zoom Video Communications", "€ 95.000,00", "01/15/2025", "General", "Annual sub"]
    ]
    df1 = pd.DataFrame(sheet1_data)

    # Sheet 2: The "Multi-Sheet & Deduplication" template
    # Tests:
    # 1. Processing multiple sheets in one workbook
    # 2. Deduplication (AWS row matches row in Sheet 1)
    # 3. Skipping zero/blank amounts
    # 4. Handling missing optional columns (No category)
    sheet2_data = [
        ["Vendor Name", "Transaction Amount", "Transaction Date"],
        ["Amazon Web Services, Inc.", "2100", "2025-01-01"], # Potential duplicate of Sheet1 AWS depending on canonical date resolution
        ["Datadog", "0", "2025-01-02"], # Should be skipped
        ["", "500", "2025-01-03"], # Should fail (Missing entity)
        ["Github", "", "2025-01-04"], # Should fail (Missing amount)
        ["Notion", "250.50", "2025-01-05"] # Should pass
    ]
    df2 = pd.DataFrame(sheet2_data)
    
    # Sheet 3: "Cost (k) Header Multipliers"
    # Tests:
    # 1. Header multiplier detection (Cost (k) -> amount * 1000)
    sheet3_data = [
        ["Supplier", "Date", "Cost (k)", "Group"],
        ["Microsoft", "2025-01-10", "15.5", "IT"], # Should become 15500
        ["GoogleCloud", "2025-01-11", "2.0", "Engineering"] # Should become 2000
    ]
    df3 = pd.DataFrame(sheet3_data)

    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df1.to_excel(writer, sheet_name="Q1 Expenses", index=False, header=False)
        df2.to_excel(writer, sheet_name="Jan Data", index=False, header=False)
        df3.to_excel(writer, sheet_name="IT Spend", index=False, header=False)
        
    print(f"Exhaustive test file successfully generated at: {filepath}")

if __name__ == "__main__":
    generate_exhaustive_test_file()

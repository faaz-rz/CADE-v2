import pandas as pd

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

sheet2_data = [
    ["Vendor Name", "Transaction Amount", "Transaction Date"],
    ["Amazon Web Services, Inc.", 2100, "2025-01-01"],
    ["Datadog", 0, "2025-01-02"],
    [pd.NA, 500, "2025-01-03"],
    ["Github", pd.NA, "2025-01-04"],
    ["Notion", 250.50, "2025-01-05"]
]
df2 = pd.DataFrame(sheet2_data)

sheet3_data = [
    ["Supplier", "Date", "Cost (k)", "Group"],
    ["Microsoft", "2025-01-10", 15.5, "IT"],
    ["GoogleCloud", "2025-01-11", 2.0, "Engineering"]
]
df3 = pd.DataFrame(sheet3_data)

out_file = "d:/Workfllow/test_universal_ingestion_exhaustive.xlsx"
with pd.ExcelWriter(out_file, engine="openpyxl") as writer:
    df1.to_excel(writer, sheet_name="Q1 Expenses", index=False, header=False)
    df2.to_excel(writer, sheet_name="Jan Data", index=False, header=False)
    df3.to_excel(writer, sheet_name="IT Spend", index=False, header=False)

print(f"Created {out_file} successfully.")

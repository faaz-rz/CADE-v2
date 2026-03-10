import requests, json

print("Clearing DB...")
requests.delete('http://localhost:8000/api/data/clear')

print("Uploading...")
res = requests.post(
    'http://localhost:8000/api/upload', 
    files={'file': open('d:/Workfllow/test_universal_ingestion_exhaustive.xlsx', 'rb')}
).json()

print("Status...")
stat = requests.get('http://localhost:8000/api/data/status').json()

print("Vendors...")
exp = requests.get('http://localhost:8000/api/exposure/vendors').json()

out = {
    "UPLOAD_ACCEPTED": res.get("rows_accepted"),
    "UPLOAD_REJECTED": res.get("rows_rejected"),
    "UPLOAD_DECISIONS": res.get("decisions_generated"),
    "STATUS": stat,
    "VENDORS": [(v["vendor_id"], v["annual_spend"], v["category"]) for v in exp]
}

with open("output.json", "w") as f:
    json.dump(out, f, indent=2)

print("Done")

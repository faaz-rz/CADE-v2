import sys

def update_readme():
    with open(r'd:\Workfllow\PROJECT.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Overview Table
    old_table = """| **Audit Trail** | Immutable event log for every decision lifecycle change |
| **Connector Architecture** | Pluggable data source interface (CSV, ERP, ServiceNow) |"""
    new_table = """| **Audit Trail** | Immutable event log for every decision lifecycle change |
| **Connector Architecture** | Pluggable data source interface (CSV, ERP, ServiceNow) |
| **AI Board Report** | Groq-powered LLM (llama-3.1-70b) executing 4-sentence CFO briefings |
| **Contract Renewals** | Simulated renewal dashboard predicting and grouping vendor windows |
| **Enterprise Security** | Auth0 RBAC and protected routing across the application |"""
    content = content.replace(old_table, new_table)

    # 2. Update Backend Tech Stack
    old_backend_stack = """| **PyYAML** | Policy configuration files |"""
    new_backend_stack = """| **PyYAML** | Policy configuration files |
| **Groq / LLMs** | Narrative generation for executive reports |
| **Auth0** | JWT verification and RBAC protection |"""
    content = content.replace(old_backend_stack, new_backend_stack)

    # 3. Update Frontend Tech Stack
    old_frontend_stack = """| **React Router 6** | Client-side routing |"""
    new_frontend_stack = """| **React Router 6** | Client-side routing |
| **Auth0 React** | User authentication and permission gates |"""
    content = content.replace(old_frontend_stack, new_frontend_stack)

    # 4. Update Backend API Project Structure
    old_api_struct = """│   │   │   ├── exposure.py              #   GET /api/exposure/vendors
│   │   │   ├── simulation.py            #   POST /simulate/price_shock
│   │   │   └── export.py               #   GET /export/executive_report"""
    new_api_struct = """│   │   │   ├── exposure.py              #   GET /api/exposure/vendors
│   │   │   ├── simulation.py            #   POST /simulate/price_shock
│   │   │   ├── export.py                #   GET /export/executive_report
│   │   │   ├── contracts.py             #   GET /api/renewals
│   │   │   ├── trends.py                #   GET /api/trends/alerts
│   │   │   └── demo.py                  #   Demo data generation"""
    content = content.replace(old_api_struct, new_api_struct)

    # 5. Update Backend Services Structure
    old_services_struct = """│   │   │   ├── analytics.py             #   Vendor stats aggregation
│   │   │   ├── audit.py                 #   Audit logging
│   │   │   └── ingestion.py             #   Universal file ingestion"""
    new_services_struct = """│   │   │   ├── analytics.py             #   Vendor stats aggregation
│   │   │   ├── audit.py                 #   Audit logging
│   │   │   ├── ingestion.py             #   Universal file ingestion
│   │   │   └── ai_narrator.py           #   Groq-powered Board summaries"""
    content = content.replace(old_services_struct, new_services_struct)

    # 6. Update Frontend Pages Structure
    old_pages_struct = """│   │   ├── Upload.tsx                # Data upload page
│   │   └── ExposureDashboard.tsx     # Exposure analysis page"""
    new_pages_struct = """│   │   ├── Upload.tsx                # Data upload page
│   │   ├── ExposureDashboard.tsx     # Exposure analysis page
│   │   └── Contracts.tsx             # Contract renewals calendar"""
    content = content.replace(old_pages_struct, new_pages_struct)

    # 7. Update Frontend Components Structure
    old_components_struct = """│   │   ├── ExposurePanel.tsx         # Vendor exposure data panel
│   │   └── PriceShockPanel.tsx       # Interactive shock simulator"""
    new_components_struct = """│   │   ├── ExposurePanel.tsx         # Vendor exposure data panel
│   │   ├── PriceShockPanel.tsx       # Interactive shock simulator
│   │   ├── ContractCalendar.tsx      # Contract renewal buckets and UI
│   │   ├── ProtectedRoute.tsx        # Auth0 permission gating
│   │   ├── SavingsTracker.tsx        # Track savings historically
│   │   └── TrendAlerts.tsx           # Monthly vendor spend anomaly UI"""
    content = content.replace(old_components_struct, new_components_struct)

    # 8. Add to API Reference
    old_api_ref = """| `GET` | `/export/executive_report` | Download Excel executive report (.xlsx) |

### Health Check"""
    new_api_ref = """| `GET` | `/export/executive_report` | Download Excel executive report (.xlsx) |

### Board Reports & Summaries

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/summary/board-narrative` | Groq-generated 4-sentence CFO summary |

### Contract Renewals

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/contracts/renewals` | 90-day simulated renewal buckets and savings |

### Health Check"""
    content = content.replace(old_api_ref, new_api_ref)

    # 9. Add AI Narrator to Core Modules
    old_core_modules = """Rejects ambiguous datasets rather than guessing."""
    new_core_modules = """Rejects ambiguous datasets rather than guessing.

### AI Narrator (`services/ai_narrator.py`)

Groq-powered LLM service utilizing `llama-3.1-70b-versatile` to synthesize total spend, high-risk vendors, decision counts, and EBITDA exposure into a concise 4-sentence executive narrative. Designed to be copy-pasted directly into CFO Board Reports. Gracefully falls back to template string generation if API keys are missing."""
    content = content.replace(old_core_modules, new_core_modules)

    # 10. Update Frontend info
    old_frontend_info = """| `/exposure` | Exposure Dashboard | Vendor concentration heatmap, exposure table, KPIs |

### Decision Detail Modal"""
    new_frontend_info = """| `/exposure` | Exposure Dashboard | Vendor concentration heatmap, exposure table, KPIs |
| `/contracts`| Contract Renewals | Simulated vendor renewals bucketed by date |

### Decision Detail Modal"""
    content = content.replace(old_frontend_info, new_frontend_info)

    # 11. Roadmap update
    old_roadmap = """- ✅ Frontend Exposure Dashboard

### Future (v3.0)"""
    new_roadmap = """- ✅ Frontend Exposure Dashboard
- ✅ AI Board Narrator (Groq)
- ✅ Contract Renewal Calendar
- ✅ Auth0 Role-based Authentication
- ✅ Trend Anomalies & Savings Trackers

### Future (v3.0)"""
    content = content.replace(old_roadmap, new_roadmap)

    with open(r'd:\Workfllow\PROJECT.md', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    update_readme()
    print("PROJECT.md successfully updated!")

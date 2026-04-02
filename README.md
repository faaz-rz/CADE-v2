# CADE - Capital Allocation Decision Engine

> **AI-powered enterprise spend analysis platform** combining intelligent data ingestion, predictive vendor analytics, financial exposure modeling, and executive decision support for procurement optimization.

---

## 🎯 Overview

**CADE** is a full-stack financial intelligence platform designed for enterprises to make data-driven capital allocation decisions at scale. It transforms raw spend data into actionable procurement strategies through:

- **Intelligent Data Ingestion** - Universal file format support with AI-powered column mapping (CSV, XLSX, ODS)
- **Rule-Based Decision Engine** - Automated vendor analysis and decision prioritization
- **Financial Exposure Analysis** - Real-time vendor concentration & worst-case scenario modeling
- **Interactive Price Shock Simulation** - "What-if" analysis with EBITDA impact projections
- **Predictive Renewal Calendar** - Vendor contract renewal forecasting and grouping
- **Executive Reporting** - Multi-format export (Excel, JSON) with audit trails

The platform answers critical questions:
> *"Which vendors represent the highest spend concentration risk? If Vendor X increases price by 15%, what's the EBITDA impact? When are our critical contracts up for renewal?"*

---

## 🚀 Core Features

| Feature | Description | Impact |
|---------|-------------|--------|
| **Universal Data Ingestion** | Auto-detects schema, maps columns via LLM, handles multi-sheet files | 80% reduction in manual data prep |
| **Decision Engine** | Rule-based vendor scoring (spend, frequency, trend analysis) | Prioritized action list for procurement teams |
| **Exposure Dashboard** | Vendor concentration heatmaps, category breakdowns, risk scoring | Real-time financial risk visibility |
| **Price Shock Simulator** | Interactive slider for scenario testing with EBITDA recalculation | Quantified impact of price negotiations |
| **Trend Alerts** | Monthly spend anomaly detection, growth trajectory analysis | Early warning system for budget overruns |
| **Contract Renewals** | ML-driven clustering of contracts by renewal date | Consolidated vendor renewal pipeline |
| **Audit Trail** | Immutable event log for every decision + state transitions | Compliance & governance ready |
| **Executive Export** | 3-sheet formatted Excel with KPI summary, exposures, recommendations | C-suite ready reports in 1-click |

---

## 🏗️ Architecture

### Tech Stack

**Backend:**
- Python 3.10+ with FastAPI (async REST API)
- SQLite with in-memory caching for performance
- Groq LLM for intelligent column mapping
- Pandas + NumPy for data processing
- Pydantic for schema validation

**Frontend:**
- React 18 + TypeScript + Vite
- TailwindCSS for responsive UI
- Auth0 for enterprise authentication
- Visx for interactive data visualization

**Deployment:**
- Backend: Nixpacks → Railway/Render/Vercel
- Frontend: Vercel with reverse proxy DNS firewall bypass
- Live: https://cade-chi.vercel.app

### System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React/TS)                       │
│  ┌──────────────┬──────────────┬─────────────┬──────────────┐   │
│  │  Decisions   │  Dashboard   │  Exposure   │  Renewals    │   │
│  │   Inbox      │   (KPIs)     │  Analysis   │  Calendar    │   │
│  └──────────────┴──────────────┴─────────────┴──────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼────────────────────────────────────┐
│                    Backend (FastAPI)                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Layer 1: Ingestion → Layer 2: Processing → Layer 3: ...  │   │
│  │ • File Detection  • Column Mapping    • Decision Engine   │   │
│  │ • Multi-sheet     • Deduplication     • Exposure Calc     │   │
│  │ • Format Convert  • Validation        • Trend Analysis    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                    ┌─────────┴──────────┐                        │
│                    ▼                    ▼                        │
│           ┌─────────────────┐   ┌──────────────┐                │
│           │ SQLite Database │   │ In-Mem Cache │                │
│           │ (Persistent)    │   │ (Perf Layer) │                │
│           └─────────────────┘   └──────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Data Flow

1. **Upload** → User uploads CSV/XLSX spend data
2. **Detect & Map** → Auto-detect schema, AI maps columns (80%+ confidence required)
3. **Normalize** → Convert to CanonicalFinancialRecord, deduplicate, validate
4. **Analyze** → Decision engine calculates vendor scores, exposure, trends
5. **Store** → Persist to SQLite with full audit trail
6. **Visualize** → Frontend renders decisions, dashboards, simulations
7. **Act** → User approves/rejects/defers decisions, exports reports

---

## 📊 Key Metrics Tracked

- **Vendor Spend Concentration** - % of budget from top vendors
- **Category Exposure** - Risk distribution across spend categories
- **EBITDA Impact** - Direct financial exposure per vendor
- **Spend Velocity** - Month-over-month growth rates
- **Contract Gap Risk** - Days until renewal without renegotiation
- **Anomaly Score** - Statistical deviation from baseline

---

## 🛠️ Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm/yarn

### Quick Start

```bash
# Clone repository
git clone https://github.com/faaz-rz/CADE.git
cd CADE

# Backend setup
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# API docs available at: http://localhost:8000/docs

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
# App available at: http://localhost:5173
```

### First Run
1. Click **"Upload"** → Select CSV/XLSX spend file
2. System auto-detects columns and ingests data
3. Browse **"Decisions"** → View recommended vendors to negotiate
4. Click any decision → See **"Exposure"** breakdown
5. Use **"Price Shock Simulator"** → Test "What-if" scenarios
6. View **"Contracts"** → See predictive renewal calendar
7. Click **"Export"** → Download executive report (Excel)

---

## 📚 Documentation

- **[PROJECT.md](./PROJECT.md)** - Detailed architecture, API reference, module documentation
- **[API Swagger UI](http://localhost:8000/docs)** - Interactive API explorer
- **[Deployment Guide](./PROJECT.md#deployment)** - Production setup instructions

---

## 🔐 Security & Compliance

- ✅ Auth0 integration for enterprise SSO
- ✅ Audit trail for all decision changes
- ✅ Immutable event log for compliance
- ✅ SQLite with encrypted at-rest support
- ✅ GDPR-ready data handling

---

## 🎯 Use Cases

- **Procurement Teams** - Identify vendors for contract renegotiation
- **Finance Leaders** - Quantify financial exposure and EBITDA risk
- **Supply Chain** - Detect vendor concentration and single-point failures
- **Executives** - One-page executive summary for capital allocation strategy
- **Compliance** - Full audit trail of all decisions and approvals

---

## 📈 Roadmap

- [ ] Multi-currency handling (currently USD/INR)
- [ ] Predictive spend forecasting with Prophet/ARIMA
- [ ] Vendor performance metrics integration
- [ ] Slack/email alerts for critical exposures
- [ ] Advanced visualization (3D portfolio bubble charts)
- [ ] GraphQL API alongside REST

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Submit a pull request with tests

See [PROJECT.md](./PROJECT.md) for detailed development guidelines.

---

## 📄 License

MIT License - See [LICENSE](./LICENSE) file for details

---

## 📞 Support

- **Issues**: Report bugs via GitHub Issues
- **Docs**: See PROJECT.md for comprehensive documentation
- **Demo**: https://cade-chi.vercel.app

---

**Last Updated**: 2026-04-02 03:57:57 | **Version**: 2.0.0
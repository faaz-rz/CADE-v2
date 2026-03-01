# Capital Risk & Exposure Platform v2

> AI-driven capital allocation decision engine with financial exposure analysis, price shock simulation, and executive reporting.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Core Modules](#core-modules)
- [Frontend](#frontend)
- [Testing](#testing)
- [Configuration](#configuration)
- [Design Principles](#design-principles)
- [Roadmap](#roadmap)

---

## Overview

The **Capital Risk & Exposure Platform** analyzes financial transaction data and produces actionable capital allocation decisions. It answers the question:

> *"If Vendor X increases price by 15%, what is the EBITDA impact and financial exposure?"*

The system ingests CSV/XLSX spend data, applies rule-based analysis to identify high-spend and high-frequency vendors, calculates financial exposure, simulates price shocks, and generates executive reports — all deterministically, with a full audit trail.

### Key Capabilities

| Capability | Description |
|---|---|
| **Decision Engine** | Rule-based vendor analysis → prioritized recommendations |
| **Financial Exposure** | Vendor concentration & worst-case exposure calculations |
| **Price Shock Simulation** | "What-if" analysis with EBITDA impact projection |
| **Executive Export** | 3-sheet Excel report with formatted financial data |
| **Persistent Storage** | SQLite database with in-memory cache for performance |
| **Trend Analysis** | Rolling averages and spend growth tracking |
| **Audit Trail** | Immutable event log for every decision lifecycle change |
| **Connector Architecture** | Pluggable data source interface (CSV, ERP, ServiceNow) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│   React + TypeScript + Vite + TailwindCSS                   │
│                                                             │
│   ┌──────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│   │ Decision │  │  Exposure    │  │  Decision Detail     │  │
│   │  Inbox   │  │  Dashboard   │  │  + Exposure Panel    │  │
│   │          │  │  + Heatmap   │  │  + Shock Simulator   │  │
│   └────┬─────┘  └──────┬───────┘  └──────────┬───────────┘  │
│        │               │                     │              │
└────────┼───────────────┼─────────────────────┼──────────────┘
         │               │                     │
    ═════╪═══════════════╪═════════════════════╪══════════════
         │          HTTP / REST API             │
    ═════╪═══════════════╪═════════════════════╪══════════════
         │               │                     │
┌────────┼───────────────┼─────────────────────┼──────────────┐
│        ▼               ▼                     ▼              │
│  ┌──────────┐  ┌─────────────┐  ┌─────────────────────┐    │
│  │ Decision │  │  Exposure   │  │  Price Shock         │    │
│  │   API    │  │    API      │  │  Simulation API      │    │
│  └────┬─────┘  └──────┬──────┘  └──────────┬──────────┘    │
│       │               │                    │               │
│       ▼               ▼                    ▼               │
│  ┌─────────────────────────────────────────────────┐       │
│  │              SERVICE LAYER                      │       │
│  │                                                 │       │
│  │  DecisionEngine  · ExposureEngine               │       │
│  │  RiskEngine      · TrendEngine                  │       │
│  │  PolicyEngine    · SpendingAnalyzer             │       │
│  │  AuditService    · IngestionService             │       │
│  └─────────────────────┬───────────────────────────┘       │
│                        │                                   │
│  ┌─────────────────────▼───────────────────────────┐       │
│  │              DATA LAYER                         │       │
│  │                                                 │       │
│  │  DecisionStore (In-Memory + SQLite)             │       │
│  │  transactions.json (Canonical Records)          │       │
│  │  policies.yaml (Rule Configuration)             │       │
│  └─────────────────────────────────────────────────┘       │
│                                                            │
│                     BACKEND (FastAPI + Python)              │
└────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

### Backend

| Technology | Purpose |
|---|---|
| **Python 3.14** | Runtime |
| **FastAPI** | REST API framework |
| **Pydantic** | Data validation & serialization |
| **SQLAlchemy** | ORM for SQLite persistence |
| **Alembic** | Database migration management |
| **openpyxl** | Excel report generation |
| **Pandas** | CSV/XLSX data ingestion |
| **PyYAML** | Policy configuration files |

### Frontend

| Technology | Purpose |
|---|---|
| **React 18** | UI framework |
| **TypeScript** | Type safety |
| **Vite 5** | Build tool + dev server |
| **TailwindCSS 3** | Utility-first CSS |
| **Axios** | HTTP client |
| **Lucide React** | Icon library |
| **React Router 6** | Client-side routing |

---

## Project Structure

```
Workfllow/
├── backend/
│   ├── main.py                          # FastAPI app entry point
│   ├── requirements.txt                 # Python dependencies
│   │
│   ├── app/
│   │   ├── api/                         # REST API routes
│   │   │   ├── decisions.py             #   GET/POST /api/decisions
│   │   │   ├── approvals.py             #   POST /api/decisions/{id}/approve|reject
│   │   │   ├── upload.py                #   POST /api/upload
│   │   │   ├── summary.py              #   GET /api/summary
│   │   │   ├── exposure.py              #   GET /api/exposure/vendors
│   │   │   ├── simulation.py            #   POST /simulate/price_shock
│   │   │   └── export.py               #   GET /export/executive_report
│   │   │
│   │   ├── models/                      # Pydantic data models
│   │   │   ├── decision.py              #   Decision, DecisionEvent, enums
│   │   │   ├── exposure.py              #   FinancialExposure
│   │   │   ├── trend.py                 #   VendorTrend, MonthlySpend
│   │   │   ├── canonical.py             #   CanonicalFinancialRecord
│   │   │   ├── data.py                  #   FinancialRecord (raw)
│   │   │   └── summary.py              #   DecisionSummary
│   │   │
│   │   ├── services/                    # Business logic layer
│   │   │   ├── decision_engine.py       #   Rule-based decision generation
│   │   │   ├── decision_store.py        #   Dual-mode storage (memory + SQLite)
│   │   │   ├── exposure_engine.py       #   Financial exposure calculations
│   │   │   ├── risk_engine.py           #   Multi-factor risk scoring
│   │   │   ├── trend_engine.py          #   Rolling average + growth analysis
│   │   │   ├── policy_engine.py         #   YAML-driven policy configuration
│   │   │   ├── analytics.py             #   Vendor stats aggregation
│   │   │   ├── audit.py                 #   Audit logging
│   │   │   └── ingestion.py             #   Universal file ingestion
│   │   │
│   │   ├── simulation/                  # What-if simulation modules
│   │   │   └── price_shock.py           #   Price shock simulator
│   │   │
│   │   ├── exports/                     # Report generation
│   │   │   └── excel_exporter.py        #   3-sheet Excel workbook
│   │   │
│   │   ├── connectors/                  # Data source connectors
│   │   │   ├── base.py                  #   BaseConnector (interface)
│   │   │   ├── csv_connector.py         #   CSV connector (stub)
│   │   │   ├── servicenow_connector.py  #   ServiceNow connector (mock)
│   │   │   └── erp_connector.py         #   ERP connector (mock)
│   │   │
│   │   ├── db/                          # Database layer
│   │   │   ├── database.py              #   SQLite engine + session factory
│   │   │   └── db_models.py             #   ORM tables (vendors, decisions, events)
│   │   │
│   │   ├── core/                        # Core business rules
│   │   │   ├── heuristics.py            #   Column-mapping heuristics
│   │   │   ├── decision_templates.py    #   Deterministic decision templates
│   │   │   └── mappings.py              #   Schema mapping config
│   │   │
│   │   └── config/
│   │       └── policies.yaml            # Category-specific policy thresholds
│   │
│   ├── config/                          # Schema mapping configs
│   │   ├── default_mapping.yaml
│   │   └── mapping_sales.yaml
│   │
│   ├── data/                            # Runtime data (auto-created)
│   │   ├── transactions.json            #   Ingested canonical records
│   │   └── capital_engine.db            #   SQLite database
│   │
│   └── tests/                           # Test suite
│       ├── test_context_aware_engine.py #   Decision engine tests
│       ├── test_exposure_engine.py      #   Exposure calculation tests
│       ├── test_price_shock.py          #   Shock simulation tests
│       ├── test_trend_engine.py         #   Trend analysis tests
│       ├── test_state_transitions.py    #   Lifecycle & store tests
│       └── stress/                      #   Stress & reliability tests
│           ├── test_audit.py
│           ├── test_boundaries.py
│           ├── test_consistency.py
│           ├── test_robustness.py
│           └── test_scale.py
│
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    └── src/
        ├── App.tsx                       # Root routes
        ├── main.tsx                      # Entry point
        ├── index.css                     # Global styles
        ├── pages/
        │   ├── Decisions.tsx             # Decision inbox page
        │   ├── Upload.tsx                # Data upload page
        │   └── ExposureDashboard.tsx     # Exposure analysis page
        ├── components/
        │   ├── DecisionCard.tsx          # Decision list item
        │   ├── DecisionDetail.tsx        # Detail modal + exposure + shock
        │   ├── PortfolioSummary.tsx      # Executive KPI cards
        │   ├── RiskBadge.tsx             # Risk level badge
        │   ├── UploadDataButton.tsx      # File upload trigger
        │   ├── ExposurePanel.tsx         # Vendor exposure data panel
        │   └── PriceShockPanel.tsx       # Interactive shock simulator
        └── services/
            └── api.ts                    # API client + TypeScript interfaces
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the server (auto-creates SQLite DB on first run)
uvicorn main:app --reload --port 8000
```

The server starts at `http://localhost:8000`. Visit `http://localhost:8000/docs` for the interactive Swagger UI.

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The frontend starts at `http://localhost:5173`.

### Quick Start Workflow

1. **Start backend** → `uvicorn main:app --reload`
2. **Start frontend** → `npm run dev`
3. **Upload data** → Click "Upload" on the Decision Inbox page or `POST /api/upload` with a CSV/XLSX file
4. **Review decisions** → Browse the Decision Inbox, approve/reject/defer
5. **Analyze exposure** → Click "Exposure" to view the Exposure Dashboard
6. **Simulate shocks** → Click any decision → use the Price Shock Simulator slider
7. **Export report** → Click "Export" to download the Excel executive report

---

## API Reference

### Decisions

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/decisions` | List all decisions |
| `GET` | `/api/decisions/{id}` | Get decision by ID |
| `POST` | `/api/decisions/{id}/approve` | Approve a decision |
| `POST` | `/api/decisions/{id}/reject` | Reject a decision (requires `note`) |
| `POST` | `/api/decisions/{id}/defer` | Defer a decision |

**Approve/Reject/Defer Body:**
```json
{ "note": "Reason or comment" }
```

### Upload

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/upload` | Upload CSV/XLSX → triggers ingestion + analysis |

**Body:** `multipart/form-data` with `file` field.

### Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/summary` | Executive dashboard summary KPIs |

### Exposure

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/exposure/vendors` | Financial exposure for all vendors |
| `GET` | `/api/exposure/vendors/{vendor_id}` | Exposure for a specific vendor |

**Response:**
```json
{
  "vendor_id": "Acme Corp",
  "annual_spend": 150000.0,
  "vendor_share_pct": 0.45,
  "category": "SaaS",
  "worst_case_exposure": 67500.0,
  "price_shock_impact_10pct": 15000.0,
  "price_shock_impact_20pct": 30000.0,
  "estimated_ebitda_delta_10pct": 3750.0,
  "estimated_ebitda_delta_20pct": 7500.0
}
```

### Price Shock Simulation

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/simulate/price_shock` | Simulate vendor price increase |

**Request:**
```json
{
  "vendor_id": "Acme Corp",
  "shock_percentage": 15.0
}
```

**Response:**
```json
{
  "base_spend": 150000.0,
  "shock_percentage": 15.0,
  "new_spend": 172500.0,
  "delta_spend": 22500.0,
  "estimated_ebitda_delta": 5625.0,
  "risk_classification_shift": "UNCHANGED (MEDIUM)"
}
```

### Export

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/export/executive_report` | Download Excel executive report (.xlsx) |

### Health Check

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | System health + version |

---

## Core Modules

### Decision Engine (`services/decision_engine.py`)

The heart of the system. Analyzes vendor stats against policy thresholds and generates prioritized decisions.

**Rules:**
1. **HIGH_SPEND** — Vendor total spend exceeds category `spend_threshold`
2. **HIGH_FREQUENCY** — Transaction count exceeds `frequency_threshold`

One decision per vendor (spend takes priority over frequency). Decisions are sorted by `annual_impact` descending. Decision IDs are **deterministic** via `uuid5` — same vendor + same rule → same ID across restarts.

### Exposure Engine (`services/exposure_engine.py`)

Pure-function financial exposure calculator. All calculations are deterministic.

**Formulas:**
- `worst_case_exposure = annual_spend × vendor_share_pct`
- `price_shock_impact_X = annual_spend × (X / 100)`
- `estimated_ebitda_delta_X = price_shock_impact_X × EBITDA_MARGIN`

**Configuration:** `EBITDA_MARGIN = 0.25` (default, editable in the module).

### Risk Engine (`services/risk_engine.py`)

Multi-factor risk scoring (0–12 scale):

| Factor | Criteria | Score |
|---|---|---|
| Spend Volume | ≥ 5× threshold: 3, ≥ 2×: 2, ≥ 1×: 1 | 0–3 |
| Operational Criticality | Policy flag | 0 or 3 |
| Regulatory Sensitivity | Policy flag | 0 or 3 |
| Vendor Concentration | Share ≥ 60%: 3, ≥ 40%: 2, ≥ 25%: 1 | 0–3 |

**Mapping:** Score ≤ 4 → LOW, ≤ 8 → MEDIUM, > 8 → HIGH.

### Policy Engine (`services/policy_engine.py`)

Singleton loading category-specific policies from `config/policies.yaml`. Falls back to default policy for unknown categories.

### Trend Engine (`services/trend_engine.py`)

Simplified time-series analysis:
- Aggregates monthly spend per vendor
- Calculates 3-month and 6-month **rolling averages**
- Calculates **percentage growth** (recent period vs. earlier period)
- Flags **emerging risk** if 3-month growth exceeds `EMERGING_RISK_THRESHOLD_PCT` (default: 20%)

### Decision Store (`services/decision_store.py`)

Dual-mode storage:
- **In-memory cache** for fast reads
- **SQLite write-through** for persistence across restarts
- Same public API: `save_decision()`, `get_decision()`, `get_all_decisions()`, `log_event()`, `get_events_for_decision()`, `clear()`

### Ingestion Service (`services/ingestion.py`)

Universal file adapter:
1. Loads CSV/XLSX via Pandas
2. Tries explicit YAML mapping configs → auto-detects from `config/` directory
3. Falls back to heuristic column matching (with confidence gate at 80%)
4. Transforms all rows into `CanonicalFinancialRecord`
5. Persists to `data/transactions.json`

Rejects ambiguous datasets rather than guessing.

---

## Frontend

### Pages

| Route | Page | Description |
|---|---|---|
| `/` | Decision Inbox | Pending + history decisions, executive summary KPIs |
| `/upload` | Upload | CSV/XLSX file upload |
| `/exposure` | Exposure Dashboard | Vendor concentration heatmap, exposure table, KPIs |

### Decision Detail Modal

Opened by clicking any decision card. Contains:

1. **Decision Context** — Rule ID, analysis period, metrics
2. **Financial Exposure Panel** — Annual spend, category share, worst-case exposure, shock impacts
3. **Price Shock Simulator** — Preset buttons (5%, 10%, 15%) + custom slider (1–50%), live EBITDA delta
4. **Rationale** — Rule-generated explanation
5. **Audit Trail** — Timeline of all lifecycle events

### Navigation

- **Exposure** button → `/exposure` dashboard
- **Export** button → Downloads `.xlsx` executive report
- **Upload** button → In-page file upload dialog

---

## Testing

### Running Tests

```bash
cd backend

# Run all Phase 2 tests
python -m pytest tests/ -v

# Run specific test suites
python -m pytest tests/test_exposure_engine.py -v     # 8 tests
python -m pytest tests/test_price_shock.py -v          # 5 tests
python -m pytest tests/test_trend_engine.py -v         # 9 tests
python -m pytest tests/test_state_transitions.py -v    # 10 tests
python -m pytest tests/test_context_aware_engine.py -v # 3 tests

# Run stress tests
python -m pytest tests/stress/ -v
```

### Test Coverage Summary

| Suite | Tests | Covers |
|---|---|---|
| `test_exposure_engine.py` | 8 | Shock impact math, per-vendor exposure, edge cases, determinism |
| `test_price_shock.py` | 5 | Simulation, vendor lookup, zero shock, determinism, risk escalation |
| `test_trend_engine.py` | 9 | Rolling avg, growth%, decline, insufficient data, zero spend |
| `test_state_transitions.py` | 10 | PENDING→APPROVED/REJECTED/DEFERRED, store CRUD, deterministic IDs |
| `test_context_aware_engine.py` | 3 | Category thresholds, default fallback, high-risk scoring |
| `stress/` | 5 suites | Audit integrity, boundary conditions, consistency, robustness, scale |

**Total: 35+ tests, all passing.**

---

## Configuration

### Policy Configuration (`app/config/policies.yaml`)

Category-specific thresholds drive how the Decision Engine evaluates vendors:

```yaml
categories:
  Cloud Infrastructure:
    spend_threshold: 20000
    frequency_threshold: 8
    savings_rate: 0.08
    regulatory_sensitive: false
    operational_critical: true

  SaaS:
    spend_threshold: 10000
    frequency_threshold: 6
    savings_rate: 0.12
    ...

default:
  spend_threshold: 5000
  frequency_threshold: 5
  savings_rate: 0.10
```

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/capital_engine.db` | Database connection string |

### Configurable Constants

| Constant | Location | Default | Description |
|---|---|---|---|
| `EBITDA_MARGIN` | `services/exposure_engine.py` | `0.25` | EBITDA margin for impact calculation |
| `EMERGING_RISK_THRESHOLD_PCT` | `services/trend_engine.py` | `20.0` | Growth % to flag emerging risk |
| `CONFIDENCE_THRESHOLD` | `core/heuristics.py` | `0.8` | Minimum confidence for heuristic mapping |

---

## Design Principles

### 1. Determinism
Same inputs produce identical outputs, always. Decision IDs use `uuid5` (namespace-based), ensuring stability across restarts. No random number generation anywhere in the pipeline.

### 2. Idempotency
Re-uploading the same dataset produces the same decisions. Re-running exposure calculations on unchanged data returns identical results.

### 3. Audit Integrity
Every decision lifecycle change (CREATED → APPROVED/REJECTED/DEFERRED) is recorded as an immutable event in `decision_events`. Events are append-only — no UPDATE or DELETE operations.

### 4. No Duplication
The `calculate_shock_impact()` function is defined once in `exposure_engine.py` and reused by both the exposure calculations and the price shock simulator.

### 5. Reject Ambiguity
The ingestion pipeline refuses to guess when column confidence is below 80%. It returns an explicit error rather than producing incorrect mappings.

### 6. DDD Structure
Clear separation of concerns: `models/` (data), `services/` (logic), `api/` (presentation), `simulation/` (what-if), `exports/` (reporting), `connectors/` (integration), `db/` (persistence).

---

## Decision Lifecycle

```
                ┌──────────┐
     Upload ──▶ │ PENDING  │
                └────┬─────┘
                     │
           ┌─────────┼──────────┐
           ▼         ▼          ▼
     ┌──────────┐ ┌──────────┐ ┌──────────┐
     │ APPROVED │ │ REJECTED │ │ DEFERRED │
     └──────────┘ └──────────┘ └─────┬────┘
                                     │
                            ┌────────┼────────┐
                            ▼                 ▼
                      ┌──────────┐     ┌──────────┐
                      │ APPROVED │     │ REJECTED │
                      └──────────┘     └──────────┘
```

**Rules:**
- APPROVED and REJECTED are terminal states
- DEFERRED decisions can later be approved or rejected
- Rejections require a mandatory note
- Every transition is logged as a `DecisionEvent`

---

## Roadmap

### Completed (v2.0)

- ✅ Financial Exposure Engine
- ✅ Price Shock Simulator
- ✅ Excel Executive Export
- ✅ SQLite Persistent Database
- ✅ Trend Engine (rolling avg + growth)
- ✅ Connector Architecture Foundation
- ✅ Frontend Exposure Dashboard

### Future (v3.0)

- ⬜ PostgreSQL migration for production scale
- ⬜ Alembic migration scripts
- ⬜ Real ServiceNow/ERP connector implementations
- ⬜ Multi-user authentication + RBAC
- ⬜ Webhook notifications for decision state changes
- ⬜ Budget constraint optimization engine
- ⬜ Historical trend charts (line graphs)
- ⬜ Bulk decision approval workflow

---

## License

Internal project. All rights reserved.

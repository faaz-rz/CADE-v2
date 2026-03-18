# Capital Risk & Exposure Platform v2

> AI-driven capital allocation decision engine with financial exposure analysis, price shock simulation, and executive reporting.

---

## Overview

The **Capital Risk & Exposure Platform** analyzes financial transaction data and produces actionable capital allocation decisions. It answers the question:

> *"If Vendor X increases price by 15%, what is the EBITDA impact and financial exposure?"*

The system ingests CSV/XLSX spend data, applies rule-based analysis to identify high-spend and high-frequency vendors, calculates financial exposure, simulates price shocks, and generates executive reports — all deterministically, with a full audit trail.

## Key Capabilities

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

## Getting Started

1. **Installation**: Clone the repository and install dependencies
   ```bash
   git clone https://github.com/faaz-rz/CADE.git
   cd CADE
   npm install
   ```

2. **Setup**: Follow the configuration guide in PROJECT.md for environment setup

3. **Usage**: Start the application with:
   ```bash
   npm start
   ```

## Documentation

For comprehensive documentation on architecture, API references, tech stack, and detailed module descriptions, please refer to [PROJECT.md](./PROJECT.md).

## Contributing

We welcome contributions! Please review our contribution guidelines in PROJECT.md for details on how to get involved.

## License

This project is licensed under the MIT License. See the LICENSE file for more information.
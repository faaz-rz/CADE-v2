# CADE: Capital Allocation Decision Engine
## Architectural & Logical Systems Report

This report serves as a high-level executive summary and technical deep-dive into the core deterministic engines, heuristic models, and probabilistic simulations driving the CADE platform.

---

### 1. Ingestion & Heuristic Pipeline
When transaction data is uploaded to CADE, it passes through a **5-tier Schema Inference Pipeline** designed to map raw CSV/Excel columns into standardized CADE fields without requiring manual human input.

**Logic Pipeline:**
1. **Explicit Mapping**: Checks if the API payload explicitly defined the mapping.
2. **YAML Configuration**: Looks in local configs for pre-defined schema templates for specific file structures.
3. **Keyword & Fuzzy Heuristics**: 
   - Uses `rapidfuzz` to calculate Levenshtein/Token Set Ratios against built-in domain dictionaries.
   - Triggers on subsets like `entity` (vendor, payee, supplier) and `amount` (total cost, spend).
   - Dynamically scales numbers if headers denote thousands/millions (e.g., `(in k)`, `(thousands)`).
4. **LLM Fallback**: If standard fuzzy matching yields no confidence, a small sample of the dataframe is securely processed via Groq AI to infer layout from structure context.
5. **Rejection**: Files that lack minimum thresholds for deterministic matching are rejected for safety.

---

### 2. The Decision Engine (Determinism Model)
The objective of the Decision Engine is to look at processed vendor data and emit *actionable financial directives*. 

**Core Constraint: "One Vendor, One Action"**
To prevent executive dashboard fatigue, CADE enforces strict prioritization syntax. It evaluates 7 distinct logic rules per vendor in descending order of severity. If a rule triggers, an actionable Decision is generated, and the vendor is excluded from further rule evaluations.

**The 7 Prioritized Rules:**
1. **`CONCENTRATION_RISK`**: If a vendor accounts for **≥ 40%** of total spend within its category. *Action: Vendor Reduction.*
2. **`RAPID_GROWTH`**: Triggered by the Trend Engine if a vendor's 3-month trailing growth exceeds **20%**. Escalates to `HIGH` risk instantly if growth exceeds 50%.
3. **`HIGH_ABSOLUTE_SPEND`**: Spend is **≥ 5x** the baseline category spend threshold. *Action: Vendor Reduction / Negotiation.*
4. **`CONTRACT_RENEWAL`**: Checks if the vendor classification is `SaaS` and exceeds its baseline threshold. Recommends renegotiation modeling **15-20%** savings.
5. **`DUPLICATE_VENDOR_CATEGORY`**: Triggers if there are **≥ 3 vendors** within the same financial category. *Action: Consolidation.* Recommends terminating the smallest vendor for ~25% localized category savings.
6. **`HIGH_SPEND_BASELINE`**: Standard rule. Spend is **> 1x** the category threshold.
7. **`HIGH_FREQUENCY`**: Fallback rule. High transaction volume denoting chaotic micropayments.

Decisions are subsequently ranked by `Risk Level` (Critical/High/Medium/Low) then by predicting `Annual Impact ($)`.

---

### 3. Probabilistic Risk Assessment (Monte Carlo Simulation)
A standout capability of CADE is pricing forward risk computationally rather than heuristically.

**Engine Specifications:**
- **Vectorization**: Uses pure NumPy C-extensions to avoid standard Python loops. It calculates millions of array intersections in under a second.
- **Scale**: It performs **50,000 independent simulations** and **200,000 HD simulations** per vendor, processing millions of generated variations against historical baseline spend.
- **Distributions**: CADE does not rely on a standard Normal / Gaussian bell curve. It utilizes **Student-t Distributions (df=4)**. This specifically allows for "Fat Tails," mathematically modeling the probability of catastrophic black swan events (e.g., sudden AWS price hikes or SaaS hyper-scale bills).
- **Correlations**: When executing a Portfolio-wide simulation, it employs **Cholesky Decomposition**. It understands that a shock in one database vendor is positively correlated (~0.7) to a shock in an infrastructure vendor, adjusting portfolio crash dynamics accordingly rather than mistakenly assuming standalone isolation.

**Outputs Generated for the CFO:**
- **P05 / P10 / P50 / P95 Boundaries**: Establishes best case, expected median, and extreme worst-case scenarios.
- **Probability Matrices**: E.g., *"There is a 14% mathematical probability that this category will exceed a $500,000 shock variance."*
- **Convergence Scoring & 95% Confidence Intervals**: Ensures that the randomized outputs have statically converged before presenting them to executives.

---

### 4. AI Narrative Generation
While raw matrices and logic rules build the foundation, the final tier generates human-ready briefings. For each high-impact decision, context parameters (Rule Triggered, Monte Carlo Worst Case Shock, Projected Savings) are passed to an LLM to cast the mathematical data into a board-ready executive summary paragraph (e.g., *"Vendor AWS dominates 80% of Cloud spend resulting in Concentration Risk. Simulations calculate a P90 shock potential of... "*).

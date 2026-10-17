# 📈 Sales Analytics Dashboard

> **Understand Sales. Discover Trends. Make Better Decisions.**

An interactive sales intelligence workspace built with **Python**, **Streamlit**, and **Plotly** that transforms raw sales data into actionable commercial insights and visual reports.

---

## 🌟 Project Overview

The **Sales Analytics Dashboard** is engineered to help business owners, sales executives, and analysts understand commercial health without relying on rigid CSV templates or proprietary schemas. It accepts multi-format sales spreadsheets (CSV, XLSX, XLS), profiles structural data quality, aligns diverse column aliases using confidence-based matching, and prepares data for multi-dimensional revenue and margin analysis.

### What the Application Answers:
- **Revenue Drivers**: How much revenue the business generates and transaction volume.
- **Profitability & Margins**: How discounts impact gross margins and where net loss occurs.
- **Assortment Performance**: Which product categories and lines contribute the majority of revenue.
- **Geographic Dynamics**: Which regions, states, and cities represent primary markets.
- **Data Health**: What missing values, duplicate transactions, or formatting anomalies exist in the data.

---

## 🛠️ Technology Stack

| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Language** | Python | 3.11 – 3.13 | Core programming runtime |
| **Web Framework** | Streamlit | 1.49.1 | Interactive web application and multipage routing |
| **Data Processing** | Pandas & NumPy | 2.3.2 / 2.3.3 | In-memory data manipulation, profiling, and aggregations |
| **Spreadsheet Engine** | OpenPyXL | 3.1.5 | Microsoft Excel (.xlsx) file parsing |
| **Visualizations** | Plotly | 6.3.0 | Custom-themed dark interactive charts |
| **Statistics** | SciPy | 1.16.2 | Advanced distribution analysis |
| **Testing** | Pytest | 8.4.2 | Automated unit and integration testing suite |
| **Code Quality** | Ruff | 0.16.2 | Fast Python linting and code formatting |
| **CI / Automation** | GitHub Actions | Ubuntu Latest | Continuous integration workflow across Python 3.11-3.13 |

---

## 🗺️ Implementation Status: Master Prompt 3 of 3 (Complete & Production Hardened)

This project has been fully developed, audited, tested, and hardened across three sequential phases:

- [x] **Phase 1: Foundation, Architecture, UI/UX, and Data Ingestion (COMPLETED)**
  - Modular project architecture and directory structure.
  - Dark Graphite, Electric Violet, and Cyan design system with responsive CSS.
  - Streamlit `st.navigation` multipage flow with state-preserving Previous / Next controls.
  - Robust file loader supporting CSV, XLSX, encoding fallbacks (`utf-8`, `latin-1`, `cp1252`), and size caps (50 MB).
  - In-depth dataset profiling (semantic type inference, quartiles, missing cell rates, quality warnings).
  - Confidence-based column mapping system with 22 standard business fields, alias detection, and manual overrides.
  - Bundled 150-record Superstore sample dataset with 1-click loading.
  - Plotly dark theme registration and chart factory.
- [x] **Phase 2: Complete Analytics Engine, Visualizations & Insights (COMPLETED)**
  - **Canonical Data Model**: Schema validation, capability negotiation, and conservative derivation rules (`qty * price`, `sales - cost`).
  - **Executive Metrics Engine**: Schema-aware calculation of 8+ core KPIs (Gross/Net Revenue, Orders, AOV, Net Profit, Margin %, ASP, Return Rate).
  - **Time-Series Engine**: Multi-frequency resampling (D, W, ME, QE, YE), moving averages, Period-over-Period (PoP) comparison, and YoY tables.
  - **Product & Assortment**: Top/Bottom rankings, category rollups, and cumulative Pareto 80/20 concentration analysis.
  - **Territory & Geography**: Multi-metric rollups across Region, Country, State, and City dimensions with local Choropleth maps.
  - **Customer Intelligence**: Customer revenue rankings, Top-5 / Top-10 concentration share, and repeat vs. single-order retention metrics.
  - **Profitability & Discounts**: Loss-making line item audit and 4-tier discount band segmentation (`0%`, `1-10%`, `11-20%`, `>20%`).
  - **Statistical Hub**: Descriptive statistics (Skewness, IQR), Pearson/Spearman correlation matrices, and IQR outlier detection.
  - **Dynamic Multi-Dimensional Filter System**: Real-time filtering across Date range, Categories, Regions, Channels, and Transaction Types (Positive vs Returns).
  - **Evidence-Based Automated Insights**: Deterministic, zero-hallucination business findings without external AI/LLM dependencies.
  - **Expanded Plotly Visualizations & Explorer**: 15+ interactive chart types (Treemap, Waterfall, Funnel, 3D Scatter, Donut, etc.) plus a self-service Chart Explorer.
  - **Multi-Currency & Indian Formatting**: Support for USD, INR (Lakhs/Crores), EUR, GBP, JPY, CAD, and AUD without mutating underlying numerical values.
  - **10-Tab Guided Workspace**: Executive Overview, Sales Trends, Products & Assortment, Geography, Customers, Profitability, Statistics, Chart Explorer, Data Explorer, and Insights Center.
- [x] **Phase 3: Finalization, Hardening, Testing & Deployment (COMPLETED)**
  - **Import Error Remediation**: Full implementation of `create_heatmap` with dual tabular/matrix modes and error-safe empty fallbacks.
  - **Mapping Hardening**: Multi-token constraint enforcement on alias matching eliminating false positives (e.g. `payment_method` on standard Superstore schemas).
  - **Interactive 2D Heatmap Explorer**: Integrated dimensional heatmap slicing into the self-service Chart Explorer.
  - **Export Synchronization**: Synchronized session-state filter scoping with Step 6 CSV and Markdown report generators.
  - **Comprehensive Quality Assurance**: 65 automated unit, integration, and regression tests (**65 passed, 0 failures, 0 errors**; `ruff check .` with 0 warnings).
  - **Streamlit Community Cloud Deployment Ready**: Verified `app.py` entrypoint, portable `.streamlit/config.toml`, clean `requirements.txt`, and zero secrets.

---

## 📂 Project Structure

```
sales-analytics-dashboard/
│
├── app.py                      # Main entrypoint and navigation router
├── requirements.txt            # Production runtime dependencies (Streamlit Cloud)
├── requirements-dev.txt        # Development, testing & linting dependencies
├── pyproject.toml              # Ruff and Pytest configuration
├── README.md                   # Complete project documentation
├── .gitignore                  # Git tracking & security rules
│
├── .streamlit/
│   └── config.toml             # Streamlit dark theme & server settings
│
├── assets/
│   ├── README.md
│   └── styles.css              # Custom CSS design system
│
├── src/
│   ├── __init__.py
│   ├── config.py               # Constants, UI tokens, and 22 standard fields
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py           # Ingestion and multi-encoding CSV/Excel reader
│   │   ├── validation.py       # Structural checks and header sanitization
│   │   ├── profiling.py        # Semantic inference and exploratory audit
│   │   ├── column_mapping.py   # Confidence-based business field mapper
│   │   └── canonical.py        # Canonical analytical data model & capabilities
│   │
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── metrics.py          # Comprehensive Executive KPI engine
│   │   ├── time_series.py      # Resampling, PoP growth, YoY tables
│   │   ├── products.py         # Product ranking, Category rollup, Pareto 80/20
│   │   ├── geography.py        # Territory rollups across 4 geo-dimensions
│   │   ├── customers.py        # Concentration risk, order frequency & repeat rate
│   │   ├── profitability.py    # Loss-making audits & 4-tier discount elasticity
│   │   ├── statistics.py       # Descriptive stats, Pearson/Spearman, IQR outliers
│   │   ├── filters.py          # Pure analytical multi-dimensional filtering
│   │   ├── aggregations.py     # Backward-compatible aggregation routines
│   │   └── insights.py         # Deterministic evidence-based commercial signals
│   │
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── chart_factory.py    # Reusable Plotly chart builders (15+ chart types)
│   │   ├── explorer.py         # Self-service Interactive Chart Explorer
│   │   └── themes.py           # Plotly Dark Graphite / Violet / Cyan template
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── layout.py           # Header, live status banner, and footer
│   │   ├── components.py       # Metric cards, step indicators, alert boxes
│   │   ├── navigation.py       # Session state management and guarded steps
│   │   └── filters.py          # Dynamic sidebar filter component
│   │
│   └── utils/
│       ├── __init__.py
│       ├── formatting.py       # Currency, Lakhs/Crores, percentages, normalization
│       └── errors.py           # User-safe error hierarchy
│
├── pages/
│   ├── README.md
│   ├── 1_Overview.py           # Step 1: Welcome & sample dataset loader
│   ├── 2_Upload_Data.py        # Step 2: Upload interface & file validation
│   ├── 3_Data_Inspection.py    # Step 3: Data health audit & profiling
│   ├── 4_Column_Mapping.py     # Step 4: Schema mapping & alignment
│   ├── 5_Analysis_Workspace.py # Step 5: 10-Tab interactive analytics workspace
│   └── 6_Reports_and_Export.py # Step 6: Multi-dataset CSV & Markdown exports
│
├── data/
│   ├── README.md               # Data privacy notes
│   └── samples/
│       ├── README.md           # Dataset sources & attribution
│       └── superstore_sample.csv # Bundled 150-record sample dataset
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Synthetic test fixtures
│   ├── test_loader.py          # Ingestion & encoding tests
│   ├── test_validation.py      # Structural validation tests
│   ├── test_profiling.py       # Statistical profiling tests
│   ├── test_column_mapping.py  # Column mapping & alias tests
│   ├── test_canonical.py       # Canonical data model & derivation tests
│   ├── test_metrics_engine.py  # Executive KPI & edge case tests
│   ├── test_time_series.py     # Resampling, growth & zero-base tests
│   ├── test_products_pareto.py # Product ranking & Pareto 80/20 tests
│   ├── test_customers.py       # Customer concentration & repeat rate tests
│   ├── test_profitability.py   # Loss-making audits & discount tier tests
│   ├── test_statistics.py      # Descriptive, correlation & IQR outlier tests
│   ├── test_filters.py         # Multi-dimensional filter tests
│   ├── test_insights.py        # Evidence-based automated insight tests
│   ├── test_visualizations.py  # Chart factory, heatmap, and Plotly tests
│   ├── test_html_rendering.py  # Clean UI rendering & AppTest regression tests
│   └── test_metrics.py         # Phase 1 backward-compatibility tests
│
├── docs/
│   ├── architecture.md         # Architecture and lifecycle design
│   ├── data_dictionary.md      # 22 standard field definitions and aliases
│   ├── analytics_methodology.md# Mathematical formulas & business definitions
│   └── testing_checklist.md    # Quality assurance and test verification matrix
│
└── .github/
    └── workflows/
        └── tests.yml           # GitHub Actions CI workflow
```

---

## ⚡ Quick Start & Local Execution

### 1. Prerequisites
- **Python**: 3.11, 3.12, or 3.13 installed (`python --version`).
- **Git**: Installed (`git --version`).

### 2. Clone or Enter Project
```bash
git clone https://github.com/<your-username>/sales-analytics-dashboard.git
cd sales-analytics-dashboard
```

### 3. Create & Activate Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Windows (PowerShell / Command Prompt)
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 4. Install Dependencies
```bash
# To run the application:
pip install -r requirements.txt

# Or for running tests and linter as well:
pip install -r requirements-dev.txt
```

### 5. Launch the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🚀 Free Deployment on Streamlit Community Cloud

The application is pre-configured for free, 1-click deployment on **Streamlit Community Cloud**.

### Deployment Walkthrough:

1. **Push your code to GitHub**:
   Ensure all files are committed and pushed to your GitHub repository (e.g., `main` or `master` branch):
   ```bash
   git add .
   git commit -m "feat: prepare repository for Streamlit Community Cloud deployment"
   git push origin master
   ```

2. **Sign in to Streamlit Community Cloud**:
   - Navigate to [share.streamlit.io](https://share.streamlit.io/).
   - Sign in using your GitHub account.

3. **Deploy the App**:
   - Click **"New app"** (or **"Create app"**).
   - In the deployment modal, select:
     - **Repository**: `<your-github-username>/sales-analytics-dashboard`
     - **Branch**: `master` (or `main`)
     - **Main file path**: `app.py`
     - **App URL**: Choose your preferred subdomain (e.g. `your-sales-analytics.streamlit.app`).

4. **Verify Advanced Settings**:
   - Click **"Advanced settings..."** before deploying.
   - **Python Version**: Select **3.11** or **3.12** (recommended for fastest package wheel resolution).
   - **Secrets**: Leave empty (the application does not require any environment variables, API keys, or external database credentials; all analytical processing is self-contained and in-memory).

5. **Click "Deploy!"**:
   - Streamlit Cloud will automatically clone your repository, install dependencies from `requirements.txt`, load `.streamlit/config.toml`, and launch `app.py`.
   - Your live dashboard will be accessible via its public URL.

---

## 🧪 Running the Automated Test Suite

Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

Run the complete Pytest suite (65 passing tests):
```bash
pytest -v
```

Run code quality linting with Ruff:
```bash
ruff check .
```

---

## 🔒 Data Privacy & Security Guardrails

- **Zero External API Calls**: The application does not transmit uploaded datasets to OpenAI, cloud storage, or external LLM APIs.
- **In-Memory Processing**: Uploaded files exist solely in memory during the active session.
- **No Evaluation of Untrusted Code**: Strictly avoids `eval()`, `exec()`, or untrusted Python `pickle` deserialization.
- **Sanitized Upload Boundaries**: Validates MIME types, extensions (`.csv`, `.xlsx`, `.xls`), and caps uploads at 50 MB.
- **Git Exclusions**: `.gitignore` strictly excludes `data/uploads/`, `.env` files, credentials, and temporary working copies.

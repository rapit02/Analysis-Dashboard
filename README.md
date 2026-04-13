# Analysis-Dashboard

# Challenge 2 — Chicago Taxi Data Analysis

## Overview

Analysis of 2,016,157 Chicago taxi trips from January to June 2020.

Built with Python, pandas, DuckDB, matplotlib, and Streamlit.

---

## Project Structure
```
challenge-2/
├── data/
│   ├── analysis.ipynb          # Main analysis notebook
│   ├── data_model.png          # Star schema diagram (dbdiagram.io)
│   └── chicago_taxi_2020.csv   # Raw dataset (not tracked — 465MB)
└── dashboard/
    ├── app.py                  # Main Streamlit entry point
    ├── data.py                 # Data loading, cleaning, DuckDB queries
    ├── .streamlit/
    │   └── config.toml         # Theme configuration
    └── views/
        ├── overview.py         # Page 1 — metrics + monthly charts
        ├── demand.py           # Page 2 — peak hours + heatmap
        ├── companies.py        # Page 3 — market share + performance
        ├── payments.py         # Page 4 — payment behaviour + tipping
        ├── efficiency.py       # Page 5 — revenue per mile + per minute
        └── kpi.py              # Page 6 — CEO KPI RPATD
```

---

## Task 1 — Data Model

Designed a lightweight **star schema** centred on `fact_trips`.

**Fact table:**
- `fact_trips` — one row per taxi trip, all measurable values

**Dimension tables:**
- `dim_date` — date attributes (day of week, month, is_weekend)
- `dim_company` — taxi company names
- `dim_taxi` — individual taxi identifiers
- `dim_payment_type` — payment method names

**Design principle:** Model around the business event. The taxi trip is the core business event — every analytical question traces back to individual trips.

---

## Task 2 — Data Analysis

Five insights extracted from 1,933,226 cleaned trip records:

| Insight | Finding |
|---|---|
| Demand & Revenue Over Time | Sharp decline from March 2020 — external factors significantly impacted urban mobility |
| Peak Demand Patterns | 17:00 is peak hour — 8x more trips than quietest hour (4am). Thursday is busiest day |
| Company Market Share | 6 operators total. Flash Cab leads avg revenue per trip at $16.82 |
| Payment Behaviour | Credit card generates 59% more revenue per trip than cash. Cash tips are invisible to the dataset |
| Operational Efficiency | Short trips (<1 mile) generate $17.42/mile vs $3.07/mile for long trips (>10 miles) |

---

## Task 3 — CEO KPI

**Revenue Per Active Taxi Per Day (RPATD)**
```
RPATD = Total Daily Revenue / Number of Taxis With ≥1 Trip That Day
```

**Why RPATD:**
- Controls for fleet size — total revenue grows just by adding taxis
- Actionable — a drop signals demand issues, pricing problems, or fleet oversizing
- Reflects real economics — every taxi has fixed daily costs
- Changes daily — useful for immediate decision making

**Ideal KPI (if cost data were available):**
Daily Contribution Margin Per Active Taxi = (Revenue − Variable Costs) / Active Taxis

**Key findings:**
- Jan–Feb baseline: $178.69 per active taxi per day
- Lowest point: $56.86 on March 29th (31.8% of baseline)
- Recovery by June 30th: 91.1% of baseline

---

## Data Cleaning

| Step | Rows Removed | Reason |
|---|---|---|
| Missing values | 769 | Null fare, tips, or taxi_id |
| Ghost trips | 52,364 | Zero miles AND zero seconds |
| Extreme outliers | 1,895 | Fare >$500, miles >100, seconds >14,400 |
| Zero-mile high-fare | 27,903 | Data entry errors — zero miles but fare >$20 |
| **Total removed** | **82,931** | **4.1% of raw dataset** |

---

## How To Run

### Jupyter Notebook
```bash
pip3 install jupyter pandas matplotlib seaborn duckdb
cd challenge-2/data
jupyter notebook
# Open analysis.ipynb
# Kernel → Restart Kernel and Run All Cells
```

### Streamlit Dashboard
```bash
pip3 install streamlit plotly duckdb pandas
cd challenge-2/dashboard
streamlit run app.py
```

Dashboard runs at `http://localhost:8501`

**Note:** The CSV file (`chicago_taxi_2020.csv`) is not tracked in git due to its size (465MB). Place it in `challenge-2/data/` before running.

---

## Tools

| Tool | Purpose |
|---|---|
| Python | Primary language |
| pandas | Data loading and cleaning |
| DuckDB | Analytical SQL queries on pandas DataFrames |
| matplotlib / seaborn | Jupyter notebook visualisation |
| plotly | Interactive dashboard charts |
| Streamlit | Dashboard framework |
| Jupyter Notebook | Exploratory analysis and documentation |

**Production alternative:** In a production environment, the cleaned data would be stored as Parquet files in AWS S3 and queried with AWS Athena — serverless, no infrastructure, ~$0.02 for this dataset size. The DuckDB SQL queries are directly portable to Athena.

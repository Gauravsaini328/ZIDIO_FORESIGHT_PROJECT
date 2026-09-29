# Project FORESIGHT – Demand & Inventory Intelligence

Project FORESIGHT is an end-to-end demand forecasting and inventory analytics project built for **NorthBay Living**, a D2C home and lifestyle brand.

The goal is simple: use historical sales and inventory data to understand demand, forecast the next 8 weeks, identify stockout and overstock risks, and turn those results into practical inventory actions.

---

## Project Overview

NorthBay Living has around 200 SKUs, but the available datasets contain reliable master and sales information for **50 matched SKUs**.

This project covers the complete analytics workflow:

**Raw Data → Data Cleaning → EDA → Demand Forecasting → Inventory Risk Scoring → Power BI Dashboard**

The final analysis focuses on 50 SKUs and produces an 8-week weekly demand forecast along with inventory risk and value-at-stake estimates.

---

## Business Problem

The business needs to answer questions such as:

- Which products are likely to have higher demand in the coming weeks?
- Which SKUs may face a stockout?
- Which SKUs are carrying excessive inventory?
- How much inventory value is exposed to these risks?
- What action should the inventory team take?

The project converts these questions into a repeatable data and analytics workflow.

---

## Project Workflow

```text
Raw Sales / Inventory / Calendar / SKU Data
                    ↓
        Python Data Quality & Cleaning
                    ↓
              EDA & Insights
                    ↓
          Weekly Demand Forecast
                    ↓
          Inventory Risk Scoring
                    ↓
            Power BI Dashboard
                    ↓
       Prioritized Inventory Actions
```

---

## Dataset

The project uses four main data sources:

| Dataset | Description |
|---|---|
| Sales | Daily SKU-level sales, units, revenue and price |
| SKU Master | Product, category, pricing and margin information |
| Calendar | Date, holiday and promotion information |
| Inventory | Inventory snapshots, stock, on-order quantity, lead time and safety stock |

### Data Size

| Item | Count |
|---|---:|
| Sales records | 36,550 |
| Matched SKUs | 50 |
| Calendar days | 731 |
| Raw inventory records | 4,800 |
| Analysis-ready inventory records | 1,200 |

Some inventory records belonged to SKU IDs that were not present in the SKU master or sales data. These unmatched inventory-only records were excluded from the analysis-ready inventory dataset.

---

## 1. Data Pipeline

The data cleaning pipeline is implemented in `src/pipeline.py`.

The pipeline:

- loads the four raw datasets
- converts required columns to appropriate datatypes
- checks missing values
- checks duplicate records
- checks invalid negative values
- checks SKU consistency
- validates sales and calendar date ranges
- handles missing calendar event values
- removes duplicate rows
- keeps inventory records associated with the available SKU master
- saves the cleaned datasets

The pipeline can be rerun from the raw data instead of relying on manually cleaned files.

---

## 2. Exploratory Data Analysis

EDA was performed using:

- `notebooks/data_understanding.ipynb`
- `notebooks/eda.ipynb`

### Key Findings

**Category demand**
Home Decor had the highest total unit sales: **132,570 units**.

**Promotion association**
Average daily demand was higher on promotion days:

| Day type | Average daily demand |
|---|---:|
| Non-promotion | 13.48 units/day |
| Promotion | 18.61 units/day |

This is an observed association in the available data and should not be interpreted as proof of causation.

**Yearly pattern**
Monthly demand patterns across 2024 and 2025 were broadly similar, suggesting recurring yearly patterns in the available history.

**Low-demand SKU**
SKU011 had the lowest average daily demand: **2.67 units/day**.
SKU011 and SKU028 also showed negative gross margins, so low demand was considered together with margin and inventory exposure.

---

## 3. Demand Forecasting

Forecasting was developed in `notebooks/forecasting.ipynb`.

The model forecasts weekly SKU-level demand for the next **8 weeks**.

### Model

The main forecasting model is **HistGradientBoostingRegressor**.

Features include:

- lagged demand (1, 2, 4, 8, 13, 26 and 52 weeks)
- rolling demand averages
- calendar features
- seasonal history

A **52-week seasonal-naive forecast** was used as the baseline.

### Validation

The model was evaluated using **4-fold rolling-origin cross-validation** to preserve the time-series structure and avoid using future information during training.

### Results

| Model | Average WAPE |
|---|---:|
| Gradient Boosting | **9.91%** |
| Seasonal Naive | **11.24%** |

The gradient boosting model achieved approximately **1.33 percentage points lower WAPE** than the seasonal-naive baseline in the project evaluation.

---

## 4. Inventory Risk Scoring

Inventory risk scoring is implemented in `src/risk.py`.

The framework evaluates two risks.

### Stockout Risk

Compares expected demand during the lead time with:

- current inventory
- on-order inventory
- safety stock

Risk levels: Low, Medium, High.

### Overstock Risk

Compares current stock with forward 30-day forecast demand.

| Level | Threshold |
|---|---|
| Low | ≤ 1× 30-day demand |
| Medium | > 1× |
| High | ≥ 2× |

### Decision Grid

| Stockout Risk | Overstock Risk | Recommended Action |
|---|---|---|
| High | Low | Reorder Now |
| Low | High | Markdown / Clear |
| High | Medium / High | Watch / Volatile |
| Medium | Any | Watch / Volatile |
| Any | Medium | Watch / Volatile |
| Low | Low | Healthy |

The risk scoring also calculates a **value at stake** based on estimated shortage and excess inventory exposure. This figure represents modeled inventory exposure and should not be interpreted as confirmed realized financial loss.

---

## 5. Power BI Dashboard

The planning dashboard is in `reports/Dashboard.pbix` and has three views.

**Executive Overview**

- Total SKUs
- High stockout SKUs
- High overstock SKUs
- Total value at stake
- Category demand
- Stockout risk distribution
- Overstock risk distribution

**Demand Forecast**

- Actual weekly demand
- 8-week forecast
- SKU filtering
- Category filtering

**Inventory Risk & Actions**

- Current stock
- On-order inventory
- Lead-time demand
- Stockout risk
- Overstock risk
- Recommended action
- Priority
- Value at stake

The dashboard lets business users move from **Forecast → Risk → Action** without reading the underlying model code.

---

## Project Results

| Metric | Result |
|---|---:|
| SKUs analyzed | 50 |
| Forecast horizon | 8 weeks |
| Model WAPE | 9.91% |
| Seasonal-naive WAPE | 11.24% |
| High stockout SKUs | 1 |
| High overstock SKUs | 5 |
| Modeled total value at stake | ≈ ₹9.64M |

These results are based on the historical data and assumptions used in the project.

---

## Repository Structure

```text
ZIDIO_FORESIGHT_PROJECT/
│
├── notebooks/
│   ├── data_understanding.ipynb
│   ├── eda.ipynb
│   └── forecasting.ipynb
│
├── reports/
│   ├── Dashboard.pbix
│   └── Project_FORESIGHT.pptx
│
├── src/
│   ├── pipeline.py
│   └── risk.py
│
├── data/
│   ├── raw/          # Local data, not committed
│   └── processed/    # Generated outputs, not committed
│
├── app/              # Reserved for future use
│
├── .gitignore
└── README.md
```

Raw and processed datasets are intentionally excluded from the Git repository.

---

## Tools & Technologies

Python · Pandas · NumPy · Scikit-learn · Matplotlib · Seaborn · Jupyter Notebook · Power BI · Git · GitHub

---

## Limitations

- The analysis covers 50 matched SKUs rather than the full 200-SKU business context.
- Forecast performance was evaluated using historical rolling-origin validation.
- Future demand can differ from historical patterns.
- Promotion analysis shows association, not causation.
- Inventory risk depends on forecast and inventory assumptions.
- Value at stake is a modeled exposure metric rather than confirmed financial loss.
- The project uses historical/static extracts rather than a live sales and inventory feed.

---

## Future Improvements

- Live sales and inventory data ingestion
- Periodic model retraining
- Forecast drift monitoring
- Improved promotion and event features
- Expanding SKU coverage as more data becomes available
- Further tuning of inventory decision thresholds

---

## Deliverables

- Reproducible Python data pipeline
- Data understanding and EDA notebooks
- Weekly SKU-level demand forecasting
- Rolling-origin forecast validation
- Inventory risk scoring
- Power BI planning dashboard
- Executive presentation

---

## Author

**Gaurav Saini**
B.Tech – Electronics & Communication Engineering

Interested in Data Engineering, Data Analytics, Python, SQL, Databricks, PySpark and Power BI.

---

## Note

Project FORESIGHT was developed as part of the **Zidio Data Scientist & Analytics Internship Project** for the NorthBay Living business case.
# 🚚 LogiGuard — Supply Chain Intelligence Dashboard

An interactive **Supply Chain Intelligence & Delivery Performance Analytics Dashboard** built with Python, Streamlit, Pandas, NumPy, and Plotly.

LogiGuard helps analyze shipment performance, delivery delays, vendor risk, country-level performance, shipment modes, freight costs, and overall data quality through an interactive business dashboard.

---

## 📊 Project Overview

Supply chain operations generate large amounts of shipment and delivery data. Analyzing this data manually can make it difficult to identify delivery delays, high-risk vendors, problematic countries, and operational inefficiencies.

**LogiGuard** transforms raw shipment data into an interactive analytics dashboard that enables users to:

- Monitor delivery performance
- Identify delayed shipments
- Compare vendors
- Analyze country-level delivery risk
- Compare shipment modes
- Monitor freight spending
- Detect data-quality issues
- Search individual shipment records
- Export filtered shipment data

---

## ✨ Key Features

### 🏠 Executive Overview

The Home dashboard provides high-level supply-chain KPIs including:

- Total Shipments
- On-Time Delivery Rate
- Delay Rate
- Average Delivery Delay
- Total Freight Cost

It also provides visual insights into:

- Delivery Status
- Monthly Shipment Volume
- Delay Rate by Shipment Mode
- Countries with Highest Delay Rates
- Highest Delay Country
- Highest Delay Vendor
- Most Used Shipment Mode

---

### 📦 Shipment Performance

The Shipment Performance page provides detailed comparisons across:

- Vendors
- Countries
- Shipment Modes

For each dimension, the dashboard analyzes:

- Total Shipments
- Delayed Shipments
- Delay Rate
- Average Delivery Delay

Interactive charts and tables make it easier to identify underperforming logistics dimensions.

---

### 🔍 Root Cause Analysis

The Root Cause Analysis section identifies areas where shipment delays are concentrated.

It analyzes:

- Country-level delivery risk
- Vendor-level delivery risk
- Shipment-mode risk

This helps users identify potential operational bottlenecks and prioritize areas requiring attention.

---

### 🧹 Data Quality Monitor

The Data Quality page provides an overview of the underlying dataset.

It monitors:

- Total Rows
- Total Columns
- Missing Cells
- Duplicate Rows
- Missing values by column
- Missing-value percentage
- Column data types
- Unique values

This helps ensure that analytics are based on clean and reliable data.

---

### 🔎 Shipment Explorer

The Shipment Explorer allows users to search and investigate individual shipment records.

Users can search using fields such as:

- Shipment ID
- Project Code
- Vendor
- Country
- Shipment Mode
- Product Group

The page also provides a **Download Filtered Data** option for exporting selected shipment records as CSV.

---

## 📈 Dashboard KPIs

LogiGuard calculates the following key performance indicators:

| KPI | Description |
|---|---|
| Total Shipments | Total number of shipment records |
| On-Time Delivery | Percentage of valid shipments delivered on or before the scheduled date |
| Delay Rate | Percentage of valid shipments delivered after the scheduled date |
| Average Delay | Average number of delayed days among delayed shipments |
| Freight Cost | Total freight expenditure |

---

## 🧮 Data Processing & Feature Engineering

The application performs several data preparation steps before visualization.

### Data Cleaning

- Removes BOM characters from column names
- Strips whitespace from column names
- Fixes common text-encoding issues
- Converts date columns to datetime
- Converts numerical fields to numeric data types
- Removes completely empty records
- Removes duplicate records

### Engineered Features

The application creates additional analytical fields including:

#### Delivery Delay Days

```text
Delivered to Client Date
        -
Scheduled Delivery Date
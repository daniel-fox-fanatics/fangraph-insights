# FanGraph Insights Dashboard

Interactive analytics dashboard showcasing insights from the FanGraph Cortex Agent, built with Streamlit and Plotly.

![Dashboard Preview](https://img.shields.io/badge/Fans-186.1M-E31837?style=for-the-badge)
![Revenue](https://img.shields.io/badge/Revenue-$5.2B-FFD700?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

## 🎯 Overview

This dashboard presents actionable insights derived from 5 distinct prompts commonly used against the **FanGraph Cortex Agent** in Snowflake Intelligence.

## ✨ New Features (v2.0)

- **🔄 Refresh Data Button** - Live data refresh from Snowflake with one click
- **🏢 OpCo Filter Dropdown** - Filter Overview and OpCo tabs by operating company
- **📊 Live Snowflake Connection** - Real-time queries against FANGRAPH tables
- **🎨 Fanatics Branding** - Official color scheme and styling

## 📊 Featured Insights

| Insight | Prompt | Key Finding |
|---------|--------|-------------|
| **OpCo Breakdown** | "What is total number of fans in fangraph, and what's the breakdown by each OpCo?" | 186.1M total fans, Commerce dominates at 91.8% |
| **Commerce Trends** | "Commerce transactions over the last 12 months compared to previous 12 months" | $5.2B revenue, +12.1% YoY growth |
| **NFL Distribution** | "What's the trend of NFL fans purchasing jerseys over the last 4 years?" | Cowboys lead with 2.55M fans |
| **Demographics** | "Tell me about the demographic profile of fans" | 41-50 age group largest at 14.6M |
| **League Preferences** | "Yearly breakdown of fans by league preference" | NFL leads with 38.2M fans |

## 🚀 Quick Start

### Option 1: Run Streamlit App (Recommended)

```bash
# Clone the repository
git clone https://github.com/daniel-fox-fanatics/fangraph-insights.git
cd fangraph-insights

# Install dependencies
pip install -r requirements.txt

# Set Snowflake credentials (or use existing connection)
export SNOWFLAKE_ACCOUNT="your_account"
export SNOWFLAKE_USER="your_user"
export SNOWFLAKE_PASSWORD="your_password"

# Run the app
streamlit run app.py
```

### Option 2: Static HTML Version

```bash
# Open the static HTML version in browser
open index.html
```

## 🛠️ Tech Stack

- **Framework**: Streamlit 1.32+
- **Visualization**: Plotly 5.18+
- **Database**: Snowflake (snowflake-connector-python)
- **Styling**: Custom CSS with Fanatics branding (Red #E31837, Black #1A1A1A)

## 📈 Dashboard Sections

1. **Executive Overview** - High-level KPIs, gauges, and league distribution
2. **OpCo Breakdown** - Fan distribution across business units with filtering
3. **Commerce Trends** - 24-month revenue and order analysis
4. **NFL Teams** - Top 15 teams by fan preference
5. **Demographics** - Age and geographic distribution
6. **League Preferences** - NFL, MLB, NBA, NCAA, NHL comparison

## 🎨 Features

- **Live Data Refresh** - Click to pull latest data from Snowflake
- **OpCo Filtering** - Drill down by operating company
- **Interactive Charts** - Plotly.js with hover, zoom, and export
- **Dark Mode** - Fanatics brand colors
- **Responsive Design** - Works on desktop and mobile
- **Data Caching** - 1-hour TTL for performance

## 🔗 Data Source

Data is sourced from:
- `FANGRAPH.ADMIN.FANGRAPH` - Main fan table (186M+ rows)
- `FANGRAPH.COMMERCE.DIM_COMMERCE_PURCHASE` - Commerce transactions

## 📁 Project Structure

```
fangraph-insights/
├── app.py              # Streamlit application
├── index.html          # Static HTML version
├── requirements.txt    # Python dependencies
├── README.md          
└── .streamlit/
    └── config.toml     # Streamlit theme config
```

## 📄 License

MIT License - Feel free to use and modify for your own analytics dashboards.

---

Built with Streamlit & Plotly | Powered by Snowflake Cortex | © 2026 Fanatics

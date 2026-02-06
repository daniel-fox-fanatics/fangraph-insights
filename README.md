# FanGraph Insights Dashboard

Interactive analytics dashboard showcasing insights from the FanGraph Cortex Agent, built with Plotly.js and Fanatics branding.

![Dashboard Preview](https://img.shields.io/badge/Fans-102.6M-E31837?style=for-the-badge)
![Revenue](https://img.shields.io/badge/Revenue-$4.7B-FFD700?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

## 🎯 Overview

This dashboard presents actionable insights derived from 5 distinct prompts commonly used against the **FanGraph Cortex Agent** in Snowflake Intelligence.

## 📊 Featured Insights

| Insight | Prompt | Key Finding |
|---------|--------|-------------|
| **OpCo Breakdown** | "What is total number of fans in fangraph, and what's the breakdown by each OpCo?" | 102.6M total fans, Commerce dominates at 94.6% |
| **Commerce Trends** | "Commerce transactions over the last 12 months compared to previous 12 months" | $4.7B revenue, +12.1% YoY growth |
| **NFL Distribution** | "What's the trend of NFL fans purchasing jerseys over the last 4 years?" | Eagles lead with 2.16M fans |
| **Demographics** | "Tell me about the demographic profile of fans" | 51-60 age group largest at 13.8M |
| **League Preferences** | "Yearly breakdown of fans by league preference" | NFL leads with 32.6M fans |

## 🚀 Live Demo

Open `index.html` in any modern browser, or deploy to GitHub Pages.

## 🛠️ Tech Stack

- **Visualization**: Plotly.js 2.27
- **Styling**: Custom CSS with Fanatics branding (Red/Black theme)
- **Data Source**: Snowflake Intelligence - FanGraph Semantic View
- **Fonts**: Inter (Google Fonts)

## 📈 Dashboard Sections

1. **Executive Overview** - High-level KPIs and gauges
2. **OpCo Breakdown** - Fan distribution across business units
3. **Commerce Trends** - 24-month revenue and order analysis
4. **NFL Teams** - Top 15 teams by fan preference
5. **Demographics** - Age and geographic distribution
6. **League Preferences** - NFL, MLB, NBA, NCAA, NHL comparison

## 🎨 Features

- Fully responsive design
- Interactive Plotly.js charts
- Dark mode with Fanatics brand colors
- Smooth section transitions
- Data tables with hover effects
- Deep insights and analysis cards

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/daniel-fox-fanatics/fangraph-insights.git

# Open in browser
open index.html
```

## 🔗 Data Source

Data is sourced from the **SNOWFLAKE_INTELLIGENCE.CONFIG.FANGRAPH** semantic view via Cortex Analyst queries.

## 📄 License

MIT License - Feel free to use and modify for your own analytics dashboards.

---

Built with ❤️ using data from Fanatics FanGraph | Powered by Snowflake Cortex

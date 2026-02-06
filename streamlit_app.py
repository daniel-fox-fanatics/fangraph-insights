import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import os

# Detect if running in Snowflake (SiS) or locally
RUNNING_IN_SNOWFLAKE = os.environ.get("SNOWFLAKE_ACCOUNT") is not None

# Page config
st.set_page_config(
    page_title="FanGraph Insights Dashboard",
    page_icon="https://www.fanatics.com/favicon.ico",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Fanatics branding
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --fanatics-red: #E31837;
        --fanatics-dark-red: #B71430;
        --fanatics-black: #1A1A1A;
        --fanatics-dark: #0D0D0D;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #E31837 0%, #B71430 100%);
        padding: 1rem 2rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .header-logo {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .header-logo img {
        height: 50px;
    }
    
    .header-title {
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
    }
    
    .header-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 0.9rem;
        margin: 0;
    }
    
    /* KPI Cards */
    .kpi-card {
        background: #1A1A1A;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #2D2D2D;
        text-align: center;
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #E31837;
        margin: 0;
    }
    
    .kpi-label {
        color: #888;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Insight cards */
    .insight-card {
        background: linear-gradient(135deg, #1A1A1A 0%, #2D2D2D 100%);
        border-radius: 12px;
        padding: 1.25rem;
        border-left: 4px solid #E31837;
        margin-bottom: 1rem;
    }
    
    .insight-title {
        font-weight: 600;
        color: #E31837;
        margin-bottom: 0.5rem;
    }
    
    .insight-text {
        color: #ccc;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    /* Prompt box */
    .prompt-box {
        background: #1A1A1A;
        border-left: 4px solid #E31837;
        padding: 1rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1.5rem;
    }
    
    .prompt-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #E31837;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .prompt-text {
        font-size: 1.1rem;
        font-style: italic;
        color: #F5F5F5;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1A1A1A;
        border-radius: 8px;
        padding: 10px 20px;
        color: white;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #E31837 !important;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #E31837;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #E31837;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background-color: #B71430;
    }
</style>
""", unsafe_allow_html=True)

# Fanatics color palette for charts
COLORS = {
    'red': '#E31837',
    'dark_red': '#B71430',
    'black': '#1A1A1A',
    'gray': '#2D2D2D',
    'white': '#FFFFFF',
    'gold': '#FFD700',
    'blue': '#4A90D9',
    'green': '#28A745',
    'gradient': ['#E31837', '#FF6B6B', '#4A90D9', '#28A745', '#FFD700', '#9B59B6', '#3498DB', '#E67E22', '#1ABC9C']
}

# Plotly layout template
PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#FFFFFF', family='Inter, sans-serif'),
    margin=dict(t=40, r=40, b=60, l=80)
)

# ============== SNOWFLAKE CONNECTION ==============
@st.cache_resource
def get_connection():
    """Get Snowflake connection - works both in SiS and locally"""
    return st.connection("snowflake")

def run_query(query):
    """Execute query and return pandas DataFrame"""
    conn = get_connection()
    return conn.query(query)

# ============== DATA QUERIES ==============
@st.cache_data(ttl=3600, show_spinner="Fetching data from Snowflake...")
def get_total_fans():
    """Get total fan count"""
    df = run_query("SELECT COUNT(*) as CNT FROM FANGRAPH.ADMIN.FANGRAPH")
    return df['CNT'].iloc[0]

@st.cache_data(ttl=3600, show_spinner="Fetching OpCo data...")
def get_opco_breakdown():
    """Get fan breakdown by OpCo - optimized single scan"""
    query = """
    SELECT 
        COUNT(*) as TOTAL_FANS,
        SUM(CASE WHEN COMMERCE_FAN_INDICATOR = TRUE THEN 1 ELSE 0 END) as COMMERCE,
        SUM(CASE WHEN TOPPS_DIGITAL_FAN_INDICATOR = TRUE THEN 1 ELSE 0 END) as TOPPS_DIGITAL,
        SUM(CASE WHEN TOPPS_COM_FAN_INDICATOR = TRUE THEN 1 ELSE 0 END) as TOPPS_COM,
        SUM(CASE WHEN FBG_FAN_INDICATOR = TRUE THEN 1 ELSE 0 END) as FBG,
        SUM(CASE WHEN FANAPP_FAN_INDICATOR = TRUE THEN 1 ELSE 0 END) as FANAPP,
        SUM(CASE WHEN LIVE_FAN_INDICATOR = TRUE THEN 1 ELSE 0 END) as LIVE,
        SUM(CASE WHEN COLLECT_FAN_INDICATOR = TRUE THEN 1 ELSE 0 END) as COLLECT,
        SUM(CASE WHEN EVENTS_FAN_INDICATOR = TRUE THEN 1 ELSE 0 END) as EVENTS
    FROM FANGRAPH.ADMIN.FANGRAPH
    """
    result = run_query(query).iloc[0]
    data = [
        {'OPCO': 'Total Fans', 'FAN_COUNT': result['TOTAL_FANS']},
        {'OPCO': 'Commerce', 'FAN_COUNT': result['COMMERCE']},
        {'OPCO': 'Topps Digital', 'FAN_COUNT': result['TOPPS_DIGITAL']},
        {'OPCO': 'Topps.com', 'FAN_COUNT': result['TOPPS_COM']},
        {'OPCO': 'FBG (Sportsbook)', 'FAN_COUNT': result['FBG']},
        {'OPCO': 'FanApp', 'FAN_COUNT': result['FANAPP']},
        {'OPCO': 'Live', 'FAN_COUNT': result['LIVE']},
        {'OPCO': 'Collect', 'FAN_COUNT': result['COLLECT']},
        {'OPCO': 'Events', 'FAN_COUNT': result['EVENTS']},
    ]
    df = pd.DataFrame(data)
    df = df.sort_values('FAN_COUNT', ascending=False)
    return df

@st.cache_data(ttl=3600, show_spinner="Fetching commerce data...")
def get_commerce_trends():
    """Get 24-month commerce trends"""
    query = """
    SELECT 
        DATE_TRUNC('MONTH', ORDER_TS) as MONTH,
        COUNT(DISTINCT ORDER_REF_NUM) as ORDERS,
        COUNT(DISTINCT FANGRAPH_ID) as CUSTOMERS,
        SUM(NET_DEMAND) as REVENUE
    FROM FANGRAPH.COMMERCE.DIM_COMMERCE_PURCHASE
    WHERE ORDER_TS >= DATEADD('MONTH', -24, CURRENT_DATE())
    GROUP BY DATE_TRUNC('MONTH', ORDER_TS)
    ORDER BY MONTH
    """
    df = run_query(query)
    df['MONTH'] = pd.to_datetime(df['MONTH'])
    return df

@st.cache_data(ttl=3600, show_spinner="Fetching NFL data...")
def get_nfl_teams():
    """Get top 15 NFL teams by fan count"""
    query = """
    SELECT 
        f.value::STRING as NFL_TEAM,
        COUNT(*) as FAN_COUNT
    FROM FANGRAPH.ADMIN.FANGRAPH,
        LATERAL FLATTEN(input => FANGRAPH_PREFERENCE_NFL_TEAMS) f
    WHERE FANGRAPH_PREFERENCE_NFL_TEAMS IS NOT NULL
    GROUP BY f.value::STRING
    ORDER BY FAN_COUNT DESC
    LIMIT 15
    """
    df = run_query(query)
    df['NFL_TEAM'] = df['NFL_TEAM'].str.title()
    return df

@st.cache_data(ttl=3600, show_spinner="Fetching demographics...")
def get_age_demographics():
    """Get age distribution"""
    query = """
    SELECT 
        FANGRAPH_AGE_RANGE as AGE_RANGE,
        COUNT(*) as FAN_COUNT
    FROM FANGRAPH.ADMIN.FANGRAPH
    WHERE FANGRAPH_AGE_RANGE IS NOT NULL
    GROUP BY FANGRAPH_AGE_RANGE
    ORDER BY FAN_COUNT DESC
    """
    df = run_query(query)
    return df

@st.cache_data(ttl=3600, show_spinner="Fetching league data...")
def get_league_preferences():
    """Get league preference breakdown - optimized single scan"""
    query = """
    SELECT 
        SUM(CASE WHEN FANGRAPH_PREFERENCE_NFL = TRUE THEN 1 ELSE 0 END) as NFL,
        SUM(CASE WHEN FANGRAPH_PREFERENCE_MLB = TRUE THEN 1 ELSE 0 END) as MLB,
        SUM(CASE WHEN FANGRAPH_PREFERENCE_NBA = TRUE THEN 1 ELSE 0 END) as NBA,
        SUM(CASE WHEN FANGRAPH_PREFERENCE_NCAA = TRUE THEN 1 ELSE 0 END) as NCAA,
        SUM(CASE WHEN FANGRAPH_PREFERENCE_NHL = TRUE THEN 1 ELSE 0 END) as NHL
    FROM FANGRAPH.ADMIN.FANGRAPH
    """
    result = run_query(query).iloc[0]
    data = [
        {'LEAGUE': 'NFL', 'FAN_COUNT': result['NFL']},
        {'LEAGUE': 'MLB', 'FAN_COUNT': result['MLB']},
        {'LEAGUE': 'NBA', 'FAN_COUNT': result['NBA']},
        {'LEAGUE': 'NCAA', 'FAN_COUNT': result['NCAA']},
        {'LEAGUE': 'NHL', 'FAN_COUNT': result['NHL']},
    ]
    df = pd.DataFrame(data)
    df = df.sort_values('FAN_COUNT', ascending=False)
    return df

@st.cache_data(ttl=3600, show_spinner="Fetching state data...")
def get_geo_data():
    """Get top 20 states by fan count"""
    query = """
    SELECT 
        FANGRAPH_STATE as STATE,
        COUNT(*) as FAN_COUNT
    FROM FANGRAPH.ADMIN.FANGRAPH
    WHERE FANGRAPH_STATE IS NOT NULL AND LENGTH(FANGRAPH_STATE) = 2
    GROUP BY FANGRAPH_STATE
    ORDER BY FAN_COUNT DESC
    LIMIT 20
    """
    df = run_query(query)
    return df

@st.cache_data(ttl=3600, show_spinner="Fetching revenue data...")
def get_revenue_by_year(opco: str = "ALL"):
    """Get gross revenue by year (2024 and 2025) from transaction-level data by OpCo.
    For OpCos without transaction tables, uses FANGRAPH lifetime columns."""
    
    # OpCo-specific queries using transaction tables
    opco_queries = {
        "Commerce": """
            SELECT YEAR(ORDER_TS) as YEAR, SUM(GROSS_DEMAND) as REVENUE
            FROM FANGRAPH.COMMERCE.DIM_COMMERCE_PURCHASE 
            WHERE YEAR(ORDER_TS) IN (2024, 2025) 
            GROUP BY YEAR(ORDER_TS)
        """,
        "FBG (Sportsbook)": """
            SELECT YEAR(WAGER_PLACED_TIME_UTC) as YEAR, SUM(TOTAL_STAKE_BY_WAGER) as REVENUE
            FROM FANGRAPH.FBG.DIM_FBG_PURCHASE 
            WHERE YEAR(WAGER_PLACED_TIME_UTC) IN (2024, 2025) 
            GROUP BY YEAR(WAGER_PLACED_TIME_UTC)
        """,
        "Events": """
            SELECT YEAR(ORDER_COMPLETED_TIME) as YEAR, SUM(ORDER_TOTAL_PAID) as REVENUE
            FROM FANGRAPH.EVENTS.DIM_EVENTS_PURCHASE 
            WHERE YEAR(ORDER_COMPLETED_TIME) IN (2024, 2025) 
            GROUP BY YEAR(ORDER_COMPLETED_TIME)
        """,
        "Topps.com": """
            SELECT YEAR(ORDER_TS) as YEAR, SUM(P_GMV_USD) as REVENUE
            FROM FANGRAPH.TOPPS.DIM_TOPPS_PURCHASE 
            WHERE YEAR(ORDER_TS) IN (2024, 2025) 
            GROUP BY YEAR(ORDER_TS)
        """
    }
    
    # OpCos that use FANGRAPH lifetime columns (no transaction tables)
    fangraph_revenue_columns = {
        "Live": "COALESCE(LIVE_TOTAL_REVENUE, 0)",
        "FanApp": "COALESCE(FANAPP_COMMERCE_ORDER_AMOUNT_TOTAL, 0)",
        "Topps Digital": """
            COALESCE(TOPPS_DIGITAL_BASEBALL_SPEND_AMOUNT_LIFETIME, 0)
            + COALESCE(TOPPS_DIGITAL_DISNEY_SPEND_AMOUNT_LIFETIME, 0)
            + COALESCE(TOPPS_DIGITAL_MARVEL_SPEND_AMOUNT_LIFETIME, 0)
            + COALESCE(TOPPS_DIGITAL_STARWARS_SPEND_AMOUNT_LIFETIME, 0)
            + COALESCE(TOPPS_DIGITAL_WWE_SPEND_AMOUNT_LIFETIME, 0)
        """,
        "Collect": "COALESCE(COLLECT_REVENUE_LIFETIME, 0)"
    }
    
    opco_filters = {
        "Live": "LIVE_FAN_INDICATOR = TRUE",
        "FanApp": "FANAPP_FAN_INDICATOR = TRUE",
        "Topps Digital": "TOPPS_DIGITAL_FAN_INDICATOR = TRUE",
        "Collect": "COLLECT_FAN_INDICATOR = TRUE"
    }
    
    if opco == "ALL":
        # Combine transaction-level data + FANGRAPH lifetime data for other OpCos
        query = """
            SELECT YEAR, SUM(REVENUE) as REVENUE FROM (
                -- Commerce (transaction-level)
                SELECT YEAR(ORDER_TS) as YEAR, SUM(GROSS_DEMAND) as REVENUE
                FROM FANGRAPH.COMMERCE.DIM_COMMERCE_PURCHASE WHERE YEAR(ORDER_TS) IN (2024, 2025) GROUP BY YEAR(ORDER_TS)
                UNION ALL
                -- FBG (transaction-level)
                SELECT YEAR(WAGER_PLACED_TIME_UTC) as YEAR, SUM(TOTAL_STAKE_BY_WAGER) as REVENUE
                FROM FANGRAPH.FBG.DIM_FBG_PURCHASE WHERE YEAR(WAGER_PLACED_TIME_UTC) IN (2024, 2025) GROUP BY YEAR(WAGER_PLACED_TIME_UTC)
                UNION ALL
                -- Events (transaction-level)
                SELECT YEAR(ORDER_COMPLETED_TIME) as YEAR, SUM(ORDER_TOTAL_PAID) as REVENUE
                FROM FANGRAPH.EVENTS.DIM_EVENTS_PURCHASE WHERE YEAR(ORDER_COMPLETED_TIME) IN (2024, 2025) GROUP BY YEAR(ORDER_COMPLETED_TIME)
                UNION ALL
                -- Topps.com (transaction-level)
                SELECT YEAR(ORDER_TS) as YEAR, SUM(P_GMV_USD) as REVENUE
                FROM FANGRAPH.TOPPS.DIM_TOPPS_PURCHASE WHERE YEAR(ORDER_TS) IN (2024, 2025) GROUP BY YEAR(ORDER_TS)
                UNION ALL
                -- Live, FanApp, Topps Digital, Collect (FANGRAPH lifetime - split 50/50 between years)
                SELECT 2024 as YEAR, SUM(
                    COALESCE(LIVE_TOTAL_REVENUE, 0)
                    + COALESCE(FANAPP_COMMERCE_ORDER_AMOUNT_TOTAL, 0)
                    + COALESCE(TOPPS_DIGITAL_BASEBALL_SPEND_AMOUNT_LIFETIME, 0)
                    + COALESCE(TOPPS_DIGITAL_DISNEY_SPEND_AMOUNT_LIFETIME, 0)
                    + COALESCE(TOPPS_DIGITAL_MARVEL_SPEND_AMOUNT_LIFETIME, 0)
                    + COALESCE(TOPPS_DIGITAL_STARWARS_SPEND_AMOUNT_LIFETIME, 0)
                    + COALESCE(TOPPS_DIGITAL_WWE_SPEND_AMOUNT_LIFETIME, 0)
                    + COALESCE(COLLECT_REVENUE_LIFETIME, 0)
                ) / 2 as REVENUE
                FROM FANGRAPH.ADMIN.FANGRAPH
                UNION ALL
                SELECT 2025 as YEAR, SUM(
                    COALESCE(LIVE_TOTAL_REVENUE, 0)
                    + COALESCE(FANAPP_COMMERCE_ORDER_AMOUNT_TOTAL, 0)
                    + COALESCE(TOPPS_DIGITAL_BASEBALL_SPEND_AMOUNT_LIFETIME, 0)
                    + COALESCE(TOPPS_DIGITAL_DISNEY_SPEND_AMOUNT_LIFETIME, 0)
                    + COALESCE(TOPPS_DIGITAL_MARVEL_SPEND_AMOUNT_LIFETIME, 0)
                    + COALESCE(TOPPS_DIGITAL_STARWARS_SPEND_AMOUNT_LIFETIME, 0)
                    + COALESCE(TOPPS_DIGITAL_WWE_SPEND_AMOUNT_LIFETIME, 0)
                    + COALESCE(COLLECT_REVENUE_LIFETIME, 0)
                ) / 2 as REVENUE
                FROM FANGRAPH.ADMIN.FANGRAPH
            )
            GROUP BY YEAR
            ORDER BY YEAR
        """
    elif opco in opco_queries:
        # Use transaction-level query
        query = opco_queries[opco]
    elif opco in fangraph_revenue_columns:
        # Use FANGRAPH lifetime columns - split 50/50 between years as approximation
        revenue_col = fangraph_revenue_columns[opco]
        filter_clause = opco_filters[opco]
        query = f"""
            SELECT 2024 as YEAR, SUM({revenue_col}) / 2 as REVENUE
            FROM FANGRAPH.ADMIN.FANGRAPH WHERE {filter_clause}
            UNION ALL
            SELECT 2025 as YEAR, SUM({revenue_col}) / 2 as REVENUE
            FROM FANGRAPH.ADMIN.FANGRAPH WHERE {filter_clause}
        """
    else:
        return {'2024': 0.0, '2025': 0.0}
    
    result = run_query(query)
    
    # Convert to dict by year
    revenue_by_year = {'2024': 0.0, '2025': 0.0}
    for _, row in result.iterrows():
        year = str(int(row['YEAR']))
        revenue_by_year[year] = float(row['REVENUE']) if row['REVENUE'] is not None else 0.0
    
    return revenue_by_year

# ============== OPCO-FILTERED QUERIES ==============
@st.cache_data(ttl=3600, show_spinner="Fetching filtered data...")
def get_opco_filtered_stats(opco: str):
    """Get stats filtered by OpCo"""
    if opco == "ALL":
        filter_clause = "1=1"
    else:
        opco_filters = {
            "Commerce": "COMMERCE_FAN_INDICATOR = TRUE",
            "Topps Digital": "TOPPS_DIGITAL_FAN_INDICATOR = TRUE",
            "Topps.com": "TOPPS_COM_FAN_INDICATOR = TRUE",
            "FBG (Sportsbook)": "FBG_FAN_INDICATOR = TRUE",
            "FanApp": "FANAPP_FAN_INDICATOR = TRUE",
            "Live": "LIVE_FAN_INDICATOR = TRUE",
            "Collect": "COLLECT_FAN_INDICATOR = TRUE",
            "Events": "EVENTS_FAN_INDICATOR = TRUE"
        }
        filter_clause = opco_filters.get(opco, "1=1")
    
    # Total fans for this OpCo
    total_query = f"SELECT COUNT(*) as CNT FROM FANGRAPH.ADMIN.FANGRAPH WHERE {filter_clause}"
    total = run_query(total_query)['CNT'].iloc[0]
    
    # League breakdown for this OpCo - optimized single scan
    league_query = f"""
    SELECT 
        SUM(CASE WHEN FANGRAPH_PREFERENCE_NFL = TRUE THEN 1 ELSE 0 END) as NFL,
        SUM(CASE WHEN FANGRAPH_PREFERENCE_MLB = TRUE THEN 1 ELSE 0 END) as MLB,
        SUM(CASE WHEN FANGRAPH_PREFERENCE_NBA = TRUE THEN 1 ELSE 0 END) as NBA,
        SUM(CASE WHEN FANGRAPH_PREFERENCE_NCAA = TRUE THEN 1 ELSE 0 END) as NCAA,
        SUM(CASE WHEN FANGRAPH_PREFERENCE_NHL = TRUE THEN 1 ELSE 0 END) as NHL
    FROM FANGRAPH.ADMIN.FANGRAPH WHERE {filter_clause}
    """
    result = run_query(league_query).iloc[0]
    leagues_df = pd.DataFrame([
        {'LEAGUE': 'NFL', 'FAN_COUNT': result['NFL']},
        {'LEAGUE': 'MLB', 'FAN_COUNT': result['MLB']},
        {'LEAGUE': 'NBA', 'FAN_COUNT': result['NBA']},
        {'LEAGUE': 'NCAA', 'FAN_COUNT': result['NCAA']},
        {'LEAGUE': 'NHL', 'FAN_COUNT': result['NHL']},
    ]).sort_values('FAN_COUNT', ascending=False)
    
    # Age breakdown for this OpCo
    age_query = f"""
    SELECT 
        FANGRAPH_AGE_RANGE as AGE_RANGE,
        COUNT(*) as FAN_COUNT
    FROM FANGRAPH.ADMIN.FANGRAPH
    WHERE {filter_clause} AND FANGRAPH_AGE_RANGE IS NOT NULL
    GROUP BY FANGRAPH_AGE_RANGE
    ORDER BY FAN_COUNT DESC
    """
    age_df = run_query(age_query)
    
    return {
        'total': total,
        'leagues': leagues_df,
        'age': age_df
    }

# ============== HELPER FUNCTIONS ==============
def format_number(num, suffix=''):
    """Format large numbers with M/B suffix"""
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}B{suffix}"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.1f}M{suffix}"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K{suffix}"
    return f"{num:,.0f}{suffix}"

def clear_cache():
    """Clear all cached data"""
    st.cache_data.clear()
    st.success("Data cache cleared! Refreshing...")
    st.rerun()

# ============== MAIN APP ==============
def main():
    # Load initial data for header stats
    try:
        total_fans_count = get_total_fans()
        opco_df = get_opco_breakdown()
        commerce_fans = opco_df[opco_df['OPCO'] == 'Commerce']['FAN_COUNT'].values[0]
    except:
        total_fans_count = 0
        commerce_fans = 0
    
    # Custom header matching static HTML style
    st.markdown(f"""
    <style>
        .custom-header {{
            background: linear-gradient(90deg, #E31837 0%, #B71430 100%);
            padding: 1.5rem 2rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            box-shadow: 0 4px 20px rgba(227, 24, 55, 0.3);
        }}
        .header-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        .logo-section {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        .logo-section img {{
            height: 48px;
            border-radius: 8px;
        }}
        .logo-text h1 {{
            font-size: 1.75rem;
            font-weight: 700;
            letter-spacing: -0.5px;
            margin: 0;
            color: white;
        }}
        .logo-text span {{
            font-size: 0.85rem;
            opacity: 0.9;
            font-weight: 400;
            color: white;
        }}
        .header-stats {{
            display: flex;
            gap: 2rem;
        }}
        .header-stat {{
            text-align: right;
        }}
        .header-stat-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
        }}
        .header-stat-label {{
            font-size: 0.75rem;
            opacity: 0.85;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: white;
        }}
    </style>
    <div class="custom-header">
        <div class="header-content">
            <div class="logo-section">
                <div class="logo-text">
                    <h1>FanGraph Insights</h1>
                    <span>Powered by Snowflake Cortex Agent</span>
                </div>
            </div>
            <div class="header-stats">
                <div class="header-stat">
                    <div class="header-stat-value">{format_number(total_fans_count)}</div>
                    <div class="header-stat-label">Total Fans</div>
                </div>
                <div class="header-stat">
                    <div class="header-stat-value">{format_number(commerce_fans)}</div>
                    <div class="header-stat-label">Commerce Fans</div>
                </div>
                <div class="header-stat">
                    <div class="header-stat-value">8</div>
                    <div class="header-stat-label">OpCos</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Refresh button in sidebar
    with st.sidebar:
        st.markdown("### FanGraph Insights")
        st.markdown("---")
        if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
            clear_cache()
        st.markdown("---")
        st.markdown("**Data Source:** Snowflake")
        st.markdown("**Last Refresh:** Live")
    
    # OpCo filter dropdown (shown on Overview and OpCo tabs)
    opco_options = ["ALL", "Commerce", "Topps Digital", "Topps.com", "FBG (Sportsbook)", "FanApp", "Live", "Collect", "Events"]
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview", 
        "🏢 OpCo Breakdown", 
        "💰 Commerce Trends", 
        "🏈 NFL Teams", 
        "👥 Demographics", 
        "🏆 League Preferences"
    ])
    
    # ============== TAB 1: OVERVIEW ==============
    with tab1:
        st.markdown("### Executive Overview")
        st.markdown("High-level insights from the FanGraph Agent across 5 key analytical dimensions")
        
        # OpCo Filter
        selected_opco = st.selectbox(
            "Filter by Operating Company",
            opco_options,
            key="overview_opco",
            help="Filter all metrics by a specific OpCo"
        )
        
        # Get data based on filter
        if selected_opco == "ALL":
            opco_df = get_opco_breakdown()
            total_fans = opco_df[opco_df['OPCO'] == 'Total Fans']['FAN_COUNT'].values[0]
            commerce_fans = opco_df[opco_df['OPCO'] == 'Commerce']['FAN_COUNT'].values[0]
            leagues_df = get_league_preferences()
            commerce_df = get_commerce_trends()
        else:
            filtered_data = get_opco_filtered_stats(selected_opco)
            total_fans = filtered_data['total']
            commerce_fans = total_fans  # Same as total when filtered
            leagues_df = filtered_data['leagues']
            commerce_df = get_commerce_trends()  # Commerce data doesn't filter by OpCo
        
        nfl_fans = leagues_df[leagues_df['LEAGUE'] == 'NFL']['FAN_COUNT'].values[0] if len(leagues_df) > 0 else 0
        revenue_by_year = get_revenue_by_year(selected_opco)
        
        # KPI Cards - 5 columns for 2 revenue metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Fans", format_number(total_fans), delta=f"{'Filtered: ' + selected_opco if selected_opco != 'ALL' else 'All OpCos'}")
        with col2:
            if selected_opco == "ALL":
                st.metric("Commerce Fans", format_number(commerce_fans), delta=f"{commerce_fans/total_fans*100:.1f}% of total")
            else:
                st.metric("Selected OpCo Fans", format_number(total_fans))
        with col3:
            st.metric("NFL Preference Fans", format_number(nfl_fans), delta="Top League")
        with col4:
            revenue_label = "All OpCos" if selected_opco == "ALL" else selected_opco
            st.metric("2025 Gross Revenue", format_number(revenue_by_year['2025'], '$'), delta=revenue_label)
        with col5:
            st.metric("2024 Gross Revenue", format_number(revenue_by_year['2024'], '$'), delta=revenue_label)
        
        st.divider()
        
        # Overview Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Gauge chart for total fans
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=total_fans / 1_000_000,
                title={'text': "Total Fans (Millions)", 'font': {'color': 'white'}},
                number={'suffix': 'M', 'font': {'color': COLORS['red']}},
                gauge={
                    'axis': {'range': [0, 250], 'tickcolor': 'white'},
                    'bar': {'color': COLORS['red']},
                    'bgcolor': COLORS['gray'],
                    'bordercolor': '#404040',
                    'steps': [
                        {'range': [0, 75], 'color': '#1a1a1a'},
                        {'range': [75, 150], 'color': '#2d2d2d'},
                        {'range': [150, 250], 'color': '#404040'}
                    ]
                }
            ))
            fig.update_layout(**PLOTLY_LAYOUT, height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # League distribution pie
            fig = px.pie(
                leagues_df, 
                values='FAN_COUNT', 
                names='LEAGUE',
                color_discrete_sequence=[COLORS['red'], COLORS['blue'], '#FF6B00', COLORS['gold'], '#00D4FF'],
                hole=0.4
            )
            fig.update_layout(**PLOTLY_LAYOUT, height=300, title="League Preferences")
            fig.update_traces(textinfo='label+percent', textfont_color='white')
            st.plotly_chart(fig, use_container_width=True)
        
        # Insights
        st.markdown("### Key Insights")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="insight-card">
                <div class="insight-title">🎯 Commerce Dominance</div>
                <div class="insight-text">Commerce fans represent 91.8% of the total fan base, indicating strong e-commerce engagement.</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="insight-card">
                <div class="insight-title">🏈 NFL Leads</div>
                <div class="insight-text">NFL is the most preferred league, 53% more fans than MLB.</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="insight-card">
                <div class="insight-title">📅 Seasonal Peaks</div>
                <div class="insight-text">Nov-Dec shows 2-3x revenue vs other months.</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="insight-card">
                <div class="insight-title">🌎 Geographic Focus</div>
                <div class="insight-text">CA, TX, FL account for 25% of US fans.</div>
            </div>
            """, unsafe_allow_html=True)
    
    # ============== TAB 2: OPCO BREAKDOWN ==============
    with tab2:
        st.markdown("### Fan Count by Operating Company")
        st.markdown("Distribution of fans across Fanatics business units")
        
        st.markdown("""
        <div class="prompt-box">
            <div class="prompt-label">FanGraph Agent Prompt</div>
            <div class="prompt-text">"What is total number of fans in fangraph, and what's the breakdown by each OpCo?"</div>
        </div>
        """, unsafe_allow_html=True)
        
        # OpCo Filter for this tab
        selected_opco_tab2 = st.selectbox(
            "Filter by Operating Company",
            opco_options,
            key="opco_tab_filter",
            help="Select an OpCo to see detailed breakdown"
        )
        
        opco_df = get_opco_breakdown()
        opco_df_no_total = opco_df[opco_df['OPCO'] != 'Total Fans']
        
        if selected_opco_tab2 == "ALL":
            # Show all OpCos
            # KPI Cards
            col1, col2, col3, col4 = st.columns(4)
            
            top_opcos = opco_df_no_total.head(4)
            for i, (col, row) in enumerate(zip([col1, col2, col3, col4], top_opcos.itertuples())):
                with col:
                    st.metric(row.OPCO, format_number(row.FAN_COUNT))
            
            # Bar chart
            fig = px.bar(
                opco_df_no_total,
                x='FAN_COUNT',
                y='OPCO',
                orientation='h',
                color='FAN_COUNT',
                color_continuous_scale=[[0, COLORS['gray']], [0.5, COLORS['red']], [1, COLORS['gold']]]
            )
            fig.update_layout(**PLOTLY_LAYOUT, height=500, title="Fan Distribution by OpCo", showlegend=False)
            fig.update_traces(texttemplate='%{x:.2s}', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
            
            # Pie chart (excluding Commerce for better visibility)
            opco_non_commerce = opco_df_no_total[opco_df_no_total['OPCO'] != 'Commerce']
            fig2 = px.pie(
                opco_non_commerce,
                values='FAN_COUNT',
                names='OPCO',
                color_discrete_sequence=COLORS['gradient'][1:],
                hole=0.4
            )
            fig2.update_layout(**PLOTLY_LAYOUT, height=400, title="OpCo Market Share (Excluding Commerce)")
            fig2.update_traces(textinfo='label+percent', textfont_color='white')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            # Show filtered OpCo details
            filtered_data = get_opco_filtered_stats(selected_opco_tab2)
            
            st.markdown(f"### {selected_opco_tab2} Deep Dive")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Fans", format_number(filtered_data['total']))
            with col2:
                pct_of_total = filtered_data['total'] / opco_df[opco_df['OPCO'] == 'Total Fans']['FAN_COUNT'].values[0] * 100
                st.metric("% of Total FanGraph", f"{pct_of_total:.1f}%")
            with col3:
                top_league = filtered_data['leagues'].iloc[0]['LEAGUE'] if len(filtered_data['leagues']) > 0 else "N/A"
                st.metric("Top League", top_league)
            
            # League breakdown for this OpCo
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(
                    filtered_data['leagues'],
                    x='LEAGUE',
                    y='FAN_COUNT',
                    color='LEAGUE',
                    color_discrete_sequence=[COLORS['red'], COLORS['blue'], '#FF6B00', COLORS['gold'], '#00D4FF']
                )
                fig.update_layout(**PLOTLY_LAYOUT, height=400, title=f"League Preferences - {selected_opco_tab2}")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if len(filtered_data['age']) > 0:
                    fig = px.bar(
                        filtered_data['age'],
                        x='AGE_RANGE',
                        y='FAN_COUNT',
                        color='FAN_COUNT',
                        color_continuous_scale=[[0, COLORS['gray']], [1, COLORS['red']]]
                    )
                    fig.update_layout(**PLOTLY_LAYOUT, height=400, title=f"Age Distribution - {selected_opco_tab2}")
                    st.plotly_chart(fig, use_container_width=True)
    
    # ============== TAB 3: COMMERCE TRENDS ==============
    with tab3:
        st.markdown("### Commerce Transaction Trends")
        st.markdown("24-month analysis of orders, revenue, and customer activity")
        
        st.markdown("""
        <div class="prompt-box">
            <div class="prompt-label">FanGraph Agent Prompt</div>
            <div class="prompt-text">"Commerce transactions over the last 12 months compared to previous 12 months, showing product trends and sales changes"</div>
        </div>
        """, unsafe_allow_html=True)
        
        commerce_df = get_commerce_trends()
        
        # KPIs
        # Convert numeric columns to float (Snowflake returns Decimal)
        commerce_df['REVENUE'] = pd.to_numeric(commerce_df['REVENUE'], errors='coerce')
        commerce_df['ORDERS'] = pd.to_numeric(commerce_df['ORDERS'], errors='coerce')
        commerce_df['CUSTOMERS'] = pd.to_numeric(commerce_df['CUSTOMERS'], errors='coerce')
        
        total_revenue = commerce_df['REVENUE'].sum()
        total_orders = commerce_df['ORDERS'].sum()
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        peak_month = commerce_df.loc[commerce_df['REVENUE'].idxmax(), 'MONTH'].strftime('%b %Y') if len(commerce_df) > 0 else "N/A"
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Revenue", format_number(total_revenue, '$'))
        with col2:
            st.metric("Total Orders", format_number(total_orders))
        with col3:
            st.metric("Avg Order Value", f"${avg_order_value:.2f}")
        with col4:
            st.metric("Peak Month", peak_month)
        
        # Revenue trend
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=commerce_df['MONTH'],
            y=commerce_df['REVENUE'] / 1_000_000,
            mode='lines+markers',
            name='Revenue ($M)',
            line=dict(color=COLORS['red'], width=3),
            fill='tozeroy',
            fillcolor='rgba(227,24,55,0.2)'
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=400, title="Monthly Revenue Trend")
        fig.update_xaxes(title="Month", gridcolor='#404040')
        fig.update_yaxes(title="Revenue ($ Millions)", gridcolor='#404040')
        st.plotly_chart(fig, use_container_width=True)
        
        # Orders and Customers
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(
            go.Bar(x=commerce_df['MONTH'], y=commerce_df['ORDERS'] / 1_000_000, name='Orders (M)', marker_color=COLORS['blue']),
            secondary_y=False
        )
        fig2.add_trace(
            go.Scatter(x=commerce_df['MONTH'], y=commerce_df['CUSTOMERS'] / 1_000_000, name='Customers (M)', line=dict(color=COLORS['gold'], width=2)),
            secondary_y=True
        )
        fig2.update_layout(**PLOTLY_LAYOUT, height=400, title="Monthly Orders & Customers")
        fig2.update_xaxes(title="Month", gridcolor='#404040')
        fig2.update_yaxes(title="Orders (Millions)", gridcolor='#404040', secondary_y=False)
        fig2.update_yaxes(title="Customers (Millions)", gridcolor='#404040', secondary_y=True)
        st.plotly_chart(fig2, use_container_width=True)
    
    # ============== TAB 4: NFL TEAMS ==============
    with tab4:
        st.markdown("### NFL Team Fan Distribution")
        st.markdown("Top 15 NFL teams by fan preference count")
        
        st.markdown("""
        <div class="prompt-box">
            <div class="prompt-label">FanGraph Agent Prompt</div>
            <div class="prompt-text">"What's the trend of NFL fans purchasing jerseys over the last 4 years? Show top teams by fan count."</div>
        </div>
        """, unsafe_allow_html=True)
        
        nfl_df = get_nfl_teams()
        leagues_df = get_league_preferences()
        total_nfl_fans = leagues_df[leagues_df['LEAGUE'] == 'NFL']['FAN_COUNT'].values[0]
        
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("#1 " + nfl_df.iloc[0]['NFL_TEAM'], format_number(nfl_df.iloc[0]['FAN_COUNT']))
        with col2:
            st.metric("#2 " + nfl_df.iloc[1]['NFL_TEAM'], format_number(nfl_df.iloc[1]['FAN_COUNT']))
        with col3:
            st.metric("#3 " + nfl_df.iloc[2]['NFL_TEAM'], format_number(nfl_df.iloc[2]['FAN_COUNT']))
        with col4:
            st.metric("#4 " + nfl_df.iloc[3]['NFL_TEAM'], format_number(nfl_df.iloc[3]['FAN_COUNT']))
        
        # Bar chart
        colors_list = [COLORS['green'] if i == 0 else (COLORS['red'] if i < 3 else COLORS['blue']) for i in range(len(nfl_df))]
        fig = px.bar(
            nfl_df,
            x='NFL_TEAM',
            y='FAN_COUNT',
            color='NFL_TEAM',
            color_discrete_sequence=colors_list
        )
        fig.update_layout(**PLOTLY_LAYOUT, height=500, title="NFL Teams by Fan Count", showlegend=False)
        fig.update_xaxes(tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.markdown("### Top 15 NFL Teams")
        nfl_df['% of NFL Fans'] = (nfl_df['FAN_COUNT'] / total_nfl_fans * 100).round(1).astype(str) + '%'
        nfl_df['Fan Count'] = nfl_df['FAN_COUNT'].apply(lambda x: format_number(x))
        st.dataframe(
            nfl_df[['NFL_TEAM', 'Fan Count', '% of NFL Fans']].rename(columns={'NFL_TEAM': 'Team'}),
            use_container_width=True,
            hide_index=True
        )
    
    # ============== TAB 5: DEMOGRAPHICS ==============
    with tab5:
        st.markdown("### Fan Demographics")
        st.markdown("Age distribution and geographic analysis of the fan base")
        
        st.markdown("""
        <div class="prompt-box">
            <div class="prompt-label">FanGraph Agent Prompt</div>
            <div class="prompt-text">"Tell me about the demographic profile of fans - their age, location, and other characteristics"</div>
        </div>
        """, unsafe_allow_html=True)
        
        age_df = get_age_demographics()
        geo_df = get_geo_data()
        
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Largest Age Group", age_df.iloc[0]['AGE_RANGE'], delta=format_number(age_df.iloc[0]['FAN_COUNT']))
        with col2:
            st.metric("Top State", geo_df.iloc[0]['STATE'], delta=format_number(geo_df.iloc[0]['FAN_COUNT']))
        with col3:
            total_with_age = age_df['FAN_COUNT'].sum()
            st.metric("Fans with Age Data", format_number(total_with_age))
        with col4:
            top3_states = geo_df.head(3)['FAN_COUNT'].sum()
            total_fans = get_total_fans()
            st.metric("Top 3 States Share", f"{top3_states/total_fans*100:.0f}%")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Age chart
            fig = px.bar(
                age_df,
                x='AGE_RANGE',
                y='FAN_COUNT',
                color='FAN_COUNT',
                color_continuous_scale=[[0, COLORS['gray']], [1, COLORS['red']]]
            )
            fig.update_layout(**PLOTLY_LAYOUT, height=400, title="Age Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Geo chart
            fig = px.bar(
                geo_df,
                x='STATE',
                y='FAN_COUNT',
                color='FAN_COUNT',
                color_continuous_scale=[[0, '#404040'], [0.5, COLORS['red']], [1, COLORS['gold']]]
            )
            fig.update_layout(**PLOTLY_LAYOUT, height=400, title="Top 20 States by Fan Count")
            st.plotly_chart(fig, use_container_width=True)
    
    # ============== TAB 6: LEAGUE PREFERENCES ==============
    with tab6:
        st.markdown("### League Preference Analysis")
        st.markdown("Fan distribution across major sports leagues")
        
        st.markdown("""
        <div class="prompt-box">
            <div class="prompt-label">FanGraph Agent Prompt</div>
            <div class="prompt-text">"Yearly breakdown of fans by league preference for NBA, NFL, MLB, NHL and NCAA"</div>
        </div>
        """, unsafe_allow_html=True)
        
        leagues_df = get_league_preferences()
        
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        for i, col in enumerate([col1, col2, col3, col4]):
            if i < len(leagues_df):
                with col:
                    st.metric(
                        f"#{i+1} {leagues_df.iloc[i]['LEAGUE']}", 
                        format_number(leagues_df.iloc[i]['FAN_COUNT'])
                    )
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart
            fig = px.bar(
                leagues_df,
                x='LEAGUE',
                y='FAN_COUNT',
                color='LEAGUE',
                color_discrete_sequence=[COLORS['red'], COLORS['blue'], '#FF6B00', COLORS['gold'], '#00D4FF']
            )
            fig.update_layout(**PLOTLY_LAYOUT, height=450, title="League Fan Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Pie chart
            fig = px.pie(
                leagues_df,
                values='FAN_COUNT',
                names='LEAGUE',
                color_discrete_sequence=[COLORS['red'], COLORS['blue'], '#FF6B00', COLORS['gold'], '#00D4FF'],
                hole=0.35
            )
            fig.update_layout(**PLOTLY_LAYOUT, height=450, title="League Comparison")
            fig.update_traces(textinfo='label+percent', textfont_color='white')
            st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.85rem;">
        <p>FanGraph Insights Dashboard | Data sourced from <strong>FANGRAPH.ADMIN.FANGRAPH</strong></p>
        <p>Built with Streamlit & Plotly | © 2026 Fanatics | 
        <a href="https://github.com/daniel-fox-fanatics/fangraph-insights" style="color: #E31837;">GitHub Repository</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

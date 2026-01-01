"""
NYC 311 Operations Dashboard - Main App
"""
import streamlit as st
import subprocess
import sys
import os
import pandas as pd
import base64
from sqlalchemy import text

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.db import get_engine
from src.config import get_database_url

st.set_page_config(
    page_title="NYC 311 Operations Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional dashboard look
st.markdown("""
<style>
    /* Professional color palette */
    :root {
        --primary-blue: #2563eb;
        --primary-dark: #1e40af;
        --accent-blue: #3b82f6;
        --success-green: #10b981;
        --warning-orange: #f59e0b;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --bg-light: #f9fafb;
        --bg-card: #ffffff;
        --border-color: #e5e7eb;
    }
    
    .header-container {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .logo-container {
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .logo-svg {
        width: 90px;
        height: 90px;
        filter: drop-shadow(0 2px 6px rgba(37, 99, 235, 0.2));
    }
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        color: var(--primary-dark);
        margin: 0;
        letter-spacing: -0.02em;
        flex: 1;
    }
    .sub-header {
        font-size: 1.3rem;
        color: var(--text-secondary);
        margin-bottom: 2rem;
        font-weight: 400;
    }
    .info-box {
        background-color: var(--bg-card);
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid var(--primary-blue);
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        border: 1px solid var(--border-color);
    }
    .info-box h3 {
        color: var(--primary-dark);
        margin-top: 0;
        font-size: 1.2rem;
    }
    .info-box h4 {
        color: var(--primary-dark);
        margin-top: 0;
        font-size: 1.1rem;
    }
    .stMetric {
        background-color: var(--bg-card);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    /* Main container background */
    .main .block-container {
        padding-top: 2rem;
    }
    /* Section headers */
    h2 {
        color: var(--primary-dark);
        font-weight: 600;
        border-bottom: 2px solid var(--border-color);
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    h3 {
        color: var(--text-primary);
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section - Logo and Title
# Create SVG logo as base64 encoded image
svg_logo = """
<svg width="90" height="90" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#2563eb;stop-opacity:0.15" />
            <stop offset="100%" style="stop-color:#1e40af;stop-opacity:0.25" />
        </linearGradient>
    </defs>
    <circle cx="50" cy="50" r="48" fill="url(#grad)"/>
    <g fill="#2563eb">
        <rect x="15" y="60" width="5" height="18" rx="0.8"/>
        <rect x="22" y="55" width="5" height="23" rx="0.8"/>
        <rect x="29" y="50" width="5" height="28" rx="0.8"/>
        <rect x="40" y="40" width="6" height="38" rx="1"/>
        <rect x="42" y="35" width="2" height="5" rx="0.5"/>
        <rect x="50" y="48" width="5" height="30" rx="0.8"/>
        <rect x="57" y="55" width="5" height="23" rx="0.8"/>
        <rect x="64" y="60" width="5" height="18" rx="0.8"/>
    </g>
    <g transform="translate(50, 30)">
        <path d="M -12 -6 L 0 -12 L 12 -6 L 12 6 L 0 12 L -12 6 Z" fill="#2563eb" stroke="#1e40af" stroke-width="1.2"/>
        <text x="0" y="2" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="white" text-anchor="middle">311</text>
    </g>
</svg>
"""

col_logo, col_title = st.columns([0.12, 0.88])
with col_logo:
    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: center; padding-top: 15px;">
        <img src="data:image/svg+xml;base64,{base64.b64encode(svg_logo.encode()).decode()}" width="85" height="85" style="filter: drop-shadow(0 2px 6px rgba(37, 99, 235, 0.2));"/>
    </div>
    """, unsafe_allow_html=True)

with col_title:
    st.markdown('<h1 class="main-header">NYC 311 Operations Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Comprehensive analytics and insights for NYC 311 service requests across all boroughs</p>', unsafe_allow_html=True)

# Sidebar controls
with st.sidebar:
    st.markdown("### Dashboard Controls")
    
    # Days selector
    days = st.radio(
        "Data Range Selection",
        options=[30, 60, 90],
        index=0,
        help="Select the number of days of historical data to fetch and analyze. This determines the time window for all metrics and visualizations."
    )
    
    st.divider()
    
    # Refresh Data button
    st.markdown("### Data Management")
    if st.button("Refresh Data", type="primary", use_container_width=True):
        with st.spinner("Refreshing data... This may take a few minutes."):
            try:
                # Step 1: Fetch data
                st.info("**Step 1/4:** Fetching data from NYC Open Data API...")
                result = subprocess.run(
                    [sys.executable, "scripts/fetch_311.py", "--days", str(days)],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd()
                )
                if result.returncode != 0:
                    st.error(f"Error fetching data: {result.stderr}")
                    st.stop()
                st.success("Data fetched successfully from API")
                
                # Step 2: Load to Postgres
                st.info("**Step 2/4:** Loading data into PostgreSQL database...")
                result = subprocess.run(
                    [sys.executable, "scripts/load_311_to_postgres.py"],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd(),
                    env=os.environ.copy()
                )
                if result.returncode != 0:
                    st.error(f"Error loading data: {result.stderr}")
                    st.stop()
                st.success("Data loaded into raw schema")
                
                # Step 3: Rebuild core table
                st.info("**Step 3/4:** Rebuilding cleaned core data table...")
                try:
                    database_url = get_database_url()
                except RuntimeError as e:
                    st.error(str(e))
                    st.stop()
                
                env = os.environ.copy()
                env['DATABASE_URL'] = database_url
                result = subprocess.run(
                    ["psql", database_url, "-f", "sql/schema/03_create_core_311.sql"],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd(),
                    env=env
                )
                if result.returncode != 0:
                    st.error(f"Error rebuilding core table: {result.stderr}")
                    if result.stdout:
                        st.text(result.stdout)
                    st.stop()
                st.success("Core table rebuilt with cleaned data")
                
                # Step 4: Build marts
                st.info("**Step 4/4:** Building analytics mart tables...")
                result = subprocess.run(
                    ["psql", database_url, "-f", "sql/marts/00_build_all_marts.sql"],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd(),
                    env=env
                )
                if result.returncode != 0:
                    st.error(f"Error building marts: {result.stderr}")
                    if result.stdout:
                        st.text(result.stdout)
                    st.stop()
                st.success("Analytics marts built successfully")
                
                st.success("**Data refresh complete!** Dashboard will reload automatically.")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error during refresh: {str(e)}")
    
    st.divider()
    st.markdown(f"**Current Data Range:** Last {days} days")
    st.caption("Select a different range and click Refresh to update")

# Store days in session state
st.session_state['days'] = days

# Main Content - Overview Section
st.markdown("## Dashboard Overview")
st.caption("Welcome to the NYC 311 Operations Dashboard - Your comprehensive analytics platform for service request insights")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div class="info-box">
        <h3>About This Dashboard</h3>
        <p>This comprehensive analytics dashboard provides real-time insights into NYC 311 service requests, 
        enabling data-driven decision-making for city operations and resource allocation.</p>
        <p><strong>Key Capabilities:</strong></p>
        <ul>
            <li><strong>KPI Metrics & Trends:</strong> Track total requests, resolution times, and performance indicators over time</li>
            <li><strong>Complaint Analysis:</strong> Identify top complaint types by borough and month</li>
            <li><strong>Agency Performance:</strong> Monitor agency efficiency and resolution metrics</li>
            <li><strong>Time-Series Analytics:</strong> Monthly aggregated data for trend analysis</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-box">
        <h3>Navigation Guide</h3>
        <p><strong>Use the sidebar menu to explore:</strong></p>
        <ul>
            <li><strong>Overview</strong><br>KPI metrics, trends, and performance indicators</li>
            <li><strong>Complaints</strong><br>Top complaints analysis by borough</li>
            <li><strong>Agency Performance</strong><br>Agency efficiency and metrics</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Try to load and display key metrics
try:
    engine = get_engine()
    query = text("""
        SELECT 
            SUM(total_requests) as total,
            SUM(open_requests) as open,
            SUM(closed_requests) as closed,
            AVG(median_resolution_hours) as avg_resolution,
            MIN(month) as first_month,
            MAX(month) as last_month
        FROM marts.kpi_monthly
    """)
    
    summary_df = pd.read_sql(query, engine)
    
    if not summary_df.empty and summary_df.iloc[0]['total'] is not None and pd.notna(summary_df.iloc[0]['total']):
        st.markdown("---")
        st.markdown("## Key Performance Indicators")
        if pd.notna(summary_df.iloc[0]['first_month']):
            st.caption(f"Data coverage: {summary_df.iloc[0]['first_month']} to {summary_df.iloc[0]['last_month']}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Service Requests",
                f"{summary_df.iloc[0]['total']:,.0f}",
                help="Total number of 311 service requests in the database"
            )
        
        with col2:
            st.metric(
                "Currently Open Requests",
                f"{summary_df.iloc[0]['open']:,.0f}",
                help="Number of requests that are still open and awaiting resolution"
            )
        
        with col3:
            st.metric(
                "Successfully Closed Requests",
                f"{summary_df.iloc[0]['closed']:,.0f}",
                help="Number of requests that have been successfully resolved and closed"
            )
        
        with col4:
            resolution = summary_df.iloc[0]['avg_resolution']
            st.metric(
                "Average Resolution Time",
                f"{resolution:.1f} hrs" if pd.notna(resolution) else "N/A",
                help="Average time taken to resolve requests, measured in hours"
            )
        
        # Quick visualization
        st.markdown("---")
        st.markdown("## Quick Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Request Status Distribution")
            try:
                import plotly.graph_objects as go
                open_val = summary_df.iloc[0]['open']
                closed_val = summary_df.iloc[0]['closed']
                fig = go.Figure(data=[go.Pie(
                    labels=['Open Requests', 'Closed Requests'],
                    values=[open_val, closed_val],
                    hole=0.4,
                    marker_colors=['#ff6b6b', '#51cf66'],
                    textinfo='label+percent+value',
                    texttemplate='%{label}<br>%{value:,.0f}<br>(%{percent})'
                )])
                fig.update_layout(
                    title="Breakdown of Request Status",
                    showlegend=True,
                    height=350,
                    font=dict(size=12)
                )
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.info("Chart unavailable")
        
        with col2:
            st.markdown("### Resolution Performance Summary")
            resolution = summary_df.iloc[0]['avg_resolution']
            closure_rate = (closed_val / (open_val + closed_val) * 100) if (open_val + closed_val) > 0 else 0
            
            st.info(f"""
            **Performance Metrics**
            
            **Average Resolution Time:** {resolution:.1f} hours (if available)
            
            **Closure Rate:** {closure_rate:.1f}% of requests have been successfully resolved
            
            **Open vs Closed:** {open_val:,.0f} open requests vs {closed_val:,.0f} closed requests
            
            This metric helps track how quickly NYC agencies respond to and resolve service requests across all boroughs.
            """)
    
except Exception as e:
    # Show helpful content even when no data
    st.markdown("---")
    st.markdown("## Getting Started")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h3>Load Your Data</h3>
            <p><strong>Step 1:</strong> Use the sidebar "Refresh Data" button to fetch and load NYC 311 data.</p>
            <p><strong>Step 2:</strong> Select the number of days (30, 60, or 90) you want to analyze.</p>
            <p><strong>Step 3:</strong> Wait for the data pipeline to complete (fetch → load → transform → analyze).</p>
            <p><strong>Step 4:</strong> Explore the dashboard pages to view insights!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-box">
        <h3>What You'll See</h3>
        <p>Once data is loaded, this dashboard will display:</p>
        <ul>
            <li>Real-time KPI metrics and trends</li>
            <li>Top complaints by borough</li>
            <li>Agency performance analytics</li>
            <li>Interactive visualizations</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### Quick Tips")
    st.markdown("""
    - **Start Small:** Begin with 30 days of data for faster loading
    - **Explore Pages:** Use the sidebar navigation to view different analytics
    - **Refresh Regularly:** Use the refresh button to get the latest data
    - **Filter & Analyze:** Use filters on each page to drill down into specific insights
    """)

st.markdown("---")
st.markdown("## Dashboard Features")

feature_col1, feature_col2, feature_col3 = st.columns(3)

with feature_col1:
    st.markdown("""
    <div class="info-box">
        <h4>Real-Time Analytics</h4>
        <p>Monitor KPIs, trends, and performance metrics with interactive visualizations updated in real-time.</p>
    </div>
    """, unsafe_allow_html=True)

with feature_col2:
    st.markdown("""
    <div class="info-box">
        <h4>Advanced Filtering</h4>
        <p>Filter by borough, month, agency, and complaint type to drill down into specific insights.</p>
    </div>
    """, unsafe_allow_html=True)

with feature_col3:
    st.markdown("""
    <div class="info-box">
        <h4>Trend Analysis</h4>
        <p>Track performance over time with monthly aggregations and time-series visualizations.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("### Data Sources & Methodology")
st.markdown("""
- **Data Source:** [NYC Open Data - 311 Service Requests](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9)
- **Update Frequency:** Manual refresh via sidebar controls
- **Data Pipeline:** Raw Data → Core (Cleaned) → Analytics Marts → Dashboard Visualizations
- **Technology Stack:** PostgreSQL, Python, Streamlit, Plotly
- **Last Updated:** Refresh data to see the most recent information
""")

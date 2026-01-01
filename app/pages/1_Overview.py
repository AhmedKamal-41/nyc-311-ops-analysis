"""
Overview Page - KPI Metrics and Trends
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.db import get_engine

st.set_page_config(page_title="Overview", layout="wide")
st.title("📊 Overview - KPI Metrics")

# Get days from session state (set in main app)
days = st.session_state.get('days', 30)

try:
    engine = get_engine()
    
    # Calculate date threshold
    threshold_date = (datetime.now() - timedelta(days=days)).date()
    
    # Load KPI monthly data
    query = """
    SELECT 
        month,
        total_requests,
        open_requests,
        closed_requests,
        median_resolution_hours,
        p90_resolution_hours
    FROM marts.kpi_monthly
    WHERE month >= %s
    ORDER BY month
    """
    
    df = pd.read_sql(query, engine, params=[threshold_date])
    
    if df.empty:
        st.warning("No data available. Please refresh data using the sidebar.")
        st.stop()
    
    # Display summary metrics
    st.subheader("Summary Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = df['total_requests'].sum()
        st.metric("Total Requests", f"{total:,.0f}")
    
    with col2:
        open_total = df['open_requests'].sum()
        st.metric("Open Requests", f"{open_total:,.0f}")
    
    with col3:
        closed_total = df['closed_requests'].sum()
        st.metric("Closed Requests", f"{closed_total:,.0f}")
    
    with col4:
        median_avg = df['median_resolution_hours'].median()
        st.metric("Avg Median Resolution", f"{median_avg:.1f} hrs" if pd.notna(median_avg) else "N/A")
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Requests Trend")
        try:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['month'],
                y=df['total_requests'],
                mode='lines+markers',
                name='Total Requests',
                line=dict(color='#1f77b4')
            ))
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Requests",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.plot(df['month'], df['total_requests'], marker='o')
            ax.set_xlabel('Month')
            ax.set_ylabel('Requests')
            ax.set_title('Requests Trend')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
    
    with col2:
        st.subheader("Median Resolution Hours Trend")
        try:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['month'],
                y=df['median_resolution_hours'],
                mode='lines+markers',
                name='Median Resolution Hours',
                line=dict(color='#ff7f0e')
            ))
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Hours",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.plot(df['month'], df['median_resolution_hours'], marker='o', color='orange')
            ax.set_xlabel('Month')
            ax.set_ylabel('Hours')
            ax.set_title('Median Resolution Hours Trend')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
    
    # Data table
    st.divider()
    st.subheader("Monthly KPI Data")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Make sure Postgres is running and data has been loaded.")


"""
Overview Page - KPI Metrics and Trends
"""
import streamlit as st
import pandas as pd
import sys
import os
from sqlalchemy import text

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.db import get_engine

st.set_page_config(page_title="Overview - KPI Metrics", layout="wide")
st.title("Overview - Key Performance Indicators")

st.markdown("""
This page provides comprehensive KPI metrics and trend analysis for NYC 311 service requests. 
Monitor request volumes, resolution times, and performance indicators over time.
""")

# Get days from session state (set in main app)
days = st.session_state.get('days', 30)

try:
    engine = get_engine()
    
    # Load KPI monthly data (show all available data)
    query = text("""
    SELECT 
        month,
        total_requests,
        open_requests,
        closed_requests,
        median_resolution_hours,
        p90_resolution_hours
    FROM marts.kpi_monthly
    ORDER BY month
    """)
    
    df = pd.read_sql(query, engine)
    
    if df.empty:
        st.warning("No data available. Please refresh data using the sidebar.")
        st.stop()
    
    # Display summary metrics
    st.markdown("---")
    st.markdown("## Summary Metrics (Aggregated)")
    st.caption(f"Data aggregated across all available months from {df['month'].min()} to {df['month'].max()}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = df['total_requests'].sum()
        st.metric(
            "Total Service Requests",
            f"{total:,.0f}",
            help="Total number of 311 service requests received in the selected time period"
        )
    
    with col2:
        open_total = df['open_requests'].sum()
        st.metric(
            "Open Requests (Unresolved)",
            f"{open_total:,.0f}",
            help="Total number of requests that are currently open and awaiting resolution"
        )
    
    with col3:
        closed_total = df['closed_requests'].sum()
        st.metric(
            "Closed Requests (Resolved)",
            f"{closed_total:,.0f}",
            help="Total number of requests that have been successfully resolved and closed"
        )
    
    with col4:
        median_avg = df['median_resolution_hours'].median()
        st.metric(
            "Median Resolution Time",
            f"{median_avg:.1f} hrs" if pd.notna(median_avg) else "N/A",
            help="Median time taken to resolve requests, measured in hours"
        )
    
    st.divider()
    
    # Main Charts Section
    st.markdown("## Trend Analysis")
    st.caption("Visual representation of key metrics over time")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Total Requests Trend Over Time")
        st.caption("Monthly volume of service requests received")
        try:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['month'],
                y=df['total_requests'],
                mode='lines+markers',
                name='Total Requests',
                line=dict(color='#2563eb', width=3),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor='rgba(37, 99, 235, 0.1)'
            ))
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Number of Requests",
                hovermode='x unified',
                height=400,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(df['month'], df['total_requests'], marker='o', linewidth=2, markersize=8)
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Number of Requests', fontsize=12)
            ax.set_title('Total Requests Trend Over Time', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
    
    with col2:
        st.markdown("### Median Resolution Time Trend")
        st.caption("Average time to resolve requests (in hours)")
        try:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['month'],
                y=df['median_resolution_hours'],
                mode='lines+markers',
                name='Median Resolution Hours',
                line=dict(color='#f59e0b', width=3),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor='rgba(245, 158, 11, 0.1)'
            ))
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Resolution Time (Hours)",
                hovermode='x unified',
                height=400,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(df['month'], df['median_resolution_hours'], marker='o', color='#f59e0b', linewidth=2, markersize=8)
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Resolution Time (Hours)', fontsize=12)
            ax.set_title('Median Resolution Time Trend', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
    
    # Additional visualizations
    st.divider()
    st.markdown("## Detailed Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Resolution Time Comparison")
        st.caption("Median vs 90th Percentile resolution times")
        try:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df['month'],
                y=df['median_resolution_hours'],
                name='Median Resolution Time',
                marker_color='#2563eb',
                text=df['median_resolution_hours'].round(1),
                textposition='outside'
            ))
            fig.add_trace(go.Bar(
                x=df['month'],
                y=df['p90_resolution_hours'],
                name='90th Percentile Resolution Time',
                marker_color='#f59e0b',
                text=df['p90_resolution_hours'].round(1),
                textposition='outside'
            ))
            fig.update_layout(
                barmode='group',
                xaxis_title="Month",
                yaxis_title="Resolution Time (Hours)",
                height=400,
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Chart data unavailable")
    
    with col2:
        st.markdown("### Request Status Over Time")
        st.caption("Open vs Closed requests comparison")
        try:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['month'],
                y=df['open_requests'],
                mode='lines+markers',
                name='Open Requests',
                line=dict(color='#ef4444', width=2),
                fill='tonexty',
                fillcolor='rgba(239, 68, 68, 0.15)'
            ))
            fig.add_trace(go.Scatter(
                x=df['month'],
                y=df['closed_requests'],
                mode='lines+markers',
                name='Closed Requests',
                line=dict(color='#10b981', width=2),
                fill='tozeroy',
                fillcolor='rgba(16, 185, 129, 0.15)'
            ))
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Number of Requests",
                height=400,
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Chart data unavailable")
    
    # Performance indicators
    st.markdown("---")
    st.markdown("## Performance Indicators")
    st.caption("Key metrics derived from the data")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        closure_rate = (df['closed_requests'].sum() / df['total_requests'].sum() * 100) if df['total_requests'].sum() > 0 else 0
        st.metric(
            "Request Closure Rate",
            f"{closure_rate:.1f}%",
            help="Percentage of total requests that have been successfully closed"
        )
    
    with col2:
        avg_monthly_requests = df['total_requests'].mean()
        st.metric(
            "Average Monthly Requests",
            f"{avg_monthly_requests:,.0f}",
            help="Average number of requests received per month"
        )
    
    with col3:
        best_resolution = df['median_resolution_hours'].min()
        st.metric(
            "Best Resolution Time",
            f"{best_resolution:.1f} hrs" if pd.notna(best_resolution) else "N/A",
            help="Best (lowest) median resolution time achieved"
        )
    
    with col4:
        worst_resolution = df['median_resolution_hours'].max()
        st.metric(
            "Peak Resolution Time",
            f"{worst_resolution:.1f} hrs" if pd.notna(worst_resolution) else "N/A",
            help="Highest median resolution time observed"
        )
    
    # Data table
    st.divider()
    st.markdown("## Monthly KPI Data Table")
    st.caption("Detailed monthly breakdown of all key performance indicators")
    st.dataframe(
        df.style.format({
            'total_requests': '{:,.0f}',
            'open_requests': '{:,.0f}',
            'closed_requests': '{:,.0f}',
            'median_resolution_hours': '{:.2f}',
            'p90_resolution_hours': '{:.2f}'
        }),
        use_container_width=True,
        hide_index=True
    )
    
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Make sure Postgres is running and data has been loaded. Use the sidebar to refresh data.")

"""
Complaints Page - Top Complaints by Borough
"""
import streamlit as st
import pandas as pd
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.db import get_engine

st.set_page_config(page_title="Complaints", layout="wide")
st.title("📋 Top Complaints by Borough")

try:
    engine = get_engine()
    
    # Load all complaints data
    query = """
    SELECT 
        month,
        borough,
        complaint_type,
        requests
    FROM marts.top_complaints_monthly
    ORDER BY month DESC, borough, requests DESC
    """
    
    df = pd.read_sql(query, engine)
    
    if df.empty:
        st.warning("No data available. Please refresh data using the sidebar.")
        st.stop()
    
    # Filters
    st.subheader("Filters")
    col1, col2 = st.columns(2)
    
    with col1:
        boroughs = ['All'] + sorted(df['borough'].dropna().unique().tolist())
        selected_borough = st.selectbox("Borough", boroughs)
    
    with col2:
        months = ['All'] + sorted(df['month'].unique(), reverse=True)
        selected_month = st.selectbox("Month", months)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_borough != 'All':
        filtered_df = filtered_df[filtered_df['borough'] == selected_borough]
    if selected_month != 'All':
        filtered_df = filtered_df[filtered_df['month'] == selected_month]
    
    if filtered_df.empty:
        st.info("No data matches the selected filters.")
        st.stop()
    
    # Display data
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Top Complaints")
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        st.subheader("Complaints Chart")
        # Prepare data for chart (top 10 if not filtered by month)
        chart_df = filtered_df.copy()
        if selected_month == 'All':
            # Aggregate by complaint_type if month is 'All'
            chart_df = chart_df.groupby('complaint_type')['requests'].sum().reset_index()
            chart_df = chart_df.sort_values('requests', ascending=False).head(10)
            x_col = 'complaint_type'
            y_col = 'requests'
        else:
            chart_df = chart_df.sort_values('requests', ascending=False).head(10)
            x_col = 'complaint_type'
            y_col = 'requests'
        
        try:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=chart_df[x_col],
                y=chart_df[y_col],
                marker_color='#2ca02c'
            ))
            fig.update_layout(
                xaxis_title="Complaint Type",
                yaxis_title="Requests",
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(chart_df[x_col], chart_df[y_col], color='green')
            ax.set_xlabel('Complaint Type')
            ax.set_ylabel('Requests')
            ax.set_title('Top Complaints')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig)
    
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Make sure Postgres is running and data has been loaded.")


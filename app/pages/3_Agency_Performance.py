"""
Agency Performance Page - Agency Metrics and Trends
"""
import streamlit as st
import pandas as pd
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.db import get_engine

st.set_page_config(page_title="Agency Performance", layout="wide")
st.title("🏛️ Agency Performance")

try:
    engine = get_engine()
    
    # Load all agency performance data
    query = """
    SELECT 
        month,
        agency,
        requests,
        median_resolution_hours,
        p90_resolution_hours
    FROM marts.agency_performance_monthly
    ORDER BY month DESC, agency
    """
    
    df = pd.read_sql(query, engine)
    
    if df.empty:
        st.warning("No data available. Please refresh data using the sidebar.")
        st.stop()
    
    # Filter
    st.subheader("Filter")
    agencies = ['All'] + sorted(df['agency'].dropna().unique().tolist())
    selected_agency = st.selectbox("Agency", agencies)
    
    # Apply filter
    filtered_df = df.copy()
    if selected_agency != 'All':
        filtered_df = filtered_df[filtered_df['agency'] == selected_agency]
    
    if filtered_df.empty:
        st.info("No data matches the selected filter.")
        st.stop()
    
    # Display data
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Performance Data")
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        st.subheader("Performance Trends")
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Requests Over Time', 'Resolution Hours Over Time'),
                vertical_spacing=0.15
            )
            
            # Requests chart
            fig.add_trace(
                go.Scatter(
                    x=filtered_df['month'],
                    y=filtered_df['requests'],
                    mode='lines+markers',
                    name='Requests',
                    line=dict(color='#1f77b4')
                ),
                row=1, col=1
            )
            
            # Resolution hours chart
            fig.add_trace(
                go.Scatter(
                    x=filtered_df['month'],
                    y=filtered_df['median_resolution_hours'],
                    mode='lines+markers',
                    name='Median Resolution Hours',
                    line=dict(color='#ff7f0e')
                ),
                row=2, col=1
            )
            
            fig.update_xaxes(title_text="Month", row=1, col=1)
            fig.update_xaxes(title_text="Month", row=2, col=1)
            fig.update_yaxes(title_text="Requests", row=1, col=1)
            fig.update_yaxes(title_text="Hours", row=2, col=1)
            fig.update_layout(height=600, hovermode='x unified', showlegend=False)
            
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            import matplotlib.pyplot as plt
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            # Requests
            ax1.plot(filtered_df['month'], filtered_df['requests'], marker='o', color='blue')
            ax1.set_xlabel('Month')
            ax1.set_ylabel('Requests')
            ax1.set_title('Requests Over Time')
            ax1.grid(True, alpha=0.3)
            
            # Resolution hours
            ax2.plot(filtered_df['month'], filtered_df['median_resolution_hours'], marker='o', color='orange')
            ax2.set_xlabel('Month')
            ax2.set_ylabel('Hours')
            ax2.set_title('Median Resolution Hours Over Time')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
    
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Make sure Postgres is running and data has been loaded.")


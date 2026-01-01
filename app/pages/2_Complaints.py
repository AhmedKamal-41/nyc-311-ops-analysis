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

st.set_page_config(page_title="Complaints Analysis", layout="wide")
st.title("📋 Complaints Analysis - Top Complaints by Borough")

st.markdown("""
Analyze the most common complaint types across NYC boroughs. Filter by borough and month to identify 
patterns and prioritize resource allocation.
""")

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
        st.warning("⚠️ No data available. Please refresh data using the sidebar.")
        st.stop()
    
    # Filters
    st.markdown("---")
    st.markdown("## 🔍 Filter Options")
    st.caption("Select specific borough and/or month to narrow down the analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        boroughs = ['All Boroughs'] + sorted(df['borough'].dropna().unique().tolist())
        selected_borough = st.selectbox(
            "Select Borough",
            boroughs,
            help="Filter complaints by specific borough or view all boroughs"
        )
    
    with col2:
        months = ['All Months'] + sorted(df['month'].unique(), reverse=True)
        selected_month = st.selectbox(
            "Select Month",
            months,
            help="Filter complaints by specific month or view all months"
        )
    
    # Apply filters
    filtered_df = df.copy()
    if selected_borough != 'All Boroughs':
        filtered_df = filtered_df[filtered_df['borough'] == selected_borough]
    if selected_month != 'All Months':
        filtered_df = filtered_df[filtered_df['month'] == selected_month]
    
    if filtered_df.empty:
        st.info("ℹ️ No data matches the selected filters. Try selecting different options.")
        st.stop()
    
    # Summary stats
    st.markdown("---")
    st.markdown("## 📊 Summary Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_complaints = filtered_df['requests'].sum()
        st.metric(
            "Total Complaints",
            f"{total_complaints:,.0f}",
            help="Total number of complaints matching the selected filters"
        )
    
    with col2:
        unique_types = filtered_df['complaint_type'].nunique()
        st.metric(
            "Unique Complaint Types",
            f"{unique_types}",
            help="Number of different complaint types in the filtered data"
        )
    
    with col3:
        avg_per_type = filtered_df.groupby('complaint_type')['requests'].sum().mean()
        st.metric(
            "Average per Type",
            f"{avg_per_type:,.0f}",
            help="Average number of requests per complaint type"
        )
    
    # Display data
    st.markdown("---")
    st.markdown("## 📋 Detailed Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📊 Top Complaints Data Table")
        st.caption("Ranked list of top complaint types with request counts")
        display_df = filtered_df.copy()
        if selected_month == 'All Months':
            # Aggregate if viewing all months
            display_df = display_df.groupby(['borough', 'complaint_type'])['requests'].sum().reset_index()
            display_df = display_df.sort_values('requests', ascending=False)
        else:
            display_df = display_df.sort_values('requests', ascending=False)
        
        st.dataframe(
            display_df.head(20).style.format({'requests': '{:,.0f}'}),
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        st.markdown("### 📈 Complaints Visualization")
        st.caption("Bar chart showing top complaint types by volume")
        # Prepare data for chart
        chart_df = filtered_df.copy()
        if selected_month == 'All Months':
            # Aggregate by complaint_type if month is 'All'
            chart_df = chart_df.groupby('complaint_type')['requests'].sum().reset_index()
            chart_df = chart_df.sort_values('requests', ascending=False).head(15)
            x_col = 'complaint_type'
            y_col = 'requests'
        else:
            chart_df = chart_df.sort_values('requests', ascending=False).head(15)
            x_col = 'complaint_type'
            y_col = 'requests'
        
        try:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=chart_df[y_col],
                y=chart_df[x_col],
                orientation='h',
                marker_color='#2ca02c',
                text=chart_df[y_col],
                textposition='outside',
                texttemplate='%{text:,.0f}'
            ))
            fig.update_layout(
                xaxis_title="Number of Requests",
                yaxis_title="Complaint Type",
                height=500,
                showlegend=False,
                yaxis={'categoryorder':'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.barh(chart_df[x_col], chart_df[y_col], color='green')
            ax.set_xlabel('Number of Requests', fontsize=12)
            ax.set_ylabel('Complaint Type', fontsize=12)
            ax.set_title('Top Complaints by Volume', fontsize=14, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig)
    
    # Borough comparison if viewing all boroughs
    if selected_borough == 'All Boroughs':
        st.markdown("---")
        st.markdown("## 🗺️ Borough Comparison")
        st.caption("Compare complaint volumes across different boroughs")
        
        borough_summary = filtered_df.groupby('borough')['requests'].sum().sort_values(ascending=False).reset_index()
        
        try:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=borough_summary['borough'],
                y=borough_summary['requests'],
                marker_color='#1f77b4',
                text=borough_summary['requests'],
                textposition='outside',
                texttemplate='%{text:,.0f}'
            ))
            fig.update_layout(
                xaxis_title="Borough",
                yaxis_title="Total Complaints",
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.dataframe(borough_summary, use_container_width=True, hide_index=True)
    
except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.info("💡 Make sure Postgres is running and data has been loaded.")

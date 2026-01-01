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
st.title("🏛️ Agency Performance Analysis")

st.markdown("""
Monitor and analyze the performance of NYC agencies handling 311 service requests. 
Track request volumes, resolution times, and efficiency metrics over time.
""")

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
        st.warning("⚠️ No data available. Please refresh data using the sidebar.")
        st.stop()
    
    # Filter
    st.markdown("---")
    st.markdown("## 🔍 Filter Options")
    st.caption("Select a specific agency to view detailed performance metrics")
    
    agencies = ['All Agencies'] + sorted(df['agency'].dropna().unique().tolist())
    selected_agency = st.selectbox(
        "Select Agency",
        agencies,
        help="Filter performance data by specific agency or view all agencies"
    )
    
    # Apply filter
    filtered_df = df.copy()
    if selected_agency != 'All Agencies':
        filtered_df = filtered_df[filtered_df['agency'] == selected_agency]
    
    if filtered_df.empty:
        st.info("ℹ️ No data matches the selected filter.")
        st.stop()
    
    # Summary metrics
    st.markdown("---")
    st.markdown("## 📊 Performance Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_requests = filtered_df['requests'].sum()
        st.metric(
            "Total Requests Handled",
            f"{total_requests:,.0f}",
            help="Total number of service requests handled by the selected agency/agencies"
        )
    
    with col2:
        avg_monthly = filtered_df['requests'].mean()
        st.metric(
            "Average Monthly Requests",
            f"{avg_monthly:,.0f}",
            help="Average number of requests handled per month"
        )
    
    with col3:
        avg_resolution = filtered_df['median_resolution_hours'].mean()
        st.metric(
            "Average Resolution Time",
            f"{avg_resolution:.1f} hrs" if pd.notna(avg_resolution) else "N/A",
            help="Average median resolution time across all months"
        )
    
    with col4:
        avg_p90 = filtered_df['p90_resolution_hours'].mean()
        st.metric(
            "Average 90th Percentile Time",
            f"{avg_p90:.1f} hrs" if pd.notna(avg_p90) else "N/A",
            help="Average 90th percentile resolution time"
        )
    
    # Display data
    st.markdown("---")
    st.markdown("## 📈 Performance Trends")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📋 Performance Data Table")
        st.caption("Detailed monthly performance metrics")
        display_df = filtered_df.copy()
        st.dataframe(
            display_df.style.format({
                'requests': '{:,.0f}',
                'median_resolution_hours': '{:.2f}',
                'p90_resolution_hours': '{:.2f}'
            }),
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        st.markdown("### 📊 Performance Trends Visualization")
        st.caption("Dual-axis chart showing request volume and resolution times")
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Request Volume Over Time', 'Resolution Time Performance'),
                vertical_spacing=0.15,
                row_heights=[0.5, 0.5]
            )
            
            # Requests chart
            fig.add_trace(
                go.Scatter(
                    x=filtered_df['month'],
                    y=filtered_df['requests'],
                    mode='lines+markers',
                    name='Request Volume',
                    line=dict(color='#1f77b4', width=3),
                    marker=dict(size=8),
                    fill='tozeroy',
                    fillcolor='rgba(31, 119, 180, 0.2)'
                ),
                row=1, col=1
            )
            
            # Resolution hours chart
            fig.add_trace(
                go.Scatter(
                    x=filtered_df['month'],
                    y=filtered_df['median_resolution_hours'],
                    mode='lines+markers',
                    name='Median Resolution',
                    line=dict(color='#ff7f0e', width=3),
                    marker=dict(size=8)
                ),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=filtered_df['month'],
                    y=filtered_df['p90_resolution_hours'],
                    mode='lines+markers',
                    name='90th Percentile',
                    line=dict(color='#d62728', width=2, dash='dash'),
                    marker=dict(size=6)
                ),
                row=2, col=1
            )
            
            fig.update_xaxes(title_text="Month", row=1, col=1)
            fig.update_xaxes(title_text="Month", row=2, col=1)
            fig.update_yaxes(title_text="Number of Requests", row=1, col=1)
            fig.update_yaxes(title_text="Resolution Time (Hours)", row=2, col=1)
            fig.update_layout(
                height=600,
                hovermode='x unified',
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            import matplotlib.pyplot as plt
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            # Requests
            ax1.plot(filtered_df['month'], filtered_df['requests'], marker='o', color='blue', linewidth=2, markersize=8)
            ax1.set_xlabel('Month', fontsize=12)
            ax1.set_ylabel('Number of Requests', fontsize=12)
            ax1.set_title('Request Volume Over Time', fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            
            # Resolution hours
            ax2.plot(filtered_df['month'], filtered_df['median_resolution_hours'], marker='o', color='orange', linewidth=2, markersize=8, label='Median')
            ax2.plot(filtered_df['month'], filtered_df['p90_resolution_hours'], marker='s', color='red', linewidth=2, markersize=6, linestyle='--', label='90th Percentile')
            ax2.set_xlabel('Month', fontsize=12)
            ax2.set_ylabel('Resolution Time (Hours)', fontsize=12)
            ax2.set_title('Resolution Time Performance', fontsize=14, fontweight='bold')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
    
    # Agency comparison if viewing all agencies
    if selected_agency == 'All Agencies':
        st.markdown("---")
        st.markdown("## 🏆 Agency Comparison")
        st.caption("Compare performance metrics across all agencies")
        
        agency_summary = df.groupby('agency').agg({
            'requests': 'sum',
            'median_resolution_hours': 'mean'
        }).sort_values('requests', ascending=False).head(15).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Top Agencies by Request Volume")
            try:
                import plotly.graph_objects as go
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=agency_summary['requests'],
                    y=agency_summary['agency'],
                    orientation='h',
                    marker_color='#1f77b4',
                    text=agency_summary['requests'],
                    textposition='outside',
                    texttemplate='%{text:,.0f}'
                ))
                fig.update_layout(
                    xaxis_title="Total Requests",
                    yaxis_title="Agency",
                    height=500,
                    showlegend=False,
                    yaxis={'categoryorder':'total ascending'}
                )
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.dataframe(agency_summary[['agency', 'requests']], use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### ⏱️ Agencies by Average Resolution Time")
            resolution_summary = df.groupby('agency')['median_resolution_hours'].mean().sort_values().head(15).reset_index()
            try:
                import plotly.graph_objects as go
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=resolution_summary['median_resolution_hours'],
                    y=resolution_summary['agency'],
                    orientation='h',
                    marker_color='#ff7f0e',
                    text=resolution_summary['median_resolution_hours'].round(1),
                    textposition='outside',
                    texttemplate='%{text:.1f} hrs'
                ))
                fig.update_layout(
                    xaxis_title="Average Resolution Time (Hours)",
                    yaxis_title="Agency",
                    height=500,
                    showlegend=False,
                    yaxis={'categoryorder':'total ascending'}
                )
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.dataframe(resolution_summary, use_container_width=True, hide_index=True)
    
except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.info("💡 Make sure Postgres is running and data has been loaded.")

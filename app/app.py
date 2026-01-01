"""
NYC 311 Operations Dashboard - Main App
"""
import streamlit as st
import subprocess
import sys
import os

st.set_page_config(
    page_title="NYC 311 Operations Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("NYC 311 Operations Dashboard")

# Sidebar controls
with st.sidebar:
    st.header("Controls")
    
    # Days selector
    days = st.radio(
        "Data Range (Days)",
        options=[30, 60, 90],
        index=0,
        help="Select the number of days of data to fetch"
    )
    
    st.divider()
    
    # Refresh Data button
    if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
        with st.spinner("Refreshing data... This may take a few minutes."):
            try:
                # Step 1: Fetch data
                st.info("Step 1/3: Fetching data from API...")
                result = subprocess.run(
                    [sys.executable, "scripts/fetch_311.py", "--days", str(days)],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd()
                )
                if result.returncode != 0:
                    st.error(f"Error fetching data: {result.stderr}")
                    st.stop()
                st.success("✓ Data fetched successfully")
                
                # Step 2: Load to Postgres
                st.info("Step 2/3: Loading data to Postgres...")
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
                st.success("✓ Data loaded to Postgres")
                
                # Step 3: Rebuild core table
                st.info("Step 3/4: Rebuilding core table...")
                database_url = os.getenv('DATABASE_URL')
                if not database_url:
                    st.error("DATABASE_URL not set. Please set it in your environment.")
                    st.stop()
                
                # Use psql with DATABASE_URL environment variable
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
                st.success("✓ Core table rebuilt")
                
                # Step 4: Build marts
                st.info("Step 4/4: Building marts...")
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
                st.success("✓ Marts built successfully")
                
                st.success("🎉 Data refresh complete!")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error during refresh: {str(e)}")
    
    st.divider()
    st.caption(f"Current data range: Last {days} days")

# Store days in session state for pages to access
st.session_state['days'] = days

# Main content area - Streamlit will auto-discover pages in app/pages/
st.info("Use the sidebar to refresh data or navigate to pages using the sidebar menu.")


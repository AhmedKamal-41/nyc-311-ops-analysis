"""
Configuration utilities for database connection.
"""
import os


def get_database_url():
    """
    Get DATABASE_URL from environment variable or Streamlit secrets.
    
    Priority:
    1. Environment variable (os.getenv) - for local development
    2. Streamlit secrets (st.secrets) - for Streamlit Cloud deployment
    
    Returns:
        str: Database connection URL
        
    Raises:
        RuntimeError: If DATABASE_URL is not found in either location
    """
    # First, try environment variable (local development)
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url
    
    # Second, try Streamlit secrets (Streamlit Cloud)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
            return st.secrets['DATABASE_URL']
    except (ImportError, RuntimeError):
        # Streamlit not available or not in Streamlit context
        # This is fine for standalone scripts
        pass
    
    # Neither found - raise clear error
    raise RuntimeError(
        "DATABASE_URL not found. "
        "For local development: Set DATABASE_URL in .env file or environment variables. "
        "For Streamlit Cloud: Add DATABASE_URL in Advanced settings → Secrets (TOML format)."
    )


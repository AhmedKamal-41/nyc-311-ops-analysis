"""
Streamlit-cached wrapper around src.data.fetch_raw.

All pages import from here so every page shares the SAME cache entry —
only one API call is made per (days, TTL) combination no matter how many
pages are open.
"""
import sys
import os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, _ROOT)

import streamlit as st
import pandas as pd
from src import data as _src_data


@st.cache_data(ttl=3600, show_spinner=False)
def load_raw(days: int = 30) -> pd.DataFrame:
    """Fetch and cache raw 311 data from Socrata.  Refreshes at most once per hour."""
    return _src_data.fetch_raw(days)

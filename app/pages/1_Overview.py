"""
Overview Page — KPI Metrics & Trend Analysis
"""
import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_APP  = os.path.join(_ROOT, "app")
sys.path.insert(0, _ROOT)
sys.path.insert(0, _APP)

import shared_ui as ui
from data_cache import load_raw
import src.data as _data

st.set_page_config(
    page_title="Overview — NYC 311 Dashboard",
    page_icon="📊",
    layout="wide",
)
ui.inject_css()

with st.sidebar:
    st.markdown(
        '<p style="font-size:0.82rem;color:rgba(255,255,255,0.75);line-height:1.5;">'
        'Change the date range or refresh data on the '
        '<strong style="color:#FDB913;">Home</strong> page.</p>',
        unsafe_allow_html=True,
    )

ui.page_hero(
    badge="📊  KPI Metrics",
    title="Overview — Key Performance Indicators",
    subtitle="Monthly trends, resolution times, and performance indicators for NYC 311 service requests",
    chips=["Request Volume", "Resolution Times", "Open vs Closed", "Performance Score"],
)

# ── Load data ─────────────────────────────────────────────────────────────────
days = st.session_state.get("days", 30)
with st.spinner(f"Loading {days}-day snapshot…"):
    try:
        df = load_raw(days)
    except Exception as exc:
        st.error(f"Could not reach NYC Open Data API: {exc}")
        st.stop()

if df.empty:
    st.warning("No data available for this time window.")
    st.stop()

kpi = _data.kpi_monthly(df)

total      = int(kpi["total_requests"].sum())
open_total = int(kpi["open_requests"].sum())
closed     = int(kpi["closed_requests"].sum())
med_res    = float(kpi["median_resolution_hours"].median()) if kpi["median_resolution_hours"].notna().any() else float("nan")
closure    = (closed / total * 100) if total > 0 else 0

# ── Trend Charts ──────────────────────────────────────────────────────────────
import plotly.graph_objects as go

ui.section_header("📈", "Trend Analysis", "Monthly view of key metrics")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Total Requests Over Time**")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=kpi["month"], y=kpi["total_requests"],
        mode="lines+markers", name="Total Requests",
        line=dict(color=ui.NYC_BLUE, width=3),
        marker=dict(size=7, color=ui.NYC_BLUE, line=dict(color="white", width=1.5)),
        fill="tozeroy", fillcolor="rgba(0,87,183,0.07)",
        hovertemplate="%{x|%b %Y}<br><b>%{y:,}</b> requests<extra></extra>",
    ))
    fig.update_layout(**ui.plotly_layout(
        height=340, xaxis_title="Month", yaxis_title="Requests", showlegend=False,
    ))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("**Median Resolution Time (Hours)**")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=kpi["month"], y=kpi["median_resolution_hours"],
        mode="lines+markers", name="Median",
        line=dict(color=ui.NYC_GOLD, width=3),
        marker=dict(size=7, color=ui.NYC_GOLD, line=dict(color="white", width=1.5)),
        fill="tozeroy", fillcolor="rgba(253,185,19,0.08)",
        hovertemplate="%{x|%b %Y}<br><b>%{y:.1f} hrs</b> median<extra></extra>",
    ))
    if kpi["p90_resolution_hours"].notna().any():
        fig.add_trace(go.Scatter(
            x=kpi["month"], y=kpi["p90_resolution_hours"],
            mode="lines", name="90th Pct",
            line=dict(color=ui.NYC_RED, width=2, dash="dot"),
            hovertemplate="%{x|%b %Y}<br><b>%{y:.1f} hrs</b> p90<extra></extra>",
        ))
    fig.update_layout(**ui.plotly_layout(
        height=340, xaxis_title="Month", yaxis_title="Hours", showlegend=True,
    ))
    st.plotly_chart(fig, use_container_width=True)

# ── Detailed Analytics ────────────────────────────────────────────────────────
ui.divider()
ui.section_header("🔬", "Detailed Analytics",
                  "Resolution time comparison and status trends")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Resolution Time: Median vs 90th Percentile**")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=kpi["month"], y=kpi["median_resolution_hours"],
        name="Median", marker_color=ui.NYC_BLUE,
        hovertemplate="%{x|%b %Y}<br>Median: <b>%{y:.1f} hrs</b><extra></extra>",
    ))
    if kpi["p90_resolution_hours"].notna().any():
        fig.add_trace(go.Bar(
            x=kpi["month"], y=kpi["p90_resolution_hours"],
            name="90th Pct", marker_color=ui.NYC_GOLD,
            hovertemplate="%{x|%b %Y}<br>P90: <b>%{y:.1f} hrs</b><extra></extra>",
        ))
    fig.update_layout(**ui.plotly_layout(
        height=340, barmode="group",
        xaxis_title="Month", yaxis_title="Hours",
    ))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("**Open vs Closed Requests Over Time**")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=kpi["month"], y=kpi["closed_requests"],
        mode="lines", name="Closed",
        line=dict(color=ui.NYC_GREEN, width=2.5),
        stackgroup="one", fillcolor="rgba(0,166,81,0.25)",
        hovertemplate="%{x|%b %Y}<br>Closed: <b>%{y:,}</b><extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=kpi["month"], y=kpi["open_requests"],
        mode="lines", name="Open",
        line=dict(color=ui.NYC_RED, width=2.5),
        stackgroup="one", fillcolor="rgba(198,40,40,0.2)",
        hovertemplate="%{x|%b %Y}<br>Open: <b>%{y:,}</b><extra></extra>",
    ))
    fig.update_layout(**ui.plotly_layout(
        height=340, xaxis_title="Month", yaxis_title="Requests",
    ))
    st.plotly_chart(fig, use_container_width=True)

# ── Performance Indicators ────────────────────────────────────────────────────
ui.divider()
ui.section_header("🏆", "Performance Indicators")
p1, p2, p3, p4 = st.columns(4)

with p1:
    flag = "🟢" if closure >= 70 else ("🟡" if closure >= 40 else "🔴")
    st.metric("Request Closure Rate", f"{closure:.1f}%",
              delta=f"{flag} {'Good' if closure>=70 else ('Fair' if closure>=40 else 'Needs attention')}")
with p2:
    avg_monthly = kpi["total_requests"].mean()
    st.metric("Avg Monthly Requests", f"{avg_monthly:,.0f}")
with p3:
    best = kpi["median_resolution_hours"].min()
    st.metric("Best Resolution Time",
              f"{best:.1f} hrs" if pd.notna(best) else "N/A")
with p4:
    worst = kpi["median_resolution_hours"].max()
    st.metric("Peak Resolution Time",
              f"{worst:.1f} hrs" if pd.notna(worst) else "N/A")

# ── Data Table ────────────────────────────────────────────────────────────────
ui.divider()
ui.section_header("📋", "Monthly KPI Data", "Full breakdown of all metrics by month")

display = kpi.copy()
display["month"] = display["month"].dt.strftime("%b %Y")
display = display.rename(columns={
    "month": "Month",
    "total_requests": "Total",
    "open_requests": "Open",
    "closed_requests": "Closed",
    "median_resolution_hours": "Median (hrs)",
    "p90_resolution_hours": "P90 (hrs)",
})
st.dataframe(
    display.style.format({
        "Total":        "{:,.0f}",
        "Open":         "{:,.0f}",
        "Closed":       "{:,.0f}",
        "Median (hrs)": "{:.1f}",
        "P90 (hrs)":    "{:.1f}",
    }).background_gradient(subset=["Total"], cmap="Blues")
      .background_gradient(subset=["Median (hrs)"], cmap="YlOrRd"),
    use_container_width=True,
    hide_index=True,
)

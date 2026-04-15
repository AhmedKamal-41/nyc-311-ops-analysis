"""
Agency Performance Page — Agency Metrics & Trends
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
    page_title="Agency Performance — NYC 311 Dashboard",
    page_icon="🏛",
    layout="wide",
)
ui.inject_css()

with st.sidebar:
    st.markdown(
        '<p style="font-size:0.82rem;color:rgba(255,255,255,0.75);line-height:1.5;">'
        'Change the date range or refresh on the '
        '<strong style="color:#FDB913;">Home</strong> page.</p>',
        unsafe_allow_html=True,
    )

ui.page_hero(
    badge="🏛  Agency Performance",
    title="Agency Performance Analysis",
    subtitle="Track request volumes, resolution times, and efficiency metrics for NYC agencies",
    chips=["Request Volume", "Resolution Speed", "Agency Ranking", "Trend Analysis"],
)

# ── Load data ─────────────────────────────────────────────────────────────────
days = st.session_state.get("days", 30)
with st.spinner(f"Loading {days}-day snapshot…"):
    try:
        raw = load_raw(days)
    except Exception as exc:
        st.error(f"Could not reach NYC Open Data API: {exc}")
        st.stop()

if raw.empty:
    st.warning("No data available for this time window.")
    st.stop()

import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Filters ───────────────────────────────────────────────────────────────────
ui.section_header("🔽", "Filters")
fc1, fc2 = st.columns(2)

with fc1:
    agencies = ["All Agencies"] + sorted(raw["agency"].dropna().unique().tolist())
    selected = st.selectbox("Department (Agency)", agencies,
                             help="Select a specific agency or view all")

with fc2:
    cases = ["All Case Types"] + sorted(raw["complaint_type"].dropna().unique().tolist())
    selected_case = st.selectbox("Case Type", cases,
                                  help="Filter by complaint/case type")

# Apply both filters to raw data, then re-aggregate
filtered_raw = raw.copy()
if selected != "All Agencies":
    filtered_raw = filtered_raw[filtered_raw["agency"] == selected]
if selected_case != "All Case Types":
    filtered_raw = filtered_raw[filtered_raw["complaint_type"] == selected_case]

if filtered_raw.empty:
    st.info("No data matches the selected filters. Try different options.")
    st.stop()

df = _data.agency_performance_monthly(filtered_raw)
fdf = df.copy()

# ── Performance Trends ────────────────────────────────────────────────────────
ui.divider()
ui.section_header("📈", "Performance Trends")
col_tbl, col_chart = st.columns([0.4, 0.6])

with col_tbl:
    st.markdown("**Monthly Performance Data**")
    display = fdf.copy()
    display["month"] = display["month"].dt.strftime("%b %Y")
    display = display.rename(columns={
        "month": "Month", "agency": "Agency",
        "requests": "Requests",
        "median_resolution_hours": "Median (hrs)",
        "p90_resolution_hours": "P90 (hrs)",
    }).style.format({
        "Requests":     "{:,.0f}",
        "Median (hrs)": "{:.1f}",
        "P90 (hrs)":    "{:.1f}",
    }).background_gradient(subset=["Requests"], cmap="Blues")
    st.dataframe(display, use_container_width=True, hide_index=True, height=420)

with col_chart:
    st.markdown("**Request Volume & Resolution Time**")
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Request Volume Over Time",
                        "Resolution Time (Median & P90)"),
        vertical_spacing=0.18,
    )
    fig.add_trace(go.Scatter(
        x=fdf["month"], y=fdf["requests"],
        mode="lines+markers", name="Requests",
        line=dict(color=ui.NYC_BLUE, width=3),
        marker=dict(size=6, color=ui.NYC_BLUE,
                    line=dict(color="white", width=1.5)),
        fill="tozeroy", fillcolor="rgba(0,87,183,0.09)",
        hovertemplate="%{x|%b %Y}<br><b>%{y:,}</b> requests<extra></extra>",
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=fdf["month"], y=fdf["median_resolution_hours"],
        mode="lines+markers", name="Median",
        line=dict(color=ui.NYC_GOLD, width=2.5),
        marker=dict(size=6),
        hovertemplate="%{x|%b %Y}<br>Median: <b>%{y:.1f} hrs</b><extra></extra>",
    ), row=2, col=1)

    if fdf["p90_resolution_hours"].notna().any():
        fig.add_trace(go.Scatter(
            x=fdf["month"], y=fdf["p90_resolution_hours"],
            mode="lines+markers", name="P90",
            line=dict(color=ui.NYC_RED, width=2, dash="dot"),
            marker=dict(size=5),
            hovertemplate="%{x|%b %Y}<br>P90: <b>%{y:.1f} hrs</b><extra></extra>",
        ), row=2, col=1)

    base = ui.plotly_layout(height=440, hovermode="x unified")
    base["xaxis_title"]  = "Month"
    base["xaxis2_title"] = "Month"
    base["yaxis_title"]  = "Requests"
    base["yaxis2_title"] = "Hours"
    fig.update_layout(**base)
    st.plotly_chart(fig, use_container_width=True)

# ── Agency Comparison (All Agencies) ─────────────────────────────────────────
if selected == "All Agencies":
    ui.divider()
    ui.section_header("🏆", "Agency Comparison",
                      "Top performers ranked by volume and resolution speed")

    summary = (filtered_raw.groupby("agency").agg(
        total=("unique_key", "count"),
        avg_resolution=("resolution_hours", lambda s:
                        float(np.nanmedian(s)) if s.notna().any() else np.nan),
    ).reset_index())

    col_v, col_r = st.columns(2)

    with col_v:
        st.markdown("**Top 15 — Request Volume**")
        vol_df  = summary.nlargest(15, "total")
        max_v   = vol_df["total"].max()
        colors_v = [f"rgba(0,87,183,{0.35 + 0.65*r/max_v})"
                    for r in vol_df["total"]]
        fig = go.Figure(go.Bar(
            x=vol_df["total"], y=vol_df["agency"],
            orientation="h",
            marker=dict(color=colors_v, line=dict(width=0)),
            text=vol_df["total"],
            texttemplate="%{text:,}",
            textposition="outside",
            hovertemplate="%{y}<br><b>%{x:,}</b> requests<extra></extra>",
        ))
        fig.update_layout(**ui.plotly_layout(
            height=480, showlegend=False,
            xaxis_title="Total Requests",
            yaxis=dict(categoryorder="total ascending", tickfont=dict(size=11)),
            margin=dict(l=5, r=60, t=10, b=10),
        ))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown("**Top 15 — Fastest Resolution Time**")
        res_df  = summary.dropna(subset=["avg_resolution"]).nsmallest(15, "avg_resolution")

        def _res_color(hrs):
            if hrs < 24:  return ui.NYC_GREEN
            if hrs < 72:  return ui.NYC_GOLD
            return ui.NYC_RED

        colors_r = [_res_color(h) for h in res_df["avg_resolution"]]
        fig = go.Figure(go.Bar(
            x=res_df["avg_resolution"], y=res_df["agency"],
            orientation="h",
            marker=dict(color=colors_r, line=dict(width=0)),
            text=res_df["avg_resolution"].round(1),
            texttemplate="%{text:.1f} hrs",
            textposition="outside",
            hovertemplate="%{y}<br>Avg resolution: <b>%{x:.1f} hrs</b><extra></extra>",
        ))
        fig.update_layout(**ui.plotly_layout(
            height=480, showlegend=False,
            xaxis_title="Avg Resolution Time (hours)",
            yaxis=dict(categoryorder="total descending", tickfont=dict(size=11)),
            margin=dict(l=5, r=80, t=10, b=10),
        ))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div style="display:flex;gap:1.2rem;font-size:0.8rem;color:#64748B;
                margin-top:0.5rem;flex-wrap:wrap;">
        <span><span style="display:inline-block;width:12px;height:12px;
               background:#00A651;border-radius:2px;margin-right:4px;"></span>
               Fast (&lt;24 hrs)</span>
        <span><span style="display:inline-block;width:12px;height:12px;
               background:#FDB913;border-radius:2px;margin-right:4px;"></span>
               Moderate (24–72 hrs)</span>
        <span><span style="display:inline-block;width:12px;height:12px;
               background:#C62828;border-radius:2px;margin-right:4px;"></span>
               Slow (&gt;72 hrs)</span>
    </div>
    """, unsafe_allow_html=True)

    ui.divider()
    ui.section_header("📋", "Full Agency Scorecard")
    scorecard = summary.sort_values("total", ascending=False).copy()
    scorecard["Speed"] = scorecard["avg_resolution"].apply(
        lambda h: ("🟢 Fast"     if pd.notna(h) and h < 24 else
                   "🟡 Moderate" if pd.notna(h) and h < 72 else "🔴 Slow")
    )
    st.dataframe(
        scorecard.rename(columns={
            "agency": "Agency",
            "total": "Total Requests",
            "avg_resolution": "Avg Resolution (hrs)",
        }).style.format({
            "Total Requests":      "{:,.0f}",
            "Avg Resolution (hrs)": "{:.1f}",
        }).background_gradient(subset=["Total Requests"], cmap="Blues"),
        use_container_width=True,
        hide_index=True,
    )

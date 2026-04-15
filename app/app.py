"""
NYC 311 Operations Dashboard — Home
"""
import streamlit as st
import sys
import os
import base64
import pandas as pd
import numpy as np
from datetime import datetime

# ── Path setup ───────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
sys.path.insert(0, _ROOT)
sys.path.insert(0, _HERE)

import shared_ui as ui
from data_cache import load_raw
import src.data as _data

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NYC 311 Operations Dashboard",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)
ui.inject_css()

# ── SVG logo ─────────────────────────────────────────────────────────────────
_SVG = """
<svg width="72" height="72" viewBox="0 0 72 72" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%"   style="stop-color:#0057B7;stop-opacity:1"/>
      <stop offset="100%" style="stop-color:#001E5A;stop-opacity:1"/>
    </linearGradient>
  </defs>
  <circle cx="36" cy="36" r="34" fill="url(#g1)"/>
  <g fill="rgba(255,255,255,0.15)">
    <rect x="8"  y="44" width="4"  height="16"/>
    <rect x="13" y="38" width="4"  height="22"/>
    <rect x="13" y="35" width="2"  height="3"/>
    <rect x="18" y="40" width="6"  height="20"/>
    <rect x="25" y="32" width="8"  height="28"/>
    <rect x="28" y="28" width="2"  height="4"/>
    <rect x="34" y="42" width="5"  height="18"/>
    <rect x="40" y="36" width="5"  height="24"/>
    <rect x="46" y="44" width="4"  height="16"/>
    <rect x="51" y="40" width="5"  height="20"/>
    <rect x="57" y="46" width="4"  height="14"/>
    <rect x="62" y="48" width="3"  height="12"/>
  </g>
  <polygon points="36,10 46,16 46,28 36,34 26,28 26,16"
           fill="#FDB913" opacity="0.95"/>
  <text x="36" y="26" font-family="Arial,sans-serif" font-size="10"
        font-weight="900" fill="#001E5A" text-anchor="middle">311</text>
</svg>
"""
_SVG_B64 = base64.b64encode(_SVG.encode()).decode()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:0.5rem 0 1.2rem;">
        <img src="data:image/svg+xml;base64,{_SVG_B64}" width="42" height="42"/>
        <span style="font-size:1rem;font-weight:800;color:white;letter-spacing:-0.01em;
                     line-height:1.2;">NYC 311<br>
            <span style="font-size:0.72rem;font-weight:500;opacity:0.7;">Operations Dashboard</span>
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<p style="font-size:0.7rem;font-weight:700;text-transform:uppercase;'
        'letter-spacing:0.1em;color:rgba(255,255,255,0.5);margin:0 0 0.5rem;">Data Range</p>',
        unsafe_allow_html=True,
    )
    days = st.radio(
        "Days to fetch",
        options=[30, 60, 90],
        index=0,
        label_visibility="collapsed",
        help="Number of recent days pulled from NYC Open Data API.",
    )

    st.divider()

    st.markdown(
        '<p style="font-size:0.7rem;font-weight:700;text-transform:uppercase;'
        'letter-spacing:0.1em;color:rgba(255,255,255,0.5);margin:0 0 0.5rem;">Live Data</p>',
        unsafe_allow_html=True,
    )

    if st.button("🔄  Refresh Data", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.markdown(
        f'<p style="font-size:0.75rem;color:rgba(255,255,255,0.5);">'
        f'Window: <strong style="color:rgba(255,255,255,0.8);">Last {days} days</strong><br>'
        f'Source: <strong style="color:rgba(255,255,255,0.8);">NYC Open Data API</strong><br>'
        f'Cached: 1 hour &nbsp;|&nbsp; {datetime.now().strftime("%d %b %Y")}</p>',
        unsafe_allow_html=True,
    )

# Store days in session state so sub-pages can pick it up
st.session_state["days"] = days

# ── Hero ──────────────────────────────────────────────────────────────────────
col_logo, col_hero = st.columns([0.07, 0.93])
with col_logo:
    st.markdown(
        f'<img src="data:image/svg+xml;base64,{_SVG_B64}" width="68" height="68"'
        f' style="margin-top:6px;"/>',
        unsafe_allow_html=True,
    )
with col_hero:
    ui.page_hero(
        badge="🟢  Live Data — NYC Open Data API",
        title='NYC <span class="hero-gold">311</span> Operations Dashboard',
        subtitle="Real-time analytics for New York City service requests across all five boroughs",
        chips=["📊 KPI Trends", "🗺 Borough Analysis", "🏛 Agency Performance",
               "📋 Complaint Tracking", "🗺 Live Map"],
    )

# ── Fetch data ────────────────────────────────────────────────────────────────
with st.spinner(f"Loading {days}-day snapshot from NYC Open Data…"):
    try:
        df = load_raw(days)
    except Exception as exc:
        st.error(f"**Could not reach NYC Open Data API.**\n\n{exc}")
        st.info("Check your internet connection and try Refresh Data.")
        st.stop()

if df.empty:
    st.warning("The API returned no records for this time window. Try a wider range.")
    st.stop()

# ── Compute summary stats ─────────────────────────────────────────────────────
total        = len(df)
open_r       = int(df["closed_date"].isna().sum())
closed       = int(df["closed_date"].notna().sum())
avg_res      = float(np.nanmedian(df["resolution_hours"].dropna())) if df["resolution_hours"].notna().any() else float("nan")
closure_rate = (closed / total * 100) if total > 0 else 0

# ── Quick Insights ────────────────────────────────────────────────────────────
ui.section_header("📈", "Quick Insights", "Current status at a glance")
col_left, col_right = st.columns([1.1, 0.9])

with col_left:
    st.markdown("##### Request Status Distribution")
    try:
        import plotly.graph_objects as go
        fig = go.Figure(go.Pie(
            labels=["Open Requests", "Closed Requests"],
            values=[open_r, closed],
            hole=0.52,
            marker_colors=[ui.NYC_RED, ui.NYC_GREEN],
            textinfo="percent",
            hovertemplate="%{label}: %{value:,}<extra></extra>",
        ))
        fig.add_annotation(
            text=f"<b>{closure_rate:.0f}%</b><br><span style='font-size:11px'>closed</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color=ui.NYC_NAVY),
        )
        fig.update_layout(
            **ui.plotly_layout(
                height=320, margin=dict(l=0, r=0, t=10, b=0),
                showlegend=True,
                legend=dict(orientation="h", y=-0.05, xanchor="center", x=0.5),
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.info("Chart unavailable")

with col_right:
    st.markdown("##### Performance Summary")
    flag = "🟢" if closure_rate >= 70 else ("🟡" if closure_rate >= 40 else "🔴")
    res_str = f"{avg_res:.1f} hours" if not np.isnan(avg_res) else "N/A"
    st.markdown(f"""
    <div class="info-block">
        <strong>Closure Rate</strong><br>
        {flag} <strong>{closure_rate:.1f}%</strong> of all requests resolved<br><br>
        <strong>Open vs Closed</strong><br>
        🔴 {open_r:,} open &nbsp;|&nbsp; ✅ {closed:,} closed<br><br>
        <strong>Median Resolution</strong><br>
        ⏱ {res_str}<br><br>
        <strong>Data Window</strong><br>
        📅 Last {days} days &nbsp;·&nbsp; {total:,} records
    </div>
    """, unsafe_allow_html=True)

    # Monthly sparkline
    try:
        monthly = _data.kpi_monthly(df)
        if not monthly.empty:
            fig2 = go.Figure(go.Scatter(
                x=monthly["month"], y=monthly["total_requests"],
                mode="lines+markers",
                line=dict(color=ui.NYC_BLUE, width=2.5),
                marker=dict(size=5),
                fill="tozeroy", fillcolor="rgba(0,87,183,0.08)",
                hovertemplate="%{x|%b %Y}: %{y:,} requests<extra></extra>",
            ))
            fig2.update_layout(
                **ui.plotly_layout(
                    height=180, margin=dict(l=0, r=0, t=20, b=0),
                    showlegend=False,
                    title=dict(text="Monthly Request Volume", font=dict(size=12)),
                )
            )
            st.plotly_chart(fig2, use_container_width=True)
    except Exception:
        pass

# ── Borough Breakdown ─────────────────────────────────────────────────────────
try:
    borough_df = (df.groupby("borough")["unique_key"]
                    .count().reset_index(name="total")
                    .sort_values("total", ascending=False))
    if not borough_df.empty:
        ui.divider()
        ui.section_header("🗺", "Borough Breakdown",
                          "Total service requests by borough")
        colors = [ui.BOROUGH_COLORS.get(b.upper(), ui.NYC_GRAY)
                  for b in borough_df["borough"]]
        fig3 = go.Figure(go.Bar(
            x=borough_df["borough"],
            y=borough_df["total"],
            marker_color=colors,
            text=borough_df["total"],
            texttemplate="%{text:,}",
            textposition="outside",
            hovertemplate="%{x}: %{y:,} requests<extra></extra>",
        ))
        fig3.update_layout(
            **ui.plotly_layout(
                height=320,
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False,
                yaxis=dict(showgrid=True, gridcolor="rgba(221,227,238,0.8)"),
                xaxis=dict(showgrid=False),
            )
        )
        st.plotly_chart(fig3, use_container_width=True)
except Exception:
    pass

# ── Feature cards ─────────────────────────────────────────────────────────────
ui.divider()
ui.section_header("🔍", "Explore the Dashboard")

import streamlit.components.v1 as components
components.html("""
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; }
  .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
  .card {
    background: #FFFFFF;
    border: 1px solid #DDE3EE;
    border-radius: 12px;
    padding: 1.25rem;
    cursor: pointer;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }
  .card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 28px rgba(0,30,90,0.16);
  }
  .card .icon { font-size: 1.6rem; margin-bottom: 0.5rem; }
  .card strong { color: #001E5A; font-size: 0.95rem; }
  .card p { font-size: 0.82rem; color: #64748B; margin-top: 0.5rem; line-height: 1.45; }
</style>
<div class="grid">
  <div class="card" style="border-top:4px solid #0057B7"
       onclick="window.parent.location.href='/Overview'">
    <div class="icon">📊</div>
    <strong>Overview & KPIs</strong>
    <p>Monthly trends, resolution time analysis, closure rates, and performance indicators across all five boroughs.</p>
  </div>
  <div class="card" style="border-top:4px solid #C62828"
       onclick="window.parent.location.href='/Complaints'">
    <div class="icon">📋</div>
    <strong>Complaints Analysis</strong>
    <p>Top complaint types ranked by volume. Filter by borough and month to identify patterns and hotspots.</p>
  </div>
  <div class="card" style="border-top:4px solid #00A651"
       onclick="window.parent.location.href='/Agency_Performance'">
    <div class="icon">🏛</div>
    <strong>Agency Performance</strong>
    <p>Compare agencies by request volume and resolution speed. Track which agencies are keeping up with demand.</p>
  </div>
  <div class="card" style="border-top:4px solid #D97706"
       onclick="window.parent.location.href='/Live_Map'">
    <div class="icon">🗺</div>
    <strong>Live Map</strong>
    <p>Interactive scatter and status view of GPS-tagged complaints across NYC streets and neighborhoods.</p>
  </div>
</div>
""", height=175)

# ── Footer ────────────────────────────────────────────────────────────────────
ui.divider()
st.markdown(
    '<p style="font-size:0.78rem;color:#94A3B8;text-align:center;">'
    'Data source: <a href="https://data.cityofnewyork.us/Social-Services/'
    '311-Service-Requests-from-2010-to-Present/erm2-nwe9" target="_blank" '
    'style="color:#0057B7;">NYC Open Data — 311 Service Requests</a> &nbsp;|&nbsp; '
    'Stack: Python · Pandas · Streamlit · Plotly &nbsp;|&nbsp; '
    'No database required — live API data</p>',
    unsafe_allow_html=True,
)

"""
Live Map Page — Geographic map of NYC 311 complaints
"""
import streamlit as st
import pandas as pd
import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_APP  = os.path.join(_ROOT, "app")
sys.path.insert(0, _ROOT)
sys.path.insert(0, _APP)

import shared_ui as ui
from data_cache import load_raw

st.set_page_config(
    page_title="Live Map — NYC 311 Dashboard",
    page_icon="🗺",
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
    badge="🗺  Live Map",
    title='NYC 311 <span class="hero-gold">Live</span> Complaint Map',
    subtitle="Geographic distribution of service requests across all five boroughs — pinpoint where NYC needs help",
    chips=["Scatter View", "Status View", "Filter by Department & Type", "Borough Zoom"],
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

# Keep only valid NYC GPS coordinates
df_geo = raw[
    raw["latitude"].notna()  &
    raw["longitude"].notna() &
    raw["latitude"].between(40.4, 41.0) &
    raw["longitude"].between(-74.3, -73.6)
].copy()

# ── Map Controls ──────────────────────────────────────────────────────────────
ui.section_header("🎛", "Map Controls")
ctrl1, ctrl2, ctrl3 = st.columns(3)

with ctrl1:
    map_style = st.selectbox(
        "Map style",
        ["Scatter Points", "Status View"],
        index=0,
        help="Scatter Points colors by complaint type. Status View colors by open/closed.",
    )
with ctrl2:
    top_n = st.slider("Complaint types to include", 5, 25, 10)
with ctrl3:
    borough_filter = st.selectbox(
        "Zoom to borough",
        ["All NYC"] + sorted(df_geo["borough"].dropna().unique().tolist()),
    )

# Borough zoom centers
BOROUGH_CENTERS = {
    "MANHATTAN":     {"lat": 40.7831, "lon": -73.9712, "zoom": 12},
    "BROOKLYN":      {"lat": 40.6501, "lon": -73.9496, "zoom": 11},
    "QUEENS":        {"lat": 40.7282, "lon": -73.7949, "zoom": 11},
    "BRONX":         {"lat": 40.8448, "lon": -73.8648, "zoom": 11},
    "STATEN ISLAND": {"lat": 40.5795, "lon": -74.1502, "zoom": 11},
    "ALL NYC":       {"lat": 40.7128, "lon": -74.0060, "zoom": 10},
}
center_key = borough_filter.upper()
center_cfg = BOROUGH_CENTERS.get(center_key, BOROUGH_CENTERS["ALL NYC"])

if borough_filter != "All NYC":
    df_geo = df_geo[df_geo["borough"] == borough_filter.upper()]

# ── Department + Case Type Filters (work together) ────────────────────────────
ui.section_header("🔽", "Filters")
f1, f2 = st.columns(2)

with f1:
    all_agencies = sorted(df_geo["agency"].dropna().unique().tolist())
    selected_agencies = st.multiselect(
        "Department (Agency)",
        options=all_agencies,
        default=all_agencies,
        help="Select one or more NYC agencies to show on the map.",
    )

# Apply department filter before building case type options so the two
# filters are fully aware of each other.
if selected_agencies:
    df_geo = df_geo[df_geo["agency"].isin(selected_agencies)]

with f2:
    top_types = (df_geo["complaint_type"].value_counts()
                   .head(top_n).index.tolist())
    selected_types = st.multiselect(
        "Case Type",
        options=top_types,
        default=top_types[:6],
        help="Select complaint/case types to display.",
    )

if selected_types:
    df_plot = df_geo[df_geo["complaint_type"].isin(selected_types)]
else:
    df_plot = df_geo

if df_plot.empty:
    st.info("No geo-tagged data matches current filters.")
    st.stop()

# ── Derived counts used in map labels ────────────────────────────────────────
total_pts = len(df_plot)

# ── Map ───────────────────────────────────────────────────────────────────────
ui.divider()
import plotly.express as px
import plotly.graph_objects as go

NYC_CENTER = {"lat": center_cfg["lat"], "lon": center_cfg["lon"]}
ZOOM       = center_cfg["zoom"]
PALETTE    = ui.CHART_PALETTE

if map_style == "Status View":
    ui.section_header("🔴🟢", "Status View",
                      f"{total_pts:,} complaints — red = open, green = closed")

    # Normalise status to Open / Closed
    df_status = df_plot.copy()
    df_status["Status"] = df_status["status"].apply(
        lambda s: "Closed" if str(s).upper() == "CLOSED" else "Open"
    )

    plot_df = df_status.head(10_000)
    if len(df_status) > 10_000:
        st.caption(f"Showing 10,000 of {len(df_status):,} points for browser performance.")

    STATUS_COLORS = {"Open": ui.NYC_RED, "Closed": ui.NYC_GREEN}

    fig = px.scatter_mapbox(
        plot_df,
        lat="latitude",
        lon="longitude",
        color="Status",
        color_discrete_map=STATUS_COLORS,
        hover_name="complaint_type",
        hover_data={
            "borough": True,
            "agency": True,
            "Status": True,
            "created_date": True,
            "latitude": False,
            "longitude": False,
        },
        center=NYC_CENTER,
        zoom=ZOOM,
        mapbox_style="carto-positron",
        opacity=0.70,
    )
    fig.update_traces(marker=dict(size=5))
    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            title="Status",
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="#DDE3EE",
            borderwidth=1,
            font=dict(size=12),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

    # Quick open/closed summary under the map
    open_n   = (df_plot["status"].str.upper() != "CLOSED").sum()
    closed_n = (df_plot["status"].str.upper() == "CLOSED").sum()
    open_pct = open_n / total_pts * 100 if total_pts else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Shown", f"{total_pts:,}")
    c2.metric("Open", f"{open_n:,}", delta=f"{open_pct:.1f}% of shown",
              delta_color="inverse")
    c3.metric("Closed", f"{closed_n:,}")

else:
    ui.section_header("📍", "Scatter Map",
                      f"{total_pts:,} individual complaints — colored by type")

    plot_df = df_plot.head(10_000)
    if len(df_plot) > 10_000:
        st.caption(f"Showing 10,000 of {len(df_plot):,} points for browser performance.")

    color_map = {t: PALETTE[i % len(PALETTE)]
                 for i, t in enumerate(selected_types or top_types)}

    fig = px.scatter_mapbox(
        plot_df,
        lat="latitude",
        lon="longitude",
        color="complaint_type",
        color_discrete_map=color_map,
        hover_name="complaint_type",
        hover_data={
            "borough": True,
            "agency": True,
            "status": True,
            "created_date": True,
            "latitude": False,
            "longitude": False,
        },
        center=NYC_CENTER,
        zoom=ZOOM,
        mapbox_style="carto-positron",
        opacity=0.65,
    )
    fig.update_traces(marker=dict(size=5))
    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            title="Complaint Type",
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="#DDE3EE",
            borderwidth=1,
            font=dict(size=11),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

# ── Borough breakdown ─────────────────────────────────────────────────────────
ui.divider()
ui.section_header("🗺", "Borough Breakdown",
                  "Complaint volume and open rate per borough")

borough_stats = (
    df_plot.groupby("borough")
    .agg(count=("unique_key", "count"),
         open_pct=("status", lambda s: (s != "CLOSED").mean() * 100))
    .reset_index()
    .sort_values("count", ascending=False)
)

col_map, col_list = st.columns([0.6, 0.4])

with col_map:
    bar_colors = [ui.BOROUGH_COLORS.get(b.upper(), ui.NYC_GRAY)
                  for b in borough_stats["borough"]]
    fig_b = go.Figure(go.Bar(
        x=borough_stats["borough"],
        y=borough_stats["count"],
        marker_color=bar_colors,
        text=borough_stats["count"],
        texttemplate="%{text:,}",
        textposition="outside",
        hovertemplate="%{x}<br><b>%{y:,}</b> complaints<extra></extra>",
    ))
    fig_b.update_layout(**ui.plotly_layout(
        height=300,
        showlegend=False,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis_title="Borough",
        yaxis_title="Complaints",
    ))
    st.plotly_chart(fig_b, use_container_width=True)

with col_list:
    st.markdown("<br>", unsafe_allow_html=True)
    total_b = borough_stats["count"].sum()
    for _, row in borough_stats.iterrows():
        b = str(row["borough"]).upper()
        css_class = {
            "MANHATTAN": "bb-manhattan", "BROOKLYN": "bb-brooklyn",
            "QUEENS": "bb-queens", "BRONX": "bb-bronx",
            "STATEN ISLAND": "bb-staten",
        }.get(b, "")
        pct = row["count"] / total_b * 100 if total_b else 0
        b_data = df_plot[df_plot["borough"] == row["borough"]]["complaint_type"].value_counts()
        top_t  = b_data.index[0] if len(b_data) else "—"
        st.markdown(f"""
        <div style="padding:0.55rem 0;border-bottom:1px solid #EEF2FF;">
            <div style="display:flex;align-items:center;
                        justify-content:space-between;margin-bottom:0.2rem;">
                <span class="borough-badge {css_class}">{row['borough']}</span>
                <span style="font-size:0.88rem;color:#1E293B;font-weight:600;">
                    {row['count']:,}
                    <span style="color:#94A3B8;font-weight:400;">({pct:.0f}%)</span>
                </span>
            </div>
            <div style="font-size:0.75rem;color:#64748B;padding-left:2px;">
                Top: <em>{top_t[:36]}</em>
                &nbsp;|&nbsp; 🔴 {row['open_pct']:.0f}% open
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Complaint breakdown bar ───────────────────────────────────────────────────
ui.divider()
ui.section_header("📊", "Complaint Breakdown",
                  "Volume by type for current map view")

type_counts = (df_plot["complaint_type"].value_counts()
               .head(15)
               .reset_index())
type_counts.columns = ["complaint_type", "requests"]

n = len(type_counts)
bar_clrs = [f"rgba(0,87,183,{0.35 + 0.65*(1 - i/max(n-1,1))})" for i in range(n)]

fig_t = go.Figure(go.Bar(
    x=type_counts["requests"],
    y=type_counts["complaint_type"],
    orientation="h",
    marker_color=bar_clrs,
    text=type_counts["requests"],
    texttemplate="%{text:,}",
    textposition="outside",
    hovertemplate="%{y}<br><b>%{x:,}</b> complaints<extra></extra>",
))
fig_t.update_layout(**ui.plotly_layout(
    height=max(320, n * 32),
    showlegend=False,
    xaxis_title="Number of Complaints",
    yaxis=dict(categoryorder="total ascending", tickfont=dict(size=11)),
    margin=dict(l=5, r=60, t=10, b=10),
))
st.plotly_chart(fig_t, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
ui.divider()
st.markdown(
    '<p style="font-size:0.78rem;color:#94A3B8;text-align:center;">'
    'Only complaints with GPS coordinates are shown on the map. '
    'Data: <a href="https://data.cityofnewyork.us/Social-Services/'
    '311-Service-Requests-from-2010-to-Present/erm2-nwe9" target="_blank" '
    'style="color:#0057B7;">NYC Open Data</a></p>',
    unsafe_allow_html=True,
)

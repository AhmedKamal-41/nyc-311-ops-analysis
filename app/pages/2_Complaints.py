"""
Complaints Page — Top Complaints by Borough
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
import src.data as _data

st.set_page_config(
    page_title="Complaints — NYC 311 Dashboard",
    page_icon="📋",
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
    badge="📋  Complaint Analysis",
    title="Top Complaints by Borough",
    subtitle="Identify the most common service request types across NYC's five boroughs",
    chips=["Filter by Borough", "Filter by Month", "Volume Ranking", "Borough Comparison"],
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

df = _data.top_complaints_monthly(raw)

# ── Filters ───────────────────────────────────────────────────────────────────
import plotly.graph_objects as go

ui.section_header("🔽", "Filters")
fc1, fc2 = st.columns(2)

with fc1:
    boroughs = ["All Boroughs"] + sorted(df["borough"].dropna().unique().tolist())
    selected_borough = st.selectbox("Borough", boroughs,
                                    help="Filter by NYC borough")
with fc2:
    month_labels = sorted(df["month"].unique(), reverse=True)
    month_options = ["All Months"] + [m.strftime("%b %Y") for m in month_labels]
    selected_month_label = st.selectbox("Month", month_options,
                                        help="Filter by month")

# Build month timestamp for filtering
selected_month = None
if selected_month_label != "All Months":
    idx = month_options.index(selected_month_label) - 1
    selected_month = month_labels[idx]

# Apply filters
fdf = df.copy()
if selected_borough != "All Boroughs":
    fdf = fdf[fdf["borough"] == selected_borough]
if selected_month is not None:
    fdf = fdf[fdf["month"] == selected_month]

if fdf.empty:
    st.info("No data matches the selected filters. Try different options.")
    st.stop()

# ── Main Analysis ─────────────────────────────────────────────────────────────
ui.divider()
ui.section_header("📊", "Top Complaint Types", "Ranked by volume")
col_table, col_chart = st.columns([0.42, 0.58])

with col_table:
    if selected_month is None:
        display = (fdf.groupby(["borough", "complaint_type"])["requests"]
                     .sum().reset_index()
                     .sort_values("requests", ascending=False)
                     .head(20))
    else:
        display = fdf.sort_values("requests", ascending=False).head(20)

    display = display.reset_index(drop=True)
    display.insert(0, "#", range(1, len(display) + 1))

    st.dataframe(
        display.style.format({"requests": "{:,.0f}"}),
        use_container_width=True,
        hide_index=True,
        height=480,
    )

with col_chart:
    if selected_month is None:
        chart_df = (fdf.groupby("complaint_type")["requests"]
                      .sum().reset_index()
                      .sort_values("requests", ascending=False)
                      .head(15))
    else:
        chart_df = fdf.sort_values("requests", ascending=False).head(15)

    n = len(chart_df)
    colors = [f"rgba(0,87,183,{0.35 + 0.65*(1 - i/max(n-1,1))})" for i in range(n)]

    fig = go.Figure(go.Bar(
        x=chart_df["requests"],
        y=chart_df["complaint_type"],
        orientation="h",
        marker=dict(color=colors, line=dict(color="rgba(0,87,183,0.3)", width=0.5)),
        text=chart_df["requests"],
        texttemplate="%{text:,}",
        textposition="outside",
        hovertemplate="%{y}<br><b>%{x:,}</b> requests<extra></extra>",
    ))
    fig.update_layout(**ui.plotly_layout(
        height=480,
        xaxis_title="Number of Requests",
        yaxis=dict(categoryorder="total ascending", tickfont=dict(size=11)),
        showlegend=False,
        margin=dict(l=5, r=60, t=10, b=10),
    ))
    st.plotly_chart(fig, use_container_width=True)

# ── Borough Comparison ────────────────────────────────────────────────────────
if selected_borough == "All Boroughs":
    ui.divider()
    ui.section_header("🗺", "Borough Comparison",
                      "Total complaint volume across all five boroughs")

    borough_sum = (fdf.groupby("borough")["requests"]
                     .sum().sort_values(ascending=False).reset_index())

    col_b1, col_b2 = st.columns([0.6, 0.4])

    with col_b1:
        bar_colors = [ui.BOROUGH_COLORS.get(b.upper(), ui.NYC_GRAY)
                      for b in borough_sum["borough"]]
        fig = go.Figure(go.Bar(
            x=borough_sum["borough"],
            y=borough_sum["requests"],
            marker_color=bar_colors,
            text=borough_sum["requests"],
            texttemplate="%{text:,}",
            textposition="outside",
            hovertemplate="%{x}<br><b>%{y:,}</b> complaints<extra></extra>",
        ))
        fig.update_layout(**ui.plotly_layout(
            height=360, showlegend=False,
            xaxis_title="Borough", yaxis_title="Total Complaints",
            margin=dict(l=0, r=0, t=10, b=0),
        ))
        st.plotly_chart(fig, use_container_width=True)

    with col_b2:
        st.markdown("<br>", unsafe_allow_html=True)
        total_b = borough_sum["requests"].sum()
        for _, row in borough_sum.iterrows():
            b = row["borough"].upper()
            css_class = {
                "MANHATTAN": "bb-manhattan", "BROOKLYN": "bb-brooklyn",
                "QUEENS": "bb-queens", "BRONX": "bb-bronx",
                "STATEN ISLAND": "bb-staten",
            }.get(b, "")
            pct = row["requests"] / total_b * 100 if total_b else 0
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                        padding:0.5rem 0;border-bottom:1px solid #EEF2FF;">
                <span class="borough-badge {css_class}">{row['borough']}</span>
                <span style="font-size:0.88rem;color:#1E293B;font-weight:600;">
                    {row['requests']:,}
                    <span style="color:#94A3B8;font-weight:400;">({pct:.0f}%)</span>
                </span>
            </div>
            """, unsafe_allow_html=True)

    # ── Top complaint per borough ─────────────────────────────────────────────
    ui.divider()
    ui.section_header("🏆", "Top Complaint per Borough")
    bc = st.columns(len(borough_sum))
    for i, (_, brow) in enumerate(borough_sum.iterrows()):
        b = brow["borough"]
        b_data = fdf[fdf["borough"] == b].groupby("complaint_type")["requests"].sum()
        if b_data.empty:
            continue
        top      = b_data.idxmax()
        top_count = int(b_data.max())
        color    = ui.BOROUGH_COLORS.get(b.upper(), ui.NYC_GRAY)
        bc[i].markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #DDE3EE;border-radius:10px;
                    padding:1rem;border-top:3px solid {color};text-align:center;">
            <div style="font-size:0.7rem;font-weight:700;color:#64748B;
                        text-transform:uppercase;letter-spacing:0.06em;
                        margin-bottom:0.25rem;">{b}</div>
            <div style="font-size:0.82rem;font-weight:700;color:#001E5A;
                        line-height:1.3;margin-bottom:0.25rem;">{top}</div>
            <div style="font-size:1.1rem;font-weight:800;color:{color};">
                {top_count:,}
            </div>
        </div>
        """, unsafe_allow_html=True)

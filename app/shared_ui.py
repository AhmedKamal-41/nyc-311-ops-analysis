"""
Shared UI components, CSS, and Plotly defaults for the NYC 311 Dashboard.
"""
import streamlit as st

# ── Official NYC color palette ──────────────────────────────────────────────
NYC_NAVY  = "#001E5A"
NYC_BLUE  = "#0057B7"
NYC_SKY   = "#00A3E0"
NYC_GOLD  = "#FDB913"
NYC_GREEN = "#00A651"
NYC_RED   = "#C62828"
NYC_GRAY  = "#64748B"
NYC_LIGHT = "#F4F6F9"
NYC_CARD  = "#FFFFFF"
NYC_BORDER= "#DDE3EE"
NYC_SHADOW= "rgba(0,30,90,0.08)"

BOROUGH_COLORS = {
    "MANHATTAN":     NYC_BLUE,
    "BROOKLYN":      NYC_RED,
    "QUEENS":        "#D97706",   # amber
    "BRONX":         NYC_GREEN,
    "STATEN ISLAND": "#7C3AED",   # violet
    "UNSPECIFIED":   NYC_GRAY,
}

CHART_PALETTE = [NYC_BLUE, NYC_RED, "#D97706", NYC_GREEN, "#7C3AED",
                 NYC_SKY, NYC_GOLD, "#EC4899", "#0891B2", "#059669"]

# ── Shared CSS ───────────────────────────────────────────────────────────────
_CSS = """
<style>
/* ===== Reset & Base ===== */
#MainMenu, footer, header { visibility: hidden; }

.stApp {
    background: #F4F6F9;
}

.block-container {
    padding-top: 1.25rem !important;
    padding-bottom: 3rem !important;
    max-width: 1440px !important;
}

/* ===== Hero Banner ===== */
.nyc-hero {
    background: linear-gradient(135deg, #001E5A 0%, #0057B7 55%, #00A3E0 100%);
    padding: 2rem 2.25rem 1.75rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    color: white;
    position: relative;
    overflow: hidden;
    animation: fade-up 0.5s ease both;
}
.nyc-hero::after {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(255,255,255,0.07) 0%, transparent 65%);
    border-radius: 50%;
    pointer-events: none;
}
.nyc-hero::before {
    content: '';
    position: absolute;
    bottom: -40px; left: 30%;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(0,163,224,0.12) 0%, transparent 65%);
    border-radius: 50%;
    pointer-events: none;
}
.nyc-hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.14);
    border: 1px solid rgba(255,255,255,0.22);
    color: rgba(255,255,255,0.92);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.28rem 0.75rem;
    border-radius: 20px;
    margin-bottom: 0.7rem;
}
.nyc-hero-badge .dot {
    width: 6px; height: 6px;
    background: #4ADE80;
    border-radius: 50%;
    display: inline-block;
    animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1;   transform: scale(1); }
    50%       { opacity: 0.5; transform: scale(1.5); }
}
@keyframes fade-up {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
    0%   { background-position: -400px 0; }
    100% { background-position:  400px 0; }
}
.nyc-hero h1 {
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    color: white !important;
    margin: 0 0 0.3rem !important;
    letter-spacing: -0.03em;
    line-height: 1.1;
}
.nyc-hero .hero-gold { color: #FDB913; }
.nyc-hero p {
    font-size: 1rem;
    color: rgba(255,255,255,0.8);
    margin: 0;
}
.nyc-hero .hero-chips {
    margin-top: 1rem;
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
}
.hero-chip {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.18);
    color: rgba(255,255,255,0.9);
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.25rem 0.65rem;
    border-radius: 6px;
}

/* ===== KPI / Metric Cards ===== */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #DDE3EE;
    border-radius: 14px;
    padding: 1.35rem 1.5rem;
    box-shadow: 0 2px 8px rgba(0,30,90,0.07);
    position: relative;
    overflow: hidden;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.kpi-card {
    animation: fade-up 0.4s ease both;
}
.kpi-card:nth-child(1) { animation-delay: 0.05s; }
.kpi-card:nth-child(2) { animation-delay: 0.10s; }
.kpi-card:nth-child(3) { animation-delay: 0.15s; }
.kpi-card:nth-child(4) { animation-delay: 0.20s; }
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0,30,90,0.15);
}
.kpi-card .kpi-bar {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 4px;
    border-radius: 14px 14px 0 0;
}
.kpi-card .kpi-icon {
    font-size: 1.5rem;
    margin-bottom: 0.45rem;
    display: block;
}
.kpi-card .kpi-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 0.2rem;
}
.kpi-card .kpi-value {
    font-size: 2rem;
    font-weight: 800;
    color: #001E5A;
    line-height: 1;
    letter-spacing: -0.025em;
}
.kpi-card .kpi-sub {
    font-size: 0.78rem;
    color: #64748B;
    margin-top: 0.3rem;
}

/* ===== Section Headers ===== */
.sec-head {
    font-size: 1.15rem;
    font-weight: 700;
    color: #001E5A;
    margin: 1.5rem 0 0.2rem;
    display: flex;
    align-items: center;
    gap: 0.45rem;
}
.sec-sub {
    font-size: 0.85rem;
    color: #64748B;
    margin: 0 0 0.85rem;
}
.nyc-divider {
    height: 1px;
    background: #DDE3EE;
    margin: 1.5rem 0;
    border: none;
}

/* ===== Info / Status Cards ===== */
.info-block {
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-left: 4px solid #0057B7;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    font-size: 0.88rem;
    color: #1E3A5F;
    line-height: 1.55;
}
.warn-block {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-left: 4px solid #FDB913;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    font-size: 0.88rem;
    color: #78350F;
}
.success-block {
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-left: 4px solid #00A651;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    font-size: 0.88rem;
    color: #14532D;
}

/* ===== Borough Badges ===== */
.borough-badge {
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 0.72rem; font-weight: 700; padding: 0.2rem 0.65rem;
    border-radius: 20px; letter-spacing: 0.04em;
}
.bb-manhattan { background:#DBEAFE; color:#1E40AF; }
.bb-brooklyn  { background:#FEE2E2; color:#991B1B; }
.bb-queens    { background:#FEF3C7; color:#92400E; }
.bb-bronx     { background:#D1FAE5; color:#065F46; }
.bb-staten    { background:#EDE9FE; color:#4C1D95; }

/* ===== Sidebar ===== */
[data-testid="stSidebar"] {
    background: #001E5A !important;
}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
    color: rgba(255,255,255,0.88) !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.15) !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: #FDB913 !important;
    color: #001E5A !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #FFD000 !important;
    color: #001E5A !important;
}
[data-testid="stSidebarNav"] a span {
    color: rgba(255,255,255,0.82) !important;
}
[data-testid="stSidebarNav"] a:hover {
    background: rgba(255,255,255,0.1) !important;
    border-radius: 8px;
}
[data-testid="stSidebarNav"] [aria-current="page"] {
    background: rgba(253,185,19,0.15) !important;
    border-radius: 8px;
}
[data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] p {
    color: rgba(255,255,255,0.7) !important;
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
[data-testid="stSidebar"] .stRadio label span,
[data-testid="stSidebar"] .stRadio label p,
[data-testid="stSidebar"] .stRadio div[data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] .stRadio label {
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] .stSelectbox [data-testid="stWidgetLabel"] p {
    color: rgba(255,255,255,0.7) !important;
}

/* ===== Streamlit metrics override ===== */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #DDE3EE;
    border-radius: 12px;
    padding: 1rem 1.2rem !important;
    box-shadow: 0 1px 4px rgba(0,30,90,0.06);
}
[data-testid="stMetricLabel"] { color: #64748B !important; font-size: 0.78rem !important; text-transform: uppercase; letter-spacing: 0.05em; }
[data-testid="stMetricValue"] { color: #001E5A !important; font-weight: 800 !important; }

/* ===== DataFrames ===== */
[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    border: 1px solid #DDE3EE !important;
    overflow: hidden !important;
}

/* ===== Selectboxes ===== */
[data-testid="stSelectbox"] > div > div {
    border-radius: 8px !important;
    border-color: #DDE3EE !important;
}

/* ===== Headings in main content ===== */
.stMarkdown h2 { color: #001E5A !important; font-weight: 700 !important; }
.stMarkdown h3 { color: #0057B7 !important; font-weight: 600 !important; }
</style>
"""


def inject_css():
    """Inject the shared NYC 311 CSS into the current Streamlit page."""
    st.markdown(_CSS, unsafe_allow_html=True)


def page_hero(badge: str, title: str, subtitle: str, chips: list[str] | None = None):
    """Render the gradient hero banner."""
    chips_html = ""
    if chips:
        chips_html = '<div class="hero-chips">' + "".join(
            f'<span class="hero-chip">{c}</span>' for c in chips
        ) + "</div>"
    st.markdown(f"""
    <div class="nyc-hero">
        <div class="nyc-hero-badge"><span class="dot"></span>{badge}</div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
        {chips_html}
    </div>
    """, unsafe_allow_html=True)


def kpi_card(icon: str, label: str, value: str, sub: str = "", bar_color: str = NYC_BLUE):
    """Return an HTML KPI card string."""
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="kpi-card">
        <div class="kpi-bar" style="background:{bar_color};"></div>
        <span class="kpi-icon">{icon}</span>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {sub_html}
    </div>
    """


def kpi_row(cards: list[str]):
    """Render a row of KPI cards."""
    st.markdown(
        '<div class="kpi-grid">' + "".join(cards) + "</div>",
        unsafe_allow_html=True,
    )


def section_header(icon: str, title: str, sub: str = ""):
    st.markdown(f'<div class="sec-head">{icon} {title}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<p class="sec-sub">{sub}</p>', unsafe_allow_html=True)


def divider():
    st.markdown('<hr class="nyc-divider">', unsafe_allow_html=True)


def stat_banner(stats: list[tuple[str, str, str]]):
    """
    Render a dark stat banner — list of (icon, value, label) tuples.
    Great for showing 3–4 "at a glance" numbers above the fold.
    """
    items = "".join(f"""
    <div style="text-align:center;padding:0 1.5rem;
                border-right:1px solid rgba(255,255,255,0.12);">
        <div style="font-size:1.3rem;margin-bottom:2px;">{icon}</div>
        <div style="font-size:1.55rem;font-weight:800;color:#FDB913;
                    letter-spacing:-0.02em;line-height:1;">{value}</div>
        <div style="font-size:0.72rem;font-weight:600;color:rgba(255,255,255,0.65);
                    text-transform:uppercase;letter-spacing:0.06em;
                    margin-top:3px;">{label}</div>
    </div>
    """ for icon, value, label in stats)
    st.markdown(f"""
    <div style="background:linear-gradient(90deg,#001E5A,#003A8C);
                border-radius:12px;padding:1.1rem 1rem;display:flex;
                justify-content:space-around;align-items:center;
                margin-bottom:1.2rem;box-shadow:0 4px 14px rgba(0,30,90,0.25);">
        {items}
    </div>
    """, unsafe_allow_html=True)


def plotly_layout(**overrides):
    """Return a Plotly layout dict with NYC-themed defaults."""
    base = dict(
        font=dict(family="system-ui, -apple-system, sans-serif", size=13, color="#1E293B"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(
            showgrid=True, gridcolor="rgba(221,227,238,0.8)",
            linecolor="rgba(221,227,238,0.8)", tickfont=dict(size=11),
        ),
        yaxis=dict(
            showgrid=True, gridcolor="rgba(221,227,238,0.8)",
            linecolor="rgba(221,227,238,0.8)", tickfont=dict(size=11),
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="rgba(221,227,238,0.8)", borderwidth=1,
            font=dict(size=12),
        ),
        hoverlabel=dict(bgcolor="white", font_size=13,
                        bordercolor="rgba(221,227,238,0.8)"),
        colorway=CHART_PALETTE,
    )
    base.update(overrides)
    return base

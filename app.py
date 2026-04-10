"""
NexaCart BI Command Center
Run: streamlit run streamlit_dashboard.py
"""
import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ═══════════════════════════════════════════════════════════════════
# PAGE CONFIG  — must be the very first Streamlit call
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="NexaCart BI · Command Center",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════
# THEME TOKENS
# ═══════════════════════════════════════════════════════════════════
BG      = "#07090F"
CARD    = "#0D1117"
CARD2   = "#111827"
BORDER  = "#1F2D3D"
ACCENT  = "#F97316"
GREEN   = "#10B981"
RED     = "#EF4444"
BLUE    = "#3B82F6"
PURPLE  = "#8B5CF6"
YELLOW  = "#FBBF24"
TEAL    = "#14B8A6"
PINK    = "#EC4899"
TEXT    = "#F1F5F9"
SUBTEXT = "#64748B"
DIMTEXT = "#334155"

BUCKET_ORDER  = ["Early (7+ days)","Slightly Early (1-6d)","On Time",
                 "1-3d Late","4-7d Late","8-14d Late","14+ days Late"]
BUCKET_COLORS = [GREEN,"#34D399",TEAL,YELLOW,ACCENT,RED,"#991B1B"]

BRAZIL_COORDS = {
    'AC':(-9.02,-70.81),'AL':(-9.57,-36.78),'AM':(-3.47,-65.10),
    'AP':(1.41,-51.77), 'BA':(-12.97,-41.73),'CE':(-5.20,-39.53),
    'DF':(-15.83,-47.86),'ES':(-19.19,-40.34),'GO':(-15.83,-49.88),
    'MA':(-5.42,-45.44), 'MG':(-18.51,-44.33),'MS':(-20.51,-54.54),
    'MT':(-12.64,-55.42),'PA':(-3.79,-52.48), 'PB':(-7.24,-36.78),
    'PE':(-8.38,-37.86), 'PI':(-7.72,-42.73), 'PR':(-24.89,-51.55),
    'RJ':(-22.91,-43.17),'RN':(-5.81,-36.59), 'RO':(-10.83,-63.34),
    'RR':(2.03,-61.33),  'RS':(-30.03,-53.38),'SC':(-27.45,-50.95),
    'SE':(-10.57,-37.45),'SP':(-22.95,-48.22),'TO':(-10.17,-48.33),
}

# ═══════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ═══════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [data-testid="stAppViewContainer"] {{
    background: {BG} !important;
    font-family: 'Inter', sans-serif;
}}
[data-testid="stSidebar"] {{
    background: {CARD} !important;
    border-right: 1px solid {BORDER};
}}
.block-container {{
    padding: 1.5rem 2.5rem 3rem 2.5rem;
    max-width: 100%;
}}
h1,h2,h3,h4 {{ color: {TEXT} !important; }}
p, label, li {{ color: {SUBTEXT}; font-size:14px; }}
[data-testid="stMetric"] {{ background:transparent; }}

/* KPI cards */
.kpi-card {{
    background: linear-gradient(145deg, {CARD2} 0%, #0A1020 100%);
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 22px 24px 18px;
    position: relative;
    overflow: hidden;
    height: 130px;
}}
.kpi-glow {{
    position: absolute;
    top: -30px; right: -30px;
    width: 100px; height: 100px;
    border-radius: 50%;
    filter: blur(35px);
    opacity: 0.18;
}}
.kpi-label {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    color: {SUBTEXT};
    margin-bottom: 10px;
}}
.kpi-value {{
    font-size: 30px;
    font-weight: 900;
    line-height: 1.0;
    letter-spacing: -0.5px;
}}
.kpi-sub {{
    font-size: 12px;
    margin-top: 7px;
    color: {SUBTEXT};
}}
.kpi-up   {{ color: {GREEN}; }}
.kpi-down {{ color: {RED}; }}

/* Insight box */
.insight-box {{
    background: linear-gradient(135deg,rgba(249,115,22,.09),rgba(139,92,246,.06));
    border-left: 4px solid {ACCENT};
    border-radius: 0 12px 12px 0;
    padding: 14px 20px;
    margin: 8px 0 16px;
}}
.insight-box p {{ color:{TEXT}; font-size:14px; margin:0; line-height:1.7; }}

/* Section header */
.sec-head {{
    display:flex; align-items:center; gap:12px;
    border-bottom: 1px solid {BORDER};
    padding-bottom: 10px;
    margin: 28px 0 16px;
}}
.sec-head span {{ font-size:22px; }}
.sec-head h3 {{
    margin:0; font-size:18px; font-weight:800;
    background: linear-gradient(90deg,{TEXT},{SUBTEXT});
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}}

/* Sidebar nav */
div[data-testid="stRadio"] label {{
    font-size:14px !important;
    font-weight:500 !important;
    padding: 4px 0 !important;
    color:{TEXT} !important;
}}
div[data-testid="stRadio"] {{
    gap: 2px;
}}

/* Funnel labels */
.funnel-row {{
    display:flex; align-items:center; gap:12px;
    padding: 10px 16px; margin:4px 0;
    border-radius:8px;
    background: {CARD2};
    border: 1px solid {BORDER};
}}
.funnel-bar {{
    height: 28px; border-radius:6px;
    background: linear-gradient(90deg,{ACCENT},{PURPLE});
    transition: width .5s ease;
}}

/* Scrollable table */
.scroll-table {{ overflow-x:auto; border-radius:12px; }}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════
def kpi(label, value, sub="", color=TEXT, glow_color=ACCENT):
    return f"""
<div class="kpi-card">
  <div class="kpi-glow" style="background:{glow_color}"></div>
  <div class="kpi-label">{label}</div>
  <div class="kpi-value" style="color:{color}">{value}</div>
  <div class="kpi-sub">{sub}</div>
</div>"""

def sec(icon, title):
    st.markdown(f"""
<div class="sec-head"><span>{icon}</span><h3>{title}</h3></div>
""", unsafe_allow_html=True)

def callout(text):
    st.markdown(f'<div class="insight-box"><p>{text}</p></div>', unsafe_allow_html=True)

def chart_layout(fig, height=None, title=None, showlegend=True,
                 margin=None, bg=CARD):
    m = margin or dict(l=16, r=16, t=40 if title else 24, b=16)
    fig.update_layout(
        paper_bgcolor=bg,
        plot_bgcolor="#080D1A",
        font=dict(family="Inter, sans-serif", color=TEXT, size=12),
        title=dict(text=title, font=dict(color=TEXT, size=14, family="Inter"),
                   x=0.01, xanchor="left") if title else None,
        margin=m,
        height=height,
        showlegend=showlegend,
        legend=dict(bgcolor="rgba(13,17,23,.85)", bordercolor=BORDER,
                    borderwidth=1, font=dict(color=TEXT, size=11)),
        xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, color=SUBTEXT,
                   tickfont=dict(color=SUBTEXT, size=11)),
        yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, color=SUBTEXT,
                   tickfont=dict(color=SUBTEXT, size=11)),
    )
    return fig

def score_color(v, lo=3.5, hi=4.0):
    if pd.isna(v):  return SUBTEXT
    if v >= hi:     return GREEN
    if v >= lo:     return YELLOW
    return RED


# ═══════════════════════════════════════════════════════════════════
# DATA LOADING  (cached)
# ═══════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="Loading NexaCart master dataset…")
def load_data():
    df = pd.read_csv("nexacart_master.csv", low_memory=False)
    for c in ["order_purchase_timestamp","order_approved_at",
              "order_delivered_carrier_date","order_delivered_customer_date",
              "order_estimated_delivery_date"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    for c in ["price","freight_value","review_score","actual_delivery_days",
              "delay_days","is_late","approval_lag_hours","carrier_pickup_days",
              "last_mile_days","total_payment_value","payment_installments"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

df_raw = load_data()


# ═══════════════════════════════════════════════════════════════════
# SIDEBAR — Navigation + Global Filters
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
<div style='padding:20px 0 24px;'>
  <div style='font-size:22px;font-weight:900;color:{TEXT};
              letter-spacing:-0.5px;line-height:1.1;'>
    🛒 NexaCart
  </div>
  <div style='font-size:11px;letter-spacing:2px;color:{SUBTEXT};
              text-transform:uppercase;margin-top:2px;'>
    BI Command Center
  </div>
</div>
<hr style='border-color:{BORDER};margin:0 0 20px;'>
""", unsafe_allow_html=True)

    page = st.radio(
        "NAVIGATE",
        ["📊  Executive Summary",
         "🚚  Delivery Intelligence",
         "🏪  Seller Performance",
         "⭐  Customer Experience",
         "🗺️  Revenue & Geography"],
        label_visibility="visible",
    )

    st.markdown(f"<hr style='border-color:{BORDER};margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:11px;letter-spacing:2px;color:{SUBTEXT};text-transform:uppercase;margin-bottom:10px;'>GLOBAL FILTERS</div>", unsafe_allow_html=True)

    years = sorted([y for y in df_raw["order_year"].dropna().unique() if not pd.isna(y)])
    sel_years = st.multiselect("Year", years, default=years, key="fy")

    all_cats = sorted(df_raw["product_category_name_english"].dropna().unique())
    sel_cats = st.multiselect("Category", all_cats, default=[], key="fc",
                              placeholder="All categories")

    all_states = sorted(df_raw["customer_state"].dropna().unique())
    sel_states = st.multiselect("Customer State", all_states, default=[], key="fs",
                                placeholder="All states")

    st.markdown(f"<hr style='border-color:{BORDER};margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown(f"""
<div style='font-size:11px;color:{SUBTEXT};line-height:1.8;'>
  <div>📁 nexacart_master.csv</div>
  <div>📦 {len(df_raw):,} line items</div>
  <div>🗓️ 2016 – 2018</div>
</div>
""", unsafe_allow_html=True)

# Apply global filters
df = df_raw.copy()
if sel_years:
    df = df[df["order_year"].isin(sel_years)]
if sel_cats:
    df = df[df["product_category_name_english"].isin(sel_cats)]
if sel_states:
    df = df[df["customer_state"].isin(sel_states)]

delivered = df[df["order_status"] == "delivered"].copy()


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════
#  PAGE 1 — EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════
if page.startswith("📊"):

    st.markdown(f"""
<h1 style='font-size:28px;font-weight:900;margin-bottom:4px;'>
  Executive Command Center
</h1>
<p style='font-size:14px;color:{SUBTEXT};margin-bottom:0;'>
  Platform health snapshot · Real-time filters active
</p>
""", unsafe_allow_html=True)

    # ── KPI STRIP ────────────────────────────────────────────────
    total_gmv   = df["price"].sum()
    total_rev   = total_gmv + df["freight_value"].sum()
    avg_review  = df["review_score"].mean()
    pct_late    = delivered["is_late"].sum() / delivered["is_late"].notna().sum() * 100
    avg_del     = delivered["actual_delivery_days"].mean()
    n_orders    = df["order_id"].nunique()

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: st.markdown(kpi("Total GMV", f"R${total_gmv/1e6:.2f}M", f"{n_orders:,} orders", ACCENT, ACCENT), unsafe_allow_html=True)
    with c2: st.markdown(kpi("Total Revenue", f"R${total_rev/1e6:.2f}M", "GMV + freight", BLUE, BLUE), unsafe_allow_html=True)
    with c3:
        rv_color = GREEN if avg_review >= 4.0 else YELLOW if avg_review >= 3.5 else RED
        st.markdown(kpi("Avg Review", f"{avg_review:.2f}/5", "Platform average", rv_color, rv_color), unsafe_allow_html=True)
    with c4:
        lt_color = GREEN if pct_late < 5 else YELLOW if pct_late < 10 else RED
        st.markdown(kpi("% Orders Late", f"{pct_late:.1f}%", "Delivered only", lt_color, lt_color), unsafe_allow_html=True)
    with c5: st.markdown(kpi("Avg Delivery", f"{avg_del:.1f}d", "End-to-end days", PURPLE, PURPLE), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

    # ── ROW 2: GMV TREND + ORDER STATUS ──────────────────────────
    sec("📈", "Revenue Trend")
    col_a, col_b = st.columns([3, 1])

    with col_a:
        mo = (df.groupby("order_month")["price"].sum()
              .reset_index().sort_values("order_month"))
        mo.columns = ["month","gmv"]
        # Rolling 3M average
        mo["rolling3"] = mo["gmv"].rolling(3, min_periods=1).mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=mo["month"], y=mo["gmv"],
            fill="tozeroy", fillcolor=f"rgba(249,115,22,0.10)",
            line=dict(color=ACCENT, width=2.5),
            name="Monthly GMV",
            hovertemplate="<b>%{x}</b><br>GMV: R$ %{y:,.0f}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=mo["month"], y=mo["rolling3"],
            line=dict(color=PURPLE, width=1.8, dash="dot"),
            name="3-month avg",
            hovertemplate="3M Avg: R$ %{y:,.0f}<extra></extra>",
        ))
        peak_idx = mo["gmv"].idxmax()
        fig.add_annotation(
            x=mo.loc[peak_idx,"month"], y=mo.loc[peak_idx,"gmv"],
            text=f"Peak: R${mo.loc[peak_idx,'gmv']/1e3:.0f}K",
            showarrow=True, arrowhead=2, arrowcolor=ACCENT,
            font=dict(color=ACCENT, size=11),
            bgcolor=CARD, bordercolor=ACCENT, borderwidth=1,
            borderpad=4, arrowsize=0.8, ay=-35,
        )
        chart_layout(fig, height=280, title="Monthly Gross Merchandise Value (GMV)")
        fig.update_xaxes(tickangle=-45, nticks=18)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        status_counts = df.groupby("order_status")["order_id"].nunique()
        STATUS_COLORS = {
            "delivered":"#10B981","canceled":"#EF4444","shipped":"#3B82F6",
            "processing":"#8B5CF6","invoiced":"#FBBF24","unavailable":"#6B7280",
            "created":"#14B8A6","approved":"#F97316",
        }
        colors_list = [STATUS_COLORS.get(s, SUBTEXT) for s in status_counts.index]
        total_sc = status_counts.sum()
        # Only label slices >= 3% of total; tiny slices get empty labels
        labels_clean = [
            lbl if (val / total_sc) >= 0.03 else ""
            for lbl, val in zip(status_counts.index, status_counts.values)
        ]
        fig2 = go.Figure(go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            hole=0.62,
            marker=dict(colors=colors_list, line=dict(color=BG, width=2)),
            text=labels_clean,
            textinfo="text+percent",
            texttemplate="%{text}<br><b>%{percent}</b>",
            insidetextorientation="horizontal",
            textposition="outside",
            hovertemplate="<b>%{label}</b><br>%{value:,} orders (%{percent})<extra></extra>",
            showlegend=True,
        ))
        fig2.add_annotation(
            text=f"<b>{total_sc:,}</b><br><span style='font-size:11px'>orders</span>",
            x=0.5, y=0.5, font=dict(size=15, color=TEXT, family="Segoe UI"),
            showarrow=False,
        )
        chart_layout(fig2, height=280, title="Order Status Mix", showlegend=True,
                     margin=dict(l=10, r=10, t=40, b=10))
        fig2.update_layout(
            legend=dict(
                orientation="v", x=1.02, y=0.5, xanchor="left", yanchor="middle",
                font=dict(size=11, color=TEXT), bgcolor="rgba(0,0,0,0)",
                itemsizing="constant",
            )
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── ROW 3: TREEMAP + DAY-OF-WEEK ─────────────────────────────
    sec("🗺️", "Revenue by Category")
    col_c, col_d = st.columns([2, 1])

    with col_c:
        cat_df = (df.groupby("product_category_name_english")
                  .agg(gmv=("price","sum"), avg_review=("review_score","mean"),
                       orders=("order_id","nunique"))
                  .reset_index().dropna())
        cat_df = cat_df[cat_df["gmv"] > 0]
        fig3 = px.treemap(
            cat_df.head(30),
            path=["product_category_name_english"],
            values="gmv",
            color="avg_review",
            color_continuous_scale=[[0,"#7F1D1D"],[0.5,"#FBBF24"],[1,"#10B981"]],
            range_color=[1, 5],
            hover_data={"orders":True, "avg_review":":.2f", "gmv":":.0f"},
            custom_data=["avg_review","orders"],
        )
        fig3.update_traces(
            textfont=dict(color="white", size=12, family="Inter"),
            hovertemplate="<b>%{label}</b><br>GMV: R$ %{value:,.0f}<br>"
                          "Avg Review: %{customdata[0]:.2f}<br>"
                          "Orders: %{customdata[1]:,}<extra></extra>",
        )
        chart_layout(fig3, height=360, title="Revenue Treemap (size=GMV · color=avg review score)")
        fig3.update_coloraxes(colorbar=dict(
            title="Avg Review", tickfont=dict(color=TEXT), title_font=dict(color=TEXT),
            bgcolor=CARD, bordercolor=BORDER, thickness=12, len=0.7,
        ))
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dow = df.groupby("order_dayofweek")["price"].sum().reindex(dow_order).fillna(0)
        fig4 = go.Figure(go.Bar(
            x=dow.values, y=dow.index, orientation="h",
            marker=dict(
                color=dow.values,
                colorscale=[[0,DIMTEXT],[1,ACCENT]],
                showscale=False,
            ),
            hovertemplate="<b>%{y}</b><br>GMV: R$ %{x:,.0f}<extra></extra>",
        ))
        chart_layout(fig4, height=360, title="GMV by Day of Week")
        fig4.update_xaxes(tickprefix="R$", tickformat=".2s")
        st.plotly_chart(fig4, use_container_width=True)

    # ── HEALTH SCORE ─────────────────────────────────────────────
    sec("💡", "Platform Health Index")
    # Composite: review_score (40%) + on-time rate (40%) + review coverage (20%)
    on_time_rate = 1 - (pct_late / 100)
    review_norm  = (avg_review - 1) / 4        # 0–1
    coverage     = df["review_score"].notna().mean()
    health_score = (review_norm * 0.40 + on_time_rate * 0.40 + coverage * 0.20) * 100

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(health_score, 1),
        delta={"reference": 80, "valueformat": ".1f",
               "increasing": {"color": GREEN}, "decreasing": {"color": RED}},
        number={"suffix": "%", "font": {"size": 48, "color": TEXT, "family": "Inter"}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"color": SUBTEXT}},
            "bar":  {"color": ACCENT, "thickness": 0.25},
            "bgcolor": "#0A1020",
            "bordercolor": BORDER,
            "steps": [
                {"range": [0, 50],  "color": "rgba(239,68,68,.12)"},
                {"range": [50, 75], "color": "rgba(251,191,36,.10)"},
                {"range": [75, 100],"color": "rgba(16,185,129,.10)"},
            ],
            "threshold": {"line": {"color": GREEN, "width": 3}, "value": 80},
        },
        title={"text": "Platform Health Score<br><span style='font-size:12px;color:#64748B;'>"
                       "Composite: Avg Review (40%) · On-Time Rate (40%) · Review Coverage (20%)"
                       "</span>",
               "font": {"color": TEXT, "size": 16, "family": "Inter"}},
    ))
    chart_layout(fig_gauge, height=280, margin=dict(l=60,r=60,t=60,b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════
#  PAGE 2 — DELIVERY INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════
elif page.startswith("🚚"):

    st.markdown(f"""
<h1 style='font-size:28px;font-weight:900;margin-bottom:4px;'>Delivery Intelligence</h1>
<p style='font-size:14px;color:{SUBTEXT};'>Where time is lost — and how it destroys reviews</p>
""", unsafe_allow_html=True)

    # ── PIPELINE STRIP ───────────────────────────────────────────
    sec("⏱️", "Fulfillment Pipeline Breakdown")

    avg_appr   = delivered["approval_lag_hours"].mean()
    avg_pick   = delivered["carrier_pickup_days"].mean()
    avg_last   = delivered["last_mile_days"].mean()
    avg_total  = delivered["actual_delivery_days"].mean()

    total_pipe = (avg_appr/24) + avg_pick + avg_last
    pct_appr   = (avg_appr/24) / total_pipe * 100
    pct_pick   = avg_pick / total_pipe * 100
    pct_last   = avg_last / total_pipe * 100

    p1,p2,p3,p4 = st.columns(4)
    with p1: st.markdown(kpi("Approval Lag",f"{avg_appr:.1f}h",f"{pct_appr:.0f}% of pipeline",BLUE,BLUE), unsafe_allow_html=True)
    with p2: st.markdown(kpi("Carrier Pickup",f"{avg_pick:.2f}d",f"{pct_pick:.0f}% of pipeline",YELLOW,YELLOW), unsafe_allow_html=True)
    with p3: st.markdown(kpi("Last Mile",f"{avg_last:.2f}d",f"{pct_last:.0f}% of pipeline ⚠️",RED,RED), unsafe_allow_html=True)
    with p4: st.markdown(kpi("Total Delivery",f"{avg_total:.1f}d","Avg end-to-end",ACCENT,ACCENT), unsafe_allow_html=True)

    # ── PIPELINE STACKED BAR ─────────────────────────────────────
    stages = ["Approval Lag","Carrier Pickup","Last Mile"]
    vals   = [avg_appr/24, avg_pick, avg_last]
    colors = [BLUE, YELLOW, RED]

    fig_pipe = go.Figure()
    for stage, val, col in zip(stages, vals, colors):
        fig_pipe.add_trace(go.Bar(
            name=stage, x=[val], y=["Pipeline"],
            orientation="h", marker_color=col,
            hovertemplate=f"<b>{stage}</b><br>{{x:.2f}} days<extra></extra>",
            text=f"{val:.2f}d", textposition="inside",
            textfont=dict(color="white", size=12, family="Inter"),
        ))
    chart_layout(fig_pipe, height=110, title=None, margin=dict(l=20,r=20,t=8,b=8))
    fig_pipe.update_layout(barmode="stack", yaxis=dict(showticklabels=False),
                           xaxis=dict(title="Days", tickformat=".1f"))
    st.plotly_chart(fig_pipe, use_container_width=True)

    callout(f"Last-mile logistics consumes <b>{pct_last:.0f}% of total delivery time</b> ({avg_last:.2f} days). "
            f"Carrier pickup ({avg_pick:.2f}d) is a secondary lever. Approval lag ({avg_appr/24:.2f}d) is negligible.")

    # ── HERO CHART: REVIEW BY DELAY BUCKET ───────────────────────
    sec("⭐", "The Delay → Review Collapse (Hero Chart)")

    bkt = (delivered.dropna(subset=["review_score"])
           .groupby("delay_bucket")
           .agg(avg_review=("review_score","mean"), count=("order_id","count"))
           .reset_index())
    bkt["bucket_sort"] = bkt["delay_bucket"].map({b:i for i,b in enumerate(BUCKET_ORDER)})
    bkt = bkt.sort_values("bucket_sort").reset_index(drop=True)
    bkt_filt = bkt[bkt["delay_bucket"].isin(BUCKET_ORDER)]

    fig_hero = go.Figure()
    for _, row in bkt_filt.iterrows():
        idx = BUCKET_ORDER.index(row["delay_bucket"]) if row["delay_bucket"] in BUCKET_ORDER else 0
        col = BUCKET_COLORS[idx]
        fig_hero.add_trace(go.Bar(
            name=row["delay_bucket"],
            x=[row["delay_bucket"]],
            y=[row["avg_review"]],
            marker=dict(color=col, line=dict(color="rgba(0,0,0,0.3)", width=1)),
            text=f'{row["avg_review"]:.2f}',
            textposition="outside",
            textfont=dict(color=col, size=13, family="Inter"),
            hovertemplate=f"<b>{row['delay_bucket']}</b><br>"
                          f"Avg Review: <b>{row['avg_review']:.3f}</b><br>"
                          f"Orders: {row['count']:,}<extra></extra>",
        ))

    # Reference line at 4.0
    fig_hero.add_hline(y=4.0, line_dash="dot", line_color=GREEN, line_width=1.5,
                       annotation_text="Target: 4.0", annotation_position="top right",
                       annotation_font=dict(color=GREEN, size=11))
    # Reference line at platform avg
    overall_avg = df["review_score"].mean()
    fig_hero.add_hline(y=overall_avg, line_dash="dash", line_color=SUBTEXT, line_width=1,
                       annotation_text=f"Platform avg: {overall_avg:.2f}",
                       annotation_position="bottom right",
                       annotation_font=dict(color=SUBTEXT, size=10))

    chart_layout(fig_hero, height=380, showlegend=False,
                 title="Avg Review Score by Delivery Timing — the core relationship")
    fig_hero.update_xaxes(categoryorder="array", categoryarray=BUCKET_ORDER)
    fig_hero.update_yaxes(range=[1, 5.5])
    st.plotly_chart(fig_hero, use_container_width=True)

    # Show the table inline
    bkt_display = bkt_filt[["delay_bucket","avg_review","count"]].copy()
    bkt_display.columns = ["Timing Bucket","Avg Review","Order Count"]
    bkt_display["Avg Review"] = bkt_display["Avg Review"].round(3)
    st.dataframe(
        bkt_display.set_index("Timing Bucket"),
        use_container_width=True,
    )

    # ── REVIEW COLLAPSE CURVE ─────────────────────────────────────
    sec("📉", "Review Collapse Curve")
    callout("Each dot = one delivered order. The collapse is non-linear: reviews hold up for small delays, then crater after +4 days. "
            "This is why preventing <i>moderate</i> lateness matters more than preventing <i>large</i> lateness.")

    sample = delivered.dropna(subset=["review_score","delay_days"]).sample(
        min(8000, len(delivered)), random_state=42)
    sample_filt = sample[(sample["delay_days"] >= -15) & (sample["delay_days"] <= 40)]

    fig_curve = go.Figure()
    fig_curve.add_trace(go.Scattergl(
        x=sample_filt["delay_days"], y=sample_filt["review_score"],
        mode="markers",
        marker=dict(size=3, color=sample_filt["delay_days"],
                    colorscale=[[0,GREEN],[0.4,TEAL],[0.55,YELLOW],[0.7,ACCENT],[1,RED]],
                    opacity=0.35, showscale=False),
        name="Orders",
        hovertemplate="Delay: %{x:.1f}d · Review: %{y}<extra></extra>",
    ))
    # Binned trend line
    bins = pd.cut(sample_filt["delay_days"], bins=30)
    trend = sample_filt.groupby(bins, observed=True)["review_score"].mean()
    bin_mids = [b.mid for b in trend.index]
    fig_curve.add_trace(go.Scatter(
        x=bin_mids, y=trend.values,
        mode="lines", line=dict(color=ACCENT, width=3),
        name="Trend (binned avg)",
        hovertemplate="Delay: %{x:.1f}d · Avg Review: %{y:.2f}<extra></extra>",
    ))
    fig_curve.add_vline(x=0, line_dash="dot", line_color=SUBTEXT, line_width=1,
                        annotation_text="On-time threshold", annotation_font=dict(color=SUBTEXT, size=10))
    fig_curve.add_hline(y=4.0, line_dash="dot", line_color=GREEN, line_width=1)
    chart_layout(fig_curve, height=340,
                 title="Delivery Delay (days) vs Review Score — scatter with trend")
    fig_curve.update_xaxes(title="delay_days (negative = early, positive = late)")
    fig_curve.update_yaxes(title="Review Score", range=[0.5, 5.5])
    st.plotly_chart(fig_curve, use_container_width=True)

    # ── STATE MAPS ───────────────────────────────────────────────
    sec("🗺️", "Geographic Delivery Performance")
    col_map, col_scat = st.columns(2)

    cst = (delivered.groupby("customer_state")
           .agg(avg_del=("actual_delivery_days","mean"),
                avg_review=("review_score","mean"),
                order_count=("order_id","count"))
           .reset_index())
    cst["lat"] = cst["customer_state"].map(lambda s: BRAZIL_COORDS.get(s,(np.nan,np.nan))[0])
    cst["lon"] = cst["customer_state"].map(lambda s: BRAZIL_COORDS.get(s,(np.nan,np.nan))[1])
    cst = cst.dropna(subset=["lat"])

    with col_map:
        fig_map = px.scatter_geo(
            cst, lat="lat", lon="lon",
            size="order_count", color="avg_del",
            hover_name="customer_state",
            hover_data={"avg_del":":.1f","avg_review":":.2f","order_count":True,"lat":False,"lon":False},
            color_continuous_scale=[[0,GREEN],[0.5,YELLOW],[1,RED]],
            size_max=55, opacity=0.85,
            labels={"avg_del":"Avg Delivery Days"},
        )
        fig_map.update_geos(
            scope="south america", showland=True, landcolor="#0D1117",
            showocean=True, oceancolor="#070912",
            showframe=False, showcountries=True, countrycolor=BORDER,
            showcoastlines=True, coastlinecolor=BORDER,
            projection_type="mercator",
            center=dict(lat=-14, lon=-52), projection_scale=2.3,
        )
        chart_layout(fig_map, height=400, title="Avg Delivery Days by Customer State",
                     margin=dict(l=0,r=0,t=40,b=0))
        fig_map.update_layout(coloraxis_colorbar=dict(
            title="Avg Del Days", tickfont=dict(color=TEXT),
            title_font=dict(color=TEXT), bgcolor=CARD, bordercolor=BORDER, thickness=12))
        st.plotly_chart(fig_map, use_container_width=True)

    with col_scat:
        overall_avg_del = delivered["actual_delivery_days"].mean()
        fig_ss = px.scatter(
            cst, x="avg_del", y="avg_review",
            size="order_count", color="avg_del",
            text="customer_state",
            color_continuous_scale=[[0,GREEN],[1,RED]],
            hover_name="customer_state",
            hover_data={"avg_del":":.1f","avg_review":":.2f","order_count":True},
            size_max=50,
        )
        fig_ss.add_hline(y=4.0, line_dash="dot", line_color=GREEN, line_width=1)
        fig_ss.add_vline(x=overall_avg_del, line_dash="dot", line_color=SUBTEXT, line_width=1)
        fig_ss.update_traces(textposition="top center", textfont=dict(color=TEXT, size=10))
        chart_layout(fig_ss, height=400,
                     title="Delivery Speed vs Review Score — by Customer State")
        fig_ss.update_xaxes(title="Avg Delivery Days")
        fig_ss.update_yaxes(title="Avg Review Score")
        fig_ss.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_ss, use_container_width=True)

    # Worst states table
    worst_states = cst.sort_values("avg_del", ascending=False).head(10)[
        ["customer_state","avg_del","avg_review","order_count"]].copy()
    worst_states.columns = ["State","Avg Delivery Days","Avg Review","Orders"]
    worst_states = worst_states.round(2).reset_index(drop=True)
    sec("⚠️", "10 Slowest Delivery States")
    st.dataframe(worst_states.set_index("State"), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════
#  PAGE 3 — SELLER PERFORMANCE
# ═══════════════════════════════════════════════════════════════════
elif page.startswith("🏪"):

    st.markdown(f"""
<h1 style='font-size:28px;font-weight:900;margin-bottom:4px;'>Seller Performance</h1>
<p style='font-size:14px;color:{SUBTEXT};'>Stars, rising stars, and risk sellers — the full picture</p>
""", unsafe_allow_html=True)

    sellers_df = (df.groupby("seller_id")
                  .agg(gmv=("price","sum"),
                       order_count=("order_id","nunique"),
                       avg_review=("review_score","mean"),
                       avg_delay=("delay_days","mean"),
                       seller_state=("seller_state","first"))
                  .reset_index())

    qualified = sellers_df[sellers_df["order_count"] >= 50].copy()
    avg_orders_q = qualified["order_count"].mean()

    def seller_segment(row):
        if row["avg_review"] >= 4.0 and row["order_count"] >= avg_orders_q: return "Star Seller"
        if row["avg_review"] >= 4.0:  return "Rising Star"
        if row["order_count"] >= avg_orders_q: return "Risk Seller"
        return "Long Tail"

    qualified["segment"] = qualified.apply(seller_segment, axis=1)

    SEG_COLORS = {"Star Seller":GREEN,"Rising Star":TEAL,
                  "Risk Seller":RED,"Long Tail":SUBTEXT}

    # ── QUADRANT SCATTER ─────────────────────────────────────────
    sec("📍", "Seller Quadrant Matrix")
    callout(f"Quadrant dividers: <b>avg {avg_orders_q:.0f} orders</b> (X-axis) · "
            f"<b>4.0 review score</b> (Y-axis). "
            f"Risk Sellers = high volume, low review — highest intervention priority.")

    fig_quad = go.Figure()

    # Shaded quadrant backgrounds
    x_max = qualified["order_count"].max() * 1.1
    fig_quad.add_shape(type="rect",
        x0=avg_orders_q, x1=x_max, y0=1, y1=4.0,
        fillcolor="rgba(239,68,68,0.06)", line_width=0)
    fig_quad.add_shape(type="rect",
        x0=0, x1=avg_orders_q, y0=4.0, y1=5.2,
        fillcolor="rgba(20,184,166,0.04)", line_width=0)
    fig_quad.add_shape(type="rect",
        x0=avg_orders_q, x1=x_max, y0=4.0, y1=5.2,
        fillcolor="rgba(16,185,129,0.06)", line_width=0)

    for seg, grp in qualified.groupby("segment"):
        fig_quad.add_trace(go.Scatter(
            x=grp["order_count"], y=grp["avg_review"],
            mode="markers",
            name=seg,
            marker=dict(size=np.clip(grp["gmv"]/5000, 4, 24),
                        color=SEG_COLORS[seg], opacity=0.8,
                        line=dict(color="rgba(0,0,0,.3)", width=0.5)),
            hovertemplate=(f"<b>%{{customdata[0]}}</b><br>"
                           f"Segment: {seg}<br>"
                           f"Orders: %{{x:,}}<br>"
                           f"Avg Review: %{{y:.2f}}<br>"
                           f"GMV: R$ %{{customdata[1]:,.0f}}<extra></extra>"),
            customdata=grp[["seller_id","gmv"]].values,
        ))

    fig_quad.add_vline(x=avg_orders_q, line_dash="dash",line_color=BORDER,line_width=1.5)
    fig_quad.add_hline(y=4.0, line_dash="dash", line_color=BORDER, line_width=1.5)

    for label, x_pos, y_pos in [
        ("⭐ STAR SELLERS",    x_max*0.75, 4.9),
        ("🌱 RISING STARS",   avg_orders_q*0.3, 4.9),
        ("🔴 RISK SELLERS",   x_max*0.75, 1.3),
        ("💤 LONG TAIL",      avg_orders_q*0.3, 1.3),
    ]:
        fig_quad.add_annotation(x=x_pos, y=y_pos, text=label,
                                font=dict(color=SUBTEXT, size=10, family="Inter"),
                                showarrow=False, opacity=0.6)

    chart_layout(fig_quad, height=450,
                 title="Seller Quadrant: Order Volume vs Avg Review Score (bubble size = GMV)")
    fig_quad.update_xaxes(title="Total Orders per Seller")
    fig_quad.update_yaxes(title="Avg Review Score", range=[0.8, 5.3])
    st.plotly_chart(fig_quad, use_container_width=True)

    # Segment summary cards
    s1,s2,s3,s4 = st.columns(4)
    seg_counts = qualified["segment"].value_counts()
    with s1: st.markdown(kpi("Star Sellers",   str(seg_counts.get("Star Seller",0)),  "high vol · high review", GREEN,  GREEN),  unsafe_allow_html=True)
    with s2: st.markdown(kpi("Rising Stars",   str(seg_counts.get("Rising Star",0)),  "low vol · high review",  TEAL,   TEAL),   unsafe_allow_html=True)
    with s3: st.markdown(kpi("Risk Sellers",   str(seg_counts.get("Risk Seller",0)),  "high vol · low review ⚠️", RED, RED),     unsafe_allow_html=True)
    with s4: st.markdown(kpi("Long Tail",      str(seg_counts.get("Long Tail",0)),    "low vol · low review",   SUBTEXT,SUBTEXT), unsafe_allow_html=True)

    # ── TOP 20 SELLERS ───────────────────────────────────────────
    sec("💰", "Top 20 Sellers by GMV")
    top20 = sellers_df.sort_values("gmv", ascending=False).head(20).copy()
    top20["short_id"] = top20["seller_id"].str[:12] + "…"
    top20["review_color"] = top20["avg_review"].apply(score_color)

    fig_top = go.Figure(go.Bar(
        y=top20["short_id"][::-1],
        x=top20["gmv"][::-1],
        orientation="h",
        marker=dict(
            color=top20["avg_review"][::-1],
            colorscale=[[0,RED],[0.5,YELLOW],[1,GREEN]],
            cmin=1, cmax=5,
            colorbar=dict(title="Avg Review", tickfont=dict(color=TEXT),
                          title_font=dict(color=TEXT), bgcolor=CARD,
                          bordercolor=BORDER, thickness=12),
            line=dict(color="rgba(0,0,0,.2)", width=0.5),
        ),
        hovertemplate="<b>%{y}</b><br>GMV: R$ %{x:,.0f}<br>Review: %{marker.color:.2f}<extra></extra>",
    ))
    chart_layout(fig_top, height=480,
                 title="Top 20 Sellers by Revenue — bars colored by avg review score",
                 showlegend=False)
    fig_top.update_xaxes(tickprefix="R$", tickformat=".2s")
    st.plotly_chart(fig_top, use_container_width=True)

    # ── BOTTOM 15 SELLERS ────────────────────────────────────────
    sec("🚨", "Highest-Risk Sellers (min 50 orders, sorted by review)")
    bottom15 = qualified.nsmallest(15, "avg_review")[
        ["seller_id","seller_state","order_count","avg_review","avg_delay","gmv"]
    ].copy()
    bottom15.columns = ["Seller ID","State","Orders","Avg Review","Avg Delay (d)","GMV (R$)"]
    bottom15["Avg Review"] = bottom15["Avg Review"].round(3)
    bottom15["Avg Delay (d)"] = bottom15["Avg Delay (d)"].round(1)
    bottom15["GMV (R$)"] = bottom15["GMV (R$)"].round(0).astype(int)
    bottom15 = bottom15.reset_index(drop=True)

    def highlight_review(v):
        if isinstance(v, float):
            if v < 2.5:  return "background-color: rgba(239,68,68,0.20); color: #EF4444;"
            if v < 3.5:  return "background-color: rgba(251,191,36,0.15); color: #FBBF24;"
        return ""

    st.dataframe(
        bottom15.style.map(highlight_review, subset=["Avg Review"]),
        use_container_width=True, hide_index=True,
    )

    # ── SELLER STATE BUBBLE MAP ───────────────────────────────────
    sec("🗺️", "Seller State: Revenue vs Quality")
    ss_state = (df.groupby("seller_state")
                .agg(gmv=("price","sum"), seller_count=("seller_id","nunique"),
                     avg_review=("review_score","mean"))
                .reset_index())
    ss_state["lat"] = ss_state["seller_state"].map(lambda s: BRAZIL_COORDS.get(s,(np.nan,np.nan))[0])
    ss_state["lon"] = ss_state["seller_state"].map(lambda s: BRAZIL_COORDS.get(s,(np.nan,np.nan))[1])
    ss_state = ss_state.dropna(subset=["lat"])

    fig_smap = px.scatter_geo(
        ss_state, lat="lat", lon="lon",
        size="gmv", color="avg_review",
        hover_name="seller_state",
        hover_data={"seller_count":True,"avg_review":":.2f","gmv":":.0f","lat":False,"lon":False},
        color_continuous_scale=[[0,RED],[0.5,YELLOW],[1,GREEN]],
        size_max=60, opacity=0.85,
        range_color=[1,5],
    )
    fig_smap.update_geos(
        scope="south america", showland=True, landcolor="#0D1117",
        showocean=True, oceancolor="#070912",
        showframe=False, showcountries=True, countrycolor=BORDER,
        center=dict(lat=-14, lon=-52), projection_scale=2.3,
    )
    chart_layout(fig_smap, height=400,
                 title="Seller State: Bubble size = GMV · Color = Avg Review Score",
                 margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig_smap, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════
#  PAGE 4 — CUSTOMER EXPERIENCE
# ═══════════════════════════════════════════════════════════════════
elif page.startswith("⭐"):

    st.markdown(f"""
<h1 style='font-size:28px;font-weight:900;margin-bottom:4px;'>Customer Experience</h1>
<p style='font-size:14px;color:{SUBTEXT};'>What drives 1-star and 5-star reviews</p>
""", unsafe_allow_html=True)

    # ── NPS CARDS ────────────────────────────────────────────────
    total_rev_count = df["review_score"].notna().sum()
    n_det = (df["review_score"] <= 2).sum()
    n_pas = (df["review_score"] == 3).sum()
    n_pro = (df["review_score"] >= 4).sum()
    pct_det = n_det / total_rev_count * 100
    pct_pas = n_pas / total_rev_count * 100
    pct_pro = n_pro / total_rev_count * 100

    sec("📊", "Review Score Distribution")
    c1,c2,c3 = st.columns(3)
    with c1: st.markdown(kpi("Detractors (1-2 ★)", f"{pct_det:.1f}%", f"{n_det:,} reviews — fix priority", RED, RED), unsafe_allow_html=True)
    with c2: st.markdown(kpi("Passives (3 ★)", f"{pct_pas:.1f}%", f"{n_pas:,} reviews — convertible", YELLOW, YELLOW), unsafe_allow_html=True)
    with c3: st.markdown(kpi("Promoters (4-5 ★)", f"{pct_pro:.1f}%", f"{n_pro:,} reviews — protect these", GREEN, GREEN), unsafe_allow_html=True)

    # NPS ring trio
    fig_nps = make_subplots(rows=1, cols=3, specs=[[{"type":"pie"},{"type":"pie"},{"type":"pie"}]],
                             subplot_titles=["Detractors","Passives","Promoters"])
    for col_idx, (val, rest, color, label) in enumerate([
        (n_det, total_rev_count-n_det, RED, "Detractors"),
        (n_pas, total_rev_count-n_pas, YELLOW, "Passives"),
        (n_pro, total_rev_count-n_pro, GREEN, "Promoters"),
    ], 1):
        fig_nps.add_trace(go.Pie(
            values=[val, rest], hole=0.72,
            marker=dict(colors=[color, BORDER]),
            textinfo="none",
            hovertemplate=f"<b>{label}</b>: {{value:,}} ({val/total_rev_count*100:.1f}%)<extra></extra>",
            showlegend=False,
        ), row=1, col=col_idx)
        fig_nps.add_annotation(
            x=[0.12,0.5,0.88][col_idx-1], y=0.5,
            text=f"<b>{val/total_rev_count*100:.1f}%</b>",
            font=dict(color=color, size=16, family="Inter"), showarrow=False,
        )
    chart_layout(fig_nps, height=200, margin=dict(l=20,r=20,t=60,b=10), showlegend=False)
    fig_nps.update_annotations(font=dict(color=SUBTEXT, size=12, family="Inter"))
    st.plotly_chart(fig_nps, use_container_width=True)

    # ── REVIEW DISTRIBUTION BY CATEGORY ──────────────────────────
    sec("📦", "Review Distribution by Category (sorted by detractor %)")

    # Top 20 categories by order count
    top_cats = df.groupby("product_category_name_english")["order_id"].nunique()\
                 .sort_values(ascending=False).head(20).index.tolist()
    cat_data = df[df["product_category_name_english"].isin(top_cats)].copy()
    cat_data["review_band"] = pd.cut(
        cat_data["review_score"],
        bins=[0,1.5,2.5,3.5,4.5,5.1],
        labels=["1 ★","2 ★","3 ★","4 ★","5 ★"],
    )
    cat_pivot = (cat_data.groupby(["product_category_name_english","review_band"])
                 .size().unstack(fill_value=0))
    cat_pivot = cat_pivot.div(cat_pivot.sum(axis=1), axis=0) * 100
    if "1 ★" in cat_pivot.columns and "2 ★" in cat_pivot.columns:
        cat_pivot["_det"] = cat_pivot.get("1 ★",0) + cat_pivot.get("2 ★",0)
        cat_pivot = cat_pivot.sort_values("_det", ascending=True)
        cat_pivot = cat_pivot.drop(columns=["_det"])

    STAR_COLORS = {"1 ★":RED,"2 ★":"#F87171","3 ★":YELLOW,"4 ★":"#34D399","5 ★":GREEN}
    fig_cat_dist = go.Figure()
    for band in cat_pivot.columns:
        fig_cat_dist.add_trace(go.Bar(
            name=band, y=cat_pivot.index, x=cat_pivot[band],
            orientation="h",
            marker_color=STAR_COLORS.get(band, SUBTEXT),
            hovertemplate=f"<b>{band}</b><br>%{{y}}<br>%{{x:.1f}}%<extra></extra>",
        ))
    chart_layout(fig_cat_dist, height=560,
                 title="Review Score Distribution by Category (% share, sorted by detractor %)")
    fig_cat_dist.update_layout(barmode="stack", bargap=0.15,
                               xaxis=dict(ticksuffix="%", range=[0,100]))
    st.plotly_chart(fig_cat_dist, use_container_width=True)

    # ── MONTHLY REVIEW TREND ──────────────────────────────────────
    sec("📈", "Review Score Over Time")
    col_trend, col_state = st.columns(2)

    with col_trend:
        mo_review = (df.groupby("order_month")["review_score"]
                     .agg(["mean","count"]).reset_index()
                     .sort_values("order_month"))
        mo_review.columns = ["month","avg","count"]
        mo_review["rolling3"] = mo_review["avg"].rolling(3, min_periods=1).mean()

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=mo_review["month"], y=mo_review["avg"],
            mode="lines+markers",
            line=dict(color=PURPLE, width=2),
            marker=dict(size=5, color=PURPLE),
            name="Monthly avg",
            hovertemplate="<b>%{x}</b><br>Avg Review: %{y:.3f}<extra></extra>",
        ))
        fig_trend.add_trace(go.Scatter(
            x=mo_review["month"], y=mo_review["rolling3"],
            mode="lines", line=dict(color=ACCENT, width=2.5, dash="dot"),
            name="3-month rolling avg",
        ))
        fig_trend.add_hline(y=4.0, line_dash="dot", line_color=GREEN, line_width=1)
        chart_layout(fig_trend, height=320,
                     title="Monthly Avg Review Score with 3-Month Rolling Avg")
        fig_trend.update_xaxes(tickangle=-45, nticks=15)
        fig_trend.update_yaxes(range=[3, 5], title="Avg Review")
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_state:
        state_review = (df.dropna(subset=["review_score"])
                        .groupby("customer_state")
                        .agg(avg=("review_score","mean"),
                             count=("order_id","nunique"))
                        .reset_index()
                        .sort_values("avg", ascending=True))
        top15_states = state_review[state_review["count"] >= 50].tail(27)
        overall_avg  = df["review_score"].mean()

        bar_colors = [GREEN if v >= 4.0 else (YELLOW if v >= 3.5 else RED)
                      for v in top15_states["avg"]]
        fig_state_rev = go.Figure(go.Bar(
            y=top15_states["customer_state"],
            x=top15_states["avg"],
            orientation="h",
            marker=dict(color=bar_colors, line=dict(color="rgba(0,0,0,.2)",width=0.5)),
            hovertemplate="<b>%{y}</b><br>Avg Review: %{x:.3f}<extra></extra>",
            text=top15_states["avg"].round(2),
            textposition="outside",
            textfont=dict(color=TEXT, size=10),
        ))
        fig_state_rev.add_vline(x=overall_avg, line_dash="dash",
                                line_color=SUBTEXT, line_width=1.5,
                                annotation_text=f"Avg {overall_avg:.2f}",
                                annotation_font=dict(color=SUBTEXT, size=10))
        chart_layout(fig_state_rev, height=320,
                     title="Avg Review Score by Customer State (colored: green≥4.0 · amber≥3.5 · red<3.5)",
                     showlegend=False)
        fig_state_rev.update_xaxes(range=[3.0, 4.8])
        st.plotly_chart(fig_state_rev, use_container_width=True)

    # ── STATE × DELAY HEATMAP ────────────────────────────────────
    sec("🔥", "Review Score Heatmap: Customer State × Delivery Timing")
    callout("This heatmap shows how review scores vary by <b>both region AND delivery timing</b>. "
            "Red cells = highest-priority intervention zones. States with red across all delay buckets have structural quality problems beyond just delivery.")

    hm_data = (delivered.dropna(subset=["review_score"])
               .groupby(["customer_state","delay_bucket"])["review_score"]
               .mean().reset_index())
    hm_pivot = hm_data.pivot(index="customer_state", columns="delay_bucket", values="review_score")
    hm_pivot = hm_pivot.reindex(columns=[c for c in BUCKET_ORDER if c in hm_pivot.columns])
    # Show top 20 states by order count
    top_states_hm = (df.groupby("customer_state")["order_id"].nunique()
                     .sort_values(ascending=False).head(20).index.tolist())
    hm_pivot = hm_pivot.loc[[s for s in top_states_hm if s in hm_pivot.index]]

    fig_hm = go.Figure(go.Heatmap(
        z=hm_pivot.values,
        x=hm_pivot.columns.tolist(),
        y=hm_pivot.index.tolist(),
        colorscale=[[0,RED],[0.35,YELLOW],[0.6,TEAL],[1,GREEN]],
        zmin=1, zmax=5,
        text=np.round(hm_pivot.values, 2),
        texttemplate="%{text}",
        textfont=dict(size=10, color="white", family="Inter"),
        hovertemplate="State: <b>%{y}</b><br>Timing: <b>%{x}</b><br>Avg Review: <b>%{z:.2f}</b><extra></extra>",
        colorbar=dict(title="Avg Review", tickfont=dict(color=TEXT),
                      title_font=dict(color=TEXT), bgcolor=CARD,
                      bordercolor=BORDER, thickness=12),
    ))
    chart_layout(fig_hm, height=560,
                 title="Avg Review Score Heatmap — State × Delivery Timing",
                 margin=dict(l=60,r=60,t=50,b=80))
    fig_hm.update_xaxes(tickangle=-30)
    st.plotly_chart(fig_hm, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════
#  PAGE 5 — REVENUE & GEOGRAPHY
# ═══════════════════════════════════════════════════════════════════
elif page.startswith("🗺️"):

    st.markdown(f"""
<h1 style='font-size:28px;font-weight:900;margin-bottom:4px;'>Revenue & Geographic Opportunity</h1>
<p style='font-size:14px;color:{SUBTEXT};'>Where to grow, where revenue is at risk</p>
""", unsafe_allow_html=True)

    # ── AT-RISK KPIs ─────────────────────────────────────────────
    state_gmv = (df.groupby("customer_state")
                 .agg(gmv=("price","sum"), avg_review=("review_score","mean"),
                      order_count=("order_id","nunique"))
                 .reset_index())
    overall_review = df["review_score"].mean()
    at_risk = state_gmv[state_gmv["avg_review"] < overall_review]
    at_risk_gmv = at_risk["gmv"].sum()
    at_risk_pct = at_risk_gmv / state_gmv["gmv"].sum() * 100

    sec("⚠️", "Revenue at Risk")
    k1,k2,k3 = st.columns(3)
    with k1: st.markdown(kpi("At-Risk GMV", f"R${at_risk_gmv/1e6:.2f}M", f"States with below-avg review", RED, RED), unsafe_allow_html=True)
    with k2: st.markdown(kpi("% Revenue at Risk", f"{at_risk_pct:.1f}%", "Of total GMV in low-review states", YELLOW, YELLOW), unsafe_allow_html=True)
    with k3: st.markdown(kpi("High-Risk States", str(len(at_risk)), "Below platform avg review", ACCENT, ACCENT), unsafe_allow_html=True)

    # ── STATE BUBBLE MAP + SCATTER ────────────────────────────────
    sec("💰", "Revenue vs Satisfaction by State")
    col_m, col_s = st.columns(2)

    state_gmv["lat"] = state_gmv["customer_state"].map(lambda s: BRAZIL_COORDS.get(s,(np.nan,np.nan))[0])
    state_gmv["lon"] = state_gmv["customer_state"].map(lambda s: BRAZIL_COORDS.get(s,(np.nan,np.nan))[1])
    sdf = state_gmv.dropna(subset=["lat"])

    with col_m:
        fig_gmap = px.scatter_geo(
            sdf, lat="lat", lon="lon",
            size="gmv", color="avg_review",
            hover_name="customer_state",
            hover_data={"gmv":":.0f","avg_review":":.2f","order_count":True,"lat":False,"lon":False},
            color_continuous_scale=[[0,RED],[0.5,YELLOW],[1,GREEN]],
            size_max=65, opacity=0.9, range_color=[1,5],
        )
        fig_gmap.update_geos(
            scope="south america", showland=True, landcolor="#0D1117",
            showocean=True, oceancolor="#070912",
            showframe=False, showcountries=True, countrycolor=BORDER,
            center=dict(lat=-14, lon=-52), projection_scale=2.3,
        )
        chart_layout(fig_gmap, height=420,
                     title="State Revenue Map — size=GMV · color=avg review",
                     margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig_gmap, use_container_width=True)

    with col_s:
        med_gmv = sdf["gmv"].median()
        sdf["risk_label"] = sdf.apply(
            lambda r: "At-Risk Revenue" if r["gmv"] > med_gmv and r["avg_review"] < overall_review
            else ("Growth Opportunity" if r["gmv"] <= med_gmv and r["avg_review"] >= overall_review
            else ("Core Market" if r["gmv"] > med_gmv else "Monitor")), axis=1)
        RISK_COLORS = {"At-Risk Revenue":RED,"Growth Opportunity":TEAL,
                       "Core Market":GREEN,"Monitor":SUBTEXT}

        fig_risk = px.scatter(
            sdf, x="gmv", y="avg_review",
            size="order_count", color="risk_label",
            text="customer_state",
            color_discrete_map=RISK_COLORS,
            size_max=50,
            hover_name="customer_state",
            hover_data={"gmv":":.0f","avg_review":":.2f","order_count":True,"risk_label":False},
        )
        fig_risk.add_hline(y=overall_review, line_dash="dash",line_color=SUBTEXT,line_width=1)
        fig_risk.add_vline(x=med_gmv, line_dash="dash", line_color=SUBTEXT, line_width=1)
        fig_risk.update_traces(textposition="top center",
                               textfont=dict(color=TEXT,size=10,family="Inter"))
        chart_layout(fig_risk, height=420,
                     title="Revenue vs Review — quadrant risk classification")
        fig_risk.update_xaxes(title="State GMV (R$)", tickprefix="R$", tickformat=".2s")
        fig_risk.update_yaxes(title="Avg Review Score")
        st.plotly_chart(fig_risk, use_container_width=True)

    # ── QUARTERLY CATEGORY AREA ────────────────────────────────────
    sec("📅", "Quarterly GMV — Top 5 Categories")
    top5_cats = (df.groupby("product_category_name_english")["price"]
                 .sum().sort_values(ascending=False).head(5).index.tolist())
    qt = (df[df["product_category_name_english"].isin(top5_cats)]
          .groupby(["order_quarter","product_category_name_english"])["price"]
          .sum().reset_index())
    qt_pivot = qt.pivot(index="order_quarter", columns="product_category_name_english", values="price").fillna(0)
    qt_pivot = qt_pivot.sort_index()

    CAT_COLORS      = [ACCENT,   BLUE,    GREEN,   PURPLE,   TEAL]
    CAT_FILL_COLORS = [
        "rgba(249,115,22,0.55)",
        "rgba(59,130,246,0.55)",
        "rgba(16,185,129,0.55)",
        "rgba(139,92,246,0.55)",
        "rgba(20,184,166,0.55)",
    ]
    fig_qt = go.Figure()
    for i, cat in enumerate(top5_cats):
        if cat in qt_pivot.columns:
            fig_qt.add_trace(go.Scatter(
                x=qt_pivot.index, y=qt_pivot[cat],
                name=cat, mode="lines",
                stackgroup="one",
                line=dict(color=CAT_COLORS[i % len(CAT_COLORS)], width=1.5),
                fillcolor=CAT_FILL_COLORS[i % len(CAT_FILL_COLORS)],
                hovertemplate=f"<b>{cat}</b><br>%{{x}}<br>R$ %{{y:,.0f}}<extra></extra>",
            ))
    chart_layout(fig_qt, height=340, title="Quarterly GMV — Top 5 Categories (stacked area)")
    fig_qt.update_xaxes(tickangle=-30)
    fig_qt.update_yaxes(title="GMV (R$)", tickprefix="R$", tickformat=".2s")
    st.plotly_chart(fig_qt, use_container_width=True)

    # ── ORDER QUALITY FUNNEL ──────────────────────────────────────
    sec("🔻", "Order Quality Attrition Funnel")
    callout("This funnel shows where quality drops off. The largest single gap is between "
            "<b>Delivered On-Time</b> and <b>Total Delivered</b> — that gap <i>is</i> the late-delivery problem.")

    total_orders  = df["order_id"].nunique()
    total_del     = df[df["order_status"]=="delivered"]["order_id"].nunique()
    on_time_del   = df[(df["order_status"]=="delivered") & (df["is_late"]==0)]["order_id"].nunique()
    with_review   = df[df["review_score"].notna()]["order_id"].nunique()
    high_review   = df[df["review_score"] >= 4]["order_id"].nunique()

    stages  = ["Total Orders","Delivered","Delivered On Time","Review Received","Score ≥ 4.0"]
    values  = [total_orders, total_del, on_time_del, with_review, high_review]
    pcts    = [v / total_orders * 100 for v in values]
    f_colors= [ACCENT, BLUE, GREEN, PURPLE, TEAL]

    fig_funnel = go.Figure(go.Funnel(
        y=stages, x=values,
        textinfo="value+percent initial",
        marker=dict(color=f_colors, line=dict(color="rgba(0,0,0,.2)", width=1)),
        connector=dict(line=dict(color=BORDER, width=2)),
        hovertemplate="<b>%{y}</b><br>%{x:,} orders (%{percentInitial})<extra></extra>",
        textfont=dict(color="white", size=13, family="Inter"),
    ))
    chart_layout(fig_funnel, height=380, title="Order Quality Attrition Funnel",
                 showlegend=False)
    st.plotly_chart(fig_funnel, use_container_width=True)

    # Drop-off table
    drops = []
    for i in range(1, len(stages)):
        drop = values[i-1] - values[i]
        drops.append({
            "From → To": f"{stages[i-1]} → {stages[i]}",
            "Dropped": f"{drop:,}",
            "% Lost": f"{drop/values[i-1]*100:.1f}%",
            "Remaining": f"{values[i]:,} ({pcts[i]:.0f}% of total)",
        })
    st.dataframe(pd.DataFrame(drops), use_container_width=True, hide_index=True)

    # ── STRATEGIC OPPORTUNITIES TABLE ────────────────────────────
    sec("🎯", "Strategic State Priorities")
    sdf_full = (df.groupby("customer_state")
                .agg(gmv=("price","sum"),
                     orders=("order_id","nunique"),
                     avg_review=("review_score","mean"),
                     avg_delivery=("actual_delivery_days","mean"),
                     pct_late=("is_late","mean"))
                .reset_index().round(2))
    sdf_full["pct_late"] = (sdf_full["pct_late"] * 100).round(1)
    sdf_full["Risk Label"] = sdf_full.apply(
        lambda r: "🔴 At-Risk Revenue" if r["gmv"] > med_gmv and r["avg_review"] < overall_review
        else ("🟢 Core Market" if r["gmv"] > med_gmv else
              ("🔵 Growth Target" if r["avg_review"] >= overall_review else "🟡 Monitor")), axis=1)
    sdf_full.columns = ["State","GMV (R$)","Orders","Avg Review","Avg Del Days",
                         "% Late","Risk Label"]
    sdf_full = sdf_full.sort_values("GMV (R$)", ascending=False)
    st.dataframe(sdf_full.reset_index(drop=True), use_container_width=True, hide_index=True)

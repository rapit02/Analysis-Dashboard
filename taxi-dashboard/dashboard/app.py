# app.py — Main entry point

import streamlit as st
from data import load_data
from views import overview, demand, companies, payments, efficiency, kpi

st.set_page_config(
    page_title="Chicago Taxi Analytics 2020",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Base ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: visible;}
    [data-testid="stHeader"] {background: transparent;}

    [data-testid="stAppViewContainer"] {
        background: #080b14;
    }
    [data-testid="stMain"] {
        background: #080b14;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #080b14 100%);
        border-right: 1px solid rgba(45,106,159,0.3);
    }

    /* ── Metric cards ── */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #0d1117 0%, #141927 100%);
        border: 1px solid rgba(45,106,159,0.25);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.4);
        transition: border-color 0.2s;
    }

    [data-testid="metric-container"]:hover {
        border-color: rgba(45,106,159,0.6);
    }

    [data-testid="stMetricValue"] {
        font-size: 1.9rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.02em;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.72rem;
        color: #6b7a99;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* ── Typography ── */
    h1 {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #ffffff;
        padding-bottom: 4px;
    }

    h2 {
        font-size: 1.3rem;
        font-weight: 700;
        color: #e2e8f0;
        letter-spacing: -0.01em;
    }

    h3 {
        font-size: 1.1rem;
        font-weight: 600;
        color: #cbd5e1;
    }

    p, li, div {
        color: #94a3b8;
    }

    /* ── Info/warning boxes ── */
    [data-testid="stAlert"] {
        border-radius: 12px;
        border: none;
        background: linear-gradient(135deg, #0d1117 0%, #141927 100%);
        border-left: 3px solid #2d6a9f;
        color: #94a3b8;
    }

    /* ── Divider ── */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg,
            transparent 0%,
            rgba(45,106,159,0.4) 30%,
            rgba(45,106,159,0.4) 70%,
            transparent 100%
        );
        margin: 24px 0;
    }

    /* ── Selectbox and multiselect ── */
    [data-testid="stSelectbox"] > div,
    [data-testid="stMultiSelect"] > div {
        background: #0d1117;
        border: 1px solid rgba(45,106,159,0.3);
        border-radius: 10px;
        color: #ffffff;
    }

    /* ── Radio buttons ── */
    [data-testid="stRadio"] label {
        font-size: 0.88rem;
        color: #94a3b8;
        padding: 6px 10px;
        border-radius: 8px;
        transition: color 0.2s;
    }

    [data-testid="stRadio"] label:hover {
        color: #ffffff;
    }

    /* ── Caption ── */
    [data-testid="stCaptionContainer"] p {
        color: #4a5568;
        font-size: 0.78rem;
    }

    /* ── Plotly chart container ── */
    .js-plotly-plot {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(45,106,159,0.15);
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #080b14;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(45,106,159,0.4);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(45,106,159,0.7);
    }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 24px 0 16px 0;'>
        <div style='font-size: 2.8rem; margin-bottom: 8px;'>🚕</div>
        <div style='font-size: 1.1rem; font-weight: 800; color: #ffffff;
                    letter-spacing: -0.02em;'>
            Chicago Taxi
        </div>
        <div style='font-size: 0.75rem; color: #6b7a99;
                    text-transform: uppercase; letter-spacing: 0.08em;
                    margin-top: 4px;'>
            Analytics · 2020
        </div>
    </div>
    <div style='height: 1px; background: linear-gradient(90deg,
        transparent, rgba(45,106,159,0.4), transparent);
        margin-bottom: 20px;'></div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        options=[
            "📊 Overview",
            "⏰ Demand Patterns",
            "🏢 Company Performance",
            "💳 Payment Behaviour",
            "⚡ Operational Efficiency",
            "📈 CEO KPI — RPATD",
        ],
        label_visibility="collapsed",
    )

    st.markdown("""
    <div style='height: 1px; background: linear-gradient(90deg,
        transparent, rgba(45,106,159,0.4), transparent);
        margin: 20px 0;'></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='font-size: 0.72rem; color: #6b7a99;
                text-transform: uppercase; letter-spacing: 0.08em;
                margin-bottom: 12px; font-weight: 600;'>
        Filters
    </div>
    """, unsafe_allow_html=True)

    month_options = {
        "All Months": None,
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July (5 trips only)": 7,
    }
    selected_month_label = st.selectbox(
        "Month",
        options=list(month_options.keys()),
        label_visibility="collapsed",
    )
    selected_month = month_options[selected_month_label]

    all_companies = sorted(df["company"].dropna().unique().tolist())
    selected_companies = st.multiselect(
        "Companies",
        options=all_companies,
        default=all_companies,
        label_visibility="collapsed",
        placeholder="Select companies...",
    )

    st.markdown("""
    <div style='height: 1px; background: linear-gradient(90deg,
        transparent, rgba(45,106,159,0.4), transparent);
        margin: 20px 0;'></div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='font-size: 0.72rem; color: #4a5568; line-height: 2;'>
        <span style='color: #6b7a99;'>📅</span> Jan – Jun 2020<br>
        <span style='color: #6b7a99;'>🚕</span> {len(df):,} clean trips<br>
        <span style='color: #6b7a99;'>🏢</span> 6 operators<br>
        <span style='color: #6b7a99;'>🔧</span> pandas + DuckDB
    </div>
    """, unsafe_allow_html=True)

# ── Apply filters ─────────────────────────────────────────────────────────────
filtered_df = df.copy()

if selected_month is not None:
    filtered_df = filtered_df[filtered_df["month"] == selected_month]

if selected_companies:
    filtered_df = filtered_df[
        filtered_df["company"].isin(selected_companies)
    ]

# ── Route to pages ────────────────────────────────────────────────────────────
if page == "📊 Overview":
    overview.render(filtered_df)

elif page == "⏰ Demand Patterns":
    demand.render(filtered_df)

elif page == "🏢 Company Performance":
    companies.render(filtered_df)

elif page == "💳 Payment Behaviour":
    payments.render(filtered_df)

elif page == "⚡ Operational Efficiency":
    efficiency.render(filtered_df)

elif page == "📈 CEO KPI — RPATD":
    kpi.render(df)
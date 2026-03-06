# ==========================================
# HPCL COST INTELLIGENCE PLATFORM
# ==========================================

import sys
import os
import pandas as pd
import streamlit as st

# ---------- PATH SETUP ----------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ---------- SAFE MODULE IMPORTS ----------
import core.item_master as item_master
from core.data_loader import DataLoader
from core.repository import PriceRepository
from core.analytics import PriceAnalytics
from core.anomaly import AnomalyDetector
from core.vendor_comparison import VendorComparison

# ---------- CONFIG ----------
DATA_PATH = os.path.join(BASE_DIR, "synthetic_hpcl_po_data.csv")

st.set_page_config(
    page_title="HPCL Cost Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CACHING LAYERS ----------
@st.cache_data
def load_data(path):
    df = DataLoader(path).load()
    df["po_date"] = pd.to_datetime(df["po_date"])
    return df

@st.cache_data
def get_time_series(df, item_code):
    return PriceRepository(df).aggregate_time_series(item_code)

@st.cache_data
def get_vendor_comparison(df, item_code, year):
    return VendorComparison(df).compare(item_code, year)
@st.cache_data
def get_anomalies(df, item_code):
    return AnomalyDetector(df).detect(item_code)


# ---------- STYLING ----------
st.markdown(
    """
    <style>

    /* ---------- PAGE BACKGROUND ---------- */
    .stApp {
        background-color: #EEF1F5;
    }

    /* ---------- HEADER ---------- */
    .header-title {
        font-size: 30px;
        font-weight: 700;
        color: #0B2E59;
    }

    .header-subtitle {
        font-size: 15px;
        color: #4B5563;
        margin-bottom: 28px;
    }

    /* ---------- SECTION TITLES ---------- */
    .section-title {
        font-size: 17px;
        font-weight: 600;
        color: #1F2937;
        border-bottom: 2px solid #E5E7EB;
        padding-bottom: 6px;
        margin-bottom: 16px;
    }

    /* ---------- CARDS ---------- */
    .card {
        background-color: #FFFFFF;
        padding: 24px;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        margin-bottom: 28px;
    }

    /* ---------- SIDEBAR ---------- */
    section[data-testid="stSidebar"] {
        background-color: #0B2E59;
        border-right: 1px solid #0A2540;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #E5E7EB !important;
    }

    /* ---------- SIDEBAR INPUTS ---------- */
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] select {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border-radius: 6px !important;
        border: 1px solid #CBD5E1 !important;
    }

    /* Selected value text inside dropdown */
    section[data-testid="stSidebar"]
    div[data-baseweb="select"] span {
        color: #FFFFFF !important;
    }

    /* Dropdown arrow icon */
    section[data-testid="stSidebar"]
    div[data-baseweb="select"] svg {
        fill: #FFFFFF !important;
    }

    /* Dropdown selected value */
    section[data-testid="stSidebar"]
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #111827 !important;
    }

    /* Item Standardization output text */
    section[data-testid="stSidebar"]
    div[data-testid="stMarkdownContainer"] p {
        color: #E5E7EB !important;
        font-size: 13px;
        line-height: 1.5;
    }

    /* Inline code styling */
    section[data-testid="stSidebar"]
    div[data-testid="stMarkdownContainer"] code {
        background-color: rgba(255, 255, 255, 0.15);
        color: #FFFFFF !important;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 12px;
    }

    /* Strong labels */
    section[data-testid="stSidebar"]
    div[data-testid="stMarkdownContainer"] strong {
        color: #FFFFFF !important;
        font-weight: 600;
    }

    /* ---------- TABLES ---------- */
    thead tr th {
        background-color: #F3F4F6 !important;
        color: #111827 !important;
        font-weight: 600 !important;
    }

    /* ---------- TABS ---------- */
    button[data-baseweb="tab"] {
        font-size: 14px;
        font-weight: 500;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #0B2E59;
        border-bottom: 3px solid #0B2E59;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ---------- HEADER ----------
st.markdown("<div class='header-title'>HPCL Cost Intelligence Platform</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='header-subtitle'>Standardized procurement cost analysis, vendor comparison, forecasting and anomaly detection</div>",
    unsafe_allow_html=True
)

# ---------- LOAD DATA ----------
with st.spinner("Loading procurement data..."):
    df = load_data(DATA_PATH)

# ---------- SIDEBAR FILTERS ----------
st.sidebar.header("Filters")

item = st.sidebar.selectbox(
    "Item Code",
    sorted(df["item_code"].unique())
)

years = sorted(df["po_date"].dt.year.unique())
selected_year = st.sidebar.selectbox("Year", ["All"] + years)

st.sidebar.markdown("---")
st.sidebar.subheader("Item Standardization")

desc_input = st.sidebar.text_input("Item Description")

if desc_input:
    result = item_master.classify_item(desc_input)
    st.sidebar.markdown(f"""
    **Item Code:** `{result["item_code"]}`  
    **Canonical Description:** {result["canonical_desc"]}  
    **Confidence Score:** {round(result["confidence"], 3)}  
    **Status:** {result["status"]}
    """)

# ---------- FILTER DATA ----------
filtered_df = df[df["item_code"] == item]

if selected_year != "All":
    filtered_df = filtered_df[filtered_df["po_date"].dt.year == selected_year]

# ---------- TABS ----------
tab1, tab2, tab3, tab4 = st.tabs([
    "Cost Trends",
    "Vendor Comparison",
    "Forecasting",
    "Anomaly Detection"
])

# ---------- COST TRENDS ----------
with tab1:
    st.markdown("<div class='section-title'>Historical Price Trend</div>", unsafe_allow_html=True)

    with st.spinner("Generating time series..."):
        ts = get_time_series(filtered_df, item)

    st.line_chart(ts.tail(500))

# ---------- VENDOR COMPARISON ----------
with tab2:
    st.markdown(
        "<div class='section-title'>Vendor-wise Price Comparison</div>",
        unsafe_allow_html=True
    )

    with st.spinner("Comparing vendors..."):
        vendor_df = get_vendor_comparison(df, item, selected_year)

    if vendor_df is None or vendor_df.empty:
        st.info("No vendor comparison data available for this selection.")
    else:
        st.dataframe(vendor_df, use_container_width=True)


# ---------- FORECAST ----------
with tab3:
    st.markdown("<div class='section-title'>Price Forecast</div>", unsafe_allow_html=True)

    with st.spinner("Running forecast model..."):
        forecast = PriceAnalytics(ts).forecast()

    st.dataframe(forecast, use_container_width=True)

# ---------- ANOMALIES ----------
with tab4:
    st.markdown("<div class='section-title'>Price Anomaly Detection</div>", unsafe_allow_html=True)

    with st.spinner("Detecting anomalies..."):
        anomalies = get_anomalies(filtered_df, item)

    st.dataframe(anomalies, use_container_width=True)

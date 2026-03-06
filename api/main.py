import sys
import os

# =====================================================
# PATH SETUP (VERY IMPORTANT FOR STREAMLIT)
# =====================================================
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# =====================================================
# IMPORTS
# =====================================================
import streamlit as st
import pandas as pd

from core.data_loader import DataLoader
from core.repository import PriceRepository
from core.analytics import PriceAnalytics
from core.anomaly import AnomalyDetector
from core.vendor_comparison import VendorComparison

# =====================================================
# CONFIG
# =====================================================
DATA_PATH = os.path.join(os.path.dirname(__file__), "synthetic_hpcl_po_data.csv")

st.set_page_config(
    page_title="HPCL Cost Intelligence Dashboard",
    layout="wide"
)

st.title("🏭 HPCL Cost Intelligence Dashboard")

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data
def load_data():
    return DataLoader(DATA_PATH).load()

df = load_data()

# =====================================================
# SIDEBAR CONTROLS
# =====================================================
st.sidebar.header("Controls")

item_families = sorted(df["item_family"].dropna().unique())
selected_item = st.sidebar.selectbox(
    "Select Item Family",
    item_families
)

# =====================================================
# MAIN LAYOUT
# =====================================================
col1, col2 = st.columns(2)

# =====================================================
# PRICE TREND (TIME SERIES)
# =====================================================
with col1:
    st.subheader("📈 Price Trend Over Time")

    ts = PriceRepository(df).aggregate_time_series(selected_item)

    if ts.empty:
        st.warning("No price data available for this item.")
    else:
        st.line_chart(ts)

# =====================================================
# FORECAST
# =====================================================
with col2:
    st.subheader("🔮 Price Forecast")

    if not ts.empty:
        forecast = PriceAnalytics(ts).forecast()
        st.write(forecast)
    else:
        st.info("Forecast unavailable")

# =====================================================
# ANOMALIES
# =====================================================
st.subheader("🚨 Price Anomalies")

anomalies = AnomalyDetector(df).detect()

if anomalies.empty:
    st.success("No anomalies detected")
else:
    st.dataframe(anomalies)

# =====================================================
# VENDOR PRICE COMPARISON (YEAR-WISE)
# =====================================================
st.subheader("🧾 Vendor Price Comparison")

vc = VendorComparison(df)

years = vc.available_years()

if years:
    selected_year = st.selectbox(
        "Select Year",
        options=["All"] + years
    )
    year_filter = None if selected_year == "All" else selected_year
else:
    st.info("Year information not available")
    year_filter = None

vendor_table = vc.compare_vendors(selected_item, year_filter)

if vendor_table.empty:
    st.warning("No vendor data available for the selected item/year.")
else:
    st.dataframe(vendor_table)

    best_vendor = vc.best_vendor(selected_item, year_filter)
    spread = vc.price_spread(selected_item, year_filter)

    if best_vendor:
        col_a, col_b = st.columns(2)

        with col_a:
            st.metric(
                label="🏆 Best Vendor",
                value=best_vendor["vendor"],
                delta=f"Avg ₹{best_vendor['avg_price']}"
            )

        with col_b:
            st.metric(
                label="📊 Price Spread",
                value=f"{spread} %"
            )

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption(
    "Stage-3 Cost Intelligence: Price Trends • Forecasting • Anomalies • Vendor Benchmarking"
)

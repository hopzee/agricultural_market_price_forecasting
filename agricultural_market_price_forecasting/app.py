import streamlit as st
from src.ui import init_state, page_header

st.set_page_config(
    page_title="Agricultural Market Price Forecasting",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_state()

with st.sidebar:
    st.title("🌾 Price Forecast Lab")
    st.caption("Nigeria · Research forecasting system")
    st.divider()
    st.markdown("**Research scope**")
    st.caption("WFP Nigeria food-price observations")
    st.caption("Maize · Rice · Garri/cassava · Tomatoes")
    st.divider()
    st.markdown("**Models**")
    st.caption("SARIMAX · XGBoost · LightGBM")
    st.caption("Naïve / seasonal-naïve benchmark")
    st.divider()
    st.caption("Forecasts are estimates, not guaranteed future prices.")

page_header("Agricultural Market Price Forecasting", "A reproducible research workflow for Nigerian food-price time series.")
st.markdown("""
This application helps you move from the original WFP Nigeria food-price CSV to
clean monthly market-price series, historical analysis, chronological model
evaluation and future price forecasts.

**Start here:** open **Overview** and upload the WFP CSV. Then configure the
source columns in **Data Explorer** before running analysis or models.
""")
c1, c2, c3 = st.columns(3)
c1.metric("Geographic scope", "Nigeria")
c2.metric("Forecast target", "Market price")
c3.metric("Research models", "3 + benchmark")
st.info("No dataset is bundled with this application. Upload the actual WFP CSV; the system will not fabricate observations or model scores.")

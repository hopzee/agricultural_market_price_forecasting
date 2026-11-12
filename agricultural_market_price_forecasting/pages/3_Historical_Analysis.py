
import streamlit as st
import pandas as pd
import plotly.express as px

from src.ui import init_state, page_header
from src.data.preprocessing import series_profile

# Initialize session variables
init_state()

page_header(
    "Historical Analysis",
    "Explore observed monthly prices without mixing incompatible series."
)

monthly = st.session_state.monthly_df

if monthly is None or monthly.empty:
    st.warning("Prepare monthly data in Data Explorer first.")
    st.stop()

profile = series_profile(monthly)

if profile.empty:
    st.warning("No eligible monthly series were found.")
    st.stop()

key = st.selectbox(
    "Select an exact commodity-market-price series",
    profile.series_key.tolist()
)

g = monthly[monthly.series_key == key].copy()
g = g.sort_values("month")

if g.empty:
    st.warning("No observations are available for this series.")
    st.stop()

# Calculate missing calendar months
month_index = pd.date_range(
    start=g.month.min(),
    end=g.month.max(),
    freq="MS"
)

observed_months = pd.DatetimeIndex(
    pd.to_datetime(g.month).dt.to_period("M").dt.to_timestamp()
)

missing_months = len(
    month_index.difference(observed_months)
)

a, b, c = st.columns(3)

a.metric("Monthly observations", len(g))
b.metric("Missing months", missing_months)
c.metric("Median price", f"{g.price.median():,.2f}")

fig = px.line(
    g,
    x="month",
    y="price",
    markers=True,
    title="Monthly median observed price"
)

fig.update_layout(
    xaxis_title="Month",
    yaxis_title=f"Price ({g.currency.iloc[0]} / {g.unit.iloc[0]})"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Series details")

st.write({
    "Commodity group": g.commodity_group.iloc[0],
    "Original commodity label": g.commodity_original.iloc[0],
    "Market": g.market.iloc[0],
    "Price type": g.price_type.iloc[0],
    "Unit": g.unit.iloc[0],
    "Currency": g.currency.iloc[0],
    "Start": str(pd.to_datetime(g.month.min()).date()),
    "End": str(pd.to_datetime(g.month.max()).date())
})

st.subheader("Monthly observations")

st.dataframe(
    g[["month", "price", "observations"]],
    use_container_width=True
)

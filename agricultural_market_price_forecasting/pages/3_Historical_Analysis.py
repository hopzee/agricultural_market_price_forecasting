import streamlit as st
import pandas as pd
import plotly.express as px
from src.ui import page_header
from src.data.preprocessing import series_profile

page_header("Historical Analysis", "Explore observed monthly prices without mixing incompatible series.")
monthly = st.session_state.monthly_df
if monthly is None or monthly.empty:
    st.warning("Prepare monthly data in Data Explorer first."); st.stop()
profile = series_profile(monthly)
key = st.selectbox("Select an exact commodity-market-price series", profile.series_key.tolist())
g = monthly[monthly.series_key == key].sort_values("month")
a,b,c = st.columns(3)
a.metric("Monthly observations", len(g))
b.metric("Missing months", int(pd.date_range(g.month.min(),g.month.max(),freq="MS").difference(pd.DatetimeIndex(g.month)).size))
c.metric("Median price", f"{g.price.median():,.2f}")
fig = px.line(g, x="month", y="price", markers=True, title="Monthly median observed price")
fig.update_layout(xaxis_title="Month", yaxis_title=f"Price ({g.currency.iloc[0]} / {g.unit.iloc[0]})")
st.plotly_chart(fig, use_container_width=True)
st.subheader("Series details")
st.write({"Commodity group":g.commodity_group.iloc[0],"Original commodity label":g.commodity_original.iloc[0],
          "Market":g.market.iloc[0],"Price type":g.price_type.iloc[0],"Unit":g.unit.iloc[0],
          "Currency":g.currency.iloc[0],"Start":str(g.month.min().date()),"End":str(g.month.max().date())})
st.dataframe(g[["month","price","observations"]], use_container_width=True)

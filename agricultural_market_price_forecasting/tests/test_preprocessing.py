import pandas as pd
from src.data.preprocessing import prepare_data, aggregate_monthly

def test_preprocess_preserves_variant_and_aggregates_median():
    raw = pd.DataFrame({
        "date":["2022-01-02","2022-01-20","2022-02-01"],
        "commodity":["Maize white","Maize white","Rice local"],
        "market":["Market A"]*3,"unit":["KG"]*3,
        "price_type":["Retail"]*3,"price":[100,120,200],"currency":["NGN"]*3
    })
    mapping = {"date":"date","commodity":"commodity","market":"market","unit":"unit",
               "price_type":"price_type","price":"price","currency":"currency"}
    clean,_ = prepare_data(raw,mapping)
    monthly = aggregate_monthly(clean)
    maize = monthly[monthly.commodity_group=="Maize"].iloc[0]
    assert maize.price == 110
    assert maize.observations == 2
    assert monthly.series_key.nunique() == 2

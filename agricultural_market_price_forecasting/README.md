# Agricultural Market Price Forecasting System

A Python + Streamlit research application implementing the methodology in the supplied manuscript, **Development of a Predictive Analytics System for Agricultural Market Price Forecasting**.

## Research scope

- Geography: Nigeria
- Data source: supplied WFP Nigeria food-price CSV
- Commodity groups: maize, rice, garri/cassava products and tomatoes, subject to available records
- Target: reported agricultural market price
- Models: SARIMAX, XGBoost and LightGBM
- Benchmarks: naïve and seasonal-naïve where annual history is adequate
- Metrics: MAE, RMSE and MAPE (with zero-value handling)
- Evaluation: chronological training, validation and test; expanding-window one-step walk-forward evaluation; validation-based selection; held-out test reporting

This project does **not** forecast market arrivals, crop yield or consumer demand. It does not add weather, fuel, exchange-rate or other external variables.

## Run locally

Python 3.10–3.12 is recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Application workflow

1. **Overview** — upload the WFP CSV or an Excel copy.
2. **Data Explorer** — confirm source-column mappings, clean records and create monthly median series.
3. **Historical Analysis** — inspect one exact commodity/market/price-type/unit/currency series.
4. **Model Training & Evaluation** — compare benchmarks and models using chronological validation and a held-out test period.
5. **Price Forecasting** — generate future monthly estimates for a selected series.
6. **Reports & Downloads** — export prepared observations, predictions and metrics.
7. **System Information** — review assumptions and limitations.

## Important data rules

- The original uploaded table is not overwritten.
- Commodity variants are not merged merely because they share a broad group.
- Retail and wholesale records are separate.
- Incompatible units and currencies are separate.
- Monthly median is calculated within each exact series.
- Missing months are shown in the profile and are not silently interpolated.
- A model requires at least 48 continuous monthly observations for the current expanding-window train/validation/test design. Incomplete series are rejected rather than scored using invented values.
- MAPE excludes zero actual values; the valid MAPE count is shown.
- Model selection uses validation MAE. The test period is used for final reporting only.
- XGBoost and LightGBM are separate required dependencies. If either is unavailable, that model is reported as failed rather than silently replaced by another algorithm.

## Deployment on Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload all files and folders in this project.
3. Open Streamlit Community Cloud and create an app from that repository.
4. Set the main file path to `app.py`.
5. Deploy.

Do not upload private credentials or sensitive data to GitHub. Streamlit Community Cloud has ephemeral local storage; re-upload data after a restart unless a persistent storage layer is separately configured.

## Reproducibility and research reporting

No empirical results are bundled. The manuscript explicitly leaves the dataset profile and model-performance results pending until the final pipeline has been executed. Report only values produced from the actual WFP file and successful model runs.

## Project structure

```text
agricultural_market_price_forecasting/
├── app.py
├── pages/
├── src/
│   ├── data/
│   ├── features/
│   └── models/
├── config/
├── .streamlit/
├── tests/
├── requirements.txt
└── README.md
```

## Known limitations in this initial release

- The source schema is user-mapped because dataset exports may vary.
- Unit conversion is intentionally not automatic. The original unit is preserved.
- SARIMAX uses a transparent baseline order and seasonal period; systematic order search can be added after the first data audit.
- The tree-model training pipeline uses recursive multi-step forecasts.
- Session state is not a permanent model registry. Export results before closing or restarting the app.

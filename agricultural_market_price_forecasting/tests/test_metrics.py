import numpy as np
from src.models.forecasting import metrics

def test_mape_excludes_zero_actuals():
    result = metrics([0,100],[5,110])
    assert result["n"] == 2
    assert result["MAPE_n"] == 1
    assert result["MAPE"] == 10

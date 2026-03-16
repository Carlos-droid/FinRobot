import os
import requests
import pandas as pd
from functools import wraps
from typing import Annotated

from ..utils import decorate_all_methods


def init_marketstack_api(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global marketstack_api_key
        if os.environ.get("MARKETSTACK_API_KEY") is None:
            print("Please set the environment variable MARKETSTACK_API_KEY to use the Marketstack API.")
            return None
        else:
            marketstack_api_key = os.environ["MARKETSTACK_API_KEY"]
            return func(*args, **kwargs)

    return wrapper


@decorate_all_methods(init_marketstack_api)
class MarketStackUtils:

    def get_eod_data(
        ticker_symbol: Annotated[str, "ticker symbol (e.g., AAPL)"],
        limit: Annotated[int, "number of recent days to fetch, default is 30"] = 30,
    ) -> str:
        """Get the end-of-day (EOD) historical stock data for a given ticker from Marketstack."""
        url = f"http://api.marketstack.com/v1/eod"
        params = {
            "access_key": marketstack_api_key,
            "symbols": ticker_symbol,
            "limit": limit
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                df = pd.DataFrame(data["data"])
                # Filtrar solo columnas relevantes y mostrar como string
                columns_to_show = ["date", "open", "high", "low", "close", "volume"]
                df_filtered = df[[c for c in columns_to_show if c in df.columns]]
                return df_filtered.to_string()
            else:
                return "No data available."
        else:
            return f"Failed to retrieve data: {response.status_code} - {response.text}"

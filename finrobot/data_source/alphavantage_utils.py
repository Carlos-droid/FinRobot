import os
import requests
import pandas as pd
from functools import wraps
from typing import Annotated

from ..utils import decorate_all_methods


def init_alphavantage_api(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global alphavantage_api_key
        if os.environ.get("ALPHA_VANTAGE_API_KEY") is None:
            print("Please set the environment variable ALPHA_VANTAGE_API_KEY to use the Alpha Vantage API.")
            return None
        else:
            alphavantage_api_key = os.environ["ALPHA_VANTAGE_API_KEY"]
            return func(*args, **kwargs)

    return wrapper


@decorate_all_methods(init_alphavantage_api)
class AlphaVantageUtils:

    def get_global_quote(
        ticker_symbol: Annotated[str, "ticker symbol (e.g., AAPL)"],
    ) -> str:
        """Get the latest price and volume information (Global Quote) for a given ticker from Alpha Vantage."""
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": ticker_symbol,
            "apikey": alphavantage_api_key
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            if "Global Quote" in data and data["Global Quote"]:
                return str(data["Global Quote"])
            else:
                return f"No global quote data available. Response: {data}"
        else:
            return f"Failed to retrieve data: {response.status_code} - {response.text}"

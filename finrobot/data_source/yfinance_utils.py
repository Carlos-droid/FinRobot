import yfinance as yf
from typing import Annotated, Callable, Any, Optional
from pandas import DataFrame
from functools import wraps

from ..utils import save_output, SavePathType, decorate_all_methods


def init_ticker(func: Callable) -> Callable:
    """Decorator to initialize yf.Ticker and pass it to the function."""

    @wraps(func)
    def wrapper(symbol: Annotated[str, "ticker symbol"], *args, **kwargs) -> Any:
        ticker = yf.Ticker(symbol)
        return func(ticker, *args, **kwargs)

    return wrapper


@decorate_all_methods(init_ticker)
class YFinanceUtils:

    def get_stock_data(
        symbol: Annotated[str, "ticker symbol"],
        start_date: Annotated[
            str, "start date for retrieving stock price data, YYYY-mm-dd"
        ],
        end_date: Annotated[
            str, "end date for retrieving stock price data, YYYY-mm-dd"
        ],
        save_path: Optional[str] = None,
    ) -> DataFrame:
        """retrieve stock price data for designated ticker symbol"""
        ticker = symbol
        try:
            stock_data = ticker.history(start=start_date, end=end_date)
            save_output(stock_data, f"Stock data for {ticker.ticker}", save_path)
            return stock_data
        except Exception as e:
            print(f"Error fetching stock data for {ticker.ticker}: {e}")
            return DataFrame()

    def get_stock_info(
        symbol: Annotated[str, "ticker symbol"],
    ) -> dict:
        """Fetches and returns latest stock information."""
        ticker = symbol
        try:
            return ticker.info
        except Exception as e:
            print(f"Error fetching stock info for {ticker.ticker}: {e}")
            return {}

    def get_company_info(
        symbol: Annotated[str, "ticker symbol"],
        save_path: Optional[str] = None,
    ) -> DataFrame:
        """Fetches and returns company information as a DataFrame."""
        ticker = symbol
        try:
            info = ticker.info
            company_info = {
                "Company Name": info.get("shortName", "N/A"),
                "Industry": info.get("industry", "N/A"),
                "Sector": info.get("sector", "N/A"),
                "Country": info.get("country", "N/A"),
                "Website": info.get("website", "N/A"),
            }
            company_info_df = DataFrame([company_info])
            if save_path:
                company_info_df.to_csv(save_path)
                print(f"Company info for {ticker.ticker} saved to {save_path}")
            return company_info_df
        except Exception as e:
            print(f"Error fetching company info for {ticker.ticker}: {e}")
            return DataFrame()

    def get_stock_dividends(
        symbol: Annotated[str, "ticker symbol"],
        save_path: Optional[str] = None,
    ) -> DataFrame:
        """Fetches and returns the latest dividends data as a DataFrame."""
        ticker = symbol
        try:
            dividends = ticker.dividends
            if save_path:
                dividends.to_csv(save_path)
                print(f"Dividends for {ticker.ticker} saved to {save_path}")
            return dividends
        except Exception as e:
            print(f"Error fetching dividends for {ticker.ticker}: {e}")
            return DataFrame()

    def get_income_stmt(symbol: Annotated[str, "ticker symbol"]) -> DataFrame:
        """Fetches and returns the latest income statement of the company as a DataFrame."""
        ticker = symbol
        try:
            return ticker.financials
        except Exception as e:
            print(f"Error fetching income statement for {ticker.ticker}: {e}")
            return DataFrame()

    def get_balance_sheet(symbol: Annotated[str, "ticker symbol"]) -> DataFrame:
        """Fetches and returns the latest balance sheet of the company as a DataFrame."""
        ticker = symbol
        try:
            return ticker.balance_sheet
        except Exception as e:
            print(f"Error fetching balance sheet for {ticker.ticker}: {e}")
            return DataFrame()

    def get_cash_flow(symbol: Annotated[str, "ticker symbol"]) -> DataFrame:
        """Fetches and returns the latest cash flow statement of the company as a DataFrame."""
        ticker = symbol
        try:
            return ticker.cashflow
        except Exception as e:
            print(f"Error fetching cash flow for {ticker.ticker}: {e}")
            return DataFrame()

    def get_analyst_recommendations(symbol: Annotated[str, "ticker symbol"]) -> tuple:
        """Fetches the latest analyst recommendations and returns the most common recommendation and its count."""
        ticker = symbol
        try:
            recommendations = ticker.recommendations
            if recommendations.empty:
                return None, 0  # No recommendations available

            # Assuming 'period' column exists and needs to be excluded
            row_0 = recommendations.iloc[0, 1:]  # Exclude 'period' column if necessary

            # Find the maximum voting result
            max_votes = row_0.max()
            majority_voting_result = row_0[row_0 == max_votes].index.tolist()

            return majority_voting_result[0], max_votes
        except Exception as e:
            print(f"Error fetching analyst recommendations for {ticker.ticker}: {e}")
            return None, 0



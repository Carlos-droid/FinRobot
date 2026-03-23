import os
import json
import sqlite3
import pandas as pd
from datetime import date, timedelta, datetime
from functools import lru_cache, wraps
from typing import Annotated
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FinRobotCache")

CACHE_DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), "finrobot_cache.db")

class HybridCache:
    """
    Hybrid Cache System for FinRobot.
    Memory: functools.lru_cache for fast access during a session.
    Disk: SQLite for persistent historical data (OHLCV).
    """
    def __init__(self, db_path=CACHE_DB):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS historical_prices (
                    symbol TEXT,
                    date TEXT,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (symbol, date)
                )
            """)
            conn.commit()

    def get_historical_data(self, symbol, start_date, end_date):
        """Retrieve data from SQLite."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT date, open, high, low, close, volume 
                    FROM historical_prices 
                    WHERE symbol = ? AND date >= ? AND date <= ?
                    ORDER BY date
                """
                df = pd.read_sql_query(query, conn, params=(symbol, start_date, end_date), index_col="date")
                if not df.empty:
                    df.index = pd.to_datetime(df.index)
                    # Rename columns to match yfinance output
                    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                    return df
        except Exception as e:
            logger.error(f"Error reading from SQLite cache: {e}")
        return None

    def save_historical_data(self, symbol, df):
        """Save data to SQLite."""
        if df is None or df.empty:
            return
        try:
            # Flatten index if it's a DatetimeIndex
            df_to_save = df.copy()
            df_to_save['symbol'] = symbol
            df_to_save['date'] = df_to_save.index.strftime('%Y-%m-%d')
            
            with sqlite3.connect(self.db_path) as conn:
                for _, row in df_to_save.iterrows():
                    conn.execute("""
                        INSERT OR REPLACE INTO historical_prices (symbol, date, open, high, low, close, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (symbol, row['date'], row['Open'], row['High'], row['Low'], row['Close'], row['Volume']))
                conn.commit()
            logger.debug(f"Cached {len(df_to_save)} records for {symbol} in SQLite.")
        except Exception as e:
            logger.error(f"Error saving to SQLite cache: {e}")

def persistent_cache(func):
    """Decorator to apply hybrid cache to yfinance data retrieval."""
    cache = HybridCache()

    @wraps(func)
    def wrapper(symbol, start_date, end_date, *args, **kwargs):
        # Determine effective symbol (if it's a yf.Ticker object passed by init_ticker)
        effective_symbol = symbol.ticker if hasattr(symbol, 'ticker') else symbol
        
        # 1. Check Disk Cache (SQLite)
        cached_df = cache.get_historical_data(effective_symbol, start_date, end_date)
        
        if cached_df is not None and not cached_df.empty:
            last_date = cached_df.index.max().strftime('%Y-%m-%d')
            # If we have enough data or it's recent enough
            if last_date >= end_date:
                logger.info(f"Cache HIT for {effective_symbol} ({start_date} to {end_date})")
                return cached_df

        # 2. Cache MISS: Call original function
        logger.info(f"Cache MISS for {effective_symbol}. Fetching from API...")
        df = func(symbol, start_date, end_date, *args, **kwargs)
        
        # 3. Save to Disk Cache
        if df is not None and not df.empty:
            cache.save_historical_data(effective_symbol, df)
            
        return df

    return wrapper

def memory_cache(func):
    return lru_cache(maxsize=128)(func)



# Define custom annotated types
# VerboseType = Annotated[bool, "Whether to print data to console. Default to True."]
SavePathType = Annotated[str, "File path to save data. If None, data is not saved."]


# def process_output(data: pd.DataFrame, tag: str, verbose: VerboseType = True, save_path: SavePathType = None) -> None:
#     if verbose:
#         print(data.to_string())
#     if save_path:
#         data.to_csv(save_path)
#         print(f"{tag} saved to {save_path}")


def save_output(data: pd.DataFrame, tag: str, save_path: SavePathType = None) -> None:
    if save_path:
        data.to_csv(save_path)
        print(f"{tag} saved to {save_path}")


def get_current_date():
    return date.today().strftime("%Y-%m-%d")


def register_keys_from_json(file_path):
    with open(file_path, "r") as f:
        keys = json.load(f)
    for key, value in keys.items():
        os.environ[key] = value


def decorate_all_methods(decorator):
    def class_decorator(cls):
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value):
                setattr(cls, attr_name, decorator(attr_value))
        return cls

    return class_decorator


def get_next_weekday(date):

    if not isinstance(date, datetime):
        date = datetime.strptime(date, "%Y-%m-%d")

    if date.weekday() >= 5:
        days_to_add = 7 - date.weekday()
        next_weekday = date + timedelta(days=days_to_add)
        return next_weekday
    else:
        return date


# def create_inner_assistant(
#         name, system_message, llm_config, max_round=10,
#         code_execution_config=None
#     ):

#     inner_assistant = autogen.AssistantAgent(
#         name=name,
#         system_message=system_message + "Reply TERMINATE when the task is done.",
#         llm_config=llm_config,
#         is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
#     )
#     executor = autogen.UserProxyAgent(
#         name=f"{name}-executor",
#         human_input_mode="NEVER",
#         code_execution_config=code_execution_config,
#         default_auto_reply="",
#         is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
#     )
#     assistant.register_nested_chats(
#         [{"recipient": assistant, "message": reflection_message, "summary_method": "last_msg", "max_turns": 1}],
#         trigger=ConversableAgent
#         )
#     return manager

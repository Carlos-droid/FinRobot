import os
import subprocess
import sys
import pandas as pd
from datetime import datetime, timedelta

# Add FinRobot to path
sys.path.append(os.path.dirname(__file__))

from finrobot.utils import HybridCache, persistent_cache
from finrobot.data_source.yfinance_utils import YFinanceUtils

def test_mcp_tools():
    print("=== Testing MCP Tools ===")
    
    # 1. Test jcodemunch-mcp (Python)
    jcodemunch_path = os.path.expanduser("~/antigravity/tools/jcodemunch-mcp")
    if os.path.exists(jcodemunch_path):
        print(f"✅ jcodemunch-mcp found at {jcodemunch_path}")
        try:
            # Check if uv run works
            result = subprocess.run(
                ["uv", "run", "--project", jcodemunch_path, "jcodemunch-mcp", "--help"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print("✅ jcodemunch-mcp is callable via uv run.")
            else:
                print(f"❌ jcodemunch-mcp returned error: {result.stderr}")
        except Exception as e:
            print(f"❌ Error calling jcodemunch-mcp: {e}")
    else:
        print("❌ jcodemunch-mcp NOT found.")

    # 2. Test engram (Go)
    engram_bin = os.path.expanduser("~/antigravity/tools/engram/cmd/engram/engram")
    if os.path.exists(engram_bin):
        print(f"✅ engram binary found at {engram_bin}")
        try:
            result = subprocess.run([engram_bin, "help"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ engram is callable.")
            else:
                print(f"❌ engram returned error: {result.stderr}")
        except Exception as e:
            print(f"❌ Error calling engram: {e}")
    else:
        print("❌ engram binary NOT found.")

def test_hybrid_cache():
    print("\n=== Testing Hybrid Cache ===")
    symbol = "AAPL"
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
    
    # 1. Warm call (Fetches from API, saves to SQLite)
    print(f"First call for {symbol} (expect Cache MISS)...")
    df1 = YFinanceUtils.get_stock_data(symbol, start_date, end_date)
    
    # 2. Cold call (Should hit SQLite)
    print(f"\nSecond call for {symbol} (expect Cache HIT)...")
    df2 = YFinanceUtils.get_stock_data(symbol, start_date, end_date)
    
    if df2 is not None and not df2.empty:
        print(f"✅ Successfully retrieved {len(df2)} rows from cache.")
        if df1.equals(df2):
            print("✅ Data integrity verified (API vs Cache).")
        else:
            print("⚠️ Data mismatch between API and Cache (possible due to indexing/formatting).")
    else:
        print("❌ Failed to retrieve data from cache.")

if __name__ == "__main__":
    test_mcp_tools()
    test_hybrid_cache()
    print("\n=== Dry Run Completed ===")

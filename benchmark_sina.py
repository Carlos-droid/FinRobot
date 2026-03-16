import time
import pandas as pd
import numpy as np
import json
from unittest.mock import MagicMock
from finnlp.data_sources.news.sina_finance_date_range import Sina_Finance_Date_Range

def benchmark_sina_finance_date_range():
    downloader = Sina_Finance_Date_Range()

    # Mocking _request_get to return dummy data
    def mock_request_get(url, headers=None, verify=None, params=None):
        mock_res = MagicMock()
        mock_res.status_code = 200

        # Create 50 dummy records
        data = []
        for i in range(50):
            data.append({
                "title": f"Title {i}",
                "url": f"http://finance.sina.com.cn/{i}",
                "ctime": 1672531200 + i,
                "mtime": 1672531200 + i,
                "intime": 1672531200 + i,
                "other_field": "some data"
            })

        mock_res.text = json.dumps({
            "result": {
                "data": data
            }
        })
        return mock_res

    downloader._request_get = mock_request_get

    # We will test _gather_one_day for 20 pages to see the impact
    # To make it faster during benchmark, we'll set delay to 0

    start_time = time.time()
    # In the original code, it goes up to 100 pages, and each page has num=50 items.
    # Total items = 50 * 100 = 5000.
    # But for benchmarking we can just run it.

    # Patch the loop to stop after N pages to make benchmark faster if needed,
    # but let's try 100 pages first.

    # We need to mock the break condition too if we want it to finish 100 pages
    # The current mock always returns 50 items, so it will go up to 100 pages.

    print("Starting benchmark for _gather_one_day...")
    res = downloader._gather_one_day("2023-01-01", delay=0)
    end_time = time.time()

    print(f"Time taken for _gather_one_day (100 pages, 5000 items): {end_time - start_time:.4f} seconds")
    print(f"Result shape: {res.shape}")

    # Now let's test download_date_range_all for 10 days
    print("\nStarting benchmark for download_date_range_all (10 days)...")
    start_time = time.time()
    downloader.download_date_range_all("2023-01-01", "2023-01-10")
    end_time = time.time()
    print(f"Time taken for download_date_range_all (10 days): {end_time - start_time:.4f} seconds")
    print(f"Total dataframe shape: {downloader.dataframe.shape}")

if __name__ == "__main__":
    benchmark_sina_finance_date_range()

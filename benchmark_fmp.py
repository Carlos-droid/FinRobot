import time
import os
import requests
from unittest.mock import patch
from finrobot.data_source.fmp_utils import FMPUtils

def mock_get(*args, **kwargs):
    time.sleep(0.1)  # Simulate 100ms API latency
    class MockResponse:
        def __init__(self, data):
            self.data = data
            self.status_code = 200
        def json(self):
            return self.data

    # Mock data structure required by the functions
    mock_data = [{
        "date": f"202{i}-12-31",
        "revenue": 100000000,
        "grossProfit": 50000000,
        "ebitda": 20000000,
        "ebitdaratio": 0.2,
        "netIncome": 10000000,
        "enterpriseValue": 200000000,
        "evToOperatingCashFlow": 10,
        "roic": 0.15,
        "enterpriseValueOverEBITDA": 10,
        "priceEarningsRatio": 20,
        "pbRatio": 5
    } for i in range(10, -1, -1)]

    return MockResponse(mock_data)

@patch('requests.get', side_effect=mock_get)
@patch.dict(os.environ, {"FMP_API_KEY": "mock_api_key"})
def benchmark(mock_requests_get):
    print("Benchmarking FMPUtils.get_financial_metrics...")
    start_time = time.time()

    try:
        FMPUtils.get_financial_metrics("AAPL", years=4)
    except Exception as e:
        print(f"Exception during run: {e}")

    end_time = time.time()
    duration = end_time - start_time
    call_count = mock_requests_get.call_count

    print(f"Execution time: {duration:.4f} seconds")
    print(f"API calls made: {call_count}")
    return duration, call_count

if __name__ == "__main__":
    benchmark()

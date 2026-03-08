import timeit
import re

# Simulate the current implementation
def current_get_year(filing_type, filing_details):
    details = filing_details.split("/")[-1]
    matches = None
    if filing_type == "10-K":
        matches = re.findall("20\d{2}", details)
    elif filing_type == "10-Q":
        matches = re.findall("20\d{4}", details)

    if matches:
        return matches[-1]
    else:
        return None

# Pre-compiled regexes
YEAR_PATTERN_10K = re.compile(r"20\d{2}")
YEAR_PATTERN_10Q = re.compile(r"20\d{4}")

# Simulate the optimized implementation
def optimized_get_year(filing_type, filing_details):
    details = filing_details.split("/")[-1]
    matches = None
    if filing_type == "10-K":
        matches = YEAR_PATTERN_10K.findall(details)
    elif filing_type == "10-Q":
        matches = YEAR_PATTERN_10Q.findall(details)

    if matches:
        return matches[-1]
    else:
        return None

if __name__ == "__main__":
    test_data_10k = "https://www.sec.gov/Archives/edgar/data/320193/000032019321000105/aapl-20210925.htm"
    test_data_10q = "https://www.sec.gov/Archives/edgar/data/320193/000032019322000059/aapl-20220326.htm"

    # Warm up caches
    current_get_year("10-K", test_data_10k)
    current_get_year("10-Q", test_data_10q)
    optimized_get_year("10-K", test_data_10k)
    optimized_get_year("10-Q", test_data_10q)

    # Number of iterations
    N = 500000

    print("Measuring current implementation (10-K)...")
    time_current_10k = timeit.timeit(lambda: current_get_year("10-K", test_data_10k), number=N)

    print("Measuring current implementation (10-Q)...")
    time_current_10q = timeit.timeit(lambda: current_get_year("10-Q", test_data_10q), number=N)

    print("Measuring optimized implementation (10-K)...")
    time_optimized_10k = timeit.timeit(lambda: optimized_get_year("10-K", test_data_10k), number=N)

    print("Measuring optimized implementation (10-Q)...")
    time_optimized_10q = timeit.timeit(lambda: optimized_get_year("10-Q", test_data_10q), number=N)

    print("\n--- Results (N={}) ---".format(N))
    print(f"Current (10-K): {time_current_10k:.4f} seconds")
    print(f"Current (10-Q): {time_current_10q:.4f} seconds")
    print(f"Total Current: {(time_current_10k + time_current_10q):.4f} seconds")
    print(f"Optimized (10-K): {time_optimized_10k:.4f} seconds")
    print(f"Optimized (10-Q): {time_optimized_10q:.4f} seconds")
    print(f"Total Optimized: {(time_optimized_10k + time_optimized_10q):.4f} seconds")

    improvement_10k = (time_current_10k - time_optimized_10k) / time_current_10k * 100
    improvement_10q = (time_current_10q - time_optimized_10q) / time_current_10q * 100
    total_improvement = ((time_current_10k + time_current_10q) - (time_optimized_10k + time_optimized_10q)) / (time_current_10k + time_current_10q) * 100

    print(f"\nImprovement 10-K: {improvement_10k:.2f}%")
    print(f"Improvement 10-Q: {improvement_10q:.2f}%")
    print(f"Total Improvement: {total_improvement:.2f}%")

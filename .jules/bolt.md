
### sec_filings.py Performance Optimization
*   **Anti-pattern:** Using `re.findall("pattern", text)` with string literals repeatedly inside a function like `get_year`.
*   **Optimization:** Pre-compiling regexes as module-level constants (e.g., `_YEAR_PATTERN_10K = re.compile(r"20\d{2}")`) and using their `.findall()` methods.
*   **Impact:** Reduces function execution time by approximately ~30% for 500,000 iterations according to local `benchmark_regex.py`.

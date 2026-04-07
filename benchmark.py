import time
import os
import json
import pdfkit
from concurrent.futures import ThreadPoolExecutor, as_completed

# Mock pdfkit.from_url to simulate IO behavior because SEC blocks
# wkhtmltopdf user agents during non-browser requests
def mock_from_url(url, path, options=None):
    # Simulate the time it takes to convert a single HTML to PDF
    time.sleep(2.0)
    with open(path, "w") as f:
        f.write("Mock PDF content")

pdfkit.from_url = mock_from_url

def _convert_html_to_pdfs_baseline(html_urls, base_path: str):
    metadata_json = {}
    for html_url in html_urls:
        pdf_path = html_url[0].split("/")[-1]
        pdf_path = pdf_path.replace(".htm", f"-{html_url[1]}.pdf")
        pdf_path = pdf_path.replace("10-K/A", "10-KA")
        metadata_json[pdf_path] = {"languages": ["English"]}
        pdf_path = os.path.join(base_path, pdf_path)
        pdfkit.from_url(html_url[0], pdf_path)
    return metadata_json

def _convert_html_to_pdfs_optimized(html_urls, base_path: str):
    metadata_json = {}

    def process_url(html_url):
        try:
            pdf_path = html_url[0].split("/")[-1]
            pdf_path = pdf_path.replace(".htm", f"-{html_url[1]}.pdf")
            pdf_path = pdf_path.replace("10-K/A", "10-KA")
            full_pdf_path = os.path.join(base_path, pdf_path)

            # Synchronous blocking call
            options = {
                "custom-header": [
                    ("User-Agent", "Indiana-University-Bloomington athecolab@gmail.com")
                ]
            }
            pdfkit.from_url(html_url[0], full_pdf_path, options=options)
            return pdf_path, {"languages": ["English"]}
        except Exception as e:
            print(f"Error processing {html_url[0]}: {e}")
            return None, None

    # Using max_workers=5 to respect rate limits and memory
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(process_url, url): url for url in html_urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                pdf_path, meta = future.result()
                if pdf_path and meta:
                    metadata_json[pdf_path] = meta
            except Exception as exc:
                print(f"{url} generated an exception: {exc}")

    return metadata_json

if __name__ == "__main__":
    # Sample SEC EDGAR URLs for benchmarking
    test_urls = [
        ["https://www.sec.gov/Archives/edgar/data/320193/000032019323000106/aapl-20230930.htm", "10-K"],
        ["https://www.sec.gov/Archives/edgar/data/320193/000032019323000064/aapl-20230401.htm", "10-Q"],
        ["https://www.sec.gov/Archives/edgar/data/320193/000032019323000077/aapl-20230701.htm", "10-Q"],
        ["https://www.sec.gov/Archives/edgar/data/320193/000032019323000078/aapl-20230801.htm", "10-Q"],
        ["https://www.sec.gov/Archives/edgar/data/320193/000032019323000079/aapl-20230901.htm", "10-Q"],
    ]

    base_dir = "test_benchmark_output"
    os.makedirs(base_dir, exist_ok=True)

    print(f"Benchmarking with {len(test_urls)} URLs (Each URL simulated to take 2.0s conversion time)...\n")

    print("Running baseline (synchronous)...")
    start = time.time()
    _convert_html_to_pdfs_baseline(test_urls, base_dir)
    baseline_time = time.time() - start
    print(f"Baseline Time: {baseline_time:.2f} seconds")

    print("\nRunning optimized (ThreadPoolExecutor)...")
    start = time.time()
    _convert_html_to_pdfs_optimized(test_urls, base_dir)
    optimized_time = time.time() - start
    print(f"Optimized Time: {optimized_time:.2f} seconds")

    print(f"\nImprovement: {baseline_time / optimized_time:.2f}x faster")

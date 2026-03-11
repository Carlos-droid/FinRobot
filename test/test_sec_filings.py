import pytest
from finrobot.data_source.filings_src.sec_filings import SECExtractor

class TestSECExtractor:
    @pytest.fixture
    def extractor(self):
        # Instantiate extractor with required parameters
        return SECExtractor(ticker="AAPL")

    @pytest.mark.parametrize(
        "filing_type, filing_details, expected_result",
        [
            # Happy path: 10-K correctly matching a year
            ("10-K", "https://www.sec.gov/Archives/edgar/data/320193/000032019321000105/aapl-20210925.htm", "2021"),
            # Happy path: 10-K correctly picking the first match among multiple
            ("10-K", "https://www.sec.gov/Archives/edgar/data/320193/aapl-20220924_2023.htm", "2022"),
            # Happy path: 10-Q correctly matching year-month (four digits following 20)
            ("10-Q", "https://www.sec.gov/Archives/edgar/data/320193/000032019322000059/aapl-20220326.htm", "202203"),
            # Empty string or no numbers
            ("10-K", "https://www.sec.gov/Archives/edgar/data/aapl.htm", None),
            ("10-Q", "https://www.sec.gov/Archives/edgar/data/aapl.htm", None),
            # Missing filing_type or unsupported type
            ("8-K", "https://www.sec.gov/Archives/edgar/data/320193/000032019321000105/aapl-20210925.htm", None),
            (None, "https://www.sec.gov/Archives/edgar/data/320193/000032019321000105/aapl-20210925.htm", None),
        ]
    )
    def test_get_year(self, extractor, filing_type, filing_details, expected_result):
        # Set the filing_type on the extractor instance as it typically happens externally
        if filing_type is not None:
            extractor.filing_type = filing_type

        result = extractor.get_year(filing_details)
        assert result == expected_result

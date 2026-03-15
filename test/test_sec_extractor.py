import pytest
from finrobot.data_source.filings_src.sec_filings import SECExtractor

class TestSECExtractor:
    def test_get_year_10k_standard(self):
        # Arrange
        extractor = SECExtractor("AAPL")
        extractor.filing_type = "10-K"
        url = "/Archives/edgar/data/320193/000032019323000064/aapl-20230930.htm"

        # Act
        result = extractor.get_year(url)

        # Assert
        assert result == "2023"

    def test_get_year_10k_multiple_matches(self):
        # Arrange
        extractor = SECExtractor("AAPL")
        extractor.filing_type = "10-K"
        url = "/data/202299/20230930/aapl-20230930.htm"

        # Act
        result = extractor.get_year(url)

        # Assert
        assert result == "2023"  # should get the last one

    def test_get_year_10q_standard(self):
        # Arrange
        extractor = SECExtractor("AAPL")
        extractor.filing_type = "10-Q"
        url = "/Archives/edgar/data/320193/000032019323000064/aapl-202306.htm"

        # Act
        result = extractor.get_year(url)

        # Assert
        assert result == "202306"

    def test_get_year_missing_match(self):
        # Arrange
        extractor = SECExtractor("AAPL")
        extractor.filing_type = "10-K"
        url = "this_is_a_garbage_string_with_no_year.htm"

        # Act
        result = extractor.get_year(url)

        # Assert
        assert result is None

    def test_get_year_missing_filing_type(self):
        # Arrange
        extractor = SECExtractor("AAPL")
        # No filing_type set
        url = "/Archives/edgar/data/320193/000032019323000064/aapl-20230930.htm"

        # Act
        result = extractor.get_year(url)

        # Assert
        assert result is None

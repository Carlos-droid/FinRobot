import pytest
from unittest.mock import patch, MagicMock
from finrobot.data_source.filings_src.sec_filings import SECExtractor

def test_pipeline_api_invalid_filing_type():
    # Arrange
    extractor = SECExtractor(ticker="AAPL")
    dummy_text = "<HTML>dummy SEC document</HTML>"

    # We will mock SECDocument.from_string to return an object with an invalid filing_type
    mock_sec_document = MagicMock()
    mock_sec_document.filing_type = "INVALID-TYPE"

    with patch('finrobot.data_source.filings_src.sec_filings.SECDocument.from_string', return_value=mock_sec_document):
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            extractor.pipeline_api(dummy_text)

        # Optional: assert the error message is correct
        assert "SEC document filing type INVALID-TYPE is not supported" in str(exc_info.value)

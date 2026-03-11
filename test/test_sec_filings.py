import pytest
from unittest.mock import MagicMock
from finrobot.data_source.filings_src.sec_filings import SECExtractor

@pytest.fixture
def sec_extractor():
    """Returns an instance of SECExtractor with mocked dependencies."""
    return SECExtractor(ticker="AAPL")

@pytest.mark.parametrize(
    "section, all_narratives, expected",
    [
        # Happy Path: multiple elements with 'text' key concatenated with space
        (
            "Item 1",
            {"Item 1": [{"text": "Hello"}, {"text": "World!"}]},
            "Hello World!"
        ),
        # Happy Path: Single element
        (
            "Item 1A",
            {"Item 1A": [{"text": "Risk Factors."}]},
            "Risk Factors."
        ),
        # Edge Case: empty list for section
        (
            "Item 2",
            {"Item 2": []},
            ""
        ),
        # Edge Case: dictionaries without 'text' key
        (
            "Item 3",
            {"Item 3": [{"other_key": "No text here"}, {"text": "Only this text"}]},
            "Only this text"
        ),
        # Edge Case: no dictionaries have 'text' key
        (
            "Item 4",
            {"Item 4": [{"other_key": "Nothing"}, {"another_key": "Nope"}]},
            ""
        ),
        # Edge Case: missing section
        (
            "Item 5",
            {"Item 1": [{"text": "Hello"}]},
            ""
        )
    ]
)
def test_get_all_text(sec_extractor, section, all_narratives, expected):
    """Test get_all_text with different edge cases and happy paths."""
    result = sec_extractor.get_all_text(section, all_narratives)
    assert result == expected

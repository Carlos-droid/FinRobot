import pytest
from unittest.mock import patch, Mock
from tenacity import RetryError
from concurrent.futures import Future
from langchain.schema import Document
from finrobot.data_source.earnings_calls_src.main_earningsData import get_earnings_all_docs

# Helper to create a realistic-looking RetryError
def create_retry_error():
    mock_future = Mock(spec=Future)
    return RetryError(last_attempt=mock_future)

@pytest.fixture
def mock_docs_and_speakers():
    # Helper to return generic success data
    docs = [Document(page_content="Some content", metadata={"speaker": "Speaker 1", "quarter": "Q"})]
    speakers = ["Speaker 1"]
    return docs, speakers

@pytest.mark.parametrize(
    "side_effect_list, expected_quarters, expected_output_msgs",
    [
        # Scenario 1: Q1 fails, Q2-Q4 succeed
        (
            [
                create_retry_error(), # Q1 fails
                ([Document(page_content="Q2 doc", metadata={"speaker": "Spk2", "quarter": "Q2"})], ["Spk2"]), # Q2 succeeds
                ([Document(page_content="Q3 doc", metadata={"speaker": "Spk3", "quarter": "Q3"})], ["Spk3"]), # Q3 succeeds
                ([Document(page_content="Q4 doc", metadata={"speaker": "Spk4", "quarter": "Q4"})], ["Spk4"])  # Q4 succeeds
            ],
            ["Q2", "Q3", "Q4"],
            ["Don't have the data for Q1"]
        ),
        # Scenario 2: All quarters fail
        (
            [
                create_retry_error(), # Q1 fails
                create_retry_error(), # Q2 fails
                create_retry_error(), # Q3 fails
                create_retry_error()  # Q4 fails
            ],
            [],
            [
                "Don't have the data for Q1",
                "Don't have the data for Q2",
                "Don't have the data for Q3",
                "Don't have the data for Q4"
            ]
        )
    ],
    ids=["q1_fails_others_succeed", "all_quarters_fail"]
)
@patch("finrobot.data_source.earnings_calls_src.main_earningsData.get_earnings_all_quarters_data")
def test_get_earnings_all_docs_retry_error(
    mock_get_data, capsys, side_effect_list, expected_quarters, expected_output_msgs
):
    # Setup mock behavior
    mock_get_data.side_effect = side_effect_list

    # Call the function
    ticker = "AAPL"
    year = 2023
    result = get_earnings_all_docs(ticker, year)

    # Unpack results
    (
        earnings_docs,
        earnings_call_quarter_vals,
        speakers_list_1,
        speakers_list_2,
        speakers_list_3,
        speakers_list_4,
    ) = result

    # Verify return values
    assert earnings_call_quarter_vals == expected_quarters

    # Check speakers lists length depending on the scenario
    # If a quarter failed, its speakers list should be empty []
    assert speakers_list_1 == ([] if isinstance(side_effect_list[0], Exception) else side_effect_list[0][1])
    assert speakers_list_2 == ([] if isinstance(side_effect_list[1], Exception) else side_effect_list[1][1])
    assert speakers_list_3 == ([] if isinstance(side_effect_list[2], Exception) else side_effect_list[2][1])
    assert speakers_list_4 == ([] if isinstance(side_effect_list[3], Exception) else side_effect_list[3][1])

    # Check stdout
    captured = capsys.readouterr()
    for msg in expected_output_msgs:
        assert msg in captured.out

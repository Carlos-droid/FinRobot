import pytest
from finrobot.data_source.earnings_calls_src.main_earningsData import clean_speakers

@pytest.mark.parametrize("input_speaker, expected_output", [
    # Basic cases (existing behavior + stripping)
    ("John Doe\n", "John Doe"),
    ("Jane Smith:", "Jane Smith"),
    ("Bob\n:", "Bob"),

    # Defensive programming: Type handling
    (None, ""),
    (12345, "12345"),
    (12.34, "12.34"),

    # Real-world edge cases from transcripts
    ("John Doe (CEO)", "John Doe"),
    ("Jane Smith (Managing Director) (Analyst)", "Jane Smith"),
    ("  Dr. Robert Smith  ", "Dr. Robert Smith"),
    ("Mr. John A. Doe, Jr.", "Mr. John A. Doe, Jr."),

    # Combined complex cases
    ("  Alice (VP)\n: ", "Alice"),
    ("Bob (CTO) \n (Interim CEO):", "Bob")
])
def test_clean_speakers(input_speaker, expected_output):
    assert clean_speakers(input_speaker) == expected_output

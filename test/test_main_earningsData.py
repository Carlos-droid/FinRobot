import pytest
from finrobot.data_source.earnings_calls_src.main_earningsData import clean_speakers

@pytest.mark.parametrize(
    "input_speaker, expected",
    [
        # Original behavior
        ("John Doe:\n", "John Doe"),

        # Titles in parentheses
        ("John Doe (CEO)", "John Doe"),

        # Multiple parentheses
        ("Jane Smith (Managing Director) (Analyst)", "Jane Smith"),

        # Excessive whitespace
        ("  Dr. Robert Smith  ", "Dr. Robert Smith"),

        # Names with initials or prefixes
        ("Mr. John A. Doe", "Mr. John A. Doe"),

        # Special characters (apostrophes, hyphens)
        ("O'Connor", "O'Connor"),
        ("Jean-Pierre", "Jean-Pierre"),

        # Non-string types (None and Integers)
        (None, ""),
        (12345, "12345"),

        # Combined cases (spaces, newlines, colons, parentheses)
        ("\n  Jane-Doe (CFO):  ", "Jane-Doe")
    ]
)
def test_clean_speakers(input_speaker, expected):
    assert clean_speakers(input_speaker) == expected

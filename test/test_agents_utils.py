import pytest
from unittest.mock import MagicMock
from finrobot.agents.utils import instruction_trigger

@pytest.fixture
def mock_sender():
    return MagicMock()

@pytest.mark.parametrize(
    "last_message_return, expected",
    [
        # Happy path: exact string present
        ({"content": "instruction & resources saved to /path/to/file"}, True),
        # Case sensitivity (trigger string is exact case, if it differs it returns False)
        ({"content": "INSTRUCTION & RESOURCES SAVED TO /path/to/file"}, False),
        # Trigger string is part of a longer sentence
        ({"content": "The final instruction & resources saved to the disk successfully."}, True),
        # Whitespace variations (extra spaces inside the sentence but exact trigger matches)
        ({"content": "   instruction & resources saved to   "}, True),

        # Failure: trigger string missing
        ({"content": "some other message"}, False),

        # Edge Case 1: missing "content" key
        ({"other_key": "instruction & resources saved to"}, False),

        # Edge Case 2: last_message() returns a string instead of dict
        ("instruction & resources saved to /path/to/file", False),

        # Edge Case 3: last_message() returns None
        (None, False),

        # Edge Case 4: last_message() returns an empty dictionary
        ({}, False),

        # Edge Case 5: content value is not a string
        ({"content": None}, False),
        ({"content": 123}, False),
    ]
)
def test_instruction_trigger_various_outputs(mock_sender, last_message_return, expected):
    """
    Test instruction_trigger handles various return values from last_message() gracefully.
    """
    mock_sender.last_message.return_value = last_message_return
    assert instruction_trigger(mock_sender) == expected

def test_instruction_trigger_missing_last_message():
    """
    Test instruction_trigger when sender lacks the last_message method.
    """
    class BadSender:
        pass

    sender = BadSender()
    assert instruction_trigger(sender) == False

def test_instruction_trigger_none_sender():
    """
    Test instruction_trigger when sender is None.
    """
    assert instruction_trigger(None) == False

def test_instruction_trigger_last_message_not_callable():
    """
    Test instruction_trigger when last_message is not a method.
    """
    class WeirdSender:
        last_message = "not a callable"

    sender = WeirdSender()
    assert instruction_trigger(sender) == False

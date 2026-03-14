import pytest
from unittest.mock import MagicMock
from finrobot.agents.utils import order_trigger

@pytest.fixture
def mock_sender():
    def _create_mock(name="assistant", content="execute the buy order", has_name=True, has_last_message=True):
        if not has_name and not has_last_message:
             return None

        sender = MagicMock()
        if has_name:
            sender.name = name
        else:
            del sender.name

        if has_last_message:
            if content is None:
                sender.last_message.return_value = None
            elif isinstance(content, dict):
                sender.last_message.return_value = content
            elif content is False:
                sender.last_message.return_value = "Not a dict"
            else:
                sender.last_message.return_value = {"content": content}
        else:
             del sender.last_message
        return sender
    return _create_mock


class TestOrderTrigger:
    @pytest.mark.parametrize(
        "sender_name, sender_content, target_name, target_pattern, expected",
        [
            # Happy path
            ("assistant", "execute the buy order", "assistant", "buy", True),

            # Negative paths
            ("user", "execute the buy order", "assistant", "buy", False),
            ("assistant", "execute the sell order", "assistant", "buy", False),

            # Case insensitivity
            ("ASSISTANT", "EXECUTE THE BUY ORDER", "assistant", "buy", True),
            ("AsSiStAnT", "eXeCuTe ThE bUy OrDeR", "aSsIsTaNt", "BuY", True),

            # Whitespace insensitivity
            ("  assistant  ", "   execute the buy order   ", " assistant ", " buy ", True),
            ("\nassistant\n", "\nexecute the buy order\n", "\nassistant\n", "\nbuy\n", True),

            # Defensive - missing keys or non-string inputs
            ("assistant", None, "assistant", "buy", False),
            ("assistant", False, "assistant", "buy", False),
            ("assistant", {"other_key": "value"}, "assistant", "buy", False),
            ("assistant", {"content": 123}, "assistant", "buy", False),
            ("assistant", "execute the buy order", 123, "buy", False),
            ("assistant", "execute the buy order", "assistant", 123, False),
            (123, "execute the buy order", "123", "buy", False),

            # Regex characters as plain text
            ("assistant", "execute the b*y order?", "assistant", "b*y", True),
            ("assistant", "execute the bbby order", "assistant", "b*y", False),
        ]
    )
    def test_order_trigger_scenarios(
        self, mock_sender, sender_name, sender_content, target_name, target_pattern, expected
    ):
        sender = mock_sender(name=sender_name, content=sender_content)
        assert order_trigger(sender, name=target_name, pattern=target_pattern) is expected

    @pytest.mark.parametrize(
        "has_name, has_last_message",
        [
            (False, False), # sender is None essentially if both missing or we test literal None
            (False, True),
            (True, False)
        ]
    )
    def test_defensive_missing_attributes(self, mock_sender, has_name, has_last_message):
        if not has_name and not has_last_message:
             assert order_trigger(None, name="assistant", pattern="buy") is False
             return

        sender = mock_sender(has_name=has_name, has_last_message=has_last_message)
        assert order_trigger(sender, name="assistant", pattern="buy") is False

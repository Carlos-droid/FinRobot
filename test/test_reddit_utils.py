import pytest
from unittest.mock import MagicMock, patch
from finrobot.data_source.reddit_utils import init_reddit_client
import finrobot.data_source.reddit_utils as reddit_utils

# Create a dummy function to be decorated
@init_reddit_client
def dummy_function(*args, **kwargs):
    return "success"

@pytest.fixture(autouse=True)
def reset_global_reddit_client(monkeypatch):
    """Ensures the global reddit_client is reset before and after each test to prevent state leakage."""
    monkeypatch.setattr(reddit_utils, 'reddit_client', None, raising=False)
    yield
    monkeypatch.setattr(reddit_utils, 'reddit_client', None, raising=False)

def test_init_reddit_client_missing_credentials(monkeypatch, capsys):
    # Ensure environment variables are missing
    monkeypatch.delenv("REDDIT_CLIENT_ID", raising=False)
    monkeypatch.delenv("REDDIT_CLIENT_SECRET", raising=False)

    mock_inner_func = MagicMock(return_value="mock_success")
    decorated_mock = init_reddit_client(mock_inner_func)

    result = decorated_mock("arg1", kwarg1="val1")

    # Check stdout
    captured = capsys.readouterr()
    assert "Please set the environment variables for Reddit API credentials." in captured.out

    # Check return value
    assert result is None

    # Check inner function is not called
    mock_inner_func.assert_not_called()

def test_init_reddit_client_with_credentials(monkeypatch, capsys):
    # Set environment variables
    monkeypatch.setenv("REDDIT_CLIENT_ID", "test_id")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "test_secret")

    # Mock praw.Reddit to prevent actual API calls
    # Note: Ensure this patch path perfectly matches how praw is imported in reddit_utils.py
    with patch("finrobot.data_source.reddit_utils.praw.Reddit") as mock_reddit:
        mock_inner_func = MagicMock(return_value="mock_success")
        decorated_mock = init_reddit_client(mock_inner_func)

        result = decorated_mock("arg1", kwarg1="val1")

        # Check praw.Reddit was called correctly
        mock_reddit.assert_called_once_with(
            client_id="test_id",
            client_secret="test_secret",
            user_agent="python:finrobot:v0.1 (by /u/finrobot)",
        )

        # Check global variable
        assert getattr(reddit_utils, 'reddit_client', None) is not None

        # Check stdout
        captured = capsys.readouterr()
        assert "Reddit client initialized" in captured.out

        # Check return value
        assert result == "mock_success"

        # Check inner function was called
        mock_inner_func.assert_called_once_with("arg1", kwarg1="val1")
import os
import pytest
from unittest.mock import patch
from finrobot.llm_config import get_auto_config

@pytest.fixture(autouse=True)
def mock_sleep():
    """Globally mock time.sleep for all tests in this file to prevent delays."""
    with patch("finrobot.llm_config.time.sleep") as mock:
        yield mock

@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Ensure relevant environment variables are clean for each test to avoid pollution."""
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.delenv("NIM_RATE_LIMIT_DELAY", raising=False)
    monkeypatch.delenv("OLLAMA_URL", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    monkeypatch.delenv("NIM_TEXT_MODEL", raising=False)

@pytest.mark.parametrize(
    "prefer_local, nvidia_key, expected_order",
    [
        # Prefer local with API key: Ollama first, then NIM fallback
        (True, "test-nim-key", ["ollama", "test-nim-key"]),
        # Prefer local without API key: Ollama only
        (True, None, ["ollama"]),
        # Prefer cloud with API key: NIM first, then Ollama fallback
        (False, "test-nim-key", ["test-nim-key", "ollama"]),
        # Prefer cloud without API key: Ollama only
        (False, None, ["ollama"]),
    ]
)
def test_get_auto_config_branches(monkeypatch, prefer_local, nvidia_key, expected_order):
    if nvidia_key:
        monkeypatch.setenv("NVIDIA_API_KEY", nvidia_key)

    config = get_auto_config(prefer_local=prefer_local)

    assert len(config["config_list"]) == len(expected_order)
    for i, expected_api_key in enumerate(expected_order):
        assert config["config_list"][i]["api_key"] == expected_api_key

def test_get_auto_config_invalid_types():
    # If invalid types are passed, Python typically proceeds but behavior might vary
    # E.g., passing a string for boolean might evaluate to True, or it might just fail if it tries to do something boolean specific, but in Python 'truthy' applies.
    config = get_auto_config(prefer_local="not-a-bool")
    # "not-a-bool" is truthy, so it behaves like prefer_local=True
    assert len(config["config_list"]) == 1
    assert config["config_list"][0]["api_key"] == "ollama"

    # prefer_local=None is falsy
    config2 = get_auto_config(prefer_local=None)
    assert len(config2["config_list"]) == 1
    assert config2["config_list"][0]["api_key"] == "ollama"

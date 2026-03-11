import os
import json
import pytest
from unittest.mock import patch
from datetime import date
from finrobot.utils import get_current_date, register_keys_from_json

@patch('finrobot.utils.date')
def test_get_current_date(mock_date):
    # Set up the mock to return a specific date when today() is called
    mock_date.today.return_value = date(2023, 10, 25)

    # Call the function
    result = get_current_date()

    # Assert the expected result
    assert result == "2023-10-25"

    # Verify today() was called once
    mock_date.today.assert_called_once()

def test_register_keys_from_json_success(tmp_path):
    # Create a temporary JSON file with mixed data types
    config_file = tmp_path / "config.json"
    config_data = {"API_KEY": "secret_123", "PORT": 8080, "DEBUG": True}
    config_file.write_text(json.dumps(config_data))

    # Use patch.dict to safely mock os.environ without altering its class type
    with patch.dict(os.environ, {}, clear=True):
        register_keys_from_json(str(config_file))

        # Verify environment variables are set and properly cast to strings
        assert os.environ["API_KEY"] == "secret_123"
        assert os.environ["PORT"] == "8080"
        assert os.environ["DEBUG"] == "True"

def test_register_keys_from_json_file_not_found():
    # Verify FileNotFoundError is raised for non-existent file
    with pytest.raises(FileNotFoundError):
        register_keys_from_json("non_existent_file.json")

def test_register_keys_from_json_invalid_json(tmp_path):
    # Create a temporary file with invalid JSON content
    bad_json_file = tmp_path / "bad.json"
    bad_json_file.write_text("{invalid_json:")

    # Verify json.JSONDecodeError is raised
    with pytest.raises(json.JSONDecodeError):
        register_keys_from_json(str(bad_json_file))

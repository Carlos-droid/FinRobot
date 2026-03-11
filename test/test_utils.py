import os
import json
import pytest
from unittest.mock import patch
from datetime import date, datetime
from finrobot.utils import get_current_date, get_next_weekday, register_keys_from_json

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


@pytest.mark.parametrize(
    "input_date, expected_date",
    [
        # Weekdays should remain the same
        (datetime(2023, 10, 23), datetime(2023, 10, 23)),  # Monday
        (datetime(2023, 10, 24), datetime(2023, 10, 24)),  # Tuesday
        (datetime(2023, 10, 25), datetime(2023, 10, 25)),  # Wednesday
        (datetime(2023, 10, 26), datetime(2023, 10, 26)),  # Thursday
        (datetime(2023, 10, 27), datetime(2023, 10, 27)),  # Friday
        # Weekends should roll over to the next Monday
        (datetime(2023, 10, 28), datetime(2023, 10, 30)),  # Saturday to Monday
        (datetime(2023, 10, 29), datetime(2023, 10, 30)),  # Sunday to Monday
    ]
)
def test_get_next_weekday_datetime(input_date, expected_date):
    assert get_next_weekday(input_date) == expected_date


@pytest.mark.parametrize(
    "input_str, expected_date",
    [
        # Weekdays should remain the same
        ("2023-10-23", datetime(2023, 10, 23)),  # Monday
        ("2023-10-27", datetime(2023, 10, 27)),  # Friday
        # Weekends should roll over to the next Monday
        ("2023-10-28", datetime(2023, 10, 30)),  # Saturday to Monday
        ("2023-10-29", datetime(2023, 10, 30)),  # Sunday to Monday
        # End of year scenarios
        ("2021-12-31", datetime(2021, 12, 31)),  # Friday (remains Friday)
        ("2022-12-31", datetime(2023, 1, 2)),    # Saturday to Monday (Jan 2nd)
        ("2023-12-31", datetime(2024, 1, 1)),    # Sunday to Monday (Jan 1st)
    ]
)
def test_get_next_weekday_string(input_str, expected_date):
    assert get_next_weekday(input_str) == expected_date


def test_get_next_weekday_invalid_string():
    with pytest.raises(ValueError):
        get_next_weekday("2023/10/25")  # Invalid format

    with pytest.raises(ValueError):
        get_next_weekday("10-25-2023")  # Invalid format


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

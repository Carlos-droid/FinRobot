import pytest
from unittest.mock import patch
from datetime import date, datetime
from finrobot.utils import get_current_date, get_next_weekday

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

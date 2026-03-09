import pytest
from unittest.mock import patch
from datetime import date
from finrobot.utils import get_current_date

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

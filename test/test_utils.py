import pytest
from unittest.mock import patch
from datetime import date
import pandas as pd
import os

from finrobot.utils import get_current_date, save_output

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

def test_save_output_with_path(tmp_path, capsys):
    # Create sample DataFrame
    df = pd.DataFrame({"col1": [1, 2], "col2": ["A", "B"]})
    tag = "TestTag"

    # Define a temporary file path
    save_path = tmp_path / "test_data.csv"

    # Call the function
    save_output(df, tag, str(save_path))

    # Assert file was created
    assert save_path.exists()
    assert save_path.is_file()

    # Assert file contents
    saved_df = pd.read_csv(save_path, index_col=0)
    pd.testing.assert_frame_equal(df, saved_df)

    # Assert explicitly the printed output
    captured = capsys.readouterr()
    expected_print = f"{tag} saved to {str(save_path)}\n"
    assert captured.out == expected_print

def test_save_output_without_path(capsys):
    # Create sample DataFrame
    df = pd.DataFrame({"col1": [1, 2], "col2": ["A", "B"]})
    tag = "TestTag"

    # Call the function with None for save_path
    save_output(df, tag, None)

    # Assert explicitly nothing was printed
    captured = capsys.readouterr()
    assert captured.out == ""

def test_save_output_exception(tmp_path, capsys):
    # Create sample DataFrame
    df = pd.DataFrame({"col1": [1, 2], "col2": ["A", "B"]})
    tag = "TestTag"

    # Define an invalid path (e.g. attempting to save to a directory rather than a file)
    # The tmp_path itself is a directory
    invalid_save_path = tmp_path

    # Call the function and expect an exception (e.g., IsADirectoryError or PermissionError)
    with pytest.raises((IsADirectoryError, PermissionError)):
        save_output(df, tag, str(invalid_save_path))

    # Assert explicitly nothing was printed since the exception bubbled up
    captured = capsys.readouterr()
    assert captured.out == ""

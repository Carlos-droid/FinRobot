import os
from unittest.mock import patch, mock_open
import pytest
from finrobot.functional.analyzer import save_to_file

def test_save_to_file():
    data = "test data"
    file_path = "some/dir/test_file.txt"

    # Mock os.makedirs and builtins.open
    with patch("os.makedirs") as mock_makedirs, \
         patch("builtins.open", mock_open()) as mock_file:

        # Execute the function
        save_to_file(data, file_path)

        # Verify os.makedirs was called correctly
        mock_makedirs.assert_called_once_with("some/dir", exist_ok=True)

        # Verify open was called correctly
        mock_file.assert_called_once_with(file_path, "w")

        # Verify the correct data was written
        mock_file().write.assert_called_once_with(data)

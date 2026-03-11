import pytest
from unittest.mock import patch, mock_open
import os
from finrobot.functional.analyzer import save_to_file

def test_save_to_file():
    data = "test content"
    file_path = "test_dir/test_file.txt"
    dir_path = "test_dir"

    with patch("os.makedirs") as mock_makedirs, \
         patch("builtins.open", mock_open()) as mock_file:

        save_to_file(data, file_path)

        # Verify os.makedirs was called correctly
        mock_makedirs.assert_called_once_with(dir_path, exist_ok=True)

        # Verify open was called correctly
        mock_file.assert_called_once_with(file_path, "w")

        # Verify write was called correctly on the file handle
        mock_file().write.assert_called_once_with(data)

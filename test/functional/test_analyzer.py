import os
from unittest.mock import patch, mock_open
import pytest
from finrobot.functional.analyzer import save_to_file

def test_save_to_file():
    # 1. Setup con datos descriptivos
    test_data = "test content"
    test_file_path = "test_dir/test_file.txt"
    expected_dir = "test_dir"

    # 2. Mocking de I/O
    with patch("os.makedirs") as mock_makedirs, \
         patch("builtins.open", mock_open()) as mock_file:

        # 3. Ejecución
        save_to_file(test_data, test_file_path)

        # 4. Aserciones de estructura y archivos
        mock_makedirs.assert_called_once_with(expected_dir, exist_ok=True)
        mock_file.assert_called_once_with(test_file_path, "w")

        # 5. Verificación de la escritura de datos
        mock_file().write.assert_called_once_with(test_data)

import os
from unittest.mock import patch, mock_open
import pytest
from finrobot.functional.analyzer import save_to_file

def test_save_to_file():
    """
    Verifica que save_to_file cree el directorio de destino si no existe,
    abra el archivo en modo escritura y vuelque el contenido correctamente.
    """
    # 1. Setup: Definición de datos y rutas de prueba
    test_data = "test content"
    test_file_path = "test_dir/test_file.txt"
    expected_dir = "test_dir"

    # 2. Mocking de I/O: Aislamos el test del sistema de archivos real
    with patch("os.makedirs") as mock_makedirs, \
         patch("builtins.open", mock_open()) as mock_file:

        # 3. Ejecución de la función bajo prueba
        save_to_file(test_data, test_file_path)

        # 4. Aserciones: Verificamos la creación del directorio
        # exist_ok=True es crucial para evitar errores si el dir ya existe
        mock_makedirs.assert_called_once_with(expected_dir, exist_ok=True)

        # 5. Aserciones: Verificamos la apertura y escritura del archivo
        mock_file.assert_called_once_with(test_file_path, "w")
        mock_file().write.assert_called_once_with(test_data)
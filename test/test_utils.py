import os
import json
import pytest
import pandas as pd
from unittest.mock import patch
from datetime import date, datetime
from finrobot.utils import (
    get_current_date, 
    get_next_weekday, 
    register_keys_from_json, 
    save_output
)

# --- Bloque 1: Tests para get_current_date ---

@patch('finrobot.utils.date')
def test_get_current_date(mock_date):
    """Verifica que la fecha actual se formatee correctamente como ISO string."""
    mock_date.today.return_value = date(2023, 10, 25)
    result = get_current_date()
    assert result == "2023-10-25"
    mock_date.today.assert_called_once()


# --- Bloque 2: Tests para get_next_weekday (Lógica de Negocio) ---

@pytest.mark.parametrize(
    "input_date, expected_date",
    [
        (datetime(2023, 10, 23), datetime(2023, 10, 23)),  # Lunes (se queda)
        (datetime(2023, 10, 27), datetime(2023, 10, 27)),  # Viernes (se queda)
        (datetime(2023, 10, 28), datetime(2023, 10, 30)),  # Sábado -> Lunes
        (datetime(2023, 10, 29), datetime(2023, 10, 30)),  # Domingo -> Lunes
    ]
)
def test_get_next_weekday_datetime(input_date, expected_date):
    """Valida el salto automático de fines de semana con objetos datetime."""
    assert get_next_weekday(input_date) == expected_date


@pytest.mark.parametrize(
    "input_str, expected_date",
    [
        ("2023-10-23", datetime(2023, 10, 23)),  # Lunes
        ("2023-10-28", datetime(2023, 10, 30)),  # Sábado -> Lunes
        ("2022-12-31", datetime(2023, 1, 2)),    # Fin de año: Sábado a Lunes
        ("2023-12-31", datetime(2024, 1, 1)),    # Domingo a Lunes (Año Nuevo)
    ]
)
def test_get_next_weekday_string(input_str, expected_date):
    """Valida el parseo de strings y el cálculo de día hábil."""
    assert get_next_weekday(input_str) == expected_date


# --- Bloque 3: Tests para save_output (Persistencia de Datos) ---

def test_save_output_with_path(tmp_path, capsys):
    """Prueba el guardado exitoso de un DataFrame en un archivo CSV temporal."""
    df = pd.DataFrame({"col1": [1, 2], "col2": ["A", "B"]})
    tag = "TestTag"
    save_path = tmp_path / "test_data.csv"

    save_output(df, tag, str(save_path))

    # Validaciones de archivo
    assert save_path.exists()
    saved_df = pd.read_csv(save_path, index_col=0)
    pd.testing.assert_frame_equal(df, saved_df)

    # Validar mensaje en consola (stdout)
    captured = capsys.readouterr()
    assert f"{tag} saved to" in captured.out


def test_save_output_without_path(capsys):
    """Verifica que si no hay ruta, la función no haga nada ni imprima nada."""
    df = pd.DataFrame({"col1": [1, 2]})
    save_output(df, "Tag", None)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_save_output_exception(tmp_path):
    """Verifica el comportamiento defensivo ante rutas inválidas."""
    df = pd.DataFrame({"col1": [1]})
    # Intentar guardar en un directorio ya existente como si fuera un archivo lanza error
    invalid_path = tmp_path 
    with pytest.raises((IsADirectoryError, PermissionError)):
        save_output(df, "Tag", str(invalid_path))
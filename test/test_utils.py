import os
import json
import pytest
from unittest.mock import patch
from datetime import date, datetime
from finrobot.utils import get_current_date, get_next_weekday, register_keys_from_json

# --- Tests para get_current_date ---

@patch('finrobot.utils.date')
def test_get_current_date(mock_date):
    # Configuramos el mock para devolver una fecha específica
    mock_date.today.return_value = date(2023, 10, 25)

    result = get_current_date()

    assert result == "2023-10-25"
    mock_date.today.assert_called_once()


# --- Tests para get_next_weekday ---

@pytest.mark.parametrize(
    "input_date, expected_date",
    [
        # Los días de semana se mantienen igual
        (datetime(2023, 10, 23), datetime(2023, 10, 23)),  # Lunes
        (datetime(2023, 10, 24), datetime(2023, 10, 24)),  # Martes
        (datetime(2023, 10, 25), datetime(2023, 10, 25)),  # Miércoles
        (datetime(2023, 10, 26), datetime(2023, 10, 26)),  # Jueves
        (datetime(2023, 10, 27), datetime(2023, 10, 27)),  # Viernes
        # Los fines de semana saltan al lunes siguiente
        (datetime(2023, 10, 28), datetime(2023, 10, 30)),  # Sábado a Lunes
        (datetime(2023, 10, 29), datetime(2023, 10, 30)),  # Domingo a Lunes
    ]
)
def test_get_next_weekday_datetime(input_date, expected_date):
    assert get_next_weekday(input_date) == expected_date


@pytest.mark.parametrize(
    "input_str, expected_date",
    [
        # Formato string: días de semana
        ("2023-10-23", datetime(2023, 10, 23)),  # Lunes
        ("2023-10-27", datetime(2023, 10, 27)),  # Viernes
        # Formato string: fines de semana
        ("2023-10-28", datetime(2023, 10, 30)),  # Sábado a Lunes
        ("2023-10-29", datetime(2023, 10, 30)),  # Domingo a Lunes
        # Escenarios de fin de año
        ("2021-12-31", datetime(2021, 12, 31)),  # Viernes (se mantiene)
        ("2022-12-31", datetime(2023, 1, 2)),    # Sábado a Lunes (2 de Enero)
        ("2023-12-31", datetime(2024, 1, 1)),    # Domingo a L
    ]
)
def test_get_next_weekday_string(input_str, expected_date):
    assert get_next_weekday(input_str) == expected_date
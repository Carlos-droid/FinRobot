import pytest
import pandas as pd
from unittest.mock import MagicMock
from finrobot.toolkits import stringify_output, register_toolkits

# --- SECCIÓN 1: Tests para el decorador @stringify_output ---

# Funciones de ayuda para testear el decorador
@stringify_output
def return_string():
    return "hello"

@stringify_output
def return_int():
    return 42

@stringify_output
def return_none():
    return None

@stringify_output
def return_empty_list():
    return []

@stringify_output
def return_empty_dict():
    return {}

class CustomObject:
    def __str__(self):
        return "custom_object_str"

@stringify_output
def return_custom_object():
    return CustomObject()

@stringify_output
def return_dataframe():
    return pd.DataFrame({'A': [1, 2], 'B': [3, 4]})

@stringify_output
def echo_args_kwargs(*args, **kwargs):
    """Echoes back arguments and keyword arguments."""
    return args, kwargs

def test_stringify_basic_types():
    assert return_string() == "hello"
    assert return_int() == "42"

def test_stringify_none():
    # Verifica que str(None) retorne la cadena "None"
    assert return_none() == "None"

def test_stringify_empty_collections():
    assert return_empty_list() == "[]"
    assert return_empty_dict() == "{}"

def test_stringify_custom_object():
    assert return_custom_object() == "custom_object_str"

def test_stringify_dataframe():
    df_str = return_dataframe()
    expected_str = pd.DataFrame({'A': [1, 2], 'B': [3, 4]}).to_string()
    assert df_str == expected_str

def test_decorator_argument_passing():
    result = echo_args_kwargs(1, 2, a=3, b=4)
    # El decorador debe retornar str( ((1, 2), {'a': 3, 'b': 4}) )
    expected_result = str(((1, 2), {'a': 3, 'b': 4}))
    assert result == expected_result

def test_decorator_metadata_preservation():
    # Verifica que @wraps haya hecho su trabajo manteniendo nombre y docstring
    assert echo_args_kwargs.__name__ == "echo_args_kwargs"
    assert echo_args_kwargs.__doc__ == "Echoes back arguments and keyword arguments."


# --- SECCIÓN 2: Tests para register_toolkits ---

def test_register_toolkits_missing_callable_function():
    """Verifica que falle si la configuración de la herramienta no es válida o invocable."""
    # Setup de mocks
    mock_caller = MagicMock()
    mock_executor = MagicMock()

    # Escenario 1: Falta la clave "function"
    invalid_config_1 = [{"name": "invalid_tool", "description": "missing function"}]

    # Escenario 2: La clave "function" existe pero no es un callable
    invalid_config_2 = [{"function": "not_a_callable"}]

    error_msg = "Function not found in tool configuration or not callable."

    with pytest.raises(ValueError, match=error_msg):
        register_toolkits(
            config=invalid_config_1,
            caller=mock_caller,
            executor=mock_executor
        )

    with pytest.raises(ValueError, match=error_msg):
        register_toolkits(
            config=invalid_config_2,
            caller=mock_caller,
            executor=mock_executor
        )

import pytest
import pandas as pd
from finrobot.toolkits import stringify_output

# Helper functions for testing
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
    # As per current implementation, str(None) returns "None"
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
    # The result of echo_args_kwargs is a tuple ((1, 2), {'a': 3, 'b': 4})
    # Since it's decorated, it should return str( ((1, 2), {'a': 3, 'b': 4}) )
    expected_result = str(((1, 2), {'a': 3, 'b': 4}))
    assert result == expected_result

def test_decorator_metadata_preservation():
    assert echo_args_kwargs.__name__ == "echo_args_kwargs"
    assert echo_args_kwargs.__doc__ == "Echoes back arguments and keyword arguments."

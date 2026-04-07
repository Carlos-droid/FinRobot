import pytest
from unittest.mock import MagicMock
from finrobot.toolkits import register_toolkits

@pytest.fixture
def mock_agents():
    caller = MagicMock()
    executor = MagicMock()
    return caller, executor

@pytest.mark.parametrize("invalid_tool", [
    {"name": "my_tool"},  # Missing "function" key
    {"function": "not_callable"},  # "function" is not callable
])
def test_register_toolkits_invalid_dict(mock_agents, invalid_tool):
    caller, executor = mock_agents
    with pytest.raises(ValueError, match="Function not found in tool configuration or not callable."):
        register_toolkits([invalid_tool], caller=caller, executor=executor)

def test_register_toolkits_invalid_type_int(mock_agents):
    caller, executor = mock_agents
    # Passing an integer directly will cause TypeError: argument of type 'int' is not iterable
    with pytest.raises(TypeError):
        register_toolkits([123], caller=caller, executor=executor)

def test_register_toolkits_invalid_type_str(mock_agents):
    caller, executor = mock_agents
    # Passing the exact string "function" will bypass the 'in' check and cause TypeError on index access
    with pytest.raises(TypeError):
        register_toolkits(["function"], caller=caller, executor=executor)

    # Passing a string without "function" as substring will cause ValueError
    with pytest.raises(ValueError):
        register_toolkits(["invalid_tool"], caller=caller, executor=executor)

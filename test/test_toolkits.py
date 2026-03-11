import pytest
from unittest.mock import MagicMock
from finrobot.toolkits import register_toolkits

def test_register_toolkits_missing_callable_function():
    # Setup mock caller and executor
    mock_caller = MagicMock()
    mock_executor = MagicMock()

    # Define invalid tool configurations
    # 1. Missing "function" key entirely
    invalid_config_1 = [{"name": "invalid_tool", "description": "missing function"}]

    # 2. "function" key exists but is not callable
    invalid_config_2 = [{"function": "not_a_callable"}]

    # Assert ValueError is raised for the first invalid config
    with pytest.raises(ValueError, match="Function not found in tool configuration or not callable."):
        register_toolkits(
            config=invalid_config_1,
            caller=mock_caller,
            executor=mock_executor
        )

    # Assert ValueError is raised for the second invalid config
    with pytest.raises(ValueError, match="Function not found in tool configuration or not callable."):
        register_toolkits(
            config=invalid_config_2,
            caller=mock_caller,
            executor=mock_executor
        )

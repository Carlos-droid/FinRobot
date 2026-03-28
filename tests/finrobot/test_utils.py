import sys
from unittest.mock import MagicMock, patch
from datetime import date

# Mock dependencies before importing the target module
mock_pd = MagicMock()
sys.modules['pandas'] = mock_pd
sys.modules['dotenv'] = MagicMock()
sys.modules['yfinance'] = MagicMock()
sys.modules['sec_api'] = MagicMock()
sys.modules['praw'] = MagicMock()
sys.modules['mplfinance'] = MagicMock()
sys.modules['backtrader'] = MagicMock()
sys.modules['reportlab'] = MagicMock()
sys.modules['reportlab.lib'] = MagicMock()
sys.modules['reportlab.platypus'] = MagicMock()

# Now we can safely import from finrobot.utils
from finrobot.utils import get_current_date, save_output

def test_get_current_date_format():
    """Test if the returned date string matches the YYYY-MM-DD format."""
    result = get_current_date()
    assert isinstance(result, str)
    # Basic format check: XXXX-XX-XX
    parts = result.split('-')
    assert len(parts) == 3
    assert len(parts[0]) == 4
    assert len(parts[1]) == 2
    assert len(parts[2]) == 2

@patch('finrobot.utils.date')
def test_get_current_date_mocked(mock_date):
    """Test if the function correctly formats a deterministic date."""
    mock_today = date(2023, 10, 27)
    mock_date.today.return_value = mock_today
    result = get_current_date()
    assert result == '2023-10-27'
    mock_date.today.assert_called_once()

def test_save_output_with_path(tmp_path, capsys):
    """Test save_output when a save_path is provided."""
    df = MagicMock()
    tag = "TestTag"
    save_path = tmp_path / "test_output.csv"

    save_output(df, tag, save_path=str(save_path))

    # Verify to_csv was called on the dataframe
    df.to_csv.assert_called_once_with(str(save_path))

    # Verify the print output
    captured = capsys.readouterr()
    assert f"{tag} saved to {save_path}" in captured.out

def test_save_output_without_path(capsys):
    """Test save_output when save_path is None."""
    df = MagicMock()
    tag = "TestTag"

    save_output(df, tag, save_path=None)

    # Verify to_csv was NOT called
    df.to_csv.assert_not_called()

    # Verify no "saved to" message was printed
    captured = capsys.readouterr()
    assert "saved to" not in captured.out

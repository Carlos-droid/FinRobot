import unittest
import re
from unittest.mock import patch
from datetime import date
from finrobot.utils import get_current_date

class TestUtils(unittest.TestCase):
    def test_get_current_date_format(self):
        """Test if the returned date string matches the YYYY-MM-DD format."""
        result = get_current_date()

        # Check if the result is a string
        self.assertIsInstance(result, str)

        # Regex for YYYY-MM-DD
        pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        self.assertTrue(bool(pattern.match(result)), f"Expected format YYYY-MM-DD, got {result}")

    @patch('finrobot.utils.date')
    def test_get_current_date_mocked(self, mock_date):
        """Test if the function correctly formats a deterministic date."""
        # Because we import `date` into `finrobot.utils` (`from datetime import date`),
        # we can patch `finrobot.utils.date` directly.

        # We need mock_date.today() to return a mock object that, when .strftime("%Y-%m-%d")
        # is called, returns our desired string.
        # Alternatively, we can just make mock_date.today() return a real datetime.date object.
        mock_today = date(2023, 10, 27)
        mock_date.today.return_value = mock_today

        result = get_current_date()

        # Assert the result matches the mocked date's string representation
        self.assertEqual(result, '2023-10-27')

        # Verify that today() was called exactly once
        mock_date.today.assert_called_once()

if __name__ == '__main__':
    unittest.main()

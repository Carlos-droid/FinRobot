import json
import os
import unittest
from unittest.mock import patch, mock_open
from datetime import datetime, timedelta
from batch_analyze import batch_process, CARTERA_PATH

class TestBatchAnalyze(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now()
        self.recent_date = (self.now - timedelta(days=2)).strftime("%Y-%m-%d")
        self.old_date = (self.now - timedelta(days=10)).strftime("%Y-%m-%d")

        self.cartera_data = [
            {"symbol": "AAPL", "name": "Apple", "last_analysis_date": self.recent_date},
            {"symbol": "MSFT", "name": "Microsoft", "last_analysis_date": self.old_date},
            {"symbol": "GOOGL", "name": "Google", "last_analysis_date": "N/A"},
            {"symbol": "AMZN", "name": "Amazon", "last_analysis_date": "invalid-date"}
        ]

    @patch('batch_analyze.os.path.exists')
    @patch('batch_analyze.run_finrobot_analysis')
    @patch('builtins.open', new_callable=mock_open)
    @patch('batch_analyze.json.dump')
    def test_batch_process_skip_recent(self, mock_json_dump, mock_file, mock_run_analysis, mock_exists):
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(self.cartera_data)
        mock_run_analysis.return_value = (None, "Recommendation: COMPRAR")

        # Test default behavior (skip_recent=True)
        batch_process()

        # Apple should be skipped, others should be analyzed
        self.assertEqual(mock_run_analysis.call_count, 3)
        calls = [call[0][0] for call in mock_run_analysis.call_args_list]
        self.assertNotIn("AAPL", calls)
        self.assertIn("MSFT", calls)
        self.assertIn("GOOGL", calls)
        self.assertIn("AMZN", calls)

    @patch('batch_analyze.os.path.exists')
    @patch('batch_analyze.run_finrobot_analysis')
    @patch('builtins.open', new_callable=mock_open)
    @patch('batch_analyze.json.dump')
    def test_batch_process_force(self, mock_json_dump, mock_file, mock_run_analysis, mock_exists):
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(self.cartera_data)
        mock_run_analysis.return_value = (None, "Recommendation: COMPRAR")

        # Test force behavior (skip_recent=False)
        batch_process(skip_recent=False)

        # All 4 should be analyzed
        self.assertEqual(mock_run_analysis.call_count, 4)

if __name__ == '__main__':
    unittest.main()

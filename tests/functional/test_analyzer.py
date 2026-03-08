import unittest
from finrobot.functional.analyzer import combine_prompt

class TestAnalyzer(unittest.TestCase):

    def test_combine_prompt_with_table_str(self):
        instruction = "Summarize the data."
        resource = "Some resource text."
        table_str = "Table Content here"

        expected_prompt = "Table Content here\n\nResource: Some resource text.\n\nInstruction: Summarize the data."
        result = combine_prompt(instruction, resource, table_str)

        self.assertEqual(result, expected_prompt)

    def test_combine_prompt_without_table_str(self):
        instruction = "Summarize the data."
        resource = "Some resource text."

        expected_prompt = "Resource: Some resource text.\n\nInstruction: Summarize the data."
        result = combine_prompt(instruction, resource)  # table_str is None by default

        self.assertEqual(result, expected_prompt)

    def test_combine_prompt_with_empty_table_str(self):
        instruction = "Summarize the data."
        resource = "Some resource text."
        table_str = ""

        expected_prompt = "Resource: Some resource text.\n\nInstruction: Summarize the data."
        result = combine_prompt(instruction, resource, table_str)

        self.assertEqual(result, expected_prompt)

if __name__ == "__main__":
    unittest.main()
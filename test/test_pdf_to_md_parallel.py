import pytest
from unittest.mock import patch
from finrobot.data_source.marker_sec_src.pdf_to_md_parallel import process_single_pdf

@pytest.mark.parametrize(
    "filepath, markdown_exists_return",
    [
        ("dummy_file.txt", False),  # Case 1: Non-pdf file
        ("document.pdf", True),      # Case 2: Markdown already exists
    ]
)
@patch("finrobot.data_source.marker_sec_src.pdf_to_md_parallel.markdown_exists")
def test_process_single_pdf_early_returns(mock_markdown_exists, filepath, markdown_exists_return):
    # Arrange
    mock_markdown_exists.return_value = markdown_exists_return

    out_folder = "dummy_out_folder"
    metadata = {}
    min_length = 0
    args = (filepath, out_folder, metadata, min_length)

    # Act
    result = process_single_pdf(args)

    # Assert
    assert result is None

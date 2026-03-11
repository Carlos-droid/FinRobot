import pytest
import re
from unittest.mock import patch, MagicMock
from finrobot.data_source.filings_src.sec_filings import get_regex_enum, SECExtractor

@pytest.fixture
def sec_extractor():
    """Returns an instance of SECExtractor with mocked dependencies."""
    return SECExtractor(ticker="AAPL")

# --- SECCIÓN 1: Generación Dinámica de Enums (Regex) ---

def test_get_regex_enum_valid_pattern():
    regex_str = r"^Item \d+"
    enum_member = get_regex_enum(regex_str)
    assert hasattr(enum_member, "pattern")
    assert enum_member.pattern == re.compile(regex_str)
    assert enum_member.pattern.match("Item 1") is not None
    assert enum_member.pattern.match("Other Item") is None

def test_get_regex_enum_invalid_pattern():
    with pytest.raises(re.error):
        get_regex_enum(r"[")

def test_get_regex_enum_empty_string():
    enum_member = get_regex_enum("")
    assert enum_member.pattern == re.compile("")
    assert enum_member.pattern.match("anything") is not None

def test_get_regex_enum_none_input():
    with pytest.raises(TypeError):
        get_regex_enum(None)

def test_get_regex_enum_dynamic_class_creation():
    regex_str = "test"
    enum1 = get_regex_enum(regex_str)
    enum2 = get_regex_enum(regex_str)
    # Verificamos igualdad de valor pero diferencia de identidad de clase
    assert enum1.pattern == enum2.pattern
    assert type(enum1) is not type(enum2)
    assert enum1 is not enum2

# --- SECCIÓN 2: Extracción de Texto (get_all_text) ---

@pytest.mark.parametrize(
    "section, all_narratives, expected",
    [
        # Happy Path: múltiples elementos con 'text' concatenados con espacio
        (
            "Item 1", 
            {"Item 1": [{"text": "Hello"}, {"text": "World!"}]}, 
            "Hello World!"
        ),
        # Happy Path: Elemento único
        (
            "Item 1A", 
            {"Item 1A": [{"text": "Risk Factors."}]}, 
            "Risk Factors."
        ),
        # Caso borde: lista vacía para la sección
        (
            "Item 2", 
            {"Item 2": []}, 
            ""
        ),
        # Caso borde: diccionarios sin la clave 'text' (debe filtrar y saltar)
        (
            "Item 3", 
            {"Item 3": [{"other_key": "No text here"}, {"text": "Only this text"}]}, 
            "Only this text"
        ),
        # Caso borde: ningún diccionario tiene la clave 'text'
        (
            "Item 4",
            {"Item 4": [{"other_key": "Nothing"}, {"another_key": "Nope"}]},
            ""
        ),
        # Caso borde: sección faltante en el diccionario
        (
            "Item 5", 
            {"Item 1": [{"text": "Hello"}]}, 
            ""
        )
    ]
)
def test_get_all_text(sec_extractor, section, all_narratives, expected):
    """Test get_all_text with different edge cases and happy paths."""
    result = sec_extractor.get_all_text(section, all_narratives)
    assert result == expected

# --- SECCIÓN 3: Validación del Pipeline API ---

def test_pipeline_api_invalid_filing_type(sec_extractor):
    """Verify that pipeline_api raises ValueError for unsupported filing types."""
    dummy_text = "<HTML>dummy SEC document</HTML>"
    mock_sec_document = MagicMock()
    mock_sec_document.filing_type = "INVALID-TYPE"

    with patch('finrobot.data_source.filings_src.sec_filings.SECDocument.from_string', return_value=mock_sec_document):
        with pytest.raises(ValueError) as exc_info:
            sec_extractor.pipeline_api(dummy_text)
        assert "SEC document filing type INVALID-TYPE is not supported" in str(exc_info.value)
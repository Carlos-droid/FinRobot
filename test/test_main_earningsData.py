import pytest
from unittest.mock import patch, Mock
from tenacity import RetryError
from concurrent.futures import Future
from langchain.schema import Document
from finrobot.data_source.earnings_calls_src.main_earningsData import (
    clean_speakers,
    get_earnings_all_docs
)

# --- SECCIÓN 1: Pruebas de limpieza de oradores (clean_speakers) ---

@pytest.mark.parametrize(
    "input_speaker, expected",
    [
        # Comportamiento original
        ("John Doe:\n", "John Doe"),
        # Títulos entre paréntesis
        ("John Doe (CEO)", "John Doe"),
        # Paréntesis múltiples
        ("Jane Smith (Managing Director) (Analyst)", "Jane Smith"),
        # Espacios excesivos
        ("  Dr. Robert Smith  ", "Dr. Robert Smith"),
        # Nombres con iniciales o prefijos
        ("Mr. John A. Doe", "Mr. John A. Doe"),
        # Caracteres especiales
        ("O'Connor", "O'Connor"),
        ("Jean-Pierre", "Jean-Pierre"),
        # Tipos no-string (Manejo defensivo)
        (None, ""),
        (12345, "12345"),
        # Casos combinados
        ("\n  Jane-Doe (CFO):  ", "Jane-Doe")
    ]
)
def test_clean_speakers(input_speaker, expected):
    """Verifica que la limpieza de nombres de oradores sea robusta."""
    assert clean_speakers(input_speaker) == expected


# --- SECCIÓN 2: Pruebas de manejo de errores en obtención de documentos ---

def create_retry_error():
    """Helper para crear un RetryError realista para las pruebas."""
    mock_future = Mock(spec=Future)
    return RetryError(last_attempt=mock_future)

@pytest.fixture
def mock_docs_and_speakers():
    """Fixture que devuelve datos de éxito genéricos."""
    docs = [Document(page_content="Some content", metadata={"speaker": "Speaker 1", "quarter": "Q"})]
    speakers = ["Speaker 1"]
    return docs, speakers

@pytest.mark.parametrize(
    "side_effect_list, expected_quarters, expected_output_msgs",
    [
        # Escenario 1: El Q1 falla, Q2-Q4 tienen éxito
        (
            [
                create_retry_error(), # Q1 falla
                ([Document(page_content="Q2 doc", metadata={"speaker": "Spk2", "quarter": "Q2"})], ["Spk2"]),
                ([Document(page_content="Q3 doc", metadata={"speaker": "Spk3", "quarter": "Q3"})], ["Spk3"]),
                ([Document(page_content="Q4 doc", metadata={"speaker": "Spk4", "quarter": "Q4"})], ["Spk4"])
            ],
            ["Q2", "Q3", "Q4"],
            ["Don't have the data for Q1"]
        ),
        # Escenario 2: Todos los trimestres fallan
        (
            [
                create_retry_error(), # Q1 falla
                create_retry_error(), # Q2 falla
                create_retry_error(), # Q3 falla
                create_retry_error()  # Q4 falla
            ],
            [],
            [
                "Don't have the data for Q1",
                "Don't have the data for Q2",
                "Don't have the data for Q3",
                "Don't have the data for Q4"
            ]
        )
    ],
    ids=["q1_fails_others_succeed", "all_quarters_fail"]
)
@patch("finrobot.data_source.earnings_calls_src.main_earningsData.get_earnings_all_quarters_data")
def test_get_earnings_all_docs_retry_error(
    mock_get_data, capsys, side_effect_list, expected_quarters, expected_output_msgs
):
    """Verifica que la función principal maneje fallos de red/API mediante RetryError."""
    # Configurar el comportamiento del mock
    mock_get_data.side_effect = side_effect_list

    # Ejecución
    ticker = "AAPL"
    year = 2023
    result = get_earnings_all_docs(ticker, year)

    # Desempaquetado de resultados
    (
        earnings_docs,
        earnings_call_quarter_vals,
        speakers_list_1,
        speakers_list_2,
        speakers_list_3,
        speakers_list_4,
    ) = result

    # Verificar trimestres procesados
    assert earnings_call_quarter_vals == expected_quarters

    # Verificar que las listas de oradores estén vacías si el trimestre falló
    assert speakers_list_1 == ([] if isinstance(side_effect_list[0], Exception) else side_effect_list[0][1])
    assert speakers_list_2 == ([] if isinstance(side_effect_list[1], Exception) else side_effect_list[1][1])
    assert speakers_list_3 == ([] if isinstance(side_effect_list[2], Exception) else side_effect_list[2][1])
    assert speakers_list_4 == ([] if isinstance(side_effect_list[3], Exception) else side_effect_list[3][1])

    # Verificar mensajes en la salida estándar (stdout)
    captured = capsys.readouterr()
    for msg in expected_output_msgs:
        assert msg in captured.out
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
# Hemos unificado los casos de ambas ramas para máxima cobertura.

@pytest.mark.parametrize(
    "input_speaker, expected",
    [
        # Casos básicos y limpieza de caracteres
        ("John Doe\n", "John Doe"),
        ("Jane Smith:", "Jane Smith"),
        ("Bob\n:", "Bob"),
        ("John Doe:\n", "John Doe"),
        
        # Manejo de títulos corporativos y paréntesis
        ("John Doe (CEO)", "John Doe"),
        ("Jane Smith (Managing Director) (Analyst)", "Jane Smith"),
        ("Alice (VP)\n: ", "Alice"),
        ("Bob (CTO) \n (Interim CEO):", "Bob"),
        
        # Espacios y normalización
        ("  Dr. Robert Smith  ", "Dr. Robert Smith"),
        ("\n  Jane-Doe (CFO):  ", "Jane-Doe"),
        
        # Preservación de puntuación válida en nombres
        ("Mr. John A. Doe, Jr.", "Mr. John A. Doe, Jr."),
        ("O'Connor", "O'Connor"),
        ("Jean-Pierre", "Jean-Pierre"),
        
        # Programación defensiva: Tipos no-string
        (None, ""),
        (12345, "12345"),
        (12.34, "12.34"),
    ]
)
def test_clean_speakers(input_speaker, expected):
    """Verifica que la limpieza de nombres de oradores sea robusta y profesional."""
    assert clean_speakers(input_speaker) == expected


# --- SECCIÓN 2: Pruebas de manejo de errores y flujo de datos ---

def create_retry_error():
    """Helper para crear un RetryError realista. Simula un fallo tras reintentos de red."""
    mock_future = Mock(spec=Future)
    return RetryError(last_attempt=mock_future)

@pytest.mark.parametrize(
    "side_effect_list, expected_quarters, expected_output_msgs",
    [
        # Escenario 1: El Q1 falla por red, Q2-Q4 funcionan correctamente
        (
            [
                create_retry_error(), 
                ([Document(page_content="Q2", metadata={"speaker": "S2", "quarter": "Q2"})], ["S2"]),
                ([Document(page_content="Q3", metadata={"speaker": "S3", "quarter": "Q3"})], ["S3"]),
                ([Document(page_content="Q4", metadata={"speaker": "S4", "quarter": "Q4"})], ["S4"])
            ],
            ["Q2", "Q3", "Q4"],
            ["Don't have the data for Q1"]
        ),
        # Escenario 2: Apocalipsis de red - Todos los trimestres fallan
        (
            [create_retry_error() for _ in range(4)],
            [],
            [f"Don't have the data for Q{i}" for i in range(1, 5)]
        )
    ],
    ids=["q1_network_fail", "total_network_blackout"]
)
@patch("finrobot.data_source.earnings_calls_src.main_earningsData.get_earnings_all_quarters_data")
def test_get_earnings_all_docs_handling(
    mock_get_data, capsys, side_effect_list, expected_quarters, expected_output_msgs
):
    """
    Verifica que la orquestación principal no se detenga ante fallos de trimestres individuales.
    Esto es crítico para la usabilidad: si un trimestre falta, queremos los otros tres.
    """
    mock_get_data.side_effect = side_effect_list

    # Ejecución simulada para Apple 2023
    result = get_earnings_all_docs("AAPL", 2023)

    # Desempaquetado del resultado complejo
    (docs, quarters, q1_spk, q2_spk, q3_spk, q4_spk) = result

    # 1. Validar que solo se registraron los trimestres exitosos
    assert quarters == expected_quarters

    # 2. Validar manejo de listas de oradores (deben ser [] si el trimestre falló)
    spk_lists = [q1_spk, q2_spk, q3_spk, q4_spk]
    for i, effect in enumerate(side_effect_list):
        if isinstance(effect, Exception):
            assert spk_lists[i] == []
        else:
            assert spk_lists[i] == effect[1]

    # 3. Validar logs informativos para el usuario
    captured = capsys.readouterr()
    for msg in expected_output_msgs:
        assert msg in captured.out
from finrobot.data_source.earnings_calls_src.earningsData import get_earnings_transcript
import re
from langchain_core.documents import Document
from tenacity import RetryError


def clean_speakers(speaker):
    """Limpia y normaliza el nombre del orador extraído del transcript."""
    if speaker is None:
        return ""
    if not isinstance(speaker, str):
        speaker = str(speaker)

    # Eliminar saltos de línea y dos puntos (estándar de limpieza)
    speaker = speaker.replace("\n", "").replace(":", "")

    # Eliminar texto entre paréntesis (y los paréntesis mismos)
    speaker = re.sub(r"\(.*?\)", "", speaker)

    # Normalizar espacios en blanco erráticos (múltiples espacios a uno solo) y recortar extremos
    speaker = re.sub(r"\s+", " ", speaker).strip()

    return speaker


def get_earnings_all_quarters_data(quarter: str, ticker: str, year: int):
    """Extrae los documentos y la lista de oradores para un trimestre específico."""
    docs = []
    resp_dict = get_earnings_transcript(quarter, ticker, year)

    content = resp_dict["content"]
    # El patrón busca nombres seguidos de dos puntos al inicio de una línea
    pattern = re.compile(r"\n(.*?):")
    matches = pattern.finditer(content)

    speakers_list = []
    ranges = []
    for match_ in matches:
        span_range = match_.span()
        ranges.append(span_range)
        speakers_list.append(match_.group())
    
    # Limpiar todos los nombres de los oradores detectados
    speakers_list = [clean_speakers(sl) for sl in speakers_list]

    # Segmentar el contenido por cada orador
    for idx, speaker in enumerate(speakers_list[:-1]):
        start_range = ranges[idx][1]
        end_range = ranges[idx + 1][0]
        speaker_text = content[start_range + 1 : end_range]

        docs.append(
            Document(
                page_content=speaker_text,
                metadata={"speaker": speaker, "quarter": quarter},
            )
        )

    # Añadir la intervención del último orador (desde su nombre hasta el final)
    if ranges:
        docs.append(
            Document(
                page_content=content[ranges[-1][1] :],
                metadata={"speaker": speakers_list[-1], "quarter": quarter},
            )
        )
    
    return docs, speakers_list


def get_earnings_all_docs(ticker: str, year: int):
    """Orquesta la extracción de datos de todos los trimestres (Q1-Q4) para un año."""
    earnings_docs = []
    earnings_call_quarter_vals = []
    
    # Listas para almacenar oradores por cada trimestre
    results_speakers = {"Q1": [], "Q2": [], "Q3": [], "Q4": []}

    for q in ["Q1", "Q2", "Q3", "Q4"]:
        print(f"Earnings Call {q}")
        try:
            docs, speakers = get_earnings_all_quarters_data(q, ticker, year)
            earnings_call_quarter_vals.append(q)
            earnings_docs.extend(docs)
            results_speakers[q] = speakers
        except RetryError:
            print(f"Don't have the data for {q}")
            results_speakers[q] = []

    return (
        earnings_docs,
        earnings_call_quarter_vals,
        results_speakers["Q1"],
        results_speakers["Q2"],
        results_speakers["Q3"],
        results_speakers["Q4"],
    )
"""
SECUtils — Acceso gratuito a filings de la SEC via edgartools.

Reemplaza la versión original que dependía de sec-api.io (pago).
Usa edgartools para acceder directamente a SEC EDGAR sin coste.

La clase mantiene la MISMA interfaz pública que el original:
  - get_10k_metadata(ticker, start_date, end_date)
  - download_10k_filing(ticker, start_date, end_date, save_folder)
  - download_10k_pdf(ticker, start_date, end_date, save_folder)
  - get_10k_section(ticker, fyear, section, report_address, save_path)
"""

import os
import logging
from functools import wraps
from typing import Annotated

from edgar import Company, set_identity

from ..utils import SavePathType, decorate_all_methods

log = logging.getLogger(__name__)

CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")

# ── Mapping de secciones 10-K ──────────────────────────────
# El original usa números/letras: "1", "1A", "7", "7A", etc.
# edgartools usa get_item_with_part(part, item).
# Mapeamos la sección al (part, item) correspondiente.
SECTION_TO_PART_ITEM = {
    "1":   ("I", "1"),
    "1A":  ("I", "1A"),
    "1B":  ("I", "1B"),
    "1C":  ("I", "1C"),
    "2":   ("I", "2"),
    "3":   ("I", "3"),
    "4":   ("I", "4"),
    "5":   ("II", "5"),
    "6":   ("II", "6"),
    "7":   ("II", "7"),
    "7A":  ("II", "7A"),
    "8":   ("II", "8"),
    "9":   ("II", "9"),
    "9A":  ("II", "9A"),
    "9B":  ("II", "9B"),
    "9C":  ("II", "9C"),
    "10":  ("III", "10"),
    "11":  ("III", "11"),
    "12":  ("III", "12"),
    "13":  ("III", "13"),
    "14":  ("IV", "14"),
    "15":  ("IV", "15"),
}


def _ensure_identity():
    """Configura la identidad SEC (requerida por la SEC para scraping)."""
    name = os.environ.get("SEC_IDENTITY_NAME", "FinRobot Agent")
    email = os.environ.get("SEC_IDENTITY_EMAIL", "finrobot@example.com")
    set_identity(f"{name} {email}")


def init_edgar(func):
    """Decorator que inicializa edgartools antes de cada llamada."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        _ensure_identity()
        return func(*args, **kwargs)
    return wrapper


def _get_latest_10k(ticker: str, start_date: str | None = None, end_date: str | None = None):
    """
    Busca el último filing 10-K para el ticker dado, opcionalmente filtrado por rango de fechas.

    Args:
        ticker: símbolo bursátil
        start_date: fecha inicio en formato yyyy-mm-dd (opcional)
        end_date: fecha fin en formato yyyy-mm-dd (opcional)

    Returns:
        EntityFiling o None si no se encontró
    """
    company = Company(ticker)

    kwargs = {"form": "10-K"}
    if start_date and end_date:
        kwargs["filing_date"] = f"{start_date}:{end_date}"

    filings = company.get_filings(**kwargs)
    if filings.empty:
        return None

    return filings.latest(1)


@decorate_all_methods(init_edgar)
class SECUtils:

    def get_10k_metadata(
        ticker: Annotated[str, "ticker symbol"],
        start_date: Annotated[
            str, "start date of the 10-k file search range, in yyyy-mm-dd format"
        ],
        end_date: Annotated[
            str, "end date of the 10-k file search range, in yyyy-mm-dd format"
        ],
    ):
        """
        Search for 10-k filings within a given time period, and return the meta data of the latest one
        """
        filing = _get_latest_10k(ticker, start_date, end_date)
        if filing is None:
            return None

        # Devolver un dict compatible con el formato original de sec-api
        return {
            "ticker": ticker,
            "formType": filing.form,
            "filedAt": str(filing.filing_date),
            "linkToFilingDetails": filing.filing_url,
            "accessionNo": filing.accession_no or "",
            "companyName": filing.company,
        }

    def download_10k_filing(
        ticker: Annotated[str, "ticker symbol"],
        start_date: Annotated[
            str, "start date of the 10-k file search range, in yyyy-mm-dd format"
        ],
        end_date: Annotated[
            str, "end date of the 10-k file search range, in yyyy-mm-dd format"
        ],
        save_folder: Annotated[
            str, "name of the folder to store the downloaded filing"
        ],
    ) -> str:
        """Download the latest 10-K filing as htm for a given ticker within a given time period."""
        filing = _get_latest_10k(ticker, start_date, end_date)
        if filing is None:
            return f"No 10-K filing found for {ticker} between {start_date} and {end_date}"

        try:
            date_str = str(filing.filing_date)[:10]
            url = filing.filing_url
            file_name = f"{date_str}_10-K_{url.split('/')[-1]}"

            if not os.path.isdir(save_folder):
                os.makedirs(save_folder)

            file_content = filing.html()
            file_path = os.path.join(save_folder, file_name)
            with open(file_path, "w") as f:
                f.write(file_content)
            return f"{ticker}: download succeeded. Saved to {file_path}"
        except Exception as e:
            return f"❌ {ticker}: download failed: {e}"

    def download_10k_pdf(
        ticker: Annotated[str, "ticker symbol"],
        start_date: Annotated[
            str, "start date of the 10-k file search range, in yyyy-mm-dd format"
        ],
        end_date: Annotated[
            str, "end date of the 10-k file search range, in yyyy-mm-dd format"
        ],
        save_folder: Annotated[
            str, "name of the folder to store the downloaded pdf filing"
        ],
    ) -> str:
        """Download the latest 10-K filing as pdf for a given ticker within a given time period."""
        filing = _get_latest_10k(ticker, start_date, end_date)
        if filing is None:
            return f"No 10-K filing found for {ticker} between {start_date} and {end_date}"

        try:
            date_str = str(filing.filing_date)[:10]
            url = filing.filing_url
            file_name = f"{date_str}_10-K_{url.split('/')[-1]}.pdf"

            if not os.path.isdir(save_folder):
                os.makedirs(save_folder)

            # Descargar HTML y convertir a PDF con pdfkit
            import pdfkit
            html_content = filing.html()
            file_path = os.path.join(save_folder, file_name)
            pdfkit.from_string(html_content, file_path)
            return f"{ticker}: download succeeded. Saved to {file_path}"
        except Exception as e:
            return f"❌ {ticker}: download failed: {e}"

    def get_10k_section(
        ticker_symbol: Annotated[str, "ticker symbol"],
        fyear: Annotated[str, "fiscal year of the 10-K report"],
        section: Annotated[
            str | int,
            "Section of the 10-K report to extract, should be in [1, 1A, 1B, 2, 3, 4, 5, 6, 7, 7A, 8, 9, 9A, 9B, 10, 11, 12, 13, 14, 15]",
        ],
        report_address: Annotated[
            str,
            "URL of the 10-K report, if not specified, will get report url from fmp api",
        ] | None = None,
        save_path: SavePathType = None,
    ) -> str:
        """
        Get a specific section of a 10-K report from SEC EDGAR (via edgartools).
        """
        if isinstance(section, int):
            section = str(section)

        valid_sections = list(SECTION_TO_PART_ITEM.keys())
        if section not in valid_sections:
            raise ValueError(
                f"Section must be in {valid_sections}"
            )

        # ── Caché ──
        cache_path = os.path.join(
            CACHE_PATH, f"sec_utils/{ticker_symbol}_{fyear}_{section}.txt"
        )
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                section_text = f.read()
        else:
            # Buscar filing por año fiscal
            year = int(fyear) if fyear.isdigit() else None
            if year:
                # Buscar filings del año fiscal (normalmente filed en ese año o el siguiente)
                filing = _get_latest_10k(
                    ticker_symbol,
                    f"{year}-01-01",
                    f"{year + 1}-12-31",
                )
            else:
                filing = _get_latest_10k(ticker_symbol)

            if filing is None:
                return f"No 10-K filing found for {ticker_symbol} (fyear={fyear})"

            # Obtener el objeto TenK y extraer la sección
            tenk = filing.obj()
            part, item = SECTION_TO_PART_ITEM[section]

            try:
                section_text = tenk.get_item_with_part(part, item) or ""
            except Exception as e:
                log.warning(
                    "Could not extract section %s from %s 10-K: %s",
                    section, ticker_symbol, e
                )
                section_text = ""

            if not section_text:
                # Fallback: intentar propiedades directas del objeto TenK
                prop_map = {
                    "1": "business",
                    "1A": "risk_factors",
                    "7": "management_discussion",
                }
                prop = prop_map.get(section)
                if prop and hasattr(tenk, prop):
                    section_text = getattr(tenk, prop) or ""

            # Guardar en caché
            if section_text:
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                with open(cache_path, "w") as f:
                    f.write(section_text)

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "w") as f:
                f.write(section_text)

        return section_text

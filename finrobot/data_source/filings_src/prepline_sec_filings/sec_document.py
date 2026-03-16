from functools import partial
import re
from typing import List, Optional, Iterable, Iterator, Any, Tuple
import sys

if sys.version_info < (3, 8):
    from typing_extensions import Final
else:
    from typing import Final

import numpy as np
import numpy.typing as npt
from sklearn.cluster import DBSCAN
from collections import defaultdict

from unstructured.cleaners.core import clean
from unstructured.documents.elements import (
    Text,
    ListItem,
    NarrativeText,
    Title,
    Element,
)
from unstructured.documents.html import HTMLDocument

from unstructured.nlp.partition import is_possible_title
from finrobot.data_source.filings_src.prepline_sec_filings.sections import SECSection


VALID_FILING_TYPES: Final[List[str]] = [
    "10-K",
    "10-Q",
    "S-1",
    "10-K/A",
    "10-Q/A",
    "S-1/A",
]
REPORT_TYPES: Final[List[str]] = ["10-K", "10-Q", "10-K/A", "10-Q/A"]
S1_TYPES: Final[List[str]] = ["S-1", "S-1/A"]

# Regex robusta para capturar Items y Partes en diversos formatos (mayúsculas, minúsculas, con punto, etc.)
ITEM_TITLE_RE = re.compile(r"(?i)(?:item\s*\d{1,3}(?:[a-z]|\([a-z]\))?|part\s*[ivx]{1,4})(?:\.)?(?::)?")

clean_sec_text = partial(
    clean, extra_whitespace=True, dashes=True, trailing_punctuation=True
)


def _raise_for_invalid_filing_type(filing_type: Optional[str]):
    if not filing_type:
        raise ValueError("Filing type is empty.")
    elif filing_type not in VALID_FILING_TYPES:
        raise ValueError(
            f"Filing type was {filing_type}. Expected: {VALID_FILING_TYPES}"
        )


class SECDocument(HTMLDocument):
    filing_type = None

    def _filter_table_of_contents(self, elements: List[Text]) -> List[Text]:
        """Filtra elementos innecesarios en el TOC usando búsqueda por palabras clave."""
        if self.filing_type in REPORT_TYPES:
            start, end = None, None
            for i, element in enumerate(elements):
                if bool(re.match(r"(?i)part i\b", clean_sec_text(element.text))):
                    if start is None:
                        start = i
                    else:
                        end = i - 1
                        return elements[start:end]
        elif self.filing_type in S1_TYPES:
            title_indices = defaultdict(list)
            for i, element in enumerate(elements):
                clean_title_text = clean_sec_text(element.text).lower()
                title_indices[clean_title_text].append(i)
            
            duplicate_title_indices = {
                k: v for k, v in title_indices.items() if len(v) > 1
            }
            for title, indices in duplicate_title_indices.items():
                if "prospectus" in title and len(indices) == 2:
                    start = indices[0]
                    end = indices[1] - 1
                    return elements[start:end]
        return []

    def get_table_of_contents(self) -> HTMLDocument:
        """Identifica las secciones de texto que probablemente sean el índice (TOC)."""
        out_cls = self.__class__
        _raise_for_invalid_filing_type(self.filing_type)
        title_locs = to_sklearn_format(self.elements)
        
        if len(title_locs) == 0:
            return out_cls.from_elements([])

        # Usamos DBSCAN para encontrar clusters de títulos densamente agrupados
        res = DBSCAN(eps=6.0).fit_predict(title_locs)
        for i in range(res.max() + 1):
            idxs = cluster_num_to_indices(i, title_locs, res)
            cluster_elements: List[Text] = [self.elements[i] for i in idxs]
            
            # Verificamos si el cluster contiene tanto títulos de "Item" como títulos de "TOC"
            if any(
                [
                    # NOTA: Cambiamos 'risk_title' por algo más genérico para mayor flexibilidad.
                    is_item_title(el.text, self.filing_type)
                    for el in cluster_elements
                    if isinstance(el, Title)
                ]
            ) and any(
                [
                    is_toc_title(el.text)
                    for el in cluster_elements
                    if isinstance(el, Title)
                ]
            ):
                return out_cls.from_elements(
                    self._filter_table_of_contents(cluster_elements)
                )
        
        return out_cls.from_elements(self._filter_table_of_contents(self.elements))

    def get_section_narrative_no_toc(self, section: SECSection) -> List[NarrativeText]:
        """Identifica secciones narrativas sin usar el índice."""
        _raise_for_invalid_filing_type(self.filing_type)
        section_elements: List[NarrativeText] = list()
        in_section = False
        for element in self.elements:
            is_title = is_possible_title(element.text)
            if in_section:
                if is_title and is_item_title(element.text, self.filing_type):
                    if section_elements:
                        return section_elements
                    else:
                        in_section = False
                elif isinstance(element, (NarrativeText, ListItem)):
                    section_elements.append(element)

            if is_title and is_section_elem(section, element, self.filing_type):
                in_section = True

        return section_elements

    def get_section_narrative(self, section: SECSection) -> List[NarrativeText]:
        """Extrae la narrativa de una sección específica (ej: RISK_FACTORS)."""
        _raise_for_invalid_filing_type(self.filing_type)
        toc = self.get_table_of_contents()
        
        if not toc.pages:
            return self.get_section_narrative_no_toc(section)

        section_toc, next_section_toc = self._get_toc_sections(section, toc)
        if section_toc is None:
            return []

        doc_after_section_toc = self.after_element(
            next_section_toc if next_section_toc else section_toc
        )
        
        section_start_element = get_element_by_title(
            reversed(doc_after_section_toc.elements), section_toc.text, self.filing_type
        )
        if section_start_element is None:
            return []
            
        doc_after_section_heading = self.after_element(section_start_element)

        if self._is_last_section_in_report(section, toc) or next_section_toc is None:
            return get_narrative_texts(doc_after_section_heading, up_to_next_title=True)

        section_end_element = get_element_by_title(
            doc_after_section_heading.elements, next_section_toc.text, self.filing_type
        )

        if section_end_element is None:
            return get_narrative_texts(doc_after_section_heading, up_to_next_title=True)

        return get_narrative_texts(
            doc_after_section_heading.before_element(section_end_element)
        )

    def _get_toc_sections(self, section: SECSection, toc: HTMLDocument) -> Tuple[Text, Text]:
        section_toc = first(
            el for el in toc.elements if is_section_elem(section, el, self.filing_type)
        )
        if section_toc is None:
            return (None, None)

        after_section_toc = toc.after_element(section_toc)
        next_section_toc = first(
            el
            for el in after_section_toc.elements
            if not is_section_elem(section, el, self.filing_type)
        )
        return (section_toc, next_section_toc)

    def get_risk_narrative(self) -> List[NarrativeText]:
        return self.get_section_narrative(SECSection.RISK_FACTORS)

    def doc_after_cleaners(self, skip_headers_and_footers=False, skip_table_text=False, inplace=False) -> HTMLDocument:
        new_doc = super().doc_after_cleaners(skip_headers_and_footers, skip_table_text, inplace)
        if not inplace:
            new_doc.filing_type = self.filing_type
        return new_doc

    def _read_xml(self, content):
        super()._read_xml(content)
        type_tag = self.document_tree.find(".//type")
        if type_tag is not None:
            self.filing_type = type_tag.text.strip()
        return self.document_tree

    def _is_last_section_in_report(self, section: SECSection, toc: HTMLDocument) -> bool:
        if self.filing_type in ["10-K", "10-K/A"]:
            if section == SECSection.FORM_SUMMARY:
                return True
            if section == SECSection.EXHIBITS:
                return first(el for el in toc.elements if is_section_elem(SECSection.FORM_SUMMARY, el, self.filing_type)) is None
        if self.filing_type in ["10-Q", "10-Q/A"]:
            if section == SECSection.EXHIBITS:
                return True
        return False


# --- Funciones Auxiliares ---

def get_narrative_texts(doc: HTMLDocument, up_to_next_title: Optional[bool] = False) -> List[Text]:
    if up_to_next_title:
        narrative_texts = []
        for el in doc.elements:
            if isinstance(el, (NarrativeText, ListItem)):
                narrative_texts.append(el)
            else:
                break
        return narrative_texts
    return [el for el in doc.elements if isinstance(el, (NarrativeText, ListItem))]


def is_section_elem(section: SECSection, elem: Text, filing_type: Optional[str]) -> bool:
    _raise_for_invalid_filing_type(filing_type)
    if section is SECSection.RISK_FACTORS:
        return is_risk_title(elem.text, filing_type=filing_type)
    
    def _is_matching_section_pattern(text):
        return bool(re.search(section.pattern, clean_sec_text(text, lowercase=True)))

    if filing_type in REPORT_TYPES:
        return _is_matching_section_pattern(remove_item_from_section_text(elem.text))
    return _is_matching_section_pattern(elem.text)


def is_item_title(title: str, filing_type: Optional[str]) -> bool:
    if filing_type in REPORT_TYPES:
        return is_10k_item_title(title)
    elif filing_type in S1_TYPES:
        return is_s1_section_title(title)
    return False


def is_risk_title(title: str, filing_type: Optional[str]) -> bool:
    clean_text = clean_sec_text(title, lowercase=True)
    if filing_type in REPORT_TYPES:
        return is_10k_risk_title(clean_text)
    elif filing_type in S1_TYPES:
        return is_s1_risk_title(clean_text)
    return False


def is_toc_title(title: str) -> bool:
    clean_title = clean_sec_text(title, lowercase=True)
    return clean_title in ["table of contents", "index"]


def is_10k_item_title(title: str) -> bool:
    return ITEM_TITLE_RE.match(clean_sec_text(title, lowercase=True)) is not None


def is_10k_risk_title(title: str) -> bool:
    return ("1a" in title.lower() or "risk factors" in title.lower()) and "summary" not in title.lower()


def is_s1_section_title(title: str) -> bool:
    return title.strip().isupper()


def is_s1_risk_title(title: str) -> bool:
    return title.strip().lower() == "risk factors"


def to_sklearn_format(elements: List[Element]) -> npt.NDArray[np.float32]:
    """Interpreta las posiciones de los títulos como coordenadas en un espacio 1D."""
    is_title = np.array([is_possible_title(el.text) for el in elements], dtype=bool)
    title_locs = np.arange(len(is_title)).astype(np.float32)[is_title].reshape(-1, 1)
    return title_locs


def cluster_num_to_indices(num: int, elem_idxs: npt.NDArray[np.float32], res: npt.NDArray[np.int_]) -> List[int]:
    return elem_idxs[res == num].astype(int).flatten().tolist()


def first(it: Iterable) -> Any:
    try:
        return next(iter(it))
    except StopIteration:
        return None


def match_s1_toc_title_to_section(text: str, title: str) -> bool:
    return text == title


def match_10k_toc_title_to_section(text: str, title: str) -> bool:
    if re.match(ITEM_TITLE_RE, title):
        return text.startswith(title)
    return remove_item_from_section_text(text).startswith(title)


def remove_item_from_section_text(text: str) -> str:
    return re.sub(ITEM_TITLE_RE, "", text).strip()


def get_element_by_title(elements: Iterator[Element], title: str, filing_type: Optional[str]) -> Optional[Element]:
    _raise_for_invalid_filing_type(filing_type)
    match = match_10k_toc_title_to_section if filing_type in REPORT_TYPES else match_s1_toc_title_to_section
    return first(
        el for el in elements 
        if match(clean_sec_text(el.text, lowercase=True), clean_sec_text(title, lowercase=True))
    )

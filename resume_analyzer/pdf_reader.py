import io

import pdfplumber
import pymupdf

MIN_CHARS = 30  # less text than this is treated as "no readable text"


def _extract_with_pymupdf(pdf_bytes: bytes) -> str:
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
        return "\n".join(page.get_text() for page in doc)


def _extract_with_pdfplumber(pdf_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


EXTRACTORS = (_extract_with_pymupdf, _extract_with_pdfplumber)


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Try each extractor in turn and return the first usable text.

    Returns "" if the PDF opened but holds (almost) no text, e.g. a scan.
    Raises the last error if no extractor could open the file at all.
    """
    errors = []
    for extract in EXTRACTORS:
        try:
            text = extract(pdf_bytes)
        except Exception as exc:
            errors.append(exc)
            continue
        if len(text.strip()) >= MIN_CHARS:
            return text
    if len(errors) == len(EXTRACTORS):
        raise errors[-1]
    return ""
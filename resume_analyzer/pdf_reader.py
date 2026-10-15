import io

import pdfplumber


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Return all the text in a PDF, page by page."""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        parts = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(parts)
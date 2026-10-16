import pymupdf
import pytest

from resume_analyzer.pdf_reader import extract_text_from_pdf


def make_pdf(text: str = "") -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    if text:
        page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data


def test_extracts_text():
    pdf = make_pdf("Python developer with Flask and Docker experience")
    assert "Flask" in extract_text_from_pdf(pdf)


def test_blank_pdf_returns_empty_string():
    assert extract_text_from_pdf(make_pdf()) == ""


def test_corrupt_file_raises():
    with pytest.raises(Exception):
        extract_text_from_pdf(b"this is not a pdf")
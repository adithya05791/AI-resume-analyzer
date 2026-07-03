"""
Basic unit tests for the pure logic in app.py.

Run with:
    pytest test_app.py -v
"""
import pytest

from app import extract_keywords, extract_skills, calculate_similarity


def test_extract_keywords_removes_stopwords_and_lemmatizes():
    text = "I was managing a team of five engineers."
    keywords = extract_keywords(text)
    assert "manage" in keywords  # lemmatized from "managing"
    assert " was " not in f" {keywords} "  # stopword removed


def test_extract_keywords_empty_string():
    assert extract_keywords("") == ""


def test_extract_skills_finds_known_skills():
    text = "Experienced with Python, Docker, and React for backend and frontend work."
    skills = extract_skills(text)
    assert "python" in skills
    assert "docker" in skills
    assert "react" in skills


def test_extract_skills_no_match():
    skills = extract_skills("The quick brown fox jumps over the lazy dog.")
    assert skills == set()


def test_calculate_similarity_identical_text_is_high():
    score = calculate_similarity("python flask developer", "python flask developer")
    assert score > 0.9


def test_calculate_similarity_unrelated_text_is_low():
    score = calculate_similarity("python flask backend developer", "watercolor painting brushes canvas")
    assert score < 0.2


def test_calculate_similarity_empty_inputs_returns_zero():
    assert calculate_similarity("", "python developer") == 0.0
    assert calculate_similarity("python developer", "") == 0.0
    assert calculate_similarity("", "") == 0.0

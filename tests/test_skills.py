from resume_analyzer.pipeline import analyze
from resume_analyzer.skills import extract_skills


def test_word_boundaries():
    assert extract_skills("I know JavaScript") == {"JavaScript"}  # not Java


def test_alias():
    assert "Kubernetes" in extract_skills("deployed on k8s")


def test_missing_skill():
    result = analyze("Python and Flask developer", "Need Python, Flask, Docker")
    assert result["missing"] == ["Docker"]
    assert round(result["coverage"]) == 67


def test_empty_input():
    assert analyze("", "Python")["similarity"] == 0.0

def test_spring_boot():
    assert "Spring Boot" in extract_skills("Built APIs with Spring Boot")
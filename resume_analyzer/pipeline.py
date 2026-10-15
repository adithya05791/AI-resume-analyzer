from .similarity import text_similarity
from .skills import extract_skills


def analyze(resume_text: str, job_text: str) -> dict:
    resume_skills = extract_skills(resume_text)
    required = extract_skills(job_text)
    matched = required & resume_skills
    missing = required - resume_skills
    coverage = (len(matched) / len(required) * 100) if required else 0.0
    return {
        "similarity": text_similarity(resume_text, job_text),
        "coverage": coverage,
        "required": sorted(required),
        "matched": sorted(matched),
        "missing": sorted(missing),
    }
import os
import sqlite3
import uuid
from datetime import datetime

import PyPDF2
import spacy
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from spacy.matcher import PhraseMatcher

from skills_data import SKILLS

# --------------------------------------------------------------------------
# App / config
# --------------------------------------------------------------------------
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB upload limit
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

ALLOWED_EXTENSIONS = {"pdf"}
DB_PATH = "history.db"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Load spaCy model once at startup
nlp = spacy.load("en_core_web_sm")

# Build a phrase matcher for the skills vocabulary once, reused per request
skill_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
skill_matcher.add("SKILL", [nlp.make_doc(skill) for skill in SKILLS])


# --------------------------------------------------------------------------
# Database
# --------------------------------------------------------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_filename TEXT NOT NULL,
                job_desc_snippet TEXT NOT NULL,
                score REAL NOT NULL,
                matched_skills TEXT NOT NULL,
                missing_skills TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def save_analysis(resume_filename, job_desc, score, matched, missing):
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO analyses
                (resume_filename, job_desc_snippet, score, matched_skills, missing_skills, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                resume_filename,
                job_desc[:200],
                score,
                ", ".join(matched),
                ", ".join(missing),
                datetime.utcnow().isoformat(timespec="seconds"),
            ),
        )


def fetch_history(limit=25):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM analyses ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return rows


# --------------------------------------------------------------------------
# Core NLP helpers
# --------------------------------------------------------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF, tolerating pages with no extractable text
    (e.g. scanned/image-only pages, which PyPDF2 returns as None or "" for)."""
    text_parts = []
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts).strip()


def extract_keywords(text):
    """Lemmatized, stopword-free keyword string used for TF-IDF similarity."""
    doc = nlp(text)
    lemmas = [
        token.lemma_.lower()
        for token in doc
        if token.is_alpha and not token.is_stop and len(token.lemma_) > 1
    ]
    return " ".join(lemmas)


def extract_skills(text):
    """Return the set of known skill phrases found in the text."""
    doc = nlp(text.lower())
    matches = skill_matcher(doc)
    found = {doc[start:end].text for _, start, end in matches}
    return found


def calculate_similarity(resume_text, job_desc):
    """TF-IDF cosine similarity between two cleaned texts.
    Returns 0.0 if either text is empty after cleaning (empty vocabulary)."""
    if not resume_text.strip() or not job_desc.strip():
        return 0.0
    try:
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([resume_text, job_desc])
        return float(cosine_similarity(vectors[0:1], vectors[1:2])[0][0])
    except ValueError:
        # Happens if, after cleaning, there's no vocabulary at all
        # (e.g. text was only stopwords/punctuation).
        return 0.0


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files or not request.form.get("jobdesc", "").strip():
        flash("Please attach a resume PDF and paste a job description.")
        return redirect(url_for("index"))

    resume_file = request.files["resume"]
    job_desc = request.form["jobdesc"]

    if resume_file.filename == "":
        flash("No file selected.")
        return redirect(url_for("index"))

    if not allowed_file(resume_file.filename):
        flash("Only PDF files are supported.")
        return redirect(url_for("index"))

    # Prefix with a UUID so concurrent uploads never collide or overwrite
    # each other, while keeping the original name for display/debugging.
    original_name = secure_filename(resume_file.filename)
    unique_name = f"{uuid.uuid4().hex}_{original_name}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    resume_file.save(filepath)

    try:
        resume_text = extract_text_from_pdf(filepath)
    except Exception:
        flash("Couldn't read that PDF. It may be corrupted or encrypted.")
        return redirect(url_for("index"))
    finally:
        # Don't keep uploaded resumes around longer than needed.
        if os.path.exists(filepath):
            os.remove(filepath)

    if not resume_text:
        flash(
            "No extractable text found in that PDF. "
            "It may be a scanned image rather than a text-based PDF."
        )
        return redirect(url_for("index"))

    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_desc)

    similarity = calculate_similarity(resume_keywords, job_keywords)
    score = round(similarity * 100, 2)

    job_skills = extract_skills(job_desc)
    resume_skills = extract_skills(resume_text)
    matched_skills = sorted(job_skills & resume_skills)
    missing_skills = sorted(job_skills - resume_skills)

    save_analysis(original_name, job_desc, score, matched_skills, missing_skills)

    return render_template(
        "result.html",
        score=score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        filename=original_name,
    )


@app.route("/history")
def history():
    rows = fetch_history()
    return render_template("history.html", rows=rows)


if __name__ == "__main__":
    init_db()
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode)
else:
    # Ensure the table exists when imported (e.g. under a WSGI server or tests)
    init_db()

# AI-Powered Resume Analyzer

An intelligent web application that analyzes resumes and matches them to job
descriptions using Natural Language Processing (NLP) and similarity scoring.
Built with Python and Flask, this tool helps recruiters and job seekers
evaluate how well a resume aligns with a specific job posting — and see
*exactly* which skills matched and which are missing.

## Features

- **Resume upload** — upload a PDF resume via a styled drag-and-drop form
- **Text extraction** — parses PDF text with `PyPDF2`, tolerating pages
  with no extractable text (scanned/image pages)
- **Lemmatized keyword extraction** — spaCy NLP with lemmatization, not
  just raw stopword removal
- **Skills matching & explainability** — a `PhraseMatcher` over a curated
  skills vocabulary shows **matched** and **missing** skills as chips,
  not just a bare percentage
- **Similarity scoring** — TF-IDF + cosine similarity, shown as an
  animated circular gauge
- **History** — every analysis is saved to a local SQLite database and
  browsable on the `/history` page
- **Validation & security** — PDF-only uploads, 5MB size limit, UUID-based
  filenames (no collisions), uploaded files deleted immediately after
  processing, debug mode off by default
- **Tests** — a pytest suite covering the core NLP helper functions

## Tech Stack

| Component         | Technology       |
|------------------|------------------|
| Backend Framework | Flask            |
| NLP               | spaCy (lemmatization + PhraseMatcher) |
| PDF Parsing       | PyPDF2           |
| Similarity Model  | scikit-learn (TF-IDF + cosine similarity) |
| Persistence       | SQLite           |
| Frontend          | HTML/CSS (Jinja2), vanilla JS |
| Language          | Python 3         |

## Project Structure

```
ai_resume_analyzer/
├── app.py                 # Flask app, NLP logic, DB access
├── skills_data.py         # Curated skills vocabulary
├── requirements.txt
├── test_app.py            # pytest suite
├── uploads/                # scratch space, cleared after each request
├── static/
│   ├── style.css
│   └── script.js
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   └── history.html
└── .vscode/
    └── launch.json
```

## Installation

```bash
git clone https://github.com/adithya05791/ai_resume_analyzer.git
cd ai_resume_analyzer
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Usage

```bash
python app.py
```

Or without `launch.json`:

```bash
set FLASK_APP=app.py
set FLASK_ENV=development
flask run
```

Go to `http://127.0.0.1:5000/` in your browser.

To enable Flask's debugger during local development only:

```bash
set FLASK_DEBUG=1   # Windows
export FLASK_DEBUG=1  # macOS/Linux
```

## How It Works

1. Upload a resume PDF and paste a job description.
2. Text is extracted from the PDF and both texts are lemmatized and
   cleaned with spaCy.
3. A skills `PhraseMatcher` finds known skill phrases in both texts and
   reports the matched and missing sets.
4. TF-IDF + cosine similarity produces an overall match score.
5. The result page shows the score as a gauge, plus matched/missing
   skill chips. The run is saved to `history.db` and visible on
   `/history`.

## Running Tests

```bash
pytest test_app.py -v
```

## Dependencies

- Flask
- PyPDF2
- spaCy
- scikit-learn
- werkzeug
- pytest (dev/test only)

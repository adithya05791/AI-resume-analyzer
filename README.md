# AI Resume Analyzer

A Python web app that compares a resume (PDF) with a job description. It shows which skills the job asks for, which of them your resume covers, which it doesn't, and how closely the two texts match.

Built with Python, Streamlit, spaCy, PyMuPDF, pdfplumber and scikit-learn. Current version: **V2**.

<!-- Add a screenshot: save it as docs/screenshot.png, then uncomment the next line -->
<!-- ![App screenshot](docs/screenshot.png) -->

## Features

- Upload a text-based PDF resume and paste a job description (or load a built-in sample)
- Extracts resume text with **PyMuPDF**, with **pdfplumber** as an automatic fallback
- Detects skills in both texts with spaCy's `PhraseMatcher` and an editable skill list (`data/skills.json`)
- Reports **skill coverage**, **matched skills** and **skills not detected**
- Reports **text similarity** (TF-IDF and cosine similarity)
- Clear messages for empty inputs, unreadable PDFs, scanned PDFs and job descriptions that name no known skills
- Downloadable plain-text report
- Automated tests and an evaluation script that measures skill-extraction precision, recall and F1

## How it works

```
PDF resume ──► pdf_reader.py ──► resume text ─┐
                                              ├─► skills.py ──► matched / missing skills ─┐
Job description (pasted text) ────────────────┘                                           ├─► pipeline.py ──► app.py
                                              ┌─► similarity.py ──► TF-IDF similarity ────┘
```

1. **Text extraction:** `pdf_reader.py` tries PyMuPDF first. If it fails, or finds almost no text, it falls back to pdfplumber. A PDF with no readable text (for example a scan) is reported as such instead of crashing the app.
2. **Skill detection:** the text is cleaned of line breaks, tokenized by spaCy, and a `PhraseMatcher` looks for every alias listed in `data/skills.json`. Matching ignores case, and when matches overlap the longest one wins (so "Tailwind CSS" is not also counted as "CSS").
3. **Comparison:** skills found in the job description are the *required* skills. Required skills also found in the resume are *matched*, and the rest are *not detected*. Coverage is matched ÷ required.
4. **Text similarity:** both texts are turned into TF-IDF vectors and compared with cosine similarity.

### Reading the scores

- **Skill coverage** is the main signal. It only counts skills that exist in `data/skills.json`.
- **Text similarity** measures overlapping wording, not ability. It is often low when the job description is short, and it is **not** a prediction of being hired.

## Project structure

```
AI-resume-analyzer/
├── app.py                      # Streamlit interface
├── requirements.txt
├── README.md
├── results.md                  # evaluation score log
├── resume_analyzer/
│   ├── __init__.py
│   ├── pdf_reader.py           # PDF → text (PyMuPDF, pdfplumber fallback)
│   ├── skills.py               # spaCy skill matching
│   ├── similarity.py           # TF-IDF similarity
│   └── pipeline.py             # analyze(): combines everything
├── data/
│   └── skills.json             # skill names and their aliases
├── evaluation/
│   ├── __init__.py
│   ├── evaluate.py             # precision / recall / F1 script
│   ├── data_dev.py             # labeled development cases
│   └── data_holdout.py         # labeled holdout cases (used during development)
└── tests/
    ├── test_skills.py
    └── test_pdf_reader.py
```

## Installation

You need Python 3.11 or newer (developed on Python 3.13).

**Windows (Command Prompt or PowerShell)**

```
git clone https://github.com/adithya05791/AI-resume-analyzer.git
cd AI-resume-analyzer
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

On PowerShell, if activation is blocked, use `.venv\Scripts\Activate.ps1` or switch to Command Prompt.

**macOS / Linux**

```
git clone https://github.com/adithya05791/AI-resume-analyzer.git
cd AI-resume-analyzer
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Run the app

```
python -m streamlit run app.py
```

Open http://localhost:8501, upload a PDF resume, paste a job description (or click **Use sample job description**) and click **Analyze resume**. When you run the app locally, uploaded files are processed in memory and are not saved to disk by the app.

## Customize the skill list

Skills live in `data/skills.json`. Each key is the name shown to the user, and each value is a list of lowercase spellings to look for:

```json
{
  "Kubernetes": ["kubernetes", "k8s"],
  "Spring Boot": ["spring boot", "springboot"]
}
```

Add an entry, save the file and restart the app. Very short or everyday-English aliases (for example `go` or `express`) cause false matches, so prefer longer, unambiguous ones.

## Run the tests and evaluation

```
python -m pytest
python -m evaluation.evaluate            # development set
python -m evaluation.evaluate holdout    # holdout set
python -m pytest tests/test_pdf_reader.py -v #tests for a made up pdf
```

The tests cover skill matching (including word boundaries, aliases and empty input) and PDF reading (normal, blank and corrupt files).

The evaluation compares the skills the app detects with skills labeled by hand and reports:

- **Precision:** of the skills detected, how many were really there
- **Recall:** of the skills really there, how many were detected
- **F1:** the combined score

### Results so far

| Version | Method | Precision | Recall | F1 |
| --- | --- | --- | --- | --- |
| V1 | Regex, small hard-coded dictionary | 0.94 | 0.33 | 0.49 |
| V2 (first pass) | spaCy PhraseMatcher + `skills.json` | 0.94 | 0.44 | 0.60 |
| V2 (current) | Larger skill list, longest-match, label fixes | 1.00 | 0.82 | 0.90 |

These figures come from a 27-case holdout set built from real resume and job-posting text. **That set was used while improving the skill list, so it is a development result and overstates how the app will perform on new text.** A score on completely unseen data has not been measured yet. Most missed skills are simply not in the list: tools and concept phrases such as "process mapping".

## Limitations

- Only skills listed in skills.json` are detected; unknown tools and concept phrases are missed.
- Scanned or image-only PDFs can't be read (there is no OCR).
- It matches words, not meaning, so a synonym that isn't listed won't count.
- A mentioned skill is not proof of real experience.
- Complex PDF layouts (multiple columns, tables) may extract text in a confusing order.
- Scores are a screening aid, not a hiring decision.

## Roadmap

- [x] **V1:** PDF extraction, regex skill matching, TF-IDF similarity
- [x] **V2:** spaCy `PhraseMatcher`, editable skill list, PyMuPDF extraction with fallback, evaluation scripts, tests, Streamlit interface
- [ ] **V3:** semantic similarity with sentence embeddings, compared against the TF-IDF baseline
- [ ] **V4:** requirement-by-requirement matching with supporting resume evidence, skill-gap analysis and recommendations
- [ ] **V5:** broader tests, interface polish and deployment

## Tech stack

Python · Streamlit · spaCy · PyMuPDF · pdfplumber · scikit-learn · pytest

## Author

Built by [adithya05791](https://github.com/adithya05791)
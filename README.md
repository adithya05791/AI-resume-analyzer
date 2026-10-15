# AI Resume Analyzer

A Python web app that compares a resume (PDF) with a job description and shows which required skills the resume covers, which it doesn't, and how closely the two texts match.

Built with Python, Streamlit, spaCy, pdfplumber and scikit-learn. Current version: **V2**.

<!-- Add a screenshot: save it as docs/screenshot.png, then uncomment the next line -->
<!-- ![App screenshot](docs/screenshot.png) -->

## Features

- Upload a text-based PDF resume and paste a job description
- Detects skills in both texts using spaCy's `PhraseMatcher` and an editable skill list (`data/skills.json`)
- Reports **skill coverage** (required skills found in the resume), **matched skills** and **skills not detected**
- Reports **text similarity** using TF-IDF and cosine similarity
- Friendly handling of empty inputs, unreadable PDFs and job descriptions that name no known skills
- Downloadable plain-text report
- Evaluation scripts that measure skill-extraction precision, recall and F1, plus automated tests

## How it works

```
PDF resume ──► pdf_reader.py ──► resume text ─┐
                                              ├─► skills.py ──► matched / missing skills ─┐
Job description (pasted text) ────────────────┘                                           ├─► pipeline.py ──► app.py (results)
                                              ┌─► similarity.py ──► TF-IDF similarity ────┘
```

1. **Text extraction:** `pdfplumber` reads the text from each page of the PDF.
2. **Skill detection:** spaCy tokenizes the text and a `PhraseMatcher` looks for every alias listed in `data/skills.json`. Matching is case-insensitive, and when matches overlap the longest one wins (so "Tailwind CSS" doesn't also count as "CSS").
3. **Comparison:** skills found in the job description are the *required* skills. Those also found in the resume are *matched*; the rest are *not detected*. Coverage is matched ÷ required.
4. **Text similarity:** the resume and job description are converted to TF-IDF vectors and compared with cosine similarity.

### Reading the scores

- **Skill coverage** is the main signal. It only counts skills that exist in `data/skills.json`.
- **Text similarity** measures overlapping wording, not ability. It is often low when the job description is short, and it is **not** a prediction of being hired.

## Project structure

```
simple_resume_analyzer/
├── app.py                    # Streamlit interface
├── requirements.txt
├── resume_analyzer/
│   ├── __init__.py
│   ├── pdf_reader.py         # PDF → text
│   ├── skills.py             # spaCy skill matching
│   ├── similarity.py         # TF-IDF similarity
│   └── pipeline.py           # analyze(): combines everything
├── data/
│   └── skills.json           # skill names and their aliases
├── evaluation/
│   ├── evaluate.py           # precision / recall / F1 script
│   ├── data_dev.py           # labeled development cases
│   └── data_holdout.py       # labeled holdout cases (used during development)
└── tests/
    └── test_skills.py
```

## Installation (Windows)

You need Python 3.11 or newer (developed on Python 3.13).

```
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

On macOS or Linux, activate the environment with `source .venv/bin/activate` instead.

## Run the app

```
python -m streamlit run app.py
```

Open http://localhost:8501, upload a PDF resume, paste a job description (or click **Use sample job description**) and click **Analyze resume**. Uploaded files are processed in memory and are not written to disk by the app.

## Customize the skill list

Skills live in `data/skills.json`. Each key is the name shown to the user and each value is a list of lowercase spellings to look for:

```json
{
  "Kubernetes": ["kubernetes", "k8s"],
  "Spring Boot": ["spring boot", "springboot"]
}
```

Add an entry, save the file and restart the app. Very short or common-English aliases (for example `go` or `express`) cause false matches, so prefer longer, unambiguous ones.

## Run the tests and evaluation

```
python -m pytest
python -m evaluation.evaluate            # development set
python -m evaluation.evaluate holdout    # holdout set
```

The evaluation compares the skills the app detects against skills labeled by hand and reports:

- **Precision:** of the skills detected, how many were really there
- **Recall:** of the skills really there, how many were detected
- **F1:** the combined score

### Results so far

| Version | Method | Precision | Recall | F1 |
| --- | --- | --- | --- | --- |
| V1 | Regex, small hard-coded dictionary | 0.94 | 0.33 | 0.49 |
| V2 (first pass) | spaCy PhraseMatcher + `skills.json` | 0.94 | 0.44 | 0.60 |
| V2 (current) | Larger skill list, longest-match, label fixes | 1.00 | 0.82 | 0.90 |

These figures are from a 27-case holdout set built from real resume and job-posting text. **That set was used while improving the skill list, so it is a development result and overstates how the app will perform on new text.** A final score on completely unseen data has not been measured yet. The main source of missed skills is vocabulary: skills and concept phrases that are not in the list.

## Limitations

- Only skills listed in `data/skills.json` are detected; unknown tools and concept phrases (for example "process mapping") are missed.
- Scanned or image-only PDFs can't be read (there is no OCR).
- It matches words, not meaning, so a synonym that isn't listed won't count.
- A mentioned skill is not proof of real experience.
- Complex PDF layouts (multiple columns, tables) may extract text in a confusing order.
- Scores are a screening aid, not a hiring decision.

## Roadmap

- [x] **V1:** PDF extraction, regex skill matching, TF-IDF similarity
- [x] **V2:** spaCy `PhraseMatcher`, editable skill list, evaluation scripts, Streamlit interface
- [ ] **V3:** semantic similarity with sentence embeddings, compared against the TF-IDF baseline
- [ ] **V4:** requirement-by-requirement matching with supporting resume evidence, skill-gap analysis and recommendations
- [ ] **V5:** broader tests, interface polish and deployment

## Tech stack

Python · Streamlit · spaCy · pdfplumber · scikit-learn · pytest

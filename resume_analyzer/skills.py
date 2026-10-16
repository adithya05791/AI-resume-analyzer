import json
from pathlib import Path

import spacy
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span
from spacy.util import filter_spans

SKILLS_PATH = Path(__file__).resolve().parent.parent / "data" / "skills.json"

nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])


def load_skills(path: Path = SKILLS_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


SKILL_ALIASES = load_skills()

_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
for _skill, _aliases in SKILL_ALIASES.items():
    _matcher.add(_skill, [nlp.make_doc(alias) for alias in _aliases])


def extract_skills(text: str) -> set:
    """Find skills in text; when matches overlap, keep the longest one."""
    doc = nlp(" ".join(text.split()))
    spans = [
        Span(doc, start, end, label=match_id)
        for match_id, start, end in _matcher(doc)
    ]
    return {nlp.vocab.strings[span.label] for span in filter_spans(spans)}
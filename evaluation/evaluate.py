import importlib
import sys

from resume_analyzer.skills import extract_skills

DATASETS = {
    "dev": ("evaluation.data_dev", "EVAL_CASES"),
    "holdout": ("evaluation.data_holdout", "HOLDOUT_CASES"),
    "test": ("evaluation.data_test", "TEST_CASES"),
}

name = sys.argv[1] if len(sys.argv) > 1 else "dev"
if name not in DATASETS:
    sys.exit(f"Unknown dataset {name!r}. Choose from: {', '.join(DATASETS)}")

module_name, var_name = DATASETS[name]
cases = getattr(importlib.import_module(module_name), var_name)


def norm(skills):
    return {s.lower() for s in skills}

bad = [
    (i, c)
    for i, c in enumerate(cases)
    if not (
        isinstance(c, tuple)
        and len(c) == 2
        and isinstance(c[0], str)
        and isinstance(c[1], set)
    )
]
if bad:
    sys.exit(f"Malformed cases (index, value): {bad}")
tp = fp = fn = 0

for text, expected in cases:
    predicted = norm(extract_skills(text))
    gold = norm(expected)
    tp += len(predicted & gold)
    fp += len(predicted - gold)
    fn += len(gold - predicted)

    if predicted != gold:
        print(f"MISMATCH: {text!r}")
        print(f"  expected: {sorted(gold)}")
        print(f"  got:      {sorted(predicted)}")

precision = tp / (tp + fp) if (tp + fp) else 0.0
recall = tp / (tp + fn) if (tp + fn) else 0.0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

print()
print(f"Dataset:   {name}")
print(f"Cases:     {len(cases)}")
print(f"Precision: {precision:.2f}")
print(f"Recall:    {recall:.2f}")
print(f"F1:        {f1:.2f}")
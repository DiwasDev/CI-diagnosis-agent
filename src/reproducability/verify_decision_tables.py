"""Verify the decision-record tables against the source dataset.

Regenerates the §3 priors and the §6/§7 likelihood cross-tabulations from
`data/ci_repair_bench_disambiguated.parquet` and checks them against
`experiments/constants.py`, so the "empirically grounded" claim is checkable.

Priors and the E1 table regenerate exactly. For E2 the per-file categorization
rules were only partially recorded when the table was first derived, so the
script reports agreement instead of asserting equality.
"""

import sys
from collections import Counter
from pathlib import Path

import polars as pl

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.constants import PRIORS, STATES, LIKELIHOODS_E1

DATASET_PATH = PROJECT_ROOT / "data" / "ci_repair_bench_disambiguated.parquet"

STATE_NAMES = {
    "Source Code Issues": "S1_source_code_issues",
    "Project Config Issues": "S2_project_config_issues",
    "Dependency Failures": "S3_dependency_failures",
    "Static Analysis Failures": "S4_static_analysis_failures",
    "Test Failures": "S5_test_failures",
    "Environment Setup Issues": "S6_environment_setup_issues",
    "Other": "S7_other",
}

# Keyword buckets documented in probability_decision_record.md §6.
E1_BUCKETS = [
    ("A_install", ["install", "pip", "poetry", "conda", "requirements", "setup-python", "dependencies"]),
    ("B_build", ["build", "compile", "import", "py_compile"]),
    ("C_test", ["test", "pytest", "unittest", "coverage"]),
    ("D_static_analysis", ["lint", "flake8", "black", "mypy", "bandit", "ruff", "format", "pre-commit", "audit", "type"]),
    ("E_workflow", ["checkout", "setup", "provision", "yaml", "job", "environment"]),
]


def main():
    df = pl.read_parquet(DATASET_PATH)
    verify_priors(df)
    verify_e1_likelihoods(df)
    report_e2_agreement(df)


def verify_priors(df):
    total = df.height
    counts = {row["primary_hidden_state"]: row["len"]
              for row in df.group_by("primary_hidden_state").len().iter_rows(named=True)}
    for state in STATES:
        name = next(n for n, key in STATE_NAMES.items() if key == state)
        prior = counts.get(name, 0) / total
        assert abs(prior - PRIORS[state]) < 1e-4, f"{state}: dataset {prior:.4f} vs constants {PRIORS[state]}"
    print(f"priors: all {len(STATES)} state priors match constants exactly ({total} rows)")


def e1_bucket(step):
    lowered = step.lower()
    for outcome, keywords in E1_BUCKETS:
        if any(keyword in lowered for keyword in keywords):
            return outcome
    return "F_other"


def first_failed_step(failed_jobs):
    for job in failed_jobs:
        for step in job.get("steps", []):
            if step:
                return step
    return None


def verify_e1_likelihoods(df):
    """Smoothed P(step | state) = (raw + 1) / (n + 6) must match constants exactly."""
    buckets = {state: Counter() for state in STATES}
    for row in df.iter_rows(named=True):
        step = first_failed_step(row["failed_jobs"])
        state = STATE_NAMES[row["primary_hidden_state"]]
        buckets[state][e1_bucket(step) if step else "F_other"] += 1
    for state in STATES:
        n = sum(buckets[state].values()) + 6  # + 6 Laplace pseudo-counts
        for outcome, recorded in LIKELIHOODS_E1[state].items():
            smoothed = (buckets[state][outcome] + 1) / n
            assert abs(smoothed - recorded) < 1e-4, \
                f"E1 {state} {outcome}: dataset {smoothed:.4f} vs constants {recorded}"
    print("E1 likelihoods: all 42 cells regenerate exactly from the dataset")


def e2_file_category(path):
    lowered = path.lower()
    if lowered.startswith("test") or "/test" in lowered:
        return "test"
    if lowered.startswith("docs") or lowered.endswith((".md", ".rst")):
        return "doc"
    if lowered.startswith(".github") or lowered.endswith((".yml", ".yaml")):
        return "ci"
    if lowered.endswith((".toml", ".cfg", ".ini", ".lock", ".txt")) or \
            lowered.split("/")[-1] in ("setup.py", "setup.cfg", "manifest.in"):
        return "config"
    if lowered.endswith(".py"):
        return "src"
    return "other"


def e2_case_category(files):
    if not files:
        return "none"
    categories = {e2_file_category(file) for file in files}
    categories.discard("other")
    return categories.pop() if len(categories) == 1 else "mixed"


def report_e2_agreement(df):
    """Compare reconstructed raw counts with the §7 table recorded in the record."""
    recorded = {
        "S1_source_code_issues": {"src": 8, "test": 3, "config": 0, "ci": 0, "doc": 0, "mixed": 4, "none": 0},
        "S2_project_config_issues": {"src": 4, "test": 3, "config": 2, "ci": 0, "doc": 0, "mixed": 23, "none": 1},
        "S3_dependency_failures": {"src": 36, "test": 4, "config": 4, "ci": 1, "doc": 0, "mixed": 132, "none": 0},
        "S4_static_analysis_failures": {"src": 128, "test": 22, "config": 2, "ci": 0, "doc": 1, "mixed": 83, "none": 0},
        "S5_test_failures": {"src": 15, "test": 22, "config": 0, "ci": 0, "doc": 0, "mixed": 29, "none": 0},
        "S6_environment_setup_issues": {"src": 13, "test": 2, "config": 0, "ci": 0, "doc": 0, "mixed": 17, "none": 0},
        "S7_other": {"src": 0, "test": 5, "config": 0, "ci": 0, "doc": 0, "mixed": 3, "none": 0},
    }
    reconstructed = {state: Counter() for state in STATES}
    for row in df.iter_rows(named=True):
        state = STATE_NAMES[row["primary_hidden_state"]]
        reconstructed[state][e2_case_category(row["changed_files"])] += 1
    total_diff = sum(abs(reconstructed[s][o] - counts) for s in STATES for o, counts in recorded[s].items())
    for state in STATES:
        if dict(reconstructed[state]) != recorded[state]:
            diffs = {o: reconstructed[state][o] - recorded[state][o]
                     for o in recorded[state] if reconstructed[state][o] != recorded[state][o]}
            print(f"E2 {state}: differs in {sum(abs(d) for d in diffs.values())} cases {diffs}")
    print(f"E2 changed-file categories: reconstruction agrees on {df.height - total_diff} of {df.height} case classifications")


if __name__ == "__main__":
    main()

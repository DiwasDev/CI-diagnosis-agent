"""Benchmark loading, policy evaluation, and metric summaries.

This is the shared harness every experiment script uses: cases go in, one
`Decision` per case comes back, and every policy is scored identically.
"""

import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from experiments.constants import ACTION_COSTS, ACTION_LABELS, EVIDENCE_COSTS, STATE_TO_ACTION

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_PATH = PROJECT_ROOT / "data" / "benchmark_data" / "benchmark_cases_seed42.jsonl"

# Benchmark row keys for each evidence source, mapped to the case keys policies read.
EVIDENCE_SOURCES = {
    "E1_outcome": "evidence_e1_pipeline_step",
    "E2_outcome": "evidence_e2_changed_files",
    "E3_outcome": "evidence_e3_rerun_outcome",
    "E4_outcome": "evidence_e4_local_repro",
}


def load_cases(path: Path = BENCHMARK_PATH) -> pd.DataFrame:
    """Benchmark cases with ground-truth state/action and cleaned evidence outcomes.

    Rows without a ground-truth action are excluded, mirroring the notebook.
    """
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    cases = pd.DataFrame([_flatten_row(row) for row in rows])
    cases["ground_action"] = cases["ground_truth"].map(STATE_TO_ACTION)
    return cases.dropna(subset=["ground_action"]).reset_index(drop=True)


def _flatten_row(row: dict) -> dict:
    """One benchmark row -> one policy input; None marks an unavailable outcome."""
    case = {"case_id": row.get("case_id"), "ground_truth": row.get("true_hidden_state")}
    for outcome_key, source_key in EVIDENCE_SOURCES.items():
        value = row.get(source_key)
        case[outcome_key] = None if pd.isna(value) else value
    return case


def evaluate(policy, cases: pd.DataFrame, evidence_costs: dict | None = None) -> pd.DataFrame:
    """Run a policy on every case and record predictions and realised costs."""
    evidence_costs = evidence_costs or EVIDENCE_COSTS
    records = []
    for case in cases.to_dict(orient="records"):
        decision = policy.decide(case)
        records.append(
            {
                "ground_truth": case["ground_truth"],
                "ground_action": case["ground_action"],
                "prediction": decision.action,
                "info_cost": sum(evidence_costs[key] for key in decision.evidence_used),
                "decision_cost": ACTION_COSTS[decision.action][case["ground_truth"]],
                "evidence_used": decision.evidence_used,
            }
        )
    return pd.DataFrame(records)


def summarize(policy_name: str, records: pd.DataFrame) -> dict:
    """Classification, cost, and escalation metrics for one evaluated policy."""
    predictions = records["prediction"]
    decision_cost = records["decision_cost"].sum()
    info_cost = records["info_cost"].sum()
    total_cost = decision_cost + info_cost
    return {
        "policy": policy_name,
        "accuracy": accuracy_score(records["ground_action"], predictions),
        "precision_macro": precision_score(
            records["ground_action"], predictions, average="macro", labels=ACTION_LABELS, zero_division=0
        ),
        "recall_macro": recall_score(
            records["ground_action"], predictions, average="macro", labels=ACTION_LABELS, zero_division=0
        ),
        "f1_macro": f1_score(
            records["ground_action"], predictions, average="macro", labels=ACTION_LABELS, zero_division=0
        ),
        "total_decision_cost": decision_cost,
        "total_information_cost": info_cost,
        "total_cost": total_cost,
        "expected_cost_per_case": total_cost / len(records),
        "human_pct": (predictions == "Escalate").mean() * 100,
    }


def comparison_table(metrics: list[dict]) -> pd.DataFrame:
    """The headline metrics of several policies as one printable table."""
    columns = [
        "policy",
        "accuracy",
        "f1_macro",
        "total_information_cost",
        "total_decision_cost",
        "total_cost",
        "expected_cost_per_case",
        "human_pct",
    ]
    return pd.DataFrame(metrics)[columns]


def evidence_acquisition(records: pd.DataFrame, evidence_keys: tuple[str, ...] = ("E1", "E2", "E3", "E4")) -> dict:
    """How many evaluated cases acquired each evidence source."""
    return {key: sum(key in used for used in records["evidence_used"]) for key in evidence_keys}

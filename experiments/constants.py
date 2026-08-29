"""Shared constants and helpers for the CI diagnosis notebook."""

from __future__ import annotations

STATES = ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]

PRIORS = {
    "S1": 0.0265,
    "S2": 0.0582,
    "S3": 0.3122,
    "S4": 0.4162,
    "S5": 0.1164,
    "S6": 0.0564,
    "S7": 0.0141,
}

ACTION_LABELS = ["Escalate", "Fix Dependency", "Fix Lint"]
ACTION_ORDER = ["Escalate", "Fix Dependency", "Fix Lint"]
STATE_TO_ACTION = {
    "S1": "Fix Lint",
    "S2": "Fix Lint",
    "S3": "Fix Dependency",
    "S4": "Fix Lint",
    "S5": "Escalate",
    "S6": "Escalate",
    "S7": "Escalate",
}
EVIDENCE_ORDER = ["E1", "E2", "E3", "E4"]

EVIDENCE_COSTS = {
    "E1": 0.0,
    "E2": 0.0,
    "E3": 0.07,
    "E4": 33.33,
}

ACTION_COSTS = {
    "Escalate": {
        "S1": 50.0,
        "S2": 50.0,
        "S3": 50.0,
        "S4": 50.0,
        "S5": 50.0,
        "S6": 50.0,
        "S7": 50.0,
    },
    "Fix Dependency": {
        "S1": 75.07,
        "S2": 75.07,
        "S3": 8.33,
        "S4": 75.07,
        "S5": 75.07,
        "S6": 75.07,
        "S7": 75.07,
    },
    "Fix Lint": {
        "S1": 8.33,
        "S2": 8.33,
        "S3": 75.07,
        "S4": 8.33,
        "S5": 75.07,
        "S6": 75.07,
        "S7": 75.07,
    },
}

E1_LIKELIHOODS = {
    "S1": {"A": 0.0476, "B": 0.0952, "C": 0.4762, "D": 0.1429, "E": 0.0952, "F": 0.1429},
    "S2": {"A": 0.2308, "B": 0.0256, "C": 0.4359, "D": 0.0769, "E": 0.0769, "F": 0.1538},
    "S3": {"A": 0.1694, "B": 0.0164, "C": 0.4426, "D": 0.3279, "E": 0.0164, "F": 0.0273},
    "S4": {"A": 0.0248, "B": 0.0083, "C": 0.0785, "D": 0.6488, "E": 0.0248, "F": 0.2149},
    "S5": {"A": 0.0417, "B": 0.0417, "C": 0.6528, "D": 0.0417, "E": 0.0556, "F": 0.1667},
    "S6": {"A": 0.0526, "B": 0.0526, "C": 0.6842, "D": 0.0789, "E": 0.0526, "F": 0.0789},
    "S7": {"A": 0.1429, "B": 0.0714, "C": 0.5714, "D": 0.0714, "E": 0.0714, "F": 0.0714},
}

E2_LIKELIHOODS = {
    "S1": {"src": 0.4091, "test": 0.1818, "config": 0.0455, "ci": 0.0455, "doc": 0.0455, "mixed": 0.2273, "none": 0.0455},
    "S2": {"src": 0.1250, "test": 0.1000, "config": 0.0750, "ci": 0.0250, "doc": 0.0250, "mixed": 0.6000, "none": 0.0500},
    "S3": {"src": 0.2011, "test": 0.0272, "config": 0.0272, "ci": 0.0109, "doc": 0.0054, "mixed": 0.7228, "none": 0.0054},
    "S4": {"src": 0.5309, "test": 0.0947, "config": 0.0123, "ci": 0.0041, "doc": 0.0082, "mixed": 0.3457, "none": 0.0041},
    "S5": {"src": 0.2192, "test": 0.3151, "config": 0.0137, "ci": 0.0137, "doc": 0.0137, "mixed": 0.4110, "none": 0.0137},
    "S6": {"src": 0.3590, "test": 0.0769, "config": 0.0256, "ci": 0.0256, "doc": 0.0256, "mixed": 0.4615, "none": 0.0256},
    "S7": {"src": 0.0667, "test": 0.4000, "config": 0.0667, "ci": 0.0667, "doc": 0.0667, "mixed": 0.2667, "none": 0.0667},
}

E3_LIKELIHOODS = {
    "S1": {"pass_on_rerun": 0.05, "fail_on_rerun": 0.95},
    "S2": {"pass_on_rerun": 0.05, "fail_on_rerun": 0.95},
    "S3": {"pass_on_rerun": 0.15, "fail_on_rerun": 0.85},
    "S4": {"pass_on_rerun": 0.03, "fail_on_rerun": 0.97},
    "S5": {"pass_on_rerun": 0.35, "fail_on_rerun": 0.65},
    "S6": {"pass_on_rerun": 0.50, "fail_on_rerun": 0.50},
    "S7": {"pass_on_rerun": 0.75, "fail_on_rerun": 0.25},
}

E4_LIKELIHOODS = {
    "S1": {"reproducible_locally": 0.92, "not_reproducible_locally": 0.08},
    "S2": {"reproducible_locally": 0.80, "not_reproducible_locally": 0.20},
    "S3": {"reproducible_locally": 0.45, "not_reproducible_locally": 0.55},
    "S4": {"reproducible_locally": 0.88, "not_reproducible_locally": 0.12},
    "S5": {"reproducible_locally": 0.70, "not_reproducible_locally": 0.30},
    "S6": {"reproducible_locally": 0.12, "not_reproducible_locally": 0.88},
    "S7": {"reproducible_locally": 0.15, "not_reproducible_locally": 0.85},
}

LIKELIHOODS = {
    "E1": E1_LIKELIHOODS,
    "E2": E2_LIKELIHOODS,
    "E3": E3_LIKELIHOODS,
    "E4": E4_LIKELIHOODS,
}


def bayes_update(posterior, evidence_key, evidence_value):
    updated = {}
    for state in STATES:
        updated[state] = posterior[state] * LIKELIHOODS[evidence_key][state][evidence_value]
    total = sum(updated.values())
    return {state: updated[state] / total for state in STATES}


def compute_v1_case_cost(row):
    posterior = PRIORS.copy()
    info_cost = 0.0
    evidence_path = []
    chosen_action = "Escalate"

    for evidence_key in EVIDENCE_ORDER:
        outcome = row.get(f"{evidence_key}_outcome")
        if outcome is None:
            break

        posterior = bayes_update(posterior, evidence_key, outcome)
        info_cost += EVIDENCE_COSTS[evidence_key]
        evidence_path.append((evidence_key, outcome))
        chosen_action = action_from_posterior(posterior)
        if chosen_action in {"Fix Lint", "Fix Dependency"}:
            break

    state = row.get("ground_truth")
    decision_cost = ACTION_COSTS[chosen_action][state]
    return {
        "ground_truth": state,
        "evidence_path": evidence_path,
        "action": chosen_action,
        "info_cost": info_cost,
        "decision_cost": decision_cost,
        "total_cost": info_cost + decision_cost,
    }


def run_v1_policy(row):
    return compute_v1_case_cost(row)["action"]

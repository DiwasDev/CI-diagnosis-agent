"""
IID CI Failure Diagnosis Benchmark Generator
Generates 500 evaluation cases from a deterministic statistical simulator.
"""

import numpy as np
import json
import csv
from datetime import datetime, timezone
import os

# ============================================================
# CONFIGURATION
# ============================================================
SEED = 42
TARGET_CASES = 500
OUTPUT_DIR = "."

# ============================================================
# PROBABILITY TABLES (EXACT SPECIFICATION)
# ============================================================
states = ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]
priors = np.array([0.0265, 0.0582, 0.3122, 0.4162, 0.1164, 0.0564, 0.0141])

E1_outcomes = ["A", "B", "C", "D", "E", "F"]
E1_likelihoods_raw = {
    "S1": [0.0476, 0.0952, 0.4762, 0.1429, 0.0952, 0.1429],
    "S2": [0.2308, 0.0256, 0.4359, 0.0769, 0.0769, 0.1538],
    "S3": [0.1694, 0.0164, 0.4426, 0.3279, 0.0164, 0.0273],
    "S4": [0.0248, 0.0083, 0.0785, 0.6488, 0.0248, 0.2149],
    "S5": [0.0417, 0.0417, 0.6528, 0.0417, 0.0556, 0.1667],
    "S6": [0.0526, 0.0526, 0.6842, 0.0789, 0.0526, 0.0789],
    "S7": [0.1429, 0.0714, 0.5714, 0.0714, 0.0714, 0.0714],
}

E2_outcomes = ["src", "test", "config", "ci", "doc", "mixed", "none"]
E2_likelihoods_raw = {
    "S1": [0.4091, 0.1818, 0.0455, 0.0455, 0.0455, 0.2273, 0.0455],
    "S2": [0.1250, 0.1000, 0.0750, 0.0250, 0.0250, 0.6000, 0.0500],
    "S3": [0.2011, 0.0272, 0.0272, 0.0109, 0.0054, 0.7228, 0.0054],
    "S4": [0.5309, 0.0947, 0.0123, 0.0041, 0.0082, 0.3457, 0.0041],
    "S5": [0.2192, 0.3151, 0.0137, 0.0137, 0.0137, 0.4110, 0.0137],
    "S6": [0.3590, 0.0769, 0.0256, 0.0256, 0.0256, 0.4615, 0.0256],
    "S7": [0.0667, 0.4000, 0.0667, 0.0667, 0.0667, 0.2667, 0.0667],
}

E3_outcomes = ["pass_on_rerun", "fail_on_rerun"]
E3_likelihoods_raw = {
    "S1": [0.05, 0.95],
    "S2": [0.05, 0.95],
    "S3": [0.15, 0.85],
    "S4": [0.03, 0.97],
    "S5": [0.35, 0.65],
    "S6": [0.50, 0.50],
    "S7": [0.75, 0.25],
}

E4_outcomes = ["reproducible_locally", "not_reproducible_locally"]
E4_likelihoods_raw = {
    "S1": [0.92, 0.08],
    "S2": [0.80, 0.20],
    "S3": [0.45, 0.55],
    "S4": [0.88, 0.12],
    "S5": [0.70, 0.30],
    "S6": [0.12, 0.88],
    "S7": [0.15, 0.85],
}

# Normalize likelihoods to sum to exactly 1.0
E1_likelihoods = {s: np.array(v) / np.sum(v) for s, v in E1_likelihoods_raw.items()}
E2_likelihoods = {s: np.array(v) / np.sum(v) for s, v in E2_likelihoods_raw.items()}
E3_likelihoods = {s: np.array(v) / np.sum(v) for s, v in E3_likelihoods_raw.items()}
E4_likelihoods = {s: np.array(v) / np.sum(v) for s, v in E4_likelihoods_raw.items()}

# ============================================================
# REJECTION FILTERS
# ============================================================
def is_rejected(e1, e2, e3, e4):
    if e1 == "D" and e3 == "pass_on_rerun":
        return True
    if e1 == "D" and e2 == "doc":
        return True
    if e3 == "pass_on_rerun" and e4 == "reproducible_locally":
        return True
    return False

# ============================================================
# GENERATION
# ============================================================
def sample_case(rng):
    state_idx = rng.choice(len(states), p=priors)
    state = states[state_idx]
    e1 = E1_outcomes[rng.choice(len(E1_outcomes), p=E1_likelihoods[state])]
    e2 = E2_outcomes[rng.choice(len(E2_outcomes), p=E2_likelihoods[state])]
    e3 = E3_outcomes[rng.choice(len(E3_outcomes), p=E3_likelihoods[state])]
    e4 = E4_outcomes[rng.choice(len(E4_outcomes), p=E4_likelihoods[state])]
    return state, e1, e2, e3, e4

def generate_cases(seed=SEED, target=TARGET_CASES):
    rng = np.random.default_rng(seed)
    cases = []
    case_id = 0
    total_draws = 0

    while len(cases) < target:
        total_draws += 1
        state, e1, e2, e3, e4 = sample_case(rng)
        if is_rejected(e1, e2, e3, e4):
            continue

        case = {
            "test_id": f"case_{case_id:04d}",
            "split": "test",
            "seed": seed,
            "ground_truth_state": state,
            "E1": e1,
            "E2": e2,
            "E3": e3,
            "E4": e4,
            "generation_method": "deterministic_statistical_simulator",
            "distribution_type": "iid_in_distribution",
            "conditional_independence_assumption": True,
            "prior_source": "empirical",
            "likelihood_source": {
                "E1": "empirical",
                "E2": "empirical",
                "E3": "assumed",
                "E4": "assumed"
            },
            "rejection_filters_applied": [
                "E1=D AND E3=pass_on_rerun",
                "E1=D AND E2=doc",
                "E3=pass_on_rerun AND E4=reproducible_locally"
            ]
        }
        cases.append(case)
        case_id += 1

    return cases, total_draws

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    cases, total_draws = generate_cases()

    # Save JSONL
    with open(os.path.join(OUTPUT_DIR, "iid_ci_agent_cases.jsonl"), "w") as f:
        for case in cases:
            f.write(json.dumps(case) + "\n")

    # Save CSV
    csv_columns = ["test_id", "split", "seed", "ground_truth_state", "E1", "E2", "E3", "E4"]
    with open(os.path.join(OUTPUT_DIR, "iid_ci_agent_cases.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns)
        writer.writeheader()
        for case in cases:
            writer.writerow({k: case[k] for k in csv_columns})

    # Save metadata
    metadata = {
        "seed": SEED,
        "number_of_cases": TARGET_CASES,
        "total_draws": total_draws,
        "rejection_rate": (total_draws - TARGET_CASES) / total_draws,
        "rejection_filters": [
            "E1=D AND E3=pass_on_rerun",
            "E1=D AND E2=doc",
            "E3=pass_on_rerun AND E4=reproducible_locally"
        ],
        "prior_table": {s: float(p) for s, p in zip(states, priors)},
        "likelihood_tables": {
            "E1": E1_likelihoods_raw,
            "E2": E2_likelihoods_raw,
            "E3": E3_likelihoods_raw,
            "E4": E4_likelihoods_raw,
        },
        "conditional_independence_assumption": True,
        "generation_method": "deterministic_statistical_simulator",
        "distribution_type": "iid_in_distribution",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "generator_version": "1.0.0",
        "outcome_spaces": {
            "E1": E1_outcomes,
            "E2": E2_outcomes,
            "E3": E3_outcomes,
            "E4": E4_outcomes
        }
    }
    with open(os.path.join(OUTPUT_DIR, "generation_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Generated {len(cases)} cases from {total_draws} draws.")
#!/usr/bin/env python3
"""
Generate out-of-distribution (OOD) benchmark test cases for CI failure diagnosis agent.
Saves the dataset as a JSON file.
"""

import json
from pathlib import Path
import numpy as np

# Set up paths
project_root = Path(__file__).resolve().parent.parent.parent

# Hidden states
HIDDEN_STATES = [
    "S1_source_code_issues",
    "S2_project_config_issues",
    "S3_dependency_failures",
    "S4_static_analysis_failures",
    "S5_test_failures",
    "S6_environment_setup_issues",
    "S7_other",
]

# Evidence outcomes
EVIDENCE_E1_OUTCOMES = ["A_install", "B_build", "C_test", "D_static_analysis", "E_workflow", "F_other"]
EVIDENCE_E2_OUTCOMES = ["src", "test", "config", "ci", "doc", "mixed", "none"]
EVIDENCE_E3_OUTCOMES = ["pass_on_rerun", "fail_on_rerun"]
EVIDENCE_E4_OUTCOMES = ["reproducible_locally", "not_reproducible_locally"]

# OOD Priors (significantly shifted compared to the original empirical priors)
OOD_PRIORS = {
    "S1_source_code_issues": 0.25,
    "S2_project_config_issues": 0.20,
    "S3_dependency_failures": 0.15,
    "S4_static_analysis_failures": 0.10,
    "S5_test_failures": 0.15,
    "S6_environment_setup_issues": 0.10,
    "S7_other": 0.05
}

# OOD Likelihoods (significantly shifted)
OOD_LIKELIHOODS_E1 = {
    "S1_source_code_issues": [0.20, 0.20, 0.20, 0.20, 0.10, 0.10],
    "S2_project_config_issues": [0.10, 0.40, 0.10, 0.10, 0.20, 0.10],
    "S3_dependency_failures": [0.40, 0.10, 0.10, 0.10, 0.10, 0.20],
    "S4_static_analysis_failures": [0.10, 0.10, 0.10, 0.50, 0.10, 0.10],
    "S5_test_failures": [0.10, 0.10, 0.50, 0.10, 0.10, 0.10],
    "S6_environment_setup_issues": [0.30, 0.30, 0.10, 0.10, 0.10, 0.10],
    "S7_other": [0.1666, 0.1666, 0.1666, 0.1666, 0.1668, 0.1668],
}

OOD_LIKELIHOODS_E2 = {
    "S1_source_code_issues": [0.10, 0.10, 0.10, 0.10, 0.10, 0.40, 0.10],
    "S2_project_config_issues": [0.40, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10],
    "S3_dependency_failures": [0.10, 0.40, 0.10, 0.10, 0.10, 0.10, 0.10],
    "S4_static_analysis_failures": [0.10, 0.10, 0.40, 0.10, 0.10, 0.10, 0.10],
    "S5_test_failures": [0.10, 0.10, 0.10, 0.40, 0.10, 0.10, 0.10],
    "S6_environment_setup_issues": [0.10, 0.10, 0.10, 0.10, 0.40, 0.10, 0.10],
    "S7_other": [0.1428, 0.1428, 0.1428, 0.1428, 0.1428, 0.1428, 0.1432],
}

OOD_LIKELIHOODS_E3 = {
    "S1_source_code_issues": [0.50, 0.50],
    "S2_project_config_issues": [0.40, 0.60],
    "S3_dependency_failures": [0.60, 0.40],
    "S4_static_analysis_failures": [0.70, 0.30],
    "S5_test_failures": [0.20, 0.80],
    "S6_environment_setup_issues": [0.80, 0.20],
    "S7_other": [0.50, 0.50],
}

OOD_LIKELIHOODS_E4 = {
    "S1_source_code_issues": [0.30, 0.70],
    "S2_project_config_issues": [0.50, 0.50],
    "S3_dependency_failures": [0.60, 0.40],
    "S4_static_analysis_failures": [0.40, 0.60],
    "S5_test_failures": [0.70, 0.30],
    "S6_environment_setup_issues": [0.80, 0.20],
    "S7_other": [0.50, 0.50],
}

def main():
    seed = 42
    num_cases = 500
    rng = np.random.RandomState(seed)
    
    cases = []
    for case_id in range(num_cases):
        # Sample hidden state from OOD priors
        states = list(OOD_PRIORS.keys())
        p_priors = list(OOD_PRIORS.values())
        state = rng.choice(states, p=p_priors)
        
        # Sample E1
        p_e1 = np.array(OOD_LIKELIHOODS_E1[state])
        p_e1 /= p_e1.sum()
        e1 = EVIDENCE_E1_OUTCOMES[rng.choice(len(EVIDENCE_E1_OUTCOMES), p=p_e1)]
        
        # Sample E2
        p_e2 = np.array(OOD_LIKELIHOODS_E2[state])
        p_e2 /= p_e2.sum()
        e2 = EVIDENCE_E2_OUTCOMES[rng.choice(len(EVIDENCE_E2_OUTCOMES), p=p_e2)]
        
        # Sample E3
        p_e3 = np.array(OOD_LIKELIHOODS_E3[state])
        p_e3 /= p_e3.sum()
        e3 = EVIDENCE_E3_OUTCOMES[rng.choice(len(EVIDENCE_E3_OUTCOMES), p=p_e3)]
        
        # Sample E4
        p_e4 = np.array(OOD_LIKELIHOODS_E4[state])
        p_e4 /= p_e4.sum()
        e4 = EVIDENCE_E4_OUTCOMES[rng.choice(len(EVIDENCE_E4_OUTCOMES), p=p_e4)]
        
        cases.append({
            "case_id": case_id,
            "true_hidden_state": state,
            "evidence_e1_pipeline_step": e1,
            "evidence_e2_changed_files": e2,
            "evidence_e3_rerun_outcome": e3,
            "evidence_e4_local_repro": e4
        })
        
    output_dir = project_root / "data" / "benchmark_data"
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "benchmark_cases_ood.json"
    
    with open(json_path, "w") as f:
        json.dump({
            "metadata": {
                "seed": seed,
                "num_cases": num_cases,
                "hidden_states": HIDDEN_STATES,
                "evidence_e1_outcomes": EVIDENCE_E1_OUTCOMES,
                "evidence_e2_outcomes": EVIDENCE_E2_OUTCOMES,
                "evidence_e3_outcomes": EVIDENCE_E3_OUTCOMES,
                "evidence_e4_outcomes": EVIDENCE_E4_OUTCOMES,
                "priors": OOD_PRIORS,
                "likelihoods": {
                    "E1": OOD_LIKELIHOODS_E1,
                    "E2": OOD_LIKELIHOODS_E2,
                    "E3": OOD_LIKELIHOODS_E3,
                    "E4": OOD_LIKELIHOODS_E4,
                }
            },
            "cases": cases
        }, f, indent=2)
        
    print(f"Generated {num_cases} OOD test cases.")
    print(f"OOD JSON dataset saved to: {json_path}")

if __name__ == "__main__":
    main()

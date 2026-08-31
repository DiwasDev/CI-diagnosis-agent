#!/usr/bin/env python3
"""
Check distribution drift between old and new (OOD) benchmark datasets.
Computes Jensen-Shannon divergence for priors, marginal evidence outcomes,
and conditional evidence outcomes.
Generates drift_report.md.
"""

import json
import math
from pathlib import Path
import numpy as np

# Set up project root in path
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

# Evidence keys and outcomes mapping
EVIDENCE_OUTCOMES = {
    "E1": ["A_install", "B_build", "C_test", "D_static_analysis", "E_workflow", "F_other"],
    "E2": ["src", "test", "config", "ci", "doc", "mixed", "none"],
    "E3": ["pass_on_rerun", "fail_on_rerun"],
    "E4": ["reproducible_locally", "not_reproducible_locally"]
}

EVIDENCE_DISPLAY_NAMES = {
    "E1": "E1 (Pipeline Step)",
    "E2": "E2 (Changed Files)",
    "E3": "E3 (Rerun Outcome)",
    "E4": "E4 (Local Repro)"
}

EVIDENCE_CASE_KEYS = {
    "E1": "evidence_e1_pipeline_step",
    "E2": "evidence_e2_changed_files",
    "E3": "evidence_e3_rerun_outcome",
    "E4": "evidence_e4_local_repro"
}

DRIFT_THRESHOLD = 0.05

def js_divergence(p, q):
    """
    Compute Jensen-Shannon divergence between two probability distributions p and q.
    Uses base 2 logarithm so JS divergence is bounded between 0.0 and 1.0.
    """
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    
    # Handle edge case where one or both distributions are empty
    if np.sum(p) == 0 or np.sum(q) == 0:
        if np.sum(p) == np.sum(q):
            return 0.0
        return 1.0
        
    p = p / np.sum(p)
    q = q / np.sum(q)
    
    m = 0.5 * (p + q)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        kl_p = np.sum(np.where(p > 0, p * np.log2(p / np.where(m > 0, m, 1.0)), 0.0))
        kl_q = np.sum(np.where(q > 0, q * np.log2(q / np.where(m > 0, m, 1.0)), 0.0))
    
    return 0.5 * (kl_p + kl_q)

def binary_js_divergence(p_val, q_val):
    """Compute JS divergence of binary Bernoulli trials with probabilities p_val and q_val."""
    p_dist = [p_val, 1.0 - p_val]
    q_dist = [q_val, 1.0 - q_val]
    return js_divergence(p_dist, q_dist)

def get_drift_alert(js_val):
    return "🚨 YES" if js_val >= DRIFT_THRESHOLD else "✅ NO"

def main():
    # Load old and new datasets
    old_path = project_root / "data" / "benchmark_data" / "benchmark_cases_seed42.json"
    new_path = project_root / "data" / "benchmark_data" / "benchmark_cases_ood.json"
    
    if not old_path.exists():
        raise FileNotFoundError(f"Original dataset not found at {old_path}")
    if not new_path.exists():
        raise FileNotFoundError(f"New OOD dataset not found at {new_path}")
        
    print(f"Loading baseline dataset: {old_path}")
    with open(old_path, 'r') as f:
        data_old = json.load(f)
        
    print(f"Loading OOD dataset: {new_path}")
    with open(new_path, 'r') as f:
        data_new = json.load(f)
        
    cases_old = data_old["cases"]
    cases_new = data_new["cases"]
    
    N_old = len(cases_old)
    N_new = len(cases_new)
    
    # 1. Priors comparison
    states_old = [c["true_hidden_state"] for c in cases_old]
    states_new = [c["true_hidden_state"] for c in cases_new]
    
    priors_old = [states_old.count(s) / N_old for s in HIDDEN_STATES]
    priors_new = [states_new.count(s) / N_new for s in HIDDEN_STATES]
    
    js_priors = js_divergence(priors_old, priors_new)
    alert_priors = get_drift_alert(js_priors)
    
    # 2. Marginal Evidences comparison
    marginal_rows = []
    
    # Prior row (for final report table)
    marginal_rows.append({
        "evidence": "Priors (Hidden States)",
        "outcome": "Overall State Distribution",
        "js": js_priors,
        "alert": alert_priors
    })
    
    for ev_key in ["E1", "E2", "E3", "E4"]:
        case_key = EVIDENCE_CASE_KEYS[ev_key]
        display_name = EVIDENCE_DISPLAY_NAMES[ev_key]
        outcomes_list = EVIDENCE_OUTCOMES[ev_key]
        
        obs_old = [c[case_key] for c in cases_old]
        obs_new = [c[case_key] for c in cases_new]
        
        # Overall marginal JS
        dist_old = [obs_old.count(o) / N_old for o in outcomes_list]
        dist_new = [obs_new.count(o) / N_new for o in outcomes_list]
        js_overall = js_divergence(dist_old, dist_new)
        
        marginal_rows.append({
            "evidence": display_name,
            "outcome": "Overall Outcome Distribution",
            "js": js_overall,
            "alert": get_drift_alert(js_overall)
        })
        
        # Individual outcomes binary JS
        for o in outcomes_list:
            p_old = obs_old.count(o) / N_old
            p_new = obs_new.count(o) / N_new
            js_o = binary_js_divergence(p_old, p_new)
            
            marginal_rows.append({
                "evidence": display_name,
                "outcome": f"Outcome: {o}",
                "js": js_o,
                "alert": get_drift_alert(js_o)
            })

    # 3. Conditional Evidences comparison (likelihoods per state)
    conditional_rows = []
    for ev_key in ["E1", "E2", "E3", "E4"]:
        case_key = EVIDENCE_CASE_KEYS[ev_key]
        display_name = EVIDENCE_DISPLAY_NAMES[ev_key]
        outcomes_list = EVIDENCE_OUTCOMES[ev_key]
        
        for state in HIDDEN_STATES:
            obs_old_s = [c[case_key] for c in cases_old if c["true_hidden_state"] == state]
            obs_new_s = [c[case_key] for c in cases_new if c["true_hidden_state"] == state]
            
            n_old_s = len(obs_old_s)
            n_new_s = len(obs_new_s)
            
            dist_old_s = [obs_old_s.count(o) / n_old_s if n_old_s > 0 else 0.0 for o in outcomes_list]
            dist_new_s = [obs_new_s.count(o) / n_new_s if n_new_s > 0 else 0.0 for o in outcomes_list]
            
            js_cond = js_divergence(dist_old_s, dist_new_s)
            
            conditional_rows.append({
                "evidence": display_name,
                "state": state,
                "n_old": n_old_s,
                "n_new": n_new_s,
                "js": js_cond,
                "alert": get_drift_alert(js_cond)
            })

    # Generate the Markdown report
    output_lines = []
    output_lines.append("# Distribution Drift Analysis Report")
    output_lines.append("")
    output_lines.append("This report checks for distribution shift between the baseline dataset and the newly generated out-of-distribution (OOD) dataset.")
    output_lines.append("")
    output_lines.append(f"- **Baseline Dataset:** `{old_path.name}` ({N_old} cases)")
    output_lines.append(f"- **OOD Dataset:** `{new_path.name}` ({N_new} cases)")
    output_lines.append(f"- **Drift Alert Threshold:** JS Divergence $\\ge {DRIFT_THRESHOLD}$")
    output_lines.append("")
    output_lines.append("---")
    output_lines.append("")
    output_lines.append("## Priors & Marginal Outcomes Drift")
    output_lines.append("")
    output_lines.append("| Name of Evidence | Outcome | JS Divergence | Is Drift Alert |")
    output_lines.append("|---|---|---|---|")
    
    # We display the rows. Prior first.
    for r in marginal_rows:
        output_lines.append(f"| {r['evidence']} | {r['outcome']} | {r['js']:.4f} | {r['alert']} |")
        
    output_lines.append("")
    output_lines.append("---")
    output_lines.append("")
    output_lines.append("## Conditional Likelihood Shift per Hidden State")
    output_lines.append("")
    output_lines.append("This section compares the conditional evidence distribution $P(\\text{Evidence} \\mid \\text{Hidden State})$ between datasets to inspect shifts in likelihood functions.")
    output_lines.append("")
    output_lines.append("| Name of Evidence | Hidden State | N (Baseline) | N (OOD) | JS Divergence | Is Drift Alert |")
    output_lines.append("|---|---|---|---|---|---|")
    
    for r in conditional_rows:
        output_lines.append(f"| {r['evidence']} | {r['state']} | {r['n_old']} | {r['n_new']} | {r['js']:.4f} | {r['alert']} |")
        
    output_content = "\n".join(output_lines)
    
    report_path = project_root / "experiments" / "drift_check" / "drift_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(output_content)
    
    print(f"Drift check completed successfully. Report saved to: {report_path}")
    
    # Print the priors comparison summary to stdout
    print(f"\nPriors JS Divergence: {js_priors:.4f} (Drift Alert: {alert_priors})")
    
    # Print top marginal drifts to stdout
    print("\nTop Marginal Outcome Drifts:")
    sorted_marginals = sorted([r for r in marginal_rows if "Priors" not in r["evidence"] and "Overall" in r["outcome"]], key=lambda x: x["js"], reverse=True)
    for r in sorted_marginals:
        print(f"  {r['evidence']:25s} | {r['js']:.4f} | {r['alert']}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Run P4 policy calibration analysis.
Loads the benchmark JSON dataset, executes the P4 policy,
extracts the final belief state (posterior probabilities) for S1-S7
immediately before the final action is taken, and generates
calibration tables for each state.
"""

import sys
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd

# Set up project root in path to import constants
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from experiments.constants import (
    STATES,
    PRIORS,
    LIKELIHOODS,
    EVIDENCE_COSTS,
    ACTION_COSTS,
    ACTION_ORDER,
    bayes_update,
)

def clean_outcome(v):
    """NaN-safe missing-value check (iterrows() turns None into NaN)."""
    return None if v is None or (isinstance(v, float) and pd.isna(v)) else v

def expected_cost_of_action(posterior, action):
    """Calculate expected cost of an action under the current posterior."""
    return sum(posterior[s] * ACTION_COSTS[action][s] for s in STATES)

def find_best_action_and_cost(posterior):
    """Find the action with minimum expected cost and return (action, cost)."""
    costs = {a: expected_cost_of_action(posterior, a) for a in ACTION_ORDER}
    best_action = min(costs, key=costs.get)
    return best_action, costs[best_action]

def calculate_voi(posterior, evidence_key, used_evidence_set):
    """Calculate Value of Information for a given evidence source."""
    current_action, ec_current = find_best_action_and_cost(posterior)
    
    likelihoods = LIKELIHOODS[evidence_key]
    outcomes = sorted({outcome for state in STATES for outcome in likelihoods[state].keys()})
    
    ec_after_total = 0.0
    breakdown = {}
    
    for outcome in outcomes:
        p_outcome = sum(posterior[state] * likelihoods[state].get(outcome, 0.0) for state in STATES)
        
        if p_outcome <= 0:
            breakdown[outcome] = {'p_outcome': 0.0, 'skipped': True}
            continue
        
        posterior_after = {}
        for state in STATES:
            likelihood = likelihoods[state].get(outcome, 0.0)
            posterior_after[state] = (posterior[state] * likelihood) / p_outcome
        
        action_after, ec_after = find_best_action_and_cost(posterior_after)
        ec_after_total += p_outcome * ec_after
        
        breakdown[outcome] = {
            'p_outcome': p_outcome,
            'action': action_after,
            'ec_after': ec_after,
            'posterior': posterior_after.copy(),
        }
    
    evidence_cost = EVIDENCE_COSTS[evidence_key]
    ec_with_evidence = evidence_cost + ec_after_total
    voi = ec_current - ec_with_evidence
    
    return {
        'voi': voi,
        'ec_current': ec_current,
        'evidence_cost': evidence_cost,
        'ec_after': ec_after_total,
        'ec_with_evidence': ec_with_evidence,
        'current_action': current_action,
        'breakdown': breakdown,
    }

def run_policy_p4_with_posterior(row):
    """
    P4 policy: Acquire evidence sequentially using Value of Information.
    Also returns the belief state (posterior) just before the final action is taken.
    """
    posterior = PRIORS.copy()
    used = []
    
    # First, apply free evidence (E1, E2)
    for evidence_key in ['E1', 'E2']:
        outcome = clean_outcome(row.get(f'{evidence_key}_outcome'))
        if outcome is None:
            continue
        posterior = bayes_update(posterior, evidence_key, outcome)
        used.append(evidence_key)
    
    # Now consider paid evidence (E3, E4)
    available_paid = ['E3', 'E4']
    
    while True:
        voi_scores = {}
        for evidence_key in available_paid:
            if evidence_key in used or clean_outcome(row.get(f'{evidence_key}_outcome')) is None:
                continue
            
            voi_data = calculate_voi(posterior, evidence_key, set(used))
            voi_scores[evidence_key] = voi_data
        
        if not voi_scores or all(v['voi'] <= 0 for v in voi_scores.values()):
            break
        
        best_evidence = max(voi_scores, key=lambda e: voi_scores[e]['voi'])
        outcome = clean_outcome(row.get(f'{best_evidence}_outcome'))
        posterior = bayes_update(posterior, best_evidence, outcome)
        used.append(best_evidence)
    
    action, _ = find_best_action_and_cost(posterior)
    info_cost = sum(EVIDENCE_COSTS[k] for k in used)
    decision_cost = ACTION_COSTS[action][row['ground_truth']]
    
    return action, info_cost, decision_cost, used, posterior

def flatten_row(row):
    """Transform benchmark case format to policy evaluation format."""
    return {
        'case_id': row.get('case_id'),
        'ground_truth': row.get('true_hidden_state'),
        'E1_outcome': row.get('evidence_e1_pipeline_step'),
        'E2_outcome': row.get('evidence_e2_changed_files'),
        'E3_outcome': row.get('evidence_e3_rerun_outcome'),
        'E4_outcome': row.get('evidence_e4_local_repro'),
    }

def get_bin_name(bin_idx):
    return f"{bin_idx * 10}–{(bin_idx + 1) * 10}%"

def main():
    # Find and load the benchmark JSON file
    json_path = project_root / 'data' / 'benchmark_data' / 'benchmark_cases_seed42.json'
    if not json_path.exists():
        # Try alternate path if any
        json_path = Path('/home/divas/ml/CI-diagnosis-agent/data/benchmark_data/benchmark_cases_seed42.json')
        
    print(f"Loading benchmark data from: {json_path}")
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    cases = data['cases']
    print(f"Loaded {len(cases)} cases.")
    
    # Run P4 on each case and capture the posterior probability over S1-S7
    results = []
    for case in cases:
        row = flatten_row(case)
        action, info_cost, decision_cost, used, posterior = run_policy_p4_with_posterior(row)
        results.append({
            'case_id': row['case_id'],
            'ground_truth': row['ground_truth'],
            'prediction': action,
            'posterior': posterior
        })
        
    # Build calibration table for each state S1-S7
    # For each state, we gather all (predicted_prob, actual) pairs
    calibration_data = {}
    for state in STATES:
        preds = []
        for r in results:
            predicted_prob = r['posterior'][state]
            actual = (r['ground_truth'] == state)
            preds.append((predicted_prob, actual))
            
        # Place into 10 bins: 0-10%, 10-20%, ..., 90-100%
        bins = {i: [] for i in range(10)}
        for p, act in preds:
            p_clamped = max(0.0, min(1.0, p))
            if p_clamped >= 1.0:
                bin_idx = 9
            else:
                bin_idx = int(p_clamped * 10)
            bins[bin_idx].append((p, act))
            
        table_rows = []
        for bin_idx in range(10):
            bin_name = get_bin_name(bin_idx)
            bin_list = bins[bin_idx]
            N = len(bin_list)
            
            if N > 0:
                avg_pred = sum(p for p, _ in bin_list) / N
                num_actual = sum(1 for _, act in bin_list if act)
                actual_pct = num_actual / N
                avg_pred_str = f"{avg_pred * 100:.1f}%"
                actual_pct_str = f"{actual_pct * 100:.1f}% ({num_actual}/{N})"
            else:
                avg_pred_str = "-"
                actual_pct_str = "-"
                
            table_rows.append({
                'Bin': bin_name,
                'N': N,
                'Avg Predicted': avg_pred_str,
                'Actual %': actual_pct_str
            })
        calibration_data[state] = table_rows

    # Generate the Markdown report content
    output_lines = []
    output_lines.append("# P4 Policy Calibration Analysis Results")
    output_lines.append("")
    output_lines.append("- **Dataset:** `benchmark_cases_seed42.json`")
    output_lines.append(f"- **Number of Cases:** {len(cases)}")
    output_lines.append("- **Policy:** P4 (Cost-based Value of Information)")
    output_lines.append("")
    output_lines.append("---")
    output_lines.append("")
    
    # State mapping dictionary for cleaner titles
    state_display_names = {
        "S1_source_code_issues": "S1 (Source Code Issues)",
        "S2_project_config_issues": "S2 (Project Config Issues)",
        "S3_dependency_failures": "S3 (Dependency Failures)",
        "S4_static_analysis_failures": "S4 (Static Analysis Failures)",
        "S5_test_failures": "S5 (Test Failures)",
        "S6_environment_setup_issues": "S6 (Environment Setup Issues)",
        "S7_other": "S7 (Other)"
    }
    
    for state in STATES:
        display_name = state_display_names.get(state, state)
        output_lines.append(f"## Calibration Table for {display_name}")
        output_lines.append("")
        output_lines.append("| Bin | N | Avg Predicted | Actual % |")
        output_lines.append("|---|---|---|---|")
        
        for row in calibration_data[state]:
            output_lines.append(f"| {row['Bin']} | {row['N']} | {row['Avg Predicted']} | {row['Actual %']} |")
            
        output_lines.append("")
        output_lines.append(f"### Calibration Summary for {state}")
        output_lines.append("")
        output_lines.append(f"<!-- ANALYSIS_{state} -->")
        output_lines.append("")
        
    output_content = "\n".join(output_lines)
    
    # Save the draft report
    results_path = Path(__file__).resolve().parent / 'calibration_results.md'
    results_path.write_text(output_content)
    print(f"Results draft written to {results_path}")
    
    # Also print the tables to stdout
    for state in STATES:
        print(f"\n=== Calibration for {state_display_names[state]} ===")
        print(f"{'Bin':<10} | {'N':<5} | {'Avg Pred':<10} | {'Actual %':<15}")
        print("-" * 50)
        for row in calibration_data[state]:
            print(f"{row['Bin']:<10} | {row['N']:<5} | {row['Avg Predicted']:<10} | {row['Actual %']:<15}")

if __name__ == "__main__":
    main()

"""
Hard CI Failure Diagnosis Benchmark Generator
Generates 200 difficult evaluation cases using rejection sampling.
"""

import numpy as np
import json
import csv
from datetime import datetime, timezone
import os
from itertools import product

# ============================================================
# CONFIGURATION
# ============================================================
SEED = 123
TARGET_PER_CATEGORY = 40
OUTPUT_DIR = "."

# ============================================================
# PROBABILITY TABLES
# ============================================================
states = ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]
state_idx = {s: i for i, s in enumerate(states)}
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

# Normalize
E1_likelihoods = {s: np.array(v) / np.sum(v) for s, v in E1_likelihoods_raw.items()}
E2_likelihoods = {s: np.array(v) / np.sum(v) for s, v in E2_likelihoods_raw.items()}
E3_likelihoods = {s: np.array(v) / np.sum(v) for s, v in E3_likelihoods_raw.items()}
E4_likelihoods = {s: np.array(v) / np.sum(v) for s, v in E4_likelihoods_raw.items()}

# Likelihood lookup
E1_lk = {s: {o: E1_likelihoods[s][i] for i, o in enumerate(E1_outcomes)} for s in states}
E2_lk = {s: {o: E2_likelihoods[s][i] for i, o in enumerate(E2_outcomes)} for s in states}
E3_lk = {s: {o: E3_likelihoods[s][i] for i, o in enumerate(E3_outcomes)} for s in states}
E4_lk = {s: {o: E4_likelihoods[s][i] for i, o in enumerate(E4_outcomes)} for s in states}

# ============================================================
# REJECTION FILTERS
# ============================================================
def is_rejected(e1, e2, e3, e4):
    if e1 == "D" and e3 == "pass_on_rerun": return True
    if e1 == "D" and e2 == "doc": return True
    if e3 == "pass_on_rerun" and e4 == "reproducible_locally": return True
    return False

# ============================================================
# SAMPLING AND BAYESIAN UPDATE
# ============================================================
def sample_case(rng):
    state_idx = rng.choice(len(states), p=priors)
    state = states[state_idx]
    e1 = E1_outcomes[rng.choice(len(E1_outcomes), p=E1_likelihoods[state])]
    e2 = E2_outcomes[rng.choice(len(E2_outcomes), p=E2_likelihoods[state])]
    e3 = E3_outcomes[rng.choice(len(E3_outcomes), p=E3_likelihoods[state])]
    e4 = E4_outcomes[rng.choice(len(E4_outcomes), p=E4_likelihoods[state])]
    return state, e1, e2, e3, e4

def bayes_update(posterior, evidence_type, evidence_value):
    new_posterior = np.zeros(7)
    for i, s in enumerate(states):
        if evidence_type == "E1": lk = E1_lk[s][evidence_value]
        elif evidence_type == "E2": lk = E2_lk[s][evidence_value]
        elif evidence_type == "E3": lk = E3_lk[s][evidence_value]
        elif evidence_type == "E4": lk = E4_lk[s][evidence_value]
        else: raise ValueError(f"Unknown evidence type: {evidence_type}")
        new_posterior[i] = posterior[i] * lk
    new_posterior /= new_posterior.sum()
    return new_posterior

def compute_posteriors(e1, e2, e3, e4):
    p0 = priors.copy()
    p1 = bayes_update(p0, "E1", e1)
    p2 = bayes_update(p1, "E2", e2)
    p3 = bayes_update(p2, "E3", e3)
    p4 = bayes_update(p3, "E4", e4)
    return [p0, p1, p2, p3, p4]

def code_fix_prob(posterior):
    return posterior[0] + posterior[1] + posterior[3]

def dependency_prob(posterior):
    return posterior[2]

def get_action(posterior):
    cf = code_fix_prob(posterior)
    dep = dependency_prob(posterior)
    if cf > 0.60: return "fix_code"
    if dep > 0.80: return "resolve_dependency"
    return "collect_more_evidence"

def sample_state_given_evidence(rng, e1, e2, e3, e4):
    posterior = compute_posteriors(e1, e2, e3, e4)[-1]
    idx = rng.choice(len(states), p=posterior)
    return states[idx]

# ============================================================
# CATEGORY CHECKERS
# ============================================================
code_fix_bands = [
    (0.54, 0.56, "band_54_56"),
    (0.57, 0.59, "band_57_59"),
    (0.595, 0.600, "band_595_600"),
    (0.600, 0.605, "band_600_605"),
    (0.61, 0.63, "band_61_63"),
]

dep_bands = [
    (0.74, 0.76, "band_74_76"),
    (0.77, 0.79, "band_77_79"),
    (0.795, 0.800, "band_795_800"),
    (0.800, 0.805, "band_800_805"),
    (0.81, 0.84, "band_81_84"),
]

def check_category_A(posters):
    for p in posters[1:]:
        cf = code_fix_prob(p)
        for lo, hi, name in code_fix_bands:
            if lo <= cf <= hi:
                return True, name, cf
    return False, None, None

def check_category_B(posters):
    for p in posters[1:]:
        dep = dependency_prob(p)
        for lo, hi, name in dep_bands:
            if lo <= dep <= hi:
                return True, name, dep
    return False, None, None

def check_category_C(posters):
    p_final = posters[-1]
    max_p = p_final.max()
    if max_p < 0.50:
        sorted_p = np.sort(p_final)[::-1]
        if len(sorted_p) >= 2 and sorted_p[1] > 0:
            ratio = sorted_p[0] / sorted_p[1]
            if ratio < 3.0:
                return True, max_p
    return False, None

def check_category_D(posters):
    map_changes = 0
    map_states = [states[np.argmax(p)] for p in posters]
    for i in range(len(map_states) - 1):
        if map_states[i] != map_states[i+1]:
            map_changes += 1
    top2_changes = 0
    for i in range(len(posters) - 1):
        top2_i = np.argsort(posters[i])[-2:]
        top2_j = np.argsort(posters[i+1])[-2:]
        if set(top2_i) != set(top2_j) or (top2_i[-1] != top2_j[-1]):
            top2_changes += 1
    if map_changes >= 2 or top2_changes >= 2:
        return True, map_changes, top2_changes
    return False, None, None

def check_category_E(posters, e1, e2, e3, e4):
    evidence_sequence = [("E1", e1), ("E2", e2), ("E3", e3), ("E4", e4)]
    for step in range(1, 5):
        current_posterior = posters[step]
        current_action = get_action(current_posterior)
        remaining = evidence_sequence[step:]
        if not remaining: continue
        all_outcomes = []
        for ev_type, _ in remaining:
            if ev_type == "E1": all_outcomes.append(E1_outcomes)
            elif ev_type == "E2": all_outcomes.append(E2_outcomes)
            elif ev_type == "E3": all_outcomes.append(E3_outcomes)
            elif ev_type == "E4": all_outcomes.append(E4_outcomes)
        actions = set()
        for outcome_combo in product(*all_outcomes):
            test_posterior = current_posterior.copy()
            for (ev_type, _), outcome in zip(remaining, outcome_combo):
                test_posterior = bayes_update(test_posterior, ev_type, outcome)
            actions.add(get_action(test_posterior))
        if len(actions) == 1:
            return True, step, current_action, list(actions)[0]
    return False, None, None, None

# ============================================================
# CASE CONSTRUCTION
# ============================================================
def make_case(test_id, state, e1, e2, e3, e4, category, band_info=None):
    posters = compute_posteriors(e1, e2, e3, e4)
    max_posteriors = [float(p.max()) for p in posters]
    code_fix_probs = [float(code_fix_prob(p)) for p in posters]
    dep_probs = [float(dependency_prob(p)) for p in posters]
    actions = [get_action(p) for p in posters]
    final_action = actions[-1]
    stop_ok, stop_step, stop_current_action, stop_final_action = check_category_E(posters, e1, e2, e3, e4)

    return {
        "test_id": test_id,
        "split": "hard_cases",
        "seed": SEED,
        "case_type": category,
        "band_info": band_info,
        "ground_truth_state": state,
        "all_evidence": {"E1": e1, "E2": e2, "E3": e3, "E4": e4},
        "agent_input_initial": {},
        "posterior_after_E1": {s: float(posters[1][i]) for i, s in enumerate(states)},
        "posterior_after_E2": {s: float(posters[2][i]) for i, s in enumerate(states)},
        "posterior_after_E3": {s: float(posters[3][i]) for i, s in enumerate(states)},
        "posterior_after_E4": {s: float(posters[4][i]) for i, s in enumerate(states)},
        "max_posterior_after_each_step": max_posteriors,
        "code_fix_probability_after_each_step": code_fix_probs,
        "dependency_probability_after_each_step": dep_probs,
        "action_after_each_step": actions,
        "expected_action_under_full_evidence": final_action,
        "stop_info": {
            "is_stop_case": stop_ok,
            "stop_after_step": stop_step,
            "action_at_stop": stop_current_action,
            "robust_action": stop_final_action,
        } if stop_ok else {"is_stop_case": False},
        "generation_method": "rejection_sampling_from_likelihood_model",
        "conditional_independence_assumption": True,
        "prior_source": "empirical",
        "likelihood_source": {"E1": "empirical", "E2": "empirical", "E3": "assumed", "E4": "assumed"},
        "rejection_filters_applied": [
            "E1=D AND E3=pass_on_rerun",
            "E1=D AND E2=doc",
            "E3=pass_on_rerun AND E4=reproducible_locally"
        ]
    }

# ============================================================
# MAIN GENERATION
# ============================================================
def generate_all_cases(seed=SEED):
    rng = np.random.default_rng(seed)
    all_cases = []
    case_counter = 0

    def add_case(case):
        nonlocal case_counter
        case["test_id"] = f"hard_{case_counter:04d}"
        case_counter += 1
        all_cases.append(case)

    # --- Enumerate all valid evidence combinations ---
    all_combos = list(product(E1_outcomes, E2_outcomes, E3_outcomes, E4_outcomes))
    valid_combos = [(e1, e2, e3, e4) for e1, e2, e3, e4 in all_combos if not is_rejected(e1, e2, e3, e4)]

    combo_data = []
    for e1, e2, e3, e4 in valid_combos:
        posters = compute_posteriors(e1, e2, e3, e4)
        ev_prob = sum(priors[i] * E1_lk[s][e1] * E2_lk[s][e2] * E3_lk[s][e3] * E4_lk[s][e4] for i, s in enumerate(states))
        combo_data.append({"e1": e1, "e2": e2, "e3": e3, "e4": e4, "ev_prob": ev_prob, "posters": posters})

    # --- Category A: Code-fix threshold ---
    a_clusters = {
        "band_54_56": [0.5446853643538645],
        "band_57_59": [0.5808708908525365],
        "band_595_600": [0.591204035912881],
        "band_600_605": [0.6094017923172601, 0.6103352121150537, 0.6144538321902369],
        "band_61_63": [0.6103352121150537, 0.6144538321902369, 0.6158149768181712, 0.6290515274363483],
    }

    a_cluster_combos = {name: [] for name in a_clusters}
    for cd in combo_data:
        cf = float(code_fix_prob(cd["posters"][-1]))
        for name, vals in a_clusters.items():
            if any(abs(cf - v) < 1e-9 for v in vals):
                a_cluster_combos[name].append(cd)

    a_per_cluster = {"band_54_56": 1, "band_57_59": 6, "band_595_600": 1, "band_600_605": 4, "band_61_63": 28}
    for name, n in a_per_cluster.items():
        combos = a_cluster_combos[name]
        if not combos: continue
        probs = np.array([c["ev_prob"] for c in combos])
        probs /= probs.sum()
        for _ in range(n):
            combo = combos[rng.choice(len(combos), p=probs)]
            state = sample_state_given_evidence(rng, combo["e1"], combo["e2"], combo["e3"], combo["e4"])
            add_case(make_case("temp", state, combo["e1"], combo["e2"], combo["e3"], combo["e4"], "A", name))

    # --- Category B: Dependency threshold ---
    b_combos_below = [c for c in combo_data if abs(float(dependency_prob(c["posters"][-1])) - 0.7451161940927913) < 1e-6]
    b_combos_above = [c for c in combo_data if abs(float(dependency_prob(c["posters"][-1])) - 0.853223) < 1e-6]

    for combo in b_combos_below:
        for _ in range(20):
            state = sample_state_given_evidence(rng, combo["e1"], combo["e2"], combo["e3"], combo["e4"])
            add_case(make_case("temp", state, combo["e1"], combo["e2"], combo["e3"], combo["e4"], "B", "band_74_76"))
    for combo in b_combos_above:
        for _ in range(20):
            state = sample_state_given_evidence(rng, combo["e1"], combo["e2"], combo["e3"], combo["e4"])
            add_case(make_case("temp", state, combo["e1"], combo["e2"], combo["e3"], combo["e4"], "B", "band_81_84"))

    # --- Categories C, D, E: Rejection sampling ---
    categories_cde = {"C": [], "D": [], "E": []}
    attempts = 0
    while any(len(categories_cde[cat]) < 40 for cat in categories_cde) and attempts < 500000:
        attempts += 1
        state, e1, e2, e3, e4 = sample_case(rng)
        if is_rejected(e1, e2, e3, e4): continue
        posters = compute_posteriors(e1, e2, e3, e4)

        if len(categories_cde["C"]) < 40:
            ok, _ = check_category_C(posters)
            if ok:
                categories_cde["C"].append(make_case("temp", state, e1, e2, e3, e4, "C"))
                continue
        if len(categories_cde["D"]) < 40:
            ok, _, _ = check_category_D(posters)
            if ok:
                categories_cde["D"].append(make_case("temp", state, e1, e2, e3, e4, "D"))
                continue
        if len(categories_cde["E"]) < 40:
            ok, _, _, _ = check_category_E(posters, e1, e2, e3, e4)
            if ok:
                categories_cde["E"].append(make_case("temp", state, e1, e2, e3, e4, "E"))
                continue

    for cat in ["C", "D", "E"]:
        for case in categories_cde[cat]:
            add_case(case)

    return all_cases, attempts

# ============================================================
# SAVE
# ============================================================
if __name__ == "__main__":
    cases, attempts = generate_all_cases()

    # JSONL
    with open(os.path.join(OUTPUT_DIR, "hard_ci_agent_cases.jsonl"), "w") as f:
        for case in cases:
            f.write(json.dumps(case) + "\n")

    # CSV
    csv_columns = ["test_id", "split", "seed", "case_type", "band_info", "ground_truth_state", "E1", "E2", "E3", "E4", "expected_action_under_full_evidence"]
    with open(os.path.join(OUTPUT_DIR, "hard_ci_agent_cases.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns)
        writer.writeheader()
        for case in cases:
            row = {k: case.get(k, "") for k in csv_columns}
            row["E1"] = case["all_evidence"]["E1"]
            row["E2"] = case["all_evidence"]["E2"]
            row["E3"] = case["all_evidence"]["E3"]
            row["E4"] = case["all_evidence"]["E4"]
            writer.writerow(row)

    print(f"Generated {len(cases)} cases.")
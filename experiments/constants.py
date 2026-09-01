"""
Constants for CI diagnosis agent policies.

Priors and likelihoods from probability_decision_record.md
Action costs and evidence costs from decisions/costs.md
"""

import math

# ============================================================================
# HIDDEN STATES
# ============================================================================

STATES = [
    "S1_source_code_issues",
    "S2_project_config_issues",
    "S3_dependency_failures",
    "S4_static_analysis_failures",
    "S5_test_failures",
    "S6_environment_setup_issues",
    "S7_other",
]

# ============================================================================
# PRIORS (from probability_decision_record.md §3)
# ============================================================================

PRIORS = {
    "S1_source_code_issues": 0.0265,
    "S2_project_config_issues": 0.0582,
    "S3_dependency_failures": 0.3122,
    "S4_static_analysis_failures": 0.4162,
    "S5_test_failures": 0.1164,
    "S6_environment_setup_issues": 0.0564,
    "S7_other": 0.0141,
}

# ============================================================================
# LIKELIHOODS (from probability_decision_record.md §6-13)
# ============================================================================

# E1: Pipeline Step outcomes [A_install, B_build, C_test, D_static_analysis, E_workflow, F_other]
LIKELIHOODS_E1 = {
    "S1_source_code_issues": {"A_install": 0.0476, "B_build": 0.0952, "C_test": 0.4762, "D_static_analysis": 0.1429, "E_workflow": 0.0952, "F_other": 0.1429},
    "S2_project_config_issues": {"A_install": 0.2308, "B_build": 0.0256, "C_test": 0.4359, "D_static_analysis": 0.0769, "E_workflow": 0.0769, "F_other": 0.1538},
    "S3_dependency_failures": {"A_install": 0.1694, "B_build": 0.0164, "C_test": 0.4426, "D_static_analysis": 0.3279, "E_workflow": 0.0164, "F_other": 0.0273},
    "S4_static_analysis_failures": {"A_install": 0.0248, "B_build": 0.0083, "C_test": 0.0785, "D_static_analysis": 0.6488, "E_workflow": 0.0248, "F_other": 0.2149},
    "S5_test_failures": {"A_install": 0.0417, "B_build": 0.0417, "C_test": 0.6528, "D_static_analysis": 0.0417, "E_workflow": 0.0556, "F_other": 0.1667},
    "S6_environment_setup_issues": {"A_install": 0.0526, "B_build": 0.0526, "C_test": 0.6842, "D_static_analysis": 0.0789, "E_workflow": 0.0526, "F_other": 0.0789},
    "S7_other": {"A_install": 0.1429, "B_build": 0.0714, "C_test": 0.5714, "D_static_analysis": 0.0714, "E_workflow": 0.0714, "F_other": 0.0714},
}

# E2: Changed Files outcomes [src, test, config, ci, doc, mixed, none]
LIKELIHOODS_E2 = {
    "S1_source_code_issues": {"src": 0.4091, "test": 0.1818, "config": 0.0455, "ci": 0.0455, "doc": 0.0455, "mixed": 0.2273, "none": 0.0455},
    "S2_project_config_issues": {"src": 0.1250, "test": 0.1000, "config": 0.0750, "ci": 0.0250, "doc": 0.0250, "mixed": 0.6000, "none": 0.0500},
    "S3_dependency_failures": {"src": 0.2011, "test": 0.0272, "config": 0.0272, "ci": 0.0109, "doc": 0.0054, "mixed": 0.7228, "none": 0.0054},
    "S4_static_analysis_failures": {"src": 0.5309, "test": 0.0947, "config": 0.0123, "ci": 0.0041, "doc": 0.0082, "mixed": 0.3457, "none": 0.0041},
    "S5_test_failures": {"src": 0.2192, "test": 0.3151, "config": 0.0137, "ci": 0.0137, "doc": 0.0137, "mixed": 0.4110, "none": 0.0137},
    "S6_environment_setup_issues": {"src": 0.3590, "test": 0.0769, "config": 0.0256, "ci": 0.0256, "doc": 0.0256, "mixed": 0.4615, "none": 0.0256},
    "S7_other": {"src": 0.0667, "test": 0.4000, "config": 0.0667, "ci": 0.0667, "doc": 0.0667, "mixed": 0.2667, "none": 0.0667},
}

# E3: Rerun Outcome [pass_on_rerun, fail_on_rerun]
LIKELIHOODS_E3 = {
    "S1_source_code_issues": {"pass_on_rerun": 0.0500, "fail_on_rerun": 0.9500},
    "S2_project_config_issues": {"pass_on_rerun": 0.0500, "fail_on_rerun": 0.9500},
    "S3_dependency_failures": {"pass_on_rerun": 0.1500, "fail_on_rerun": 0.8500},
    "S4_static_analysis_failures": {"pass_on_rerun": 0.0300, "fail_on_rerun": 0.9700},
    "S5_test_failures": {"pass_on_rerun": 0.3500, "fail_on_rerun": 0.6500},
    "S6_environment_setup_issues": {"pass_on_rerun": 0.5000, "fail_on_rerun": 0.5000},
    "S7_other": {"pass_on_rerun": 0.7500, "fail_on_rerun": 0.2500},
}

# E4: Local Reproducibility [reproducible_locally, not_reproducible_locally]
LIKELIHOODS_E4 = {
    "S1_source_code_issues": {"reproducible_locally": 0.92, "not_reproducible_locally": 0.08},
    "S2_project_config_issues": {"reproducible_locally": 0.80, "not_reproducible_locally": 0.20},
    "S3_dependency_failures": {"reproducible_locally": 0.45, "not_reproducible_locally": 0.55},
    "S4_static_analysis_failures": {"reproducible_locally": 0.90, "not_reproducible_locally": 0.10},
    "S5_test_failures": {"reproducible_locally": 0.40, "not_reproducible_locally": 0.60},
    "S6_environment_setup_issues": {"reproducible_locally": 0.25, "not_reproducible_locally": 0.75},
    "S7_other": {"reproducible_locally": 0.15, "not_reproducible_locally": 0.85},
}

# Unified likelihood structure for use in policies
LIKELIHOODS = {
    "E1": LIKELIHOODS_E1,
    "E2": LIKELIHOODS_E2,
    "E3": LIKELIHOODS_E3,
    "E4": LIKELIHOODS_E4,
}

# ============================================================================
# UNCERTAIN BAND (from probability_decision_record.md, threshold policies)
# A decision is "uncertain" — and escalates instead of acting — when the two
# cheapest actions cost nearly the same, or no single state is likely enough.
# ============================================================================

UNCERTAIN_COST_GAP = 5.0     # $ difference below which two actions count as tied
UNCERTAIN_CONFIDENCE = 0.55  # minimum posterior max for acting confidently

# ============================================================================
# ACTIONS
# ============================================================================

ACTIONS = ["Fix Code", "Fix Dependency", "Escalate"]
ACTION_LABELS = ["Fix Code", "Fix Dependency", "Escalate"]
ACTION_ORDER = ["Fix Code", "Fix Dependency", "Escalate"]

# ============================================================================
# ACTION COSTS (from decisions/costs.md)
# ============================================================================

ACTION_COSTS = {
    "Fix Code": {
        "S1_source_code_issues": 8.33,
        "S2_project_config_issues": 8.33,
        "S3_dependency_failures": 75.07,
        "S4_static_analysis_failures": 8.33,
        "S5_test_failures": 75.07,
        "S6_environment_setup_issues": 75.07,
        "S7_other": 75.07,
    },
    "Fix Dependency": {
        "S1_source_code_issues": 75.07,
        "S2_project_config_issues": 75.07,
        "S3_dependency_failures": 8.33,
        "S4_static_analysis_failures": 75.07,
        "S5_test_failures": 75.07,
        "S6_environment_setup_issues": 75.07,
        "S7_other": 75.07,
    },
    "Escalate": {
        "S1_source_code_issues": 50.00,
        "S2_project_config_issues": 50.00,
        "S3_dependency_failures": 50.00,
        "S4_static_analysis_failures": 50.00,
        "S5_test_failures": 50.00,
        "S6_environment_setup_issues": 50.00,
        "S7_other": 50.00,
    },
}

# ============================================================================
# EVIDENCE COSTS (from decisions/costs.md)
# ============================================================================

EVIDENCE_COSTS = {
    "E1": 0.00,     # Pipeline Step (free)
    "E2": 0.00,     # Changed Files (free)
    "E3": 0.07,     # Rerun Outcome ($0.07 for 12 min GitHub runner)
    "E4": 33.33,    # Local Repro ($33.33 for 20 min developer time)
}

EVIDENCE_ORDER = ["E1", "E2", "E3", "E4"]

# ============================================================================
# STATE-TO-ACTION MAPPING (Policy P1: map best state to action)
# ============================================================================

STATE_TO_ACTION = {
    "S1_source_code_issues": "Fix Code",
    "S2_project_config_issues": "Fix Code",
    "S3_dependency_failures": "Fix Dependency",
    "S4_static_analysis_failures": "Fix Code",
    "S5_test_failures": "Escalate",
    "S6_environment_setup_issues": "Escalate",
    "S7_other": "Escalate",
}

# ============================================================================
# BAYES UPDATE HELPER
# ============================================================================

def bayes_update(posterior, evidence_key, outcome, likelihoods=None):
    """
    Update posterior given an evidence source and observed outcome.

    Args:
        posterior: dict[state] -> P(state | previous evidence)
        evidence_key: "E1", "E2", "E3", or "E4"
        outcome: observed outcome (e.g., "C_test", "src", "fail_on_rerun", etc.)
        likelihoods: optional override table (what-if experiments); defaults to LIKELIHOODS

    Returns:
        Updated posterior dict[state] -> P(state | previous + new evidence)
    """
    likelihoods = likelihoods or LIKELIHOODS
    likelihood_table = likelihoods[evidence_key]

    # Numerator: prior (or posterior from previous update) * likelihood
    unnormalised = {}
    for state in STATES:
        likelihood = likelihood_table[state].get(outcome, 0.0)
        unnormalised[state] = posterior[state] * likelihood
    
    # Normalise
    z = sum(unnormalised.values())
    if z == 0:
        # If no state has non-zero likelihood for this outcome, return prior
        return posterior.copy()
    
    return {state: unnormalised[state] / z for state in STATES}

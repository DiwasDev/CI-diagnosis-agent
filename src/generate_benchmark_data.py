"""
Generate reproducible benchmark test cases for CI failure diagnosis agent.

Each case has:
- A true hidden state (sampled from empirical priors)
- Evidence observations (sampled from likelihood tables)
- All deterministic given a seed for full reproducibility
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from dataclasses import dataclass, asdict


# ============================================================================
# CONFIGURATION
# ============================================================================

# Hidden states: S1 through S7
HIDDEN_STATES = [
    "S1_source_code_issues",
    "S2_project_config_issues",
    "S3_dependency_failures",
    "S4_static_analysis_failures",
    "S5_test_failures",
    "S6_environment_setup_issues",
    "S7_other",
]

# Evidence sources and their possible outcomes
EVIDENCE_E1_OUTCOMES = ["A_install", "B_build", "C_test", "D_static_analysis", "E_workflow", "F_other"]
EVIDENCE_E2_OUTCOMES = ["src", "test", "config", "ci", "doc", "mixed", "none"]
EVIDENCE_E3_OUTCOMES = ["pass_on_rerun", "fail_on_rerun"]
EVIDENCE_E4_OUTCOMES = ["reproducible_locally", "not_reproducible_locally"]

# ============================================================================
# EMPIRICAL PRIORS (from probability_decision_record.md, §3)
# ============================================================================

PRIORS: Dict[str, float] = {
    "S1_source_code_issues": 0.0265,
    "S2_project_config_issues": 0.0582,
    "S3_dependency_failures": 0.3122,
    "S4_static_analysis_failures": 0.4162,
    "S5_test_failures": 0.1164,
    "S6_environment_setup_issues": 0.0564,
    "S7_other": 0.0141,
}

# ============================================================================
# LIKELIHOODS (Laplace-smoothed empirical tables from probability_decision_record.md)
# ============================================================================

# E1: Pipeline Step (§6, smoothed likelihood table)
LIKELIHOODS_E1: Dict[str, List[float]] = {
    "S1_source_code_issues": [0.0476, 0.0952, 0.4762, 0.1429, 0.0952, 0.1429],  # A, B, C, D, E, F
    "S2_project_config_issues": [0.2308, 0.0256, 0.4359, 0.0769, 0.0769, 0.1538],
    "S3_dependency_failures": [0.1694, 0.0164, 0.4426, 0.3279, 0.0164, 0.0273],
    "S4_static_analysis_failures": [0.0248, 0.0083, 0.0785, 0.6488, 0.0248, 0.2149],
    "S5_test_failures": [0.0417, 0.0417, 0.6528, 0.0417, 0.0556, 0.1667],
    "S6_environment_setup_issues": [0.0526, 0.0526, 0.6842, 0.0789, 0.0526, 0.0789],
    "S7_other": [0.1429, 0.0714, 0.5714, 0.0714, 0.0714, 0.0714],
}

# E2: Changed Files (§7, smoothed likelihood table)
LIKELIHOODS_E2: Dict[str, List[float]] = {
    "S1_source_code_issues": [0.4091, 0.1818, 0.0455, 0.0455, 0.0455, 0.2273, 0.0455],  # src, test, config, ci, doc, mixed, none
    "S2_project_config_issues": [0.1250, 0.1000, 0.0750, 0.0250, 0.0250, 0.6000, 0.0500],
    "S3_dependency_failures": [0.2011, 0.0272, 0.0272, 0.0109, 0.0054, 0.7228, 0.0054],
    "S4_static_analysis_failures": [0.5309, 0.0947, 0.0123, 0.0041, 0.0082, 0.3457, 0.0041],
    "S5_test_failures": [0.2192, 0.3151, 0.0137, 0.0137, 0.0137, 0.4110, 0.0137],
    "S6_environment_setup_issues": [0.3590, 0.0769, 0.0256, 0.0256, 0.0256, 0.4615, 0.0256],
    "S7_other": [0.0667, 0.4000, 0.0667, 0.0667, 0.0667, 0.2667, 0.0667],
}

# E3: Rerun Outcome (§13, assumed likelihoods)
LIKELIHOODS_E3: Dict[str, List[float]] = {
    "S1_source_code_issues": [0.0500, 0.9500],  # pass_on_rerun, fail_on_rerun
    "S2_project_config_issues": [0.0500, 0.9500],
    "S3_dependency_failures": [0.1500, 0.8500],
    "S4_static_analysis_failures": [0.0300, 0.9700],
    "S5_test_failures": [0.3500, 0.6500],
    "S6_environment_setup_issues": [0.5000, 0.5000],
    "S7_other": [0.7500, 0.2500],
}

# E4: Local Reproducibility (§13, assumed likelihoods - continuing from the file)
LIKELIHOODS_E4: Dict[str, List[float]] = {
    "S1_source_code_issues": [0.92, 0.08],  # reproducible_locally, not_reproducible_locally
    "S2_project_config_issues": [0.80, 0.20],
    "S3_dependency_failures": [0.45, 0.55],
    "S4_static_analysis_failures": [0.90, 0.10],
    "S5_test_failures": [0.40, 0.60],
    "S6_environment_setup_issues": [0.25, 0.75],
    "S7_other": [0.15, 0.85],
}

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class TestCase:
    """Single test case for the CI diagnosis agent."""
    case_id: int
    true_hidden_state: str
    evidence_e1_pipeline_step: str
    evidence_e2_changed_files: str
    evidence_e3_rerun_outcome: str
    evidence_e4_local_repro: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


# ============================================================================
# GENERATION LOGIC
# ============================================================================

class BenchmarkGenerator:
    """Generate reproducible test cases from empirical priors and likelihoods."""

    def __init__(self, seed: int = 42, num_cases: int = 500):
        """Initialize generator with a seed for reproducibility."""
        self.rng = np.random.RandomState(seed)
        self.num_cases = num_cases
        self.seed = seed

    def sample_hidden_state(self) -> str:
        """Sample a hidden state from empirical priors."""
        states = list(PRIORS.keys())
        probs = list(PRIORS.values())
        return self.rng.choice(states, p=probs)

    def sample_evidence_e1(self, state: str) -> str:
        """Sample E1 outcome from likelihood table given hidden state."""
        probs = np.array(LIKELIHOODS_E1[state])
        probs = probs / probs.sum()  # Normalize to ensure sum = 1.0
        return EVIDENCE_E1_OUTCOMES[self.rng.choice(len(EVIDENCE_E1_OUTCOMES), p=probs)]

    def sample_evidence_e2(self, state: str) -> str:
        """Sample E2 outcome from likelihood table given hidden state."""
        probs = np.array(LIKELIHOODS_E2[state])
        probs = probs / probs.sum()  # Normalize to ensure sum = 1.0
        return EVIDENCE_E2_OUTCOMES[self.rng.choice(len(EVIDENCE_E2_OUTCOMES), p=probs)]

    def sample_evidence_e3(self, state: str) -> str:
        """Sample E3 outcome from likelihood table given hidden state."""
        probs = np.array(LIKELIHOODS_E3[state])
        probs = probs / probs.sum()  # Normalize to ensure sum = 1.0
        return EVIDENCE_E3_OUTCOMES[self.rng.choice(len(EVIDENCE_E3_OUTCOMES), p=probs)]

    def sample_evidence_e4(self, state: str) -> str:
        """Sample E4 outcome from likelihood table given hidden state."""
        probs = np.array(LIKELIHOODS_E4[state])
        probs = probs / probs.sum()  # Normalize to ensure sum = 1.0
        return EVIDENCE_E4_OUTCOMES[self.rng.choice(len(EVIDENCE_E4_OUTCOMES), p=probs)]

    def generate_cases(self) -> List[TestCase]:
        """Generate num_cases test cases, each with hidden state and evidence."""
        cases = []
        for case_id in range(self.num_cases):
            # Sample true hidden state from priors
            true_state = self.sample_hidden_state()

            # Generate evidence conditioned on true state
            e1 = self.sample_evidence_e1(true_state)
            e2 = self.sample_evidence_e2(true_state)
            e3 = self.sample_evidence_e3(true_state)
            e4 = self.sample_evidence_e4(true_state)

            case = TestCase(
                case_id=case_id,
                true_hidden_state=true_state,
                evidence_e1_pipeline_step=e1,
                evidence_e2_changed_files=e2,
                evidence_e3_rerun_outcome=e3,
                evidence_e4_local_repro=e4,
            )
            cases.append(case)

        return cases

    def save_to_jsonl(self, cases: List[TestCase], output_path: Path) -> None:
        """Save cases to JSONL format (one JSON object per line)."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            for case in cases:
                f.write(json.dumps(case.to_dict()) + "\n")

    def save_to_json(self, cases: List[TestCase], output_path: Path) -> None:
        """Save cases to JSON format (array of objects)."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(
                {
                    "metadata": {
                        "seed": self.seed,
                        "num_cases": len(cases),
                        "hidden_states": HIDDEN_STATES,
                        "evidence_e1_outcomes": EVIDENCE_E1_OUTCOMES,
                        "evidence_e2_outcomes": EVIDENCE_E2_OUTCOMES,
                        "evidence_e3_outcomes": EVIDENCE_E3_OUTCOMES,
                        "evidence_e4_outcomes": EVIDENCE_E4_OUTCOMES,
                        "priors": PRIORS,
                    },
                    "cases": [case.to_dict() for case in cases],
                },
                f,
                indent=2,
            )

    def print_summary(self, cases: List[TestCase]) -> None:
        """Print summary statistics of generated cases."""
        from collections import Counter

        state_counts = Counter(c.true_hidden_state for c in cases)
        e1_counts = Counter(c.evidence_e1_pipeline_step for c in cases)
        e2_counts = Counter(c.evidence_e2_changed_files for c in cases)
        e3_counts = Counter(c.evidence_e3_rerun_outcome for c in cases)
        e4_counts = Counter(c.evidence_e4_local_repro for c in cases)

        print("\n" + "=" * 80)
        print("BENCHMARK DATASET GENERATION SUMMARY")
        print("=" * 80)
        print(f"\nGenerated {len(cases)} test cases with seed={self.seed}")
        print(f"\nHidden State Distribution (should match priors):")
        print(f"  Prior          | Generated Count | Generated Freq | Expected")
        print(f"  " + "-" * 76)
        for state in HIDDEN_STATES:
            count = state_counts[state]
            freq = count / len(cases)
            expected = PRIORS[state]
            print(
                f"  {state:30s} | {count:5d} ({freq:6.2%}) | {expected:6.2%}"
            )

        print(f"\nEvidence E1 Distribution (Pipeline Step):")
        print(f"  Outcome            | Count | Frequency")
        print(f"  " + "-" * 40)
        for outcome in EVIDENCE_E1_OUTCOMES:
            count = e1_counts[outcome]
            freq = count / len(cases)
            print(f"  {outcome:18s} | {count:5d} | {freq:6.2%}")

        print(f"\nEvidence E2 Distribution (Changed Files):")
        print(f"  Outcome            | Count | Frequency")
        print(f"  " + "-" * 40)
        for outcome in EVIDENCE_E2_OUTCOMES:
            count = e2_counts[outcome]
            freq = count / len(cases)
            print(f"  {outcome:18s} | {count:5d} | {freq:6.2%}")

        print(f"\nEvidence E3 Distribution (Rerun Outcome):")
        print(f"  Outcome            | Count | Frequency")
        print(f"  " + "-" * 40)
        for outcome in EVIDENCE_E3_OUTCOMES:
            count = e3_counts[outcome]
            freq = count / len(cases)
            print(f"  {outcome:18s} | {count:5d} | {freq:6.2%}")

        print(f"\nEvidence E4 Distribution (Local Repro):")
        print(f"  Outcome            | Count | Frequency")
        print(f"  " + "-" * 40)
        for outcome in EVIDENCE_E4_OUTCOMES:
            count = e4_counts[outcome]
            freq = count / len(cases)
            print(f"  {outcome:18s} | {count:5d} | {freq:6.2%}")

        print("\n" + "=" * 80)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys

    # Default: 500 cases with seed 42 for reproducibility
    num_cases = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42

    print(f"Generating {num_cases} benchmark test cases with seed={seed}...")

    generator = BenchmarkGenerator(seed=seed, num_cases=num_cases)
    cases = generator.generate_cases()

    # Save to both formats
    output_dir = Path(__file__).parent.parent / "data" / "benchmark_data"
    output_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = output_dir / f"benchmark_cases_seed{seed}.jsonl"
    json_path = output_dir / f"benchmark_cases_seed{seed}.json"

    generator.save_to_jsonl(cases, jsonl_path)
    generator.save_to_json(cases, json_path)

    print(f"\nSaved {len(cases)} cases to:")
    print(f"  JSONL: {jsonl_path.relative_to(Path.cwd())}")
    print(f"  JSON:  {json_path.relative_to(Path.cwd())}")

    generator.print_summary(cases)

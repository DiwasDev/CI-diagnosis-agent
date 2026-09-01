"""Experiment (Fix 2): P4 with an optimistic rerun likelihood for S3.

What-if: dependency failures that clear on a simple rerun far more often than
the decision record assumes — P(E3 = pass | S3) 0.15 -> 0.40 — injected via the
policy instead of mutating constants. Both runs use the corrected E3 benchmark
mapping, so the E3 outcome actually updates beliefs.
"""

import copy

from experiments.constants import LIKELIHOODS
from experiments.evaluation import comparison_table, evidence_acquisition, evaluate, load_cases, summarize
from experiments.policies import ValueOfInformation

OPTIMISTIC_RERUN_LIKELIHOODS = copy.deepcopy(LIKELIHOODS)
OPTIMISTIC_RERUN_LIKELIHOODS["E3"]["S3_dependency_failures"] = {
    "pass_on_rerun": 0.40,
    "fail_on_rerun": 0.60,
}


def main():
    cases = load_cases()
    metrics = []
    runs = [
        ("P4, original S3 rerun likelihood (0.15/0.85)", ValueOfInformation()),
        ("P4, optimistic S3 rerun likelihood (0.40/0.60)",
         ValueOfInformation(likelihoods=OPTIMISTIC_RERUN_LIKELIHOODS)),
    ]
    for label, policy in runs:
        records = evaluate(policy, cases)
        metrics.append(summarize(label, records))
        acquired = evidence_acquisition(records)
        print(f"{label}: accuracy {metrics[-1]['accuracy']:.1%}, "
              f"E3 acquired in {acquired['E3']} cases ({acquired['E3'] / len(records):.1%}), "
              f"E4 in {acquired['E4']}, total cost ${metrics[-1]['total_cost']:,.2f}")

    print("\nFIX 2 COMPARISON — S3 rerun likelihood what-if")
    print(comparison_table(metrics).to_string(index=False, float_format=lambda x: f"{x:,.3f}"))


if __name__ == "__main__":
    main()

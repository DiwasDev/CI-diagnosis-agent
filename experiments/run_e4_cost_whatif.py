"""Experiment (Fix 1): P4 with automated local reproduction, E4 cost $0.10.

What-if re-run of the value-of-information policy with the E4 cost dropped
from $33.33 to $0.10, injected via the policy instead of mutating constants.
"""

from experiments.constants import EVIDENCE_COSTS
from experiments.evaluation import comparison_table, evidence_acquisition, evaluate, load_cases, summarize
from experiments.policies import ValueOfInformation

AUTOMATED_E4_COSTS = {**EVIDENCE_COSTS, "E4": 0.10}


def main():
    cases = load_cases()
    metrics = []
    runs = [
        ("P4 baseline (E4 = $33.33)", ValueOfInformation(), EVIDENCE_COSTS),
        ("P4 with E4 = $0.10", ValueOfInformation(evidence_costs=AUTOMATED_E4_COSTS), AUTOMATED_E4_COSTS),
    ]
    for label, policy, evidence_costs in runs:
        records = evaluate(policy, cases, evidence_costs)
        metrics.append(summarize(label, records))
        acquired = evidence_acquisition(records)
        print(f"{label}: accuracy {metrics[-1]['accuracy']:.1%}, "
              f"E4 acquired in {acquired['E4']} cases, "
              f"total cost ${metrics[-1]['total_cost']:,.2f}")

    print("\nFIX 1 COMPARISON — E4 cost what-if")
    print(comparison_table(metrics).to_string(index=False, float_format=lambda x: f"{x:,.3f}"))


if __name__ == "__main__":
    main()

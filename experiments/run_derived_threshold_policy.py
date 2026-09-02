"""Experiment (Fix 3): all-evidence policy with a cost-derived act/escalate threshold.

Derives the break-even threshold p* from the cost of being wrong in each
direction, checks it is not knife-edge
sensitive, then runs the DerivedThreshold policy on the full benchmark and
compares it against the P2/P3/P4 family.
"""

from experiments.constants import ACTION_COSTS, PRIORS
from experiments.evaluation import comparison_table, evidence_acquisition, evaluate, load_cases, summarize
from experiments.policies import (
    DerivedThreshold,
    ExpectedCostThreshold,
    InfoGainPerDollar,
    ValueOfInformation,
)
from experiments.policies.base import observe_free_evidence
from experiments.policies.derived_threshold import act_escalate_threshold, action_belief_mass


def main():
    print_threshold_derivation()
    cases = load_cases()
    fix3 = DerivedThreshold()
    trace_first_cases(fix3, cases.head(3))

    metrics = []
    for policy in [ExpectedCostThreshold(), InfoGainPerDollar(), ValueOfInformation(), fix3]:
        records = evaluate(policy, cases)
        metrics.append(summarize(policy.name, records))
        if isinstance(policy, DerivedThreshold):
            for key, count in evidence_acquisition(records).items():
                print(f"Fix 3: {key} acquired in {count} cases ({count / len(records):.1%})")

    print(f"\nFIX 3 vs THE POLICY FAMILY (threshold p* = {act_escalate_threshold():.4f})")
    print(comparison_table(metrics).to_string(index=False, float_format=lambda x: f"{x:,.3f}"))


def print_threshold_derivation():
    """Show where p* comes from and that +-10% cost noise does not move it much."""
    matching_fix = ACTION_COSTS["Fix Code"]["S1_source_code_issues"]
    wrong_fix = ACTION_COSTS["Fix Code"]["S3_dependency_failures"]
    escalate = ACTION_COSTS["Escalate"]["S1_source_code_issues"]
    p_star = act_escalate_threshold()
    print(f"act on a wrong fix wastes ${wrong_fix - escalate:.2f}; "
          f"not committing although a fix works wastes ${escalate - matching_fix:.2f}")
    print(f"p* = {wrong_fix - escalate:.2f} / ({wrong_fix - escalate:.2f} + {escalate - matching_fix:.2f}) "
          f"= {p_star:.4f}")

    base = (matching_fix, wrong_fix, escalate)
    perturbed = [tuple(c * f if j == i else c for j, c in enumerate(base))
                 for i in range(3) for f in (1.10, 0.90)]
    values = [_break_even(*costs) for costs in perturbed]
    print(f"sensitivity (+/-10% on one cost at a time): p* stays within "
          f"[{min(values):.3f}, {max(values):.3f}]")


def _break_even(matching_fix, wrong_fix, escalate):
    return (wrong_fix - escalate) / ((wrong_fix - escalate) + (escalate - matching_fix))


def trace_first_cases(policy, cases):
    """Show the belief trajectory of the threshold loop on a few cases."""
    for case in cases.to_dict(orient="records"):
        posterior, _ = observe_free_evidence(PRIORS.copy(), case)
        decision = policy.decide(case)
        print(f"case {case['case_id']} (true {case['ground_truth']}): "
              f"after free evidence P(Fix Code)={action_belief_mass(posterior, 'Fix Code'):.3f}, "
              f"P(Fix Dep)={action_belief_mass(posterior, 'Fix Dependency'):.3f} "
              f"-> ACT {decision.action} using {decision.evidence_used}")


if __name__ == "__main__":
    main()

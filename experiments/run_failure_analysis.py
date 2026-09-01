"""Experiment: markdown failure reports for P0-P4.

For each policy, finds the misclassified cases and documents the five most
expensive ones with a dry-run trace of the belief updates, writing one file
per policy to experiments/failures/.
"""

from experiments.constants import ACTION_COSTS, PRIORS, bayes_update
from experiments.evaluation import evaluate, load_cases
from experiments.policies import (
    BeliefOnly,
    ExpectedCostThreshold,
    InfoGainPerDollar,
    MajorityBaseline,
    ValueOfInformation,
)
from experiments.policies.base import best_expected_cost_action
from pathlib import Path

FAILURES_DIR = Path(__file__).parent / "failures"


def main():
    cases = load_cases()
    policies = [
        MajorityBaseline(cases["ground_action"].value_counts().idxmax()),
        BeliefOnly(),
        ExpectedCostThreshold(),
        InfoGainPerDollar(),
        ValueOfInformation(),
    ]
    for policy in policies:
        records = evaluate(policy, cases)
        write_failure_report(policy.name, cases, records)


def write_failure_report(policy_name, cases, records):
    failures = records[records["prediction"] != records["ground_action"]]
    failures = failures.sort_values("decision_cost", ascending=False).head(5)
    lines = [f"# {policy_name} — failure analysis", "",
             f"**Total failures:** {len(failures.index)} of {len(records)} cases "
             f"({len(failures) / len(records):.1%} failure rate)", ""]
    for position, (_, failure) in enumerate(failures.iterrows(), start=1):
        case = cases.iloc[failure.name].to_dict()
        lines += trace_failure(position, case, failure)
    FAILURES_DIR.mkdir(exist_ok=True)
    filename = FAILURES_DIR / f"{policy_name.split()[0].lower()}_failures.md"
    filename.write_text("\n".join(lines))
    print(f"wrote {filename} ({len(failures)} expensive failures documented)")


def trace_failure(position, case, failure):
    """Markdown lines replaying the belief updates that led to one failure."""
    lines = [f"## Failure {position} — case {case['case_id']}", "",
             f"- **True state:** {case['ground_truth']}",
             f"- **Predicted action:** {failure['prediction']}",
             f"- **Realised cost:** ${failure['decision_cost']:.2f}",
             f"- **Correct action was:** {case['ground_action']}", "",
             "### Dry-run trace", "", "```"]

    posterior = PRIORS.copy()
    lines.append(f"priors: {top_states(posterior)}")
    for key in ("E1", "E2", "E3", "E4"):
        outcome = case[f"{key}_outcome"]
        if outcome is None:
            continue
        if key in failure["evidence_used"]:
            posterior = bayes_update(posterior, key, outcome)
            lines.append(f"{key} = {outcome} (acquired) -> {top_states(posterior)}")
        else:
            lines.append(f"{key} = {outcome} available but not acquired")
    action, cost = best_expected_cost_action(posterior)
    lines.append(f"final: {action} at expected cost ${cost:.2f} "
                 f"(realised ${ACTION_COSTS[failure['prediction']][case['ground_truth']]:.2f})")
    return [*lines, "```", ""]


def top_states(posterior):
    return ", ".join(f"{state.split('_')[0]} {p:.3f}" for state, p in
                     sorted(posterior.items(), key=lambda kv: kv[1], reverse=True)[:3])


if __name__ == "__main__":
    main()

"""Experiment: policy-comparison variance across benchmark seeds.

Regenerates the 500-case benchmark at seeds 42/7/123, evaluates every policy
on each seed, and writes per-case results plus a mean/std summary to
experiments/results/. Seed 42 is the headline benchmark; the other two show
that the policy ranking is not a single-draw artefact.
"""

import importlib.util
import json
from pathlib import Path

from experiments.constants import EVIDENCE_COSTS
from experiments.evaluation import evaluate, load_cases, summarize
from experiments.policies import (
    BeliefOnly,
    DerivedThreshold,
    ExpectedCostThreshold,
    InfoGainPerDollar,
    MajorityBaseline,
    ValueOfInformation,
)

RESULTS_DIR = Path(__file__).parent / "results"
SEEDS = (42, 7, 123)
GENERATOR_PATH = Path(__file__).resolve().parents[1] / "src" / "generate_benchmark_data.py"


def main():
    generator = load_generator()
    per_seed = {}
    for seed in SEEDS:
        benchmark_path = RESULTS_DIR / f"benchmark_cases_seed{seed}.json"
        benchmark = generator.BenchmarkGenerator(seed=seed, num_cases=500)
        benchmark.save_to_json(benchmark.generate_cases(), benchmark_path)
        cases = load_cases(benchmark_path)
        summaries, records_by_policy = [], {}
        for policy in make_policies(cases):
            records = evaluate(policy, cases, EVIDENCE_COSTS)
            summaries.append(summarize(policy.name, records))
            records_by_policy[policy.name] = records.to_dict(orient="records")
            print(f"seed {seed} | {policy.name}: accuracy {summaries[-1]['accuracy']:.1%}, "
                  f"cost/case ${summaries[-1]['expected_cost_per_case']:.2f}")
        per_seed[seed] = summaries
        write_per_case_results(seed, records_by_policy)

    write_summary_table(per_seed)


def load_generator():
    """Import the benchmark generator from src/, which is not a package."""
    spec = importlib.util.spec_from_file_location("benchmark_generator", GENERATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_policies(cases):
    return [
        MajorityBaseline(cases["ground_action"].value_counts().idxmax()),
        BeliefOnly(),
        ExpectedCostThreshold(),
        InfoGainPerDollar(),
        ValueOfInformation(),
        DerivedThreshold(),
    ]


def write_per_case_results(seed, records_by_policy):
    RESULTS_DIR.mkdir(exist_ok=True)
    path = RESULTS_DIR / f"policy_cases_seed{seed}.json"
    path.write_text(json.dumps({"seed": seed, "policies": records_by_policy}, default=float, indent=2))
    print(f"wrote {path}")


def write_summary_table(per_seed):
    """Markdown table of mean ± std over seeds for each policy and headline metric."""
    policies = [s["policy"] for s in per_seed[SEEDS[0]]]
    lines = [
        "# Seed variance — policy comparison across benchmark draws",
        "",
        "The headline results in the README use the seed-42 benchmark. This table "
        "re-runs the same policies on independently sampled 500-case benchmarks "
        "(seeds 7 and 123) to show the ranking is not a single-draw artefact.",
        "",
        "| Policy | Accuracy | Cost / case | Escalation % |",
        "|---|---|---|---|",
    ]
    for policy in policies:
        cells = []
        for key, fmt in (("accuracy", "{:.1%}"), ("expected_cost_per_case", "${:.2f}"), ("human_pct", "{:.1f}%")):
            values = [next(s[key] for s in per_seed[seed] if s["policy"] == policy) for seed in SEEDS]
            mean = sum(values) / len(values)
            std = (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5
            cells.append(f"{fmt.format(mean)} ± {fmt.format(std).lstrip('$')}")
        lines.append(f"| {policy} | " + " | ".join(cells) + " |")
    lines += [
        "",
        "± is the population standard deviation across the three seeds (n = 3).",
        "",
        "P0's majority action is fit on each seed's own cases (disclosed in the "
        "README), so its accuracy is a slightly optimistic floor on every seed.",
        "",
    ]
    RESULTS_DIR.mkdir(exist_ok=True)
    path = RESULTS_DIR / "seed_variance.md"
    path.write_text("\n".join(lines))
    print(f"wrote {path}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

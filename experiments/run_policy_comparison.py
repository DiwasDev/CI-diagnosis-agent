"""Experiment: evaluate P0-P4 on the benchmark and compare them.

Reports per-policy metrics, a comparison table with rankings, and a 2x2 chart
saved to experiments/reports/policy_comparison.png.
"""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

from experiments.constants import EVIDENCE_COSTS
from experiments.evaluation import comparison_table, evaluate, load_cases, summarize
from experiments.policies import (
    BeliefOnly,
    ExpectedCostThreshold,
    InfoGainPerDollar,
    MajorityBaseline,
    ValueOfInformation,
)

REPORTS_DIR = Path(__file__).parent / "reports"


def main():
    cases = load_cases()
    policies = [
        MajorityBaseline(cases["ground_action"].value_counts().idxmax()),
        BeliefOnly(),
        ExpectedCostThreshold(),
        InfoGainPerDollar(),
        ValueOfInformation(),
    ]

    metrics = []
    for policy in policies:
        records = evaluate(policy, cases, EVIDENCE_COSTS)
        summary = summarize(policy.name, records)
        metrics.append(summary)
        print(f"\n=== {policy.name} ===")
        print(f"accuracy {summary['accuracy']:.1%} | total cost ${summary['total_cost']:,.2f} | "
              f"escalation {summary['human_pct']:.1f}%")

    print("\nPOLICY COMPARISON (500 test cases)")
    print(comparison_table(metrics).to_string(index=False, float_format=lambda x: f"{x:,.3f}"))
    print_rankings(metrics)
    plot_comparison(metrics)


def print_rankings(metrics):
    by_accuracy = sorted(metrics, key=lambda m: m["accuracy"], reverse=True)
    by_cost = sorted(metrics, key=lambda m: m["total_cost"])
    print("\nBest accuracy : " + ", ".join(f"{m['policy']} ({m['accuracy']:.1%})" for m in by_accuracy[:2]))
    print("Lowest cost   : " + ", ".join(f"{m['policy']} (${m['total_cost']:,.2f})" for m in by_cost[:2]))


def plot_comparison(metrics):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Policy Comparison Metrics", fontsize=16, fontweight="bold")
    panels = [
        ("accuracy", "Accuracy by policy", axes[0][0], "{:.1%}", 1.0, False),
        ("total_cost", "Total cost (500 cases)", axes[0][1], "${:,.0f}", None, True),
        ("expected_cost_per_case", "Expected cost per case", axes[1][0], "${:,.2f}", None, True),
        ("human_pct", "Human escalation percentage", axes[1][1], "{:.1f}%", 100.0, True),
    ]
    names = [m["policy"].split()[0] for m in metrics]
    for key, title, ax, fmt, ylim, lower_is_better in panels:
        values = [m[key] for m in metrics]
        best = min(values) if lower_is_better else max(values)
        bars = ax.bar(names, values, color="#1f77b4", alpha=0.7, edgecolor="black")
        for bar, value in zip(bars, values):
            bar.set_color("#2ca02c" if value == best else "#1f77b4")
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), fmt.format(value),
                    ha="center", va="bottom", fontweight="bold", fontsize=9)
        ax.set_title(title, fontweight="bold")
        if ylim:
            ax.set_ylim(0, ylim)
        ax.grid(axis="y", alpha=0.3)
    REPORTS_DIR.mkdir(exist_ok=True)
    fig.tight_layout()
    fig.savefig(REPORTS_DIR / "policy_comparison.png", dpi=150)
    print(f"\nChart saved to {REPORTS_DIR / 'policy_comparison.png'}")


if __name__ == "__main__":
    main()

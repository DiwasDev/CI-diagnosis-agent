"""P0 — baseline that ignores all evidence."""

from experiments.policies.base import Decision, Policy


class MajorityBaseline(Policy):
    """Always predicts the most common action in the benchmark.

    It exists to prove the evidence-driven policies beat doing nothing; the
    majority action is computed from the evaluation set and injected here.
    """

    def __init__(self, majority_action: str):
        self.name = "P0 majority baseline"
        self.majority_action = majority_action

    def decide(self, case: dict) -> Decision:
        return Decision(self.majority_action, [])

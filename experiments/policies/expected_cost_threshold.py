"""P2 — expected-cost threshold policy."""

from experiments.constants import PRIORS
from experiments.policies.base import (
    Decision,
    Policy,
    act_or_escalate,
    observe_free_evidence,
)


class ExpectedCostThreshold(Policy):
    """Chooses the cheapest action under the posterior, escalating when uncertain.

    Same free evidence as P1, but the action minimises expected cost and the
    uncertain band guard diverts close calls to a human.
    """

    def __init__(self):
        self.name = "P2 expected-cost threshold"

    def decide(self, case: dict) -> Decision:
        posterior, used = observe_free_evidence(PRIORS.copy(), case)
        return Decision(act_or_escalate(posterior), used)

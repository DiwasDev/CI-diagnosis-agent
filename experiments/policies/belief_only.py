"""P1 — belief-only policy."""

from experiments.constants import PRIORS
from experiments.policies.base import Decision, Policy, observe_free_evidence, state_to_action


class BeliefOnly(Policy):
    """Updates on the free evidence, then maps the most likely state to its action.

    No cost awareness: the action follows directly from the argmax state.
    """

    def __init__(self):
        self.name = "P1 belief-only"

    def decide(self, case: dict) -> Decision:
        posterior, used = observe_free_evidence(PRIORS.copy(), case)
        best_state = max(posterior, key=posterior.get)
        return Decision(state_to_action(best_state), used)

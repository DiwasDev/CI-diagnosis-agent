"""P3 — information-gain-per-dollar policy."""

from experiments.constants import PRIORS, bayes_update
from experiments.policies.base import (
    PAID_EVIDENCE,
    Decision,
    Policy,
    act_or_escalate,
    best_evidence_per_dollar,
    observe_free_evidence,
)


class InfoGainPerDollar(Policy):
    """Buys paid evidence ranked by expected information gain per dollar.

    Heuristic value of information: keep buying while the best remaining
    score exceeds MIN_SCORE, and stop as soon as the decision leaves the
    uncertain band.
    """

    MIN_SCORE = 0.05

    def __init__(self):
        self.name = "P3 info-gain per dollar"

    def decide(self, case: dict) -> Decision:
        posterior, used = observe_free_evidence(PRIORS.copy(), case)
        while True:
            best = best_evidence_per_dollar(
                posterior, case, used, PAID_EVIDENCE, self.MIN_SCORE
            )
            if best is None:
                break
            posterior = bayes_update(posterior, best, case[f"{best}_outcome"])
            used.append(best)
            if act_or_escalate(posterior) != "Escalate":
                break
        return Decision(act_or_escalate(posterior), used)

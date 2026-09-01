"""P4 — cost-based value-of-information policy."""

from experiments.constants import (
    EVIDENCE_COSTS,
    LIKELIHOODS,
    PRIORS,
    bayes_update,
)
from experiments.policies.base import (
    PAID_EVIDENCE,
    Decision,
    Policy,
    best_expected_cost_action,
    observe_free_evidence,
)


class ValueOfInformation(Policy):
    """Buys paid evidence only when its value of information is positive.

    VoI(E) = EC(best action now) − (cost of E + expected EC after observing E),
    averaged over E's possible outcomes. Evidence with VoI ≤ 0 can only make
    the decision worse, so the policy stops as soon as nothing pays off.

    Evidence costs and likelihoods are injectable so what-if experiments can
    vary them without mutating the shared constants.
    """

    def __init__(self, evidence_costs: dict | None = None, likelihoods: dict | None = None):
        self.name = "P4 cost-based VoI"
        self.evidence_costs = evidence_costs or EVIDENCE_COSTS
        self.likelihoods = likelihoods or LIKELIHOODS

    def decide(self, case: dict) -> Decision:
        posterior, used = observe_free_evidence(PRIORS.copy(), case)
        while True:
            best = self._most_valuable_evidence(posterior, case, used)
            if best is None:
                break
            posterior = bayes_update(
                posterior, best, case[f"{best}_outcome"], self.likelihoods
            )
            used.append(best)
        action, _ = best_expected_cost_action(posterior)
        return Decision(action, used)

    def _most_valuable_evidence(self, posterior: dict, case: dict, used: list[str]) -> str | None:
        """The pending paid evidence with the highest positive VoI, or None."""
        scores = {
            key: self.value_of_information(posterior, key)
            for key in PAID_EVIDENCE
            if key not in used and case.get(f"{key}_outcome") is not None
        }
        positive = {key: voi for key, voi in scores.items() if voi > 0}
        return max(positive, key=positive.get) if positive else None

    def value_of_information(self, posterior: dict, evidence_key: str) -> float:
        """Net expected cost saving from buying `evidence_key` before acting."""
        likelihoods = self.likelihoods[evidence_key]
        _, cost_of_acting_now = best_expected_cost_action(posterior)
        outcomes = sorted({outcome for state in posterior for outcome in likelihoods[state]})

        cost_of_acting_after = 0.0
        for outcome in outcomes:
            p_outcome = sum(
                posterior[state] * likelihoods[state].get(outcome, 0.0) for state in posterior
            )
            if p_outcome <= 0:
                continue
            posterior_after = bayes_update(posterior, evidence_key, outcome, self.likelihoods)
            _, best_cost_after = best_expected_cost_action(posterior_after)
            cost_of_acting_after += p_outcome * best_cost_after

        return cost_of_acting_now - (self.evidence_costs[evidence_key] + cost_of_acting_after)

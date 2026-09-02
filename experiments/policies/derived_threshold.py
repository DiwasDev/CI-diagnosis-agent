"""Fix 3 — policy whose act/escalate threshold is derived from failure costs."""

from experiments.constants import (
    ACTION_COSTS,
    EVIDENCE_ORDER,
    PRIORS,
    STATE_TO_ACTION,
    bayes_update,
)
from experiments.policies.base import (
    Decision,
    Policy,
    best_evidence_per_dollar,
    best_expected_cost_action,
    expected_action_cost,
    observe_free_evidence,
)

FIX_ACTIONS = ("Fix Code", "Fix Dependency")


def act_escalate_threshold() -> float:
    """Break-even belief p* = C_FP / (C_FP + C_FN) for acting instead of escalating.

    Acting on a wrong fix wastes the gap between a wrong fix and escalating;
    escalating although a fix would have worked wastes the mirrored gap.
    """
    matching_fix = ACTION_COSTS["Fix Code"]["S1_source_code_issues"]
    wrong_fix = ACTION_COSTS["Fix Code"]["S3_dependency_failures"]
    escalate = ACTION_COSTS["Escalate"]["S1_source_code_issues"]
    cost_of_acting_wrong = wrong_fix - escalate
    cost_of_escalating_wrong = escalate - matching_fix
    return cost_of_acting_wrong / (cost_of_acting_wrong + cost_of_escalating_wrong)


def action_belief_mass(posterior: dict, action: str) -> float:
    """Belief mass on the states for which `action` is the correct fix."""
    return sum(p for s, p in posterior.items() if STATE_TO_ACTION[s] == action)


class DerivedThreshold(Policy):
    """Acts once a fix action's correct-belief mass passes the derived threshold.

    Free evidence is always taken first (the priors already clear the threshold,
    so the threshold loop only governs paid evidence). When no threshold passes,
    the highest information-gain-per-dollar evidence is bought and the check
    repeats; exhausted evidence falls back to the lowest expected-loss action.
    """

    def __init__(self):
        self.name = "Fix3 derived threshold"
        self.threshold = act_escalate_threshold()

    def decide(self, case: dict) -> Decision:
        posterior, used = observe_free_evidence(PRIORS.copy(), case)
        while True:
            action = self._passing_action(posterior)
            if action is not None:
                return Decision(action, used)
            best = best_evidence_per_dollar(posterior, case, used, EVIDENCE_ORDER, 0.0)
            if best is None:
                action, _ = best_expected_cost_action(posterior)
                return Decision(action, used)
            posterior = bayes_update(posterior, best, case[f"{best}_outcome"])
            used.append(best)

    def _passing_action(self, posterior: dict) -> str | None:
        """The fix action to commit to, or None while the belief is too weak."""
        passing = [a for a in FIX_ACTIONS if action_belief_mass(posterior, a) >= self.threshold]
        if not passing:
            return None
        return min(passing, key=lambda a: expected_action_cost(posterior, a))

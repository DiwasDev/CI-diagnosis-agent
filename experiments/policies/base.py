"""Policy interface and the probability math shared by several policies."""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass

from experiments.constants import (
    ACTION_COSTS,
    ACTION_ORDER,
    EVIDENCE_COSTS,
    LIKELIHOODS,
    STATES,
    STATE_TO_ACTION,
    UNCERTAIN_CONFIDENCE,
    UNCERTAIN_COST_GAP,
    bayes_update,
)

FREE_EVIDENCE = ("E1", "E2")
PAID_EVIDENCE = ("E3", "E4")


@dataclass
class Decision:
    """The outcome of one policy run on one benchmark case."""

    action: str
    evidence_used: list[str]


class Policy(ABC):
    """A decision rule: observe evidence, then commit to one repair action."""

    name: str

    @abstractmethod
    def decide(self, case: dict) -> Decision:
        """Choose an action for a case whose `{E1..E4}_outcome` entries may be None."""


def observe_free_evidence(posterior: dict, case: dict) -> tuple[dict, list[str]]:
    """Bayes-update on E1/E2, which cost nothing, and return the evidence observed."""
    used = []
    for key in FREE_EVIDENCE:
        outcome = case.get(f"{key}_outcome")
        if outcome is not None:
            posterior = bayes_update(posterior, key, outcome)
            used.append(key)
    return posterior, used


def expected_action_cost(posterior: dict, action: str) -> float:
    """Average cost of taking `action`, weighted by belief in each hidden state."""
    return sum(posterior[state] * ACTION_COSTS[action][state] for state in STATES)


def best_expected_cost_action(posterior: dict) -> tuple[str, float]:
    """The action with the lowest expected cost, and that cost."""
    costs = {action: expected_action_cost(posterior, action) for action in ACTION_ORDER}
    best = min(costs, key=costs.get)
    return best, costs[best]


def act_or_escalate(posterior: dict) -> str:
    """Lowest-expected-cost action unless the decision sits in the uncertain band.

    The band is defined in the decision record: escalate when the two cheapest
    actions are within UNCERTAIN_COST_GAP of each other, or no single state
    reaches UNCERTAIN_CONFIDENCE.
    """
    ranked = sorted(ACTION_ORDER, key=lambda a: expected_action_cost(posterior, a))
    cost_gap = expected_action_cost(posterior, ranked[1]) - expected_action_cost(posterior, ranked[0])
    if cost_gap < UNCERTAIN_COST_GAP or max(posterior.values()) < UNCERTAIN_CONFIDENCE:
        return "Escalate"
    return ranked[0]


def expected_information_gain(posterior: dict, evidence_key: str) -> float:
    """Expected reduction in belief entropy from observing `evidence_key`."""
    likelihoods = LIKELIHOODS[evidence_key]
    outcomes = sorted({outcome for state in STATES for outcome in likelihoods[state]})
    conditional_entropy = 0.0
    for outcome in outcomes:
        p_outcome = sum(posterior[state] * likelihoods[state].get(outcome, 0.0) for state in STATES)
        if p_outcome <= 0:
            continue
        posterior_after = {
            state: posterior[state] * likelihoods[state].get(outcome, 0.0) / p_outcome
            for state in STATES
        }
        conditional_entropy += p_outcome * entropy(posterior_after)
    return entropy(posterior) - conditional_entropy


def entropy(distribution: dict) -> float:
    """Shannon entropy in bits of a `{state: probability}` mapping."""
    probabilities = [p for p in distribution.values() if p > 0]
    return -sum(p * math.log2(p) for p in probabilities)


def best_evidence_per_dollar(
    posterior: dict, case: dict, used: list[str], candidates: tuple[str, ...], min_score: float
) -> str | None:
    """Unused candidate evidence with the highest information gain per dollar.

    Evidence that cannot move the belief is never worth buying, and free
    evidence scores infinity. Returns None when nothing beats `min_score`.
    """
    ranked = []
    for key in candidates:
        if key in used or case.get(f"{key}_outcome") is None:
            continue
        gain = expected_information_gain(posterior, key)
        if gain <= 0:
            continue
        score = gain / EVIDENCE_COSTS[key] if EVIDENCE_COSTS[key] > 0 else math.inf
        if score > min_score:
            ranked.append((score, key))
    return max(ranked)[1] if ranked else None


def state_to_action(state: str) -> str:
    """The repair action the decision record prescribes for a hidden state."""
    return STATE_TO_ACTION.get(state, "Escalate")

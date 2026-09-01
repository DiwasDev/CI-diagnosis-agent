"""Policy implementations for the CI diagnosis decision study.

Every policy implements the Strategy pattern: a common `Policy` interface with a
single `decide` method, so `experiments.evaluation` can evaluate any of them
without knowing how the decision was reached.
"""

from experiments.policies.baseline import MajorityBaseline
from experiments.policies.belief_only import BeliefOnly
from experiments.policies.expected_cost_threshold import ExpectedCostThreshold
from experiments.policies.info_gain import InfoGainPerDollar
from experiments.policies.value_of_information import ValueOfInformation
from experiments.policies.derived_threshold import DerivedThreshold

__all__ = [
    "MajorityBaseline",
    "BeliefOnly",
    "ExpectedCostThreshold",
    "InfoGainPerDollar",
    "ValueOfInformation",
    "DerivedThreshold",
]

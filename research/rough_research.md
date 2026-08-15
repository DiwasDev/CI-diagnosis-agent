# Problem Statement

> The agent observes a failing CI pipeline, forms mutually exclusive hypotheses, and provides the user with a possible diagnosis if it is confident.

## Research Goals

- Gather information about the causes of failing CI runs and determine the hidden states of the agent.
- Know what the agent needs to observe to reduce its uncertainty.
- Determine what actions it can take.
- Determine suitable policies that lead to those actions.

## Research Methods

- Research papers
- Reddit discussions
- Blog posts and indie developer opinions

## Research Findings

### From Research Papers

**1. LogSage** ([arxiv.org/abs/2506.03691](https://arxiv.org/abs/2506.03691?utm_source=chatgpt.com))

- **Findings:** Dumping every piece of information into an LLM wastes tokens and increases hallucination.
- **Impact on design:** The agent should choose evidence based on uncertainty reduction.

**2. A Tale of CI Build Failures: An Open Source and a Financial Organization Perspective** ([research.tudelft.nl](https://research.tudelft.nl/en/publications/a-tale-of-ci-build-failures-an-open-source-and-a-financial-organi/))

- **Findings:** CI build failures occur across many different failure categories, including testing, compilation, dependencies, deployment, release preparation, and infrastructure. The study analyzed 34,182 failing builds across open-source and industrial organizations.
- **Impact on design:** The agent should maintain multiple candidate explanations for a CI failure rather than assuming every failure belongs to exactly one universal category.

**3. MSeer — An Advanced Technique for Locating Multiple Bugs in Parallel**

- **Findings:** A program can contain multiple bugs simultaneously. The authors specifically note that techniques designed for exactly one bug become problematic when multiple bugs are present, since different failed tests may be caused by different underlying bugs.
- **Impact on design:** The CI diagnosis agent should not represent the hidden state as exactly one winning cause. Multiple faults/causes should be allowed to exist simultaneously.

**Important assumption:** Since the events are not mutually exclusive, P(A or B) = P(A) + P(B) − P(A ∩ B).

**4. "Programmers' Build Errors: A Case Study at Google"**

- **Findings:** 90% of build errors are caused by 10% of the problems — the distribution is heavily skewed.
- **Impact on design:** There's no need for hundreds of hidden states; the 5–10 most frequent are sufficient for a baseline.

### Android Research Across Open-Source Build Failures

A study across build failures in 200 open-source projects found that the majority of failures fall into these categories. The table below shows the distribution of 139 total issue instances across 102 successfully resolved failing projects.

| Category | Approx. Share |
| :--- | :--- |
| Development-environment errors | 45% |
| Dependency / Gradle errors | 42% |
| Configuration errors | 8% |
| Syntax/API errors | 5% |

**Takeaway:** A few failure types dominate over the others, and a single failure may point toward multiple causes.

### Refined Hypothesis Set

The table below maps the original hypothesis set to the refined, more actionable set:

| Original Hypothesis | Updated Belief / Granular Hypothesis | Why the Update Matters |
| :--- | :--- | :--- |
| **H_flaky** | **H_flaky_test** vs. **H_timing_race** | Distinguishes pure non-determinism from load-dependent race conditions in test setup. |
| **H_environment_fault** | **H_container_image_fault** vs. **H_infra_provisioning_fault** | Fix paths diverge completely: local image rebuild vs. a DevOps infrastructure ticket. |
| *(Missing)* | **H_human_operator_error** | Catches branch/commit anomalies (force pushes, bad merges) before burning LLM execution tokens. |
| **H_fault_revealing** | **H_fault_revealing** (Code Bug) | A direct codebase failure requiring a developer fix. |
| **H_dependency_fault** | **H_dependency_fault** | Outdated, missing, or upstream registry failures. |
| **H_config_error** | **H_config_error** | Misconfigured environment variables, CI YAML syntax, or secrets. |
| **H_shared_root_cause** | **H_shared_root_cause** | A compound identifier linking multiple test failures. |

## The Problem with Mutually Exclusive Sets

The value-of-information formula requires hypotheses to be mutually exclusive; otherwise the resulting numbers are misleading.

Forming every possible combination of failures would yield 2⁹ = 512 hypotheses, which is impractical for a baseline version.

## The New Approach

Two failures might not always occur at the same time, and some failures may be genuinely mutually exclusive. For example, Hypothesis 1 and Hypothesis 2 might be able to co-occur, but Hypothesis 1 and Hypothesis 3 cannot.

I shifted the goal from listing every possible edge case to constructing a set of individual hypotheses and joint hypotheses, while dropping those that are not plausible or that have very low joint probability.

For some hypotheses, this assumes P(A and B) ≈ P(A) × P(B), where P(A ∩ B) is treated as negligible or artificially assumed to be zero to create a baseline.

### After Discussion on Reddit and Further Research, I Constructed a Board of Hidden States

| Node | Role |
| :--- | :--- |
| **H_human_operator_error** | If confirmed, this explains the failure away — short-circuiting the rest of the board via "explaining away," rather than requiring an edge to every other hypothesis. |

**Marginal beliefs (independent):**

- H_flaky_test
- H_timing_race
- H_fault_revealing
- H_dependency_fault
- H_config_error
- H_container_image_fault
- H_infra_provisioning_fault

**Kept edges (the only two co-occurrence relationships worth modeling explicitly):**

| Edge | Status |
| :--- | :--- |
| H_flaky_test — H_fault_revealing | Confirmed; cf. Haben et al. 2023 (Section 9): ~1/3 of regression faults had flaky histories — real, measured, and kept. |
| H_timing_race — H_fault_revealing | Plausible but not yet confirmed. A race condition can itself be a genuine concurrency bug rather than a test artifact — reasoned by analogy from the row above, not independently measured. |

**H_container_image_fault × H_infra_provisioning_fault** — These were split apart precisely because they have different owners and different fixes (Section 12); there is no cited reason to expect them to co-occur more than chance. Treated as independent.

**H_dependency_fault × H_config_error** — Plausible on paper (a bad lockfile setting could look like either), but no CI-specific source was found establishing that these co-occur more than chance.
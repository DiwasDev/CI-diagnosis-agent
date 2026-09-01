# Research File — CI Diagnosis Agent

## Problem statement
The agent observes a failing CI run (failing test IDs, logs, diff/commit, recent test-history). It must select the next diagnostic action because whether the failure is a real regression, flaky, an environment fault, or another cause is not known.

## Project objective
Build and test a small agent that, given incomplete evidence from a CI run, chooses the next diagnostic action (ask for more evidence, or recommend a specific fix) — not a one-shot classifier — modeled as sequential decision-making under partial observability (POMDP).

## Technical terminology
- **CI (Continuous Integration):** automated build/test on every commit.
- **Flaky test:** fails/passes on unchanged code — the result carries no information about correctness.
- **POMDP:** decision framework where the true state isn't directly observable, only evidence about it.
- **Hidden state / belief state:** the unobserved cause; a probability distribution over possible causes.
- **Noisy-OR:** compact model for combining multiple non-exclusive causes without a full joint table.
- **Value of Information (VoI):** expected reduction in loss from gathering more evidence, minus the cost of gathering it.
- **Threshold policy:** act above a confidence threshold, gather evidence in a middle band, withhold below it — thresholds set by cost ratios, not fixed.
- **Explaining away:** confirming one sufficient cause lowers belief in competing causes.

## Search queries
- predictive test selection continuous integration
- reinforcement learning test case prioritization
- flaky test detection machine learning
- root cause analysis CI pipeline failure multiple causes
- factored POMDP sparse belief state
- value of information decision theory
- GitHub Actions REST API workflow logs
- TravisTorrent CI dataset

## Reddit communities (verified active)
| Subreddit | Why |
|---|---|
| r/ExperiencedDevs | Senior engineers who've owned a CI pipeline — real cost tradeoffs |
| r/devops | Broadest home for CI/CD pipeline pain |
| r/softwaretesting | Most directly on-topic — testers/QA |
| r/SoftwareEngineering | Theory/architecture framing questions |
| r/MachineLearning | RL/POMDP/belief-state side (strict on self-promotion — post substance only) |
| r/mlops | Production-agent framing, closest to existing professional identity |
| r/ComputerScience | Definitional questions (is POMDP the right model here) |
| r/programming | High-traffic, general technical audience |

## Relevant X accounts (verified real, active)
- **@jyangballin** (John Yang) — creator of SWE-bench/SWE-agent; AI agents acting on real repos
- **@KLieret** (Kilian Lieret) — SWE-agent co-author, benchmark construction
- **@Mark_Harman** — UCL/ex-Meta, search-based software testing pioneer (real, but low X activity — don't expect replies)

## 5 useful papers/datasets
1. Spieker, Gotlieb, Marijan, Mossige — "Reinforcement Learning for Automatic Test Case Prioritization and Selection in Continuous Integration" (ISSTA 2017)
2. Machalica, Samylkin, Porth, Chandra — "Predictive Test Selection" (Facebook, ICSE-SEIP 2019) — real production cost-asymmetric thresholds
3. Haben, Habchi, Papadakis, Cordy, Le Traon — "The Importance of Discerning Flaky from Fault-triggering Test Failures" (Chromium case study, arXiv:2302.10594) — evidence hidden states are non-exclusive
4. Pauker & Kassirer — "The Threshold Approach to Clinical Decision Making" (NEJM, 1980) — the structural template for the act/gather/withhold policy
5. TravisTorrent (Beller et al.) — ~2.6M labeled Travis CI builds; useful for the failure-taxonomy, not directly for GitHub Actions-specific test cases (platform mismatch — flagged, not silently reused)

## Questions I wanted to answer
- What exactly counts as "a CI failure" — test assertion, build step, infra, or flakiness — and does the answer change the agent design?
- Is the action space just "select next test," or does it include rerun/bisect/escalate?
- What's the actual evaluation metric — tests-to-diagnosis, cost-weighted error, time-to-signal?
- Where do labeled cases come from without a real company/CI history?
- How should non-mutually-exclusive hidden states be represented without the joint blowing up (2^N)?
- Without real cost data, how are expected-loss/VoI numbers grounded rather than guessed?

## Important AI prompts/errors
- Initial upload of 4 supporting chapter files failed silently (uploads folder was empty each time checked) — all research in this file was produced without them.
- Declined to invent a single dollar cost for "a wrong CI diagnosis" — real sources measure general production downtime, not this specific failure mode; flagged the gap rather than papering over it with a fabricated number.
- One hypothesis-interaction edge (`H_timing_race`–`H_fault_revealing`) is reasoned by analogy, not independently confirmed — kept labeled as such rather than presented as established.
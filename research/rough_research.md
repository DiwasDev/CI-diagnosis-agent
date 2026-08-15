## Problem Statement

``` The Agent observes a failing CI pipelines makes some mutually exclusive hypothesis and provides the user with the possible diagnosis if it is confident```


## Research goals
-> Gather information about the causes of failing CI run and determine hidden states of Agent.
-> Know what the agent need observe to reduce it's uncertainity.
-> What actions can it take ?
-> Determine suitable policies that lead to the action.


### Research methods 
-> Research papers
-> Reddit discusions
-> Blogpost and indie developer opinions


### Research findings.

### From research papers. 



1. LogSage(https://arxiv.org/abs/2506.03691?utm_source=chatgpt.com)

        Findings:  Dumping every information to LLM wastes tokens & increases hallutination 
        Impact on design: Agent  chooses evidentce based on uncertainity reduction


2. A Tale of CI Build Failures: An Open Source and a Financial Organization Perspective(https://research.tudelft.nl/en/publications/a-tale-of-ci-build-failures-an-open-source-and-a-financial-organi/)

        Findings: CI build failures occur across many different failure categories, including testing, compilation, dependencies, deployment, release preparation, and infrastructure-related failures. The study analyzed 34,182 failing builds across OSS and an industrial organization
        Impact on design: The agent should maintain multiple candidate explanations for a CI failure rather than assuming every failure belongs to exactly one universal failure.

3. MSeer — An Advanced Technique for Locating Multiple Bugs in Parallel

        Findings: A program can contain multiple bugs simultaneously. The authors specifically point out that techniques designed for exactly one bug become problematic when multiple bugs are present, because different failed tests may be caused by different underlying bugs.
        The CI diagnosis agent should not represent the hidden state as exactly one winning cause. Multiple faults/causes should be allowed to exist simultaneously.

Important assumption.
     Since the events are not mutually exclusive so P(A or B) = P(A) + P(B) - P(A N B)


4. "Programmers' Build Errors: A Case Study at Google"
        
       Findings: 90% of the build errors are caused by 10% of the problems, distribution is heavily skewed.
       Impact on design: No need of 100s of hidden stattes, most frequent 5-10 is good for baseline.


Andriod research acorss build fails across 200 opensource proejcts notes that majority of the failure are also in these type of category 

Distribution of 139 total issue instances from 102 successfully resolved failing project.
Category	Approx. share
Development-environment errors	45%
Dependency / Gradle errors	42%
Configuration errors	8%
Syntax/API errors	5%

Takeway: Few failure types dominate over other.And one fail may point towards multiple causes.


The table below maps the original hypothesis set to the refined, actionable set:

| Original Hypothesis | Updated Belief / Granular Hypothesis | Why the Update Matters |
| :--- | :--- | :--- |
| **H_flaky** | **H_flaky_test** vs. **H_timing_race** | Distinguishes pure non-determinism from load-dependent race conditions in test setup. |
| **H_environment_fault** | **H_container_image_fault** vs. **H_infra_provisioning_fault** | Fix paths diverge completely: local image rebuild vs. DevOps infrastructure ticket. |
| *(Missing)* | **H_human_operator_error** | Catches branch/commit anomalies (force pushes, bad merges) before burning LLM execution tokens. |
| **H_fault_revealing** | **H_fault_revealing** (Code Bug) | Direct codebase failure requiring developer fix. |
| **H_dependency_fault** | **H_dependency_fault** | Outdated, missing, or upstream registry failures. |
| **H_config_error** | **H_config_error** | Misconfigured environment variables, CI YAML syntax, or secrets. |
| **H_shared_root_cause** | **H_shared_root_cause** | Compound identifier link across multiple test failures. |


## The problem with mutually exclusive sets
-> The value of information formual requires the hypothesis to be mutually exclusive if they aren't the numbers are misleading.

While forming every possible combination of falures will yield 2^(9) = 512 hypoethesis, both are impractical for a baseline version.


## The new approach
-> Two failures might not always have occured at the same time and some failure might be geneunely mutually excluisive, or let's say Hypotheis1 and Hypothesis can occur at the same time but Hypothesis 1 and Hypothesis 3 can't occur at the same.

I shifted the goal from listing everyposibe edge cases to constructing the set of individial hypothesis, and  joint hypotehsis while dropping those which are not posssbible and have very low joint proabability

For some hypothesis this assumes
P(A and B) ≈ P(A) * P(B), while P(A N B) is negligible or artificially assumed to be zero to create a baseline.



### After discussion on reddit and research I constructed board of hidden states.

Node	Role
H_human_operator_error	If confirmed, explains the failure away — short-circuits the rest of the board via "explaining away," rather than needing an edge to every other hypothesis

Marginal beliefs (independent):

Hypothesis	Independent belief
H_flaky_test	
H_timing_race	
H_fault_revealing	
H_dependency_fault	
H_config_error	
H_container_image_fault	
H_infra_provisioning_fault	

Kept edges (the only two co-occurrence relationships worth modeling explicitly):

Edge	Status
H_flaky_test — H_fault_revealing	Confirmed, cite Haben et al. 2023 (Section 9): ~1/3 of regression faults had flaky histories — real, measured, keep

H_timing_race — H_fault_revealing	Plausible, not yet confirmed. A race condition can itself be a genuine concurrency bug rather than a test artifact — reasoned by analogy from the row above, not independently measured. 

H_container_image_fault × H_infra_provisioning_fault — these were split apart precisely because they have different owners/fixes (Section 12); no cited reason to expect them to co-occur more than chance. Treat as independent.

H_dependency_fault × H_config_error — plausible on paper (a bad lockfile setting could look like either), but I found no CI-specific source establishing this co-occurs more than chance. 
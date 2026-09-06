# Reddit Discussions — CI Diagnosis Agent

Accounts used: u/Elegant_Quantity_583, u/No-Cheetah-4745. Removed posts kept in full (bottom); live posts linked.

| Community | Link | Questions asked | Replies | My next answer | Design change |
|---|---|---|---|---|---|
| r/devops | ❌ removed by mods | How do you think on a failed CI run? Flaky vs real? When are you sure? | Flaky = passes on retry. Root causes often outside pipeline, red herrings. Maybe don't build it. Existing agents already do this. Tests vs plumbing first; read first error, not last. Sure = reproduces locally. No nearby code change = flaky. | Defended iterative belief-updating agent; asked what to observe, when to stop | Added local-repro check; changed-files as evidence |
| r/QualityAssurance | ❌ removed by mods | First thing you check? Flaky vs genuine? When do you stop? | First real error → recent code changes → rerun unchanged = flaky | — | Rerun-same-test + recent-changes as evidence |
| r/AI_Agents | ❌ removed by Reddit filters | Are these 6 hidden states right? What's missing / not actionable? | `H_shared_root_cause` is a relationship between failures, not a cause | — | Removed `H_shared_root_cause`; redesigned hidden states |
| r/LangChain | ❌ removed by Reddit filters | Same 6 hidden states, LangGraph framing | Remove `H_shared_root_cause`; use a DB graph, not a state flag | — | Removed `H_shared_root_cause` |
| r/LLMDevs (hidden states) | ❌ removed by Reddit filters | Same — missing / not-actionable states? | Add `H_timing_race`, `H_human_error` (~15%), `H_stale_cache`. Split env fault (image vs infra). Diagnosis confidence ≠ evidence sufficiency → per-hypothesis evidence checklist. Split `H_flaky`: in-test vs around-test. | Two-agent split (human-error checker → diagnosis); joint hypotheses, only 2 edges kept (flaky↔real-bug: Haben et al. 2023; timing-race↔real-bug: plausible) | Hidden-state redesign; two-agent architecture; evidence-completeness gate; flaky split |
| r/LLMDevs (Bayesian, posted twice) | ❌ removed by Reddit filters | Do my priors/likelihood tables make sense? Are my synthetic test cases realistic? | Mutual exclusivity + independence is the real risk. `S7 Other` absorbs miscalibration. Real failures are stacked (dep+flake); add multi-cause bucket, refuse when top-2 within factor ~2 | — | Multi-cause bucket + abstain rule planned |
| r/LLMDevs (sanity check) | ✅ [live](https://www.reddit.com/r/LLMDevs/comments/1vv3370/sanity_check_for_ci_diagnosis_agent_hidden_states/) | Sanity-check hidden states + priors (375 paper cases). How to build likelihoods / test cases? | Cheaper to just prompt Claude? Build `P(log fingerprint \| state)`: cluster logs by first-failing step, hand-label; synthetic test = swap smoking-gun line, posterior must flip | Just-prompting is static; this agent iterates and fetches evidence only when its cost < cost of an uncertain report | — |
| r/LLMDevs (cost matrix) | ✅ [live](https://www.reddit.com/r/LLMDevs/comments/1w2hecn/does_this_cost_matrix_make_sense_for_a_ci_failure/) ([r/cicd crosspost](https://www.reddit.com/r/cicd/comments/1w2hf9e/does_this_cost_matrix_make_sense_for_a_ci_failure/)) | Escalate $50 / correct fix $8.33 / wrong fix $75.07 — is flat escalation and flat wrong-fix too simplistic? | Flat $50 undercounts slow failure modes. Flat is fine unless it masks a fat tail (shared config, cross-pipeline); use blast-radius override; only 1–2 states need distributions | — | No numeric change; fat-tailed failures need special routing |
| r/agenticAI (repost) | ⚠️ not indexed | Same cost matrix | Split cost into diagnosis time / availability / blast radius. Log evidence, margin, action, outcome; calibrate from incidents; escalate when margin narrow | — | Decision logging + calibration adopted |
two agents — human-error checker, then diagnosis agent.

---

## Full transcripts (removed posts only)

### 4.1 r/devops — "AI Agent for CI Failure Diagnosis" — ❌ removed by moderators

**Post (u/Elegant_Quantity_583, 22d ago):**

> I'm trying to build an agent that finds the reason why CI run failed.
>
> Like, what are the things going on in your head — let's imagine your brain has something like a belief system that sort of makes you suspect certain things more.
>
> I want to know how practitioners think: what doubts they are holding the moment they see a CI failure, and how they determine what to look for to find the real cause, and if it's a real code failure or some flaky test.
>
> And finally, at what point do they determine that they're pretty much sure about the cause?

**Comments:**

**u/aenae** (4 pts):
> Flaky means it works after just running it again. So just write a script that looks at the last 1000 pipelines, get their jobs, see if any pipeline had a job fail, the user retried it and it worked. If that happened more than once, fix that test. No need for an agent.

**OP:**
> Yeah, it works when you have a lot of pipeline data. I'm trying to build a general sort of agent. Like you run the pipeline, if it fails, agent gets the log message and pipeline run info. Now comes the part about what beliefs about the cause it should hold.
>
> So, if you see a CI run failing, what sort of general beliefs do you make? And generally speaking, what do you do to choose between those beliefs as considered as reality (cause)?
>
> But probably you stop after a certain number of pieces of evidence. How do you know that you're sure about the cause, and no more info is needed?

**u/Low-Opening25:**
> Appreciate you aren't using LLM to write, but the term is "assumptions" not "beliefs".
>
> If you work with decent engineers instead of a bunch of amateurs then they won't be making any obvious errors in the pipelines themselves that can be solved by looking at the logs. What you will often find is that the root cause of the issue is dependencies outside of pipelines and likely obfuscated by red herring errors. Your agent will be limited because its view is just the pipeline and it will be missing the context of how everything fits together and will be taking error messages literally, inevitably chasing down wrong rabbit holes.

**OP:**
> Thanks, that really brings a new perspective — only logs won't be enough. So my idea is that when it receives a CI fail, it has something like belief tokens — let's say 100 tokens it has to spend over assumptions.
>
> e.g. (initial input is the log of the failed CI): Red Herring Error: 30, Flaky test: 10, assumption3: 40, assumption: 20.
>
> It can check a lot of things, but it chooses to check the things that are likely to reduce its uncertainty about the cause. We can control what type of information it's allowed to fetch; it's an iterative process, we're not dumping everything into one prompt. It checks one piece of evidence, re-spends belief tokens over the strongest assumption.
>
> So, what are the things that the agent should be able to observe — env variables, your code, everything that comes to your mind. Let's assume for a second that it can fetch anything if we choose to let the agent use it if it asks.
>
> At last we can set the rule that if confidence in 1 assumption exceeds 80 points, then assume that's the cause and give a report to the user, else ask the user to diagnose on their own.
>
> I'd love your opinion on this, and what might be the causes of wrong diagnosis — is it only about time, or is something else also involved?

**u/mo0nman_** (4 pts):
> I think the first thing you should ask yourself is whether this is something that even needs to be solved.
>
> CI failure diagnosis is directly related to how well the pipelines are written. If they error with minimal or hard-to-interpret messages, the solution is to write better pipelines. Don't waste a bunch of compute on generative AI.

**u/ceejayoz:**
> Isn't that its job? It should be able to run the tests and see.

**OP:**
> I think you misunderstood — I'm asking about the cases when your tests sometimes pass and sometimes fail on the same code. I think my post isn't clear; I edited it. *(re-pasted original post)*

**u/ceejayoz:**
> "Assess this test failure." Mine tell me they think certain tests are flaky unprompted, with evidence.

**OP:**
> Sorry, but I didn't get what you're trying to say.

**u/ceejayoz:**
> I'm saying your agents can already do what you want.

**OP:**
> Yeah, if we are [talking about] existing coding agents, but I'm trying to build my own agent.

**u/ceejayoz:**
> Unless you're hand-training a model, "an agent" is just a prompt saying something like "investigate this test failure".
>
> You might give it info or tools to look at the logs, you might tell it to consider the possibility of flakiness, but all that depends on what you can provide it, and what you want it to do.
>
> Consider how you find a flaky test. You probably re-run the specific test a few times, then the whole suite a few times, yeah? Teach it that.

**OP:**
> Thanks for the info but I'm trying to build my own architecture, so the agent I'm building sets its beliefs. As it sees a CI fail, it searches for the evidence that it's allowed to use that clears out a lot of beliefs, and this is how it reduces its uncertainty. Not just an API call where I dump every piece of information. Let's think of it like you're trying to train someone to do your work — somewhat similar to how humans work.
>
> But I'm not an expert in this field. Probably I learned about Git just a few months back. So, I'm wondering what those initial beliefs should be. And what is the info that should be accessible to the agent if it asks? Excluding credentials, API keys.
>
> And at last it needs to give a diagnosis, so at what point do you feel like "I'm very sure that this is a problem, let's fix this"?
>
> And I think we're comparing the benefit of evidence vs the benefit of acting now. Is that benefit only about time, or are there other costs too?
>
> And if we give a wrong diagnosis and the user acts on it, what do you think we measure cost in?
>
> And I think always there should be one belief that asks, "Is this test flaky?" I think we should check that first. But how do you guys check that in practice? Can you please give me a list of ways you do it?
>
> So in summary, I'm asking: what information should the agent be able to access, what should the beliefs be, when should it stop, and what should it search over or do to catch flaky. I'd love your take.

**u/ceejayoz:**
> This really is an iterative process. Point it at a test you think is flaky. Don't tell it! See what it figures out. See where it gets stuck, where it doesn't have the right tools, and adjust prompts and access accordingly. Retry with a fresh context and see if it's better. Keep tweaking until happy. It's an ongoing maintenance thing on your part, not a single-shot.

**u/Low-Opening25:**
> Find new job. *(snark)*

**u/Worth_Wealth_6811:**
> The first split in my head is always: did it die in my tests or in the plumbing before them — install steps, docker pulls, runner setup. Plumbing failures are almost never your diff. After that I read the first error in the log, not the last, since CI logs cascade and the bottom is mostly noise. I only call it sure once I can reproduce the failure locally on demand; before that it's just a theory.

**u/Raja-Karuppasamy:**
> First thing I check is "has this exact test failed before with no code changes nearby" — if yes, flaky, not real.
>
> After that I weight what changed in the diff. Config file touched = suspect config first. Pure logic file = more likely real regression.
>
> "Pretty sure about the cause" = I can reproduce it locally with the same inputs. Can't repro locally but fails consistently in CI = different bucket — treat as env drift, not code bug.
>
> Been trying to turn this gut-feel process into an actual model instead of vibes; the hard part isn't the logic, it's getting labeled data (this failure was flaky vs real), which most teams don't have lying around.

---

### 4.2 r/QualityAssurance — "AI Agent for CI Fail Diagnosis" — ❌ removed by moderators

**Post (u/Elegant_Quantity_583, 22d ago):**

> I'm trying to build an agent that finds the reason why a CI run failed.
>
> For that I am curious to know how practitioners think when a CI run fails. When a CI build fails and there are multiple potential causes, what's the very first thing you inspect? What's your immediate mental checklist or set of suspicions when a pipeline turns red? How do you usually determine whether it's a genuine code issue versus just a flaky failure? And at last, how do you determine "I'm pretty much sure what's happening and there's not much value in additional searching"?
>
> Would love to hear how you all approach CI triage!

**Comments:**

**u/TocinoLips:**
> I usually start with the first real error in the logs, then check recent code changes. After that, rerun the same test unchanged — [if it passes] I start suspecting flakiness.

**u/Useful_Calendar_6274:**
> You don't even need to know that. AI is really capable for a lot of things and it's just starting to trickle down even among tech workers. You can just point it to the pipeline, leave it running and it knows what to do, spawn subagents and everything. It's just a matter of whether you really want to spend unknown tokens on that.

---

### 4.3 r/AI_Agents — "What hidden states should an AI agent track when diagnosing CI failures?" — ❌ removed by Reddit's filters

**Post (u/Elegant_Quantity_583, 20d ago):**

> Hi, if a CI run fails, there can be multiple explanations, so over the past few days I've been researching what the agent needs to have that helps me diagnose the failing Continuous Integration run.
>
> The agent first makes assumptions → searches for evidence → updates probability of each assumption → at the end, the agent takes an action like:
>
> - if very high confidence: ask the user to change the exact thing or to something specific.
> - if medium: hold, ask for more search evidence if the value of information is greater,
> - if the cost of being wrong is too high: simply escalate to human.
>
> I have mapped out some hidden states. They are not mutually exclusive, as a failing CI can be because of many reasons:
>
> - **H_flaky** — the test/system itself can behave nondeterministically
> - **H_fault_revealing** — the failure is actually revealing a real bug/regression
> - **H_dependency_fault** — something is wrong with a dependency
> - **H_environment_fault** — something in the execution environment is causing the failure
> - **H_config_error** — some CI/build/runtime configuration is wrong
> - **H_shared_root_cause** — multiple failures may actually be coming from the same underlying cause
>
> Each hypothesis has a probability that gets updated with evidence.
>
> Can you spot any weaknesses in here? What hidden states did I not include? Are these hidden states actionable? I'd [love] your honest opinion.

*(AutoModerator comment omitted.)*

**u/Apprehensive-Run7844:**
> The shared root cause one feels like it belongs in a different layer than the others — more of a relationship between failures than a standalone cause.

---

### 4.4 r/LangChain — "Modeling hidden states for a CI-diagnosis agent in LangGraph — feedback wanted" — ❌ removed by Reddit's filters

**Post (u/Elegant_Quantity_583, 20d ago):**

> I'm building an agent (on LangGraph) that diagnoses failing CI runs instead of just re-running the pipeline and hoping. The loop is: hypothesize → pull evidence via tools → update belief state → act.
>
> I'm representing the "why did this fail" question as a set of non-mutually-exclusive hidden states, each with a probability that gets updated as the agent gathers evidence (log parsing, git diff, past run history, etc.):
>
> - **H_flaky** — test/system behaves nondeterministically
> - **H_fault_revealing** — failure is a real bug/regression
> - **H_dependency_fault** — a dependency broke something
> - **H_environment_fault** — execution environment is the cause
> - **H_config_error** — CI/build/runtime config is wrong
> - **H_shared_root_cause** — multiple failures trace to one underlying cause
>
> At the end, the agent acts based on confidence: very high → propose a specific fix; medium → gather more evidence if the value of information justifies it; low-confidence-but-high-cost-of-being-wrong → escalate to a human.
>
> Since a lot of you have built LangGraph agents with real state schemas for multi-step diagnosis/investigation flows: what am I missing in this hidden-state list? Anything here not actually actionable once inferred?

**u/New_Fee972:**
> `H_shared_root_cause` is the one I'd remove, because I have never seen it stay actionable when deduced. Storing the graph, whether in [hydra]db or just an ordinary postgres schema, is more appropriate for the causal link than one state flag.

---

### 4.5 r/LLMDevs — "Building a CI-diagnosis agent — sanity check on the hidden states it tracks" — ❌ removed by Reddit's filters

**Post (u/Elegant_Quantity_583, 20d ago):**

> Shipping an agent that diagnoses why a CI run failed instead of leaving that to the human. Flow: hypothesize possible causes → search for evidence with tools → update probability per hypothesis → act based on confidence (recommend a specific fix if very confident, keep digging if medium confidence and it's worth it, hand off to a human if getting it wrong is expensive).
>
> Hypotheses tracked right now (can overlap):
>
> - **H_flaky** — flaky test/system
> - **H_fault_revealing** — real bug
> - **H_dependency_fault**
> - **H_environment_fault**
> - **H_config_error**
> - **H_shared_root_cause** — one cause behind multiple failures
>
> If you've built anything in this diagnostic-agent space: what's missing from this list, and does anything on it seem like it wouldn't actually be actionable once the agent is confident about it?

**u/Designer_Piece7723** (2 pts):
> I built something similar for our internal pipelines last year and the thing that tripped us up was not tracking "H_timing_race" separately — we kept having these failures that would disappear on retry but weren't flaky in the classic sense; they were actual race conditions in the test setup that only appeared under certain load patterns.
>
> Also your H_environment_fault might be too broad. We split ours into image/container issues vs infra provisioning failures because the fix paths are completely different — one needs a rebuild and the other needs a cloud team ticket.
>
> What we added later was H_human_error, which sounds dumb but turned out to be like 15% of our failures — someone pushed to the wrong branch or force-pushed over commits and the CI just did what it was told; the agent would spin forever looking for bugs that didn't exist.
>
> One thing I'm curious about: how does your agent handle when multiple hypotheses are correct simultaneously, like a real bug that only triggers because of a config error? We had some ugly cases where fixing just one thing would make the pipeline green but not actually solve the root problem.

**OP (19d ago):**
> Thanks — your question opened my eyes; I spent the whole morning trying to figure out its answer, and now I have a different approach. It's about first determining if it was a silly human mistake.
>
> I have now divided the work into 2 agents:
>
> - **First agent:** finds if the CI run failure was caused by a silly human mistake, like pushing to the wrong branch, etc.
> - **Second agent:** gets activated once the first agent confirms that it's not a silly problem.
>
> However, two failures might not always have occurred at the same time, and some failures might be genuinely mutually exclusive. For instance, Hypothesis 1 and Hypothesis 2 can occur at the same time, but Hypothesis 1 and Hypothesis 3 cannot.
>
> I shifted the goal from listing every possible edge case to constructing a set of individual hypotheses and joint hypotheses, while dropping those that are impossible or have a very low joint probability. For some hypotheses this assumes P(A and B) ≈ P(A) × P(B), while P(A ∩ B) is negligible or artificially assumed to be zero to create a baseline.
>
> Now it has these hypotheses:
>
> | Hypothesis |
> |---|
> | H_flaky_test |
> | H_timing_race |
> | H_fault_revealing |
> | H_dependency_fault |
> | H_config_error |
> | H_container_image_fault |
> | H_infra_provisioning_fault |
>
> Kept edges (the only two co-occurrence relationships worth modeling explicitly):
>
> | Edge | Status |
> |---|---|
> | H_flaky_test — H_fault_revealing | Confirmed — Haben et al. 2023 (Section 9): ~1/3 of regression faults had flaky histories — real, measured, keep |
> | H_timing_race — H_fault_revealing | Plausible, not yet confirmed. A race condition can itself be a genuine concurrency bug rather than a test artifact — reasoned by analogy from the row above, not independently measured |
>
> Additional notes:
> - **H_container_image_fault × H_infra_provisioning_fault:** split apart precisely because they have different owners/fixes; no cited reason to expect them to co-occur more than chance. Treat as independent.
> - **H_dependency_fault × H_config_error:** plausible on paper (a bad lockfile setting could look like either), but no CI-specific source establishes that these co-occur more than by chance.
>
> Now the second job is to find the real cause. Do you find anything bad about this structure?

**u/Innowise_:**
> One thing we'd track separately is confidence in the diagnosis vs confidence that the agent has enough evidence. A failed test plus a matching log can make one hypothesis look very strong, but if the agent never checked the deploy diff or environment state, that confidence can be misleading. We'd only let it act automatically when both are high.

**OP:**
> Good catch — and heads up in case you didn't see it, I posted an update below where I split this into two agents (one just checks for silly human mistakes like a wrong-branch push, the second only activates once that's ruled out).
>
> Your confidence-vs-evidence distinction is making me second-guess that split, though. Agent one could be confident it found a "silly mistake" without having checked enough to actually rule out a real bug underneath it — like a bad push that happens to coincide with an unrelated regression. Right now agent one has no signal for "I'm confident, but did I check enough?" before it decides not to hand off to agent two.
>
> Would you track that evidence-completeness check as part of each agent, or as a separate gate that has to pass before either agent is allowed to act on its own confidence? Could you please challenge me on this?

**u/eddzsh** (18d ago):
> The confidence vs evidence-completeness split is the right next cut.
>
> One practical way to implement the gate: keep a required evidence checklist per hypothesis (log match, deploy diff, env fingerprint, last green commit). Confidence can only go high after every item on that checklist is filled or explicitly marked N/A with a reason. That stops agent one from short-circuiting on a wrong-branch push that happens to sit next to a real regression.
>
> Also worth a separate H_stale_cache (CI caches, package caches, docker layer caches). It is not flaky and not a code bug, and the fix path is purge and rerun, not a patch.

**u/CautionIAmAGeek** (15d ago):
> H_flaky is worth tracking, but a flaky test is usually two states wearing one label: nondeterminism in the test (timing, shared fixtures, ordering) and nondeterminism around it (network, clock, seeded data). Collapsing them is how an agent ends up "fixing" a real bug by adding a wait. A cheap discriminator that works: rerun the same commit in isolation N times, then rerun it inside the full suite, and compare the two failure rates before you let the agent conclude anything. The other thing worth modeling is evidence per attempt (UI state, network calls, console) rather than a single confidence score, since a verdict you can inspect is the one people act on.

---

### 4.6 r/LLMDevs — "Bayesian CI Failure Diagnosis Agent — Feedback on Likelihoods & Test Cases" — ❌ removed by Reddit's filters (posted twice, identical)

**Post (u/Elegant_Quantity_583, 8d ago):**

> I'm building a small Bayesian agent that diagnoses why a Python CI run failed, then decides whether to auto-fix or escalate to a human. It uses Bayes' theorem to update beliefs over 7 hidden root-cause categories as it gathers evidence.
>
> I could really use a second pair of eyes on two things:
>
> 1. My likelihood tables — do the probabilities make sense, or am I baking in weird assumptions?
> 2. My synthetic test cases — do they look like realistic scenarios, or are they too contrived?
>
> **The Setup — 7 hidden states (mutually exclusive root causes):**
>
> | State | Description |
> |---|---|
> | S1 | Source Code Issues (syntax, import, logic) |
> | S2 | Project Config Issues (bad pyproject.toml, metadata) |
> | S3 | Dependency Failures (unresolvable packages, broken lockfiles) |
> | S4 | Static Analysis Failures (flake8, mypy, ruff, bandit, etc.) |
> | S5 | Test Failures (assertion errors, fixture failures) |
> | S6 | Environment Setup Issues (missing gcc, wrong Python version) |
> | S7 | Other (network flakes, OOM, rate limits) |
>
> **Priors (empirically counted from 567 open-source Python CI repair cases):**
>
> | State | Prior |
> |---|---|
> | S4 | 0.416 |
> | S3 | 0.312 |
> | S5 | 0.116 |
> | S2 | 0.058 |
> | S6 | 0.056 |
> | S1 | 0.027 |
> | S7 | 0.014 |
>
> **Evidence sources** — the agent queries evidence one by one (greedy EIG), updating beliefs after each observation.
>
> **E1 — Which pipeline step failed first?** Buckets: A Install, B Build, C Test, D Static Analysis, E Workflow/Env, F Ambiguous. Smoothed likelihood P(step | state):
>
> | State | A | B | C | D | E | F |
> |---|---|---|---|---|---|---|
> | S1 | 0.048 | 0.095 | 0.476 | 0.143 | 0.095 | 0.143 |
> | S2 | 0.231 | 0.026 | 0.436 | 0.077 | 0.077 | 0.154 |
> | S3 | 0.169 | 0.016 | 0.443 | 0.328 | 0.016 | 0.027 |
> | S4 | 0.025 | 0.008 | 0.079 | 0.649 | 0.025 | 0.215 |
> | S5 | 0.042 | 0.042 | 0.653 | 0.042 | 0.056 | 0.167 |
> | S6 | 0.053 | 0.053 | 0.684 | 0.079 | 0.053 | 0.079 |
> | S7 | 0.143 | 0.071 | 0.571 | 0.071 | 0.071 | 0.071 |
>
> Used Laplace +1 smoothing because some states only have 8–15 rows.
>
> **E2 — What files were changed in the fix commit?** Buckets: src, test, config, ci, doc, mixed, none. Smoothed likelihood P(files | state):
>
> | State | src | test | config | ci | doc | mixed | none |
> |---|---|---|---|---|---|---|---|
> | S1 | 0.409 | 0.182 | 0.046 | 0.046 | 0.046 | 0.227 | 0.046 |
> | S2 | 0.125 | 0.100 | 0.075 | 0.025 | 0.025 | 0.600 | 0.050 |
> | S3 | 0.201 | 0.027 | 0.027 | 0.011 | 0.005 | 0.723 | 0.005 |
> | S4 | 0.531 | 0.095 | 0.012 | 0.004 | 0.008 | 0.346 | 0.004 |
> | S5 | 0.219 | 0.315 | 0.014 | 0.014 | 0.014 | 0.411 | 0.014 |
> | S6 | 0.359 | 0.077 | 0.026 | 0.026 | 0.026 | 0.462 | 0.026 |
> | S7 | 0.067 | 0.400 | 0.067 | 0.067 | 0.067 | 0.267 | 0.067 |
>
> **E3 — Rerun outcome** (ASSUMED, not empirical):
>
> | State | pass_on_rerun | fail_on_rerun |
> |---|---|---|
> | S1 | 0.05 | 0.95 |
> | S2 | 0.05 | 0.95 |
> | S3 | 0.15 | 0.85 |
> | S4 | 0.03 | 0.97 |
> | S5 | 0.35 | 0.65 |
> | S6 | 0.50 | 0.50 |
> | S7 | 0.75 | 0.25 |
>
> **E4 — Local reproducibility** (ASSUMED, not empirical):
>
> | State | reproducible_locally | not_reproducible_locally |
> |---|---|---|
> | S1 | 0.92 | 0.08 |
> | S2 | 0.80 | 0.20 |
> | S3 | 0.45 | 0.55 |
> | S4 | 0.88 | 0.12 |
> | S5 | 0.70 | 0.30 |
> | S6 | 0.12 | 0.88 |
> | S7 | 0.15 | 0.85 |
>
> **Action Policy:**
> - FIX_CODE if P(S1) + P(S2) + P(S4) > 0.60 (safe, local changes)
> - FIX_DEPENDENCY if P(S3) > 0.80 (high bar — affects downstream)
> - ESCALATE otherwise (S5, S6, S7 need human context)
>
> **Test Cases I'm Using** — I generated 100 synthetic test cases by sampling evidence conditioned on the ground-truth state. A few representative ones:
>
> ```json
> {"test_id": "tc_001", "ground_truth_state": "S4", "ground_truth_label": "Static Analysis Failures", "evidence": {"E1_pipeline_step": "E", "E2_changed_files": "src", "E3_rerun_outcome": "fail_on_rerun", "E4_local_repro": "reproducible_locally"}, "expected_decision": "FIX_CODE"}
> {"test_id": "tc_002", "ground_truth_state": "S4", "ground_truth_label": "Static Analysis Failures", "evidence": {"E1_pipeline_step": "C", "E2_changed_files": "mixed", "E3_rerun_outcome": "fail_on_rerun", "E4_local_repro": "reproducible_locally"}, "expected_decision": "FIX_CODE"}
> {"test_id": "tc_003", "ground_truth_state": "S5", "ground_truth_label": "Test Failures", "evidence": {"E1_pipeline_step": "C", "E2_changed_files": "test", "E3_rerun_outcome": "fail_on_rerun", "E4_local_repro": "not_reproducible_locally"}, "expected_decision": "ESCALATE"}
> ```

**u/conifer_v11:**
> Priors summing is the easy check. The hard one is treating those 7 states as mutually exclusive and the evidence as independent. 567 cases is enough to get S4/S3/S5 looking stable and still be wrong on the tails. S7 "other" will eat every miscalibration — if it grows when you add a test, the likelihoods aren't identified.
>
> Your synthetic cases are single-cause. The ones that actually break CI are stacked (dep break + flake, or flake + bad cache). If those aren't in the 567, the posterior looks confident and picks the wrong hidden state. I'd add a multi-cause bucket and refuse to diagnose when two likelihoods are within a factor of ~2.

---

### 4.7 r/LLMDevs — "Sanity check for CI diagnosis agent hidden states, and How to generate test cases?" — ✅ [live](https://www.reddit.com/r/LLMDevs/comments/1vv3370/sanity_check_for_ci_diagnosis_agent_hidden_states/)

Priors recomputed from 375 paper-classified cases:

| Failure Category | Paper Code(s) | Count | Prior |
|---|---|---|---|
| Source Code Issues | P1 | 54 | 0.144 |
| Project Config Issues | P2 | 19 | 0.051 |
| Dependency Failures | P3 + P4 | 78 | 0.208 |
| Static Analysis Failures | P5 + P6 | 41 | 0.109 |
| Test Failures | P8 | 120 | 0.320 |
| Workflow Config Issues | W2 | 21 | 0.056 |
| Environment Setup Issues | W4 | 13 | 0.035 |
| Other | Remaining | 29 | 0.077 |
| **Total** | — | **375** | 1.000 |

**Comments (from the captured thread):**

**u/No_External7343:**
> Is it going to be a lot cheaper than feeding the log to Claude Code Sonnet and just prompting it?

**OP:**
> This is a bit different. Just prompting is static — it decides based on whatever evidence it has on log. But this is an iterative agent: it observes evidence (let's say logs) → updates its beliefs across causes of failure → asks for another piece of evidence to reduce uncertainty → updates it. And the most important part is that it only asks for evidence if the cost of having it is less than the cost of giving the cause analysis.

**u/eddzsh:**
> Priors from the paper counts are a fine starting distribution. The missing piece is likelihoods: P(log fingerprint | state), not P(state). A practical way to build those is to cluster real CI logs by the first failing step signature, then label each cluster with one hidden state by hand for a few dozen runs. Synthetic cases fall out of those clusters: take a log from state A, swap in the smoking-gun line from state B, and check the posterior flips. If it does not, your evidence channel is too coarse.

---

### 4.8 r/LLMDevs — "Does this cost matrix make sense for a CI failure diagnosis agent?" — ✅ [live](https://www.reddit.com/r/LLMDevs/comments/1w2hecn/does_this_cost_matrix_make_sense_for_a_ci_failure/) (crosspost on [r/cicd](https://www.reddit.com/r/cicd/comments/1w2hf9e/does_this_cost_matrix_make_sense_for_a_ci_failure/))

Posted by **u/No-Cheetah-4745**. Post summary: engineer time $100/hr; escalate = flat **$50** (30 min senior triage); correct fix = **$8.33** (5-min spot-check); wrong fix = **$75.07** (review patch, rerun CI, re-diagnose). Questions: is flat escalation too simplistic? Does every wrong action really cost the same?

**u/Certain_Brilliant199:**
> Escalating to a human always feeling like the safe choice is the whole problem. The 50 bucks is probably fine as a baseline, but if you've got one failure mode that consistently eats 2 hours of a senior dev's time, you're gonna undercount that real quick.
>
> Wrong-fix cost being flat makes sense if the cleanup is always the same steps, but in practice some bad patches are way more annoying to unwind than others — especially if they touch shared config or something that breaks other pipelines.

**u/lulu_dev:**
> Both of OP's questions are really the same question: does flattening the cost matrix ever change which action has the lowest expected cost? If escalation still wins by a wide-enough margin under the worst plausible variance in triage time or cleanup cost for a given state, the flat number was never actually deciding anything and more granularity there buys nothing. It only matters where a state's cost sits close enough to a decision boundary that the approximation could flip the argmin.
>
> So the fix isn't "add per-state granularity everywhere," it's "find the states where the flat number is masking a fat tail." Your point about shared config and cross-pipeline breaks is the real signal — a wrong-fix cost that's flat because cleanup is usually the same few steps is fine to approximate; a wrong-fix cost that occasionally cascades into breaking three other pipelines isn't a slightly-higher-mean case, it's a different distribution with a long tail that a single $75.07 point estimate can't represent at all. That's exactly the kind of state where escalation should structurally win regardless of the model's confidence — not via a bigger flat cost, but by treating "blast radius could be large" as its own override signal, the same way a lot of cost-sensitive systems hard-floor uncertain-and-high-stakes cases into a safe default rather than trusting the point estimate.
>
> Practical next step for OP: instead of re-deriving costs for all 7 states, find the 1–2 states with real fan-out risk and give only those a distribution or hard override — leave the rest flat, since the data so far suggests they don't need it.

---

### 4.9 r/agenticAI — "Does this cost matrix make sense for a CI failure diagnosis agent?" (repost) — ⚠️ link not indexed

Repost of 4.8 by **u/No-Cheetah-4745**; same post body.

**u/No_Order6491:**
> A flat escalation cost is a reasonable first control, but I'd split the model into diagnosis time by failure class, pipeline/deployment availability cost, and blast radius. The "wrong patch" cost should also separate harmless failures from changes that need rollback or leave partial state.
>
> More important than the first dollar estimates: log the evidence used, confidence/expected-cost margin, selected action, and eventual outcome. Then calibrate from observed incidents and make escalation or evidence-gathering the default when the margin is narrow or the evidence is stale. That gives you an audit trail and a safer way to improve the matrix than trying to perfect it up front.

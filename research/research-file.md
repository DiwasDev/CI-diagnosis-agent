# Final Research — CI Diagnosis Agent: Observation, Cost, and Test-Case Grounding

Written after actually reading the five uploaded course files (`week1-belief-engine-saturday.html` and the four `dryrun-ch*` chapters), which the first research file explicitly flagged as inaccessible at the time. That matters for what follows — see Section 0.

---

## 0. Two things the course material changes about the earlier research file

**0.1 — The board should be one Categorical distribution, not nine independent Bernoullis.**
The first research file (Sections 10–14) built a "noisy-OR" model: nine roughly-independent marginal beliefs `P(H_flaky)`, `P(H_fault_revealing)`, etc., each its own yes/no (Bernoulli) question, with a couple of hand-added interaction edges. That was a reasonable move *given no access to the course content* — but the course's actual Chapter 1 ("Email Behind the Curtain") and Chapter 3 ("Distribution Zoo") teach something narrower and stricter: a **belief board** is "100 points split across the live stories," and it must obey two rules stated explicitly in Chapter 1 — *no two boxes may both be true at once* (mutually exclusive) and *no true story may be left without a box* (collectively exhaustive). Chapter 3 then names this shape: a single yes/no question is a **Bernoulli**; a question with several exclusive, exhaustive outcomes is not nine Bernoullis, it's one **Categorical** distribution over nine boxes summing to 1.

This is exactly what you're now describing — "H_flaky_test means only P(H_flaky_test), since we are finding a mutually exclusive set" plus "2 joint cases." That's a pivot from *independent marginals with bolted-on interaction terms* to *one Categorical belief board with explicit joint boxes carved out as their own cells*. It's the right call, and it's the course's own design, not a deviation from it.

**0.2 — Assumption I'm making about "9 hypotheses, total":**
You didn't list the 9 by name, so here is my best reconstruction from your message plus the prior research file — **stated as an assumption, not a fact**:

| # | Box | Status |
|---|---|---|
| 1 | `H_flaky_test` (pure — flaky, not also fault-revealing) | carried over, now a pure cell |
| 2 | `H_timing_race` (pure) | carried over, now a pure cell |
| 3 | `H_fault_revealing` (pure — real bug, not flaky/timing-race) | carried over, now a pure cell |
| 4 | `H_dependency_fault` | carried over |
| 5 | `H_config_error` | carried over |
| 6 | `H_container_image_fault` | carried over |
| 7 | `H_infra_provisioning_fault` | carried over |
| 8 | `H_flaky_AND_fault_revealing` (joint box) | **new** — was an "edge" in v3, now its own MECE cell |
| 9 | `H_timing_race_AND_fault_revealing` (joint box) | **new** — same treatment |

That's 7 pure cells + 2 joint cells = 9, all mutually exclusive, all summing to 100%. **Please confirm this is what you meant** — if instead you meant a different 9 (e.g. keeping `H_unrelated_change` or `H_config_specific` from the original 8-hypothesis list in the first research file), the mechanism below is unaffected, only the table changes.

`H_human_operator_error` sits **outside** this board entirely, as Agent 1's own separate Bernoulli — matching your description ("first agent finds out whether it was silly human error, then hands to agent 2"). This also matches Chapter 1's Bernoulli/Categorical distinction directly: Agent 1 asks a single yes/no question (Bernoulli — "is this operator error?"); Agent 2, only reached on "no," asks a 9-way categorical question. Two different distribution shapes for two different questions, exactly the habit Chapter 3 is teaching.

---

## 1. Is expected loss / VoI even the right calculation here?

Yes — and this isn't just the general decision-theory literature (Howard 1966, Wald 1945, Chow 1970, Pauker & Kassirer 1980, all already in the first research file). It is **literally the mechanism the course itself builds**, chapter by chapter, for the email agent you're meant to be generalizing from:

- Chapter 4 ("What Should It Ask?") builds an **evidence planner**: given the current belief board and a tool ledger of historical branch rates, it ranks candidate next-questions by *expected reduction in the uncertainty that matters* — this is expected information gain, the same computation Krause & Guestrin's myopic-VoI fallback (already cited in file 1) formalizes.
- Chapter 5 ("Information Is Not Free") then wraps that in cost: `expected_loss[action] = Σ over stories: belief[story] × cost(action, story)`, and the stopping rule is `saving = expected_loss[best action now] − expected_loss[best action after the check]; if saving > cost_of(check): run the check`. That is Howard's VoI formula from file 1, verbatim, just written as running pseudocode instead of an equation.
- The worked example (message 101, ₹4,80,000 invoice) is the same threshold logic Pauker & Kassirer describe for clinical decisions: the agent doesn't act on "which story is most likely," it acts on "which action has the lowest expected harm" — belief 31% attack still makes *hold* win over *deliver* by ~500× in expected-loss terms, because the cost of the rare bad outcome dominates.

So: **yes, expected loss is the correct core calculation, and myopic VoI (per Krause & Guestrin, already flagged as the tractable approximation in file 1) is the correct way to decide whether the next observation is worth its cost.** The one adjustment worth making explicit for your two-agent architecture: Agent 1's gate needs its own tiny expected-loss calculation (2 stories: operator-error vs. real-issue) before handing off to Agent 2's 9-way board — don't treat the handoff itself as free. See Section 6 for why that matters and what it costs.

---

## 2. What the agent needs to observe, and the tools that provide it

**Hard constraint restated so it's not lost:** the agent does not execute anything — no test runs, no CLI, no re-triggering a job itself. Every tool below is a **read (GET) call against an API**, or a **write call that only posts a comment / label / check-run annotation** (never a re-run, never a merge, never a code change). This is deliberate and matches the course's own boundary: V5's "act" move is *tell the user the specific fix*, not *apply* it — the agent is capped at "suggest," the same ceiling Parasuraman/Sheridan/Wickens' GPWS example enforces in file 1 Section 11.

All of these are read-only calls against the **GitHub REST/GraphQL API**, since you said the whole thing runs on GitHub. I'm listing them mapped to which hidden state they actually discriminate — a tool that doesn't separate any two boxes is exactly the "favourite colour" trap Chapter 4 warns against.

| Tool / API surface | What it returns | Which hidden states it actually separates |
|---|---|---|
| **Workflow run + job status** (`GET /repos/{o}/{r}/actions/runs`, `.../jobs`) | Conclusion, timing, which specific job/step failed | First-pass triage: narrows to build-step vs test-step vs infra-step failure before any hypothesis is touched |
| **Job logs** (`GET .../jobs/{job_id}/logs`) | Raw stdout/stderr of the failing step | The single richest signal — a dependency-resolution error, a container pull failure, and a test assertion failure all look completely different in raw log text |
| **Workflow run *attempts*** (`GET .../runs/{run_id}/attempts/{n}`) | Whether this exact job was retried, and with what result | Directly discriminates `H_flaky_test`/`H_timing_race` from everything else: if attempt 1 failed and attempt 2 (same commit, same code) passed, that is the single strongest observable signal of non-determinism — this is what Bell et al.'s DeFlaker and the iDFlakies methodology (cited in file 1) actually use as ground truth |
| **Check Runs API** (`GET /repos/{o}/{r}/commits/{sha}/check-runs`) | Structured pass/fail + annotations per check, often with a categorized error `output.summary` | Cheap structured alternative/supplement to raw logs; some CI setups annotate flaky vs. hard failures already |
| **Compare / diff API** (`GET /repos/{o}/{r}/compare/{base}...{head}`) | Full file-level diff for the triggering commit or PR | Core input for `H_fault_revealing` vs. everything-not-code-related; also this is exactly Test Impact Analysis's input (Machalica et al., file 1) |
| **Commits API + git log** (`GET .../commits`) | Author, timestamp, parents, whether force-pushed (parent-history discontinuity) | The Stage-0 free gate for Agent 1 (`H_human_operator_error`) — a force-push, an amended commit, or a branch reset is visible here without opening a single log line |
| **Pull Request API** (`GET /repos/{o}/{r}/pulls/{n}`) | Base/head SHAs, mergeable state, requested reviewers, draft status, linked issues | Distinguishes "this diff was reviewed and approved" from "this is a fresh unreviewed push," relevant context for both agents' priors |
| **Dependency manifest / lockfile diff** (Contents API on `package-lock.json`, `requirements.txt`, `go.sum`, etc., diffed via the compare API) | Whether a dependency version actually changed in this commit | Directly discriminates `H_dependency_fault` from the rest — Seo et al. 2014 and Ziftci & Reardon (file 1) both point to dependency/programming faults as a dominant category, and this is the cheap check that tells you which |
| **CI config diff** (compare API scoped to `.github/workflows/*.yml`) | Whether the workflow file itself changed in this commit | Directly discriminates `H_config_error` |
| **Container/image reference in the workflow YAML + registry pull status in the logs** | Which base image was requested and whether the pull/build of it succeeded | Discriminates `H_container_image_fault` from `H_infra_provisioning_fault` (bad image tag vs. provisioning/network layer) |
| **Historical run list for the same workflow + branch/test** (`GET .../runs?branch=...&status=...`, paginated) | Pass/fail history over time for this exact job or test name | This *is* the "tool ledger" Chapter 4 uses — you cannot rank candidate evidence by expected information gain without a base-rate history to rank it against |
| **GitHub status page** (`https://www.githubstatus.com/api/v2/status.json` — a public, unauthenticated, read-only endpoint) | Whether GitHub Actions itself is currently degraded | Cheap, free, external corroboration for `H_infra_provisioning_fault` — if GitHub itself is reporting incidents, that's strong evidence pointing away from your code entirely |
| **Artifacts API** (`GET .../actions/artifacts`) | Uploaded test reports (JUnit XML, coverage, etc.), if the workflow uploads them | Structured per-test result detail when logs alone are ambiguous — only useful if the repo's workflow already uploads artifacts; the agent cannot generate one, only read what's there |

**What this list deliberately excludes, because you ruled it out:** anything that requires the agent to *run* something — no triggering a rerun, no dispatching a workflow_dispatch event, no SSH/CLI into a runner, no bisection. Bisection and delta-debugging (both named in file 1 Section 1) are **execution-based techniques and are out of scope for this agent as you've now defined it** — worth flagging explicitly since the first research file's literature review (Section 5–9) leaned on papers that assume an agent *can* run tests. Your agent can only ask a human to do that (see Section 5, HOLD).

---

## 3. Where the agent lives, and how it gets information

Given the "observe only, no execution, GitHub-based" constraint, the natural shape is a **GitHub App** (not an Action running on a runner — a runner is compute you'd be executing on, which is off-limits) that:

1. Is installed on the repo with **read-only permissions**: `actions:read`, `checks:read`, `contents:read`, `pull_requests:read`, `metadata:read`, plus `issues:write` / `checks:write` (write, but restricted to *posting a comment or annotation* — never a code or config write).
2. Is triggered by a **webhook** — most naturally `workflow_run` (`completed`, `conclusion=failure`) or `check_run` (`completed`, `conclusion=failure`) — rather than polling. This is a receive-and-respond process (a small serverless handler is the standard shape — e.g. a Lambda/Cloud Function behind GitHub's webhook, or a lightweight always-on service), **not** something that lives on a CI runner.
3. Calls the model (Anthropic API, per the course's own architecture diagram in Chapter 0 — "our small program builds a clear prompt → Anthropic API returns a structured judgment → our code chooses an action") with the observations from Section 2 assembled into context.
4. Writes its output back as a **PR/issue comment or a Check Run annotation** — this is also how it "asks a human": by posting a comment that names exactly what it needs (e.g. *"@reviewer — could you confirm whether this bank-detail... sorry, wrong domain — could you confirm whether commit abc123 was an intentional force-push?"*) and, per the course's Chapter 5 requirement, stating **how long the hold lasts, who is notified, and what happens if nobody responds** in that same comment.
5. Keeps its own **evidence receipt** (Chapter 4's requirement: "target question, candidate tool, possible answers and expected belief changes, historical source used, permission boundary, tool version, timestamp, actual result") — practically, this is a small structured log per incident, not necessarily anything GitHub-hosted itself.

**Requesting a rerun specifically:** since the agent cannot trigger `workflow_dispatch` or re-run a job itself, "ask the user to rerun the job" (part of your HOLD definition) is a **comment**, not a tool call — e.g. *"This looks like it could be `H_flaky_test` (posterior 41%) or `H_fault_revealing` (34%) with the current evidence. Could someone re-run this job? A pass with no code change would raise the flaky posterior; a repeat failure would raise fault-revealing."* That comment is itself the action; the human's subsequent click is outside the agent's authority, exactly as you specified.

---

## 4. What the agent cannot access, and must ask a human for

Stated explicitly, since you flagged this as important:

- **Secrets and credentials** — cannot verify whether a leaked/rotated/expired secret caused a failure; can only observe the *symptom* in logs (an auth error string) and must ask "did this secret rotate recently?"
- **Cloud provider state** — AWS/GCP/Azure console, Kubernetes cluster health, VM/network status. A CI job failing because a cloud dependency (a database, a queue, an internal service) was down is invisible to the agent beyond "the log shows a connection timeout to X" — it cannot check whether X was actually down. This is a real gap for `H_infra_provisioning_fault` beyond what the GitHub status page covers (Section 2) — GitHub's own status page tells you if *GitHub Actions* is degraded, not whether *your* infra is.
- **APM / observability tooling** (Datadog, Sentry, New Relic, PagerDuty, etc.) — unless explicitly connected as a separate integration, none of this is reachable; if the org uses one, it's a tool to add later, not assumed here.
- **Institutional/tacit knowledge** — "is this expected," "was this a planned migration," "is this test known-bad and already ticketed" — this is exactly the kind of context Chapter 5's dry run keeps returning to (the phone call to the supplier is *asking a human who has out-of-band knowledge*, not a technical check).
- **Authority to act** — even where the agent's belief is very high, per your ESCALATE condition #2 ("required action exceeds the agent's authority"), reverting a commit, merging a fix, or force-pushing are all outside a read-only GitHub App's permission set by construction — this isn't just a policy choice, the API scope enforces it.

---

## 5. The three end-states — ACT / HOLD / ESCALATE — mapped onto the course's own policy

Your three-way framing lines up almost exactly with Chapter 5's four-move policy (`Act`, `Ask`, `Abstain/hold`, `Escalate`), with one small collapse: you're folding the course's *Ask* (request more evidence) and *Abstain/hold* (decline to decide, no evidence being sought) into a single **HOLD**. That's a reasonable simplification for a diagnosis agent — "ask a human for information" and "ask a human to rerun the job" are both, in your framing, *the agent handing the next step to a person without committing to a diagnosis*. Worth keeping as one internal action with two receipt sub-types (`hold: ask` vs `hold: rerun-requested`) rather than two policy branches, so you don't lose the distinction Chapter 5 makes between "there is a specific, permitted, worthwhile check" (Ask) and "there is nothing left worth checking, but I still can't decide" (Abstain).

| Your state | Course's move | Fires when |
|---|---|---|
| **ACT** | *Act* | Posterior on a single hypothesis clears its test-treatment threshold (Pauker & Kassirer, file 1 Section 11) **and** the fix is within the agent's authority to merely *state* (never apply). Output: a specific, named fix — "revert commit X," "pin dependency Y to version Z," "this is `H_flaky_test` with posterior 82%; quarantine/skip and file a ticket," etc. |
| **HOLD** | *Ask* + *Abstain* | Either (a) a permitted, cheap observation still has positive expected value (myopic VoI > its cost — mostly the interruption cost of asking, per Section 6) and there's time before any deadline, → ask/request-rerun; or (b) no further permitted observation clears that bar, but no hypothesis has cleared its act threshold either → abstain, with the same "how long, who's notified, what happens on timeout" receipt Chapter 5 requires |
| **ESCALATE** | *Escalate* | Your three conditions map directly onto the course's own reasons: (1) "consequence of wrong autonomous decision too high" = Chapter 5's consequence-table override / Chow's ratio-driven threshold, and Parasuraman et al.'s automation-ceiling cap from file 1; (2) "required action exceeds agent's authority" = literally true by API scope (Section 4); (3) "uncertainty can't be reduced within budget" = the VoI stopping condition failing to converge before a time/cost budget — Chapter 5's own worked example ends this way ("the next-best check could save a few hundred rupees but costs delay past the noon deadline, so the agent stops asking") |

---

## 6. Costs per hidden state, for VoI — sourced where possible, flagged where estimated

Following the first research file's own conclusion (Section 13, technique 3): **use cost *ratios*, not fabricated absolute dollar figures, wherever real data doesn't exist** (Chow 1970; Pauker & Kassirer 1980). Below are the pieces that *do* have a real, sourced number, and the pieces that don't — with every unsourced number named as an assumption, not a fact, per your instruction.

### 6.1 — Costs with a real, checkable source

| Cost item | Sourced estimate | Source |
|---|---|---|
| Cost of one CI job-minute (Linux 2-core, GitHub-hosted) | **$0.006/min** as of the January 2026 repricing | GitHub's own Actions runner pricing page; corroborated by three independent 2026 pricing trackers |
| Cost of one CI job-minute (Windows / macOS) | **$0.010/min (Windows)**, **$0.062/min (macOS)** | Same source — macOS is ~10× Linux |
| Cost of asking a human one question (interruption/refocus cost, time only) | **~23 min 15 sec** to return to full engagement on the original task, per interruption | Mark, Gudith & Klocke, *"The Cost of Interrupted Work: More Speed and Stress,"* CHI 2008 (the original peer-reviewed source behind the widely-recycled "23-minute" figure — I traced it back past the blog re-quotes to the actual paper) |
| Fully-loaded engineer hourly cost, US, 2026 | Base pay **~$63/hr** (median), fully-loaded (benefits, payroll tax, overhead) typically **1.25×–1.4×** base | ERI (erieri.com) 2026 salary data for base pay; squadxp.com's 2026 hiring-cost guide for the fully-loaded multiplier. Combining these: **≈ $79–$88/hr fully loaded**, a range, not a point estimate — treat it as one per Hubbard's calibrated-interval method (already cited file 1) |
| Dollar cost of one "ask" interruption, derived | 23.25 min × ~$83/hr (midpoint of the range above) **≈ $32 per interruption** | Derived from the two rows above — this is a computed number, not an independently sourced one; the two inputs are sourced, the multiplication is mine |
| Change failure rate base rates (for calibrating how often `H_fault_revealing` should be true *before* any evidence, i.e. a sanity check on your prior, not a cost) | 2025 DORA: elite/top-tier ideal band **0–2%**, largest observed cluster **8–16%**, low performers **45–60%+** | Google Cloud's DORA *State of AI-Assisted Software Development* 2025 report (via multiple 2026 secondary summaries — I was not able to fetch the primary DORA report PDF directly, so treat this as sourced-but-secondhand, same caveat file 1 already carried) |

### 6.2 — Costs that do **not** have a real, transferable source (flagged, not invented)

- **Cost of a shipped regression in dollars.** I searched for this specifically. What exists is enterprise-wide *downtime* cost literature (Gartner's often-cited $5,600/min from 2014, Atlassian and ITIC's more recent $8,000–$14,000+/min figures, Splunk/Oxford Economics' Global 2000 studies) — but every one of these is measuring *total-system outage cost for a large enterprise*, not *the cost of one regression slipping through one CI check in one repository*. Using those numbers directly here would be exactly the mistake file 1 already warned against in its own Section 11 ("use DORA CFR only as a base-rate sanity check, not a cost figure"). **I am not going to manufacture a per-regression dollar figure from these — it would be a fabricated transfer, not a sourced one.** The honest path, per Chow (1970) and file 1 Section 13's technique 3, is: elicit the ratio directly from your own team/practitioners — *"how many false 'it's flaky' calls would you tolerate to avoid missing one real regression?"* — and let that ratio, not an invented dollar amount, set the act/hold threshold for `H_fault_revealing` specifically.
- **Cost of an unnecessary code fix / false ACT.** No literature I found prices this directly for a CI-diagnosis context specifically. A defensible proxy — **flagged as my estimate, not a citation** — is one engineer's review-and-revert cycle: roughly 15–45 minutes at the fully-loaded rate above, i.e. **~$20–$62**. Treat this as a placeholder to replace with real data once you have any (per Hubbard's calibrated-estimation method, again).
- **Cost of a false ESCALATE (unnecessary human handoff).** Compose it from sourced pieces: one interruption (~$32, Section 6.1) plus a review pass, conservatively 15–30 min at $83/hr → **roughly $50–$75 total.** This one *is* built from sourced inputs, but the composition itself is mine, not a study's.
- **Cost of failing to escalate a genuinely severe/irreversible issue** (e.g., silently treating a security-relevant regression as routine). This is the one place file 1 already got this right and I'd repeat it rather than "fix" it with a fake number: per Parasuraman, Sheridan & Wickens (2000) and the GPWS aircraft-warning example, this isn't a threshold you compute from a cost ratio at all — it's a **design-time authority cap**: certain hypotheses (security-relevant, data-loss-relevant, pipeline-blocking-for-everyone) are flagged in advance to never auto-ACT regardless of posterior, the same way GPWS is capped at "suggest, never auto-execute" independent of how confident it is. Don't try to price your way to this one.

### 6.3 — Cost of Agent 1's gate specifically (new, since you split it out)

Since Agent 1 now runs *before* Agent 2 and decides whether to hand off at all: the cost of Agent 1 wrongly calling something operator-error when it's real is the same as a false-negative on `H_fault_revealing` above (a shipped bug — priced by ratio, not dollars, per 6.2). The cost of Agent 1 wrongly handing a genuine trivial operator error off to Agent 2 is comparatively tiny — it's model-inference cost (cents, not dollars, and no human interruption, since Agent 2 is itself fully automated up until *it* decides to HOLD or ESCALATE). **This asymmetry is itself decision-relevant**: because over-triggering Agent 2 is cheap and under-triggering it is potentially expensive, Agent 1's gate threshold should be conservative — i.e., require strong, specific evidence (a clean force-push/amend signature from the Commits API, Section 2) before calling something operator-error, and default to Agent 2 otherwise. This isn't a sourced number, it's a structural argument from the cost asymmetry above, and I'm labeling it as such.

---

## 7. Where to find real test cases

You asked for meaningful test cases specifically, not invented ones — same standard file 1 already held itself to in Section 7 ("that your simulated test cases are comparable to real historical CI failures needs to be checked, not assumed").

**Real, checkable datasets that exist and are publicly accessible:**

| Source | What it actually contains | Use for |
|---|---|---|
| **IDoFT — International Dataset of Flaky Tests** (`github.com/TestingResearchIllinois/idoft`, Wing Lam, UIUC) | 2,000+ flaky tests detected in real-world Java/Maven open-source projects, 500+ with fixes, with links to the actual pull requests that fixed them | Ground truth for `H_flaky_test` / `H_timing_race`, and — because it links the fixing PR — you can pull the *actual diff, commit, and CI run* around each one directly from GitHub's API, which is exactly the observation surface from Section 2 |
| **FlakeFlagger dataset** (Alshammari et al., referenced via the Flakify paper, arXiv:2112.12331) | 22,236 test cases across 23 real GitHub projects, Java/Maven, with computed flakiness features | Larger-volume supplement to IDoFT for the same two hypotheses |

**Real cases you'd need to construct yourself (I did not find a ready-made public dataset for these, and I'm not going to claim one exists):**

- For `H_dependency_fault`, `H_config_error`, `H_container_image_fault`, `H_infra_provisioning_fault`, and the joint boxes — I could not find an equivalent public, pre-labeled dataset. The closest published work (Seo et al. 2014's 26.6M Google builds, Hassan et al.'s 91-failure taxonomy, the 2025 GitHub-Actions-failure taxonomy study across 260 Java projects, the Android build-issue study, Google's OSS-Fuzz 1.2M-build-log study — all already in file 1 Section 9) describe the *shape* of real failures (what fraction are dependency vs. config vs. environment) but, as far as I could verify, **do not publish the raw labeled logs/diffs themselves** for you to pull individual cases from. Treat those papers as telling you what proportions to sample toward, not as a data source to draw actual test cases from.
- The practical route: use the GitHub Actions API directly (Section 2's tools) against a handful of real, popular, active open-source repositories, pull recent **failed** workflow runs, and hand-label each using the same signal a real reviewer would: did the very next commit touching the same file/test fix it with a code change (→ real bug), or did a bare re-run with no code change pass (→ flaky), or does the log show a registry/network/image-pull error unrelated to the diff (→ infra/dependency)? This is manual, and it should be — the assignment's own Section 10 requirement (per file 1) is that you can justify the comparability of your test cases, and hand-verification is how you earn that, not a substitute for it.
- **Caution I'm carrying forward from file 1, because it still applies:** don't let automatic labeling heuristics (e.g., "rerun passed → flaky") stand in unverified. Haben et al.'s Chromium finding (already in file 1 Section 9) is specifically that a large share of flaky-history tests were *also*, at some point, genuinely fault-revealing — a single rerun result is evidence, not proof, exactly the belief-vs-certainty distinction Chapter 1 keeps insisting on.

---

## 8. Consolidated tools & information manifest, with rationale

This restates Section 2 as a single build-checklist, in priority order (cheapest/most-discriminating first, matching Chapter 4's "cheap, highly-informative evidence before expensive evidence" sequencing insight from file 1 Section 11):

1. **Commit metadata / force-push detection** — free, instant, the Stage-0 gate for Agent 1 (`H_human_operator_error`), checked before anything else runs.
2. **Workflow run + job status, and run *attempts*** — cheapest possible signal for whether this is even reproducible (attempt 1 fail / attempt 2 pass on identical code is the strongest single flaky-vs-real signal available without executing anything).
3. **GitHub status page** — free, external, one HTTP call, rules `H_infra_provisioning_fault` in or out at the platform level before you spend anything else.
4. **Diff / compare API** (code diff, dependency-manifest diff, CI-config diff) — the direct input to `H_fault_revealing`, `H_dependency_fault`, `H_config_error`.
5. **Job logs** — the expensive-to-parse but highest-information-content source; read last, after the cheaper structured signals above have already narrowed the board, so the log-reading (or model-reading) effort is spent where it matters.
6. **Historical run list for this workflow/branch/test** — the "tool ledger," needed to compute prior base rates and therefore needed before the evidence planner (Section 1) can rank anything at all.
7. **Artifacts (test reports), if present** — supplementary, not guaranteed to exist in every repo's workflow.
8. **The human** — reachable only through a posted comment/annotation, used only when Sections 1–7's expected value of one more observation drops below its cost (Section 6), consistent with Chapter 5's own stopping rule.

Everything **not** on this list — cloud consoles, secrets, APM tooling, execution of any kind — is out of scope by the constraint you gave, and is exactly the set of things that route to a human instead (Section 4).

---

## Open items worth resolving before you start building

- **Confirm or correct the 9-hypothesis table in Section 0.2** — I reconstructed it from your message and the prior file; I could be wrong about which two joint boxes you mean.
- **Decide the real cost ratios for Section 6.2's unsourced items** with your own team, per Chow's method — I've deliberately not invented numbers there.
- **Decide how much of Section 7's manual-labeling work you're doing vs. automating**, and if automating, build in the Haben-et-al caution (a rerun result alone is not ground truth) rather than trusting a single heuristic.
- **Decide whether Agent 1's gate gets its own tiny evidence-planner/expected-loss pass** (Section 6.3) or is a fixed rule ("force-push detected → operator error, full stop") — the former is more in the spirit of the course, the latter is simpler to build first and upgrade later.
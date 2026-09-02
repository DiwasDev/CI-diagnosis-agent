# Cost Matrix & Evidence Costs — CI Failure Diagnosis Agent

## Evidence Source Costs

| Evidence | Description | Time | Cost | Status | Calculation |
|----------|-------------|------|------|--------|-------------|
| E1 — Pipeline Step | Parse `failed_jobs[0].steps[0]` via GitHub REST API | 0 min | **$0.00** | REAL | GitHub API free tier; zero marginal cost |
| E2 — Changed Files | Query commit diff via GitHub REST API | 0 min | **$0.00** | REAL | GitHub API free tier; zero marginal cost |
| E3 — Rerun Outcome | Trigger identical CI re-run; observe pass/fail | 12 min | **$0.07** | REAL | 12 min × $0.006/min (GitHub Linux 2-core runner) |
| E4 — Local Repro | Developer checks out commit and runs locally | 20 min | **$33.33** | ASSUMED | 20 min × ($100 / 60) = $33.33 |

---

## Action Cost Matrix `C(action | true_state)`

### Row: Escalate

| State | Cost | Status | Reason & Calculation |
|-------|------|--------|---------------------|
| S1 | **$50.00** | ASSUMED | Human triage: 30 min × $100/hr = $50.00. Constant across all states because escalation always routes to a senior engineer for context-switching and diagnosis. |
| S2 | **$50.00** | ASSUMED | Same as S1. |
| S3 | **$50.00** | ASSUMED | Same as S1. |
| S4 | **$50.00** | ASSUMED | Same as S1. |
| S5 | **$50.00** | ASSUMED | Same as S1. |
| S6 | **$50.00** | ASSUMED | Same as S1. |
| S7 | **$50.00** | ASSUMED | Same as S1. |

### Row: Fix Dependency

| State | Cost | Status | Reason & Calculation |
|-------|------|--------|---------------------|
| S1 | **$75.07** | ASSUMED | Wrong action. Triggers misdiagnosis chain: wrong patch review (15 min = $25.00) + CI rerun ($0.07) + manual re-diagnosis (30 min = $50.00) = **$75.07**. |
| S2 | **$75.07** | ASSUMED | Wrong action. Same misdiagnosis chain as S1. Dependency change does not fix project config. |
| S3 | **$8.33** | ASSUMED | **Correct action.** Agent fix is automated ($0.00) + human verification 5 min × ($100 / 60) = **$8.33**. |
| S4 | **$75.07** | ASSUMED | Wrong action. Same misdiagnosis chain. Dependency change does not fix lint/static analysis issue. |
| S5 | **$75.07** | ASSUMED | Wrong action. Same misdiagnosis chain. Dependency change does not fix test failure. |
| S6 | **$75.07** | ASSUMED | Wrong action. Same misdiagnosis chain. Dependency change does not fix environment setup issue. |
| S7 | **$75.07** | ASSUMED | Wrong action. Same misdiagnosis chain. Dependency change does not fix transient/external failure. |

### Row: Fix Code (src / config / lint)

| State | Cost | Status | Reason & Calculation |
|-------|------|--------|---------------------|
| S1 | **$8.33** | ASSUMED | **Correct action.** 5-min spot-check × ($100 / 60) = **$8.33**. |
| S2 | **$8.33** | ASSUMED | **Correct action.** Project config (pyproject.toml, etc.) is within the "Fix Code" action scope per policy. Same automation cost as S1 |
| S3 | **$75.07** | ASSUMED | Wrong action. Same misdiagnosis chain. Code patch does not resolve dependency failure. |
| S4 | **$8.33** | ASSUMED | **Correct action.** Static analysis failure is resolved by lint/code patch. Same automation cost as S1. |
| S5 | **$75.07** | ASSUMED | Wrong action. Same misdiagnosis chain. Code patch does not fix broken test or fixture. |
| S6 | **$75.07** | ASSUMED | Wrong action. Same misdiagnosis chain. Code patch does not fix missing OS headers or wrong Python version. |
| S7 | **$75.07** | ASSUMED | Wrong action. Same misdiagnosis chain. Code patch does not fix network flakes, OOM, or rate limits. |

---

## Full Matrix (Summary View)

| Action \ True State | S1 Source | S2 Config | S3 Dependency | S4 Static | S5 Test | S6 Env | S7 Other |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Escalate** | $50.00 | $50.00 | $50.00 | $50.00 | $50.00 | $50.00 | $50.00 |
| **Fix Dependency** | $75.07 | $75.07 | **$8.33** | $75.07 | $75.07 | $75.07 | $75.07 |
| **Fix Code** | **$8.33** | **$8.33** | $75.07 | **$8.33** | $75.07 | $75.07 | $75.07 |




## Threshold Derivation

## Assumption Register

| # | Assumption | Status | Note |
|---|-----------|--------|------|
| 1 | Engineer loaded cost = $100/hr | ASSUMED | Mid-market benchmark between US ($150–250) and offshore ($25–45). |
| 2 | Wrong-patch cost = $75.07 | ASSUMED | From approved Case 1 model: review ($25) + CI ($0.07) + re-diagnosis ($50). |
| 3 | Correct code fix = $8.33 | ASSUMED | 5-min spot-check × ($100 / 60) = $8.33. |
| 4 | Correct dependency fix = $8.33 | ASSUMED | 5-min human verification × ($100 / 60) = $8.33. |
| 5 | E4 local repro = 20 min | ASSUMED | Clean Python env; Docker/microservice setups would be 45–60 min. |
| 6 | Escalation cost is constant | ASSUMED | Simplification. Real triage time may vary by state (e.g., S7 may take longer). |
| 7 | Single-step matrix | ASSUMED | Catastrophic tail risk ($10,000+ production leak) is excluded; assumes CI catches wrong patches before production. |
| 8 | S2 config fix ≈ S1/S4 code fix | ASSUMED | pyproject.toml edits are treated as equally automatable as lint fixes. |

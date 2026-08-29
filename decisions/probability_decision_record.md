# Probability Decision Record — CI Failure Diagnosis Agent

> **Problem statement:** The agent observes a failing GitHub Actions CI run. It must select the correct failure category because the true root cause is not known.

---

## 1. Hidden States & Priors

The priors are derived from Zheng et al. (2025), a study of 375 Java project CI failures. We merged near-duplicate categories (P3+P4, P5+P6) because our evidence sources cannot reliably distinguish them at the top level. The resulting 8 states and their empirical priors:

| # | Hidden State | Paper Code(s) | Count | Prior | Reasoning |
|---|-------------|---------------|-------|-------|-----------|
| 1 | Source Code Issues | P1 | 54 | **0.144** | Syntax/logic errors in application code. Empirical frequency from paper. |
| 2 | Project Config Issues | P2 | 19 | **0.051** | Bad `pyproject.toml`, missing README, incorrect build metadata. Empirical frequency. |
| 3 | Dependency Failures | P3 + P4 | 78 | **0.208** | Merged: unresolved packages + version conflicts. Combined count. |
| 4 | Static Analysis Failures | P5 + P6 | 41 | **0.109** | Merged: linting/coverage + security vulnerabilities. Combined count. |
| 5 | Test Failures | P8 | 120 | **0.320** | Assertion failures, fixture errors, integration test breaks. Most common. Empirical. |
| 6 | Workflow Config Issues | W2 | 21 | **0.056** | YAML syntax errors, missing secrets, bad `uses:` references. Empirical. |
| 7 | Environment Setup Issues | W4 | 13 | **0.035** | Missing system packages, wrong Python version, runner image issues. Empirical. |
| 8 | Other | Remaining | 29 | **0.077** | Resource limits, network flakes, API rate limits, permission issues, version control problems. Residual. |

**Assumption:** These priors are drawn from Java projects but generalized to Python CI. We assume the relative frequencies are comparable because the CI pipeline structure (install → build → test → lint) is language-agnostic.

**Prior entropy:**
```
H(S) = -[0.144*log2(0.144) + 0.051*log2(0.051) + 0.208*log2(0.208)
       + 0.109*log2(0.109) + 0.320*log2(0.320) + 0.056*log2(0.056)
       + 0.035*log2(0.035) + 0.077*log2(0.077)]
     = 2.6543 bits
```

---

## 2. Agent Actions

The agent selects an action based on the most probable hidden state after observing evidence:

| Action | Target States | When Applied |
|--------|----------------|--------------|
| **Fix the code** | Source Code Issues, Static Analysis Failures, Project Config Issues | Agent believes the fix is in code, config files, or lint rules. Agent generates a patch or suggests specific edits. |
| **Try to resolve** | Dependency Failures | Agent attempts to fix version pins, update lockfiles, or suggest compatible dependency versions. |
| **Escalate to human** | Test Failures, Workflow Config Issues, Environment Setup Issues, Other | These require human judgment: test logic may need domain knowledge, workflow changes need repo permissions, environment issues need infrastructure access, and "Other" is too vague to act on automatically. |

**Why this policy:**
- Code/config/static-analysis fixes are local and safe to attempt automatically.
- Dependency resolution is semi-automated (poetry/pip can suggest fixes) but may need human approval for version bumps.
- Test failures often require understanding the intended behavior — an agent shouldn't change test assertions without human review.
- Workflow, environment, and "Other" issues touch infrastructure the agent doesn't control.

---

## 3. Evidence Source E2 — Which Pipeline Step Failed First

### What the agent does
1. Fetch job metadata from GitHub API (or read webhook payload).
2. Parse `jobs.steps[]` array.
3. Find the first step with `conclusion == "failure"`.

### Cost
- Time: ~0.3 seconds
- API calls: 0–1 (free if using webhook payload)
- Money: ~$0
- Attention: Low
- Maintenance: None

### Outcomes
- **A** — Install step (`pip install`, `poetry install`, `conda`)
- **B** — Build/compile step (`python -m build`, import collection, `py_compile`)
- **C** — Test step (`pytest`, `unittest`)
- **D** — Static-analysis step (`flake8`, `black`, `mypy`, `bandit`, `pip-audit`)
- **E** — Workflow/environment step (checkout, `actions/setup-python`, system provisioning, YAML parse)
- **F** — Other / ambiguous (multi-phase failure, indeterminate)

### Likelihood Table with Assumption Rationale

| State | A | B | C | D | E | F |
|-------|---|---|---|---|---|---|
| Source Code Issues | 0.03 | **0.75** | 0.15 | 0.04 | 0.01 | 0.02 |
| Project Config Issues | 0.20 | **0.65** | 0.10 | 0.02 | 0.02 | 0.01 |
| Dependency Failures | **0.88** | 0.07 | 0.02 | 0.01 | 0.01 | 0.01 |
| Static Analysis Failures | 0.01 | 0.04 | 0.10 | **0.78** | 0.02 | 0.05 |
| Test Failures | 0.01 | 0.08 | **0.85** | 0.02 | 0.02 | 0.02 |
| Workflow Config Issues | 0.03 | 0.03 | 0.03 | 0.03 | **0.83** | 0.05 |
| Environment Setup Issues | 0.15 | 0.10 | 0.02 | 0.02 | **0.68** | 0.03 |
| Other | 0.18 | 0.12 | 0.20 | 0.08 | 0.25 | 0.17 |

#### Row-by-row assumption rationale

**Source Code Issues (P1):**
- **B = 0.75:** Syntax errors and import failures kill the build/collection phase before pytest executes. Assumed 0.75 (not 0.90) because some logic bugs survive import and fail in tests; (not 0.50) because syntax/import errors dominate over logic bugs in CI — developers catch many logic bugs locally before pushing.
- **C = 0.15:** Logic bugs that survive import but cause test failures. Assumed 0.15 (not 0.30) because developers run tests locally; (not 0.05) because some logic bugs are environment-dependent and slip through.
- **A = 0.03:** Rare case where a missing local package causes `pip install -e .` to fail. Not 0.00 to avoid claiming mathematical impossibility.
- **D = 0.04:** Some static analysis tools run during build and catch issues. Not 0.00 because type checkers may run at compile time.
- **E = 0.01:** Almost never a workflow issue for source code bugs. Kept at 0.01 as epsilon.
- **F = 0.02:** Ambiguous cases where multiple phases fail simultaneously.

**Project Config Issues (P2):**
- **B = 0.65:** Bad `pyproject.toml` or missing `README.md` explodes during `python -m build` or `pip install -e .` (build phase). Assumed 0.65 (not 0.80) because some config errors only surface during editable install (A=0.20); (not 0.40) because build is the primary failure point for config.
- **A = 0.20:** Editable install fails due to bad config metadata. Not 0.30 because most config errors are caught earlier in build.
- **C = 0.10:** Rarely reaches test phase if config is truly broken. Not 0.00 because some config errors are subtle (e.g., wrong package name that only breaks test imports).

**Dependency Failures (P3):**
- **A = 0.88:** The dependency resolver lives in the install step. Assumed 0.88 (not 1.0) because compiled extensions can fail during build after a "successful" install; (not 0.70) because 88% reflects the empirical strength from the paper data.
- **B = 0.07:** Compiled extensions (e.g., `numpy`) fail at import/compile time after install. Not 0.15 because most dependency issues are resolver-level, not compile-level.
- **C–F:** Near-zero because dependency issues rarely manifest in later phases.

**Static Analysis Failures (P4):**
- **D = 0.78:** Dedicated lint/security/coverage steps fail with tool exit codes. Assumed 0.78 (not 0.90) because tests may run in parallel and fail first (C=0.10); (not 0.60) because static analysis is usually its own distinct step.
- **C = 0.10:** Parallel test execution reports first. Not 0.20 because most CIs run lint before or after tests, not in parallel.
- **B = 0.04:** Some linters run during build. Not 0.00 because pre-commit hooks may run at build time.

**Test Failures (P5):**
- **C = 0.85:** Home state — tests fail in the test step. Assumed 0.85 (not 0.95) because collection errors (`conftest.py` crashes) structurally look like build failures (B=0.08); (not 0.70) because assertion failures are the canonical test failure mode.
- **B = 0.08:** Collection errors attributed to the test job. Not 0.15 because most test failures are genuine assertion mismatches, not collection issues.

**Workflow Config Issues (P6):**
- **E = 0.83:** YAML parse errors and invalid `uses:` references fail at workflow parse time or during "Set up job." Assumed 0.83 (not 0.95) because some workflow issues (missing secrets) only kill specific downstream steps; (not 0.70) because most workflow config issues are caught before user-defined steps run.
- **A–D = 0.03 each:** Missing secrets can kill a specific step. Set to 0.03 (not 0.00) to avoid exact zeros — a missing `PYPI_TOKEN` could make the publish step fail, which might be categorized as install/build/test/static depending on step naming.

**Environment Setup Issues (P7):**
- **E = 0.68:** Runner provisioning fails (wrong Python version, missing `gcc`). Assumed 0.68 (not 0.80) because missing system headers can make `pip install` fail with what looks like a dependency error (A=0.15); (not 0.50) because provisioning is the primary failure point.
- **A = 0.15:** The **critical confound** — missing `libpq-dev` or `gcc` makes `pip install` fail. The symptom looks like dependency failure but the cause is environment setup. Assumed 0.15 (not 0.25) because not all env issues manifest this way; (not 0.05) because this is a well-known and common pattern in Python CI.
- **B = 0.10:** Missing compiler kills C extension build. Not 0.20 because most env issues are caught at provisioning time, not build time.

**Other (P8):**
- Spread out by design. No dominant state. **E = 0.25** for GitHub platform issues (rate limits, bad action refs). **C = 0.20** for OOM during tests. **A = 0.18** for network flakes during install. Not concentrated because "Other" is a catch-all residual category containing multiple unrelated mechanisms.

### EIG Computation

**P(outcome) = sum over all states of [P(state) * P(outcome | state)]**

**Outcome A (Install):**
```
P(A) = 0.144*0.03 + 0.051*0.20 + 0.208*0.88 + 0.109*0.01
     + 0.320*0.01 + 0.056*0.03 + 0.035*0.15 + 0.077*0.18

     = 0.00432 + 0.01020 + 0.18304 + 0.00109
     + 0.00320 + 0.00168 + 0.00525 + 0.01386

     = 0.22264
```

**Posterior P(state | A):**
```
Source Code Issues:       0.00432 / 0.22264 = 0.0194
Project Config Issues:    0.01020 / 0.22264 = 0.0458
Dependency Failures:      0.18304 / 0.22264 = 0.8221
Static Analysis Failures: 0.00109 / 0.22264 = 0.0049
Test Failures:            0.00320 / 0.22264 = 0.0144
Workflow Config Issues:   0.00168 / 0.22264 = 0.0075
Environment Setup Issues: 0.00525 / 0.22264 = 0.0236
Other:                    0.01386 / 0.22264 = 0.0623
```

**H(S | A) = 1.102 bits** (entropy drop = 1.552 bits)

**Outcome B (Build):**
```
P(B) = 0.144*0.75 + 0.051*0.65 + 0.208*0.07 + 0.109*0.04
     + 0.320*0.08 + 0.056*0.03 + 0.035*0.10 + 0.077*0.12

     = 0.10800 + 0.03315 + 0.01456 + 0.00436
     + 0.02560 + 0.00168 + 0.00350 + 0.00924

     = 0.20009
```

**Posterior P(state | B):**
```
Source Code Issues:       0.10800 / 0.20009 = 0.5398
Project Config Issues:    0.03315 / 0.20009 = 0.1657
Dependency Failures:      0.01456 / 0.20009 = 0.0728
Static Analysis Failures: 0.00436 / 0.20009 = 0.0218
Test Failures:            0.02560 / 0.20009 = 0.1279
Workflow Config Issues:   0.00168 / 0.20009 = 0.0084
Environment Setup Issues: 0.00350 / 0.20009 = 0.0175
Other:                    0.00924 / 0.20009 = 0.0462
```

**H(S | B) = 2.050 bits** (entropy drop = 0.605 bits)

**Outcome C (Test):**
```
P(C) = 0.144*0.15 + 0.051*0.10 + 0.208*0.02 + 0.109*0.10
     + 0.320*0.85 + 0.056*0.03 + 0.035*0.02 + 0.077*0.20

     = 0.02160 + 0.00510 + 0.00416 + 0.01090
     + 0.27200 + 0.00168 + 0.00070 + 0.01540

     = 0.33154
```

**H(S | C) = 1.088 bits** (entropy drop = 1.566 bits)

**Outcome D (Static):**
```
P(D) = 0.144*0.04 + 0.051*0.02 + 0.208*0.01 + 0.109*0.78
     + 0.320*0.02 + 0.056*0.03 + 0.035*0.02 + 0.077*0.08

     = 0.00576 + 0.00102 + 0.00208 + 0.08502
     + 0.00640 + 0.00168 + 0.00070 + 0.00616

     = 0.10882
```

**H(S | D) = 1.290 bits** (entropy drop = 1.365 bits)

**Outcome E (Workflow/Env):**
```
P(E) = 0.144*0.01 + 0.051*0.02 + 0.208*0.01 + 0.109*0.02
     + 0.320*0.02 + 0.056*0.83 + 0.035*0.68 + 0.077*0.25

     = 0.00144 + 0.00102 + 0.00208 + 0.00218
     + 0.00640 + 0.04648 + 0.02380 + 0.01925

     = 0.10265
```

**H(S | E) = 2.093 bits** (entropy drop = 0.561 bits)

**Outcome F (Other):**
```
P(F) = 0.144*0.02 + 0.051*0.01 + 0.208*0.01 + 0.109*0.05
     + 0.320*0.02 + 0.056*0.05 + 0.035*0.03 + 0.077*0.17

     = 0.00288 + 0.00051 + 0.00208 + 0.00545
     + 0.00640 + 0.00280 + 0.00105 + 0.01309

     = 0.03426
```

**H(S | F) = 2.490 bits** (entropy drop = 0.165 bits)

**Full EIG for E2:**
```
H(S | E2) = 0.2226*1.102 + 0.2001*2.050 + 0.3315*1.088
          + 0.1088*1.290 + 0.1027*2.093 + 0.0343*2.490

          = 0.2453 + 0.4102 + 0.3607
          + 0.1404 + 0.2149 + 0.0854

          = 1.457 bits

EIG(E2) = H(S) - H(S | E2)
        = 2.654 - 1.457
        = 1.198 bits
```

**Failure mode:** Outcome A (install) conflates **P3 (Dependency)** with **P7 (Environment Setup)** — missing system headers masquerade as resolver errors. Outcome B (build) conflates **P1 (Source Code)** with **P2 (Project Config)** — both fail during build.

---

## 4. Evidence Source E3 — Error Class / Exit Code Signature

### What the agent does
1. Identify the failing step (same as E2).
2. Fetch the full stderr/stdout log for that step.
3. Classify the error text into one of 8 categories using regex/heuristics.

### Cost
- Time: ~1.5 seconds
- API calls: 1–2
- Money: ~$0 (regex) or ~$0.005 (LLM)
- Attention: Medium
- Maintenance: **Real** — regex patterns need updating when pip changes error formats or new tools emerge

### Outcomes
- **α** — Syntax / Import / Compile (`SyntaxError`, `NameError`, `ImportError`, C-extension compile failure)
- **β** — Config / Metadata (`FileNotFoundError` for `pyproject.toml`, `TomlDecodeError`, bad package metadata)
- **γ** — Dependency Resolver (`Could not find a version`, `ResolutionImpossible`, `No matching distribution found`)
- **δ** — Static Analysis (linter rule codes `E501`/`F401`, CVE IDs, coverage threshold messages)
- **ε** — Test Assertion (`AssertionError`, `assert x == y`, `FAILED tests/...`, fixture `SetupError`)
- **ζ** — System / Environment (`command not found: gcc`, `Killed` (exit 137/OOM), `No space left`, `Connection timed out`)
- **η** — Workflow / Platform (`Unexpected value`, `Input required and not supplied`, `Unable to resolve action`, YAML parse error)
- **θ** — Other / Ambiguous (generic non-zero exit, unrecognizable mashup, multi-error output)

### Likelihood Table with Assumption Rationale

| State | α | β | γ | δ | ε | ζ | η | θ |
|-------|---|---|---|---|---|---|---|---|
| Source Code Issues | **0.80** | 0.05 | 0.02 | 0.01 | 0.10 | 0.01 | 0.00 | 0.01 |
| Project Config Issues | 0.05 | **0.85** | 0.05 | 0.01 | 0.01 | 0.02 | 0.00 | 0.01 |
| Dependency Failures | 0.05 | 0.05 | **0.88** | 0.00 | 0.00 | 0.01 | 0.00 | 0.01 |
| Static Analysis Failures | 0.02 | 0.02 | 0.01 | **0.90** | 0.02 | 0.02 | 0.00 | 0.01 |
| Test Failures | 0.03 | 0.01 | 0.01 | 0.05 | **0.85** | 0.03 | 0.00 | 0.02 |
| Workflow Config Issues | 0.005 | 0.005 | 0.005 | 0.005 | 0.005 | 0.05 | **0.875** | 0.05 |
| Environment Setup Issues | 0.05 | 0.02 | 0.10 | 0.01 | 0.01 | **0.75** | 0.05 | 0.01 |
| Other | 0.05 | 0.05 | 0.10 | 0.05 | 0.15 | **0.35** | 0.15 | 0.10 |

#### Row-by-row assumption rationale

**Source Code Issues (P1):**
- **α = 0.80:** `SyntaxError`, `NameError`, `ImportError` pointing to `src/` dominate. Assumed 0.80 (not 0.90) because some logic bugs trigger test assertions instead (ε=0.10); (not 0.60) because syntax/import errors are the majority of CI-level code defects — developers catch logic bugs locally before pushing.
- **ε = 0.10:** Logic bugs that survive import and trigger `AssertionError` in tests. Not 0.20 because developers run tests locally; not 0.05 because some environment-dependent logic bugs slip through.
- **η = 0.00:** Workflow issues do not produce syntax errors. Assumed exactly 0.00 because these are disjoint error vocabularies — a YAML parse error never looks like a Python `SyntaxError`.

**Project Config Issues (P2):**
- **β = 0.85:** `TomlDecodeError`, `FileNotFoundError` on config files, `setup.py` metadata failures. Assumed 0.85 (not 0.95) because some config issues look like dependency errors when `pip install -e .` fails (γ=0.05); (not 0.70) because config errors have distinctive signatures that are easy to recognize.
- **γ = 0.05:** Bad config can cause `pip install` to fail with resolver-like symptoms. Not 0.15 because most config errors are caught before the resolver runs.

**Dependency Failures (P3):**
- **γ = 0.88:** Resolver-specific vocabulary (`ResolutionImpossible`, `No matching distribution found`) is unmistakable. Assumed 0.88 (not 1.0) because compiled extensions can fail with C-compiler errors during install (α=0.05); (not 0.70) because resolver errors have a very specific and consistent format across pip/poetry/conda.
- **δ = 0.00:** Dependency resolver does not emit linter rule codes or CVE IDs. Exact zero justified because these are completely disjoint error types — no pip error message contains `E501` or a CVE ID.
- **ε = 0.00:** Dependency resolution does not produce test assertions. Exact zero justified — the resolver runs before tests.

**Static Analysis Failures (P4):**
- **δ = 0.90:** Linter rule codes (`E501`, `F401`), CVE IDs (`CVE-2024-XXXX`), and coverage threshold messages (`Coverage failure: total of 45`) are unique signatures. Assumed 0.90 (not 1.0) because some static analysis failures are collection errors that look like test setup failures (ε=0.02); (not 0.80) because the signature is extremely distinctive.
- **ε = 0.02:** Test collection errors in `conftest.py` can be misattributed. Not 0.05 because most static analysis failures are genuine tool exits.

**Test Failures (P5):**
- **ε = 0.85:** `AssertionError`, `assert x == y`, `FAILED tests/...` are the canonical test failure signatures. Assumed 0.85 (not 0.95) because some test failures are fixture/setup errors (δ=0.05) or timeouts (ζ=0.03); (not 0.70) because assertion mismatch is the dominant test failure mode.
- **δ = 0.05:** Test collection errors or coverage threshold failures. Not 0.10 because these are less common than assertion failures.

**Workflow Config Issues (P6):**
- **η = 0.875:** YAML parse errors (`mapping values are not allowed`), `Unexpected value 'python-versionn'`, `Unable to resolve action` are unmistakably GitHub Actions vocabulary. Assumed 0.875 (not 0.95) because some workflow issues manifest as system errors (ζ=0.05, e.g., missing runner image); (not 0.80) because the vocabulary is extremely specific.
- **α–ε = 0.005 each:** Epsilon masses instead of exact zeros. We use 0.005 (not 0.00) to avoid claiming mathematical impossibility — a malformed workflow could inject bad shell code via `run:` that generates a `SyntaxError` in a generated file, or a missing secret could cause a downstream `AssertionError` in a test that depends on the secret. These are vanishingly rare but not logically impossible.
- **Why 0.005 specifically:** Small enough to not materially affect posteriors, large enough to prevent the agent from permanently zeroing out a state based on a single edge-case observation.

**Environment Setup Issues (P7):**
- **ζ = 0.75:** `command not found: gcc`, `Killed` (exit 137/OOM), `No space left on device`, runner-image version mismatches. Assumed 0.75 (not 0.90) because missing system headers can cause `pip install` to fail with resolver-like symptoms (γ=0.10); (not 0.60) because system-level errors dominate environment setup failures.
- **γ = 0.10:** The **same confound as E2** — missing `libpq-dev` or `gcc` makes `pip install` fail with `Could not find a version` or compile errors that look like dependency problems. Assumed 0.10 (not 0.20) because not all environment issues are missing headers; (not 0.05) because this is a well-documented and common pattern in Python CI (especially with `psycopg2` and `numpy`).
- **α = 0.05:** Missing compiler causes C-extension compile failure. Not 0.10 because most env issues are caught at provisioning time.

**Other (P8):**
- **ζ = 0.35:** Resource limits (OOM, disk full) produce system-level errors. Not 0.50 because "Other" also contains network flakes and platform issues.
- **η = 0.15:** GitHub platform issues (rate limits, API outages) produce workflow-like errors. Not 0.25 because these are a subset of "Other."
- **ε = 0.15:** Flaky tests that fail with assertions on retry. Not 0.25 because flaky tests are only one sub-category.
- **Spread design:** No single outcome dominates because "Other" is a catch-all containing multiple unrelated mechanisms.

### EIG Computation

**P(α) calculation:**
```
P(α) = 0.144*0.80 + 0.051*0.05 + 0.208*0.05 + 0.109*0.02
     + 0.320*0.03 + 0.056*0.005 + 0.035*0.05 + 0.077*0.05

     = 0.11520 + 0.00255 + 0.01040 + 0.00218
     + 0.00960 + 0.00028 + 0.00175 + 0.00385

     = 0.14581
```

**Posterior P(state | α):**
```
Source Code Issues:       0.11520 / 0.14581 = 0.7901
Project Config Issues:    0.00255 / 0.14581 = 0.0175
Dependency Failures:      0.01040 / 0.14581 = 0.0713
Static Analysis Failures: 0.00218 / 0.14581 = 0.0149
Test Failures:            0.00960 / 0.14581 = 0.0658
Workflow Config Issues:   0.00028 / 0.14581 = 0.0019
Environment Setup Issues: 0.00175 / 0.14581 = 0.0120
Other:                    0.00385 / 0.14581 = 0.0264
```

**H(S | α) = 1.224 bits** (drop = 1.431 bits)

**P(β) = 0.07116, H(S | β) = 1.856 bits** (drop = 0.799 bits)

**P(γ) calculation:**
```
P(γ) = 0.144*0.02 + 0.051*0.05 + 0.208*0.88 + 0.109*0.01
     + 0.320*0.01 + 0.056*0.005 + 0.035*0.10 + 0.077*0.10

     = 0.00288 + 0.00255 + 0.18304 + 0.00109
     + 0.00320 + 0.00028 + 0.00350 + 0.00770

     = 0.20424
```

**Posterior P(state | γ):**
```
Source Code Issues:       0.00288 / 0.20424 = 0.0141
Project Config Issues:    0.00255 / 0.20424 = 0.0125
Dependency Failures:      0.18304 / 0.20424 = 0.8962
Static Analysis Failures: 0.00109 / 0.20424 = 0.0053
Test Failures:            0.00320 / 0.20424 = 0.0157
Workflow Config Issues:   0.00028 / 0.20424 = 0.0014
Environment Setup Issues: 0.00350 / 0.20424 = 0.0171
Other:                    0.00770 / 0.20424 = 0.0377
```

**H(S | γ) = 0.734 bits** (drop = 1.921 bits)

**P(δ) = 0.12053, H(S | δ) = 0.942 bits** (drop = 1.713 bits)

**P(ε) calculation:**
```
P(ε) = 0.144*0.10 + 0.051*0.01 + 0.208*0.00 + 0.109*0.02
     + 0.320*0.85 + 0.056*0.005 + 0.035*0.01 + 0.077*0.15

     = 0.01440 + 0.00051 + 0.00000 + 0.00218
     + 0.27200 + 0.00028 + 0.00035 + 0.01155

     = 0.30127
```

**Posterior P(state | ε):**
```
Source Code Issues:       0.01440 / 0.30127 = 0.0478
Project Config Issues:    0.00051 / 0.30127 = 0.0017
Dependency Failures:      0.00000 / 0.30127 = 0.0000
Static Analysis Failures: 0.00218 / 0.30127 = 0.0072
Test Failures:            0.27200 / 0.30127 = 0.9028
Workflow Config Issues:   0.00028 / 0.30127 = 0.0009
Environment Setup Issues: 0.00035 / 0.30127 = 0.0012
Other:                    0.01155 / 0.30127 = 0.0383
```

**H(S | ε) = 0.611 bits** (drop = 2.043 bits)

**P(ζ) = 0.07232, H(S | ζ) = 2.129 bits** (drop = 0.526 bits)
**P(η) = 0.06230, H(S | η) = 0.868 bits** (drop = 1.786 bits)
**P(θ) = 0.02237, H(S | θ) = 2.425 bits** (drop = 0.229 bits)

**Full EIG for E3:**
```
H(S | E3) = 0.1458*1.224 + 0.0712*1.856 + 0.2042*0.734 + 0.1205*0.942
          + 0.3013*0.611 + 0.0723*2.129 + 0.0623*0.868 + 0.0224*2.425

          = 0.1785 + 0.1321 + 0.1499 + 0.1135
          + 0.1841 + 0.1539 + 0.0541 + 0.0543

          = 1.020 bits

EIG(E3) = 2.654 - 1.020 = 1.634 bits
```

**Failure mode:** γ (dependency resolver) leaks from **P7 (Environment Setup)** when missing `gcc`/`libpq-dev` causes pip to emit resolver-like errors. This is the same confound as E2's outcome A.

---

## 5. Evidence Source E4 — Git Diff Against Last Green Build

### What the agent does
1. Query GitHub API for the most recent successful run on the same branch.
2. Fetch the diff: `GET /repos/{owner}/{repo}/compare/{base}...{head}`.
3. Classify each changed file path into one of six buckets.
4. Emit the dominant category.

### Cost
- Time: ~0.5–1.0 seconds
- API calls: 2
- Money: ~$0
- Attention: Low
- Maintenance: Low (file path patterns are stable)

### Outcomes
- **src** — Application source code changed (`src/`, main package)
- **test** — Test files changed (`tests/`, `test_*.py`)
- **config** — Build/dependency config changed (`pyproject.toml`, `requirements.txt`, `poetry.lock`)
- **ci** — CI/environment config changed (`.github/workflows/`, `Dockerfile`, `.python-version`)
- **mixed** — Multiple categories changed
- **none** — Empty diff / no file changes (same commit retried, or no code changes)

### Likelihood Table with Assumption Rationale

| State | src | test | config | ci | mixed | none |
|-------|-----|------|--------|----|-------|------|
| Source Code Issues | **0.70** | 0.05 | 0.03 | 0.02 | 0.15 | 0.05 |
| Project Config Issues | 0.05 | 0.03 | **0.75** | 0.02 | 0.10 | 0.05 |
| Dependency Failures | 0.03 | 0.02 | **0.80** | 0.02 | 0.08 | 0.05 |
| Static Analysis Failures | **0.55** | 0.10 | 0.15 | 0.03 | 0.15 | 0.02 |
| Test Failures | 0.35 | **0.45** | 0.03 | 0.02 | 0.10 | 0.05 |
| Workflow Config Issues | 0.01 | 0.01 | 0.03 | **0.85** | 0.06 | 0.04 |
| Environment Setup Issues | 0.03 | 0.02 | 0.02 | **0.55** | 0.08 | 0.30 |
| Other | 0.12 | 0.08 | 0.08 | 0.10 | 0.15 | **0.47** |

#### Row-by-row assumption rationale

**Source Code Issues (P1):**
- **src = 0.70:** The buggy code changed. Assumed 0.70 (not 0.90) because sometimes tests expose existing bugs (test=0.05) or the bug is in mixed changes; (not 0.50) because most source code issues are introduced by the changed code itself.
- **mixed = 0.15:** `src/` + other files changed together. Not 0.30 because many PRs are focused on a single concern.
- **none = 0.05:** Retried same commit, real bug persists. Not 0.10 because most source code issues are introduced by new code.

**Project Config Issues (P2):**
- **config = 0.75:** `pyproject.toml`/`setup.py` changed. Assumed 0.75 (not 0.90) because some config issues are latent and only triggered by a new dependency version (none=0.05); (not 0.60) because config changes are the primary trigger for config failures.

**Dependency Failures (P3):**
- **config = 0.80:** `requirements.txt`/`poetry.lock` changed. Assumed 0.80 (not 0.90) because upstream packages can be yanked from PyPI without local changes (none=0.05); (not 0.70) because lockfile changes are the dominant trigger.

**Static Analysis Failures (P4):**
- **src = 0.55:** New code triggers lint/security rules. Assumed 0.55 (not 0.70) because lint config changes also trigger failures (config=0.15) and test code changes can be linted (test=0.10); (not 0.40) because new code is the most common trigger for lint failures.

**Test Failures (P5):**
- **test = 0.45:** Test logic changed. Assumed 0.45 (not 0.60) because code changes breaking existing tests are also common (src=0.35); (not 0.30) because test files are frequently modified in PRs.
- **src = 0.35:** Code change broke existing tests. Not 0.50 because test file changes are slightly more common than src changes for test failures.

**Workflow Config Issues (P6):**
- **ci = 0.85:** Workflow file changed. Assumed 0.85 (not 0.95) because secrets can expire without workflow changes (none=0.04); (not 0.75) because workflow file changes are the dominant trigger.

**Environment Setup Issues (P7):**
- **ci = 0.55:** `Dockerfile`/`.python-version` changed. Assumed 0.55 (not 0.70) because runner image updates happen upstream without local changes (none=0.30); (not 0.40) because local env config changes are still a significant trigger.
- **none = 0.30:** Runner image updated upstream, no local diff. This is high because environment setup issues are often caused by GitHub changing runner images, not by developer changes. Not 0.40 because some env issues are local Dockerfile changes; not 0.20 because upstream changes are a major cause of "it worked yesterday" failures.

**Other (P8):**
- **none = 0.47:** Flaky/resource/network failures have no code changes. Assumed 0.47 (not 0.60) because some "Other" failures coincide with unrelated file changes; (not 0.30) because the defining feature of flaky/resource/network failures is that they occur without code changes.

### EIG Computation

**P(src) = 0.2924, H(S | src) = 1.911 bits** (drop = 0.744 bits)
**P(test) = 0.1752, H(S | test) = 1.087 bits** (drop = 1.567 bits)
**P(config) = 0.2435, H(S | config) = 1.552 bits** (drop = 1.103 bits)
**P(ci) = 0.0923, H(S | ci) = 2.131 bits** (drop = 0.524 bits)
**P(mixed) = 0.1094, H(S | mixed) = 2.642 bits** (drop = 0.012 bits)
**P(none) = 0.0873, H(S | none) = 2.423 bits** (drop = 0.231 bits)

**Full EIG for E4:**
```
H(S | E4) = 0.2924*1.911 + 0.1752*1.087 + 0.2435*1.552
          + 0.0923*2.131 + 0.1094*2.642 + 0.0873*2.423

          = 0.5588 + 0.1904 + 0.3779
          + 0.1967 + 0.2890 + 0.2115

          = 1.824 bits

EIG(E4) = 2.654 - 1.824 = 0.830 bits
```

**Failure mode:** The **"mixed" outcome** (10.9% of the time) is nearly uninformative — entropy drops only 0.012 bits. When multiple file categories change, the diff says "something changed" without isolating the cause. The **"src" outcome** is muddy because src changes can break tests, trigger lint, or contain syntax errors — three states compete.

---

## 6. Cost Analysis

| Source | Time | API Calls | Money | Attention | Maintenance | Honest Cost |
|--------|------|-----------|-------|-----------|-------------|-------------|
| E2 | 0.3s | 0–1 | $0 | Low | None | **0.3 agent-seconds** |
| E4 | 0.5–1.0s | 2 | $0 | Low | Low | **0.5 agent-seconds** |
| E3 | 1.5s | 1–2 | $0 (regex) or $0.005 (LLM) | Medium | **Real** — pattern updates for new tool versions | **1.5 agent-seconds + ongoing maintenance** |

**Key insight:** Costs are not independent. E3's log fetch can reuse the failing step identified by E2. If E2 is run first, E3's marginal cost drops because the log is already located.

---

## 7. Cost-Adjusted Ranking

### Raw EIG ranking

| Rank | Source | EIG |
|------|--------|-----|
| 1 | E3 | 1.634 bits |
| 2 | E2 | 1.198 bits |
| 3 | E4 | 0.830 bits |

### Bits per agent-second (isolated costs)

| Source | EIG | Cost (s) | EIG/Cost |
|--------|-----|----------|----------|
| E2 | 1.198 | 0.3 | **3.99 bits/s** |
| E4 | 0.830 | 0.5 | **1.66 bits/s** |
| E3 | 1.634 | 1.5 | **1.09 bits/s** |

### Marginal cost when sequenced

If E2 is run first (identifies failing step), E3's log fetch is already done:

| Source | Marginal Cost | Marginal EIG/Cost |
|--------|--------------|-------------------|
| E2 | 0.3s | 3.99 bits/s |
| E3 (after E2) | **0.5s** (log cached) | **3.27 bits/s** |
| E4 | 0.5s | 1.66 bits/s |

---

## 8. Ordering Policy

**The rule: maximize EIG per marginal cost, accounting for shared infrastructure.**

1. **Run E2 first.** Cheapest per bit (3.99 bits/s). Tells you which phase died.
2. **If E2 is ambiguous** (outcome B = build step, or E = workflow/env step), **run E3 next.** The failing step's log is already identified — marginal cost drops to ~0.5s, efficiency jumps to 3.27 bits/s.
3. **If E3 leaves a tie**, run E4 as tie-breaker. Specifically:
   - E2=B (build) + E3=ε (assertion) + E4=src → diagnose **P1** (logic bug in src), not P5 → **Action: Fix the code**
   - E2=E (workflow/env) + E3=γ (resolver) + E4=ci → diagnose **P6** (workflow config), not P7 → **Action: Escalate**
   - E2=C (test) + E3=ε + E4=none → diagnose **P8 Other** (flaky test), not P5 → **Action: Escalate**
   - E2=A (install) + E3=γ + E4=config → diagnose **P3** (dependency) → **Action: Try to resolve**
   - E2=A (install) + E3=γ + E4=none → ambiguous P3 vs P7 → **Action: Escalate** (needs human to check if system headers are missing)

---

## 9. Limitations & Assumptions

1. **Priors from Java, applied to Python.** We assume CI failure frequencies are language-agnostic at the pipeline-structure level. This is unverified.

2. **Likelihoods are gut estimates, not empirical.** Every P(evidence | state) is a reasoned assumption backed by structural arguments (stage gating, error vocabulary), but the exact decimals are not measured from data.

3. **EIG is a planning-time average.** It does not tell you how reliably informative a check is — only how informative it is in expectation. E2 is bimodal: sometimes brilliant (A, C, D), sometimes muddy (B, E, F). EIG alone hides this variance.

4. **Manual likelihood lookups are error-prone.** At 8x8 table width, off-by-one column references are a real failure mode. An eventual simulator should automate this.

5. **Costs are approximate.** "Agent-seconds" is an arbitrary unit. Real deployment would need API quota costs, LLM token pricing, and human review time measured in dollars.

6. **E4's "mixed" outcome is nearly useless.** It occurs ~11% of the time and provides almost zero information (entropy drop = 0.012 bits). In a monorepo where every PR touches multiple categories, this outcome's probability rises and E4's value drops further.

7. **The P3 vs P7 confound is unresolved by any single evidence source.** Both E2-A and E3-γ conflate dependency failures with environment setup issues. Only the combination of E2 + E3 + E4 can partially resolve it, and even then, E4=none leaves ambiguity.

---

## 10. Audit Data

| Item | Value |
|------|-------|
| Time of record | 2026-08-23 |
| Data version | Zheng et al. 2025 (375 Java CI failures) |
| Model version | 8 hidden states, 3 evidence sources |
| Policy version | Sequential: E2 → E3 → E4 (conditional) |
| Prior entropy | 2.6543 bits |
| Best single EIG | E3 = 1.634 bits |
| Best EIG/cost | E2 = 3.99 bits/s |
| Assumed numbers | All likelihoods; all cost figures; Java→Python generalization |
| Action policy | Fix: P1, P2, P4; Resolve: P3; Escalate: P5, P6, P7, P8 |

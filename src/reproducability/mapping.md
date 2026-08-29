# Probability Decision Record v2 — Empirical Mapping from CI Repair Benchmark

    > **Date:** 2026-08-23
    > **Author:** Disambiguation pipeline (`src/disambiguate.py`)
    > **Polars version:** 1.43.2
    > **Status:** Final — approved after interactive 20-row validation checkpoint

    ---

    ## 1. Dataset

    | Property | Value |
    |---|---|
    | Source file | `data/ci_repair_bench.parquet` |
    | Rows | 567 |
    | Columns (original) | 21 |
    | Columns (enriched) | 23 (+`error_type_deduped`, +`primary_hidden_state`) |
    | Output file | `data/ci_repair_bench_disambiguated.parquet` |
    | Tool | Polars 1.43.2 — lazy scan + single-column materialisation |
    | Compression | zstd |

    ### Memory strategy

    `scan_parquet` defers all I/O and allocates no RAM until explicitly told to collect.
    Only the `error_type` column (a `List(String)` series) is materialised in RAM for
    the UDF pass. The two derived columns (`error_type_deduped`, `primary_hidden_state`)
    are computed as plain Python-level series, then joined back into one final collect
    before the write. The full 1 GB frame is never fully resident in RAM at the same time
    as the UDF output.

    ---

    ## 2. Assumptions

    1. **Tags are symptoms, not root causes.** The `error_type` column records what the
      CI log *reported*, not what *caused* the failure. A test that fails because a
      dependency is missing will surface both `Test Failure` and `Dependency Issues`.
      The true root cause is the dependency — the test failure is a downstream effect.

    2. **One row = one CI failure event.** Each row represents a single failing workflow
      run tied to one commit. The hidden state is therefore a property of the run, not
      of individual steps.

    3. **Hidden states are mutually exclusive.** The PDR models exactly one root-cause
      category per run. Multi-label tags must be collapsed to a single state.

    4. **Pipeline phase = causality.** CI pipelines execute in a fixed order:
      environment setup → dependency install → build/static analysis → test.
      A failure earlier in the chain causes all downstream steps to fail too.
      Therefore the tag corresponding to the earliest broken phase is the root cause;
      all later tags are consequences of it.

    5. **`error_type` covers all 12 unique tags exactly.** After inspecting the full
      dataset, every tag in the corpus appears in the mapping table below. No unmapped
      tags were found — no `Other` assignments arose from unknown tags.

    6. **`Configuration Error` → Project Config Issues (uniformly).** Inspection of all
      34 `Configuration Error` rows showed `workflow_filename` values such as
      `pre_commit.yml`, `run-tests.yml`, `framework.yml`. These are failures *within*
      the project's configuration (e.g., a bad pre-commit hook config, a malformed
      `pyproject.toml`) — not errors in the CI YAML authoring itself. The spec's
      alternative branch ("Workflow Config Issues if CI YAML file error") does not
      apply to any row in this dataset. All `Configuration Error` rows → **Project
      Config Issues**.

    7. **`Runtime Error` alone → Other (user decision, 2026-08-23).** Eight rows
      carry only `Runtime Error` with no co-occurring tags. The spec's conservative
      default was "Source Code Issues", but on inspection their failed steps include
      "Run tests", "Run Test", "Test tier two interpreter" — genuinely ambiguous
      between source code bugs and test infrastructure issues. The decision was made
      to assign these to **Other** rather than force a misleading label, acknowledging
      that these 8 rows (1.4% of the dataset) require manual review.

    ---

    ## 3. Tag-to-State Mapping

    Every unique string tag found in the `error_type` column maps to exactly one of
    the 8 hidden states. There are 12 unique tags; all 12 are covered.

    | Benchmark Tag | Hidden State | Rationale |
    |---|---|---|
    | `Environment Error` | Environment Setup Issues | Runner image, Python version, missing system package — all pre-code setup failures. |
    | `Configuration Error` | Project Config Issues | Bad `pyproject.toml`, `setup.cfg`, pre-commit config, build metadata. See §2 assumption 6 for the CI YAML edge case decision. |
    | `Package Installation Error` | Dependency Failures | `pip install` / `poetry install` failed — a package could not be resolved or fetched. |
    | `Dependency Issues` | Dependency Failures | Version conflicts, missing transitive deps — the package resolves but is incompatible. Merged with Package Installation Error into one state because the fix path is identical (update pins, regenerate lockfile). |
    | `Syntax Error` | Source Code Issues | Python parse-time failure in application code. Kills import collection; always a code bug. |
    | `Type Checking Error` | Static Analysis Failures | `mypy`/`pyright` found a type mismatch. Code runs but violates declared types. |
    | `Code Linting` | Static Analysis Failures | `flake8`/`ruff`/`pylint` style or complexity violation. No runtime impact. |
    | `Code Formatting` | Static Analysis Failures | `black`/`isort`/`docformatter` found formatting divergence. No runtime impact. |
    | `Documentation or Docstring Error` | Static Analysis Failures | Docstring format violation (`pydocstyle`, `darglint`). Treated as a static check. |
    | `Assertion Error` | Test Failures | A test assertion failed — the code ran but produced the wrong result. |
    | `Test Failure` | Test Failures | Generic test failure (fixture error, timeout, xfail flip). Downstream of correct setup. |
    | `Runtime Error` | *context-dependent* | See §5 — handled by co-occurrence fallback, not by this table directly. |

    ---

    ## 4. Disambiguation Precedence

    When a row carries multiple tags, exactly one wins. The rule is: **the tag
    corresponding to the earliest failing pipeline phase is the root cause.** All
    later tags are downstream symptoms caused by that root failure.

    Precedence order (position 1 = highest priority = earliest phase):

    ```
    1.  Environment Error              →  Environment Setup Issues
    2.  Configuration Error            →  Project Config Issues
    3.  Package Installation Error     →  Dependency Failures
    4.  Dependency Issues              →  Dependency Failures
    5.  Syntax Error                   →  Source Code Issues
    6.  Type Checking Error            →  Static Analysis Failures
    7.  Code Linting                   →  Static Analysis Failures
    8.  Code Formatting                →  Static Analysis Failures
    9.  Documentation or Docstring Error → Static Analysis Failures
        [Runtime Error — not in this list; see §5]
    10. Assertion Error                →  Test Failures
    11. Test Failure                   →  Test Failures
    ```

    **Algorithm:** scan the row's deduplicated tag set against this ordered list top
    to bottom. Return the state of the first tag that matches. `Runtime Error` is
    skipped entirely in this walk; if it is the only remaining unmatched tag after
    the walk, the co-occurrence rule (§5) fires.

    ### Why this ordering is correct

    - **Environment before Config:** A missing system library prevents pip from even
      starting. Config errors only manifest after the runner is healthy.
    - **Config before Dependency:** A broken `pyproject.toml` prevents the resolver
      from reading the dependency list at all.
    - **Dependency before Syntax:** A missing package causes `ImportError` at test
      collection time, which the linter may also flag — but the fix is the package,
      not the code.
    - **Syntax before Static Analysis:** A file that fails to parse cannot be linted.
      Linter errors on a file with syntax errors are secondary.
    - **Static Analysis before Test:** Linting and type-checking run before or
      alongside tests in most pipelines. A formatting check that prevents a test job
      from starting is the root cause.
    - **Assertion/Test last:** Tests only fail if everything upstream succeeded.

    ### Example resolutions from the corpus

    | Original tags | Deduplicated | Winner | State |
    |---|---|---|---|
    | `['Dependency Issues', 'Code Linting']` | `Code Linting, Dependency Issues` | Dependency Issues (pos 4 < pos 7) | Dependency Failures |
    | `['Syntax Error', 'Test Failure', 'Test Failure']` | `Syntax Error, Test Failure` | Syntax Error (pos 5 < pos 11) | Source Code Issues |
    | `['Code Formatting', 'Test Failure']` | `Code Formatting, Test Failure` | Code Formatting (pos 8 < pos 11) | Static Analysis Failures |
    | `['Code Formatting', 'Code Formatting']` | `Code Formatting` | Code Formatting (single, pos 8) | Static Analysis Failures |
    | `['Environment Error', 'Runtime Error', 'Test Failure']` | `Environment Error, Runtime Error, Test Failure` | Environment Error (pos 1) | Environment Setup Issues |

    ---

    ## 5. Runtime Error Resolution Logic

    `Runtime Error` is the only tag in the corpus that **cannot be resolved by
    pipeline phase alone.** A runtime error can be caused by:

    - A missing dependency (ImportError at runtime)
    - A syntax error in a dynamically imported module
    - A genuine test assertion that raises an exception
    - A flaky environment (OOM, network timeout)

    Because `Runtime Error` could map to 4+ different states depending on context,
    placing it at any fixed position in the precedence list would produce systematic
    misclassification.

    ### Resolution rules (co-occurrence fallback)

    This rule fires only when the precedence walk reaches the end without matching any
    other tag — meaning `Runtime Error` is the *only unresolved tag* left.

    | Co-occurring tags | Resolved state | Reasoning |
    |---|---|---|
    | `Dependency Issues` or `Package Installation Error` | Dependency Failures | The most common cause of runtime `ImportError` is a missing or wrong-version package. |
    | `Test Failure` or `Assertion Error` | Test Failures | The error was raised inside a test body — the test infrastructure is working, the code result is wrong. |
    | `Syntax Error` | Source Code Issues | A runtime syntax error means a dynamically-imported module has a parse bug. |
    | `Code Linting` or `Code Formatting` | Static Analysis Failures | Runtime error during a pre-commit or lint run — the tool itself crashed on malformed code. |
    | `Environment Error` | Environment Setup Issues | Runtime crash during environment provision (e.g., a setup script). |
    | `Configuration Error` | Project Config Issues | Runtime error during build/install driven by bad config. |
    | **Alone / no other tags** | **Other** | Genuinely ambiguous — 8 rows, 1.4% of the dataset. Assigned to `Other` rather than forcing a misleading label. These rows require manual inspection. |

    ### Why `Runtime Error` alone → `Other`, not `Source Code Issues`

    The spec's default was `Source Code Issues` (conservative). However, the 8
    lone-`Runtime Error` rows have failed steps like "Run tests", "Run Test", "Test
    tier two interpreter" — indicating the error occurred during test execution, not
    during import/build. Mapping them to `Source Code Issues` would overstate the
    frequency of code bugs and understate ambiguity. `Other` is the honest label
    until a human reviews the logs.

    ---

    ## 6. Validation Sample

    The following 20 rows were shown interactively before writing any output file.
    The mapping was approved on 2026-08-23.

    | id | Original error_type | Deduplicated | primary_hidden_state |
    |---|---|---|---|
    | 315 | `['Runtime Error', 'Assertion Error']` | `Assertion Error, Runtime Error` | Test Failures |
    | 574 | `['Syntax Error']` | `Syntax Error` | Source Code Issues |
    | 361 | `['Code Formatting']` | `Code Formatting` | Static Analysis Failures |
    | 326 | `['Configuration Error']` | `Configuration Error` | Project Config Issues |
    | 428 | `['Package Installation Error']` | `Package Installation Error` | Dependency Failures |
    | 181 | `['Dependency Issues', 'Code Linting']` | `Code Linting, Dependency Issues` | Dependency Failures |
    | 100 | `['Runtime Error']` | `Runtime Error` | Other |
    | 487 | `['Code Formatting', 'Code Linting']` | `Code Formatting, Code Linting` | Static Analysis Failures |
    | 530 | `['Environment Error', 'Runtime Error', 'Test Failure']` | `Environment Error, Runtime Error, Test Failure` | Environment Setup Issues |
    | 218 | `['Code Formatting']` | `Code Formatting` | Static Analysis Failures |
    | 447 | `['Package Installation Error', 'Runtime Error', 'Test Failure']` | `Package Installation Error, Runtime Error, Test Failure` | Dependency Failures |
    | 234 | `['Dependency Issues']` | `Dependency Issues` | Dependency Failures |
    | 224 | `['Test Failure', 'Code Formatting', 'Code Linting']` | `Code Formatting, Code Linting, Test Failure` | Static Analysis Failures |
    | 23 | `['Dependency Issues']` | `Dependency Issues` | Dependency Failures |
    | 532 | `['Test Failure']` | `Test Failure` | Test Failures |
    | 387 | `['Dependency Issues', 'Test Failure']` | `Dependency Issues, Test Failure` | Dependency Failures |
    | 120 | `['Dependency Issues']` | `Dependency Issues` | Dependency Failures |
    | 10 | `['Syntax Error', 'Code Linting']` | `Code Linting, Syntax Error` | Source Code Issues |
    | 156 | `['Dependency Issues', 'Code Linting']` | `Code Linting, Dependency Issues` | Dependency Failures |
    | 512 | `['Code Formatting', 'Dependency Issues', 'Code Linting']` | `Code Formatting, Code Linting, Dependency Issues` | Dependency Failures |

    **Approval note:** All 20 rows correctly reflect the precedence and co-occurrence
    rules. Notably:

    - id=315 (`Runtime Error` + `Assertion Error`): `Runtime Error` skipped in precedence
      walk; co-occurrence rule fires → `Assertion Error` present → **Test Failures**. Correct.
    - id=100 (`Runtime Error` alone): no co-occurring tags → **Other**. Correct per §5.
    - id=530 (`Environment Error` + `Runtime Error` + `Test Failure`): `Environment Error`
      wins at position 1 — both downstream tags are consequences. Correct.
    - id=10 (`Syntax Error` + `Code Linting`): Syntax Error at position 5 beats Code
      Linting at position 7 — linter ran on broken code. Correct.

    ---

    ## 7. Empirical Priors (Computed from Benchmark)

    Computed from all 567 rows of `data/ci_repair_bench_disambiguated.parquet`.

    | Hidden State | Count | Prior (proportion) |
    |---|---|---|
    | Static Analysis Failures | 236 | **0.4162** |
    | Dependency Failures | 177 | **0.3122** |
    | Test Failures | 66 | **0.1164** |
    | Project Config Issues | 33 | **0.0582** |
    | Environment Setup Issues | 32 | **0.0564** |
    | Source Code Issues | 15 | **0.0265** |
    | Other | 8 | **0.0141** |
    | Workflow Config Issues | 0 | **0.0000** |
    | **TOTAL** | **567** | **1.0000** |

    ```
    Prior entropy H(S) = 2.1100 bits
    ```

    ### What the priors mean and why they differ from literature

    **Static Analysis Failures dominates at 41.6%.** This dataset is drawn from Python
    open-source projects that heavily use pre-commit hooks (`black`, `flake8`, `ruff`,
    `isort`). A single formatting divergence fails the entire CI run and surfaces as a
    `Code Formatting` or `Code Linting` tag — even if the commit itself is substantively
    correct. This inflates Static Analysis relative to Java project benchmarks.

    **Dependency Failures at 31.2%** is the second-largest state. Python's packaging
    ecosystem (pip, poetry, conda) has well-known resolver fragility. Unpinned
    dependencies and frequent upstream releases cause frequent install failures in CI.

    **Test Failures at 11.6%** is notably lower than the Zheng et al. literature prior
    of 32.0%. Two factors explain this:
    1. Many apparent "test failures" in this benchmark are actually rooted in dependency
      or static analysis problems (precedence correctly assigns them to the earlier phase).
    2. This dataset skews toward projects with strong pre-commit enforcement, where most
      failures are caught at the lint/format stage before tests even run.

    **Source Code Issues at 2.6%** is very low. Python's dynamic nature means syntax
    errors are rare in mature projects — they are caught by editors and pre-commit
    hooks before a push reaches CI.

    **Workflow Config Issues at 0.0%** — no row in this dataset was tagged with a
    workflow-authoring error. This state exists in the model (it was in the original
    PDR with a 5.6% prior from Java projects) but is empirically absent here. It
    remains in the state space for generality; the agent should retain a small
    non-zero prior (e.g., 0.01) from the literature rather than hard-zeroing it,
    to avoid division-by-zero in Bayesian updates and to handle future runs from
    projects with more YAML authoring errors.

    ### Comparison to literature priors (Zheng et al. 2025, Java projects)

    | Hidden State | Literature prior | Benchmark prior | Delta |
    |---|---|---|---|
    | Source Code Issues | 0.144 | 0.0265 | −0.118 |
    | Project Config Issues | 0.051 | 0.0582 | +0.007 |
    | Dependency Failures | 0.208 | 0.3122 | +0.104 |
    | Static Analysis Failures | 0.109 | 0.4162 | +0.307 |
    | Test Failures | 0.320 | 0.1164 | −0.204 |
    | Workflow Config Issues | 0.056 | 0.0000 | −0.056 |
    | Environment Setup Issues | 0.035 | 0.0564 | +0.021 |
    | Other | 0.077 | 0.0141 | −0.063 |

    The deltas confirm that **the Java-derived literature priors are not appropriate for
    this Python dataset.** The agent's prior distribution should be updated to use the
    empirical benchmark priors above. The one exception is `Workflow Config Issues`:
    retain the literature prior of 0.056 rather than 0.0 for robustness.

    ### Recommended agent priors (post-update)

    | Hidden State | Recommended prior |
    |---|---|
    | Static Analysis Failures | 0.4162 |
    | Dependency Failures | 0.3122 |
    | Test Failures | 0.1164 |
    | Project Config Issues | 0.0582 |
    | Environment Setup Issues | 0.0564 |
    | Source Code Issues | 0.0265 |
    | Other | 0.0141 |
    | Workflow Config Issues | 0.0100 *(floor from literature)* |

    > Note: these sum to > 1.0 because of the Workflow Config floor. Normalise before
    > use: divide each by the sum (≈ 1.01) to get a valid probability distribution.

    ---

    ## 8. Reproducibility

    | Property | Value |
    |---|---|
    | Polars version | 1.43.2 |
    | Python version | 3.12.3 |
    | Script | `src/disambiguate.py` |
    | Run command | `python src/disambiguate.py` |
    | Validation seed | `seed=42` (20-row sample) |
    | Date of computation | 2026-08-23 |
    | Manual overrides | None — all assignments are fully deterministic from the rules above |
    | Approval | Interactive checkpoint passed (typed `yes` at prompt) |

    ### Exact disambiguation rules encoded in `src/disambiguate.py`

    ```python
    PRECEDENCE = [
        ("Environment Error",                STATE_ENV_SETUP),
        ("Configuration Error",              STATE_PROJECT_CFG),
        ("Package Installation Error",       STATE_DEPENDENCY),
        ("Dependency Issues",                STATE_DEPENDENCY),
        ("Syntax Error",                     STATE_SOURCE_CODE),
        ("Type Checking Error",              STATE_STATIC),
        ("Code Linting",                     STATE_STATIC),
        ("Code Formatting",                  STATE_STATIC),
        ("Documentation or Docstring Error", STATE_STATIC),
        ("Assertion Error",                  STATE_TEST),
        ("Test Failure",                     STATE_TEST),
        # Runtime Error handled by co-occurrence — not in this list
    ]

    def _resolve_runtime_error(tags):
        if tags & {"Dependency Issues", "Package Installation Error"}: return DEPENDENCY
        if tags & {"Test Failure", "Assertion Error"}:                 return TEST
        if "Syntax Error" in tags:                                     return SOURCE_CODE
        if tags & {"Code Linting", "Code Formatting"}:                 return STATIC
        if "Environment Error" in tags:                                return ENV_SETUP
        if "Configuration Error" in tags:                             return PROJECT_CFG
        return OTHER  # alone or ambiguous
    ```

    ### How to reproduce from scratch

    ```bash
    # From repo root
    python src/disambiguate.py
    # Type 'yes' at the interactive prompt
    # Output: data/ci_repair_bench_disambiguated.parquet
    ```

    ### What would change this record

    - New rows added to the benchmark → re-run the script; priors update automatically.
    - A `Runtime Error`-alone row whose logs are inspected and found to be a clear
      code bug → add a manual override in the script's `_disambiguate_element` function
      keyed on row `id`, and document it in this section under "Manual overrides".
    - A `Workflow Config Issues` row appears → the 0.0 count will update naturally.
    - Decision to split `Other` into sub-categories → requires a new tag-to-state
      mapping entry and a new PDR version.


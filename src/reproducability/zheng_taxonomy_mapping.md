# Zheng et al. Taxonomy → 7 Hidden States — Mapping Record

> **Purpose:** make the extraction of the seven hidden states of the CI-diagnosis
> agent from the failure taxonomy of Zheng et al. (2025) fully reproducible.
> **Date:** 2026-09-03
> **Companion records:** empirical tag→state mapping and priors in
> [`mapping.md`](mapping.md); encoding in [`disambiguate.py`](disambiguate.py).

---

## 1. Source

| Property | Value |
|---|---|
| Paper | L. Zheng, S. Li, X. Huang, J. Huang, B. Lin, J. Chen, J. Xuan, "Why Do GitHub Actions Workflows Fail? An Empirical Study," *ACM Trans. Softw. Eng. Methodol.*, 1(1), Article 1, 2025. doi:10.1145/3749371 |
| Dataset | 375 failed GitHub Actions workflow executions from 260 open-source **Java** projects |
| Method | Card-sorting of manually analyzed failure logs; taxonomy validated by a 151-developer survey |
| Taxonomy | **16 failure types**: P1–P8 (project-related, 315 cases) and W1–W8 (workflow-related, 60 cases) |

The paper's categories are shown in its Figure 3 (project-related) and Figure 4
(workflow-related); the counts below were read from those figures and
cross-checked against the in-text percentages.

## 2. The 16 failure types and their counts

### Project-related factors — 315 cases (84%)

| Group | Code | Failure type | Count |
|---|---|---|---:|
| Compilation Failures (151) | P1 | Project compilation fails due to issues in the source code | 54 |
| | P2 | Project compilation fails due to project configuration mistakes/issues | 19 |
| | P3 | Project compilation fails due to unresolved dependencies | 33 |
| | P4 | Project compilation fails due to dependency conflicts | 45 |
| Quality Issues (44) | P5 | Source code fails predefined quality checks (lint, style, docs, coverage) | 26 |
| | P6 | The project contains potential vulnerabilities | 15 |
| | P7 | Performance degradation is detected | 3 |
| Testing Failures (120) | P8 | Software tests fail (unit 102, integration 18) | 120 |

### Workflow-related factors — 60 cases (16%)

| Group | Code | Failure type | Count |
|---|---|---|---:|
| Environment/Configuration Issues (48) | W1 | Workflow builds fail due to resource limitations | 2 |
| | W2 | Workflow executions fail due to workflow configuration issues or incorrect instructions | 21 |
| | W3 | Workflow executions fail due to network connection issues | 10 |
| | W4 | Workflow environment setups fail due to dependency issues | 13 |
| | W5 | Accesses to third-party services fail due to permission issues | 2 |
| GitHub Issues (12) | W6 | The required actions cannot be resolved | 3 |
| | W7 | The GitHub API rate limit is exceeded in GHA workflows | 3 |
| | W8 | Workflows fail due to version control management issues | 6 |

**Arithmetic identity checks** (all hold):

- Project: 54+19+33+45 = 151 (compilation); 26+15+3 = 44 (quality); 151+44+120 = 315 ✓
- Workflow: 2+21+10+13+2 = 48 (env/config); 3+3+6 = 12 (GitHub); 48+12 = 60 ✓
- Total: 315+60 = 375 ✓

> **Note on reading Figure 4:** the "48" printed at the top of the figure is the
> total of the Environment/Configuration *group*, not the count of W1; W1's own
> count (2) is printed inside its box. The group sums above disambiguate this.

## 3. Collapse rules: 16 types → 7 hidden states

The agent's hidden states are **not** the paper's categories. Each hidden state is
a collapse of one or more of the 16 types, chosen so that every state implies a
distinct repair action (the state-to-action map of the decision policy):

| Hidden state | Zheng types collapsed | Rationale |
|---|---|---|
| **S1 Source Code Issues** | P1 | One-to-one: syntax/logic/import defects in application code. |
| **S2 Project Config Issues** | P2 | One-to-one: bad project-level configuration (build metadata, paths). |
| **S3 Dependency Failures** | P3 + P4 | Unresolved dependencies (P3) and dependency conflicts (P4) have the **same fix path** (update pins, regenerate lockfile); the distinction does not change the action. |
| **S4 Static Analysis Failures** | P5 + P6 | Quality-check rejections (P5) and vulnerability-scan rejections (P6) are both static tools refusing the code; both are fixed by changing the code/metadata, not the environment. |
| **S5 Test Failures** | P8 | One-to-one: assertion/fixture failures during test execution. |
| **S6 Environment Setup Issues** | W4 | Runner-infrastructure provisioning failures (missing OS packages, wrong toolchain versions — the paper's own example is a missing `gcc-10`). |
| **S7 Other** | P7, W1, W2, W3, W5, W6, W7, W8 | Residual: transient/external causes (performance gates, runner resource limits/OOM, workflow YAML authoring errors, network flakes, permission errors, unresolvable actions, API rate limits, version-control issues) that share no single automated fix. |

**Intermediate 8-state variant (historical).** The first state list kept W2 as
its own state, *Workflow Config Issues*. In the Python benchmark (Section 4) zero
rows mapped to it — every `Configuration Error` tag was project-level config, not
workflow-YAML authoring (see `mapping.md` §2, assumption 6) — so the final model
has seven states and W2 falls to the S7 residual.

**Resulting literature priors** (per 375 Java cases; used only as the pre-benchmark
starting point, then replaced by the empirical Python priors of `mapping.md` §7):

| Hidden state | Zheng types | Count | Literature prior |
|---|---|---:|---:|
| S1 Source Code Issues | P1 | 54 | 0.144 |
| S2 Project Config Issues | P2 | 19 | 0.051 |
| S3 Dependency Failures | P3+P4 | 78 | 0.208 |
| S4 Static Analysis Failures | P5+P6 | 41 | 0.109 |
| S5 Test Failures | P8 | 120 | 0.320 |
| S6 Environment Setup Issues | W4 | 13 | 0.035 |
| S7 Other | rest | 50 | 0.133 |
| *(8-state variant: Workflow Config Issues = W2 alone: 21 → 0.056; Other = 29 → 0.077)* | | | |
| **Total** | | **375** | **1.000** |

## 4. Second mapping: benchmark `error_type` tags → hidden states

The priors actually used by the agent are **not** the Java literature priors. They
are counted from a Python benchmark (`ci_repair_bench`, 567 cases), whose
multi-label `error_type` symptom tags are disambiguated to one hidden state per
case. The 12 unique tags map onto the same seven states:

| Benchmark tag | Hidden state |
|---|---|
| `Environment Error` | S6 Environment Setup Issues |
| `Configuration Error` | S2 Project Config Issues |
| `Package Installation Error` | S3 Dependency Failures |
| `Dependency Issues` | S3 Dependency Failures |
| `Syntax Error` | S1 Source Code Issues |
| `Type Checking Error` | S4 Static Analysis Failures |
| `Code Linting` | S4 Static Analysis Failures |
| `Code Formatting` | S4 Static Analysis Failures |
| `Documentation or Docstring Error` | S4 Static Analysis Failures |
| `Assertion Error` | S5 Test Failures |
| `Test Failure` | S5 Test Failures |
| `Runtime Error` | context-dependent (co-occurrence fallback); alone → S7 Other |

Multi-tag rows are resolved by **pipeline-phase precedence** (earliest failing
phase wins; later tags are downstream symptoms), with a co-occurrence fallback for
the ambiguous `Runtime Error` tag. The full rules, rationale, worked examples,
20-row validation sample, and the resulting empirical priors are in
[`mapping.md`](mapping.md); the deterministic encoding is `PRECEDENCE` and
`_resolve_runtime_error` in [`disambiguate.py`](disambiguate.py).

## 5. How to reproduce

```bash
# 1. Taxonomy → states (this file, Section 3): pure collapse of the counts in
#    Zheng et al. Figures 3-4. Verify the identity checks in Section 2.
#
# 2. Benchmark tags → states + empirical priors:
python src/reproducability/disambiguate.py        # interactive; type 'yes'
#    writes data/ci_repair_bench_disambiguated.parquet and prints the prior table
#
# 3. Verify the priors and E1/E2 likelihood tables regenerate exactly:
python src/reproducability/verify_decision_tables.py
```

**What would change this record:** a re-tagging of the benchmark's `error_type`
column, a new tag not in the Section 4 table (currently impossible — all 12 tags
are covered), or a decision to split a collapsed state (e.g., separate P6
vulnerability scans from P5 lint) would require updating both this mapping and
`mapping.md`, then re-running the pipeline above.

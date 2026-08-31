# Distribution Drift Analysis Report

This report checks for distribution shift between the baseline dataset and the newly generated simulated out-of-distribution (OOD) dataset just for the shake of experimentation.

- **Baseline Dataset:** `benchmark_cases_seed42.json` (500 cases)
- **OOD Dataset:** `benchmark_cases_ood.json` (500 cases)
- **Drift Alert Threshold:** JS Divergence $\ge 0.05$

---

## Priors & Marginal Outcomes Drift

| Name of Evidence | Outcome | JS Divergence | Is Drift Alert |
|---|---|---|---|
| Priors (Hidden States) | Overall State Distribution | 0.2148 | 🚨 YES |
| E1 (Pipeline Step) | Overall Outcome Distribution | 0.1545 | 🚨 YES |
| E1 (Pipeline Step) | Outcome: A_install | 0.0154 | ✅ NO |
| E1 (Pipeline Step) | Outcome: B_build | 0.0796 | 🚨 YES |
| E1 (Pipeline Step) | Outcome: C_test | 0.0252 | ✅ NO |
| E1 (Pipeline Step) | Outcome: D_static_analysis | 0.0455 | ✅ NO |
| E1 (Pipeline Step) | Outcome: E_workflow | 0.0190 | ✅ NO |
| E1 (Pipeline Step) | Outcome: F_other | 0.0002 | ✅ NO |
| E2 (Changed Files) | Overall Outcome Distribution | 0.2540 | 🚨 YES |
| E2 (Changed Files) | Outcome: src | 0.0461 | ✅ NO |
| E2 (Changed Files) | Outcome: test | 0.0037 | ✅ NO |
| E2 (Changed Files) | Outcome: config | 0.0331 | ✅ NO |
| E2 (Changed Files) | Outcome: ci | 0.0658 | 🚨 YES |
| E2 (Changed Files) | Outcome: doc | 0.0463 | ✅ NO |
| E2 (Changed Files) | Outcome: mixed | 0.0747 | 🚨 YES |
| E2 (Changed Files) | Outcome: none | 0.0312 | ✅ NO |
| E3 (Rerun Outcome) | Overall Outcome Distribution | 0.1023 | 🚨 YES |
| E3 (Rerun Outcome) | Outcome: pass_on_rerun | 0.1023 | 🚨 YES |
| E3 (Rerun Outcome) | Outcome: fail_on_rerun | 0.1023 | 🚨 YES |
| E4 (Local Repro) | Overall Outcome Distribution | 0.0071 | ✅ NO |
| E4 (Local Repro) | Outcome: reproducible_locally | 0.0071 | ✅ NO |
| E4 (Local Repro) | Outcome: not_reproducible_locally | 0.0071 | ✅ NO |

---

## Conditional Likelihood Shift per Hidden State

This section compares the conditional evidence distribution $P(\text{Evidence} \mid \text{Hidden State})$ between datasets to inspect shifts in likelihood functions.

| Name of Evidence | Hidden State | N (Baseline) | N (OOD) | JS Divergence | Is Drift Alert |
|---|---|---|---|---|---|
| E1 (Pipeline Step) | S1_source_code_issues | 12 | 130 | 0.1546 | 🚨 YES |
| E1 (Pipeline Step) | S2_project_config_issues | 29 | 90 | 0.4110 | 🚨 YES |
| E1 (Pipeline Step) | S3_dependency_failures | 160 | 68 | 0.2154 | 🚨 YES |
| E1 (Pipeline Step) | S4_static_analysis_failures | 198 | 53 | 0.0817 | 🚨 YES |
| E1 (Pipeline Step) | S5_test_failures | 58 | 73 | 0.1054 | 🚨 YES |
| E1 (Pipeline Step) | S6_environment_setup_issues | 38 | 59 | 0.3330 | 🚨 YES |
| E1 (Pipeline Step) | S7_other | 5 | 27 | 0.2715 | 🚨 YES |
| E2 (Changed Files) | S1_source_code_issues | 12 | 130 | 0.2630 | 🚨 YES |
| E2 (Changed Files) | S2_project_config_issues | 29 | 90 | 0.3388 | 🚨 YES |
| E2 (Changed Files) | S3_dependency_failures | 160 | 68 | 0.4607 | 🚨 YES |
| E2 (Changed Files) | S4_static_analysis_failures | 198 | 53 | 0.5161 | 🚨 YES |
| E2 (Changed Files) | S5_test_failures | 58 | 73 | 0.3771 | 🚨 YES |
| E2 (Changed Files) | S6_environment_setup_issues | 38 | 59 | 0.5100 | 🚨 YES |
| E2 (Changed Files) | S7_other | 5 | 27 | 0.3565 | 🚨 YES |
| E3 (Rerun Outcome) | S1_source_code_issues | 12 | 130 | 0.1542 | 🚨 YES |
| E3 (Rerun Outcome) | S2_project_config_issues | 29 | 90 | 0.2770 | 🚨 YES |
| E3 (Rerun Outcome) | S3_dependency_failures | 160 | 68 | 0.1649 | 🚨 YES |
| E3 (Rerun Outcome) | S4_static_analysis_failures | 198 | 53 | 0.3501 | 🚨 YES |
| E3 (Rerun Outcome) | S5_test_failures | 58 | 73 | 0.0370 | ✅ NO |
| E3 (Rerun Outcome) | S6_environment_setup_issues | 38 | 59 | 0.0963 | 🚨 YES |
| E3 (Rerun Outcome) | S7_other | 5 | 27 | 0.0086 | ✅ NO |
| E4 (Local Repro) | S1_source_code_issues | 12 | 130 | 0.2709 | 🚨 YES |
| E4 (Local Repro) | S2_project_config_issues | 29 | 90 | 0.1572 | 🚨 YES |
| E4 (Local Repro) | S3_dependency_failures | 160 | 68 | 0.0156 | ✅ NO |
| E4 (Local Repro) | S4_static_analysis_failures | 198 | 53 | 0.2242 | 🚨 YES |
| E4 (Local Repro) | S5_test_failures | 58 | 73 | 0.1573 | 🚨 YES |
| E4 (Local Repro) | S6_environment_setup_issues | 38 | 59 | 0.2045 | 🚨 YES |
| E4 (Local Repro) | S7_other | 5 | 27 | 0.3892 | 🚨 YES |
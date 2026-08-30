# P3 Failures Analysis

**Total Failures:** 245 / 500
**Failure Rate:** 49.0%

## Top 5 Most Expensive Failures

1. Case #10: Cost = $75.07
2. Case #29: Cost = $75.07
3. Case #45: Cost = $75.07
4. Case #48: Cost = $75.07
5. Case #49: Cost = $75.07

---


## Failure #1: Case #10

**True Hidden State:** S6_environment_setup_issues
**Predicted Action:** Fix Dependency
**Cost:** $75.07

### Dry Run Trace

**Step 1: Initialize Priors**
```
P(S4_static_analysis_failures) = 0.4162
P(S3_dependency_failures) = 0.3122
P(S5_test_failures) = 0.1164
P(S2_project_config_issues) = 0.0582
```

**Step 2: Apply Free Evidence (E1, E2)**
```
Observed E1 = C_test
Observed E2 = mixed

After E1, E2:
  P(S3_dependency_failures|E1,E2) = 0.5535
  P(S5_test_failures|E1,E2) = 0.1731
  P(S6_environment_setup_issues|E1,E2) = 0.0987
  P(S2_project_config_issues|E1,E2) = 0.0844
  Best Action: Fix Dependency, EC = $38.13
```

**Step 3: Evaluate E3 (Rerun Test, $0.07)**
```
```

**Step 4: Evaluate E4 (Local Repro, $33.33)**
```
Decision: SKIP (cost not justified)
```

**Step 5: Final Decision**
  Action Taken: Fix Dependency
  Actual Cost: $75.07
  ✗ Wrong (should have taken Escalate)


## Failure #2: Case #29

**True Hidden State:** S2_project_config_issues
**Predicted Action:** Fix Dependency
**Cost:** $75.07

### Dry Run Trace

**Step 1: Initialize Priors**
```
P(S4_static_analysis_failures) = 0.4162
P(S3_dependency_failures) = 0.3122
P(S5_test_failures) = 0.1164
P(S2_project_config_issues) = 0.0582
```

**Step 2: Apply Free Evidence (E1, E2)**
```
Observed E1 = C_test
Observed E2 = mixed

After E1, E2:
  P(S3_dependency_failures|E1,E2) = 0.5535
  P(S5_test_failures|E1,E2) = 0.1731
  P(S6_environment_setup_issues|E1,E2) = 0.0987
  P(S2_project_config_issues|E1,E2) = 0.0844
  Best Action: Fix Dependency, EC = $38.13
```

**Step 3: Evaluate E3 (Rerun Test, $0.07)**
```
```

**Step 4: Evaluate E4 (Local Repro, $33.33)**
```
Decision: SKIP (cost not justified)
```

**Step 5: Final Decision**
  Action Taken: Fix Dependency
  Actual Cost: $75.07
  ✗ Wrong (should have taken Fix Code)


## Failure #3: Case #45

**True Hidden State:** S3_dependency_failures
**Predicted Action:** Fix Code
**Cost:** $75.07

### Dry Run Trace

**Step 1: Initialize Priors**
```
P(S4_static_analysis_failures) = 0.4162
P(S3_dependency_failures) = 0.3122
P(S5_test_failures) = 0.1164
P(S2_project_config_issues) = 0.0582
```

**Step 2: Apply Free Evidence (E1, E2)**
```
Observed E1 = F_other
Observed E2 = mixed

After E1, E2:
  P(S4_static_analysis_failures|E1,E2) = 0.5768
  P(S5_test_failures|E1,E2) = 0.1488
  P(S3_dependency_failures|E1,E2) = 0.1149
  P(S2_project_config_issues|E1,E2) = 0.1002
  Best Action: Fix Code, EC = $28.82
```

**Step 3: Evaluate E3 (Rerun Test, $0.07)**
```
```

**Step 4: Evaluate E4 (Local Repro, $33.33)**
```
Decision: SKIP (cost not justified)
```

**Step 5: Final Decision**
  Action Taken: Fix Code
  Actual Cost: $75.07
  ✗ Wrong (should have taken Fix Dependency)


## Failure #4: Case #48

**True Hidden State:** S6_environment_setup_issues
**Predicted Action:** Fix Code
**Cost:** $75.07

### Dry Run Trace

**Step 1: Initialize Priors**
```
P(S4_static_analysis_failures) = 0.4162
P(S3_dependency_failures) = 0.3122
P(S5_test_failures) = 0.1164
P(S2_project_config_issues) = 0.0582
```

**Step 2: Apply Free Evidence (E1, E2)**
```
Observed E1 = F_other
Observed E2 = mixed

After E1, E2:
  P(S4_static_analysis_failures|E1,E2) = 0.5768
  P(S5_test_failures|E1,E2) = 0.1488
  P(S3_dependency_failures|E1,E2) = 0.1149
  P(S2_project_config_issues|E1,E2) = 0.1002
  Best Action: Fix Code, EC = $28.82
```

**Step 3: Evaluate E3 (Rerun Test, $0.07)**
```
```

**Step 4: Evaluate E4 (Local Repro, $33.33)**
```
Decision: SKIP (cost not justified)
```

**Step 5: Final Decision**
  Action Taken: Fix Code
  Actual Cost: $75.07
  ✗ Wrong (should have taken Escalate)


## Failure #5: Case #49

**True Hidden State:** S5_test_failures
**Predicted Action:** Fix Dependency
**Cost:** $75.07

### Dry Run Trace

**Step 1: Initialize Priors**
```
P(S4_static_analysis_failures) = 0.4162
P(S3_dependency_failures) = 0.3122
P(S5_test_failures) = 0.1164
P(S2_project_config_issues) = 0.0582
```

**Step 2: Apply Free Evidence (E1, E2)**
```
Observed E1 = C_test
Observed E2 = mixed

After E1, E2:
  P(S3_dependency_failures|E1,E2) = 0.5535
  P(S5_test_failures|E1,E2) = 0.1731
  P(S6_environment_setup_issues|E1,E2) = 0.0987
  P(S2_project_config_issues|E1,E2) = 0.0844
  Best Action: Fix Dependency, EC = $38.13
```

**Step 3: Evaluate E3 (Rerun Test, $0.07)**
```
```

**Step 4: Evaluate E4 (Local Repro, $33.33)**
```
Decision: SKIP (cost not justified)
```

**Step 5: Final Decision**
  Action Taken: Fix Dependency
  Actual Cost: $75.07
  ✗ Wrong (should have taken Escalate)

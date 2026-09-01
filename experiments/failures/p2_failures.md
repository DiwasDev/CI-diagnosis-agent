# P2 expected-cost threshold — failure analysis

**Total failures:** 5 of 500 cases (1.0% failure rate)

## Failure 1 — case 10

- **True state:** S6_environment_setup_issues
- **Predicted action:** Fix Dependency
- **Realised cost:** $75.07
- **Correct action was:** Escalate

### Dry-run trace

```
priors: S4 0.416, S3 0.312, S5 0.116
E1 = C_test (acquired) -> S3 0.417, S5 0.229, S6 0.116
E2 = mixed (acquired) -> S3 0.553, S5 0.173, S6 0.099
E3 = fail_on_rerun available but not acquired
E4 = not_reproducible_locally available but not acquired
final: Fix Dependency at expected cost $38.13 (realised $75.07)
```

## Failure 2 — case 45

- **True state:** S3_dependency_failures
- **Predicted action:** Fix Code
- **Realised cost:** $75.07
- **Correct action was:** Fix Dependency

### Dry-run trace

```
priors: S4 0.416, S3 0.312, S5 0.116
E1 = F_other (acquired) -> S4 0.660, S5 0.143, S2 0.066
E2 = mixed (acquired) -> S4 0.577, S5 0.149, S3 0.115
E3 = fail_on_rerun available but not acquired
E4 = not_reproducible_locally available but not acquired
final: Fix Code at expected cost $28.82 (realised $75.07)
```

## Failure 3 — case 48

- **True state:** S6_environment_setup_issues
- **Predicted action:** Fix Code
- **Realised cost:** $75.07
- **Correct action was:** Escalate

### Dry-run trace

```
priors: S4 0.416, S3 0.312, S5 0.116
E1 = F_other (acquired) -> S4 0.660, S5 0.143, S2 0.066
E2 = mixed (acquired) -> S4 0.577, S5 0.149, S3 0.115
E3 = pass_on_rerun available but not acquired
E4 = reproducible_locally available but not acquired
final: Fix Code at expected cost $28.82 (realised $75.07)
```

## Failure 4 — case 29

- **True state:** S2_project_config_issues
- **Predicted action:** Fix Dependency
- **Realised cost:** $75.07
- **Correct action was:** Fix Code

### Dry-run trace

```
priors: S4 0.416, S3 0.312, S5 0.116
E1 = C_test (acquired) -> S3 0.417, S5 0.229, S6 0.116
E2 = mixed (acquired) -> S3 0.553, S5 0.173, S6 0.099
E3 = fail_on_rerun available but not acquired
E4 = reproducible_locally available but not acquired
final: Fix Dependency at expected cost $38.13 (realised $75.07)
```

## Failure 5 — case 49

- **True state:** S5_test_failures
- **Predicted action:** Fix Dependency
- **Realised cost:** $75.07
- **Correct action was:** Escalate

### Dry-run trace

```
priors: S4 0.416, S3 0.312, S5 0.116
E1 = C_test (acquired) -> S3 0.417, S5 0.229, S6 0.116
E2 = mixed (acquired) -> S3 0.553, S5 0.173, S6 0.099
E3 = fail_on_rerun available but not acquired
E4 = not_reproducible_locally available but not acquired
final: Fix Dependency at expected cost $38.13 (realised $75.07)
```

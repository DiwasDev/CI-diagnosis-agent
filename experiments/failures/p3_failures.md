# P3 info-gain per dollar — failure analysis

**Total failures:** 5 of 500 cases (1.0% failure rate)

## Failure 1 — case 0

- **True state:** S3_dependency_failures
- **Predicted action:** Fix Code
- **Realised cost:** $75.07
- **Correct action was:** Fix Dependency

### Dry-run trace

```
priors: S4 0.416, S3 0.312, S5 0.116
E1 = D_static_analysis (acquired) -> S4 0.691, S3 0.262, S5 0.012
E2 = mixed (acquired) -> S4 0.533, S3 0.422, S2 0.015
E3 = fail_on_rerun (acquired) -> S4 0.569, S3 0.395, S2 0.016
E4 = reproducible_locally available but not acquired
final: Fix Code at expected cost $35.70 (realised $75.07)
```

## Failure 2 — case 10

- **True state:** S6_environment_setup_issues
- **Predicted action:** Fix Dependency
- **Realised cost:** $75.07
- **Correct action was:** Escalate

### Dry-run trace

```
priors: S4 0.416, S3 0.312, S5 0.116
E1 = C_test (acquired) -> S3 0.417, S5 0.229, S6 0.116
E2 = mixed (acquired) -> S3 0.553, S5 0.173, S6 0.099
E3 = fail_on_rerun (acquired) -> S3 0.595, S5 0.142, S2 0.101
E4 = not_reproducible_locally available but not acquired
final: Fix Dependency at expected cost $35.39 (realised $75.07)
```

## Failure 3 — case 18

- **True state:** S3_dependency_failures
- **Predicted action:** Fix Code
- **Realised cost:** $75.07
- **Correct action was:** Fix Dependency

### Dry-run trace

```
priors: S4 0.416, S3 0.312, S5 0.116
E1 = D_static_analysis (acquired) -> S4 0.691, S3 0.262, S5 0.012
E2 = mixed (acquired) -> S4 0.533, S3 0.422, S2 0.015
E3 = fail_on_rerun (acquired) -> S4 0.569, S3 0.395, S2 0.016
E4 = not_reproducible_locally available but not acquired
final: Fix Code at expected cost $35.70 (realised $75.07)
```

## Failure 4 — case 17

- **True state:** S3_dependency_failures
- **Predicted action:** Fix Code
- **Realised cost:** $75.07
- **Correct action was:** Fix Dependency

### Dry-run trace

```
priors: S4 0.416, S3 0.312, S5 0.116
E1 = D_static_analysis (acquired) -> S4 0.691, S3 0.262, S5 0.012
E2 = mixed (acquired) -> S4 0.533, S3 0.422, S2 0.015
E3 = fail_on_rerun (acquired) -> S4 0.569, S3 0.395, S2 0.016
E4 = not_reproducible_locally available but not acquired
final: Fix Code at expected cost $35.70 (realised $75.07)
```

## Failure 5 — case 29

- **True state:** S2_project_config_issues
- **Predicted action:** Fix Dependency
- **Realised cost:** $75.07
- **Correct action was:** Fix Code

### Dry-run trace

```
priors: S4 0.416, S3 0.312, S5 0.116
E1 = C_test (acquired) -> S3 0.417, S5 0.229, S6 0.116
E2 = mixed (acquired) -> S3 0.553, S5 0.173, S6 0.099
E3 = fail_on_rerun (acquired) -> S3 0.595, S5 0.142, S2 0.101
E4 = reproducible_locally available but not acquired
final: Fix Dependency at expected cost $35.39 (realised $75.07)
```

# P4 cost-based VoI — failure analysis

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
E3 = fail_on_rerun available but not acquired
E4 = not_reproducible_locally available but not acquired
final: Fix Dependency at expected cost $38.13 (realised $75.07)
```

## Failure 3 — case 17

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

## Failure 4 — case 18

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

## Failure 5 — case 23

- **True state:** S5_test_failures
- **Predicted action:** Fix Code
- **Realised cost:** $75.07
- **Correct action was:** Escalate

### Dry-run trace

```
priors: S4 0.416, S3 0.312, S5 0.116
E1 = E_workflow (acquired) -> S4 0.314, S5 0.197, S3 0.156
E2 = src (acquired) -> S4 0.514, S5 0.133, S6 0.100
E3 = fail_on_rerun (acquired) -> S4 0.579, S1 0.107, S5 0.101
E4 = not_reproducible_locally available but not acquired
final: Fix Code at expected cost $25.40 (realised $75.07)
```

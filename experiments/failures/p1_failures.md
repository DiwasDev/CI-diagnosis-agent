# P1 belief-only — failure analysis

**Total failures:** 192 of 500 cases (38.4% failure rate)

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
E3 = fail_on_rerun available but not acquired
E4 = reproducible_locally available but not acquired
final: Fix Code at expected cost $38.16 (realised $75.07)
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

## Failure 3 — case 11

- **True state:** S5_test_failures
- **Predicted action:** Fix Dependency
- **Realised cost:** $75.07
- **Correct action was:** Escalate

### Dry-run trace

```
priors: S4 0.416, S3 0.312, S5 0.116
E1 = C_test (acquired) -> S3 0.417, S5 0.229, S6 0.116
E2 = src (acquired) -> S3 0.329, S4 0.205, S5 0.197
E3 = pass_on_rerun available but not acquired
E4 = reproducible_locally available but not acquired
final: Escalate at expected cost $50.00 (realised $75.07)
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
E3 = fail_on_rerun available but not acquired
E4 = not_reproducible_locally available but not acquired
final: Fix Code at expected cost $38.16 (realised $75.07)
```

## Failure 5 — case 18

- **True state:** S3_dependency_failures
- **Predicted action:** Fix Code
- **Realised cost:** $75.07
- **Correct action was:** Fix Dependency

### Dry-run trace

```
priors: S4 0.416, S3 0.312, S5 0.116
E1 = D_static_analysis (acquired) -> S4 0.691, S3 0.262, S5 0.012
E2 = mixed (acquired) -> S4 0.533, S3 0.422, S2 0.015
E3 = fail_on_rerun available but not acquired
E4 = not_reproducible_locally available but not acquired
final: Fix Code at expected cost $38.16 (realised $75.07)
```

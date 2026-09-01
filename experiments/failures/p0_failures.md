# P0 majority baseline — failure analysis

**Total failures:** 5 of 500 cases (1.0% failure rate)

## Failure 1 — case 0

- **True state:** S3_dependency_failures
- **Predicted action:** Fix Code
- **Realised cost:** $75.07
- **Correct action was:** Fix Dependency

### Dry-run trace

```
priors: S4 0.416, S3 0.312, S5 0.116
E1 = D_static_analysis available but not acquired
E2 = mixed available but not acquired
E3 = fail_on_rerun available but not acquired
E4 = reproducible_locally available but not acquired
final: Fix Code at expected cost $41.64 (realised $75.07)
```

## Failure 2 — case 1

- **True state:** S3_dependency_failures
- **Predicted action:** Fix Code
- **Realised cost:** $75.07
- **Correct action was:** Fix Dependency

### Dry-run trace

```
priors: S4 0.416, S3 0.312, S5 0.116
E1 = A_install available but not acquired
E2 = mixed available but not acquired
E3 = fail_on_rerun available but not acquired
E4 = not_reproducible_locally available but not acquired
final: Fix Code at expected cost $41.64 (realised $75.07)
```

## Failure 3 — case 3

- **True state:** S3_dependency_failures
- **Predicted action:** Fix Code
- **Realised cost:** $75.07
- **Correct action was:** Fix Dependency

### Dry-run trace

```
priors: S4 0.416, S3 0.312, S5 0.116
E1 = C_test available but not acquired
E2 = mixed available but not acquired
E3 = fail_on_rerun available but not acquired
E4 = reproducible_locally available but not acquired
final: Fix Code at expected cost $41.64 (realised $75.07)
```

## Failure 4 — case 8

- **True state:** S3_dependency_failures
- **Predicted action:** Fix Code
- **Realised cost:** $75.07
- **Correct action was:** Fix Dependency

### Dry-run trace

```
priors: S4 0.416, S3 0.312, S5 0.116
E1 = C_test available but not acquired
E2 = src available but not acquired
E3 = fail_on_rerun available but not acquired
E4 = reproducible_locally available but not acquired
final: Fix Code at expected cost $41.64 (realised $75.07)
```

## Failure 5 — case 10

- **True state:** S6_environment_setup_issues
- **Predicted action:** Fix Code
- **Realised cost:** $75.07
- **Correct action was:** Escalate

### Dry-run trace

```
priors: S4 0.416, S3 0.312, S5 0.116
E1 = C_test available but not acquired
E2 = mixed available but not acquired
E3 = fail_on_rerun available but not acquired
E4 = not_reproducible_locally available but not acquired
final: Fix Code at expected cost $41.64 (realised $75.07)
```

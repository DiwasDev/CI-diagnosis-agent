# P4 failure analysis

Top 5 highest-cost failures.

## 1. Test case: hard_000068
- True state: S5
- Ground action: Escalate
- Predicted action: Fix Dependency
- Decision cost paid: $75.07
- Evidence observed: E1=C, E2=mixed

### Priors
```text
  S1: 0.026500
  S2: 0.058200
  S3: 0.312200
  S4: 0.416200
  S5: 0.116400
  S6: 0.056400
  S7: 0.014100
```

### Dry run / trace
- Evidence received: E1 = C
- Posterior calculation:
  prior -> posterior
  ```text
  S1: 0.026500
  S2: 0.058200
  S3: 0.312200
  S4: 0.416200
  S5: 0.116400
  S6: 0.056400
  S7: 0.014100
  ```
  ```text
  S1: 0.038071
  S2: 0.076536
  S3: 0.416867
  S4: 0.098566
  S5: 0.229238
  S6: 0.116417
  S7: 0.024306
  ```
- Evidence received: E2 = mixed
- Posterior calculation:
  prior -> posterior
  ```text
  S1: 0.038071
  S2: 0.076536
  S3: 0.416867
  S4: 0.098566
  S5: 0.229238
  S6: 0.116417
  S7: 0.024306
  ```
  ```text
  S1: 0.015896
  S2: 0.084354
  S3: 0.553489
  S4: 0.062592
  S5: 0.173070
  S6: 0.098692
  S7: 0.011908
  ```

### Final posterior
```text
  S1: 0.015896
  S2: 0.084354
  S3: 0.553489
  S4: 0.062592
  S5: 0.173070
  S6: 0.098692
  S7: 0.011908
```

### Expected cost of each action at the final posterior
```text
  Escalate: 50.000000
  Fix Dependency: 38.130153
  Fix Lint: 64.201929
```

### Final action: Fix Dependency

## 2. Test case: hard_000071
- True state: S5
- Ground action: Escalate
- Predicted action: Fix Dependency
- Decision cost paid: $75.07
- Evidence observed: E1=C, E2=mixed

### Priors
```text
  S1: 0.026500
  S2: 0.058200
  S3: 0.312200
  S4: 0.416200
  S5: 0.116400
  S6: 0.056400
  S7: 0.014100
```

### Dry run / trace
- Evidence received: E1 = C
- Posterior calculation:
  prior -> posterior
  ```text
  S1: 0.026500
  S2: 0.058200
  S3: 0.312200
  S4: 0.416200
  S5: 0.116400
  S6: 0.056400
  S7: 0.014100
  ```
  ```text
  S1: 0.038071
  S2: 0.076536
  S3: 0.416867
  S4: 0.098566
  S5: 0.229238
  S6: 0.116417
  S7: 0.024306
  ```
- Evidence received: E2 = mixed
- Posterior calculation:
  prior -> posterior
  ```text
  S1: 0.038071
  S2: 0.076536
  S3: 0.416867
  S4: 0.098566
  S5: 0.229238
  S6: 0.116417
  S7: 0.024306
  ```
  ```text
  S1: 0.015896
  S2: 0.084354
  S3: 0.553489
  S4: 0.062592
  S5: 0.173070
  S6: 0.098692
  S7: 0.011908
  ```

### Final posterior
```text
  S1: 0.015896
  S2: 0.084354
  S3: 0.553489
  S4: 0.062592
  S5: 0.173070
  S6: 0.098692
  S7: 0.011908
```

### Expected cost of each action at the final posterior
```text
  Escalate: 50.000000
  Fix Dependency: 38.130153
  Fix Lint: 64.201929
```

### Final action: Fix Dependency

## 3. Test case: hard_000153
- True state: S5
- Ground action: Escalate
- Predicted action: Fix Dependency
- Decision cost paid: $75.07
- Evidence observed: E1=C, E2=mixed

### Priors
```text
  S1: 0.026500
  S2: 0.058200
  S3: 0.312200
  S4: 0.416200
  S5: 0.116400
  S6: 0.056400
  S7: 0.014100
```

### Dry run / trace
- Evidence received: E1 = C
- Posterior calculation:
  prior -> posterior
  ```text
  S1: 0.026500
  S2: 0.058200
  S3: 0.312200
  S4: 0.416200
  S5: 0.116400
  S6: 0.056400
  S7: 0.014100
  ```
  ```text
  S1: 0.038071
  S2: 0.076536
  S3: 0.416867
  S4: 0.098566
  S5: 0.229238
  S6: 0.116417
  S7: 0.024306
  ```
- Evidence received: E2 = mixed
- Posterior calculation:
  prior -> posterior
  ```text
  S1: 0.038071
  S2: 0.076536
  S3: 0.416867
  S4: 0.098566
  S5: 0.229238
  S6: 0.116417
  S7: 0.024306
  ```
  ```text
  S1: 0.015896
  S2: 0.084354
  S3: 0.553489
  S4: 0.062592
  S5: 0.173070
  S6: 0.098692
  S7: 0.011908
  ```

### Final posterior
```text
  S1: 0.015896
  S2: 0.084354
  S3: 0.553489
  S4: 0.062592
  S5: 0.173070
  S6: 0.098692
  S7: 0.011908
```

### Expected cost of each action at the final posterior
```text
  Escalate: 50.000000
  Fix Dependency: 38.130153
  Fix Lint: 64.201929
```

### Final action: Fix Dependency

## 4. Test case: hard_000117
- True state: S5
- Ground action: Escalate
- Predicted action: Fix Dependency
- Decision cost paid: $75.07
- Evidence observed: E1=C, E2=mixed

### Priors
```text
  S1: 0.026500
  S2: 0.058200
  S3: 0.312200
  S4: 0.416200
  S5: 0.116400
  S6: 0.056400
  S7: 0.014100
```

### Dry run / trace
- Evidence received: E1 = C
- Posterior calculation:
  prior -> posterior
  ```text
  S1: 0.026500
  S2: 0.058200
  S3: 0.312200
  S4: 0.416200
  S5: 0.116400
  S6: 0.056400
  S7: 0.014100
  ```
  ```text
  S1: 0.038071
  S2: 0.076536
  S3: 0.416867
  S4: 0.098566
  S5: 0.229238
  S6: 0.116417
  S7: 0.024306
  ```
- Evidence received: E2 = mixed
- Posterior calculation:
  prior -> posterior
  ```text
  S1: 0.038071
  S2: 0.076536
  S3: 0.416867
  S4: 0.098566
  S5: 0.229238
  S6: 0.116417
  S7: 0.024306
  ```
  ```text
  S1: 0.015896
  S2: 0.084354
  S3: 0.553489
  S4: 0.062592
  S5: 0.173070
  S6: 0.098692
  S7: 0.011908
  ```

### Final posterior
```text
  S1: 0.015896
  S2: 0.084354
  S3: 0.553489
  S4: 0.062592
  S5: 0.173070
  S6: 0.098692
  S7: 0.011908
```

### Expected cost of each action at the final posterior
```text
  Escalate: 50.000000
  Fix Dependency: 38.130153
  Fix Lint: 64.201929
```

### Final action: Fix Dependency

## 5. Test case: hard_000147
- True state: S5
- Ground action: Escalate
- Predicted action: Fix Dependency
- Decision cost paid: $75.07
- Evidence observed: E1=C, E2=mixed

### Priors
```text
  S1: 0.026500
  S2: 0.058200
  S3: 0.312200
  S4: 0.416200
  S5: 0.116400
  S6: 0.056400
  S7: 0.014100
```

### Dry run / trace
- Evidence received: E1 = C
- Posterior calculation:
  prior -> posterior
  ```text
  S1: 0.026500
  S2: 0.058200
  S3: 0.312200
  S4: 0.416200
  S5: 0.116400
  S6: 0.056400
  S7: 0.014100
  ```
  ```text
  S1: 0.038071
  S2: 0.076536
  S3: 0.416867
  S4: 0.098566
  S5: 0.229238
  S6: 0.116417
  S7: 0.024306
  ```
- Evidence received: E2 = mixed
- Posterior calculation:
  prior -> posterior
  ```text
  S1: 0.038071
  S2: 0.076536
  S3: 0.416867
  S4: 0.098566
  S5: 0.229238
  S6: 0.116417
  S7: 0.024306
  ```
  ```text
  S1: 0.015896
  S2: 0.084354
  S3: 0.553489
  S4: 0.062592
  S5: 0.173070
  S6: 0.098692
  S7: 0.011908
  ```

### Final posterior
```text
  S1: 0.015896
  S2: 0.084354
  S3: 0.553489
  S4: 0.062592
  S5: 0.173070
  S6: 0.098692
  S7: 0.011908
```

### Expected cost of each action at the final posterior
```text
  Escalate: 50.000000
  Fix Dependency: 38.130153
  Fix Lint: 64.201929
```

### Final action: Fix Dependency


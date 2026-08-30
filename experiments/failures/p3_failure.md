# P3 failure analysis

Top 5 highest-cost failures.

## 1. Test case: easy_000001
- True state: S4
- Ground action: Fix Lint
- Predicted action: Fix Dependency
- Decision cost paid: $75.07
- Evidence observed: E1=A, E2=src, E3=pass_on_rerun

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
- Evidence received: E1 = A
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
  S1: 0.014377
  S2: 0.153099
  S3: 0.602781
  S4: 0.117643
  S5: 0.055323
  S6: 0.033813
  S7: 0.022965
  ```
- Evidence received: E2 = src
- Posterior calculation:
  prior -> posterior
  ```text
  S1: 0.014377
  S2: 0.153099
  S3: 0.602781
  S4: 0.117643
  S5: 0.055323
  S6: 0.033813
  S7: 0.022965
  ```
  ```text
  S1: 0.025082
  S2: 0.081612
  S3: 0.516944
  S4: 0.266349
  S5: 0.051715
  S6: 0.051766
  S7: 0.006532
  ```
- Entropy-based expected information gain check for E3
  IG = 0.080625
  score = IG / cost = 1.151780
  threshold = 0.050000
  policy rule: if score <= threshold -> stop gathering evidence
- Evidence received: E3 = pass_on_rerun
- Posterior calculation:
  prior -> posterior
  ```text
  S1: 0.025082
  S2: 0.081612
  S3: 0.516944
  S4: 0.266349
  S5: 0.051715
  S6: 0.051766
  S7: 0.006532
  ```
  ```text
  S1: 0.008974
  S2: 0.029199
  S3: 0.554863
  S4: 0.057177
  S5: 0.129519
  S6: 0.185210
  S7: 0.035057
  ```

### Final posterior
```text
  S1: 0.008974
  S2: 0.029199
  S3: 0.554863
  S4: 0.057177
  S5: 0.129519
  S6: 0.185210
  S7: 0.035057
```

### Expected cost of each action at the final posterior
```text
  Escalate: 50.000000
  Fix Dependency: 38.038456
  Fix Lint: 68.706287
```

### Final action: Fix Dependency

## 2. Test case: hard_000071
- True state: S5
- Ground action: Escalate
- Predicted action: Fix Dependency
- Decision cost paid: $75.07
- Evidence observed: E1=C, E2=mixed, E3=fail_on_rerun

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
- Entropy-based expected information gain check for E3
  IG = 0.090685
  score = IG / cost = 1.295502
  threshold = 0.050000
  policy rule: if score <= threshold -> stop gathering evidence
- Evidence received: E3 = fail_on_rerun
- Posterior calculation:
  prior -> posterior
  ```text
  S1: 0.015896
  S2: 0.084354
  S3: 0.553489
  S4: 0.062592
  S5: 0.173070
  S6: 0.098692
  S7: 0.011908
  ```
  ```text
  S1: 0.019085
  S2: 0.101280
  S3: 0.594596
  S4: 0.076733
  S5: 0.142177
  S6: 0.062366
  S7: 0.003762
  ```

### Final posterior
```text
  S1: 0.019085
  S2: 0.101280
  S3: 0.594596
  S4: 0.076733
  S5: 0.142177
  S6: 0.062366
  S7: 0.003762
```

### Expected cost of each action at the final posterior
```text
  Escalate: 50.000000
  Fix Dependency: 35.386649
  Fix Lint: 61.915615
```

### Final action: Fix Dependency

## 3. Test case: hard_000068
- True state: S5
- Ground action: Escalate
- Predicted action: Fix Dependency
- Decision cost paid: $75.07
- Evidence observed: E1=C, E2=mixed, E3=fail_on_rerun

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
- Entropy-based expected information gain check for E3
  IG = 0.090685
  score = IG / cost = 1.295502
  threshold = 0.050000
  policy rule: if score <= threshold -> stop gathering evidence
- Evidence received: E3 = fail_on_rerun
- Posterior calculation:
  prior -> posterior
  ```text
  S1: 0.015896
  S2: 0.084354
  S3: 0.553489
  S4: 0.062592
  S5: 0.173070
  S6: 0.098692
  S7: 0.011908
  ```
  ```text
  S1: 0.019085
  S2: 0.101280
  S3: 0.594596
  S4: 0.076733
  S5: 0.142177
  S6: 0.062366
  S7: 0.003762
  ```

### Final posterior
```text
  S1: 0.019085
  S2: 0.101280
  S3: 0.594596
  S4: 0.076733
  S5: 0.142177
  S6: 0.062366
  S7: 0.003762
```

### Expected cost of each action at the final posterior
```text
  Escalate: 50.000000
  Fix Dependency: 35.386649
  Fix Lint: 61.915615
```

### Final action: Fix Dependency

## 4. Test case: hard_000117
- True state: S5
- Ground action: Escalate
- Predicted action: Fix Dependency
- Decision cost paid: $75.07
- Evidence observed: E1=C, E2=mixed, E3=fail_on_rerun

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
- Entropy-based expected information gain check for E3
  IG = 0.090685
  score = IG / cost = 1.295502
  threshold = 0.050000
  policy rule: if score <= threshold -> stop gathering evidence
- Evidence received: E3 = fail_on_rerun
- Posterior calculation:
  prior -> posterior
  ```text
  S1: 0.015896
  S2: 0.084354
  S3: 0.553489
  S4: 0.062592
  S5: 0.173070
  S6: 0.098692
  S7: 0.011908
  ```
  ```text
  S1: 0.019085
  S2: 0.101280
  S3: 0.594596
  S4: 0.076733
  S5: 0.142177
  S6: 0.062366
  S7: 0.003762
  ```

### Final posterior
```text
  S1: 0.019085
  S2: 0.101280
  S3: 0.594596
  S4: 0.076733
  S5: 0.142177
  S6: 0.062366
  S7: 0.003762
```

### Expected cost of each action at the final posterior
```text
  Escalate: 50.000000
  Fix Dependency: 35.386649
  Fix Lint: 61.915615
```

### Final action: Fix Dependency

## 5. Test case: hard_000147
- True state: S5
- Ground action: Escalate
- Predicted action: Fix Dependency
- Decision cost paid: $75.07
- Evidence observed: E1=C, E2=mixed, E3=fail_on_rerun

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
- Entropy-based expected information gain check for E3
  IG = 0.090685
  score = IG / cost = 1.295502
  threshold = 0.050000
  policy rule: if score <= threshold -> stop gathering evidence
- Evidence received: E3 = fail_on_rerun
- Posterior calculation:
  prior -> posterior
  ```text
  S1: 0.015896
  S2: 0.084354
  S3: 0.553489
  S4: 0.062592
  S5: 0.173070
  S6: 0.098692
  S7: 0.011908
  ```
  ```text
  S1: 0.019085
  S2: 0.101280
  S3: 0.594596
  S4: 0.076733
  S5: 0.142177
  S6: 0.062366
  S7: 0.003762
  ```

### Final posterior
```text
  S1: 0.019085
  S2: 0.101280
  S3: 0.594596
  S4: 0.076733
  S5: 0.142177
  S6: 0.062366
  S7: 0.003762
```

### Expected cost of each action at the final posterior
```text
  Escalate: 50.000000
  Fix Dependency: 35.386649
  Fix Lint: 61.915615
```

### Final action: Fix Dependency


# P1 failure analysis

Top 5 highest-cost failures.

## 1. Test case: easy_000001
- True state: S4
- Ground action: Fix Lint
- Predicted action: Fix Dependency
- Decision cost paid: $75.07
- Evidence observed: E1=A, E2=src

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

### Final posterior
```text
  S1: 0.025082
  S2: 0.081612
  S3: 0.516944
  S4: 0.266349
  S5: 0.051715
  S6: 0.051766
  S7: 0.006532
```

### Expected cost of each action at the final posterior
```text
  Escalate: 50.000000
  Fix Dependency: 40.569179
  Fix Lint: 50.173085
```

### Final action: Fix Dependency

## 2. Test case: easy_000002
- True state: S1
- Ground action: Escalate
- Predicted action: Fix Dependency
- Decision cost paid: $75.07
- Evidence observed: E1=C, E2=src

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
- Evidence received: E2 = src
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
  S1: 0.061085
  S2: 0.037522
  S3: 0.328797
  S4: 0.205237
  S5: 0.197081
  S6: 0.163919
  S7: 0.006359
  ```

### Final posterior
```text
  S1: 0.061085
  S2: 0.037522
  S3: 0.328797
  S4: 0.205237
  S5: 0.197081
  S6: 0.163919
  S7: 0.006359
```

### Expected cost of each action at the final posterior
```text
  Escalate: 50.000000
  Fix Dependency: 53.126090
  Fix Lint: 54.791398
```

### Final action: Fix Dependency

## 3. Test case: easy_000006
- True state: S6
- Ground action: Escalate
- Predicted action: Fix Lint
- Decision cost paid: $75.07
- Evidence observed: E1=E, E2=ci

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
- Evidence received: E1 = E
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
  S1: 0.076715
  S2: 0.136096
  S3: 0.155694
  S4: 0.313870
  S5: 0.196800
  S6: 0.090211
  S7: 0.030614
  ```
- Evidence received: E2 = ci
- Posterior calculation:
  prior -> posterior
  ```text
  S1: 0.076715
  S2: 0.136096
  S3: 0.155694
  S4: 0.313870
  S5: 0.196800
  S6: 0.090211
  S7: 0.030614
  ```
  ```text
  S1: 0.206243
  S2: 0.201036
  S3: 0.100274
  S4: 0.076036
  S5: 0.159306
  S6: 0.136455
  S7: 0.120650
  ```

### Final posterior
```text
  S1: 0.206243
  S2: 0.201036
  S3: 0.100274
  S4: 0.076036
  S5: 0.159306
  S6: 0.136455
  S7: 0.120650
```

### Expected cost of each action at the final posterior
```text
  Escalate: 50.000000
  Fix Dependency: 68.377725
  Fix Lint: 42.813553
```

### Final action: Fix Lint

## 4. Test case: easy_000007
- True state: S6
- Ground action: Escalate
- Predicted action: Fix Lint
- Decision cost paid: $75.07
- Evidence observed: E1=E, E2=ci

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
- Evidence received: E1 = E
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
  S1: 0.076715
  S2: 0.136096
  S3: 0.155694
  S4: 0.313870
  S5: 0.196800
  S6: 0.090211
  S7: 0.030614
  ```
- Evidence received: E2 = ci
- Posterior calculation:
  prior -> posterior
  ```text
  S1: 0.076715
  S2: 0.136096
  S3: 0.155694
  S4: 0.313870
  S5: 0.196800
  S6: 0.090211
  S7: 0.030614
  ```
  ```text
  S1: 0.206243
  S2: 0.201036
  S3: 0.100274
  S4: 0.076036
  S5: 0.159306
  S6: 0.136455
  S7: 0.120650
  ```

### Final posterior
```text
  S1: 0.206243
  S2: 0.201036
  S3: 0.100274
  S4: 0.076036
  S5: 0.159306
  S6: 0.136455
  S7: 0.120650
```

### Expected cost of each action at the final posterior
```text
  Escalate: 50.000000
  Fix Dependency: 68.377725
  Fix Lint: 42.813553
```

### Final action: Fix Lint

## 5. Test case: easy_000011
- True state: S1
- Ground action: Escalate
- Predicted action: Fix Dependency
- Decision cost paid: $75.07
- Evidence observed: E1=C, E2=src

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
- Evidence received: E2 = src
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
  S1: 0.061085
  S2: 0.037522
  S3: 0.328797
  S4: 0.205237
  S5: 0.197081
  S6: 0.163919
  S7: 0.006359
  ```

### Final posterior
```text
  S1: 0.061085
  S2: 0.037522
  S3: 0.328797
  S4: 0.205237
  S5: 0.197081
  S6: 0.163919
  S7: 0.006359
```

### Expected cost of each action at the final posterior
```text
  Escalate: 50.000000
  Fix Dependency: 53.126090
  Fix Lint: 54.791398
```

### Final action: Fix Dependency


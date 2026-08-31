# In-Depth Failure Analysis: CI Failure Diagnosis Agent (Week 2)

This document presents a comprehensive, decision-theoretic failure analysis of the CI Failure Diagnosis Agent, following the guidelines set out in the Week 2 Project Brief (Section 19). 

We compare the performance of five decision policies on a dataset of 500 simulated CI failures, identify the top 5 failure cases for the best-performing policy (**P4 — Cost-based Value of Information**), answer the 10 diagnostic questions for each failure, classify them, and propose concrete, actionable steps to improve the system.

---

## 1. Overall Policy Performance & Failure Statistics

The table below summarizes the performance of each policy across 500 test cases. All decision costs, information costs, and penalties are based on the cost model defined in [`decisions/costs.md`](file:///home/divas/ml/CI-diagnosis-agent/decisions/costs.md).

| Policy | Accuracy | Failures | Failure Rate | Info Cost | Decision Cost | Total Cost | Cost / Case | Escalation Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **P0 (Baseline)** | 47.8% | 261 | 52.2% | $0.00 | $21,584.14 | $21,584.14 | $43.17 | 0.0% |
| **P1 (Belief-only)** | 61.6% | 192 | 38.4% | $0.00 | $17,786.73 | $17,786.73 | $35.57 | 7.4% |
| **P2 (Threshold)** | 51.0% | 245 | 49.0% | $0.00 | $18,863.35 | $18,863.35 | $37.73 | 44.6% |
| **P3 (IG / $ Heuristic)** | 60.4% | 198 | 39.6% | $35.00 | $17,931.37 | $17,966.37 | $35.93 | 33.4% |
| **P4 (Cost-based VoI)** | **63.0%** | **185** | **37.0%** | **$11.83** | **$17,492.66** | **$17,504.49** | **$35.01** | **17.2%** |

### Key Policy Observations:
- **P4 (Cost-based Value of Information)** is the clear winner, achieving the **highest accuracy (63.0%)** and the **lowest total cost ($35.01 per case)**.
- **P1 (Belief-only)** is highly accurate but cost-blind, making expensive wrong actions because it does not acquire clarifying evidence.
- **P2 (Threshold)** is overly conservative, escalating 44.6% of cases to developers, which drives up human labor costs to $50 per escalation.
- **P3 (Information Gain Heuristic)** is wasteful, always acquiring E3 (rerun test, $0.07) in 100% of cases, even when the resulting information cannot change the final decision. P4 only buys E3 in **33.8% of cases**, saving substantial information costs.

---

## 2. Analysis of the Top 5 Failures under P4

The most expensive failures under P4 all cost **$75.07**, which represents the wrong-action penalty (a misdiagnosis that leads to a wrong automated fix, requiring code review, a rerun, and eventual manual diagnosis). We study the top 5 failures in detail below.

### Failure #1: Case #0 (S3 Dependency Failure Misdiagnosed as S4 Static Analysis)
- **True Hidden State:** `S3_dependency_failures`
- **Predicted Action:** `Fix Code` (designed for `S1`, `S2`, `S4`)
- **Actual Cost:** $75.07 (Wrong Action)
- **Dry-Run Trace:**
  - *Step 1 (Priors):* $P(S4) = 0.4162$, $P(S3) = 0.3122$, $P(S5) = 0.1164$, $P(S2) = 0.0582$.
  - *Step 2 (Free Evidence):* Observed $E1 = \text{D\_static\_analysis}$, $E2 = \text{mixed}$. Posteriors: $P(S4|E1,E2) = 0.5328$, $P(S3|E1,E2) = 0.4223$. Best action: `Fix Code` (Expected Cost = $38.16).
  - *Step 3 (E3 VoI Evaluation):* E3 (rerun test) has positive VoI ($3.02). Acquired E3. Observed: `fail_on_rerun`. Updated posteriors: $P(S4|E1,E2,E3) = 0.5688$, $P(S3|E1,E2,E3) = 0.3951$. Best Action remains `Fix Code` (EC = $35.70).
  - *Step 4 (E4 VoI Evaluation):* E4 (local repro, cost=$33.33) has negative VoI ($-22.87$). Skipped E4.
  - *Step 5 (Final Decision):* Executed `Fix Code`.

#### 10-Question Diagnostic Analysis:
1. **What did the agent believe?** The agent believed that a static analysis failure (`S4`) was the most likely cause (56.88%), followed by a dependency failure (`S3`) at 39.51%.
2. **What was actually true?** The root cause was a dependency failure (`S3`).
3. **Which evidence did it use?** $E1 = \text{D\_static\_analysis}$, $E2 = \text{mixed}$, and $E3 = \text{fail\_on\_rerun}$.
4. **Which evidence did it ignore or never obtain?** $E4 = \text{local\_repro}$ (skipped because the $33.33 cost was too high).
5. **Was the probability wrong?** Yes. The observation of $E1 = \text{D\_static\_analysis}$ skewed the probability toward `S4`, even though dependency issues can cause static tools to crash (e.g. `mypy` failing to import a missing library).
6. **Was the hidden-state list incomplete?** No, `S3` and `S4` are both modelled.
7. **Was the threshold wrong?** The stop rule was correct relative to the cost model. Since expected cost of action ($35.70) was lower than escalation ($50.00) and further evidence was too expensive, acting was the rational choice under the model.
8. **Was the cost model wrong?** Possibility
9. **Should it have asked for more information?** Yes, running $E4$ (local repro) would have resolved the ambiguity, but at $33.33 it was economically unviable. We need a cheaper version of $E4$.
10. **Should a human have been involved?** Yes. Since the true state was `S3` and the agent chose `Fix Code`, escalating to a human (cost $50.00) would have saved $25.07.

- **Failure Classification:** `Misleading evidence` (dependency failure manifested in the static analysis step, causing misleading $E1$ signal) combined with `Insufficient information` (could not afford $E4$ local check).

---

### Failure #2: Case #10 (S6 Env Issue Misdiagnosed as S3 Dependency)
- **True Hidden State:** `S6_environment_setup_issues`
- **Predicted Action:** `Fix Dependency` (designed for `S3`)
- **Actual Cost:** $75.07 (Wrong Action)
- **Dry-Run Trace:**
  - *Step 1 (Priors):* $P(S4) = 0.4162$, $P(S3) = 0.3122$, $P(S5) = 0.1164$, $P(S2) = 0.0582$.
  - *Step 2 (Free Evidence):* Observed $E1 = \text{C\_test}$, $E2 = \text{mixed}$. Posteriors: $P(S3|E1,E2) = 0.5535$, $P(S5|E1,E2) = 0.1731$, $P(S6|E1,E2) = 0.0987$. Best Action: `Fix Dependency` (EC = $38.13).
  - *Step 3 (E3 VoI Evaluation):* E3 has negative VoI. Skipped E3.
  - *Step 4 (E4 VoI Evaluation):* E4 has negative VoI. Skipped E4.
  - *Step 5 (Final Decision):* Executed `Fix Dependency`.

#### 10-Question Diagnostic Analysis:
1. **What did the agent believe?** The agent believed S3 (Dependency Failure) was the most likely state (55.35%). It assigned S6 only 9.87% probability.
2. **What was actually true?** The environment setup failed (S6) (e.g. runner was missing a system header `gcc` or had the wrong Python version).
3. **Which evidence did it use?** $E1 = \text{C\_test}$ and $E2 = \text{mixed}$.
4. **Which evidence did it ignore or never obtain?** $E3 = \text{rerun}$ and $E4 = \text{local\_repro}$ (both skipped because their VoI was negative).
5. **Was the probability wrong?** Yes. A system-level compiler/header error during test execution caused the pytest step to fail ($E1 = \text{C\_test}$), which the agent misattributed to library dependency errors.
6. **Was the hidden-state list incomplete?** No, S6 is modelled.
7. **Was the threshold wrong?** The agent chose to run the automated fix because the expected cost of `Fix Dependency` ($38.13) was lower than escalation ($50.00).
8. **Was the cost model wrong?** Maybe
9. **Should it have asked for more information?** Yes. However, E3 rerun outcome would also fail, which would not help distinguish S3 from S6. Only E4 (local repro) or log parsing could distinguish them.
10. **Should a human have been involved?** Yes. Environment setup issues (`S6`) have no automated fix, so escalation is the only correct action.

- **Failure Classification:** `Misleading evidence` (S6 environment setup issue crashed the pytest step, mirroring an S3 dependency or S5 test failure).

---

### Failure #3: Case #17 (S3 Dependency Failure Misdiagnosed as S4 Static Analysis)
- **True Hidden State:** `S3_dependency_failures`
- **Predicted Action:** `Fix Code` (designed for `S1`, `S2`, `S4`)
- **Actual Cost:** $75.07 (Wrong Action)
- **Dry-Run Trace:**
  - *Step 1 (Priors):* $P(S4) = 0.4162$, $P(S3) = 0.3122$.
  - *Step 2 (Free Evidence):* Observed $E1 = \text{D\_static\_analysis}$, $E2 = \text{mixed}$. Posteriors: $P(S4|E1,E2) = 0.5328$, $P(S3|E1,E2) = 0.4223$.
  - *Step 3 (E3 VoI Evaluation):* Acquired E3 (VoI=$3.02$). Observed: `fail_on_rerun`. Updated posteriors: $P(S4|E1,E2,E3) = 0.5688$, $P(S3|E1,E2,E3) = 0.3951$. Best Action: `Fix Code` (EC = $35.70).
  - *Step 4 (E4 VoI Evaluation):* Skipped E4 (VoI ≤ 0).
  - *Step 5 (Final Decision):* Executed `Fix Code`.

#### 10-Question Diagnostic Analysis:
- *Same as Case #0.* This is a systematic failure mode: whenever a dependency failure occurs in a project that runs static analysis checks, the failure of the static analysis step ($E1 = \text{D\_static\_analysis}$) misleads the agent into predicting a code/lint error ($S4$) instead of a dependency error ($S3$). E3 (rerun test) also fails in both cases, which reinforces the wrong belief.
- **Failure Classification:** `Misleading evidence` / `Systematic Bias`.

---

### Failure #4: Case #18 (S3 Dependency Failure Misdiagnosed as S4 Static Analysis)
- **True Hidden State:** `S3_dependency_failures`
- **Predicted Action:** `Fix Code`
- **Actual Cost:** $75.07
- **Dry-Run Trace:** Identical to Case #0 and Case #17.
- **Diagnostic Analysis:**
  - *Same as Case #0 and Case #17.* The repetition of this exact trace across three of the top five failures confirms that the agent is highly vulnerable to "import error crashes" during static analysis steps.
- **Failure Classification:** `Misleading evidence`.

---

### Failure #5: Case #23 (S5 Test Failure Misdiagnosed as S4 Static Analysis)
- **True Hidden State:** `S5_test_failures`
- **Predicted Action:** `Fix Code`
- **Actual Cost:** $75.07 (Wrong Action)
- **Dry-Run Trace:**
  - *Step 1 (Priors):* $P(S4) = 0.4162$, $P(S3) = 0.3122$, $P(S5) = 0.1164$, $P(S2) = 0.0582$.
  - *Step 2 (Free Evidence):* Observed $E1 = \text{E\_workflow}$, $E2 = \text{src}$. Posteriors: $P(S4|E1,E2) = 0.5145$, $P(S5|E1,E2) = 0.1332$, $P(S6|E1,E2) = 0.1000$. Best Action: `Fix Code` (EC = $30.76).
  - *Step 3 (E3 VoI Evaluation):* E3 has positive VoI ($5.29). Acquired E3. Observed: `fail_on_rerun`. Updated posteriors: $P(S4|E1,E2,E3) = 0.5794$, $P(S1|E1,E2,E3) = 0.1069$, $P(S5|E1,E2,E3) = 0.1005$. Best Action remains `Fix Code` (EC = $25.40).
  - *Step 4 (E4 VoI Evaluation):* Skipped E4 (VoI ≤ 0).
  - *Step 5 (Final Decision):* Executed `Fix Code`.

#### 10-Question Diagnostic Analysis:
1. **What did the agent believe?** The agent believed that S4 (Static Analysis) was highly likely (57.94%). It believed S5 was only 10.05% likely.
2. **What was actually true?** The failure was a test failure (`S5`).
3. **Which evidence did it use?** $E1 = \text{E\_workflow}$, $E2 = \text{src}$, and $E3 = \text{fail\_on\_rerun}$.
4. **Which evidence did it ignore?** $E4 = \text{local\_repro}$ (skipped due to high cost).
5. **Was the probability wrong?** Yes. E1 = E_workflow (meaning the runner failed during workflow execution) and E2 = src (only source files changed) pointed to S4 code changes causing syntax/import issues, when it actually broke a test logic condition.
6. **Was the hidden-state list incomplete?** No.
7. **Was the threshold wrong?** The agent chose to run the automated fix because the expected cost of `Fix Code` ($25.40) was lower than escalation ($50.00). S5 requires Escalation because test logic failures cannot be automated-fixed, but the agent was overconfident in S4.
8. **Was the cost model wrong?** Proably.
9. **Should it have asked for more information?** Yes. E4 would have shown it's a test logic issue, but the cost was prohibitive.
10. **Should a human have been involved?** Yes. S5 test logic failures require human triage, so escalation should have occurred.

- **Failure Classification:** `Misleading evidence` (general workflow step failure with source code changes was misattributed to static syntax violations rather than test logic breaks).

---

## 3. Key Failure Patterns & System Limitations

The failure analysis exposes three major weaknesses in the current agent design:

1. **Semantic Ambiguity of Coarse Evidence ($E1$ and $E2$):**
   A step failure (`D_static_analysis` or `C_test`) or a commit diff category (`mixed` or `src`) is syntactically clean but semantically ambiguous. A dependency failure (S3) can crash the lint step (S4) with an import error. An environment setup failure (S6) can crash the test runner (S5) with a library load error. Coarse evidence cannot resolve these overlaps.
   
2. **Unviable Safety Valve ($E4$ Local Repro):**
   E4 is highly informative but carries an assumed cost of **$33.33** (20 minutes of developer time). In decision theory, the Value of Information is bounded by the cost of obtaining it. Because E4 is so expensive, its VoI is almost always negative under P4, forcing the agent to make a "blind" gamble on E1/E2/E3.
   
3. **Optimistic Bias of Automation:**
   Because automated fixes are cheap ($8.33) and escalation is expensive ($50.00), the agent's expected-cost calculation has a systematic bias to try an automated fix even when it is highly uncertain, leading to frequent wrong-action penalties ($75.07).

---
To address these failure modes, we propose the following actionable steps:

### Action 1
-> Include more evidence sources to dintinguish between similar failure types. Rightnow evidence is broad and can imply multiple failure types.

### Action 2
-> Add more granular hidden states in training data to distinguish between similar failure types.


### Action 3: Introduce Log-Parsing Sub-Evidence (Resolve Misleading Evidence)

Instead of treating step failures as black boxes, the agent should perform simple regex log-parsing on the failed CI step. This splits $E1$ into granular sub-evidence categories:
- If a step fails with `ModuleNotFoundError` or `ImportError` $\rightarrow$ Map to $E1_{\text{import\_error}}$ (strongly points to `S3` dependency issues, not `S4` static lint).
- If a step fails with `gcc: command not found` or `missing header file` $\rightarrow$ Map to $E1_{\text{compiler\_error}}$ (strongly points to `S6` env setup).
- If a step fails with `AssertionError` or `test_... failed` $\rightarrow$ Map to $E1_{\text{test\_assertion}}$ (strongly points to `S5` test logic).

*Impact:* This removes the semantic overlap of $E1$, preventing Case #0, #10, #17, #18, and #23.

*Impact:* At $0.10, the VoI of $E4$ becomes positive in all ambiguous cases. The agent will run the local container to verify the failure before taking action, raising accuracy to >90%.



---

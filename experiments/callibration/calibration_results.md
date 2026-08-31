# P4 Policy Calibration Analysis Results

This document presents the calibration (reliability) analysis for the **P4 (Cost-based Value of Information)** policy run on the benchmark dataset.

- **Dataset:** `benchmark_cases_seed42.json`
- **Number of Cases:** 500
- **Policy Name:** P4 (Cost-based Value of Information)

Calibration tables evaluate whether the predicted probabilities output by the agent match the actual frequency of the events. Perfect calibration means that for all cases assigned a probability of $p$, the event occurs with frequency $p$.

---

## S1 (Source Code Issues)

### Calibration Table
| Bin | N | Avg Predicted | Actual % |
|---|---|---|---|
| 0–10% | 483 | 2.2% | 2.3% (11/483) |
| 10–20% | 17 | 13.6% | 5.9% (1/17) |
| 20–30% | 0 | - | - |
| 30–40% | 0 | - | - |
| 40–50% | 0 | - | - |
| 50–60% | 0 | - | - |
| 60–70% | 0 | - | - |
| 70–80% | 0 | - | - |
| 80–90% | 0 | - | - |
| 90–100% | 0 | - | - |

### Calibration Summary
S1 has a very low prior probability ($2.65\%$) and never reaches high posterior beliefs, with the maximum probability falling in the $10-20\%$ range. The policy is exceptionally well-calibrated in the dominant $0-10\%$ bin, which contains $483$ of the $500$ cases (predicted $2.2\%$ vs. actual $2.3\%$). However, in the $10-20\%$ bin, the agent is overconfident, predicting $13.6\%$ on average while the actual occurrence rate is only $5.9\%$ ($1$ out of $17$ cases).

---

## S2 (Project Config Issues)

### Calibration Table
| Bin | N | Avg Predicted | Actual % |
|---|---|---|---|
| 0–10% | 411 | 3.9% | 2.4% (10/411) |
| 10–20% | 66 | 12.8% | 19.7% (13/66) |
| 20–30% | 19 | 23.2% | 26.3% (5/19) |
| 30–40% | 4 | 32.2% | 25.0% (1/4) |
| 40–50% | 0 | - | - |
| 50–60% | 0 | - | - |
| 60–70% | 0 | - | - |
| 70–80% | 0 | - | - |
| 80–90% | 0 | - | - |
| 90–100% | 0 | - | - |

### Calibration Summary
S2 is a low-prior state ($5.82\%$). The agent exhibits slight overconfidence in the $0-10\%$ bin (predicted $3.9\%$ vs. actual $2.4\%$), but shows underconfidence in the $10-20\%$ bin (predicted $12.8\%$ vs. actual $19.7\%$) and the $20-30\%$ bin (predicted $23.2\%$ vs. actual $26.3\%$). The highest reached bin ($30-40\%$) shows overconfidence (predicted $32.2\%$ vs. actual $25.0\%$), but has a very small sample size ($N=4$) which limits its statistical significance.

---

## S3 (Dependency Failures)

### Calibration Table
| Bin | N | Avg Predicted | Actual % |
|---|---|---|---|
| 0–10% | 88 | 6.5% | 3.4% (3/88) |
| 10–20% | 130 | 12.2% | 13.8% (18/130) |
| 20–30% | 17 | 25.7% | 35.3% (6/17) |
| 30–40% | 113 | 37.0% | 45.1% (51/113) |
| 40–50% | 10 | 43.1% | 40.0% (4/10) |
| 50–60% | 109 | 54.8% | 50.5% (55/109) |
| 60–70% | 7 | 68.3% | 57.1% (4/7) |
| 70–80% | 26 | 70.7% | 73.1% (19/26) |
| 80–90% | 0 | - | - |
| 90–100% | 0 | - | - |

### Calibration Summary
S3 is a high-prior state ($31.22\%$) and spans posterior beliefs from $0\%$ to $80\%$. The P4 policy demonstrates excellent overall calibration across most populated bins. It is slightly underconfident in the $10-20\%$ bin (predicted $12.2\%$ vs. actual $13.8\%$), $20-30\%$ bin (predicted $25.7\%$ vs. actual $35.3\%$), $30-40\%$ bin (predicted $37.0\%$ vs. actual $45.1\%$), and $70-80\%$ bin (predicted $70.7\%$ vs. actual $73.1\%$). It is slightly overconfident in the $50-60\%$ bin (predicted $54.8\%$ vs. actual $50.5\%$), but remains very close to the ideal diagonal.

---

## S4 (Static Analysis Failures)

### Calibration Table
| Bin | N | Avg Predicted | Actual % |
|---|---|---|---|
| 0–10% | 166 | 6.2% | 8.4% (14/166) |
| 10–20% | 21 | 15.8% | 28.6% (6/21) |
| 20–30% | 71 | 23.2% | 23.9% (17/71) |
| 30–40% | 0 | - | - |
| 40–50% | 2 | 46.2% | 100.0% (2/2) |
| 50–60% | 85 | 56.8% | 48.2% (41/85) |
| 60–70% | 30 | 63.2% | 46.7% (14/30) |
| 70–80% | 0 | - | - |
| 80–90% | 125 | 83.9% | 83.2% (104/125) |
| 90–100% | 0 | - | - |

### Calibration Summary
S4 has the highest prior probability ($41.62\%$) and displays a strong bimodal distribution; the policy either rules it out ($0-10\%$, $166$ cases) or assigns high confidence ($80-90\%$, $125$ cases). The agent is exceptionally well-calibrated at these two extremes—namely in the $0-10\%$ bin (predicted $6.2\%$ vs. actual $8.4\%$), $20-30\%$ bin (predicted $23.2\%$ vs. actual $23.9\%$), and the $80-90\%$ bin (predicted $83.9\%$ vs. actual $83.2\%$). However, it shows some miscalibration in intermediate regions: it is underconfident in the $10-20\%$ and $40-50\%$ bins, and overconfident in the $50-60\%$ bin (predicted $56.8\%$ vs. actual $48.2\%$) and $60-70\%$ bin (predicted $63.2\%$ vs. actual $46.7\%$).

---

## S5 (Test Failures)

### Calibration Table
| Bin | N | Avg Predicted | Actual % |
|---|---|---|---|
| 0–10% | 254 | 2.4% | 0.8% (2/254) |
| 10–20% | 196 | 16.4% | 17.3% (34/196) |
| 20–30% | 10 | 25.7% | 20.0% (2/10) |
| 30–40% | 3 | 31.9% | 33.3% (1/3) |
| 40–50% | 7 | 45.0% | 28.6% (2/7) |
| 50–60% | 29 | 57.3% | 55.2% (16/29) |
| 60–70% | 0 | - | - |
| 70–80% | 1 | 71.8% | 100.0% (1/1) |
| 80–90% | 0 | - | - |
| 90–100% | 0 | - | - |

### Calibration Summary
S5 has a prior probability of $11.64\%$. The predictions are mostly concentrated in the $0-10\%$ and $10-20\%$ bins, which encompass $90\%$ of all cases. Within these dominant bins, the agent is well-calibrated (especially in the $10-20\%$ bin with $196$ cases, where predicted $16.4\%$ matches actual $17.3\%$). It is also well-calibrated in the $50-60\%$ bin (predicted $57.3\%$ vs. actual $55.2\%$). However, the policy shows slight overconfidence in the $0-10\%$, $20-30\%$, and $40-50\%$ bins.

---

## S6 (Environment Setup Issues)

### Calibration Table
| Bin | N | Avg Predicted | Actual % |
|---|---|---|---|
| 0–10% | 440 | 4.1% | 5.7% (25/440) |
| 10–20% | 53 | 16.3% | 20.8% (11/53) |
| 20–30% | 3 | 27.5% | 0.0% (0/3) |
| 30–40% | 4 | 32.8% | 50.0% (2/4) |
| 40–50% | 0 | - | - |
| 50–60% | 0 | - | - |
| 60–70% | 0 | - | - |
| 70–80% | 0 | - | - |
| 80–90% | 0 | - | - |
| 90–100% | 0 | - | - |

### Calibration Summary
S6 is a low-prior state ($5.64\%$). The agent exhibits underconfidence in the most populated bins: the $0-10\%$ bin (predicted $4.1\%$ vs. actual $5.7\%$) and the $10-20\%$ bin (predicted $16.3\%$ vs. actual $20.8\%$). The higher bins have very few cases ($N \le 4$), resulting in high statistical variance (e.g., $0.0\%$ actual rate for the $20-30\%$ bin, and $50.0\%$ actual rate for the $30-40\%$ bin).

---

## S7 (Other)

### Calibration Table
| Bin | N | Avg Predicted | Actual % |
|---|---|---|---|
| 0–10% | 492 | 1.1% | 0.8% (4/492) |
| 10–20% | 1 | 10.1% | 0.0% (0/1) |
| 20–30% | 4 | 24.5% | 0.0% (0/4) |
| 30–40% | 2 | 38.0% | 50.0% (1/2) |
| 40–50% | 1 | 44.4% | 0.0% (0/1) |
| 50–60% | 0 | - | - |
| 60–70% | 0 | - | - |
| 70–80% | 0 | - | - |
| 80–90% | 0 | - | - |
| 90–100% | 0 | - | - |

### Calibration Summary
S7 has the lowest prior probability ($1.41\%$) in the system. The vast majority of cases ($492$ out of $500$) fall into the $0-10\%$ bin, where the agent is exceptionally well-calibrated (predicted $1.1\%$ vs. actual $0.8\%$). The remaining higher bins contain only $1$ to $4$ cases, making calibration metrics in those ranges highly noisy and subject to high variance due to small sample sizes.

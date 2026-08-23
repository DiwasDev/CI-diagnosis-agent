### Problem Statement


## Hidden states
| Failure Category | Paper Code(s) | Count | Exact Fraction | Ratio | Prior |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Source Code Issues** | P1 | 54 | 54 / 375 | 0.144 | 0.144 |
| **Project Config Issues** | P2 | 19 | 19 / 375 | 0.05067 | 0.051 |
| **Dependency Failures** | P3 + P4 | 78 | (33 + 45) / 375 | 0.208 | 0.208 |
| **Static Analysis Failures** | P5 + P6 | 41 | (26 + 15) / 375 | 0.10933 | 0.109 |
| **Test Failures** | P8 | 120 | 120 / 375 | 0.320 | 0.320 |
| **Workflow Config Issues** | W2 | 21 | 21 / 375 | 0.056 | 0.056 |
| **Environment Setup Issues** | W4 | 13 | 13 / 375 | 0.03467 | 0.035 |
| **Other** | Remaining | 29 | 29 / 375 | 0.07733 | 0.077 |
| **Total** | — | **375** | **375 / 375** | **1.000** | **1.000** |



## Entropy Calculation-- Examples
The setup
8 hidden states with priors:
Table
State	Prior P(S)
Source Code Issues	0.144
Project Config Issues	0.051
Dependency Failures	0.208
Static Analysis Failures	0.109
Test Failures	0.320
Workflow Config Issues	0.056
Environment Setup Issues	0.035
Other	0.077
Prior entropy H(S):
plain
H(S) = -[0.144×log₂(0.144) + 0.051×log₂(0.051) + 0.208×log₂(0.208) 
       + 0.109×log₂(0.109) + 0.320×log₂(0.320) + 0.056×log₂(0.056) 
       + 0.035×log₂(0.035) + 0.077×log₂(0.077)]
     = 2.6543 bits
E1: Binary evidence (AssertionError in test phase)
Likelihoods P(E1 | S):
Table
State	yes	no
Source Code Issues	0.040	0.960
Project Config Issues	0.001	0.999
Dependency Failures	0.001	0.999
Static Analysis Failures	0.001	0.999
Test Failures	0.650	0.350
Workflow Config Issues	0.001	0.999
Environment Setup Issues	0.001	0.999
Other	0.020	0.980
Step 1: Compute P(outcome) for "yes"
plain
P(yes) = Σ_s P(S=s) × P(yes | S=s)

       = 0.144×0.040 + 0.051×0.001 + 0.208×0.001 + 0.109×0.001
       + 0.320×0.650 + 0.056×0.001 + 0.035×0.001 + 0.077×0.020

       = 0.005760 + 0.000051 + 0.000208 + 0.000109
       + 0.208000 + 0.000056 + 0.000035 + 0.001540

       = 0.215759
Step 2: Compute posterior P(S | yes) for each state
Bayes' rule:
plain
P(S=s | yes) = [P(S=s) × P(yes | S=s)] / P(yes)
Table
State	Prior × Like	Posterior
Source Code Issues	0.144×0.040 = 0.005760	0.005760 / 0.215759 = 0.0267
Project Config Issues	0.051×0.001 = 0.000051	0.000051 / 0.215759 = 0.0002
Dependency Failures	0.208×0.001 = 0.000208	0.000208 / 0.215759 = 0.0010
Static Analysis Failures	0.109×0.001 = 0.000109	0.000109 / 0.215759 = 0.0005
Test Failures	0.320×0.650 = 0.208000	0.208000 / 0.215759 = 0.9640
Workflow Config Issues	0.056×0.001 = 0.000056	0.000056 / 0.215759 = 0.0003
Environment Setup Issues	0.035×0.001 = 0.000035	0.000035 / 0.215759 = 0.0002
Other	0.077×0.020 = 0.001540	0.001540 / 0.215759 = 0.0071
Sum of posteriors = 1.0000. Check.
Step 3: Entropy of posterior given "yes"
plain
H(S | yes) = -[0.0267×log₂(0.0267) + 0.0002×log₂(0.0002) + 0.0010×log₂(0.0010)
             + 0.0005×log₂(0.0005) + 0.9640×log₂(0.9640) + 0.0003×log₂(0.0003)
             + 0.0002×log₂(0.0002) + 0.0071×log₂(0.0071)]

           = -[0.0267×(-5.23) + 0.0002×(-12.29) + 0.0010×(-9.97)
             + 0.0005×(-10.97) + 0.9640×(-0.053) + 0.0003×(-11.70)
             + 0.0002×(-12.29) + 0.0071×(-7.14)]

           = 0.140 + 0.002 + 0.010 + 0.005 + 0.051 + 0.004 + 0.002 + 0.051
           = 0.2646 bits
Entropy drop for "yes": 2.6543 - 0.2646 = 2.3898 bits
Step 4: Same thing for "no"
plain
P(no) = Σ_s P(S=s) × P(no | S=s)

      = 0.144×0.960 + 0.051×0.999 + 0.208×0.999 + 0.109×0.999
      + 0.320×0.350 + 0.056×0.999 + 0.035×0.999 + 0.077×0.980

      = 0.138240 + 0.050949 + 0.207792 + 0.108891
      + 0.112000 + 0.055944 + 0.034965 + 0.075460

      = 0.784241
Posterior P(S | no):
Table
State	Prior × Like	Posterior
Source Code Issues	0.138240	0.138240 / 0.784241 = 0.1763
Project Config Issues	0.050949	0.050949 / 0.784241 = 0.0650
Dependency Failures	0.207792	0.207792 / 0.784241 = 0.2650
Static Analysis Failures	0.108891	0.108891 / 0.784241 = 0.1389
Test Failures	0.112000	0.112000 / 0.784241 = 0.1428
Workflow Config Issues	0.055944	0.055944 / 0.784241 = 0.0713
Environment Setup Issues	0.034965	0.034965 / 0.784241 = 0.0446
Other	0.075460	0.075460 / 0.784241 = 0.0962
Entropy H(S | no):
plain
= -[0.1763×log₂(0.1763) + 0.0650×log₂(0.0650) + 0.2650×log₂(0.2650)
   + 0.1389×log₂(0.1389) + 0.1428×log₂(0.1428) + 0.0713×log₂(0.0713)
   + 0.0446×log₂(0.0446) + 0.0962×log₂(0.0962)]

= -[0.1763×(-2.504) + 0.0650×(-3.944) + 0.2650×(-1.916)
   + 0.1389×(-2.846) + 0.1428×(-2.808) + 0.0713×(-3.810)
   + 0.0446×(-4.487) + 0.0962×(-3.378)]

= 0.441 + 0.256 + 0.508 + 0.395 + 0.401 + 0.272 + 0.200 + 0.325
= 2.7986 bits
Entropy drop for "no": 2.6543 - 2.7986 = -0.1443 bits (entropy went UP)
Step 5: Expected Information Gain for E1
plain
H(S | E1) = P(yes)×H(S|yes) + P(no)×H(S|no)
          = 0.215759 × 0.2646 + 0.784241 × 2.7986
          = 0.0571 + 2.1948
          = 2.2519 bits

EIG(E1) = H(S) - H(S | E1)
        = 2.6543 - 2.2519
        = 0.4024 bits
E2: Categorical evidence (which step failed)
Same exact process, but 6 outcomes. I'll show one full example (outcome A), then the summary.
Likelihoods P(E2 | S):
Table
State	A	B	C	D	E	F
Source Code Issues	0.03	0.75	0.15	0.04	0.01	0.02
Project Config Issues	0.20	0.65	0.10	0.02	0.02	0.01
Dependency Failures	0.88	0.07	0.02	0.01	0.01	0.01
Static Analysis Failures	0.01	0.04	0.10	0.78	0.02	0.05
Test Failures	0.01	0.08	0.85	0.02	0.02	0.02
Workflow Config Issues	0.03	0.03	0.03	0.03	0.83	0.05
Environment Setup Issues	0.15	0.10	0.02	0.02	0.68	0.03
Other	0.18	0.12	0.20	0.08	0.25	0.17
Outcome A (Install step failed)
P(A) calculation:
plain
P(A) = 0.144×0.03 + 0.051×0.20 + 0.208×0.88 + 0.109×0.01
     + 0.320×0.01 + 0.056×0.03 + 0.035×0.15 + 0.077×0.18

   = 0.00432 + 0.01020 + 0.18304 + 0.00109
   + 0.00320 + 0.00168 + 0.00525 + 0.01386

   = 0.22264
Posterior P(S | A):
plain
Source Code Issues:      0.00432 / 0.22264 = 0.0194
Project Config Issues:   0.01020 / 0.22264 = 0.0458
Dependency Failures:     0.18304 / 0.22264 = 0.8221   <-- dominates
Static Analysis Failures: 0.00109 / 0.22264 = 0.0049
Test Failures:           0.00320 / 0.22264 = 0.0144
Workflow Config Issues:  0.00168 / 0.22264 = 0.0075
Environment Setup Issues: 0.00525 / 0.22264 = 0.0236
Other:                   0.01386 / 0.22264 = 0.0623
Entropy H(S | A):
plain
= -[0.0194×log₂(0.0194) + 0.0458×log₂(0.0458) + 0.8221×log₂(0.8221)
   + 0.0049×log₂(0.0049) + 0.0144×log₂(0.0144) + 0.0075×log₂(0.0075)
   + 0.0236×log₂(0.0236) + 0.0623×log₂(0.0623)]

= -[0.0194×(-5.69) + 0.0458×(-4.45) + 0.8221×(-0.283)
   + 0.0049×(-7.68) + 0.0144×(-6.12) + 0.0075×(-7.06)
   + 0.0236×(-5.41) + 0.0623×(-4.00)]

= 0.110 + 0.204 + 0.233 + 0.038 + 0.088 + 0.053 + 0.128 + 0.249
= 1.1020 bits
Entropy drop: 2.6543 - 1.1020 = 1.5523 bits
All 6 outcomes for E2
| Outcome | P(outcome) | H(S | outcome) | Entropy Drop |
|---------|-----------|-------------|--------------|
| A | 0.2226 | 1.102 bits | 1.552 bits |
| B | 0.2001 | 2.050 bits | 0.605 bits |
| C | 0.3315 | 1.088 bits | 1.566 bits |
| D | 0.1088 | 1.290 bits | 1.365 bits |
| E | 0.1027 | 2.093 bits | 0.561 bits |
| F | 0.0343 | 2.490 bits | 0.165 bits |
H(S | E2) = weighted average:
plain
= 0.2226×1.102 + 0.2001×2.050 + 0.3315×1.088
+ 0.1088×1.290 + 0.1027×2.093 + 0.0343×2.490

= 0.2453 + 0.4102 + 0.3607 + 0.1404 + 0.2149 + 0.0854
= 1.4567 bits

EIG(E2) = 2.6543 - 1.4567 = 1.1976 bits
E3: Categorical evidence (error class)
Same process, 8 outcomes. I'll show the key calculations.
Likelihoods P(E3 | S):
Table
State	α	β	γ	δ	ε	ζ	η	θ
Source Code Issues	0.80	0.05	0.02	0.01	0.10	0.01	0.00	0.01
Project Config Issues	0.05	0.85	0.05	0.01	0.01	0.02	0.00	0.01
Dependency Failures	0.05	0.05	0.88	0.00	0.00	0.01	0.00	0.01
Static Analysis Failures	0.02	0.02	0.01	0.90	0.02	0.02	0.00	0.01
Test Failures	0.03	0.01	0.01	0.05	0.85	0.03	0.00	0.02
Workflow Config Issues	0.005	0.005	0.005	0.005	0.005	0.05	0.875	0.05
Environment Setup Issues	0.05	0.02	0.10	0.01	0.01	0.75	0.05	0.01
Other	0.05	0.05	0.10	0.05	0.15	0.35	0.15	0.10
Outcome ε (Test Assertion) — the biggest one
P(ε):
plain
= 0.144×0.10 + 0.051×0.01 + 0.208×0.00 + 0.109×0.02
+ 0.320×0.85 + 0.056×0.005 + 0.035×0.01 + 0.077×0.15

= 0.0144 + 0.00051 + 0.00000 + 0.00218
+ 0.2720 + 0.00028 + 0.00035 + 0.01155

= 0.30127
Posterior P(S | ε):
plain
Source Code Issues:      0.01440 / 0.30127 = 0.0478
Project Config Issues:   0.00051 / 0.30127 = 0.0017
Dependency Failures:     0.00000 / 0.30127 = 0.0000
Static Analysis Failures: 0.00218 / 0.30127 = 0.0072
Test Failures:           0.27200 / 0.30127 = 0.9028   <-- dominates
Workflow Config Issues:  0.00028 / 0.30127 = 0.0009
Environment Setup Issues: 0.00035 / 0.30127 = 0.0012
Other:                   0.01155 / 0.30127 = 0.0383
H(S | ε):
plain
= -[0.0478×log₂(0.0478) + 0.0017×log₂(0.0017) + 0.0000×log₂(0.0000)
   + 0.0072×log₂(0.0072) + 0.9028×log₂(0.9028) + 0.0009×log₂(0.0009)
   + 0.0012×log₂(0.0012) + 0.0383×log₂(0.0383)]

= -[0.0478×(-4.39) + 0.0017×(-9.20) + 0 + 0.0072×(-7.12)
   + 0.9028×(-0.148) + 0.0009×(-10.12) + 0.0012×(-9.71) + 0.0383×(-4.71)]

= 0.210 + 0.016 + 0 + 0.051 + 0.134 + 0.009 + 0.012 + 0.180
= 0.6109 bits
Entropy drop: 2.6543 - 0.6109 = 2.0434 bits
Outcome γ (Dependency Resolver)
P(γ):
plain
= 0.144×0.02 + 0.051×0.05 + 0.208×0.88 + 0.109×0.01
+ 0.320×0.01 + 0.056×0.005 + 0.035×0.10 + 0.077×0.10

= 0.00288 + 0.00255 + 0.18304 + 0.00109
+ 0.00320 + 0.00028 + 0.00350 + 0.00770

= 0.20424
Posterior P(S | γ):
plain
Source Code Issues:      0.00288 / 0.20424 = 0.0141
Project Config Issues:   0.00255 / 0.20424 = 0.0125
Dependency Failures:     0.18304 / 0.20424 = 0.8962   <-- dominates
Static Analysis Failures: 0.00109 / 0.20424 = 0.0053
Test Failures:           0.00320 / 0.20424 = 0.0157
Workflow Config Issues:  0.00028 / 0.20424 = 0.0014
Environment Setup Issues: 0.00350 / 0.20424 = 0.0171
Other:                   0.00770 / 0.20424 = 0.0377
H(S | γ):
plain
= -[0.0141×log₂(0.0141) + 0.0125×log₂(0.0125) + 0.8962×log₂(0.8962)
   + 0.0053×log₂(0.0053) + 0.0157×log₂(0.0157) + 0.0014×log₂(0.0014)
   + 0.0171×log₂(0.0171) + 0.0377×log₂(0.0377)]

= -[0.0141×(-6.15) + 0.0125×(-6.32) + 0.8962×(-0.158)
   + 0.0053×(-7.56) + 0.0157×(-5.99) + 0.0014×(-9.48)
   + 0.0171×(-5.87) + 0.0377×(-4.73)]

= 0.087 + 0.079 + 0.142 + 0.040 + 0.094 + 0.013 + 0.100 + 0.178
= 0.7335 bits
Entropy drop: 2.6543 - 0.7335 = 1.9209 bits
All 8 outcomes for E3
| Outcome | P(outcome) | H(S | outcome) | Entropy Drop |
|---------|-----------|-------------|--------------|
| α | 0.1458 | 1.224 bits | 1.431 bits |
| β | 0.0712 | 1.856 bits | 0.799 bits |
| γ | 0.2042 | 0.734 bits | 1.921 bits |
| δ | 0.1205 | 0.942 bits | 1.713 bits |
| ε | 0.3013 | 0.611 bits | 2.043 bits |
| ζ | 0.0723 | 2.129 bits | 0.526 bits |
| η | 0.0623 | 0.868 bits | 1.786 bits |
| θ | 0.0224 | 2.425 bits | 0.229 bits |
H(S | E3) = weighted average:
plain
= 0.1458×1.224 + 0.0712×1.856 + 0.2042×0.734 + 0.1205×0.942
+ 0.3013×0.611 + 0.0723×2.129 + 0.0623×0.868 + 0.0224×2.425

= 0.1785 + 0.1321 + 0.1499 + 0.1135
+ 0.1841 + 0.1539 + 0.0541 + 0.0543

= 1.0201 bits

EIG(E3) = 2.6543 - 1.0201 = 1.6342 bits
Final Comparison
| Evidence Source | Outcomes | H(S | E) | EIG |
|----------------|----------|------|-----|
| E1 (AssertionError binary) | 2 | 2.252 bits | 0.402 bits |
| E2 (Which step failed) | 6 | 1.457 bits | 1.198 bits |
| E3 (Error class) | 8 | 1.020 bits | 1.634 bits |
The key insight about EIG
EIG is a planning-time average. It tells you: "If I run this check before I know what I'll see, how much will my uncertainty drop on average?" It does NOT tell you how reliably informative the check is.
E1 has a bimodal usefulness: "yes" is brilliant (2.39 bits), but "no" is worse than useless (-0.14 bits). Since "no" happens 78% of the time, the average is dragged down to 0.40 bits.
E3 wins because its two most probable outcomes (ε at 30%, γ at 20%) are both very sharp. Even the confounds (row 7's γ=0.10 leaking to Environment Setup) don't hurt enough because the home state still dominates at 89.6%.
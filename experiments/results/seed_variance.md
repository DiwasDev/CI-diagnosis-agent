# Seed variance — policy comparison across benchmark draws

The headline results in the README use the seed-42 benchmark. This table re-runs the same policies on independently sampled 500-case benchmarks (seeds 7 and 123) to show the ranking is not a single-draw artefact.

| Policy | Accuracy | Cost / case | Escalation % |
|---|---|---|---|
| P0 majority baseline | 49.5% ± 1.2% | $42.01 ± 0.83 | 0.0% ± 0.0% |
| P1 belief-only | 60.3% ± 0.9% | $35.96 ± 0.30 | 5.9% ± 1.1% |
| P2 expected-cost threshold | 50.9% ± 0.4% | $37.53 ± 0.25 | 44.3% ± 0.8% |
| P3 info-gain per dollar | 60.0% ± 0.7% | $35.64 ± 0.21 | 31.0% ± 1.7% |
| P4 cost-based VoI | 63.8% ± 0.7% | $34.21 ± 0.57 | 16.1% ± 2.3% |
| Fix3 derived threshold | 63.3% ± 0.4% | $39.03 ± 0.78 | 5.3% ± 1.4% |

± is the population standard deviation across the three seeds (n = 3).

P0's majority action is fit on each seed's own cases (disclosed in the README), so its accuracy is a slightly optimistic floor on every seed.

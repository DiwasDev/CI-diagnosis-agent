# Code review notes — notebook → `.py` conversion (Sep 2026)

Self-review performed against the rules in [`AGENTS.md`](../AGENTS.md), per the
conversion task. This file records what was checked, what was dropped on
purpose, and one spot that was hard to understand, written out with three
simpler alternative implementations.

## Self-review

1. **Can this be simpler?** Two things found and simplified during review:
   `run_policy_comparison.py` recomputed accuracy/cost/escalation from records
   that `summarize()` had already produced — it now prints straight from the
   summary; `summarize()` computed total cost twice. A third review pass (after
   a question about P3) caught `run_failure_analysis.py` counting failures
   *after* taking the top five, so every report claimed "5 failures"; it also
   revealed that the notebook's own stored P3/P4 cell outputs predate the E3
   mapping fix — see the mismatch section below.
2. **Can this be smaller?** The notebook's per-policy metric printouts
   (classification report + confusion matrix per policy, ~80 lines each) were
   collapsed into one comparison table plus a chart; the numbers a human acts
   on are unchanged.
3. **Can this be split further?** No. Policies are one module each; the harness
   is one module; each experiment is one script. Splitting further would create
   files without a concrete need.
4. **Would a human reviewer immediately understand the intent?** The one
   non-obvious function is `expected_information_gain` — see below.

## What was deliberately dropped from the notebook

- **The guard-fragility demo (Fix 2 `_probe` frame).** It existed to prove that
  pandas 3.x `iterrows()` turns a missing value into `NaN`, defeating an
  `is None` check. The conversion removes the failure mode instead of
  demonstrating it: outcomes are cleaned once in `evaluation._flatten_row`
  (using `pd.isna`) and policies only ever see `None`-or-value.
- **The worked-example narration (cell 23)** reprinted one P4 case with
  intermediate VoI numbers. The same information survives in generated form in
  the failure traces and the Fix 3 traces.
- **Banner-style printouts** (`=== ... ===` blocks restating results already
  shown) — dead output.
- **`action_cost_for_state`** — defined in the notebook, never called anywhere.

## Hard-to-understand spot: `expected_information_gain`

The notebook's implementation (kept, modulo naming) computes the expected
reduction in entropy from observing a evidence source. It took the longest to
verify during review because it nests three loops and mixes two concepts in
one pass: the *probability of each outcome* and the *entropy of each resulting
posterior*. Written out in plain math it is:

```
IG(post, E) = H(post) − Σ_o P(o) · H(post updated with o)
```

Three different ways to write it, from most literal to most vectorised:

### Approach A — decompose into two named helpers (chosen shape, cleaned)

Split the formula the way the math reads: build each hypothetical posterior,
weight its entropy.

```python
def posterior_after(posterior, evidence_key, outcome):
    """What the belief would become if `outcome` were observed."""
    return bayes_update(posterior, evidence_key, outcome)  # already normalises

def expected_information_gain(posterior, evidence_key):
    likelihoods = LIKELIHOODS[evidence_key]
    outcomes = {o for state in STATES for o in likelihoods[state]}
    return entropy(posterior) - sum(
        outcome_probability(posterior, likelihoods, o) * entropy(posterior_after(posterior, evidence_key, o))
        for o in outcomes
    )
```

Pros: reads like the formula; reuses `bayes_update` so there is exactly one
Bayes rule in the codebase. Cons: recomputes `P(o)` twice unless the marginal
is passed along.

### Approach B — marginal-table style, one dict pass

First compute the outcome marginal `P(o)`, then reuse it for both the
normalisation and the weighting — this is what the current implementation does,
but expressed as data instead of loop variables:

```python
def expected_information_gain(posterior, evidence_key):
    likelihoods = LIKELIHOODS[evidence_key]
    marginals = {
        outcome: sum(posterior[s] * likelihoods[s].get(outcome, 0.0) for s in STATES)
        for outcome in {o for s in STATES for o in likelihoods[s]}
    }
    return entropy(posterior) - sum(
        p_o * entropy({s: posterior[s] * likelihoods[s].get(o, 0.0) / p_o for s in STATES})
        for o, p_o in marginals.items() if p_o > 0
    )
```

Pros: `P(o)` computed once; the guard for impossible outcomes is one clause.
Cons: the nested dict-comprehension is denser, not simpler — reviewers must
hold the whole expression in their head.

### Approach C — numpy vectorisation

```python
def expected_information_gain(posterior, evidence_key):
    L = np.array([[LIKELIHOODS[evidence_key][s].get(o, 0.0) for o in OUTCOMES[evidence_key]]
                  for s in STATES])                      # states x outcomes
    prior = np.array([posterior[s] for s in STATES])
    joint = prior[:, None] * L                            # P(s, o)
    marginal = joint.sum(axis=0, keepdims=True)           # P(o)
    with np.errstate(divide="ignore", invalid="ignore"):
        posterior_given_o = np.where(marginal > 0, joint / marginal, 0.0)
    h_post = -(prior * np.log2(prior, where=prior > 0)).sum()
    h_cond = (marginal * xlogx(posterior_given_o)).sum()
    return h_post - h_cond
```

Pros: fastest on large state/outcome spaces; no Python loops. Cons: index
bookkeeping (`axis=0`, `[:, None]`) is exactly the kind of thing a human
reviewer cannot verify at a glance, and the project's state space is 7 states —
the speed-up is irrelevant here.

### Decision

Approach A's *shape* (reuse `bayes_update`, name the pieces) is the one the
converted code follows, keeping B's single computation of the outcome
marginal. C was rejected: it trades reviewability for speed the benchmark does
not need. If state or outcome spaces grow by an order of magnitude, revisit C.

## Things re-verified against the notebook's outputs

- **The notebook disagrees with itself.** Its stored cell outputs for P3
  (51.0%, $0.00 info cost — byte-identical to P2) and P4 (61.0%, $17,918.17)
  were last executed with the E3 key bug, so E3 never updated any belief and
  P3 degenerated to P2. The narrative summary (P3 60.4%, P4 63.0%, $17,504.49)
  matches the *corrected* E3-active run from the Fix 2 section, row (a).
- **The converted scripts reproduce the corrected (E3-active) numbers**: P3
  60.4% / $17,966.37 / 33.4% escalation, P4 63.0% / $17,504.49 / 17.2%. The
  committed `experiments/failures/*.md` from the notebook era are E3-broken
  artifacts (P4 reports 195 failures = 61.0% accuracy); the regenerated
  reports reflect E3-active policies (P4: 185 failures = 63.0% accuracy).
- **The P3 rewrite is per-case identical**: the notebook's verbatim cell-11
  implementation and the converted `InfoGainPerDollar` produce the same action
  and the same evidence set on all 500 cases. The notebook's two-clause stop
  `if action != 'Escalate' and max(posterior.values()) >= 0.55` collapses to
  `act_or_escalate(posterior) != "Escalate"` because
  `choose_expected_cost_action` already returns `Escalate` whenever the max
  posterior is below 0.55 — the second clause is redundant.
- Fix 1's E4 = $0.10 what-if reproduces the direction and magnitude of the
  notebook's Fix-part results (accuracy up, E4 now purchased).
- Fix 2's baseline row "(a) E3 mapped, original likelihood" reproduces the
  notebook's corrected-mapping run; the optimistic-likelihood run reproduces
  the Fix 2 result.
- Fix 3's p* = 0.3756 and its [0.30, 0.45] sensitivity band reproduce the
  notebook derivation.

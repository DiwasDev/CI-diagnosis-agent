# Coding rules for agents working in this repo

Scope discipline

- Never make unrelated changes in the same PR, commit, or task.
- Every change must have a single clear intent that can be explained in one sentence.
- Split large features into small independently reviewable commits.

Size and intent

- Prefer modifying existing code over rewriting entire files.
- Do not increase code size unless complexity reduction or functionality gain is justified.
- Before writing code, identify the smallest possible change that solves the problem.

Functions and naming

- Every new function must have a clear responsibility.
- If a function requires "START/END" comments, refactor it into smaller functions.
- Prefer descriptive naming over explanatory comments.
- Comments should explain *why*, not *what*.

Hygiene

- Never leave dead code, TODOs, placeholder implementations, or "kind of useless" logic.
- Remove temporary debugging code before completion.

Structure

- Avoid nested abstractions that do not reduce complexity.
- New code must match the style and architecture of the existing codebase.
- Do not create files, classes, patterns, or abstractions without a concrete need.

Self-review before finishing

1. Can this be simpler?
2. Can this be smaller?
3. Can this be split further?
4. Would a human reviewer immediately understand the intent?

Optimize for maintainability and reviewability, not output volume.

Notebook → script conversions

- Keep experiment logic out of notebooks: notebooks may remain as narrative archives,
  but every runnable experiment lives in a `.py` script under `experiments/`.
- Shared model constants stay in `experiments/constants.py`; shared decision math in
  `experiments/policies/base.py`; data loading and metrics in `experiments/evaluation.py`.
- What-if experiments must not mutate module-level constants; inject overrides instead.

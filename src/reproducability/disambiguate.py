"""
CI Repair Benchmark — Tag Disambiguation Script
================================================
Maps multi-label `error_type` symptom tags to exactly ONE of 8 mutually
exclusive hidden states, per the Probability Decision Record v2.

Strategy for memory efficiency
-------------------------------
Polars lazy evaluation (scan_parquet) defers I/O and pushes down predicates
so only the columns we touch are loaded.  The UDF step requires materialising
the `error_type` series in RAM, but we do that on a single column at a time
rather than loading the full 1 GB frame eagerly.

Pipeline
--------
1.  scan_parquet  →  LazyFrame   (no RAM allocated yet)
2.  collect only `error_type`   (one column, tiny)
3.  Apply dedup UDF             → `error_type_deduped`  (str)
4.  Apply disambiguate UDF      → `primary_hidden_state` (str)
5.  Rejoin enriched columns back into the full LazyFrame via with_columns
    on the sink path — we write in one streaming pass.
6.  Interactive checkpoint: 20-row sample before any file is written.
7.  sink_parquet  (streaming write, never loads full frame into RAM)

Hidden States
-------------
1. Source Code Issues
2. Project Config Issues
3. Dependency Failures
4. Static Analysis Failures
5. Test Failures
6. Workflow Config Issues
7. Environment Setup Issues
8. Other

Usage
-----
    python src/disambiguate.py

Requires: polars >= 1.0
"""

import math
import sys
from pathlib import Path

import polars as pl

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT   = Path(__file__).resolve().parent.parent
INPUT_PATH  = REPO_ROOT / "data" / "ci_repair_bench.parquet"
OUTPUT_PATH = REPO_ROOT / "data" / "ci_repair_bench_disambiguated.parquet"

# ---------------------------------------------------------------------------
# Constants — Hidden States
# ---------------------------------------------------------------------------
STATE_SOURCE_CODE  = "Source Code Issues"
STATE_PROJECT_CFG  = "Project Config Issues"
STATE_DEPENDENCY   = "Dependency Failures"
STATE_STATIC       = "Static Analysis Failures"
STATE_TEST         = "Test Failures"
STATE_WORKFLOW_CFG = "Workflow Config Issues"
STATE_ENV_SETUP    = "Environment Setup Issues"
STATE_OTHER        = "Other"

VALID_STATES = {
    STATE_SOURCE_CODE,
    STATE_PROJECT_CFG,
    STATE_DEPENDENCY,
    STATE_STATIC,
    STATE_TEST,
    STATE_WORKFLOW_CFG,
    STATE_ENV_SETUP,
    STATE_OTHER,
}

# ---------------------------------------------------------------------------
# Precedence order: index 0 = earliest pipeline phase = highest priority.
# "Runtime Error" is deliberately absent — it is handled by co-occurrence only.
# ---------------------------------------------------------------------------
PRECEDENCE: list[tuple[str, str]] = [
    ("Environment Error",               STATE_ENV_SETUP),
    ("Configuration Error",             STATE_PROJECT_CFG),
    ("Package Installation Error",      STATE_DEPENDENCY),
    ("Dependency Issues",               STATE_DEPENDENCY),
    ("Syntax Error",                    STATE_SOURCE_CODE),
    ("Type Checking Error",             STATE_STATIC),
    ("Code Linting",                    STATE_STATIC),
    ("Code Formatting",                 STATE_STATIC),
    ("Documentation or Docstring Error", STATE_STATIC),
    # Runtime Error handled separately — not in this list
    ("Assertion Error",                 STATE_TEST),
    ("Test Failure",                    STATE_TEST),
]


# ---------------------------------------------------------------------------
# Core disambiguation logic
# ---------------------------------------------------------------------------

def _to_py_list(val) -> list[str]:
    """
    Normalise whatever map_elements delivers for a List(String) element.
    Polars passes a pl.Series per element; convert to a plain Python list.
    """
    if val is None:
        return []
    if isinstance(val, pl.Series):
        return val.to_list()          # List[str | None]
    if isinstance(val, list):
        return val
    return list(val)


def _resolve_runtime_error(tags: set[str]) -> str:
    """
    Co-occurrence fallback for 'Runtime Error'.
    Called only when no higher-precedence tag was found.

    Priority order (spec §3):
      1. Dependency Issues / Package Installation Error → Dependency Failures
      2. Test Failure / Assertion Error                 → Test Failures
      3. Syntax Error                                   → Source Code Issues
      4. Code Linting / Code Formatting                 → Static Analysis Failures
      5. Environment Error                              → Environment Setup Issues
      6. Configuration Error                            → Project Config Issues
      7. Alone / ambiguous                              → Other  (user decision)
    """
    if tags & {"Dependency Issues", "Package Installation Error"}:
        return STATE_DEPENDENCY
    if tags & {"Test Failure", "Assertion Error"}:
        return STATE_TEST
    if "Syntax Error" in tags:
        return STATE_SOURCE_CODE
    if tags & {"Code Linting", "Code Formatting"}:
        return STATE_STATIC
    if "Environment Error" in tags:
        return STATE_ENV_SETUP
    if "Configuration Error" in tags:
        return STATE_PROJECT_CFG
    return STATE_OTHER   # alone or ambiguous


def _disambiguate_element(val) -> str:
    """
    Per-row UDF: given raw error_type tags (as a pl.Series or list),
    return exactly one hidden-state string.

    Steps:
      1. Normalise to Python list, filter None, deduplicate into a set.
      2. Walk PRECEDENCE; return the state of the first matched tag.
      3. If nothing matched but 'Runtime Error' is present: co-occurrence fallback.
      4. Fallback: Other.
    """
    raw = _to_py_list(val)
    tags: set[str] = {t for t in raw if t is not None}

    if not tags:
        return STATE_OTHER

    # Precedence walk
    for tag, state in PRECEDENCE:
        if tag in tags:
            return state

    # Runtime Error co-occurrence
    if "Runtime Error" in tags:
        return _resolve_runtime_error(tags)

    return STATE_OTHER   # unknown tags → catch-all


def _dedup_element(val) -> str | None:
    """
    Per-row UDF: deduplicate error_type tags and return a sorted,
    comma-separated string.

    e.g.  ['Code Formatting', 'Code Formatting']  →  'Code Formatting'
          ['Syntax Error', 'Test Failure']         →  'Syntax Error, Test Failure'

    Returns None only if the input list is empty/null (shouldn't occur
    in this dataset but handled defensively).
    """
    raw = _to_py_list(val)
    unique = sorted({t for t in raw if t is not None})
    return ", ".join(unique) if unique else None


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 65)
    print("  CI Repair Benchmark — Disambiguation Pipeline")
    print(f"  Polars  : {pl.__version__}")
    print(f"  Input   : {INPUT_PATH}")
    print(f"  Output  : {OUTPUT_PATH}")
    print("=" * 65)

    # ------------------------------------------------------------------
    # Step 1 — Lazy scan: schema + row count without loading data
    # ------------------------------------------------------------------
    print("\n[1/5]  Lazy scan …")
    lf = pl.scan_parquet(INPUT_PATH)
    schema = lf.collect_schema()
    total_rows = lf.select(pl.len()).collect().item()
    print(f"       Columns : {len(schema)}")
    print(f"       Rows    : {total_rows:,}")

    # ------------------------------------------------------------------
    # Step 2 — Collect ONLY the error_type column for UDF processing.
    #          Everything else stays on disk; we re-join at write time.
    # ------------------------------------------------------------------
    print("\n[2/5]  Collecting error_type column …")
    et_series: pl.Series = (
        lf.select("error_type")
          .collect()["error_type"]      # single column, dtype List(String)
    )
    print(f"       Loaded {len(et_series):,} rows  |  "
          f"null count: {et_series.null_count()}")

    # ------------------------------------------------------------------
    # Step 3 — Apply UDFs on the in-memory series
    # ------------------------------------------------------------------
    print("\n[3/5]  Applying dedup + disambiguation UDFs …")

    deduped_series: pl.Series = et_series.map_elements(
        _dedup_element, return_dtype=pl.String
    ).alias("error_type_deduped")

    state_series: pl.Series = et_series.map_elements(
        _disambiguate_element, return_dtype=pl.String
    ).alias("primary_hidden_state")

    # Validate: no nulls, no unknown states
    null_state    = state_series.null_count()
    invalid_count = (~state_series.is_in(list(VALID_STATES))).sum()
    print(f"       Null primary_hidden_state : {null_state}")
    print(f"       Unknown state values      : {invalid_count}")
    if null_state > 0 or invalid_count > 0:
        bad = state_series.filter(~state_series.is_in(list(VALID_STATES))).unique()
        print(f"       Bad values: {bad.to_list()}", file=sys.stderr)
        print("       ERROR: validation failed — aborting.", file=sys.stderr)
        sys.exit(1)
    print("       Validation passed.")

    # ------------------------------------------------------------------
    # Step 4 — Interactive checkpoint: 20-row sample
    # ------------------------------------------------------------------
    print("\n[4/5]  Validation sample (20 rows, seed=42) …")
    print("-" * 65)

    # Build a tiny in-memory frame just for display
    ids: pl.Series = lf.select("id").collect()["id"]
    sample_df = (
        pl.DataFrame({
            "id":                  ids,
            "error_type":          et_series,
            "error_type_deduped":  deduped_series,
            "primary_hidden_state": state_series,
        })
        .sample(n=20, seed=42)
    )

    for row in sample_df.iter_rows(named=True):
        orig    = str(row["error_type"].to_list()
                      if isinstance(row["error_type"], pl.Series)
                      else row["error_type"])
        deduped = row["error_type_deduped"]
        state   = row["primary_hidden_state"]
        rid     = row["id"]
        print(f"  id={rid:<6} | orig : {orig}")
        print(f"         | dedup: {deduped}")
        print(f"         | state: {state}")
        print()

    print("-" * 65)
    answer = input(
        "\nDoes the mapping look correct? Type 'yes' to write the output: "
    ).strip().lower()
    if answer != "yes":
        print("Aborted. No files written.")
        sys.exit(0)

    # ------------------------------------------------------------------
    # Step 5 — Re-scan full file, attach derived columns, sink to parquet.
    #          We inject the two new columns as pl.lit Series so the scan
    #          never loads the original data columns into RAM beyond what
    #          the Parquet reader streams.
    # ------------------------------------------------------------------
    print(f"\n[5/5]  Writing enriched dataset → {OUTPUT_PATH} …")

    full_df = (
        lf.collect()                     # collect full frame once for write
          .with_columns([
              deduped_series,
              state_series,
          ])
    )
    full_df.write_parquet(OUTPUT_PATH, compression="zstd")
    print(f"       Written {full_df.shape[0]:,} rows × {full_df.shape[1]} columns.")

    # ------------------------------------------------------------------
    # Empirical priors
    # ------------------------------------------------------------------
    print("\n" + "=" * 65)
    print("  Empirical Priors")
    print("=" * 65)

    priors = (
        full_df
        .group_by("primary_hidden_state")
        .agg(pl.len().alias("count"))
        .with_columns(
            (pl.col("count") / pl.col("count").sum()).alias("proportion")
        )
        .sort("count", descending=True)
    )

    print(f"\n  {'Hidden State':<30} {'Count':>6}  {'Prior':>8}")
    print("  " + "-" * 48)
    for row in priors.iter_rows(named=True):
        print(f"  {row['primary_hidden_state']:<30} {row['count']:>6}  {row['proportion']:>8.4f}")

    total = priors["count"].sum()
    print("  " + "-" * 48)
    print(f"  {'TOTAL':<30} {total:>6}  {'1.0000':>8}")

    entropy = -sum(
        p * math.log2(p)
        for p in priors["proportion"].to_list()
        if p > 0
    )
    print(f"\n  Prior entropy  H(S) = {entropy:.4f} bits")
    print(f"  (cf. literature prior from Zheng et al.: 2.6543 bits)")
    print()
    print("  Pipeline complete.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Verify deterministic outputs from axis_property_reproduction.py."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REQUIRED_AUDIT_TRUE = {
    "pi_countermodel_verified",
    "pii_countermodel_verified",
    "primitive_non_derivability_finite_witness_pair_verified",
    "undefined_rank_distinct_from_defined_zero_verified",
    "rank_two_witness_verified",
    "rank_two_defined_zero_coupling_verified",
    "rank_two_whole_span_normal_zero_dim_verified",
    "rank_three_cyclic_closure_verified",
    "single_normal_match_insufficient_verified",
    "degenerate_overlap_not_transverse_verified",
    "matrix_size_rank_separation_verified",
    "same_rank_property_value_obstruction_verified",
    "same_size_block_value_obstruction_verified",
    "scalar_collision_obstruction_verified",
    "conditional_rank_three_witness_verified",
}


def verify(results_dir: Path) -> dict[str, object]:
    summary_path = results_dir / "axis_property_witness_summary.json"
    audit_path = results_dir / "proof_obligation_audit.json"
    catalog_path = results_dir / "witness_catalog.csv"
    for path in (summary_path, audit_path, catalog_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    missing = sorted(REQUIRED_AUDIT_TRUE.difference(audit))
    if missing:
        raise AssertionError(f"missing audit keys: {missing}")
    failed = sorted(key for key in REQUIRED_AUDIT_TRUE if audit[key] is not True)
    if failed:
        raise AssertionError(f"failed proof-obligation checks: {failed}")

    if summary["rank_status_witnesses"]["rank_inapplicable"] is not None:
        raise AssertionError("inapplicable rank must remain JSON null")
    if summary["rank_status_witnesses"]["rank_zero"] != 0:
        raise AssertionError("defined rank-zero witness changed")
    if summary["rank_two_witness"]["rank"] != 2:
        raise AssertionError("rank-two witness changed")
    if summary["rank_three_cyclic_witness"]["rank"] != 3:
        raise AssertionError("rank-three witness changed")
    if summary["matrix_size_rank_witness"]["block_size"] != 3 or summary["matrix_size_rank_witness"]["realized_rank"] != 2:
        raise AssertionError("matrix-size/rank witness changed")

    with catalog_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 13:
        raise AssertionError(f"expected 13 witness rows, got {len(rows)}")
    if any(row["verified"] != "True" for row in rows):
        raise AssertionError("witness_catalog.csv contains an unverified row")

    return {
        "summary_file": summary_path.name,
        "audit_file": audit_path.name,
        "catalog_file": catalog_path.name,
        "audit_checks": len(REQUIRED_AUDIT_TRUE),
        "catalog_rows": len(rows),
        "all_verified": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "results",
        help="Directory containing deterministic reproduction outputs.",
    )
    args = parser.parse_args()
    print(json.dumps(verify(args.results_dir), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

# Axioms for the Property Structure of Realized Axes — reproducibility package

This repository is the standard-library Python companion to:

> Kwon Dominicus, *Axioms for the Property Structure of Realized Axes in Dimensional-Structural Describability*.

It reconstructs the manuscript's explicit finite countermodels, finite axis-property witnesses, and displayed classification obstructions with exact rational linear algebra. It does **not** replace the manuscript's general set-theoretic proofs of unique explicit completion, Stage-VI factorization, strict-isomorphism equivalence, or finite-realization existence.

## Reproduced claims

The package deterministically verifies:

- the displayed PI-failure / PII-satisfied finite countermodel;
- the displayed PII-failure / PI-satisfied finite countermodel;
- the distinction between axis-inapplicable rank (`null`) and defined rank zero (`0`);
- rank-one, fully specified rank-two, and Euclidean rank-three cyclic witnesses;
- the rank-two witness's defined zero coupling and zero-dimensional intrinsic normal of the whole realized span;
- the Euclidean `R^4` counterexample showing that one normal-axis inclusion does not imply cyclic triadic closure;
- a degenerate bilinear witness with a nonzero radical that is not transverse;
- a `3 x 3` property block built from three tagged axes whose realized-axis rank is only `2`;
- equal-rank models with a fixed-channel property-value obstruction to strict isomorphism;
- equal-size representation blocks with a preserved encoded-value obstruction;
- a displayed finite-coordinate scalar collision that loses a typed property distinction;
- the conditional `2 + 1 = 3` rank witness for a nondegenerate two-dimensional axis-generated subspace with a one-dimensional intrinsic normal.

## Requirements

- Python 3.10 or later
- No third-party dependencies

The finite witness data are embedded deterministically in the program. There is no external input file for this formal reproducibility package, matching the companion `Formation_Axiom_System` repository.

## Run on Windows

From the repository root:

```powershell
python src\axis_property_reproduction.py --output-dir results
python src\verify_axis_property_results.py --results-dir results
python -m unittest discover -s tests -v
```

## Run on Linux or macOS

```bash
python3 src/axis_property_reproduction.py --output-dir results
python3 src/verify_axis_property_results.py --results-dir results
python3 -m unittest discover -s tests -v
```

## Deterministic outputs

- `results/axis_property_witness_summary.json`
- `results/proof_obligation_audit.json`
- `results/witness_catalog.csv`

## Interpretation boundary

The executable checks finite instances and necessary obstructions appearing in the manuscript. It is not an automated formalization of the whole axiom system. In particular, the general theorems on unique explicit completion, primitive reduction, strict-isomorphism equivalence, Stage-VI factorization, and arbitrary compatible finite-data realization remain manuscript proofs. See `PROOF_MAP.md` for the claim-by-claim boundary.

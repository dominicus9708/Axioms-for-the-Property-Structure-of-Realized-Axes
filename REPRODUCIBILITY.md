# Reproducibility

The package is deterministic and uses only the Python standard library. All linear-algebra calculations use `fractions.Fraction`; no floating-point tolerance is used.

## Canonical run

Windows PowerShell:

```powershell
python src\axis_property_reproduction.py --output-dir results
python src\verify_axis_property_results.py --results-dir results
python -m unittest discover -s tests -v
```

Linux/macOS:

```bash
python3 src/axis_property_reproduction.py --output-dir results
python3 src/verify_axis_property_results.py --results-dir results
python3 -m unittest discover -s tests -v
```

The first command regenerates all committed files under `results/`. The second command verifies the expected witness inventory and proof-obligation booleans. The third command tests exact linear algebra, countermodels, obstructions, and byte-for-byte deterministic regeneration.

## Inputs and outputs

This formal witness package has no external input dataset. The finite model data are part of the executable constructions, following the precedent of the `Formation_Axiom_System` reproducibility repository.

Outputs:

- `results/axis_property_witness_summary.json`
- `results/proof_obligation_audit.json`
- `results/witness_catalog.csv`

## Boundary

Passing the computational audit means that the displayed finite constructions are internally reproduced by the code. It does not by itself prove the manuscript's general ZFC-level theorems or any physical interpretation.

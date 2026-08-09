from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import axis_property_reproduction as apr  # noqa: E402
import verify_axis_property_results as verifier  # noqa: E402


class AxisPropertyReproductionTests(unittest.TestCase):
    def test_pi_countermodel(self) -> None:
        model = apr.construct_pi_countermodel()
        self.assertFalse(model.check_pi())
        self.assertTrue(model.check_pii())

    def test_pii_countermodel(self) -> None:
        model = apr.construct_pii_countermodel()
        self.assertTrue(model.check_pi())
        self.assertFalse(model.check_pii())

    def test_undefined_rank_is_not_defined_zero(self) -> None:
        data = apr.construct_trivial_and_rank_witnesses()
        self.assertIsNone(data["rank_inapplicable"])
        self.assertEqual(data["rank_zero"], 0)
        self.assertTrue(data["undefined_is_distinct_from_zero"])

    def test_rank_two_witness(self) -> None:
        _, audit = apr.construct_rank_two_witness()
        self.assertEqual(audit["rank"], 2)
        self.assertTrue(audit["canonical_independence"])
        self.assertTrue(audit["canonical_orthogonality"])
        self.assertTrue(audit["defined_zero_coupling"])
        self.assertEqual(audit["whole_span_intrinsic_normal_dimension"], 0)

    def test_rank_three_cyclic_witness(self) -> None:
        data = apr.construct_rank_three_cyclic_witness()
        self.assertEqual(data["rank"], 3)
        self.assertTrue(data["lines_independent"])
        self.assertTrue(data["cyclic_closed"])

    def test_single_normal_match_is_insufficient(self) -> None:
        data = apr.construct_single_normal_insufficient_witness()
        self.assertTrue(data["ell3_is_contained_in_normal_12"])
        self.assertFalse(data["normal_12_is_one_dimensional"])
        self.assertFalse(data["cyclic_closed_for_123"])

    def test_degenerate_radical(self) -> None:
        data = apr.construct_degenerate_radical_witness()
        self.assertEqual(data["radical_dimension"], 1)
        self.assertTrue(data["line_is_in_ambient_normal"])
        self.assertFalse(data["line_is_transverse"])
        self.assertFalse(data["subspace_nondegenerate"])

    def test_matrix_size_does_not_fix_rank(self) -> None:
        data = apr.construct_matrix_size_rank_witness()
        self.assertEqual(data["block_size"], 3)
        self.assertEqual(data["realized_rank"], 2)
        self.assertTrue(data["block_size_differs_from_realized_rank"])

    def test_same_rank_property_obstruction(self) -> None:
        data = apr.construct_same_rank_different_property_witness()
        self.assertTrue(data["ranks_equal"])
        self.assertTrue(data["strict_value_preservation_obstruction"])

    def test_scalar_collision(self) -> None:
        data = apr.construct_scalar_collision_witness()
        self.assertTrue(data["same_displayed_summary"])
        self.assertTrue(data["typed_property_value_obstruction"])

    def test_conditional_rank_three(self) -> None:
        data = apr.conditional_rank_three_witness()
        self.assertTrue(data["subspace_nondegenerate"])
        self.assertEqual(data["subspace_dimension"], 2)
        self.assertEqual(data["intrinsic_normal_dimension"], 1)
        self.assertEqual(data["realized_span_dimension"], 3)

    def test_deterministic_outputs_and_verifier(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            apr.write_outputs(out)
            result = verifier.verify(out)
            self.assertTrue(result["all_verified"])
            first = (out / "axis_property_witness_summary.json").read_bytes()
            apr.write_outputs(out)
            second = (out / "axis_property_witness_summary.json").read_bytes()
            self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()

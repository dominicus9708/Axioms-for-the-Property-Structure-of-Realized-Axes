#!/usr/bin/env python3
"""Reproduce finite witnesses from the realized-axis property axiom system.

This module is a standard-library computational companion to

    Kwon Dominicus,
    "Axioms for the Property Structure of Realized Axes in
    Dimensional-Structural Describability".

It reconstructs the manuscript's explicit finite countermodels and witnesses
with exact rational linear algebra.  It is not a proof assistant and does not
replace the manuscript's general set-theoretic proofs of unique completion,
Stage-VI factorization, or strict-isomorphism equivalence.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Mapping, Sequence

Number = int | Fraction
Vector = tuple[Fraction, ...]
Matrix = tuple[Vector, ...]
Line = Vector

EXPECTED = {
    "pi_countermodel_pi": False,
    "pi_countermodel_pii": True,
    "pii_countermodel_pi": True,
    "pii_countermodel_pii": False,
    "rank_inapplicable": None,
    "rank_zero": 0,
    "rank_one": 1,
    "rank_two": 2,
    "rank_three": 3,
    "rank_two_whole_span_intrinsic_normal_dimension": 0,
    "rank_three_cyclic_closed": True,
    "r4_single_normal_match_cyclic_closed": False,
    "degenerate_radical_dimension": 1,
    "three_tag_block_size": 3,
    "three_tag_realized_rank": 2,
    "same_rank_property_value_obstruction": True,
    "same_size_block_value_obstruction": True,
    "scalar_collision_same_summary": True,
    "scalar_collision_value_obstruction": True,
}


def q(value: Number) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def vec(values: Iterable[Number]) -> Vector:
    return tuple(q(value) for value in values)


def mat(rows: Iterable[Iterable[Number]]) -> Matrix:
    rows_t = tuple(vec(row) for row in rows)
    if rows_t and len({len(row) for row in rows_t}) != 1:
        raise ValueError("matrix rows must have a common width")
    return rows_t


def identity(n: int) -> Matrix:
    return tuple(tuple(Fraction(int(i == j)) for j in range(n)) for i in range(n))


def zero_vector(n: int) -> Vector:
    return tuple(Fraction(0) for _ in range(n))


def add_vectors(left: Vector, right: Vector) -> Vector:
    return tuple(a + b for a, b in zip(left, right, strict=True))


def scale_vector(scale: Fraction, vector: Vector) -> Vector:
    return tuple(scale * entry for entry in vector)


def linear_combination(coefficients: Sequence[Fraction], basis: Sequence[Vector]) -> Vector:
    if not basis:
        return ()
    out = zero_vector(len(basis[0]))
    for coefficient, vector in zip(coefficients, basis, strict=True):
        out = add_vectors(out, scale_vector(coefficient, vector))
    return out


def rref(rows: Sequence[Sequence[Number]], width: int | None = None) -> tuple[Matrix, tuple[int, ...]]:
    a = [list(vec(row)) for row in rows]
    if not a:
        return tuple(), tuple()
    n_cols = len(a[0]) if width is None else width
    if any(len(row) != n_cols for row in a):
        raise ValueError("row width mismatch")

    pivot_cols: list[int] = []
    pivot_row = 0
    for col in range(n_cols):
        candidate = next((row for row in range(pivot_row, len(a)) if a[row][col] != 0), None)
        if candidate is None:
            continue
        a[pivot_row], a[candidate] = a[candidate], a[pivot_row]
        pivot = a[pivot_row][col]
        a[pivot_row] = [entry / pivot for entry in a[pivot_row]]
        for row in range(len(a)):
            if row == pivot_row:
                continue
            factor = a[row][col]
            if factor != 0:
                a[row] = [entry - factor * base for entry, base in zip(a[row], a[pivot_row], strict=True)]
        pivot_cols.append(col)
        pivot_row += 1
        if pivot_row == len(a):
            break
    return tuple(tuple(row) for row in a), tuple(pivot_cols)


def matrix_rank(rows: Sequence[Sequence[Number]]) -> int:
    if not rows:
        return 0
    _, pivots = rref(rows)
    return len(pivots)


def independent_row_basis(rows: Sequence[Sequence[Number]]) -> tuple[Vector, ...]:
    basis: list[Vector] = []
    for row in rows:
        candidate = vec(row)
        if all(entry == 0 for entry in candidate):
            continue
        if matrix_rank([*basis, candidate]) > len(basis):
            basis.append(candidate)
    return tuple(basis)


def nullspace(rows: Sequence[Sequence[Number]], n_cols: int) -> tuple[Vector, ...]:
    if n_cols < 0:
        raise ValueError("n_cols must be nonnegative")
    if not rows:
        return tuple(
            tuple(Fraction(int(i == j)) for i in range(n_cols))
            for j in range(n_cols)
        )
    reduced, pivots = rref(rows, width=n_cols)
    free_cols = [col for col in range(n_cols) if col not in pivots]
    basis: list[Vector] = []
    for free in free_cols:
        vector = [Fraction(0) for _ in range(n_cols)]
        vector[free] = Fraction(1)
        for row_index, pivot_col in enumerate(pivots):
            vector[pivot_col] = -reduced[row_index][free]
        basis.append(tuple(vector))
    return tuple(basis)


def matrix_vector_product(matrix: Matrix, vector: Vector) -> Vector:
    return tuple(sum(row[j] * vector[j] for j in range(len(vector))) for row in matrix)


def bilinear(x: Vector, form: Matrix, y: Vector) -> Fraction:
    fy = matrix_vector_product(form, y)
    return sum(x[i] * fy[i] for i in range(len(x)))


def canonical_line(vector: Sequence[Number]) -> Line:
    v = vec(vector)
    first = next((entry for entry in v if entry != 0), None)
    if first is None:
        raise ValueError("zero vector does not define a line")
    return tuple(entry / first for entry in v)


def line_equal(left: Sequence[Number], right: Sequence[Number]) -> bool:
    return canonical_line(left) == canonical_line(right)


def line_in_span(line: Sequence[Number], basis: Sequence[Sequence[Number]]) -> bool:
    b = independent_row_basis(basis)
    return matrix_rank([*b, vec(line)]) == len(b)


def span_rank(lines: Iterable[Sequence[Number]]) -> int:
    return matrix_rank([vec(line) for line in lines])


def lines_independent(lines: Sequence[Sequence[Number]]) -> bool:
    if not lines:
        return True
    return span_rank(lines) == len(lines)


def gram_matrix(basis: Sequence[Vector], form: Matrix) -> Matrix:
    return tuple(tuple(bilinear(x, form, y) for y in basis) for x in basis)


def ambient_normal(subspace_basis: Sequence[Vector], form: Matrix, ambient_dim: int) -> tuple[Vector, ...]:
    constraints = tuple(matrix_vector_product(form, vector) for vector in subspace_basis)
    return independent_row_basis(nullspace(constraints, ambient_dim))


def intrinsic_normal(
    subspace_basis: Sequence[Vector], realized_span_basis: Sequence[Vector], form: Matrix
) -> tuple[Vector, ...]:
    realized = independent_row_basis(realized_span_basis)
    subspace = independent_row_basis(subspace_basis)
    if not realized:
        return tuple()
    equations: list[Vector] = []
    for s in subspace:
        equations.append(tuple(bilinear(r, form, s) for r in realized))
    coeff_basis = nullspace(equations, len(realized))
    return independent_row_basis(tuple(linear_combination(coeffs, realized) for coeffs in coeff_basis))


def radical(subspace_basis: Sequence[Vector], form: Matrix) -> tuple[Vector, ...]:
    basis = independent_row_basis(subspace_basis)
    if not basis:
        return tuple()
    gram = gram_matrix(basis, form)
    coeff_basis = nullspace(gram, len(basis))
    return independent_row_basis(tuple(linear_combination(coeffs, basis) for coeffs in coeff_basis))


def subspace_is_nondegenerate(subspace_basis: Sequence[Vector], form: Matrix) -> bool:
    basis = independent_row_basis(subspace_basis)
    return matrix_rank(gram_matrix(basis, form)) == len(basis)


def subspace_equal(left: Sequence[Vector], right: Sequence[Vector]) -> bool:
    left_basis = independent_row_basis(left)
    right_basis = independent_row_basis(right)
    if len(left_basis) != len(right_basis):
        return False
    return all(line_in_span(vector, right_basis) for vector in left_basis)


def cyclic_closed(lines: Sequence[Vector], realized_span_basis: Sequence[Vector], form: Matrix) -> bool:
    if len(lines) != 3 or not lines_independent(lines):
        return False
    l1, l2, l3 = lines
    pairs = ((l1, l2, l3), (l2, l3, l1), (l3, l1, l2))
    for left, right, expected in pairs:
        normal = intrinsic_normal((left, right), realized_span_basis, form)
        if len(normal) != 1 or not line_equal(normal[0], expected):
            return False
    return True


def is_orthogonal(left: Vector, right: Vector, form: Matrix) -> bool:
    return bilinear(left, form, right) == 0


def fraction_json(value: Fraction) -> int | str:
    return int(value) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def vector_json(vector: Vector) -> list[int | str]:
    return [fraction_json(entry) for entry in vector]


def basis_json(basis: Sequence[Vector]) -> list[list[int | str]]:
    return [vector_json(vector) for vector in basis]


@dataclass(frozen=True)
class PropertyKind:
    name: str
    arity: int
    bilinear_dependent: bool = False
    zero_bearing: bool = False


@dataclass
class FiniteAxisModel:
    name: str
    axis_applicable: bool
    selected_channels: tuple[str, ...] = ()
    ambient_dim: int = 0
    axis_lines: dict[str, Vector] = field(default_factory=dict)
    bilinear_form: Matrix | None = None
    property_kinds: dict[str, PropertyKind] = field(default_factory=dict)
    property_maps: dict[str, dict[tuple[str, ...], int]] = field(default_factory=dict)
    formal_closure_declared: bool = False
    formal_bilinear_dependent: bool = False
    triadic_declared: bool = False
    subspace_declared: bool = False

    @property
    def rank(self) -> int | None:
        if not self.axis_applicable:
            return None
        return span_rank(tuple(self.axis_lines[channel] for channel in self.selected_channels if channel in self.axis_lines))

    @property
    def formal_bildep(self) -> int:
        return int(self.formal_closure_declared and self.formal_bilinear_dependent)

    @property
    def closure_bildep(self) -> int:
        return int(self.formal_bildep or self.triadic_declared or self.subspace_declared)

    def check_pi(self) -> bool:
        if not self.axis_applicable:
            return True
        return set(self.axis_lines) == set(self.selected_channels)

    def bilinear_property_application_active(self) -> bool:
        for name, kind in self.property_kinds.items():
            if kind.bilinear_dependent and self.property_maps.get(name):
                return True
        return False

    def check_pii(self) -> bool:
        if not self.axis_applicable:
            return True
        antecedent = self.bilinear_property_application_active() or bool(self.formal_bildep)
        return (not antecedent) or self.bilinear_form is not None

    def check_option_typing(self) -> bool:
        if not self.axis_applicable:
            return not (self.formal_closure_declared or self.triadic_declared or self.subspace_declared)
        if (self.triadic_declared or self.subspace_declared) and self.bilinear_form is None:
            return False
        return True

    def realized_span_basis(self) -> tuple[Vector, ...]:
        return independent_row_basis(tuple(self.axis_lines[channel] for channel in self.selected_channels if channel in self.axis_lines))


def construct_pi_countermodel() -> FiniteAxisModel:
    model = FiniteAxisModel(
        name="PI countermodel",
        axis_applicable=True,
        selected_channels=("c",),
        ambient_dim=1,
        axis_lines={},
        property_kinds={"varpi_bil": PropertyKind("varpi_bil", 1)},
    )
    assert not model.check_pi()
    assert model.check_pii()
    assert model.check_option_typing()
    return model


def construct_pii_countermodel() -> FiniteAxisModel:
    model = FiniteAxisModel(
        name="PII countermodel",
        axis_applicable=True,
        selected_channels=("c",),
        ambient_dim=1,
        axis_lines={"c": vec((1,))},
        property_kinds={"varpi_bil": PropertyKind("varpi_bil", 1, bilinear_dependent=True)},
        property_maps={"varpi_bil": {("c",): 1}},
        bilinear_form=None,
    )
    assert model.check_pi()
    assert not model.check_pii()
    assert model.check_option_typing()
    return model


def construct_trivial_and_rank_witnesses() -> dict[str, object]:
    inapplicable = FiniteAxisModel(name="inapplicable", axis_applicable=False)
    rank_zero = FiniteAxisModel(name="rank zero", axis_applicable=True, selected_channels=(), ambient_dim=1)
    rank_one = FiniteAxisModel(
        name="rank one",
        axis_applicable=True,
        selected_channels=("c1",),
        ambient_dim=1,
        axis_lines={"c1": vec((1,))},
    )
    return {
        "rank_inapplicable": inapplicable.rank,
        "rank_zero": rank_zero.rank,
        "rank_one": rank_one.rank,
        "undefined_is_distinct_from_zero": inapplicable.rank is None and rank_zero.rank == 0,
        "rank_one_distinct_pair_domain_empty": len(set(canonical_line(v) for v in rank_one.axis_lines.values())) < 2,
    }


def construct_rank_two_witness() -> tuple[FiniteAxisModel, dict[str, object]]:
    kinds = {
        "varpi_ind": PropertyKind("varpi_ind", 2),
        "varpi_perp": PropertyKind("varpi_perp", 2, bilinear_dependent=True),
        "varpi_cpl": PropertyKind("varpi_cpl", 2, zero_bearing=True),
    }
    maps = {
        "varpi_ind": {("c1", "c2"): 1, ("c2", "c1"): 1},
        "varpi_perp": {("c1", "c2"): 1, ("c2", "c1"): 1},
        "varpi_cpl": {("c1", "c2"): 0, ("c2", "c1"): 0},
    }
    model = FiniteAxisModel(
        name="fully specified relative rank-two witness",
        axis_applicable=True,
        selected_channels=("c1", "c2"),
        ambient_dim=2,
        axis_lines={"c1": vec((1, 0)), "c2": vec((0, 1))},
        bilinear_form=identity(2),
        property_kinds=kinds,
        property_maps=maps,
    )
    span = model.realized_span_basis()
    whole_normal = intrinsic_normal(span, span, model.bilinear_form)
    l1, l2 = model.axis_lines["c1"], model.axis_lines["c2"]
    audit = {
        "rank": model.rank,
        "pi": model.check_pi(),
        "pii": model.check_pii(),
        "option_typing": model.check_option_typing(),
        "canonical_independence": lines_independent((l1, l2)),
        "canonical_orthogonality": is_orthogonal(l1, l2, model.bilinear_form),
        "recorded_independence": maps["varpi_ind"][("c1", "c2")],
        "recorded_orthogonality": maps["varpi_perp"][("c1", "c2")],
        "defined_zero_coupling": maps["varpi_cpl"][("c1", "c2")] == 0,
        "whole_span_intrinsic_normal_dimension": len(whole_normal),
        "formal_bildep": model.formal_bildep,
        "closure_bildep": model.closure_bildep,
    }
    assert audit["rank"] == 2
    assert audit["pi"] and audit["pii"] and audit["option_typing"]
    assert audit["canonical_independence"] and audit["canonical_orthogonality"]
    assert audit["whole_span_intrinsic_normal_dimension"] == 0
    return model, audit


def construct_rank_three_cyclic_witness() -> dict[str, object]:
    lines = (vec((1, 0, 0)), vec((0, 1, 0)), vec((0, 0, 1)))
    form = identity(3)
    span = independent_row_basis(lines)
    pair_normals = {
        "12": intrinsic_normal((lines[0], lines[1]), span, form),
        "23": intrinsic_normal((lines[1], lines[2]), span, form),
        "31": intrinsic_normal((lines[2], lines[0]), span, form),
    }
    return {
        "rank": span_rank(lines),
        "lines_independent": lines_independent(lines),
        "cyclic_closed": cyclic_closed(lines, span, form),
        "pair_normals": {key: basis_json(value) for key, value in pair_normals.items()},
    }


def construct_single_normal_insufficient_witness() -> dict[str, object]:
    lines = (vec((1, 0, 0, 0)), vec((0, 1, 0, 0)), vec((0, 0, 1, 0)), vec((0, 0, 0, 1)))
    form = identity(4)
    span = independent_row_basis(lines)
    normal12 = intrinsic_normal((lines[0], lines[1]), span, form)
    return {
        "rank": span_rank(lines),
        "normal_12": basis_json(normal12),
        "ell3_is_contained_in_normal_12": line_in_span(lines[2], normal12),
        "normal_12_is_one_dimensional": len(normal12) == 1,
        "cyclic_closed_for_123": cyclic_closed(lines[:3], span, form),
    }


def construct_degenerate_radical_witness() -> dict[str, object]:
    form = mat(((1, 0), (0, 0)))
    e2 = vec((0, 1))
    s = (e2,)
    rad = radical(s, form)
    amb = ambient_normal(s, form, 2)
    transverse = line_in_span(e2, amb) and not line_in_span(e2, s)
    return {
        "subspace_dimension": len(independent_row_basis(s)),
        "radical_dimension": len(rad),
        "radical_basis": basis_json(rad),
        "line_is_in_ambient_normal": line_in_span(e2, amb),
        "line_is_transverse": transverse,
        "subspace_nondegenerate": subspace_is_nondegenerate(s, form),
    }


def construct_matrix_size_rank_witness() -> dict[str, object]:
    tags = {
        "t1": vec((1, 0)),
        "t2": vec((0, 1)),
        "t3": vec((1, 1)),
    }
    block = (
        (1, 0, 1),
        (0, 1, 0),
        (1, 0, 1),
    )
    return {
        "tag_count": len(tags),
        "block_size": len(block),
        "realized_rank": span_rank(tuple(tags.values())),
        "block": [list(row) for row in block],
        "block_size_equals_tag_count": len(block) == len(tags),
        "block_size_differs_from_realized_rank": len(block) != span_rank(tuple(tags.values())),
    }


def fixed_channel_value_obstruction(
    left: FiniteAxisModel, right: FiniteAxisModel, property_name: str, key: tuple[str, ...]
) -> bool:
    """Check a necessary strict-isomorphism condition in the displayed fixed fiber.

    The manuscript's full strict-isomorphism relation is more general.  Here the
    Stage-VI channel tuple and property kind are fixed, so differing defined
    values are already sufficient to obstruct strict isomorphism.
    """
    return left.property_maps[property_name][key] != right.property_maps[property_name][key]


def construct_same_rank_different_property_witness() -> dict[str, object]:
    base_lines = {"c1": vec((1, 0, 0)), "c2": vec((0, 1, 0)), "c3": vec((0, 0, 1))}
    kind = PropertyKind("tension", 1)
    left = FiniteAxisModel(
        name="rank-three tension-1",
        axis_applicable=True,
        selected_channels=tuple(base_lines),
        ambient_dim=3,
        axis_lines=dict(base_lines),
        property_kinds={"tension": kind},
        property_maps={"tension": {("c1",): 1}},
    )
    right = FiniteAxisModel(
        name="rank-three tension-2",
        axis_applicable=True,
        selected_channels=tuple(base_lines),
        ambient_dim=3,
        axis_lines=dict(base_lines),
        property_kinds={"tension": kind},
        property_maps={"tension": {("c1",): 2}},
    )
    obstruction = fixed_channel_value_obstruction(left, right, "tension", ("c1",))
    return {
        "left_rank": left.rank,
        "right_rank": right.rank,
        "ranks_equal": left.rank == right.rank,
        "left_value": 1,
        "right_value": 2,
        "strict_value_preservation_obstruction": obstruction,
    }


def construct_same_size_block_obstruction() -> dict[str, object]:
    left = ((1, 0), (0, 1))
    right = ((1, 1), (0, 1))
    return {
        "left_block": [list(row) for row in left],
        "right_block": [list(row) for row in right],
        "same_size": len(left) == len(right) == 2 and all(len(row) == 2 for row in (*left, *right)),
        "one_defined_relation_entry_differs": left[0][1] != right[0][1],
        "representation_inclusive_value_preservation_obstruction": left[0][1] != right[0][1],
    }


def displayed_scalar_summary(rank: int, indicators: Mapping[str, int], weights: Mapping[str, int]) -> int:
    return rank + sum(weights[name] * indicators[name] for name in sorted(indicators))


def construct_scalar_collision_witness() -> dict[str, object]:
    same_rank = construct_same_rank_different_property_witness()
    indicators_left = {"selected_channels": 3, "declared_property_kinds": 1}
    indicators_right = dict(indicators_left)
    weights = {"selected_channels": 10, "declared_property_kinds": 100}
    left_summary = displayed_scalar_summary(same_rank["left_rank"], indicators_left, weights)
    right_summary = displayed_scalar_summary(same_rank["right_rank"], indicators_right, weights)
    return {
        "rank": same_rank["left_rank"],
        "indicators_left": indicators_left,
        "indicators_right": indicators_right,
        "weights": weights,
        "left_summary": left_summary,
        "right_summary": right_summary,
        "same_displayed_summary": left_summary == right_summary,
        "typed_property_value_obstruction": same_rank["strict_value_preservation_obstruction"],
    }


def conditional_rank_three_witness() -> dict[str, object]:
    form = identity(3)
    realized = (vec((1, 0, 0)), vec((0, 1, 0)), vec((0, 0, 1)))
    s = realized[:2]
    normal = intrinsic_normal(s, realized, form)
    return {
        "subspace_dimension": span_rank(s),
        "subspace_nondegenerate": subspace_is_nondegenerate(s, form),
        "intrinsic_normal_dimension": len(normal),
        "realized_span_dimension": span_rank(realized),
        "dimension_sum": span_rank(s) + len(normal),
        "rank_three_conclusion": span_rank(realized) == 3,
    }


def proof_obligation_audit() -> dict[str, object]:
    pi = construct_pi_countermodel()
    pii = construct_pii_countermodel()
    ranks = construct_trivial_and_rank_witnesses()
    _, rank2 = construct_rank_two_witness()
    rank3 = construct_rank_three_cyclic_witness()
    r4 = construct_single_normal_insufficient_witness()
    deg = construct_degenerate_radical_witness()
    matrix_rank_witness = construct_matrix_size_rank_witness()
    rank_property = construct_same_rank_different_property_witness()
    block = construct_same_size_block_obstruction()
    scalar = construct_scalar_collision_witness()
    conditional = conditional_rank_three_witness()

    return {
        "scope": "finite exact witnesses and necessary obstructions only; general theorems remain manuscript proofs",
        "pi_countermodel_verified": (not pi.check_pi()) and pi.check_pii() and pi.check_option_typing(),
        "pii_countermodel_verified": pii.check_pi() and (not pii.check_pii()) and pii.check_option_typing(),
        "primitive_non_derivability_finite_witness_pair_verified": (not pi.check_pi()) and pi.check_pii() and pii.check_pi() and (not pii.check_pii()),
        "undefined_rank_distinct_from_defined_zero_verified": ranks["undefined_is_distinct_from_zero"],
        "rank_two_witness_verified": rank2["rank"] == 2 and rank2["pi"] and rank2["pii"],
        "rank_two_defined_zero_coupling_verified": rank2["defined_zero_coupling"],
        "rank_two_whole_span_normal_zero_dim_verified": rank2["whole_span_intrinsic_normal_dimension"] == 0,
        "rank_three_cyclic_closure_verified": rank3["rank"] == 3 and rank3["cyclic_closed"],
        "single_normal_match_insufficient_verified": r4["ell3_is_contained_in_normal_12"] and not r4["cyclic_closed_for_123"],
        "degenerate_overlap_not_transverse_verified": deg["radical_dimension"] == 1 and not deg["line_is_transverse"],
        "matrix_size_rank_separation_verified": matrix_rank_witness["block_size_differs_from_realized_rank"],
        "same_rank_property_value_obstruction_verified": rank_property["ranks_equal"] and rank_property["strict_value_preservation_obstruction"],
        "same_size_block_value_obstruction_verified": block["same_size"] and block["representation_inclusive_value_preservation_obstruction"],
        "scalar_collision_obstruction_verified": scalar["same_displayed_summary"] and scalar["typed_property_value_obstruction"],
        "conditional_rank_three_witness_verified": conditional["subspace_nondegenerate"] and conditional["intrinsic_normal_dimension"] == 1 and conditional["rank_three_conclusion"],
    }


def build_witness_catalog() -> list[dict[str, object]]:
    pi = construct_pi_countermodel()
    pii = construct_pii_countermodel()
    ranks = construct_trivial_and_rank_witnesses()
    _, rank2 = construct_rank_two_witness()
    rank3 = construct_rank_three_cyclic_witness()
    r4 = construct_single_normal_insufficient_witness()
    deg = construct_degenerate_radical_witness()
    matrix_rank_witness = construct_matrix_size_rank_witness()
    rank_property = construct_same_rank_different_property_witness()
    block = construct_same_size_block_obstruction()
    scalar = construct_scalar_collision_witness()
    conditional = conditional_rank_three_witness()
    return [
        {"witness": "PI countermodel", "claim": "PI false / PII true", "value_1": pi.check_pi(), "value_2": pi.check_pii(), "verified": (not pi.check_pi()) and pi.check_pii()},
        {"witness": "PII countermodel", "claim": "PI true / PII false", "value_1": pii.check_pi(), "value_2": pii.check_pii(), "verified": pii.check_pi() and not pii.check_pii()},
        {"witness": "rank undefined vs zero", "claim": "None != 0", "value_1": ranks["rank_inapplicable"], "value_2": ranks["rank_zero"], "verified": ranks["undefined_is_distinct_from_zero"]},
        {"witness": "rank one", "claim": "rank = 1", "value_1": ranks["rank_one"], "value_2": "distinct-pair-domain-empty", "verified": ranks["rank_one"] == 1 and ranks["rank_one_distinct_pair_domain_empty"]},
        {"witness": "rank two", "claim": "rank = 2 with defined zero coupling", "value_1": rank2["rank"], "value_2": rank2["defined_zero_coupling"], "verified": rank2["rank"] == 2 and rank2["defined_zero_coupling"]},
        {"witness": "rank three cyclic", "claim": "cyclic closure = 1", "value_1": rank3["rank"], "value_2": rank3["cyclic_closed"], "verified": rank3["rank"] == 3 and rank3["cyclic_closed"]},
        {"witness": "single normal insufficient", "claim": "ell3 in normal12 but cyclic false", "value_1": r4["ell3_is_contained_in_normal_12"], "value_2": r4["cyclic_closed_for_123"], "verified": r4["ell3_is_contained_in_normal_12"] and not r4["cyclic_closed_for_123"]},
        {"witness": "degenerate radical", "claim": "nonzero radical not transverse", "value_1": deg["radical_dimension"], "value_2": deg["line_is_transverse"], "verified": deg["radical_dimension"] == 1 and not deg["line_is_transverse"]},
        {"witness": "3x3 block rank separation", "claim": "block size 3 / realized rank 2", "value_1": matrix_rank_witness["block_size"], "value_2": matrix_rank_witness["realized_rank"], "verified": matrix_rank_witness["block_size_differs_from_realized_rank"]},
        {"witness": "same rank different property", "claim": "equal rank / strict value obstruction", "value_1": rank_property["ranks_equal"], "value_2": rank_property["strict_value_preservation_obstruction"], "verified": rank_property["ranks_equal"] and rank_property["strict_value_preservation_obstruction"]},
        {"witness": "same-size blocks", "claim": "same size / encoded value obstruction", "value_1": block["same_size"], "value_2": block["representation_inclusive_value_preservation_obstruction"], "verified": block["same_size"] and block["representation_inclusive_value_preservation_obstruction"]},
        {"witness": "scalar collision", "claim": "same displayed scalar / typed value obstruction", "value_1": scalar["same_displayed_summary"], "value_2": scalar["typed_property_value_obstruction"], "verified": scalar["same_displayed_summary"] and scalar["typed_property_value_obstruction"]},
        {"witness": "conditional rank three", "claim": "2D nondegenerate + 1D intrinsic normal -> rank 3", "value_1": conditional["dimension_sum"], "value_2": conditional["realized_span_dimension"], "verified": conditional["conditional_rank_three_witness_verified"] if "conditional_rank_three_witness_verified" in conditional else conditional["rank_three_conclusion"]},
    ]


def write_outputs(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pi = construct_pi_countermodel()
    pii = construct_pii_countermodel()
    ranks = construct_trivial_and_rank_witnesses()
    _, rank2 = construct_rank_two_witness()
    rank3 = construct_rank_three_cyclic_witness()
    single_normal = construct_single_normal_insufficient_witness()
    degenerate = construct_degenerate_radical_witness()
    matrix_rank_witness = construct_matrix_size_rank_witness()
    rank_property = construct_same_rank_different_property_witness()
    block = construct_same_size_block_obstruction()
    scalar = construct_scalar_collision_witness()
    conditional = conditional_rank_three_witness()
    audit = proof_obligation_audit()

    summary = {
        "paper": "Axioms for the Property Structure of Realized Axes in Dimensional-Structural Describability",
        "author": "Kwon Dominicus",
        "interpretation_boundary": "finite exact witness reproduction; general set-theoretic theorems remain manuscript proofs",
        "primitive_countermodels": {
            "PI_failure_PII_satisfied": {"PI": pi.check_pi(), "PII": pi.check_pii()},
            "PII_failure_PI_satisfied": {"PI": pii.check_pi(), "PII": pii.check_pii()},
        },
        "rank_status_witnesses": ranks,
        "rank_two_witness": rank2,
        "rank_three_cyclic_witness": rank3,
        "single_normal_insufficient_witness": single_normal,
        "degenerate_radical_witness": degenerate,
        "matrix_size_rank_witness": matrix_rank_witness,
        "same_rank_different_property_witness": rank_property,
        "same_size_block_obstruction": block,
        "scalar_collision_witness": scalar,
        "conditional_rank_three_witness": conditional,
        "proof_obligation_audit": audit,
    }

    (output_dir / "axis_property_witness_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "proof_obligation_audit.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    catalog = build_witness_catalog()
    fieldnames = ["witness", "claim", "value_1", "value_2", "verified"]
    with (output_dir / "witness_catalog.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(catalog)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "results",
        help="Directory for deterministic JSON and CSV outputs.",
    )
    args = parser.parse_args()
    summary = write_outputs(args.output_dir)
    print(json.dumps(summary["proof_obligation_audit"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

# Computational proof map

This map states what each executable check supports and what remains a manuscript proof.

| Manuscript result or construction | Executable support | Scope |
|---|---|---|
| PI countermodel | `construct_pi_countermodel()` | Checks the displayed finite model with PI false and PII true |
| PII countermodel | `construct_pii_countermodel()` | Checks the displayed finite model with PI true and PII false |
| Primitive non-derivability | both countermodel constructors | Reproduces the finite witness pair; the metatheoretic admitted-class reading remains the manuscript argument |
| Axis-inapplicable vs rank zero | `construct_trivial_and_rank_witnesses()` | Checks `None` versus defined `0` |
| Rank-one witness | `construct_trivial_and_rank_witnesses()` | Checks the displayed one-line realization and absence of a distinct-line pair |
| Fully specified rank-two witness | `construct_rank_two_witness()` | Checks PI, PII, independence, orthogonality, defined-zero coupling, and whole-span intrinsic normal dimension `0` |
| Rank-three cyclic closure | `construct_rank_three_cyclic_witness()` | Exact rational check for the three coordinate lines of Euclidean `R^3` |
| One normal match insufficient | `construct_single_normal_insufficient_witness()` | Reproduces the `R^4` coordinate-line counterexample |
| Degenerate overlap is not transverse | `construct_degenerate_radical_witness()` | Constructs a nonzero radical in a degenerate two-dimensional bilinear space |
| Conditional rank-three consequence | `conditional_rank_three_witness()` | Checks the displayed finite `2 + 1 = 3` instance, not the general theorem |
| Matrix size does not determine rank | `construct_matrix_size_rank_witness()` | Reproduces a `3 x 3` block with realized rank `2` |
| Equal rank does not imply strict property equivalence | `construct_same_rank_different_property_witness()` | Checks a fixed-channel property-value preservation obstruction, not a general isomorphism decision procedure |
| Equal matrix size does not imply strict equivalence | `construct_same_size_block_obstruction()` | Checks equal `2 x 2` sizes with one preserved encoded-value difference |
| Displayed scalar collision obstruction | `construct_scalar_collision_witness()` | Reproduces one typed collision with equal displayed scalar summary |
| Unique explicit layered completion | none | General set-theoretic theorem remains in the manuscript |
| Primitive reduction/completion inverse laws | none | General theorem remains in the manuscript |
| Strict axis-property equivalence relation | finite necessary obstructions only | Identity/inverse/composition proof remains in the manuscript |
| Stage-VI factorization / Stage-VII independence | none | General theorem remains in the manuscript |
| Finitely specified realization theorem | displayed witnesses only | General sufficiency theorem remains in the manuscript |

The executable package is therefore a reproducibility and proof-audit companion, not a replacement formalization of the axiom system.

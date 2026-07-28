"""Intervention Compiler unit tests (doc06 §5) - real cobrapy GPR
resolution, not a hardcoded hint table.
"""
from __future__ import annotations

from harness import db
from harness.ids import new_id, now
from harness.virtual_cell import compiler
from harness.virtual_cell.models import PerturbationSpec


def _spec(**kwargs) -> PerturbationSpec:
    defaults = dict(
        perturbation_id=new_id("PSPEC"), simulation_case_id="SIMCASE-x", design_version_id="DV-x", type="deletion",
        target="ppc", target_namespace="gene_symbol", biological_intent="", operation="knockout", strength=None,
        implementation="", timing=None, combination_group=None, environmental_changes=[], required_mappings=[],
        assumptions=[], status="pending", created_at=now(),
    )
    defaults.update(kwargs)
    return PerturbationSpec(**defaults)


def test_ppc_knockout_compiles_with_real_gpr_resolved_reaction():
    ci = compiler.compile_intervention(_spec(target="ppc", operation="knockout"), model_id="MREG-gem_fba")
    assert ci.status == "compiled"
    assert ci.resolved_gene_id == "b3956"
    assert ci.affected_reactions == ["PPC"]
    assert ci.new_bounds["PPC"] == {"lower": 0.0, "upper": 0.0}
    assert ci.mapping_status == "direct"


def test_ptsg_knockout_is_an_honest_null_result_not_a_guess():
    """Regression guard against the old hardcoded hint table's wrong claim
    (ptsG knockout fully blocks GLCpts): real GPR resolution shows GLCpts
    has redundant isozyme complexes, so single-gene ptsG knockout affects
    zero reactions - compiled, not rejected, but with no bound change."""
    ci = compiler.compile_intervention(_spec(target="ptsG", operation="knockout"), model_id="MREG-gem_fba")
    assert ci.status == "compiled"
    assert ci.affected_reactions == []
    assert ci.new_bounds == {}
    assert "isozyme" in ci.compilation_log[0]


def test_gene_outside_core_model_is_out_of_domain():
    ci = compiler.compile_intervention(_spec(target="aroG", operation="overexpression"), model_id="MREG-gem_fba")
    assert ci.status == "rejected"
    assert ci.mapping_status == "unsupported"
    assert "not part of" in ci.rejection_reason


def test_unsupported_operation_is_rejected():
    ci = compiler.compile_intervention(_spec(target="ppc", operation="chromosomal_inversion"), model_id="MREG-gem_fba")
    assert ci.status == "rejected"


def test_non_gem_fba_model_id_is_rejected_not_silently_run():
    ci = compiler.compile_intervention(_spec(target="ppc", operation="knockout"), model_id="MREG-vecoli")
    assert ci.status == "rejected"
    assert "no compiler" in ci.rejection_reason


def test_overexpression_scales_bounds_and_records_assumption():
    ci = compiler.compile_intervention(_spec(target="mdh", operation="overexpression"), model_id="MREG-gem_fba")
    assert ci.status == "compiled"
    assert ci.mapping_status == "approximate"
    assert ci.new_bounds["MDH"]["upper"] > ci.original_bounds["MDH"]["upper"]
    assert any("approximated" in a for a in ci.mapping_assumptions)


def test_merge_compiled_bounds_detects_conflicts():
    ci_a = compiler.compile_intervention(_spec(target="ppc", operation="knockout"), model_id="MREG-gem_fba")
    ci_b = compiler.compile_intervention(_spec(target="ppc", operation="overexpression"), model_id="MREG-gem_fba")
    import pytest

    with pytest.raises(ValueError):
        compiler.merge_compiled_bounds([ci_a, ci_b])

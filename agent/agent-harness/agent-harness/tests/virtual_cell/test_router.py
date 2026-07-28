"""Model Router tests (doc06 §4.2) - selection rationale, honest gaps, and
never bypassing the compatibility gate.
"""
from __future__ import annotations

from harness import db
from harness.virtual_cell import router as router_mod


def test_steady_state_question_routes_to_gem_fba_with_rationale():
    with db.session_scope() as s:
        decision = router_mod.route(s, question_type="steady_state_flux")
        assert decision["decision"] == "selected"
        assert decision["selected_model_id"] == "MREG-gem_fba"
        assert decision["rationale"]
        assert decision["coverage_gap"] is None


def test_whole_cell_dynamics_question_has_no_compatible_model():
    with db.session_scope() as s:
        decision = router_mod.route(s, question_type="whole_cell_dynamics")
        assert decision["decision"] == "no_compatible_model"
        assert decision["coverage_gap"]
        reasons = {n["adapter_id"]: n["reason"] for n in decision["not_selected"] if n.get("adapter_id") == "vecoli"}
        assert reasons["vecoli"]


def test_protein_local_property_question_has_no_registered_model_class():
    with db.session_scope() as s:
        decision = router_mod.route(s, question_type="protein_local_property")
        assert decision["decision"] == "no_compatible_model"


def test_unknown_question_type_is_rejected():
    import pytest

    with db.session_scope() as s:
        with pytest.raises(ValueError):
            router_mod.route(s, question_type="not_a_real_question_type")

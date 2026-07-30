"""Round 2 (老师 §Phase2): `project_context_summary` is the one normalized
read entry point for "Current Project Context" - replaces the duplicated
`(project.host_definition or {}).get("species") or .get("host")` that used
to live separately in `harness/api/generation.py` and
`harness/evidence_retrieval/service.py`.
"""
from __future__ import annotations

from harness import db
from harness.projects import service as proj_svc


def _make_project(**overrides):
    with db.session_scope() as s:
        kwargs = {
            "name": "t", "host_definition": {"species": "E. coli", "strain": "K-12"},
            "target_product": "L-tryptophan", "actor_id": "pi",
        }
        kwargs.update(overrides)
        p = proj_svc.create_project(s, **kwargs)
        return p.project_id


def test_summary_reads_species_and_strain():
    with db.session_scope() as s:
        p = proj_svc.get_project(s, _make_project())
        ctx = proj_svc.project_context_summary(p)
        assert ctx["host"] == "E. coli"
        assert ctx["strain"] == "K-12"
        assert ctx["target_product"] == "L-tryptophan"


def test_summary_falls_back_to_legacy_host_key():
    with db.session_scope() as s:
        p = proj_svc.get_project(s, _make_project(host_definition={"host": "E. coli B"}))
        ctx = proj_svc.project_context_summary(p)
        assert ctx["host"] == "E. coli B"
        assert ctx["strain"] is None


def test_summary_never_fabricates_missing_host():
    with db.session_scope() as s:
        p = proj_svc.get_project(s, _make_project(host_definition={}))
        ctx = proj_svc.project_context_summary(p)
        assert ctx["host"] is None
        assert ctx["strain"] is None

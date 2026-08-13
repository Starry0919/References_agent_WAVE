"""Component 1 - `EvidenceObject` projection tests. Uses the real, shipped
`knowledge/ddr_database/DDR-001_tryptophan.json` record (not a fixture
stand-in) so a regression in the actual corpus or in `ddr_converter`'s
step shape would be caught here too."""
from __future__ import annotations

from sqlalchemy.orm import Session

from harness import db
from harness.diagnosis.evidence import link_evidence, record_evidence_item
from harness.evidence_intelligence import adapters
from harness.evidence_retrieval.local_ddr_adapter import LocalDDRAdapter


def _ddr001_step(step_no: int) -> tuple[str, dict, dict]:
    doc = LocalDDRAdapter().fetch("DDR-001")
    assert doc is not None
    rec = doc.raw_metadata
    step = next(s for s in rec["decision_chain"] if s["step"] == step_no)
    return "DDR-001", step, rec["metadata"]


def test_from_ddr_decision_step_never_fabricates_host_or_product():
    ddr_id, step, meta = _ddr001_step(1)
    obj = adapters.from_ddr_decision_step(ddr_id, step, meta)

    assert obj.evidence_id == "ddr:DDR-001:1"
    assert obj.host == "Escherichia coli"
    assert obj.product == "L-tryptophan"
    assert obj.evidence_grading == "硬"
    # step 1's reason_nature is 机理推断 -> mechanistic hypothesis per the char. mapping
    assert obj.evidence_type == "mechanistic hypothesis"
    assert obj.evidence_origin == "published experiment"
    assert obj.claim  # non-empty: falls back through rule -> trigger.observation -> evidence.description
    assert obj.confidence_level in ("Medium", "High")  # 硬 grade, no per-step calibration_status recorded -> Medium
    assert obj.applicability_boundary  # never empty - always at least an explicit "unknown" note
    assert obj.limitations
    assert obj.review.reviewable_via == "POST /api/paper-extraction/ddr/DDR-001/attempts"


def test_from_ddr_decision_step_soft_evidence_flags_low_confidence():
    ddr_id, step, meta = _ddr001_step(2)
    # step 2 is graded 硬 in the real record; force a soft-graded synthetic
    # step to prove the Low-confidence path without inventing a fake DDR.
    soft_step = {**step, "evidence_grading": "软", "evidence": {"source": "OptKnock 预测", "description": "predicted knockout effect"}}
    obj = adapters.from_ddr_decision_step(ddr_id, soft_step, meta)
    assert obj.confidence_level == "Low"
    assert obj.evidence_origin == "model prediction"
    assert obj.evidence_type == "simulation prediction"
    assert any("软证据" in lim or "prediction" in lim.lower() for lim in obj.limitations)


def test_from_ddr_decision_step_unknown_ddr_id_is_caller_responsibility():
    # adapters.py is a pure projection - it trusts the caller already
    # resolved the record; service.get_evidence_object is what 404s.
    ddr_id, step, meta = _ddr001_step(3)
    obj = adapters.from_ddr_decision_step(ddr_id, step, {})
    assert obj.host is None and obj.product is None  # no metadata -> honestly unknown, never guessed


def _make_project(session: Session) -> str:
    from harness.projects.service import create_project

    project = create_project(session, name="t", host_definition={"species": "Escherichia coli"}, target_product="L-tryptophan", actor_id="tester")
    return project.project_id


def test_from_diagnosis_evidence_item_without_link():
    with db.session_scope() as session:
        project_id = _make_project(session)
        item = record_evidence_item(
            session, project_id=project_id, source_type="literature", content_summary="terminal enzyme overexpression did not raise titer",
            actor_id="tester", quality="high", directness="direct", organism="Escherichia coli", intervention="overexpress trpE",
        )
        session.flush()
        obj = adapters.from_diagnosis_evidence_item(item, None)

        assert obj.evidence_id == f"diag:{item.evidence_item_id}"
        assert obj.confidence_level == "High"
        assert obj.evidence_origin == "published experiment"
        assert obj.evidence_type == "direct engineering validation"
        assert obj.product is None  # EvidenceItem has no product field - never fabricated
        assert obj.review.status == "not_linked_to_a_hypothesis"
        assert "not yet linked" in obj.review.note or "never gates" in obj.review.note


def test_from_diagnosis_evidence_item_with_link_prefers_link_claim_and_limitations():
    with db.session_scope() as session:
        project_id = _make_project(session)
        item = record_evidence_item(
            session, project_id=project_id, source_type="model_run", content_summary="FBA predicted flux increase",
            actor_id="tester", quality="low", directness="indirect",
        )
        session.flush()

        from harness.learning import service as learning_svc

        fam = learning_svc.create_hypothesis_family(session, project_id=project_id, title="precursor supply bottleneck")
        hyp = learning_svc.propose_hypothesis(
            session, project_id=project_id, hypothesis_family_id=fam.hypothesis_family_id,
            statement="precursor supply is the bottleneck", actor_id="tester",
        )

        link = link_evidence(
            session, hypothesis_version_id=hyp.hypothesis_version_id, evidence_item_id=item.evidence_item_id,
            relation="supports", actor_id="tester", claim="precursor supply limits titer", condition_match="matched",
            limitations="only one biological replicate",
        )
        obj = adapters.from_diagnosis_evidence_item(item, link)

        assert obj.claim == "precursor supply limits titer"
        assert "only one biological replicate" in obj.limitations
        assert obj.review.status == "matched"
        assert obj.review.reviewable_via == f"POST /api/diagnosis/evidence-links/{link.evidence_link_id}/review"
        assert obj.confidence_level == "Low"  # quality=low on the underlying item, never upgraded by the link

"""Component 4 - Engineering Provenance Graph tests. `ddr` anchors use the
real shipped corpus/rule library; `strategy`/`candidate` anchors construct
minimal-but-real `EngineeringDesignProject`/`EngineeringStrategy`/
`CandidateDesign` rows directly (SQLite FK enforcement is on -
`harness/db.py` sets `PRAGMA foreign_keys=ON` - so the parent rows must be
real, even though this test doesn't run the full diagnosis->design
pipeline that would normally produce them)."""
from __future__ import annotations

from harness import db
from harness.engineering_design.models import CandidateDesign, EngineeringDesignProject, EngineeringStrategy
from harness.evidence_intelligence.provenance_graph import build_engineering_provenance_graph
from harness.ids import new_id, now
from harness.projects.service import create_project


def test_ddr_anchor_includes_paper_and_evidence_object_nodes_for_every_step():
    graph = build_engineering_provenance_graph("ddr", "DDR-001")
    assert graph is not None
    assert graph.anchor == {"anchor_type": "ddr", "anchor_id": "DDR-001"}

    kinds = {n.kind for n in graph.nodes}
    assert "paper" in kinds
    assert "evidence_object" in kinds
    evidence_ids = {n.ref.get("evidence_id") for n in graph.nodes if n.kind == "evidence_object"}
    assert {"ddr:DDR-001:1", "ddr:DDR-001:2", "ddr:DDR-001:3"} <= evidence_ids

    # RULE-001 and RULE-004 both cite DDR-001 in the real rule library.
    rule_ids = {n.ref.get("rule_id") for n in graph.nodes if n.kind == "mechanistic_rule"}
    assert {"RULE-001", "RULE-004"} <= rule_ids

    # every evidence_object -> paper edge exists (reported_in)
    paper_node_id = next(n.id for n in graph.nodes if n.kind == "paper")
    reported_edges = {(e.source, e.target) for e in graph.edges if e.relation == "reported_in"}
    assert ("evidence:DDR-001:1", paper_node_id) in reported_edges


def test_ddr_anchor_unknown_ddr_returns_none():
    assert build_engineering_provenance_graph("ddr", "DDR-does-not-exist") is None


def test_invalid_anchor_type_raises():
    import pytest

    with pytest.raises(ValueError):
        build_engineering_provenance_graph("nonsense", "X")


def _make_design_project(session) -> str:
    project = create_project(session, name="t", host_definition={"species": "Escherichia coli"}, target_product="L-tryptophan", actor_id="tester")
    design_project = EngineeringDesignProject(
        design_project_id=new_id("DESPROJ"), project_id=project.project_id, diagnosis_session_id=new_id("DIAG"),
        diagnosis_decision_id=new_id("DECN"), diagnosis_version=1, created_by="tester", created_at=now(), updated_at=now(),
    )
    session.add(design_project)
    session.flush()
    return design_project.design_project_id


def test_strategy_anchor_walks_evidence_links_to_a_ddr_via_curated_knowledge_action():
    with db.session_scope() as session:
        design_project_id = _make_design_project(session)
        # ACT-005 (knowledge/engineering_actions/action_database.json) cites
        # DDR-003 in its own `evidence` field - a real curated-knowledge ->
        # paper resolution, not a fixture stand-in.
        strategy = EngineeringStrategy(
            strategy_id=new_id("STRAT"), design_project_id=design_project_id, diagnosis_reference="HANDOFF-1",
            engineering_objective="increase precursor supply", mechanism_target="PEP/E4P availability",
            strategy_class="pathway_engineering", evidence_links=[{"source_type": "curated_knowledge", "reference": "ACT-005", "detail": ""}],
            created_by="tester", created_at=now(),
        )
        session.add(strategy)
        session.flush()

        graph = build_engineering_provenance_graph("strategy", strategy.strategy_id, session=session)
        assert graph is not None
        kinds = {n.kind for n in graph.nodes}
        assert "engineering_strategy" in kinds
        assert "paper" in kinds  # merged in from build_ddr_subgraph("DDR-003")
        strategy_node_id = f"strategy:{strategy.strategy_id}"
        assert any(e.source == strategy_node_id and e.relation == "supported_by" for e in graph.edges)


def test_strategy_anchor_diagnosis_hypothesis_link_becomes_an_evidence_object_node():
    with db.session_scope() as session:
        design_project_id = _make_design_project(session)
        strategy = EngineeringStrategy(
            strategy_id=new_id("STRAT"), design_project_id=design_project_id, diagnosis_reference="HANDOFF-1",
            engineering_objective="reduce competing flux", mechanism_target="pykF",
            strategy_class="flux_redistribution", evidence_links=[{"source_type": "diagnosis_hypothesis", "reference": "HYPV-abc123", "detail": "precursor bottleneck hypothesis"}],
            created_by="tester", created_at=now(),
        )
        session.add(strategy)
        session.flush()

        graph = build_engineering_provenance_graph("strategy", strategy.strategy_id, session=session)
        assert graph is not None
        hyp_nodes = [n for n in graph.nodes if n.ref.get("kind") == "diagnosis_hypothesis"]
        assert len(hyp_nodes) == 1
        assert hyp_nodes[0].ref["hypothesis_version_id"] == "HYPV-abc123"


def test_strategy_anchor_unresolved_link_is_reported_not_fabricated():
    with db.session_scope() as session:
        design_project_id = _make_design_project(session)
        strategy = EngineeringStrategy(
            strategy_id=new_id("STRAT"), design_project_id=design_project_id, diagnosis_reference="HANDOFF-1",
            engineering_objective="x", mechanism_target="y", strategy_class="other",
            evidence_links=[{"source_type": "curated_knowledge", "reference": "ACT-does-not-exist", "detail": ""}],
            created_by="tester", created_at=now(),
        )
        session.add(strategy)
        session.flush()

        graph = build_engineering_provenance_graph("strategy", strategy.strategy_id, session=session)
        assert graph is not None
        assert graph.unresolved  # the missing action must be reported, not silently dropped
        assert any("ACT-does-not-exist" in u or "no such curated-knowledge action" in u for u in graph.unresolved)


def test_candidate_anchor_chains_decision_to_strategy():
    with db.session_scope() as session:
        design_project_id = _make_design_project(session)
        strategy = EngineeringStrategy(
            strategy_id=new_id("STRAT"), design_project_id=design_project_id, diagnosis_reference="HANDOFF-1",
            engineering_objective="increase precursor supply", mechanism_target="PEP/E4P",
            strategy_class="pathway_engineering", evidence_links=[], created_by="tester", created_at=now(),
        )
        session.add(strategy)
        session.flush()

        candidate = CandidateDesign(
            design_id=new_id("CAND"), design_project_id=design_project_id, lineage_id=new_id("LIN"),
            strategy_ids=[strategy.strategy_id], expected_mechanism="knock out ptsG to spare PEP",
            source_diagnosis_version=1, proposed_by="tester", created_at=now(),
        )
        session.add(candidate)
        session.flush()

        graph = build_engineering_provenance_graph("candidate", candidate.design_id, session=session)
        assert graph is not None
        kinds = {n.kind for n in graph.nodes}
        assert {"engineering_decision", "engineering_strategy"} <= kinds
        decision_node_id = f"decision:{candidate.design_id}"
        strategy_node_id = f"strategy:{strategy.strategy_id}"
        assert any(e.source == decision_node_id and e.target == strategy_node_id and e.relation == "implements" for e in graph.edges)


def test_candidate_anchor_unknown_design_returns_none():
    with db.session_scope() as session:
        assert build_engineering_provenance_graph("candidate", "CAND-does-not-exist", session=session) is None


def test_strategy_or_candidate_anchor_without_session_raises():
    import pytest

    with pytest.raises(ValueError):
        build_engineering_provenance_graph("strategy", "STRAT-1", session=None)

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from harness.bootstrap import Base
from harness.world_model.entities import get_or_create_entity, list_entities
from harness.world_model.state_transition_graph import build_state_transition_graph
from harness.world_model.transitions import InvalidTransitionContext, list_transitions, record_state_transition


def _session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


CONTEXT = {
    "host": "Escherichia coli K-12", "strain": "MG1655", "medium": "M9",
    "carbon_source": "glucose", "oxygen_condition": "aerobic",
    "growth_phase": "exponential",
    "engineering_objective": "improve tryptophan production while maintaining growth",
}


def test_entity_registry_is_idempotent():
    with _session() as session:
        first = get_or_create_entity(session, entity_type="gene", name="trpE", canonical_id="b1264", namespace="EcoCyc", source="manual", actor_id="reviewer")
        second = get_or_create_entity(session, entity_type="gene", name="trpE", canonical_id="b1264", namespace="EcoCyc", source="manual", actor_id="reviewer", aliases=["anthranilate synthase component I"])
        assert first.entity_id == second.entity_id
        assert len(list_entities(session, query="trpE")) == 1


def test_transition_requires_complete_supported_context_and_provenance():
    with _session() as session:
        bad = {**CONTEXT, "host": "Saccharomyces cerevisiae"}
        try:
            record_state_transition(session, initial_state={"summary": "A"}, perturbation={"type": "deletion"}, final_state={"summary": "B"}, context=bad, origin="experimental", evidence_id="diag:E1", actor_id="reviewer")
        except InvalidTransitionContext:
            pass
        else:
            raise AssertionError("unsupported host was accepted")


def test_nonexperimental_transition_cannot_be_validated_and_graph_is_queryable():
    with _session() as session:
        row = record_state_transition(
            session, initial_state={"summary": "baseline", "entities_involved": []},
            perturbation={"type": "overexpression", "target": "trpE"},
            final_state={"summary": "observed tryptophan increase", "entities_involved": []},
            context=CONTEXT, origin="literature_inferred", evidence_id="ddr:DDR-001:1",
            status="inferred", outcome="success", uncertainty={"level": "unknown"}, actor_id="reviewer",
        )
        assert list_transitions(session, host="Escherichia coli K-12")[0].transition_id == row.transition_id
        graph = build_state_transition_graph(session)
        assert len(graph.nodes) == 2
        assert graph.edges[0].status == "inferred"

"""Module 2 (Engineering Decision Intelligence Layer) §7: real `Observation.
modality` rows must reach the persisted `HypothesisVersion.scope.omics_layers`
via the orchestrator's diagnosis adapter - not just the pure
`hypothesis_generator` unit level (covered separately in
`tests/diagnosis/test_mechanism_and_hypotheses.py`).
"""
from __future__ import annotations

from sqlalchemy import select

from harness import db
from harness.learning.models import HypothesisVersion
from harness.orchestrator.service import UnifiedScientificWorkflowOrchestrator
from harness.projects import service as proj_svc
from tests.orchestrator.conftest import grounded_request

ORC = UnifiedScientificWorkflowOrchestrator()
_SUFFICIENT = {"has_baseline": True, "has_genotype": True, "has_condition": True, "has_time": True, "has_qc": True, "has_key_phenotype": True}


def test_typed_observations_produce_persisted_omics_layers():
    with db.session_scope() as s:
        proj = proj_svc.create_project(
            s, name="Multi-omics Trp", host_definition={"species": "E. coli", "strain": "K-12"},
            target_product="L-tryptophan", actor_id="pi",
        )
        project_id = proj.project_id

    with db.session_scope() as s:
        run = ORC.create_run(s, project_id=project_id, actor_id="pi", target_product="L-tryptophan", host="E. coli K-12")
        run_id = run.workflow_run_id

    with db.session_scope() as s:
        ORC.start_diagnosis(
            s, run_id, expected_version=1, actor_id="agent",
            request=grounded_request(s, project_id, {
                "biological_system": {"species": "E. coli", "strain": "K-12"},
                "phenotype": "L-tryptophan titer plateaus below target",
                "target_product": "L-tryptophan", "host": "E. coli K-12", "data_sufficiency": _SUFFICIENT,
            }, modalities=[("transcriptomic", "mRNA:trpE"), ("unknown", "misc")]),
            context={"medium": "M9", "carbon_source": "glucose"},
        )

    with db.session_scope() as s:
        hypotheses = list(s.execute(
            select(HypothesisVersion).where(HypothesisVersion.mechanism_class == "biological_mechanism")
        ).scalars())
        assert hypotheses, "expected at least one biological_mechanism hypothesis for a matched DDR product"
        for h in hypotheses:
            assert h.scope.get("omics_layers") == ["transcriptomic"], (
                "the untyped observation must never contribute a layer, and the real modality must be honestly reflected"
            )

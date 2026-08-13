"""Module 3: Evidence Intelligence Infrastructure.

A thin, read-side aggregation layer over evidence that already lives in
this repository - `harness.diagnosis.models.EvidenceItem`/`EvidenceLink`
(Problem 03's wet-lab/literature evidence table) and
`knowledge/ddr_database/*.json` `decision_chain[i].evidence` (the
paper_extraction/DDR pipeline's per-paper evidence field group). It answers
"why should this information be trusted?" without owning biological
reasoning (that stays in `harness.diagnosis`/`harness.engineering_design`)
and without replacing DDR (that stays the authoritative record of approved
engineering decisions).

This package intentionally has NO new SQLAlchemy tables and writes nothing
to `project_ledger.db` or `knowledge/ddr_database/`: every function here is
a pure projection/aggregation over data other packages already own and
persist. See `harness/evidence_intelligence/models.py` for why (mirrors
`harness.paper_extraction.rule_distillation.rule_as_knowledge_claim_view`'s
"read-only view over existing data, not a new claim object" precedent).

Components (per the Module 3 prompt):
  1. `models.py`          - the `EvidenceObject` shape + confidence vocabulary.
  2. `retrieval.py`       - `EngineeringContextQuery` + engineering-aware search.
  3. `characterization.py`- categorical confidence/applicability/uncertainty derivation.
  4. `adapters.py`        - projects EvidenceItem / DDR decision_chain steps into EvidenceObject.
  5. `provenance_graph.py`- Engineering Decision -> Strategy -> Rule -> Evidence -> Experiment -> Paper.
  6. `service.py`         - the facade `harness/api/evidence_intelligence.py` calls.
"""

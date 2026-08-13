# Reference Optimization Acceptance Matrix — 2026-08-12

| Requirement | Implementation | Test | Result | Evidence path |
|---|---|---|---|---|
| Route before experiment extraction | `LiteratureExecutionPlan` constructed before model/cache/extractor | real paper replay + route tests | PASS | `harness/paper_extraction/execution_plan.py`, `opus_extractor.py` |
| SynBioGPT2 no fake wet-lab object | Benchmark route, zero model calls, empty experiments | real clean-document replay | PASS | `tests/reference_optimization/test_contracts_and_replay.py` |
| ELISER no fake strain experiment | Resource route, historical-prior-only downstream | real clean-document replay | PASS | `tests/reference_optimization/test_contracts_and_replay.py` |
| Primary experimental is not killed | Primary route permits ExperimentInstance | route + extractor regression | PASS | `test_routing_and_quantitative.py`, `test_unified_extraction.py` |
| Quantitative roles do not cross fields | Typed role classifier and projection assertion | five semantic cases | PASS for typed path | `harness/paper_extraction/quantitative_roles.py` |
| All legacy numeric projections guarded | Integrate role object everywhere | not complete | PARTIAL | — |
| Observation belongs to project/QC/provenance/context/baseline | Existing mandatory grounding gate | grounding + repaired engineering fixture | PASS | `harness/diagnosis/grounding.py` |
| Immutable DiagnosisFinding | Strict creation from problem+hypothesis+observations | schema/service tests | PASS | `harness/diagnosis/findings.py`, `models.py` |
| Every candidate requires finding | Candidate linkage field exists | selected tests only | PARTIAL | `harness/engineering_design/models.py` |
| Generated cannot jump to selected/build | Explicit state graph | illegal-transition test | PASS through new service | `decision_state.py` |
| All legacy status changes use state graph | Legacy services retained | not complete | PARTIAL | `governance_service.py`, `build_test_planner.py` |
| Candidate/product/condition-specific FBA | Four real solves + FVA + persistence | cobrapy replay | PASS | `model_evaluation.py`, `_cobrapy_fba_base.py` |
| Truthful model identity | Reports internal iJO1366, legacy filename in provenance | FBA assertion | PASS | `gem_fba_iml1515.py` |
| Dynamic EvidenceNeed | Typed gap/source, retrieve, accept/reject, stop audit | integration test | PASS (MVP) | `dynamic_loop.py` |
| Claim/hypothesis state update after retrieval | Interface not yet linked | none | PARTIAL | — |
| Section-aware hybrid retrieval | Authority-weighted lexical + dense RRF | authority ranking test | PASS (MVP) | `hybrid.py` |
| ELISER prior isolated from evidence/recommendation | Separate four dimensions | prior test | PASS (MVP) | `historical_prior.py` |
| Full ELISER import/promotion | Not attempted | none | PARTIAL | — |
| Technical failure excluded from biological learning | Canonical failure taxonomy exclusion | biological + measurement pair | PASS | `failure_recall.py` |
| Negative result changes future ranking | Penalty output changes rank input | recall/penalty test | PARTIAL | `failure_recall.py` |
| Benchmark V2 contract | Eight axes and non-fake temporal holdout rules | schema test | PASS (schema) | `scientific_benchmark_v2.py` |
| Artifact hash/data dictionary/migration | Release manifest | contract test | PASS | `release_contract.py` |
| Frontend source labels | Route-safe adapter contract | adapter test | PASS (contract) | `frontend_adapter.py` |
| Full frontend scientific-state UI | Not implemented | none | PARTIAL | — |
| Relevant regression | 70 affected tests | pytest | PASS | test output recorded in implementation report |
| Full backend regression | Attempted; timed out with legacy failures | pytest | FAIL / BLOCKER | implementation report Regression section |

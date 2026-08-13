# Module 3: Evidence Intelligence Infrastructure

## Architecture review

### Existing architecture

- `harness/diagnosis/models.py` owns project-scoped `EvidenceItem` and `EvidenceLink` records.
- `knowledge/ddr_database/*.json` and `harness/paper_extraction/` own paper-derived DDR decision chains, calibration, and provenance.
- `harness/evidence_retrieval/` already provides DDR retrieval, condition matching, DOI verification, and categorical hard/soft evidence grading.
- `harness/knowledge_distillation/` owns reusable rule and knowledge representations.
- `harness/engineering_design/` owns strategies and candidate decisions. DDR remains the authoritative decision record.
- Existing diagnosis evidence review and DDR calibration are the human-governance mechanisms; Module 3 does not introduce approval state.
- The orchestrator and project ledger preserve the DBTL links between diagnosis, design, simulation, experiment, evaluation, and learning.

### Integration decision

Module 3 is an additive, read-only aggregation layer. It projects existing diagnosis evidence and DDR steps into a common `EvidenceObject`, searches those authoritative sources using engineering fields, characterizes them categorically, and builds decision-oriented provenance graphs. It adds no database table and performs no evidence or approval writes.

### Compatibility risks and controls

- Legacy evidence shapes differ: adapters expose missing values as `null`, `Unknown`, or an explicit limitation; they never infer absent metadata.
- DDR records do not have a distinct experiment entity: provenance returns an `unresolved` explanation instead of fabricating an experiment node.
- Existing applicability code contains a legacy numeric confidence field. Module 3 does not consume or expose it; its confidence vocabulary is categorical only.
- Rule-to-step linkage is exact-text only. When exact resolution is impossible, provenance links at paper level and records the unresolved hop.
- Review remains delegated to existing diagnosis review and DDR calibration endpoints.

## Updated architecture and data flow

```text
Engineering problem/context
  -> engineering-aware retrieval (host, product, objective, bottleneck,
     intervention, experimental context, optional text)
  -> EvidenceObject projections (diagnosis EvidenceItem or DDR step)
  -> categorical characterization
  -> engineering provenance graph
  -> existing human review/calibration pointers
  -> diagnosis / engineering design / DDR (unchanged owners)
```

Module 1 continues to answer how similar problems were solved. Module 2 continues to reason and decide. Module 3 answers where supporting information came from, its applicability, and its limitations.

## Schema documentation

### `EvidenceObject`

| Field | Source | Purpose | Example |
|---|---|---|---|
| `evidence_id` | Adapter-generated stable view ID | Resolve the source view | `ddr:DDR-001:2` |
| `claim` | Evidence link claim or DDR rule/observation | Supported engineering statement | `Deleting gene X improves production` |
| `source` | Source reference or DDR step | Human-readable origin | `DDR-001 decision_chain step 2` |
| `evidence_origin` | Existing source type/content | Distinguish experiment, simulation, model, expert, or literature analysis | `published experiment` |
| `evidence_type` | Existing directness/grading | Nature of support | `direct engineering validation` |
| `host`, `product` | Stored organism/DDR metadata | Engineering transfer context | `E. coli`, `succinate` |
| `engineering_intervention` | Stored intervention/implementation | Engineering action tested | `gene knockout` |
| `experimental_context` | Stored condition, time, target, trigger | Conditions under which evidence arose | `{"condition":{"medium":"M9"}}` |
| `result` | Stored measurement/direction/effect or DDR result | Observed or predicted outcome | `{"direction":"increase"}` |
| `applicability_boundary` | Recorded host/strain/product/condition and match status | Explicit transfer boundary | `host: E. coli` |
| `limitations` | Recorded uncertainty, extraction/calibration state, missing quantification | Known uncertainty | `only one condition recorded` |
| `confidence_level` | Categorical mapping from existing grading/quality/directness/calibration | Trust communication without arbitrary score | `Medium` |
| `confidence_basis` | Same existing signals | Explain the category | `hard evidence pending calibration` |
| `origin_kind`, `origin_ref` | Authoritative source IDs | Trace back to the real record | `ddr_decision_step` |
| `review` | Existing review/calibration route and status | Integrate human governance without duplicating it | `pending` |

Allowed confidence levels are exactly `High`, `Medium`, `Low`, and `Unknown`.

### `EngineeringContextQuery`

Optional fields are `host`, `product`, `objective`, `bottleneck`, `intervention_type`, `experimental_context`, and `free_text`. Structured fields filter first; free text supplements rather than replaces engineering context.

### `ProvenanceGraph`

The graph contains typed nodes (`engineering_decision`, `engineering_strategy`, `mechanistic_rule`, `evidence_object`, `experiment`, `paper`), directed labeled edges, an anchor, and an `unresolved` list. Missing hops are disclosed, never invented.

## API

- `GET /api/evidence-intelligence/evidence/{evidence_id}` returns one object plus characterization.
- `GET /api/evidence-intelligence/search` accepts engineering-context filters and optional project scope.
- `GET /api/evidence-intelligence/provenance-graph?anchor_type=ddr|strategy|candidate&anchor_id=...` returns the traceability graph.

## Frontend integration

The Trust Center retains its existing DDR summary and review flow, adds the engineering provenance graph, and resolves graph evidence nodes into side-by-side evidence cards for inspection and comparison. The cards expose origin, type, source, intervention, categorical confidence, applicability boundary, uncertainty, and limitations.

## Validation report

Automated coverage includes adapters, categorical characterization, structured retrieval, provenance construction, API routing, missing-data behavior, and confidence-vocabulary guards. Validation commands:

```text
python -m compileall -q harness/evidence_intelligence harness/api/evidence_intelligence.py
pytest -q tests -k evidence_intelligence
cd frontend && npm run build
```

Current limitations:

- DDR schema needs a future first-class experiment identifier to complete the experiment provenance tier.
- Product/objective/bottleneck are not fields on legacy diagnosis `EvidenceItem`; retrieval does not claim those dimensions were checked.
- Rule-to-DDR-step resolution should eventually use stable source-step IDs rather than exact statement text.
- A future validated statistical model could augment categorical confidence, but no numeric confidence is currently generated by Module 3.


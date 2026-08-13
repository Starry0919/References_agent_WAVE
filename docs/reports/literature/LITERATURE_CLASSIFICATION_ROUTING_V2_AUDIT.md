# Literature Classification and Routing v2 Audit

## Scope

The implementation is confined to literature discovery, classification, ranking, routing, acquisition decisions, search-result contracts, benchmarks, and tests. DDR, Skill07, Skill08, knowledge graphs, and downstream agents were not changed.

## Before

Candidates exposed metadata relevance, a single publication type, review flag, acquisition state, and relevance-only ordering. Formal Gold status was represented by a separate monolithic verification admission result.

## After

- Additive `literature-search-result/2.0` candidate fields preserve backward compatibility.
- Six independent multi-label scientific axes carry confidence, evidence source/location, and concise reason codes.
- Metadata classification may be refined by full text without deleting metadata provenance.
- Conflicts are explicit and route to manual review.
- Classification drives ranking, filtering, diversity, acquisition priority, and downstream handoff type.
- Functional literature readiness is independent of formal Gold calibration.
- Automatic knowledge admission remains conservative and DDR writes remain disabled.

No chain-of-thought is stored. Classification is deterministic and batch-capable; source failures remain isolated by the existing discovery service.


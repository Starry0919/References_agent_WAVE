# Skill07 Gold Schema

Machine schemas are in `benchmarks/skill07_human_gold/schemas/` for Experiment, Claim and Evidence, version 1.0.0.

Stable IDs originate from benchmark/source identity: `GOLD-Pxx-Eyyy`, `...-Czzz`, `...-Vzzz`; candidate IDs may only appear in comparison metadata. Tiers progress from UNANNOTATED/SILVER_CANDIDATE to HUMAN_DRAFT, HUMAN_REVIEWED, ADJUDICATED_GOLD and FROZEN_GOLD. Deterministic or model output cannot satisfy human tiers.

Experiment granularity and relations are first class. Biological objects preserve host/strain/genotype/construct/role. Claims preserve epistemic status, value role and criticality. Evidence preserves locator correctness, support strength/directness, availability and multi-anchor scope.

Validator gates: G0 identity, G1 source coverage, G2 structure/granularity, G3 claims, G4 evidence, G5 epistemic integrity, G6 human review/adjudication, G7 auditability. Explicit blocker codes are returned.

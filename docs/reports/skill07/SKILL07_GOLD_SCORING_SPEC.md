# Skill07 Frozen-Gold Scoring Specification

Candidate scoring accepts only a verified frozen release. Alignment uses scientific content, not experiment IDs, and accepts explicit one-to-one/one-to-many/many-to-one granularity maps. Ambiguous candidates remain unresolved. Metrics expose exact numerators/denominators for experiment recall/precision, omissions, spurious items, granularity and unresolved alignment; adjudicated atomic claims/evidence supply field, claim and evidence metrics.

Hard gates are non-compensatory: critical experiment/evidence omission, wrong binding, unsupported mechanism, provenance regression, result inversion, trigger/action corruption or schema reliability regression prevents non-inferiority. `UNCERTAIN` Gold is excluded unless a frozen policy explicitly scores it. Token/latency cannot offset a hard failure.

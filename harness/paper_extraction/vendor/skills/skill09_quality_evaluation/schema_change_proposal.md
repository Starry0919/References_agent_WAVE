# Unified schema change proposal

No framework file is modified. The existing `qualityEvaluation` object remains the interoperable core. A future schema version may add optional `evaluation_report` and `score_details` properties for:

- transparent 0–100 dimension scores and reasons;
- evidence grade and coverage;
- variable/workflow/logic diagnostics;
- structured missing-information importance;
- replication, information-missing and interpretation risks;
- weighted-score contributions and recommendation.

These values currently travel as Skill09 extension output beside the unified core.

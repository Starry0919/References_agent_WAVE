# Experiment, DDR and Admission Gold schemas

Schemas live under `benchmarks/paper_extraction_e2e_v2/schemas`. Experiment Gold defines boundaries and native content; Claim/Evidence Gold defines exact proposition support; DDR Gold defines whether a decision should exist and its triggering lineage; Admission Gold defines admit/block/review outcomes plus whether knowledge is valid and critical.

Every record requires human tier, reviewer, source identity where applicable, schema/version history and linked IDs. Only `ADJUDICATED_GOLD` is scored. Prior decisions are immutable history. Development Gold may guide engineering; sealed holdout Gold is evaluator-only and cannot guide prompts or rules.

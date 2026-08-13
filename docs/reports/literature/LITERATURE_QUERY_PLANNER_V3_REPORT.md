# Literature Query Planner v3 Report

Eight controlled query families cover exact objective, metabolic engineering, strain lineage, intervention concepts, production metrics, mechanistic support, review synthesis, and recall expansion. Templates use normalized intent fields rather than a fixed tryptophan-only string.

Every query records family, rationale, target source, stable ID, and source-specific syntax. Queries are deduplicated and stopped at `max_queries`; raw and canonical candidate budgets plus an overall timeout prevent expansion.


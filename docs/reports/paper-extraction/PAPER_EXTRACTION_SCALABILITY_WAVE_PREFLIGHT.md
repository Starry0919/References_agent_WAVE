# Paper Extraction Scalability Wave Preflight

The existing runtime is a 13-skill workflow launched by an in-memory task-level thread pool. Paper stages 05-09 fan out inside a task; Parse, Clean and Skill07 have content caches, and workflow checkpoint JSON supports limited resume. DDR persistence and optional Git sync are post-processing side effects. There was no durable batch/stage registry, resource-specific global pools, unified retry taxonomy, transactional scientific commit, supplement chain or 1000-job scheduler test.

Actual resource classes: discovery/citation/download are network-bound; checksum/dedup is disk/CPU; MinerU is GPU/CPU/RAM/disk; cleaning/validation/DDR/frontend packaging are CPU/disk; Skill07 is provider-bound; persistence is database/disk; Git sync is an external post-commit side effect. Summary translation is provider/UI-bound and must not be triggered by status polling.

Reusable components retained: existing single-paper service/API, workflow checkpoint artifacts, `pipeline_cache`, MinerU parser/fallback, deterministic cleaner, unchanged Skill07 executor/prompt/model/schema, Skill08+ validators, DDR converter and frontend status APIs.

Scope: add a compatible durable wrapper, not replace scientific implementations. Risks are SQLite writer contention, device-specific MinerU capacity, provider quotas and safe migration of historical artifacts. Defaults therefore remain conservative and model calls are denied unless explicitly allowed.

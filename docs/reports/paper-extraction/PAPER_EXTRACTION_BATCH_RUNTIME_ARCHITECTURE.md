# Paper Extraction Batch Runtime Architecture

`Batch → SQLite Paper Registry → Durable Stage State → Bounded Resource Pools → Content-addressed Artifacts → Transactional Commit/Outbox → Telemetry`

SQLite WAL stores batches, jobs, attempts, artifacts, events and outbox records. Stable UUIDv5 identities derive from batch/paper/stage inputs. Each stage cache identity includes source hash, implementation version and configuration hash. A successful stage atomically inserts its immutable artifact and advances only that paper. Final persistence atomically completes the paper and creates a retryable post-commit outbox event.

Pools are separate for download, MinerU, LLM, CPU validation/cleaning and DB persistence. Queue capacity provides admission backpressure. A process-global MinerU semaphore prevents task × stage concurrency multiplication; disk pressure is checked before admission. GPU/CPU/AUTO execution stays delegated to the existing parser.

Failures are classified and attempts bounded. Permanent failures stop one paper only; upstream immutable artifacts remain. Resume reads SQLite state, retries from `current_stage`, and never recreates successful upstream rows. Cancellation changes job state without deleting shared artifacts.

Scientific boundary: Skill07 content, prompt, model/provider, schema meaning and evidence behavior are untouched. Supplements are separate immutable artifacts and `skill07_supplement_injection` is disabled by default.

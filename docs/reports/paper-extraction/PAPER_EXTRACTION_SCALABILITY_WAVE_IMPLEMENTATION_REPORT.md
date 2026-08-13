# Paper Extraction Scalability Wave Implementation Report

Date: 2026-08-12

## Decision

- Batch runtime: **BATCH_RUNTIME_READY**
- Scientific optimization: **HOLD_FOR_HUMAN_GOLD**
- Skill07 semantics/prompt/model/schema meaning: **UNCHANGED**
- Production scientific default: **UNCHANGED**
- New model calls: **0**

## Required questions

1. Durable queue: YES, SQLite WAL registry. 2. Restart survival: YES, state reconstructs from SQLite. 3. Per-paper/stage persistence: YES. 4. One-paper failure isolation: YES. 5. Failed-stage-only retry: YES. 6. Upstream reuse: YES. 7. Cross-batch cache: YES. 8. Version/config-correct cache: YES. 9. Stage pipeline parallelism: YES. 10. Resource pools: YES. 11. Backpressure: bounded queue capacity. 12. MinerU governance: global semaphore + disk guard. 13. Multiplication prevented: YES. 14. DOI identity/PDF hash dedup: identity registry plus content-addressed artifact schema; production downloader integration remains adapter work. 15-16. Supplements/provenance: YES, additive intake and safe classifications. 17. Supplement injection: disabled by default. 18. Transactional final persistence: YES. 19. External side effects: outbox. 20. Retry: classified/bounded/backoff+jitter. 21. Terminal visibility: persisted error/stage/attempt. 22. Cancellation: YES, non-destructive. 23. Metrics: structured events and batch metrics. 24-25. Status/resume/retry: CLI. 26-28. 100/500/1000 Level-0: PASS. 29. Measured bulk scheduler/persistence overhead: 0.542/0.232/0.254 ms per paper respectively. 30. Level-0 state ceiling: 1,844-4,306 jobs/s; not scientific throughput. 31. Provider capacity: UNKNOWN. 32. Defaults: download 8, MinerU 1, LLM 2, CPU 4, DB 1. 33. Hardware: no GPU assumption; AUTO/device benchmark required. 34-38. Scientific behavior/defaults: unchanged. 39. Model calls: 0. 40. Tests: 234 full paper-extraction tests passed. 41. Security: error redaction, no secrets, safe ZIP, no execution. 42. Real 1000 blockers: provider quota/SLA, verified MinerU hardware capacity, publisher access, supplement availability, production adapter rollout and operational soak.

## Load interpretation

Level-0 persisted 900, 4,500 and 9,000 stage records for 100, 500 and 1,000 papers. It deliberately measures durable admission/state persistence with no handlers or providers. Peak traced Python memory was 0.27, 1.12 and 2.17 MiB; temporary SQLite footprint was 0.57, 2.16 and 7.91 MiB. These figures are scheduler-system measurements, not predictions of PDF, MinerU, LLM or provider throughput.

## Reliability finding

Combined concurrency tests exposed and fixed a scheduler race where a post-submit `RUNNING` write could overwrite a fast worker's next-stage `READY` transition. State is now marked before pool submission. The full suite passed after the fix.

## Compatibility

The runtime is an infrastructure wrapper. Existing single-paper APIs and scientific executors were not modified. Rollout requires wiring real stage handlers into the wrapper; default CLI remains model-call-denied.

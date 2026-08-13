# Partitioned regression report

- Unified extraction/cache/validation: 14 passed in 0.94 s.
- Batch cache/concurrency/recovery/supplement: 6 passed in 2.96 s after isolated rerun.
- Prior complete paper-extraction partition: 215 passed, one warning.
- Prior Evidence partition: 50 passed, one skipped.
- Prior Projects/Admission partition: 44 passed.
- Frontend production build: PASS; tests 47 passed and one pre-existing CommandCenter text assertion failed.
- JSON/Schema/compile/diff checks previously passed for V2 artifacts.
- Full backend: 743 collected; monolithic 300-second run remains INCONCLUSIVE.

No timeout is reported as PASS.

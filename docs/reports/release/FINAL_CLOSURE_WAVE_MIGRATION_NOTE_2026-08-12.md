# Final Closure Wave Migration Note — 2026-08-12

- Existing candidates without `diagnosis_finding_ids` are read as `LEGACY_UNVERIFIED`; no synthetic finding is backfilled.
- Existing API `status/readiness` fields remain available as read-only compatibility projections of `decision_state`.
- Candidate generation now rejects projects lacking observation-grounded DiagnosisFinding records.
- Legacy quantitative fields are populated only after semantic-role validation; ambiguous historical values are quarantined and marked `LEGACY_UNVERIFIED`.
- Historical priors are no longer copied into evidence links.
- The registry id and legacy asset path `MREG-gem_fba_iml1515` / `iML1515.xml` remain for compatibility, but runtime scientific identity is reported as iJO1366 (1367 genes, 2583 reactions).
- Schema migration `0017` from the preceding optimization implementation remains the database migration for the new fields/tables; this closure wave adds no parallel schema.

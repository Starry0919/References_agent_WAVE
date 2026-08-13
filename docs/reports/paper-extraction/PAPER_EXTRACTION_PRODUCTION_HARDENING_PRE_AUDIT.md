# Paper Extraction production hardening pre-audit

Production entry is `service.submit_run()`/WorkflowEngine. All source routes converge on cached Skill05/06 executors and `opus_extractor.make_executor()` for Skill07. The latter loads the runtime system prompt, `SKILL.md`, JSON Schema, semantic contract and validation rules; calls Poe Code CLI; performs bounded network retries and one structural repair; validates before caching or Skill08 eligibility; then hands off through current Skill08, DDR converter and Admission.

Actual configured model on 2026-08-12 is `claude-sonnet-4.6`. Poe CLI doctor/configuration check passes. This benchmark does not override the production model. Cache identity includes document bytes, model, Skill, system prompt, schema, semantic contract, validation rules, runtime contract and validator versions. Writes are atomic; cache hits are re-normalized and revalidated. Existing production cache contains 17 files and is not modified by the cold benchmark, which uses an isolated namespace.

Corpus is the exact ten Development plus five sealed Holdout identities from E2E V1. Holdout is used only for engineering stress, never scientific tuning. The earlier 15/15 result was a deterministic one-claim fixture and is explicitly not called production replay here.

Baseline evidence includes `E2E-BENCH-001` legacy normalization, `E2E-BENCH-002` evaluator-stage mapping, paper-extraction scoped tests, batch runtime failure isolation/resume/cache tests, cache-key invalidation tests, corrupt/invalid-cache revalidation, failed-output non-caching, and conservative downstream gates. External dependencies are Poe provider availability/quota and the configured Claude model.

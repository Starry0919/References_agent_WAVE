# Paper Extraction E2E Benchmark V1 Pre-analysis

Date: 2026-08-12

The repository contains 20 readable real-paper clean-document artifacts and 17
successful historical Skill07 cache artifacts. Fifteen cache artifacts can be
identity-matched to unique clean documents and are used here. Existing audit
files explicitly say `NO_SKILL07_HUMAN_GOLD`; therefore generated annotations
are Silver and the release decision cannot be PASS.

The audited path is Document → historical Skill07 candidate → current
deterministic E1/E2/E3 audit. Current Skill08 handoff, DDR conversion and
knowledge admission require newer provenance/contract envelopes that historical
caches do not contain, so those stages are tested through their existing scoped
regression suites but are not misrepresented as real-paper metric estimates.

Scientific priority is fail-closed: a missing anchor, biological attribution
failure or missing semantic entailment cannot become verified. No paper ID,
paragraph ID or exact claim text is special-cased.

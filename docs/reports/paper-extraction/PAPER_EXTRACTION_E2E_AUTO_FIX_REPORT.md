# Paper Extraction E2E Auto-fix Report

One deterministic P1 defect was fixed: the new evaluator initially assumed that
all historical `field_metadata` values were dictionaries and all locators were
objects. Real caches include legacy list metadata and string locators, causing an
`AttributeError`. The evaluator now type-guards metadata and normalizes string
locators. Regression fixture: `E2E-BENCH-001.json`.

No production scientific rule, prompt, Skill07 extractor, Skill08 threshold,
DDR rule or admission gate was changed. Low E3 agreement is not an eligible
auto-fix: relaxing it without human adjudication could create false verified
knowledge. No paper-specific hardcode was introduced.

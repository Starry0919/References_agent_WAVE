# Skill07 UI Acceptance Report — V3

Date: 2026-08-12

## Acceptance matrix

| Area | Result | Evidence |
|---|---|---|
| Human/Agent isolation | PASS | Human Gold has source + independent annotation only; Agent summaries remain on Paper Detail. |
| Scientific semantics | PASS | Paper Detail separates fact / interpretation / reconstructed hypothesis. |
| Human-readable identity | PASS | GOLD-P01 keeps benchmark identity while title derives from source text, not a hash. |
| Provenance hygiene | PASS | Technical source ID and raw paragraph locators are not primary-page content. |
| Download contracts | PASS | Both pages expose curated Machine-readable JSON and Review JSON. |
| Role isolation | PASS | Review export reads only the requested role; regression test excludes ANNOTATOR_B from A export. |
| Gold safety | PASS | No draft is auto-populated; candidates remain UNREVIEWED / NOT GOLD. |
| Canonical document | PASS | P01/P02 automated checks find no Markdown image, HTML sup tag, source path, or primary internal ID leakage. |
| Backend regression | PASS | Full paper-extraction suite: 225 passed. |
| Frontend regression | PASS | Production build and Human Gold component test passed. |
| Navigation / i18n | PASS | Human Gold remains in the global navigation; new V3 labels support Chinese and English. |
| Screenshot export | PASS (code path) | Existing segmented PNG export remains available; production build and component rendering pass. No browser pixel-baseline comparison was run in this execution. |

## Known non-blocking observation

Vite reports the pre-existing main JavaScript chunk above 500 kB. The screenshot library remains dynamically split; the warning does not block this acceptance. GOLD-P02 lacks a reliably identified source Abstract, so the engineering-goal overview correctly reports unavailable rather than inferring one.

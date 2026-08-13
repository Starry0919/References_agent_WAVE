# Skill07 Gold Workbench Frontend Audit

## Current problems

The direct route works but is a two-column engineering prototype: raw JSON, weak hierarchy, no formal navigation entry, no metadata/progress, no role-safe exports, no original-PDF endpoint, no capture workflow, and no help/onboarding. Candidate data can dominate once revealed. The global i18n context exists and persists language, but the prototype does not consume it.

## Reuse

Reuse the platform `I18nProvider/useI18n`, `LanguageToggle`, existing Tailwind tokens, router, API client, FastAPI app and role-isolated Gold storage. Preserve `/skill07-gold` as a refresh-safe non-project route. Add a clear Knowledge navigation link without changing existing DBTL pages.

## Additions

- Productized source-first workbench with header, role/status/progress, paper/experiment navigator, readable source cards, structured experiment editor, claims/evidence/candidate tabs, help dialog, loading/error/toast and unsaved-change guard.
- Role-safe deterministic review-PDF endpoint; no LLM and no other annotator data.
- Original-PDF endpoint resolved from corrected manifest by exact paper ID/hash, never filename guessing.
- Browser capture mode using the native print-to-PDF-independent DOM screenshot flow: lazy-loaded `html2canvas`, page-height safety check and segmented PNG fallback.
- API metadata exposes only review-safe paper metadata and download availability.

## Export design

Review PDF uses ReportLab, A4 margins, CJK font discovery, headers/footers/page numbers, short source excerpts and structured sections. It is explicitly a working annotation document, not frozen Gold. Original PDF bytes are streamed unchanged after exact mapping/hash validation.

## Navigation and i18n

Add `Human Gold Review` under Knowledge & Evidence navigation and a return link in the workbench. All new UI chrome uses one local bilingual dictionary driven by the existing global language context; scientific source text remains unchanged.

# Skill07 Gold Workbench Frontend Implementation Report

## Outcome

`/skill07-gold` is now a formal source-first review workspace with platform navigation, global i18n, reviewer onboarding, paper/role/status/progress context, readable long-form source, structured Human Gold editor, secondary candidate aids, save/validation protection and deterministic exports.

## Capabilities

- Navigation: persistent Human Gold Review entry in the platform header and return path to Knowledge & Evidence.
- i18n: uses existing `I18nProvider`/`LanguageToggle`; all new chrome has curated Chinese/English text and language switching does not recreate the draft.
- Review PDF: role-isolated ReportLab A4 export with cover, instructions, metadata, progress, experiments, claims, evidence, decisions/blockers and compact provenance. It never reads another annotator draft and works when Gold=0.
- Original PDF: exact paper-ID lookup through corrected manifest plus SHA-256 verification; 10/10 mappings validated; missing/mismatch fails clearly.
- Capture: lazy-loaded html2canvas; capture mode removes sticky duplication; content above 14,000px is exported as numbered segments rather than silently truncated.
- Data safety: revision saves, beforeunload warning, role/paper change confirmation and exports/capture that never write annotations.

## Validation

- Export/Gold/accelerated targeted: 24 passed.
- Full paper-extraction: 219 passed, one existing Starlette deprecation warning.
- Frontend workbench test: 1 passed.
- Frontend production build: PASS. html2canvas is a separate lazy chunk (202.43 kB); existing main bundle warning remains (1.31 MB) and was not caused by eagerly loading capture code.
- Review PDF: rendered and visually inspected across all 3 pages.
- Security scan: zero secret-pattern hits in new deliverables.
- New model calls: 0.

## State

Workbench UI: HUMAN_REVIEW_READY  
Review PDF export: PASS  
Full-page capture: PASS  
Original PDF download: PASS  
Chinese/English i18n: PASS  
Navigation integration: PASS  
Human Gold fabricated: NO  
New model calls: 0  
Production behavior changed: NO

Human Gold remains `AWAITING_HUMAN_ANNOTATION`; benchmark remains `HOLD`; production default remains unchanged.

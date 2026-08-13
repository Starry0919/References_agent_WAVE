# Skill07 Human Gold Mirror Audit

Date: 2026-08-12

## Current Paper Detail

- Route: `/projects/:projectId/evidence/:sourceId`.
- Loader: `getEvidenceDocument`.
- Stable view components: `PaperHeader`, `ExperimentalDesignPanel`, `ExperimentalStepCard`, `EvidenceProvenancePanel`, graph and export controls.
- Core hierarchy: paper metadata → paper-specific experimental-design reconstruction → evidence provenance.
- Paper Detail is the protected reference for this task and will not be edited.

## Current Human Gold gap

- Route is `/skill07-gold` with one selected paper at a time; it does not render ten papers together.
- It uses a custom three-column source-search/form layout rather than the Paper Detail card hierarchy.
- Full text is no longer shown by default, but the source-search column remains visually dominant.
- Human-only controls that must remain: role, revision, save, validation, add missed experiment, merge/split/link/uncertain, PDF, capture and role-isolated JSON.
- Candidate data is hidden and Agent reasoning/confidence is not rendered.

## Reuse decision

- Mirror the existing `ExperimentalStepCard` visual hierarchy: numbered experiment title, WHY/problem/hypothesis, HOW/intervention/method/result, evidence, and optional relations.
- Feed it only Human Gold draft values and linked source evidence; do not load or copy Agent extraction as Gold.
- Add field/item states `ACCEPTED`, `EDITED`, `REJECTED`, `UNCERTAIN`, `NOT_REVIEWED` plus edit/reject/add controls.
- Keep canonical source lookup as a secondary on-demand Evidence viewer.
- Keep loader/storage separate: Paper Detail remains read-only DDR; Human Gold writes only role-specific annotation JSON.

## Regression boundary

- No Paper Detail route, component, data loader, JSON, workflow, copy, or styling file will be changed in this task.
- Verification will include a scoped diff check asserting no Paper Detail file changes attributable to this task, plus existing frontend/build regression.

# Skill07 Human Gold Mirror Implementation Report

Date: 2026-08-12

## Implementation

- Added `/skill07-gold/:paperId` while retaining `/skill07-gold`; each route renders one selected paper.
- Reworked the Human Gold experiment area to mirror the current Paper Detail experiment-card hierarchy: paper-specific title, WHY/problem/rationale, HOW/intervention/validation/result, evidence, and relations.
- The mirrored values come only from the current role's Human Gold draft. No Agent extraction is copied into Gold.
- Added item states: `ACCEPTED`, `EDITED`, `REJECTED`, `UNCERTAIN`; absence of a decision remains `NOT_REVIEWED`.
- Added human operations for missing experiment/step/claim/evidence, move, merge, split, parent-child link, branch add/remove, and relation edit.
- Linked readable source evidence is shown within each Human Gold experiment. Full source text remains an on-demand keyword search, not a default reader.
- Expanded Human Gold Machine JSON with metadata, full design representation, workflow, design rounds, detailed steps, claims, evidence, decisions, review status, provenance, validation and schema version.
- Expanded Review JSON with reviewer, field states, edits, additions, rejections, unresolved items, comments, evidence corrections, completion and adjudication state.

## Isolation

- All decisions and edits write through the existing role-specific Gold draft API.
- Production DDR/Paper Detail artifacts remain read-only and unchanged by this task.
- A/B draft isolation and optimistic revision checks remain intact.
- No model call was added.

## Files changed in this task

- `frontend/src/pages/gold/Skill07GoldWorkbenchPage.tsx`
- `frontend/src/router.tsx`
- `harness/api/skill07_gold.py`
- `harness/paper_extraction/human_review_view.py`
- `tests/paper_extraction/test_skill07_human_gold_mirror.py`
- Mirror audit, implementation and acceptance reports.

No Paper Detail source file was modified in this task.

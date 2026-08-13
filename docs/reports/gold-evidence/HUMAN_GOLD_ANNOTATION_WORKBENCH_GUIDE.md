# Human Gold Annotation Workbench guide

Open the frontend route registered for **Skill07 Human Gold Workbench** and select a paper and role. Candidate output is hidden by default for source-first review. The API is under `/api/skill07-gold`; saves use revisions to prevent overwrite, and every action is appended to the audit log.

1. Open a paper and confirm its document hash.
2. Review experiment boundaries; add, delete, merge, split or link subexperiments.
3. Correct context, interventions, conditions, controls, measurements and outcomes.
4. Review every atomic claim, its semantics and experiment binding.
5. Add/resolve evidence spans and their roles.
6. Adjudicate support and attribution; keep uncertainty explicit.
7. Review DDR and admission decisions.
8. Save `HUMAN_REVIEWED` with reviewer identity.
9. A second reviewer works independently; the adjudicator resolves recorded disagreements.
10. Promote only resolved records to `ADJUDICATED_GOLD`, seal the version, and let the benchmark consume it read-only.

AI candidates are Silver aids only. For the first meaningful run, independently annotate at least two development papers plus two untouched holdout papers covering multiple experiments and at least one time-course/dose/control case; expand to the planned ten-paper release before promotion.

# Gold pilot operator checklist

1. Start backend with the repository’s normal server command and frontend with `npm run dev` in `frontend`.
2. Open `http://localhost:5175/skill07-gold`.
3. Annotate Development `GOLD-P01` and `GOLD-P09`; Holdout `GOLD-P05` and `GOLD-P06` stays sealed from development changes.
4. Assign two real, distinct opaque reviewer IDs. Reviewer A and B work independently, source-first.
5. Resolve experiment boundaries, scientific claims, evidence roles/anchors, DDR and admission. Required identity, provenance, critical claims and resolvable anchors cannot remain incomplete for sealing.
6. Validate each draft, submit both for adjudication, preserve disagreements, then have a distinct adjudicator record rationale and decisions.
7. Promote only QC-clean adjudicated records; seal via the versioned Gold freeze operation. Never overwrite an existing release.
8. Run `python benchmarks/paper_extraction_e2e_v2/evaluation/gold_pilot.py` and the Gold Benchmark V2 evaluator.
9. Verify the pilot manifest still marks Holdout sealed and export the immutable release directory plus manifest hashes.

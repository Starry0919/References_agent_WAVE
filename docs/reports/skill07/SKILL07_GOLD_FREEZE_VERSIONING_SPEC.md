# Skill07 Gold Freeze and Versioning

Only 10 validated ADJUDICATOR records with G0-G7 pass may freeze. Release name is `skill07-gold-vMAJOR.MINOR.PATCH`. Freeze copies annotations and schemas into a new directory, records hashes/source fingerprints/actor/timestamp/validation, and refuses an existing target. Verification rejects missing, unexpected or changed files. Scoring first verifies the release and never reads mutable drafts.

- PATCH: correction without intended benchmark semantic change.
- MINOR: additive adjudicated coverage.
- MAJOR: schema/policy change affecting interpretation.

Frozen files are never edited in place; a correction creates a new version with parent/changelog metadata in the release process.

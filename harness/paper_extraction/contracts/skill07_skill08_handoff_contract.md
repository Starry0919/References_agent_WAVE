# Skill07 to Skill08 Handoff Contract

Version: `skill07_skill08_handoff_v2`

The handoff carries an immutable Skill07 result identity, its candidate payload,
and the exact clean-document identity. Skill08 accepts only success-compatible,
eligible, self-check-passing Skill07 results whose schema/semantic/rules versions
are compatible and whose document hash resolves. Missing, duplicate, mismatched,
or legacy identity fails closed. Positional association is forbidden.


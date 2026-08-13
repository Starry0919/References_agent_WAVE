# Atomic Claim Layer Design

An atomic claim contains one experiment foreign key, scalar subject, predicate
and object, optional value/unit, epistemic status and a non-empty evidence
bundle. Skill07 evidence is always candidate.

Skill08 verifies the relation with E1/E2/E3. Claim verification is canonical;
legacy fields remain compatibility output. Admission independently accepts
verified claim IDs. Legacy migration never performs sentence splitting and marks
generated records review-required.

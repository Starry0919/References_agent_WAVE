# Literature Multi-Axis Taxonomy v2

Contract: `literature-taxonomy/2.0`.

The controlled vocabularies are machine-readable in `literature_taxonomy_v2.json`. The six axes are deliberately independent:

1. `publication_form`: what publication object this is, including detailed review subtypes.
2. `research_design`: how the research was conducted; multi-label.
3. `engineering_modes`: concrete engineering modalities; multi-label.
4. `evidence_modalities`: measurements or evidence channels; multi-label.
5. `knowledge_contributions`: search and routing value, not knowledge-base admission.
6. `evidence_strength`: directness of evidence, independent of publication form and design.

Every label contains `value`, `confidence`, numeric `score`, `evidence_source`, `evidence_location`, and concise `reason_codes`. Insufficient evidence produces `UNKNOWN`, `NONE_DETECTED`, or a generic `REVIEW`; no detailed subtype is invented.


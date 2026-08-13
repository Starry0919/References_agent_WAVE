# Literature Classifier v2 Implementation Report

Implementation: `harness/literature_discovery/classification.py` and `taxonomy.py`.

- Metadata stage uses title, abstract, publication metadata, and source-record provenance.
- Full-text stage refines all axes and retains the complete metadata classification in provenance.
- Review subtyping covers narrative, systematic, scoping, meta-analysis, systematic plus meta-analysis, state-of-the-art, mini, critical, methodological, and technology reviews.
- Wet-lab, computational, hybrid, model, omics, screening, bioprocess, method, resource, database, software, and benchmark designs are multi-label.
- Engineering and evidence labels are pattern-evidenced rather than inferred from publication form.
- Metadata/full-text contradictions set `classification_conflict`, enumerate fields, and record the resolution policy.
- Deterministic batch classification is idempotent and failure-isolatable; mandatory LLM calls are not introduced.

Review papers retain literature value and synthesized-secondary evidence. They are not treated as direct primary evidence and are not discarded from search.


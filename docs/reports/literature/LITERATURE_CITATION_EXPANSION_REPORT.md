# Literature Citation Expansion Report

The bounded implementation supports BACKWARD_CITATION_EXPANSION and FORWARD_CITATION_EXPANSION with limits for seed count, references/citations per seed, total expansion, deduplication, and maximum depth 1. Review-derived candidates receive `DISCOVERED_FROM_REVIEW_CITATION` provenance and must re-enter the normal pipeline.

Live expansion is safely disabled by default because the current OpenAlex/Crossref normalized candidates do not consistently expose reference identifiers. The implementation and bounded/dedup/provenance tests are complete; enabling it requires a stable citation provider, not a redesign.


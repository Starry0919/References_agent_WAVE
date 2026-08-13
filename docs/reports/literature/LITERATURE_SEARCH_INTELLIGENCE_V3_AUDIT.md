# Literature Search Intelligence v3 Audit

Repository truth: v2 provided OpenAlex/Crossref retrieval, basic deduplication, metadata classification/routing, lawful acquisition, and separate fulltext verification. It did not provide a natural-language intent contract, generalized query plan, identity conflicts, citation expansion, explicit v3 ranking, stage states, fulltext score deltas, production result contract, or a mounted search API.

v3 adds those components inside the literature subsystem only. Existing adapters, source failure isolation, v2 classification, acquisition, canonical parsing, and verification remain the implementation base. DDR, Skill07, Skill08, knowledge schemas, and unrelated workflows were not changed.

Production path: natural-language request -> intent v3 -> bounded queries -> adapters -> conservative identity resolution -> metadata classification/ranking -> bounded selection -> optional fulltext refinement -> final reranking -> explainable v3 response.


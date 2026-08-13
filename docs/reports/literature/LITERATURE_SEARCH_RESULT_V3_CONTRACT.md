# Literature Search Result v3 Contract

`literature-search-result/3.0` exposes request/paper identity, metadata, scientific host/product/objective/engineering match, metadata/fulltext/final classification, metadata/fulltext/final scores, delta, rank, score breakdown, route, verification level, acquisition, parser, concise explanation, and source provenance.

Verification levels distinguish METADATA_CLASSIFIED and FULLTEXT_VERIFIED. Stage transitions separately expose query generation, retrieval, identity resolution, metadata ranking, and fulltext reranking. The contract is additive to existing candidate fields.

Production endpoint: `POST /api/literature-search`; readiness: `GET /api/literature-search/readiness`.


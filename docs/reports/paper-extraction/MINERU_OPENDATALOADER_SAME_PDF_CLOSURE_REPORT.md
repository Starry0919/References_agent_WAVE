# MinerU / OpenDataLoader Same-PDF Closure

1. MinerU truly ran all 5 identical PDFs: yes.
2. OpenDataLoader truly ran the same 5 hashes: yes.
3. Section recovery: MinerU retained structured heading levels; comparison is in JSON.
4. Tables: compare per-paper structured counts in JSON.
5. Figures/captions: both retained figures; MinerU emitted raw images.
6. Anchor stability: relocation matrices are in JSON.
7. Scientific Judge disagreements: {'host_relation': 0, 'product_role': 0, 'publication_type': 1, 'implemented_interventions': 1, 'measured_evidence': 1, 'scientific_judge': 1, 'evidence_span_count': 3}.
8. Runtime: MinerU 332.68s vs OpenDataLoader 0.00s for five PDFs.
9. Continue OpenDataLoader shadow: yes.
10. Change PRIMARY: no; retain MinerU PRIMARY / OpenDataLoader SHADOW.

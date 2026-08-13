# Inter-Annotator Agreement Implementation

`gold.py` now computes per-field valid-pair count, missingness, raw agreement, Cohen's kappa and disagreement count for identity, publication, host, product, intervention, measured production and final eligibility. Constant-label kappa returns null rather than a misleading value. `adjudication_queue()` detects missing/invalid or disagreeing required fields. No agreement metric is reported on the empty human batch.

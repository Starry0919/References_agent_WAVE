# Literature Ranking v3 Implementation Report

Ranking separates scientific relevance, classification confidence, availability, classic importance, recent relevance, fulltext verification, and hard-negative penalties. Availability is a small secondary signal.

Direct engineering mode rewards K-12 evidence, target-product evidence, engineering, wet-lab design, direct evidence, and production metrics. General rules suppress wrong products, non-target hosts, clinical/infection/detection contexts, unresolved requested strain, model/enzyme/review mismatch, missing objective evidence, and missing engineering evidence.

Fulltext refinement retains metadata score, final score, score delta, breakdown, and reasons. Classic papers receive a bounded importance signal and are never removed solely by year. Diversity uses bounded route quotas only in BALANCED mode and never overrides direct-mode relevance.


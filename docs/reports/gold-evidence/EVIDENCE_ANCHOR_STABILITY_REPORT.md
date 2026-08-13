# Evidence Anchor Stability Report

Anchor resolution v1.2 tries: exact ID → same section+quote hash → any section normalized quote hash → AMBIGUOUS/UNRESOLVED. It never silently chooses among duplicate quotes. Unit tests cover exact and relocated exact quote. Cross-parser empirical stability awaits matching MinerU/OpenDataLoader outputs for the same PDF.

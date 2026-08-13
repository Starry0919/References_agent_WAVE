# Gold-driven error propagation

Scientific root-cause rates are not estimable. One deterministic P1 was found: the new replay queried obsolete Skill08 stage keys, falsely reporting E1/E2/E3 incomplete despite verified envelopes. It is recorded once at `BENCHMARK_EVALUATOR`; downstream stage undercounts are consequences, not separate errors.

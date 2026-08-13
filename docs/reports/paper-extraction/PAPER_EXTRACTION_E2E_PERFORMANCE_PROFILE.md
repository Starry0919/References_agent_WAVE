# Paper Extraction E2E Performance Profile

The deterministic 15-paper audit used historical cache hits and made zero LLM
calls. The measured run took about 4.3 seconds, with median per-paper evaluation
near 264 ms and peak traced Python memory near 7.9 MB. Exact values are persisted
in `reports/e2e_results.json`.

These numbers profile only annotation/evaluation, not Poe extraction. Historical
stage telemetry reports Skill07 non-cache median latency around 729 seconds and
dominant runtime share around 94%; those historical values are not rebranded as
this run's latency. No performance optimization changed scientific behavior.

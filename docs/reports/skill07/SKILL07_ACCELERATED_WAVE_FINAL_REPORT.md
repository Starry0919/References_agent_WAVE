# Skill07 Accelerated Integrated Wave Final Report

- Starting state: Human-Gold infrastructure ready; Gold 0; HOLD; production unchanged.
- Current state: `P01_AWAITING_HUMANS`; engineering/orchestration `READY`.
- Human counts: A 0/10, B 0/10, adjudicated 0/10; Gold experiments/claims/evidence 0.
- P01 calibration: AWAITING_HUMANS; no policy/schema defect can be inferred before real annotations.
- Packages: 10/10 source/package valid; 66/66 unresolved traceable; 70 Silver union items preserved.
- Coverage aids: generated for all 10, including unlinked source regions, figures/tables and deterministic intervention/readout cues; never Gold.
- IAA: NOT_EXECUTED, blocked by missing paired human annotations.
- G0-G7 blockers per paper: G1 source coverage, G6 adjudication, G7 history. Invalid Gold cannot freeze.
- Frozen Gold: none; version/integrity NOT_APPLICABLE.
- Existing A/G vs Gold: NOT_EXECUTED, blocked by verified frozen Gold.
- Pilot/Round1/repetitions/concurrency: all NOT_EXECUTED, blocked by verified Gold and quality gates.
- Critical G regression: UNKNOWN; no Gold comparison exists.
- Successful papers/hour and 100/500/1000 projection: NOT_MEASURED; no eligible measured throughput.
- Calls: primary 0, repair 0; planned maximum primary 68 after unlock.
- Provenance: PASS after resolving runtime `poe_code_cli + kimi-k3`; provider revision UNKNOWN; credentials not serialized.
- Production behavior: unchanged.
- Final G decision: **HOLD**.

One-command workflow:

```powershell
python tools/skill07_gold_cli.py status --all
python tools/skill07_gold_cli.py advance --all --dry-run
python tools/skill07_gold_cli.py advance --all
```

Model stages require the extra `--allow-model-calls` flag and still fail closed without verified Gold. Exact next action: two humans independently complete source-first GOLD-P01 annotations in `/skill07-gold`; then run `advance --all` to compute calibration/IAA and create adjudication inputs.

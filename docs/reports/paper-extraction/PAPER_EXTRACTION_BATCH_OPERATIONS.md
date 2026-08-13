# Paper Extraction Batch Operations

```powershell
python tools/paper_batch_runtime.py submit batch.json --dry-run
python tools/paper_batch_runtime.py submit batch.json
python tools/paper_batch_runtime.py status <batch_id>
python tools/paper_batch_runtime.py metrics <batch_id>
python tools/paper_batch_runtime.py resume <batch_id>
python tools/paper_batch_runtime.py retry-failed <batch_id>
python tools/paper_batch_runtime.py cancel <batch_id>
```

Dry-run performs zero model calls. Resume also performs no new model call by default; use `--allow-model-calls` only after explicit authorization. Inspect `FAILED_PERMANENT` rows for stage, attempts, redacted error and retained upstream artifact hashes. Cancellation is non-destructive.

Recommended initial workers: download 8, MinerU 1, LLM 2, CPU 4, DB 1, queue capacity 64. Raise MinerU only after local VRAM/RAM tests; do not infer provider capacity from Level-0 load results.

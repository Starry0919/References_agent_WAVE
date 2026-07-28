"""Checkpoint persistence. Atomic write so a crash mid-save can never leave a
half-written checkpoint that a resumed run would treat as valid (SKILL.md
第九章: "重试不能覆盖旧版本" / "状态成功必须发生在有效 Artifact 持久化之后").
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path


class ArtifactStore:
    def __init__(self, root):
        self.root = Path(root)

    def save_checkpoint(self, task_id, state):
        folder = self.root / task_id
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / "checkpoint.json"
        fd, temp = tempfile.mkstemp(dir=folder, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2, default=str)
            os.replace(temp, target)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
        return target

    def load_checkpoint(self, task_id):
        path = self.root / task_id / "checkpoint.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None

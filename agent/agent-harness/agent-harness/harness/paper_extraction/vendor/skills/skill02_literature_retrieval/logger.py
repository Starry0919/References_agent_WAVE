import json
from pathlib import Path
from typing import Any, Mapping, Optional


class JsonlSkillLogger:
    def __init__(self, path: Optional[Path] = None):
        root = Path(__file__).resolve().parents[2]
        self.path = path or root / "logs" / "skill02_literature_retrieval.jsonl"

    def __call__(self, event: Mapping[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(dict(event), ensure_ascii=False, sort_keys=True) + "\n")


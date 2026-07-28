import json
from pathlib import Path
class JsonlSkillLogger:
    def __init__(self, path=None):
        self.path = Path(path) if path else Path(__file__).resolve().parents[2] / "logs" / "skill11_engineering_proposal.jsonl"
    def __call__(self, event):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f: f.write(json.dumps(dict(event), ensure_ascii=False, default=str) + "\n")

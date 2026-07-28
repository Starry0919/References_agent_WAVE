from __future__ import annotations
import hashlib, json
SKILL_ID = "skill11_engineering_proposal"
SKILL_VERSION = "0.2.0"
POLICY = "evidence-dbtl-v1"
PHASES = ("design", "build", "test", "learn")
def sha256_json(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()

import hashlib, json
from datetime import datetime, timezone
SKILL_ID = "skill12_qc_human_review"
SKILL_VERSION = "0.2.0"
RULESET = "governance-rules-v1"
STATUSES = ("PASS", "WARNING", "REVIEW_REQUIRED", "BLOCKED")
def sha256_json(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
def now_iso():
    return datetime.now(timezone.utc).isoformat()
def stable_id(prefix, *parts):
    return f"{prefix}_{hashlib.sha256('|'.join(map(str, parts)).encode()).hexdigest()[:16]}"

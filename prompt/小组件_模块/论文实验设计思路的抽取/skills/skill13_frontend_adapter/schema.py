import hashlib, json
SKILL_ID="skill13_frontend_adapter"
SKILL_VERSION="0.2.0"
POLICY="scientific-interface-v1"
def sha256_json(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
def unwrap(value):
    return value.get("output", value) if isinstance(value, dict) else value
def short(value, limit=140):
    text=json.dumps(value,ensure_ascii=False,default=str) if not isinstance(value,str) else value
    return text if len(text)<=limit else text[:limit-1]+"…"

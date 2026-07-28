from __future__ import annotations
try:
    from ..schema import present
except ImportError:
    from schema import present

def field_score(fields, names):
    found = [name for name in names if present(fields.get(name))]
    missing = [name for name in names if name not in found]
    return round(100 * len(found) / len(names), 2), found, missing

def result(score, reason, **extra):
    return {"score": round(float(score), 2), "reason": reason, **extra}

def values(value):
    if isinstance(value, list): return value
    if isinstance(value, dict):
        for key in ("items", "variables", "workflow", "steps"):
            if isinstance(value.get(key), list): return value[key]
    return []

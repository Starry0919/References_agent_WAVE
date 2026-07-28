from .common import result
try:
    from ..schema import present
except ImportError:
    from schema import present

def evaluate(fields):
    checks = {
        "strain": present(fields.get("strain")),
        "protocol": present(fields.get("engineering_method")),
        "condition": present(fields.get("culture_conditions")),
        "replicate": present(fields.get("replicates")),
        "measurement": present(fields.get("assay")) or present(fields.get("instruments")),
    }
    score = 20 * sum(checks.values())
    level = "low" if score >= 80 else "medium" if score >= 50 else "high"
    missing = [k for k, v in checks.items() if not v]
    return result(score, f"{sum(checks.values())} of 5 reproduction-critical components are reported.", level=level, missing_components=missing)

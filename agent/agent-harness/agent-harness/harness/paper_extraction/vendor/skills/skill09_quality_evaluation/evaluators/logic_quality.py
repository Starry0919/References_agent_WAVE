from .common import result
try:
    from ..schema import present
except ImportError:
    from schema import present

def evaluate(fields, extensions):
    checks = {
        "research_question": present(fields.get("objective")),
        "hypothesis": present(fields.get("hypothesis")),
        "intervention": present(fields.get("engineering_method")) or present(fields.get("experimental_groups")),
        "measurement": present(fields.get("assay")) or present(fields.get("instruments")),
        "outcome": present(fields.get("outcomes")),
    }
    score = 20 * sum(checks.values())
    missing = [k for k, v in checks.items() if not v]
    return result(score, f"{sum(checks.values())} of 5 logic links are explicitly represented.", missing_components=missing, components=checks)

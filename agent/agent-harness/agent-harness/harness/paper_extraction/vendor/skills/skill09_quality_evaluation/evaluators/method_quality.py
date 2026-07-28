from .common import result
try:
    from ..schema import present
except ImportError:
    from schema import present

def evaluate(fields):
    checks = {
        "control": present(fields.get("controls")),
        "replicate": present(fields.get("replicates")),
        "assay": present(fields.get("assay")),
        "validation": present(fields.get("outcomes")),
        "statistical_analysis": present(fields.get("analysis_methods")),
    }
    score = 20 * sum(checks.values())
    return result(score, f"{sum(checks.values())} of 5 method-description components are available.",
                  strengths=[k for k, v in checks.items() if v], limitations=[k for k, v in checks.items() if not v])

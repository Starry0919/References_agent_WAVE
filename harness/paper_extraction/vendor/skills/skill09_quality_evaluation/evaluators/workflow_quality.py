from .common import result, values

def evaluate(fields, extensions):
    raw = extensions.get("experiment_workflow", {})
    steps = values(raw)
    # Search only the actual textual content of each step (stage label +
    # source operation text), never str(dict) on the whole step: every step
    # also carries a literal "status": "reported" key, and stringifying the
    # dict makes "stat" (and thus the "analysis" check) match on the key
    # name alone regardless of what the step is actually about.
    text = " ".join(f"{step.get('stage', '')} {step.get('operation', '')}".lower() for step in steps if isinstance(step, dict))
    checks = {
        "construction": bool(steps) and any(x in text for x in ("construct", "engineer", "transform", "edit")),
        "cultivation": bool(steps) and any(x in text for x in ("cult", "grow", "ferment")),
        "measurement": bool(steps) and any(x in text for x in ("measure", "assay", "detect", "quant")),
        "analysis": bool(steps) and any(x in text for x in ("analy", "stat", "calculate")),
    }
    # Field-backed stages are valid explicit knowledge even when workflow labels differ.
    checks["construction"] |= fields.get("engineering_method", {}).get("status") in {"reported", "inferred"}
    checks["cultivation"] |= fields.get("culture_conditions", {}).get("status") in {"reported", "inferred"}
    checks["measurement"] |= fields.get("assay", {}).get("status") in {"reported", "inferred"}
    checks["analysis"] |= fields.get("analysis_methods", {}).get("status") in {"reported", "inferred"}
    score = 25 * sum(checks.values())
    return result(score, f"{sum(checks.values())} of 4 workflow stages are represented.",
                  missing_steps=[k for k, v in checks.items() if not v], stages=checks)

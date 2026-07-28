def _walk(value, path="$"):
    if isinstance(value, dict):
        for k, v in value.items():
            current = f"{path}.{k}"
            if (isinstance(v, dict) and v.get("status") == "unknown") or v == "unknown":
                yield current
            yield from _walk(v, current)
    elif isinstance(value, list):
        for i, v in enumerate(value): yield from _walk(v, f"{path}[{i}]")
def check(content):
    missing = sorted(set(_walk(content)))
    return {"passed": not missing, "missing_information": missing,
            "issues": [{"code": "unknown_information", "path": x, "severity": "warning"} for x in missing],
            "reason": f"{len(missing)} unknown values were found."}

from typing import Any, Dict, List, Mapping, Optional


def validate_input(request: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(request, Mapping) or not isinstance(request.get("research_intent"), Mapping):
        return _error("EDX-RET-001", "RET001", "Skill01 research_intent is missing.", False)
    sources = request.get("sources")
    if sources is not None and (not isinstance(sources, list) or not all(isinstance(v, str) for v in sources)):
        return _error("EDX-VAL-001", "RET001", "sources must be an array of strings.", False)
    return None


def validate_output(output: Mapping[str, Any]) -> List[Dict[str, Any]]:
    candidates = output.get("candidates", [])
    sourced = all(bool(c.get("retrieval_sources")) for c in candidates)
    complete = all(
        isinstance(c.get("title"), str) and bool(c["title"].strip())
        and isinstance(c.get("authors"), list) and "year" in c
        for c in candidates
    )
    dois = [c.get("identifiers", {}).get("doi") for c in candidates if c.get("identifiers", {}).get("doi")]
    unique_doi = len(dois) == len(set(dois))
    annotations = output.get("candidate_annotations", {})
    no_unsourced = all(c["paper_id"] in annotations for c in candidates)
    return [
        {"name": "source_authenticity", "passed": sourced},
        {"name": "no_unsourced_candidates", "passed": no_unsourced},
        {"name": "schema_completeness", "passed": complete},
        {"name": "duplicate_doi_check", "passed": unique_doi}
    ]


def _error(code: str, local_code: str, message: str, retryable: bool) -> Dict[str, Any]:
    return {
        "code": code, "local_code": local_code, "category": "retrieval",
        "message": message, "retryable": retryable,
        "severity": "error", "context": {},
        "suggested_action": "Check Skill01 output or source configuration."
    }


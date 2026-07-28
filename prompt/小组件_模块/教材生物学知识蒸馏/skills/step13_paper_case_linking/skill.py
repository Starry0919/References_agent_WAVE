"""Step13 - link engineering principles / design patterns to paper cases
produced by 论文实验设计抽取 (a paper_case_artifacts entry is treated as an
opaque ExperimentalCase-shaped dict; no assumption is made about its exact
field set beyond "it has some text describing intervention/outcome").

Because a single paper knockout instantiating part of a principle is not
the same as validating the whole principle (SKILL.md Step13 closing
warning), every link produced here keeps confidence low and is marked
requires_human_review; nothing here is ever auto-promoted to "validated".
"""
from __future__ import annotations

import re

VERSION = "0.1.0"

_TOKEN = re.compile(r"[A-Za-z一-鿿]{5,}")
_SUCCESS_WORDS = ["increase", "improved", "higher titer", "提高", "增加", "提升"]
_FAILURE_WORDS = ["decrease", "impaired", "reduced growth", "failed", "降低", "受损", "下降"]


def _flatten_text(value, acc):
    if isinstance(value, str):
        acc.append(value)
    elif isinstance(value, dict):
        for v in value.values():
            _flatten_text(v, acc)
    elif isinstance(value, list):
        for v in value:
            _flatten_text(v, acc)


def _blob(value):
    acc = []
    _flatten_text(value, acc)
    return " ".join(acc)


def _tokens(text):
    return {t.lower() for t in _TOKEN.findall(text)}


def _case_id(case, index):
    return case.get("experiment_id") or case.get("case_id") or case.get("id") or f"paper_case_{index}"


def execute(request, **kwargs):
    objects = [o for o in request.get("knowledge_objects", []) if o.get("type") in {"engineering_principle", "design_pattern"}]
    cases = request.get("paper_case_artifacts", [])
    links = []
    seq = 0

    for obj in objects:
        obj_text = " ".join([
            " ".join(obj.get("trigger_conditions", [])), " ".join(obj.get("recommended_actions", [])),
            " ".join(obj.get("canonical_structure", [])), " ".join(obj.get("biological_basis", [])),
        ])
        obj_tokens = _tokens(obj_text)
        if not obj_tokens:
            continue
        for i, case in enumerate(cases, start=1):
            case_text = _blob(case)
            case_tokens = _tokens(case_text)
            shared = obj_tokens & case_tokens
            if len(shared) < 2:
                continue
            seq += 1
            low_case = case_text.lower()
            if any(w in low_case or w in case_text for w in _FAILURE_WORDS):
                link_type = "contradicts"
            elif any(w in low_case or w in case_text for w in _SUCCESS_WORDS):
                link_type = "instantiates"
            else:
                link_type = "supports"
            case_id = _case_id(case, i)
            links.append({
                "link_id": f"link:{obj.get('id')}:{case_id}:{seq}",
                "knowledge_object_id": obj.get("id"),
                "paper_case_id": case_id,
                "link_type": link_type,
                "paper_experiment_id": case.get("experiment_id", ""),
                "shared_entities": sorted(shared),
                "shared_conditions": [],
                "differences": ["textbook principle is organism/condition-general; paper case is a single specific instance - do not treat this link as proof of the general principle"],
                "transferability": "unconfirmed - requires human review before treating this as validating or refuting the principle",
                "evidence": [{"paper_case_id": case_id, "matched_tokens": sorted(shared)}],
                "confidence": 0.3,
            })

    status = "needs_review" if links else "succeeded"
    return {
        "output": {"paper_case_links": links}, "status": status, "errors": [],
        "provenance": {"step_version": VERSION, "source_ids": sorted({o.get("id", "").split(":", 1)[0] for o in objects}) if objects else []},
    }

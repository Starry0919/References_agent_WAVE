"""Conservative deterministic E1/E2/E3 checks for Skill08 V2."""
from __future__ import annotations

import json
import re
from typing import Any, Mapping

VERDICTS = {"verified", "unsupported", "unresolved", "conflicted"}
NEGATION = re.compile(r"\b(no|not|never|without|failed to|did not|does not|wasn't|weren't|不|未|无|没有|并未)\b", re.I)
UP = re.compile(r"\b(increas\w*|higher|enhanc\w*|improv\w*|upregulat\w*|升高|增加|提高|增强)\b", re.I)
DOWN = re.compile(r"\b(decreas\w*|lower|reduc\w*|diminish\w*|downregulat\w*|降低|减少|下降)\b", re.I)
UNCHANGED = re.compile(r"\b(unchanged|no significant|not significant|similar to|无显著|未显著|不变)\b", re.I)
CAUSAL = re.compile(r"\b(caus\w*|resulted in|led to|drives?|because|由于|导致|引起)\b", re.I)
ASSOCIATION = re.compile(r"\b(correlat\w*|associat\w*|linked to|相关|关联)\b", re.I)
NUMBER_UNIT = re.compile(r"(?<!\w)([-+]?\d+(?:\.\d+)?)\s*(%|fold|x|g/l|mg/l|µm|μm|um|mm|h|min|°c|℃|ph)?", re.I)
CONDITIONS = re.compile(r"\b(glucose|glycerol|lb|m9|aerobic|anaerobic|oxygen|iptg|arabinose|exponential|stationary|wt|wild[- ]type|control|parent)\b", re.I)
STOP = {"the", "and", "with", "from", "that", "this", "were", "was", "for", "into", "using", "used", "than", "value", "reported"}


def normalize(value: Any) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w.%µμ°℃/+\-]+", " ", str(value).casefold())).strip()


def claim_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def semantic_support(value: Any, quote: str, *, augmented_pair: tuple[str, str] | None = None) -> tuple[str, list[str]]:
    """Return passed/failed/unresolved/conflicted; never promotes lexical-only hits."""
    claim, evidence = augmented_pair or (claim_text(value), str(quote or ""))
    c, e = normalize(claim), normalize(evidence)
    if not c or not e:
        return "unresolved", ["empty claim or evidence"]

    c_neg, e_neg = bool(NEGATION.search(claim)), bool(NEGATION.search(evidence))
    if c_neg != e_neg and (UP.search(claim) or DOWN.search(claim) or UNCHANGED.search(claim)):
        return "conflicted", ["negation polarity differs"]

    c_dir = "up" if UP.search(claim) else "down" if DOWN.search(claim) else "same" if UNCHANGED.search(claim) else None
    e_dir = "up" if UP.search(evidence) else "down" if DOWN.search(evidence) else "same" if UNCHANGED.search(evidence) else None
    if c_dir and e_dir and c_dir != e_dir:
        return "conflicted", [f"direction differs: claim={c_dir}, evidence={e_dir}"]

    c_nums, e_nums = _number_units(claim), _number_units(evidence)
    if c_nums:
        for number, unit in c_nums:
            candidates = [(n, u) for n, u in e_nums if abs(n - number) <= max(1e-9, abs(number) * 1e-6)]
            if not candidates:
                return "conflicted", [f"numeric value {number:g} absent"]
            if unit and not any(_unit(u) == _unit(unit) for _, u in candidates):
                return "conflicted", [f"unit for {number:g} differs"]

    c_conditions = {m.group(0).casefold() for m in CONDITIONS.finditer(claim)}
    e_conditions = {m.group(0).casefold() for m in CONDITIONS.finditer(evidence)}
    if c_conditions and not c_conditions.issubset(e_conditions):
        return "unresolved", ["condition/comparison scope is incomplete"]

    if CAUSAL.search(claim) and ASSOCIATION.search(evidence) and not CAUSAL.search(evidence):
        return "conflicted", ["association does not entail causation"]

    tokens = {t for t in re.findall(r"[a-z0-9][a-z0-9_.-]{1,}|[\u4e00-\u9fff]{2,}", c) if t not in STOP and not t.isdigit()}
    matched = {t for t in tokens if t in e}
    if c in e or (tokens and len(matched) / len(tokens) >= 0.72):
        return "passed", []
    if tokens and not matched:
        return "failed", ["claim entities are absent from evidence"]
    return "unresolved", ["lexical overlap is insufficient for semantic support"]


def attribution_status(location: Mapping[str, Any], unit: Mapping[str, Any], *, experiment_anchors: set[str] | None = None) -> tuple[str, list[str]]:
    attribution = location.get("source_attribution")
    if attribution in {"background_citation", "included_study"}:
        return "failed", [f"source attribution is {attribution}, not the current experiment"]
    if attribution in {"author_inference", "model_inference"}:
        return "unresolved", [f"source attribution is {attribution}"]
    anchor = location.get("paragraph_id") or location.get("figure") or location.get("table") or location.get("supplement")
    if experiment_anchors is not None and anchor not in experiment_anchors:
        return "failed", ["anchor is not assigned to the candidate experiment"]
    section = str(unit.get("section") or "").casefold()
    if re.search(r"previous studies|related work|references", section):
        return "failed", ["anchor belongs to background literature"]
    if attribution != "current_article" and experiment_anchors is None:
        return "unresolved", ["current-article attribution is not explicit"]
    return "passed", []


def overall(existence: str, attribution: str, semantic: str) -> str:
    states = {existence, attribution, semantic}
    if states == {"passed"}:
        return "verified"
    if "conflicted" in states:
        return "conflicted"
    if "failed" in states:
        return "unsupported"
    return "unresolved"


def _number_units(text: str) -> list[tuple[float, str]]:
    return [(float(m.group(1)), _unit(m.group(2) or "")) for m in NUMBER_UNIT.finditer(text)]


def _unit(unit: str) -> str:
    return unit.casefold().replace("μ", "µ").replace("um", "µm").replace("℃", "°c")

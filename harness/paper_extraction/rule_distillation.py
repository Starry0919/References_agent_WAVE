r"""DDR → rule library distillation (老师 §4.5: 跨论文蒸馏的可泛化规则).

``knowledge/biological_rules/rules.json`` (RULE-001..009) was hand-authored
by manually synthesizing DDR-001..005 into cross-paper heuristics. Nothing
in the codebase updates that file, and nothing reads it for retrieval - it
is a one-time snapshot, not the "live rule library" §4.5 calls for. This
module closes that gap for *new* DDRs (whether hand-curated or produced by
``ddr_converter``) without touching the already-curated content for
DDR-001..005: RULE-001..009's own ``source_ddrs`` strings already reference
those five DDR ids, so a DDR already covered by an existing rule's
provenance is skipped rather than re-distilled into a near-duplicate entry
worded differently from the human-written one.

Only decision_chain steps with ``reason_nature in {机理推断, 文献类比}`` and
a non-null ``rule`` are eligible — the exact same gate ``ddr_converter``
already applies before writing ``rule`` in the first place, so this module
never has to re-derive "is this a reliable generalization" from scratch; it
only has to avoid re-litigating it.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from harness.config import PROJECT_ROOT

DDR_DIR = PROJECT_ROOT / "knowledge" / "ddr_database"
RULES_PATH = PROJECT_ROOT / "knowledge" / "biological_rules" / "rules.json"

_ELIGIBLE_REASON_NATURES = ("机理推断", "文献类比")
_DDR_ID_RE = re.compile(r"DDR-\d+")


def _load_ddrs() -> list[dict[str, Any]]:
    if not DDR_DIR.is_dir():
        return []
    records = []
    for f in sorted(DDR_DIR.glob("DDR-*.json")):
        try:
            record = json.loads(f.read_text(encoding="utf-8"))
            admission = record.get("knowledge_admission") or {}
            if admission.get("status") not in {"KNOWLEDGE_ADMISSION_ALLOWED", "KNOWLEDGE_ADMISSION_PARTIAL"}:
                continue
            if not admission.get("source_skill08_artifact_id") or not admission.get("admitted_ddr_candidates"):
                continue
            records.append(record)
        except (OSError, json.JSONDecodeError):
            continue
    return records


def _load_rules() -> dict[str, Any]:
    if not RULES_PATH.is_file():
        return {
            "_schema_version": "2.0",
            "_description": "规则库 — 从 DDR 决策链中跨论文蒸馏出的可泛化启发式规则。",
            "rules": [],
            "governance": {"total_rules": 0, "calibrated_rules": 0, "pending_calibration": 0, "notes": ""},
        }
    return json.loads(RULES_PATH.read_text(encoding="utf-8"))


def _already_covered_ddr_ids(rules_doc: dict[str, Any]) -> set[str]:
    """DDR ids already cited in some rule's provenance, so re-running
    distillation doesn't append a second, differently-worded entry for a DDR
    a human has already distilled by hand."""
    covered: set[str] = set()
    for rule in rules_doc.get("rules", []):
        for src in rule.get("source_ddrs", []):
            covered.update(_DDR_ID_RE.findall(str(src)))
    return covered


def _next_rule_id(rules_doc: dict[str, Any]) -> str:
    existing = [int(m.group(1)) for r in rules_doc.get("rules", []) if (m := re.match(r"RULE-(\d+)", r.get("rule_id", "")))]
    return f"RULE-{(max(existing) + 1) if existing else 1:03d}"


def _candidate_rules(ddr: dict[str, Any]) -> list[dict[str, Any]]:
    ddr_id = ddr.get("ddr_id", "")
    candidates = []
    for step in ddr.get("decision_chain", []):
        rule_text = step.get("rule")
        if not rule_text or step.get("reason_nature") not in _ELIGIBLE_REASON_NATURES:
            continue
        trigger_obs = (step.get("trigger") or {}).get("observation", "")
        candidates.append({
            "statement": rule_text,
            "trigger_conditions": [trigger_obs[:120]] if trigger_obs else [],
            "source_ddrs": [f"{ddr_id} (step {step.get('step')})"],
            "evidence_grading": step.get("evidence_grading"),
            "applicable_modules": [step.get("design_action")] if step.get("design_action") else [],
            "cross_references": [],
            "calibration_status": "pending",
        })
    return candidates


def distill_rules(*, write: bool = False) -> list[dict[str, Any]]:
    """Scan every DDR for eligible, not-yet-distilled rules.

    Parameters
    ----------
    write:
        If True, append the new candidates to ``rules.json`` on disk
        (assigning fresh ``rule_id``s and updating ``governance`` counts).
        Default False — callers should review candidates first, matching
        the "AI 半自动抽取,人工抽检" posture the rest of this pipeline uses
        (see ``ddr_converter.convert_extraction_to_ddr``'s ``auto_save``).

    Returns
    -------
    list[dict]
        The newly-proposed rule entries (without ``rule_id`` assigned yet
        when ``write=False``, since ids are only allocated at write time).
    """
    rules_doc = _load_rules()
    covered = _already_covered_ddr_ids(rules_doc)

    new_candidates: list[dict[str, Any]] = []
    for ddr in _load_ddrs():
        ddr_id = ddr.get("ddr_id", "")
        if not ddr_id or ddr_id in covered:
            continue
        new_candidates.extend(_candidate_rules(ddr))

    if write and new_candidates:
        for candidate in new_candidates:
            candidate["rule_id"] = _next_rule_id(rules_doc)
            rules_doc.setdefault("rules", []).append(candidate)
        gov = rules_doc.setdefault("governance", {})
        gov["total_rules"] = len(rules_doc["rules"])
        gov["calibrated_rules"] = sum(1 for r in rules_doc["rules"] if r.get("calibration_status") == "calibrated")
        gov["pending_calibration"] = gov["total_rules"] - gov["calibrated_rules"]
        RULES_PATH.parent.mkdir(parents=True, exist_ok=True)
        RULES_PATH.write_text(json.dumps(rules_doc, ensure_ascii=False, indent=2), encoding="utf-8")

    return new_candidates


def search_rules(query: str) -> list[dict[str, Any]]:
    """Keyword search over the rule library — the retrieval path §4.5/§5.3
    (自建 DB: 规则库) calls for, and that nothing previously read this file
    for. Empty query returns every rule (full browse)."""
    query_lower = query.strip().lower()
    words = [w for w in query_lower.split() if len(w) > 1]
    hits = []
    for rule in _load_rules().get("rules", []):
        if not query_lower:
            hits.append(rule)
            continue
        haystack = " ".join([
            rule.get("statement", ""),
            " ".join(rule.get("trigger_conditions", [])),
            " ".join(rule.get("applicable_modules", [])),
        ]).lower()
        if query_lower in haystack or any(w in haystack for w in words):
            hits.append(rule)
    return hits


def rule_source_ddr_ids(rule: dict[str, Any]) -> list[str]:
    """Extracts real `DDR-\\d+` ids out of a rule's free-text `source_ddrs`
    entries (e.g. ``"DDR-005 (Chen & Zeng 2018 色氨酸)"`` -> ``"DDR-005"``).
    Some entries name a paper with no matching DDR record at all (e.g.
    ``"丁醇论文(驱动力规则)"``) - those are silently skipped rather than
    fabricating an id, matching `rule_distillation._already_covered_ddr_ids`'s
    own convention.
    """
    ids: list[str] = []
    for src in rule.get("source_ddrs", []):
        ids.extend(m for m in _DDR_ID_RE.findall(str(src)) if m not in ids)
    return ids


def rules_citing_ddr_ids(ddr_ids: list[str]) -> list[str]:
    """Reverse of `rule_source_ddr_ids`: every `rule_id` whose own
    `source_ddrs` cites at least one of `ddr_ids` (老师 §Phase4 Round 2:
    "Design Decision → Rule → DDR" provenance needs to walk from a DDR back
    to the rule(s) distilled from it, not just forward from rule to DDR).
    Order follows `rules.json` (`RULE-001` first), not `ddr_ids` order.
    """
    wanted = set(ddr_ids)
    if not wanted:
        return []
    return [
        rule["rule_id"] for rule in _load_rules().get("rules", [])
        if wanted & set(rule_source_ddr_ids(rule))
    ]


def rule_as_knowledge_claim_view(rule: dict[str, Any]) -> dict[str, Any]:
    """Reshapes one rule-library entry into the "多个 DDR 支持的可迁移知识"
    Knowledge Claim shape 老师 §Phase4 asks for (statement/evidence/
    confidence/boundary) - *without* a second schema or storage layer:
    `knowledge/biological_rules/rules.json` already IS "DDR aggregation"
    (each rule's `source_ddrs` cites the DDRs it was distilled from,
    `evidence_grading` is the same 硬/软 vocabulary a DDR step uses) - this
    is a read-only view over that existing data, not a new claim object
    (老师 §第一阶段: "如果已有实现：不要重复建设").
    """
    ddr_ids = rule_source_ddr_ids(rule)
    hard = rule.get("evidence_grading") == "硬"
    calibrated = rule.get("calibration_status") == "calibrated"
    if hard and len(ddr_ids) >= 2:
        confidence = "high"
    elif hard or len(ddr_ids) >= 2:
        confidence = "medium"
    else:
        confidence = "low"
    boundary_parts = list(rule.get("trigger_conditions") or [])
    if not calibrated:
        boundary_parts.append("尚未完成人工校准（calibration_status=pending），规则表述需人工复核")
    boundary_parts.append("规则为跨论文蒸馏的启发式，不替代针对当前项目的实测验证")
    return {
        "claim_id": rule.get("rule_id"),
        "statement": rule.get("statement", ""),
        "evidence_ddr_ids": ddr_ids,
        "evidence_count": len(ddr_ids),
        "evidence_grading": rule.get("evidence_grading"),
        "confidence": confidence,
        "boundary": "；".join(boundary_parts),
        "applicable_modules": rule.get("applicable_modules", []),
        "calibration_status": rule.get("calibration_status"),
    }

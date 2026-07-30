r"""Dual-annotator calibration primitive (老师 §4.3 step 3: "规则字段由两人
独立写、再对齐,统一标注口径(解决'同一篇不同人抽出来不一样')").

Nothing in the codebase previously modeled a second annotator at all -
``extraction_meta`` only ever carried a single ``calibration_status``/
``human_review_status`` pair, with no place to put a second person's
independent draft or to detect where two drafts disagree. This module adds
that without changing the shape of an already-saved DDR's ``decision_chain``
(the canonical, reviewed record) - independent attempts live alongside it in
``extraction_meta.extraction_attempts``, and conflicts are computed on
demand rather than a stored derived value that could go stale.

``calibration_status`` already has a "disputed" value in
``knowledge/ddr_database/schema_v2.json`` — anticipated by the schema but
never set anywhere in the codebase before ``record_extraction_attempt``
below.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from harness.config import PROJECT_ROOT

DDR_DIR = PROJECT_ROOT / "knowledge" / "ddr_database"

# Fields worth flagging a disagreement on: the ones that gate downstream
# trust (module routing, evidence strength, whether a rule may exist at
# all) rather than free-text description fields where wording naturally
# varies between two annotators without being a "conflict".
_COMPARED_FIELDS = ("design_action", "evidence_grading", "reason_nature", "rule")


def _ddr_path(ddr_id: str) -> Path | None:
    for f in DDR_DIR.glob(f"{ddr_id}_*.json"):
        return f
    direct = DDR_DIR / f"{ddr_id}.json"
    return direct if direct.is_file() else None


def detect_conflicts(attempts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compare independent extraction attempts of the same paper, step by
    step, on the fields whose disagreement actually matters.

    Parameters
    ----------
    attempts:
        Each item: ``{"annotator": str, "decision_chain": [...]}``. Steps
        are matched across attempts by their ``step`` number — this assumes
        both annotators segmented the paper into the same number of steps
        in the same order, which will not always hold; a step-count
        mismatch itself is reported as a conflict (field ``"step_count"``)
        rather than silently comparing misaligned steps.

    Returns
    -------
    list[dict]
        One entry per (step, field) disagreement:
        ``{"step": int, "field": str, "values_by_annotator": {name: value}}``.
    """
    if len(attempts) < 2:
        return []

    conflicts: list[dict[str, Any]] = []
    step_counts = {a.get("annotator", "unknown"): len(a.get("decision_chain", [])) for a in attempts}
    if len(set(step_counts.values())) > 1:
        conflicts.append({"step": None, "field": "step_count", "values_by_annotator": step_counts})

    by_step: dict[int, dict[str, dict[str, Any]]] = {}
    for attempt in attempts:
        annotator = attempt.get("annotator", "unknown")
        for step in attempt.get("decision_chain", []):
            step_num = step.get("step")
            if step_num is None:
                continue
            by_step.setdefault(step_num, {})[annotator] = step

    for step_num in sorted(by_step):
        by_annotator = by_step[step_num]
        if len(by_annotator) < 2:
            continue
        for field in _COMPARED_FIELDS:
            values = {annotator: s.get(field) for annotator, s in by_annotator.items()}
            # Normalize via JSON so dict/list-shaped fields (none currently,
            # but future-proof) compare by value, not identity.
            distinct = {json.dumps(v, ensure_ascii=False, sort_keys=True) for v in values.values()}
            if len(distinct) > 1:
                conflicts.append({"step": step_num, "field": field, "values_by_annotator": values})

    return conflicts


def record_extraction_attempt(ddr_id: str, annotator: str, decision_chain: list[dict[str, Any]]) -> dict[str, Any]:
    """Append one annotator's independent draft to a saved DDR's
    ``extraction_meta.extraction_attempts``, recompute conflicts across all
    attempts recorded so far, and flip ``calibration_status`` to
    ``"disputed"`` the moment any conflict exists (moving it back to
    ``"in_progress"`` — never auto-"calibrated" — once conflicts clear, since
    agreement between two automated passes is not itself human sign-off).

    Raises
    ------
    FileNotFoundError
        If no DDR with this id exists on disk.
    """
    path = _ddr_path(ddr_id)
    if path is None:
        raise FileNotFoundError(f"no DDR file found for ddr_id={ddr_id!r}")

    ddr = json.loads(path.read_text(encoding="utf-8"))
    meta = ddr.setdefault("extraction_meta", {})
    attempts: list[dict[str, Any]] = meta.setdefault("extraction_attempts", [])
    attempts.append({
        "annotator": annotator,
        "decision_chain": decision_chain,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    })

    conflicts = detect_conflicts(attempts)
    meta["conflict_count"] = len(conflicts)
    if conflicts:
        meta["calibration_status"] = "disputed"
    elif len(attempts) >= 2 and meta.get("calibration_status") in (None, "pending", "disputed"):
        meta["calibration_status"] = "in_progress"

    path.write_text(json.dumps(ddr, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ddr_id": ddr_id, "attempts": len(attempts), "conflicts": conflicts, "calibration_status": meta["calibration_status"]}


def get_conflicts(ddr_id: str) -> list[dict[str, Any]]:
    """Recompute conflicts for a DDR's currently-recorded attempts (read-only
    — does not require submitting a new attempt first)."""
    path = _ddr_path(ddr_id)
    if path is None:
        raise FileNotFoundError(f"no DDR file found for ddr_id={ddr_id!r}")
    ddr = json.loads(path.read_text(encoding="utf-8"))
    attempts = (ddr.get("extraction_meta") or {}).get("extraction_attempts", [])
    return detect_conflicts(attempts)

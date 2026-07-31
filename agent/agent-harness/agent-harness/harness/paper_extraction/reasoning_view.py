"""Reshapes a saved DDR record's `decision_chain` + summary fields into the
"Dual-track Evidence Reasoning View" the literature-evidence detail page
renders (prompt/小组件_模块/论文实验设计思路的抽取/抽取详情页面.md): a
step-sequenced `agent_trace` (left column - observable analysis steps, never
raw chain-of-thought) and a step-sequenced `experimental_design` (right
column - SOP-style reconstruction), plus a flat `evidence_provenance` list
and a minimal `evidence_graph` for the two array outputs to stay in sync.

`engineering_problem` / `biological_diagnosis` / `engineering_hypothesis` /
`decision_chain` are present on every DDR-v2 record regardless of whether it
was hand-curated (DDR-001..005) or produced by
`ddr_converter.convert_extraction_to_ddr` - this module only reads those
shared top-level keys, so it works for both origins without needing the
pipeline-only `paper_extraction_detail` blob.
"""
from __future__ import annotations

from typing import Any

from harness.i18n import get_locale, t
from harness.translation.service import translate_batch

_GRADE_CONFIDENCE = {"硬": 0.9, "软": 0.6}


def _grade_to_confidence(grade: str | None) -> float | None:
    return _GRADE_CONFIDENCE.get(grade or "")


def _overall_confidence(chain: list[dict[str, Any]]) -> float | None:
    graded = [c for c in (_grade_to_confidence(s.get("evidence_grading")) for s in chain) if c is not None]
    return round(sum(graded) / len(graded), 2) if graded else None


def _step_evidence(step: dict[str, Any]) -> list[str]:
    evidence = step.get("evidence") or {}
    out = []
    for v in (evidence.get("source_location"), evidence.get("source")):
        if v and v not in out:
            out.append(v)
    return out


def build_agent_trace(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Fixed narrative shell (problem -> per-step diagnosis/intervention ->
    logic reconstruction -> evidence validation), populated from whatever
    the record actually has. Each per-decision-chain-step card carries
    `design_step_ref` pointing at the matching `experimental_design` step
    number so the frontend can sync-highlight; the three narrative cards
    (problem understanding / logic reconstruction / evidence validation)
    use `"all"` since they summarize across every design step.
    """
    problem = raw.get("engineering_problem") or {}
    diagnosis = raw.get("biological_diagnosis") or {}
    hypothesis_obj = raw.get("engineering_hypothesis") or {}
    chain = raw.get("decision_chain") or []

    # These per-step fields are raw source-paper text (English for most
    # papers, but hand-curated DDR-001..005 records carry Chinese-authored
    # equivalents) interpolated straight into the narrative shell below -
    # neither i18n.tsx nor harness/i18n.py's static dictionaries cover this
    # (they only translate UI chrome / generated narrative, not literature
    # content), so it goes through the LLM translation cache instead, one
    # batched call for the whole trace rather than one call per step.
    # Symmetric: a zh-CN viewer gets English fragments translated to
    # Chinese, an en-US viewer gets Chinese fragments translated to English -
    # `translate_batch`'s own needs-translation check skips whichever
    # fragments are already in the target language, so this is a no-op (no
    # LLM call) for content that doesn't need it either way.
    #
    # The surrounding narrative-shell labels ("问题理解"/"Problem
    # Understanding" etc. below) are fixed, not per-record content, so they
    # are hand-translated in `harness/i18n.py`'s CATALOG (`agent_trace.*`
    # keys) via `t()` instead - same convention as the diagnosis/design
    # generators' narrative strings, and no LLM/network call involved.
    translation_map: dict[str, str] = {}
    locale = get_locale()
    if locale in ("zh-CN", "en-US"):
        raw_texts: list[str] = []
        for s in chain:
            trigger = s.get("trigger") or {}
            raw_texts.append(trigger.get("reasoning") or "")
            raw_texts.append(trigger.get("observation") or "")
            raw_texts.append(s.get("implementation_detail") or "")
            raw_texts.append((s.get("result") or {}).get("metric") or "")
        raw_texts.append(hypothesis_obj.get("hypothesis") or "")
        raw_texts.append(hypothesis_obj.get("expected_effect") or "")
        unique_texts = list(dict.fromkeys(txt for txt in raw_texts if txt))
        if unique_texts:
            translation_map = dict(zip(unique_texts, translate_batch(unique_texts, locale)))

    def tr(text: str) -> str:
        return translation_map.get(text, text) if text else text

    steps: list[dict[str, Any]] = []
    idx = 1

    problem_statement = problem.get("problem_statement", "")
    if problem_statement:
        steps.append({
            "step": idx,
            "kind": "problem_understanding",
            "title": t("agent_trace.problem_understanding.title"),
            "status": "completed",
            "input": t("agent_trace.problem_understanding.input"),
            "operation": t("agent_trace.problem_understanding.operation"),
            "output": problem_statement,
            "confidence": _overall_confidence(chain),
            "evidence": list(problem.get("trigger_conditions") or []),
            "design_step_ref": "all",
        })
        idx += 1

    for s in chain:
        target = s.get("target") or {}
        trigger = s.get("trigger") or {}
        target_label = target.get("gene") or target.get("enzyme") or target.get("pathway") or "?"
        steps.append({
            "step": idx,
            "kind": "intervention",
            "title": t("agent_trace.intervention.title", target_label=target_label),
            "status": "completed",
            "input": trigger.get("source_location") or t("agent_trace.intervention.input_fallback"),
            "operation": tr(trigger.get("reasoning", "")),
            "output": tr(trigger.get("observation", "")),
            "confidence": _grade_to_confidence(s.get("evidence_grading")),
            "evidence": _step_evidence(s),
            "design_step_ref": s.get("step"),
        })
        idx += 1

    if not any(s.get("kind") == "intervention" for s in steps) and diagnosis.get("bottlenecks"):
        # decision_chain was empty but the record still carries a flat
        # bottleneck list (e.g. a legacy v1-only DDR) - surface it as one
        # aggregate step rather than silently dropping this content.
        steps.append({
            "step": idx,
            "kind": "intervention",
            "title": t("agent_trace.bottleneck.title"),
            "status": "completed",
            "input": t("agent_trace.intervention.input_fallback"),
            "operation": t("agent_trace.bottleneck.operation"),
            "output": list(diagnosis.get("bottlenecks") or []),
            "confidence": None,
            "evidence": list(diagnosis.get("observations") or []),
            "design_step_ref": "all",
        })
        idx += 1

    if hypothesis_obj.get("hypothesis"):
        modifications = "；".join(filter(None, (tr(s.get("implementation_detail") or "") for s in chain)))
        measurements = "；".join(filter(None, (tr((s.get("result") or {}).get("metric") or "") for s in chain)))
        steps.append({
            "step": idx,
            "kind": "logic_reconstruction",
            "title": t("agent_trace.logic_reconstruction.title"),
            "status": "completed",
            "input": t("agent_trace.logic_reconstruction.input"),
            "operation": t("agent_trace.logic_reconstruction.operation"),
            "output": {
                "problem": problem_statement,
                "hypothesis": tr(hypothesis_obj.get("hypothesis", "")),
                "modification": modifications,
                "measurement": measurements,
                "conclusion": tr(hypothesis_obj.get("expected_effect", "")),
            },
            "confidence": _overall_confidence(chain),
            "evidence": [],
            "design_step_ref": "all",
        })
        idx += 1

    if chain:
        hard = sum(1 for s in chain if s.get("evidence_grading") == "硬")
        sources: list[str] = []
        for s in chain:
            for loc in _step_evidence(s):
                if loc not in sources:
                    sources.append(loc)
        steps.append({
            "step": idx,
            "kind": "evidence_validation",
            "title": t("agent_trace.evidence_validation.title"),
            "status": "completed",
            "input": t("agent_trace.evidence_validation.input"),
            "operation": t("agent_trace.evidence_validation.operation"),
            "output": t("agent_trace.evidence_validation.output", hard=hard, total=len(chain)),
            "confidence": hard / len(chain) if chain else None,
            "evidence": sources,
            "design_step_ref": "all",
        })

    return steps


def build_experimental_design(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """SOP-style reconstruction, one card per decision_chain step. Falls
    back to the flat legacy `engineering_actions` list (v1 DDRs that predate
    decision_chain) so no hand-curated record renders empty.
    """
    chain = raw.get("decision_chain") or []
    design: list[dict[str, Any]] = []
    for s in chain:
        target = s.get("target") or {}
        trigger = s.get("trigger") or {}
        evidence = s.get("evidence") or {}
        result = s.get("result") or {}
        target_label = target.get("gene") or target.get("enzyme") or target.get("pathway") or ""
        title = " · ".join(filter(None, [s.get("implementation"), target_label])) or f"实验步骤 {s.get('step')}"

        result_str = ""
        if result.get("before") or result.get("after"):
            result_str = f"{result.get('before') or '—'} → {result.get('after') or '—'}"
            if result.get("fold_change"):
                result_str += f"（{result['fold_change']}）"
        elif result.get("metric"):
            result_str = str(result.get("metric") or "")

        design.append({
            "step": s.get("step"),
            "title": title,
            "problem": trigger.get("observation", ""),
            "hypothesis": trigger.get("reasoning", ""),
            "engineering_action": {
                "type": s.get("implementation", ""),
                "target": target_label,
                "modification": s.get("implementation_detail", ""),
            },
            "method": [m for m in [s.get("implementation"), evidence.get("source")] if m],
            "result": result_str,
            "evidence": _step_evidence(s),
            "evidence_grading": s.get("evidence_grading"),
            # reason_nature/alternatives/rule were computed by ddr_converter
            # (or hand-curated) but never reached this view or the frontend -
            # a reviewer calibrating evidence_grading had no way to also see
            # *why* the step was classified that way, or to catch a rule that
            # should have been suppressed. See 老师 §4.2: reason_nature is
            # the field that gates rule generation, so it has to be visible
            # wherever a human is asked to calibrate a step.
            "reason_nature": s.get("reason_nature"),
            "alternatives": [
                {"approach": a.get("approach", ""), "rejected_reason": a.get("rejected_reason", "")}
                if isinstance(a, dict) else {"approach": str(a), "rejected_reason": ""}
                for a in (s.get("alternatives") or [])
            ],
            "rule": s.get("rule"),
        })
    if design:
        return design

    actions = raw.get("engineering_actions") or []
    ep = raw.get("engineering_problem") or {}
    eh = raw.get("engineering_hypothesis") or {}
    fallback: list[dict[str, Any]] = []
    for i, a in enumerate(actions, start=1):
        fallback.append({
            "step": i,
            "title": a.get("modification_type") or f"实验步骤 {i}",
            "problem": ep.get("problem_statement", ""),
            "hypothesis": eh.get("hypothesis", ""),
            "engineering_action": {
                "type": a.get("modification_type", ""),
                "target": a.get("target", ""),
                "modification": a.get("gene_or_pathway", ""),
            },
            "method": list(a.get("validation") or []),
            "result": a.get("expected_effect", ""),
            "evidence": [a["source"]] if a.get("source") else [],
            "evidence_grading": None,
            "reason_nature": None,
            "alternatives": [],
            "rule": None,
        })
    return fallback


def build_evidence_provenance(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Flat claim -> source -> confidence list for the bottom traceability
    panel - the aggregated view of the same evidence each decision_chain
    step already carries individually.
    """
    chain = raw.get("decision_chain") or []
    items: list[dict[str, Any]] = []
    for s in chain:
        trigger = s.get("trigger") or {}
        evidence = s.get("evidence") or {}
        claim = trigger.get("observation") or evidence.get("description") or ""
        if not claim:
            continue
        items.append({
            "step": s.get("step"),
            "claim": claim,
            "source": evidence.get("source_location") or evidence.get("source") or "",
            "grading": s.get("evidence_grading"),
            "confidence": _grade_to_confidence(s.get("evidence_grading")),
        })
    return items


def build_evidence_graph(experimental_design: list[dict[str, Any]]) -> dict[str, Any]:
    """Minimal node/edge graph backing the "View Evidence Graph" action:
    design steps in sequence, each with its supporting evidence as leaf
    nodes. Not a general-purpose graph schema - just enough structure for
    the detail page's own flow-diagram rendering.
    """
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    prev_id: str | None = None
    for d in experimental_design:
        step_id = f"step-{d['step']}"
        nodes.append({"id": step_id, "type": "step", "label": d["title"]})
        seen_ids.add(step_id)
        if prev_id is not None:
            edges.append({"source": prev_id, "target": step_id, "type": "sequence"})
        prev_id = step_id
        for i, ev in enumerate(d.get("evidence") or []):
            ev_id = f"{step_id}-evidence-{i}"
            if ev_id in seen_ids:
                continue
            nodes.append({"id": ev_id, "type": "evidence", "label": ev})
            seen_ids.add(ev_id)
            edges.append({"source": ev_id, "target": step_id, "type": "supports"})
    return {"nodes": nodes, "edges": edges}


def build_header_summary(raw: dict[str, Any], has_design: bool) -> dict[str, Any]:
    chain = raw.get("decision_chain") or []
    grades = [s.get("evidence_grading") for s in chain if s.get("evidence_grading")]
    confidence: str | None = None
    if grades:
        hard_ratio = grades.count("硬") / len(grades)
        confidence = "high" if hard_ratio >= 0.7 else "medium" if hard_ratio >= 0.4 else "low"
    meta = raw.get("extraction_meta") or {}
    return {
        "status": "completed" if has_design else "pending",
        "evidence_confidence": confidence,
        "human_review_status": meta.get("human_review_status"),
    }

"""Step04 - decide which sections are worth extracting.

Scores every section on its *content* (keyword hits inside the paragraph
text), never on the heading alone, so a section titled "Feedback
Inhibition" with no engineering framing is not skipped, and a section
titled "History" that happens to discuss growth burden is not skipped
either (SKILL.md Step04: "不得因为章节标题不含'工程'就跳过").
"""
from __future__ import annotations

import re

VERSION = "0.1.0"

HIGH_VALUE_TOPICS = [
    "gene expression regulation", "enzyme kinetics", "feedback", "stress response",
    "membrane transport", "resource competition", "protein folding", "growth burden",
    "gene dosage", "metabolite toxicity", "evolutionary stability",
    "基因表达调控", "酶动力学", "代谢反馈", "应激响应", "膜转运", "资源竞争",
    "蛋白折叠", "细胞生长负担", "基因剂量", "代谢物毒性", "进化稳定性",
]
DEFINITION_MARKERS = ["is defined as", "refers to", "is a", "are a class of", "是指", "定义为", "被定义为"]
CAUSAL_MARKERS = ["because", "causes", "inhibits", "activates", "leads to", "导致", "抑制", "激活", "引起"]
DECISION_MARKERS_COND = ["if ", "when ", "如果", "当", "若"]
DECISION_MARKERS_ACT = ["should", "consider", "recommended", "建议", "应", "可以考虑"]
DESIGN_MARKERS = ["strategy", "approach", "engineering", "design pattern", "策略", "设计", "工程"]
VALIDATION_MARKERS = ["measure", "assay", "verify", "validate", "quantify", "检测", "验证", "测定", "定量"]
FAILURE_MARKERS = ["burden", "toxicity", "instability", "leak", "misfold", "escape", "resistance evolves",
                    "负担", "毒性", "不稳定", "泄漏", "折叠错误", "逃逸"]


def _score(blob, keywords):
    low = blob.lower()
    hits = sum(1 for k in keywords if k.lower() in low or k in blob)
    return min(1.0, hits / 4.0)


def _contains(blob, keywords):
    low = blob.lower()
    return any(k.lower() in low or k in blob for k in keywords)


def execute(request, **kwargs):
    ss = request["source_structure"]
    source_id = ss["source_id"]
    blocks = ss.get("blocks", [])

    groups = {}
    order = []
    for b in blocks:
        if b["block_type"] in {"chapter", "section"}:
            continue
        key = tuple(b["section_path"]) or (b["chapter_id"],)
        if key not in groups:
            groups[key] = {"blocks": [], "block_types": set()}
            order.append(key)
        groups[key]["blocks"].append(b)
        groups[key]["block_types"].add(b["block_type"])

    sections = []
    for key in order:
        info = groups[key]
        blob = "\n".join(b["text"] for b in info["blocks"])
        bio_score = max(_score(blob, HIGH_VALUE_TOPICS), _score(blob, DEFINITION_MARKERS + CAUSAL_MARKERS))
        eng_score = max(_score(blob, DESIGN_MARKERS), _score(blob, FAILURE_MARKERS), _score(blob, DECISION_MARKERS_ACT))
        target_score = bio_score if bio_score or eng_score else 0.0

        is_reference_or_exercise = info["block_types"] <= {"reference", "exercise"}
        if is_reference_or_exercise:
            action, reason = "metadata_only", "reference/exercise block; kept as metadata only, not a knowledge source."
        elif bio_score >= 0.4 or eng_score >= 0.25:
            action, reason = "extract_full", "keyword density indicates concept/mechanism or engineering-relevant content."
        elif bio_score > 0 or eng_score > 0:
            action, reason = "extract_partial", "some relevant keywords found; partial extraction recommended."
        else:
            action, reason = "metadata_only", "no biological or engineering keywords detected in section body."

        sections.append({
            "section_id": "/".join(key) if key else f"{source_id}:root",
            "relevance_to_biological_knowledge": round(bio_score, 2),
            "relevance_to_engineering_design": round(eng_score, 2),
            "relevance_to_target_system": round(target_score, 2),
            "contains_concepts": _contains(blob, DEFINITION_MARKERS),
            "contains_mechanisms": _contains(blob, CAUSAL_MARKERS),
            "contains_decision_rules": _contains(blob, DECISION_MARKERS_COND) and _contains(blob, DECISION_MARKERS_ACT),
            "contains_design_patterns": _contains(blob, DESIGN_MARKERS),
            "contains_validation_strategy": _contains(blob, VALIDATION_MARKERS),
            "contains_failure_modes": _contains(blob, FAILURE_MARKERS),
            "recommended_action": action,
            "reason": reason,
            "source_id": source_id,
            "block_ids": [b["block_id"] for b in info["blocks"]],
        })

    return {
        "output": sections, "status": "succeeded", "errors": [],
        "provenance": {"step_version": VERSION, "source_ids": [source_id]},
    }

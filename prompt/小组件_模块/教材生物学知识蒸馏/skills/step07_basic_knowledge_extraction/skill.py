"""Step07 - extract concepts, definitions and mechanisms from in-scope blocks.

Phase-1 deterministic pattern extraction (definition/causal connective
matching), the same "python_rule_extraction" style as
论文实验设计抽取/skills/skill07_experiment_extraction, not an LLM call.
Definitions and mechanisms are kept as separate object lists
(SKILL.md Step07 requirement 1), every object carries a source_statement
tied to its block_id, and textbook simplifications are flagged rather than
presented as complete mechanisms (requirement 7).
"""
from __future__ import annotations

import re

VERSION = "0.1.0"

_SENT_SPLIT = re.compile(r"(?<=[.!?。!?])\s+")

_DEF_EN = re.compile(r"^(?P<subject>[A-Z][\w()\- ]{1,60}?)\s+(?:is defined as|refers to|is a|is the)\s+(?P<definition>.+)$")
_DEF_ZH = re.compile(r"^(?P<subject>[^\s，,。：:]{1,20})(?:是指|被定义为|定义为)(?P<definition>.+)$")

_CAUSAL_VERBS_EN = ["inhibits", "activates", "represses", "induces", "causes", "leads to", "results in"]
_CAUSAL_VERBS_ZH = ["抑制", "激活", "促进", "阻遏", "导致", "引起"]
_NEGATIVE_VERBS = {"inhibits", "represses", "抑制", "阻遏"}
_POSITIVE_VERBS = {"activates", "induces", "促进", "激活"}

_ORGANISM_HINTS = [
    ("Escherichia coli", ["escherichia coli", "e. coli", "大肠杆菌"]),
    ("Saccharomyces cerevisiae", ["saccharomyces cerevisiae", "s. cerevisiae", "酿酒酵母"]),
    ("eukaryote (unspecified)", ["eukaryot", "真核"]),
    ("prokaryote (unspecified)", ["prokaryot", "细菌", "bacteria"]),
]
_SIMPLIFICATION_HINTS = ["simplif", "for simplicity", "idealized", "简化模型", "简化", "为便于理解"]


def _sentences(text):
    return [s.strip() for s in _SENT_SPLIT.split(text) if s.strip()]


def _organism_scope(text):
    low = text.lower()
    return [name for name, hints in _ORGANISM_HINTS if any(h in low or h in text for h in hints)]


def _causal_verb(sentence):
    low = sentence.lower()
    for v in _CAUSAL_VERBS_EN:
        if v in low:
            return v
    for v in _CAUSAL_VERBS_ZH:
        if v in sentence:
            return v
    return None


def _causal_direction(verb):
    if verb in _NEGATIVE_VERBS:
        return "negative"
    if verb in _POSITIVE_VERBS:
        return "positive"
    return "unspecified"


def _is_simplification(block):
    low = block["text"].lower()
    return block["block_type"] == "box" and any(h in low or h in block["text"] for h in _SIMPLIFICATION_HINTS)


def execute(request, **kwargs):
    ss = request["source_structure"]
    scope = request.get("extraction_scope", [])
    source_id = ss["source_id"]
    blocks_by_id = {b["block_id"]: b for b in ss.get("blocks", [])}

    eligible_ids = set()
    for section in scope:
        if section.get("recommended_action") in {"extract_full", "extract_partial"}:
            eligible_ids.update(section.get("block_ids", []))

    concepts, mechanisms = [], []
    warnings = []
    concept_seq = mechanism_seq = 0

    for block_id in eligible_ids:
        block = blocks_by_id.get(block_id)
        if not block or block["block_type"] not in {"paragraph", "box"}:
            continue
        simplification = _is_simplification(block)
        organism_scope = _organism_scope(block["text"])
        if not organism_scope:
            warnings.append({"code": "ORGANISM_SCOPE_UNCERTAIN", "message": f"{block_id}: no organism could be identified; scope left empty rather than defaulted.", "retryable": False, "source_id": source_id})

        for sentence in _sentences(block["text"]):
            m = _DEF_EN.match(sentence) or _DEF_ZH.match(sentence)
            if m:
                concept_seq += 1
                concepts.append({
                    "knowledge_id": f"{source_id}:concept:{concept_seq}",
                    "knowledge_type": "concept",
                    "name_zh": m.group("subject") if block["language"] == "zh" else "",
                    "name_en": m.group("subject") if block["language"] != "zh" else "",
                    "aliases_zh": [], "aliases_en": [],
                    "definition_zh": m.group("definition").strip() if block["language"] == "zh" else "",
                    "definition_en": m.group("definition").strip() if block["language"] != "zh" else "",
                    "entities": [], "relationships": [], "causal_direction": "",
                    "conditions": [], "exceptions": [],
                    "biological_scale": "unknown",
                    "organism_scope": organism_scope, "strain_scope": [], "environment_scope": [],
                    "source_statements": [{"block_id": block_id, "text": sentence, "source_anchor": block["source_anchor"]}],
                    "status": "normalized", "confidence": 0.55,
                    "pedagogical_simplification": simplification,
                })
                continue
            verb = _causal_verb(sentence)
            if verb:
                mechanism_seq += 1
                mechanisms.append({
                    "knowledge_id": f"{source_id}:mechanism:{mechanism_seq}",
                    "knowledge_type": "mechanism",
                    "name_zh": "", "name_en": "",
                    "aliases_zh": [], "aliases_en": [],
                    "definition_zh": sentence if block["language"] == "zh" else "",
                    "definition_en": sentence if block["language"] != "zh" else "",
                    "entities": [], "relationships": [{"predicate": verb, "raw_sentence": sentence}],
                    "causal_direction": _causal_direction(verb),
                    "conditions": [], "exceptions": [],
                    "biological_scale": "unknown",
                    "organism_scope": organism_scope, "strain_scope": [], "environment_scope": [],
                    "source_statements": [{"block_id": block_id, "text": sentence, "source_anchor": block["source_anchor"]}],
                    "status": "normalized", "confidence": 0.5,
                    "pedagogical_simplification": simplification,
                })

    status = "succeeded_with_warnings" if warnings else "succeeded"
    return {
        "output": {"concepts": concepts, "mechanisms": mechanisms},
        "status": status, "errors": warnings,
        "provenance": {"step_version": VERSION, "source_ids": [source_id]},
    }

"""Step10 - cross-source fusion, never a majority-vote overwrite.

Objects are only grouped when they share the same knowledge type and an
(near-)identical normalized name - nothing is merged on semantic
similarity alone in this phase. Every source that contributed to a group
is kept in source_specific_variants even when it disagrees with the rest
(SKILL.md 十一.10-12: "不得采用多数来源一致就覆盖少数来源的粗暴方式" /
"不得删除少数来源提出的重要限制"), and a differing organism_scope or
definition always produces an explicit conflict record rather than a
silently-picked winner.
"""
from __future__ import annotations

VERSION = "0.1.0"


def _display_name(obj):
    return (obj.get("name_en") or obj.get("name_zh") or obj.get("decision_topic") or "").strip().lower()


def _definition_text(obj):
    return (obj.get("definition_en") or obj.get("definition_zh") or obj.get("principle_statement_en")
            or obj.get("principle_statement_zh") or "").strip()


def execute(request, **kwargs):
    objects = request.get("knowledge_objects", [])
    groups = {}
    for obj in objects:
        name = _display_name(obj)
        if not name:
            continue
        key = (obj.get("type"), name)
        groups.setdefault(key, []).append(obj)

    canonical_objects, fusions, conflicts = [], [], []
    seq = 0

    for (obj_type, name), members in groups.items():
        source_ids = sorted({m["id"].split(":", 1)[0] for m in members})
        if len(source_ids) < 2 and len(members) < 2:
            continue
        seq += 1
        canonical_id = f"canonical:{obj_type}:{seq}"

        definitions = {m["id"]: _definition_text(m) for m in members}
        organisms = {m["id"]: tuple(sorted(m.get("organism_scope", []))) for m in members}
        distinct_definitions = {d for d in definitions.values() if d}
        distinct_organisms = {o for o in organisms.values() if o}
        is_cross_source = len(source_ids) > 1

        # A single source producing two slightly-worded extractions of the
        # same named object (e.g. one from its concept sentence, one from
        # its mechanism sentence) is our own extraction's duplication, not a
        # textbook disagreement - only cross-source variance is a real
        # "source_conflicts" candidate (SKILL.md 十.merge_relation vs
        # KNOWLEDGE_DUPLICATION).
        member_conflicts = []
        if is_cross_source and len(distinct_definitions) > 1:
            conflict_id = f"conflict:{canonical_id}:definition"
            conflicts.append({
                "conflict_id": conflict_id, "topic": name, "conflict_type": "definition",
                "claims": [{"knowledge_id": m["id"], "source_id": m["id"].split(":", 1)[0], "statement": definitions[m["id"]]} for m in members],
                "possible_explanation": ["different sources may emphasize different aspects, or one source may be a pedagogical simplification"],
                "impact_on_agent_use": "do not average or silently pick one definition; surface both to the user/reviewer",
                "resolution_status": "unresolved", "requires_human_review": True,
            })
            member_conflicts.append(conflict_id)
        if is_cross_source and len(distinct_organisms) > 1:
            conflict_id = f"conflict:{canonical_id}:organism_scope"
            conflicts.append({
                "conflict_id": conflict_id, "topic": name, "conflict_type": "organism_difference",
                "claims": [{"knowledge_id": m["id"], "source_id": m["id"].split(":", 1)[0], "organism_scope": list(organisms[m["id"]])} for m in members],
                "possible_explanation": ["sources describe the same named concept in different organisms; do not merge scope"],
                "impact_on_agent_use": "keep organism-specific variants separate; do not apply one organism's rule to another",
                "resolution_status": "unresolved", "requires_human_review": True,
            })
            member_conflicts.append(conflict_id)

        if member_conflicts:
            merge_relation = "conflicting"
        elif is_cross_source and len(distinct_organisms) > 1:
            merge_relation = "organism_specific_variant"
        elif not is_cross_source and len(distinct_definitions) > 1:
            merge_relation = "related_but_distinct"  # our own duplicate extraction (same source, different sentences), not a source disagreement
        else:
            merge_relation = "same_concept"
        confidences = []
        for m in members:
            c = m.get("confidence", 0.4)
            confidences.append(c.get("value", 0.4) if isinstance(c, dict) else c)
        fusion_confidence = round(sum(confidences) / len(confidences), 3) if confidences else 0.0
        if member_conflicts:
            fusion_confidence = round(fusion_confidence * 0.6, 3)

        canonical = {
            "canonical_knowledge_id": canonical_id,
            "canonical_name_zh": next((m.get("name_zh") for m in members if m.get("name_zh")), ""),
            "canonical_name_en": next((m.get("name_en") for m in members if m.get("name_en")), name),
            "merged_from": [m["id"] for m in members],
            "merge_relation": merge_relation,
            "shared_core": sorted(distinct_definitions) if len(distinct_definitions) <= 1 else [],
            "source_specific_variants": [{"knowledge_id": m["id"], "source_id": m["id"].split(":", 1)[0], "definition": definitions[m["id"]], "organism_scope": list(organisms[m["id"]])} for m in members],
            "organism_specific_variants": [{"organism_scope": list(o), "knowledge_ids": [m["id"] for m in members if tuple(sorted(m.get("organism_scope", []))) == o]} for o in distinct_organisms] if len(distinct_organisms) > 1 else [],
            "condition_specific_variants": [],
            "conflicts": member_conflicts,
            "unresolved_questions": [] if not member_conflicts else ["definition/scope divergence not yet reconciled by a human reviewer"],
            "provenance": [{"knowledge_id": m["id"], "source_id": m["id"].split(":", 1)[0]} for m in members],
            "fusion_confidence": fusion_confidence,
            "review_status": "pending_human_review" if member_conflicts else "auto_merged",
        }
        canonical_objects.append(canonical)
        fusions.append({"canonical_knowledge_id": canonical_id, "merged_from": canonical["merged_from"], "merge_relation": merge_relation})

    status = "needs_review" if conflicts else "succeeded"
    all_source_ids = sorted({o["id"].split(":", 1)[0] for o in objects}) if objects else []
    return {
        "output": {"canonical_knowledge_objects": canonical_objects, "cross_source_fusions": fusions, "source_conflicts": conflicts},
        "status": status, "errors": [],
        "provenance": {"step_version": VERSION, "source_ids": all_source_ids},
    }

"""Step08 - distill engineering principles out of mechanisms/concepts.

This is the step SKILL.md calls out as the most important one, and the one
most at risk of turning "the textbook explained a mechanism" into "the
textbook told me what to do" without saying so. Every principle here is
built from a small fixed library of engineering archetypes (feedback
resistance, competitive-pathway removal, burden reduction, toxicity
mitigation, cofactor balancing); a match only fires when the source text's
own causal/definition sentence contains the archetype's trigger keywords,
and the IF/THEN/BECAUSE/ONLY IF/DO NOT GENERALIZE/VALIDATE
BY/ALTERNATIVES structure is filled from the archetype template, never
free-generated. If the source sentence itself already contains a
recommendation verb (consider/may/建议/可以), derivation_type is
"normalized_from_source"; otherwise the archetype's engineering
implication goes beyond what the source literally said, so
derivation_type is "model_inference" and requires_human_review is forced
true (SKILL.md 3.8 / Step08 "推荐结构" / 十一.7).
"""
from __future__ import annotations

VERSION = "0.1.0"

_RECOMMEND_MARKERS = ["consider", "may", "can be", "recommended", "建议", "可以考虑", "可考虑", "可以"]

ARCHETYPES = [
    {
        "id": "feedback_resistance",
        "keywords": ["feedback", "end-product inhibition", "反馈抑制", "终产物抑制"],
        "name_zh": "反馈抗性酶工程", "name_en": "Feedback-Resistant Enzyme Engineering",
        "engineering_objective": ["relieve pathway flux limitation caused by end-product/allosteric feedback inhibition"],
        "trigger_conditions": ["the pathway's flux-controlling enzyme is subject to feedback/end-product inhibition by a pathway metabolite"],
        "required_preconditions": ["the inhibited step has been confirmed to be flux-controlling under the relevant condition", "the feedback mechanism (competitive/allosteric) is known well enough to target a site"],
        "recommended_actions": ["mutate the regulatory/allosteric site of the enzyme", "replace the enzyme with a feedback-insensitive homolog", "introduce a heterologous feedback-resistant enzyme"],
        "expected_effects": ["increased flux through the previously limited step"],
        "possible_side_effects": ["loss of native regulation can cause metabolite over-accumulation or growth burden downstream"],
        "failure_conditions": ["downstream steps or cofactor/precursor supply become newly limiting after desensitization"],
        "contraindications": ["the enzyme is not actually flux-controlling", "the pathway metabolite also serves an essential regulatory role elsewhere"],
        "alternatives": ["dynamic pathway regulation instead of permanent desensitization", "moderate enzyme dosage tuning rather than full feedback removal"],
        "validation_requirements": ["in vitro enzyme activity assay in presence/absence of the inhibitor", "intracellular metabolite concentration before/after", "production titer or flux measurement"],
    },
    {
        "id": "competitive_pathway_removal",
        "keywords": ["competing pathway", "competitive pathway", "branch pathway", "竞争支路", "支路"],
        "name_zh": "竞争支路去除", "name_en": "Competitive Pathway Removal",
        "engineering_objective": ["redirect precursor flux away from a competing branch toward the target product"],
        "trigger_conditions": ["a branch pathway consumes a precursor or cofactor shared with the target pathway"],
        "required_preconditions": ["the branch pathway is not required for growth or an essential function under the intended culture condition"],
        "recommended_actions": ["attenuate the competing branch (weak promoter, CRISPRi, degradation tag)", "use dynamic/conditional repression of the branch", "delete the branch only after confirming it is dispensable"],
        "expected_effects": ["more precursor/cofactor available to the target pathway"],
        "possible_side_effects": ["growth defect if the branch has an unrecognized essential role", "accumulation of the branch's own substrate to toxic levels"],
        "failure_conditions": ["the branch turns out to be conditionally essential (e.g., under stress or selection)"],
        "contraindications": ["the branch pathway is essential for growth under the culture condition actually used"],
        "alternatives": ["conditional knockout instead of permanent deletion", "partial knockdown to preserve some flux through the branch"],
        "validation_requirements": ["growth curve of the modified strain vs parent", "flux/titer of the target product", "branch-pathway metabolite levels"],
    },
    {
        "id": "burden_reduction",
        "keywords": ["growth burden", "metabolic burden", "生长负担", "代谢负担"],
        "name_zh": "代谢负担缓解", "name_en": "Metabolic Burden Reduction",
        "engineering_objective": ["reduce the fitness cost imposed by heterologous expression or pathway flux on host growth"],
        "trigger_conditions": ["heterologous expression or pathway activity measurably slows host growth or reduces yield"],
        "required_preconditions": ["burden has been attributed to a specific expression construct or pathway rather than an unrelated stress"],
        "recommended_actions": ["lower expression level (weaker promoter/RBS, lower copy number)", "stage expression temporally (induction after growth phase)", "balance pathway enzyme stoichiometry instead of maximizing every step"],
        "expected_effects": ["improved growth rate/yield trade-off"],
        "possible_side_effects": ["lower absolute pathway flux if expression is reduced too far"],
        "failure_conditions": ["burden persists after expression tuning, indicating a different bottleneck (e.g., toxic intermediate)"],
        "contraindications": ["burden is caused by product/intermediate toxicity rather than expression load; see toxicity mitigation instead"],
        "alternatives": ["toxicity mitigation", "chassis engineering for higher expression tolerance"],
        "validation_requirements": ["growth rate/doubling time under induced vs uninduced conditions", "plasmid/copy-number stability over passages", "pathway yield at each expression level tested"],
    },
    {
        "id": "toxicity_mitigation",
        "keywords": ["toxic", "toxicity", "毒性"],
        "name_zh": "代谢物毒性缓解", "name_en": "Metabolite Toxicity Mitigation",
        "engineering_objective": ["prevent a pathway intermediate or product from accumulating to growth-inhibitory levels"],
        "trigger_conditions": ["a pathway intermediate or product is reported to inhibit growth or viability above some concentration"],
        "required_preconditions": ["the toxic species and an approximate threshold are identified, not just a qualitative 'toxic' label"],
        "recommended_actions": ["increase downstream consumption rate of the toxic intermediate (pull strategy)", "add active efflux/export of the toxic species", "engineer host tolerance (e.g., stress-response overexpression)"],
        "expected_effects": ["reduced intracellular accumulation of the toxic species and improved viability at higher titers"],
        "possible_side_effects": ["export/tolerance engineering may itself add metabolic burden"],
        "failure_conditions": ["toxicity mechanism is not concentration-dependent in the assumed way (e.g., structural damage vs enzyme inhibition)"],
        "contraindications": ["none identified in source; treat as organism/condition specific until validated"],
        "alternatives": ["burden reduction if the issue is expression load rather than the metabolite itself"],
        "validation_requirements": ["dose-response growth assay against the suspected toxic species", "intracellular/extracellular concentration of the species", "viability/production titer at increasing titers"],
    },
    {
        "id": "cofactor_balancing",
        "keywords": ["cofactor", "nadh", "nadph", "atp balance", "辅因子"],
        "name_zh": "辅因子平衡", "name_en": "Cofactor Balancing",
        "engineering_objective": ["match cofactor (e.g., NAD(P)H/ATP) supply to the demand of the target pathway"],
        "trigger_conditions": ["the target pathway's redox or energy cofactor demand is reported as a limiting factor"],
        "required_preconditions": ["the specific cofactor and the direction of imbalance (excess vs deficit) are identified"],
        "recommended_actions": ["swap an enzyme's cofactor specificity to match the more abundant pool", "add or remove a transhydrogenase/regenerating reaction", "co-express a cofactor-regenerating pathway"],
        "expected_effects": ["improved pathway flux or yield per unit substrate"],
        "possible_side_effects": ["shifting one cofactor pool can create a new imbalance in another pathway that shares it"],
        "failure_conditions": ["the identified cofactor is not actually rate-limiting once tested"],
        "contraindications": ["cofactor pools are already balanced under the intended culture condition"],
        "alternatives": ["substrate/condition changes that shift cofactor pools without genetic modification"],
        "validation_requirements": ["intracellular cofactor ratio measurement (e.g., NADH/NAD+)", "pathway flux/yield before and after", "growth phenotype under the modified cofactor regime"],
    },
]


def _matched_archetypes(text):
    low = text.lower()
    return [a for a in ARCHETYPES if any(k in low or k in text for k in a["keywords"])]


def _has_recommendation(text):
    low = text.lower()
    return any(m in low or m in text for m in _RECOMMEND_MARKERS)


def _source_id_of(knowledge_id):
    return knowledge_id.split(":", 1)[0]


def execute(request, **kwargs):
    concepts = request.get("concepts", [])
    mechanisms = request.get("mechanisms", [])
    principles = []
    constraints = []
    review_flags = []
    seq = 0

    for obj in mechanisms + concepts:
        definition_text = ((obj.get("definition_en") or "") + " " + (obj.get("definition_zh") or "")).strip()
        match_text = " ".join(filter(None, [obj.get("name_en"), obj.get("name_zh"), definition_text])).strip()
        text = definition_text or match_text
        if not match_text:
            continue
        matches = _matched_archetypes(match_text)
        explicit_recommendation = _has_recommendation(match_text)
        source_id = _source_id_of(obj["knowledge_id"])

        for archetype in matches:
            seq += 1
            derivation_type = "normalized_from_source" if explicit_recommendation else "model_inference"
            organism_scope = obj.get("organism_scope", [])
            do_not_generalize = ["do not extend beyond the organism/strain scope actually evidenced by the source"]
            if not organism_scope:
                do_not_generalize.append("source did not specify an organism; do NOT assume this applies to E. coli K-12 or any other specific chassis")
            principle = {
                "principle_id": f"{source_id}:principle:{seq}",
                "name_zh": archetype["name_zh"], "name_en": archetype["name_en"],
                "principle_statement_zh": "",
                "principle_statement_en": (
                    f"IF {archetype['trigger_conditions'][0]}, THEN CONSIDER {'; '.join(archetype['recommended_actions'])}, "
                    f"BECAUSE {text}, ONLY IF {'; '.join(archetype['required_preconditions'])}, "
                    f"DO NOT GENERALIZE TO other organisms/strains without independent evidence, "
                    f"VALIDATE BY {'; '.join(archetype['validation_requirements'])}, "
                    f"ALTERNATIVES {'; '.join(archetype['alternatives'])}."
                ),
                "biological_basis": [text],
                "engineering_objective": archetype["engineering_objective"],
                "trigger_conditions": archetype["trigger_conditions"],
                "required_preconditions": archetype["required_preconditions"],
                "recommended_actions": archetype["recommended_actions"],
                "expected_effects": archetype["expected_effects"],
                "possible_side_effects": archetype["possible_side_effects"],
                "failure_conditions": archetype["failure_conditions"],
                "contraindications": archetype["contraindications"],
                "do_not_generalize_to": do_not_generalize,
                "alternatives": archetype["alternatives"],
                "validation_requirements": archetype["validation_requirements"],
                "dbtl_stage": ["design", "test"],
                "organism_scope": organism_scope, "strain_scope": obj.get("strain_scope", []),
                "evidence": [{"knowledge_id": obj["knowledge_id"], "source_statements": obj.get("source_statements", [])}],
                "derivation_type": derivation_type,
                "confidence": 0.6 if derivation_type == "normalized_from_source" else 0.35,
                "requires_human_review": derivation_type == "model_inference",
                "pedagogical_simplification": obj.get("pedagogical_simplification", False),
            }
            principles.append(principle)
            if principle["requires_human_review"]:
                review_flags.append({"code": "OVERGENERALIZATION_RISK", "message": f"{principle['principle_id']}: engineering action inferred by the model from a mechanism description, not stated as a recommendation in the source.", "retryable": False, "source_id": source_id, "affected_objects": [principle["principle_id"]]})

        if not matches and obj.get("causal_direction") and obj["causal_direction"] != "unspecified":
            constraints.append({
                "constraint_id": f"{source_id}:constraint:{seq}",
                "description": text, "constraint_type": "unclassified_causal_relationship",
                "evidence": [{"knowledge_id": obj["knowledge_id"]}],
                "derivation_type": "explicit_in_source", "confidence": 0.5,
            })

    status = "needs_review" if review_flags else "succeeded"
    return {
        "output": {"engineering_principles": principles, "constraints_and_tradeoffs": constraints},
        "status": status, "errors": review_flags,
        "provenance": {"step_version": VERSION, "source_ids": sorted({_source_id_of(o["knowledge_id"]) for o in mechanisms + concepts})},
    }

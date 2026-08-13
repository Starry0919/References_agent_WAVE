from __future__ import annotations

import re

from .models import HostRelation, PaperCandidate, RelevanceAssessment, RelevanceTier, ScientificLiteratureRequest


K12_DERIVATIVES = {"mg1655", "w3110", "bw25113"}
ENGINEERING = {"engineer", "overexpress", "knockout", "deletion", "promoter", "feedback resistant", "mutant", "flux", "transporter", "adaptive laboratory evolution", "pathway"}
PRODUCTION = {"production", "overproduction", "biosynthesis", "titer", "yield", "productivity", "fermentation"}
EXPERIMENTAL = {"g/l", "mg/l", "mmol", "mol/mol", "fed-batch", "batch fermentation"}
CLINICAL = {"infection", "clinical", "patient", "pathogenic", "virulence", "sepsis", "urinary tract", "food safety", "contamination", "diagnostic", "assay", "detection"}


def assess(candidate: PaperCandidate, request: ScientificLiteratureRequest) -> RelevanceAssessment:
    title = candidate.canonical_title.casefold()
    abstract = (candidate.abstract or "").casefold()
    text = f"{title} {abstract}"
    title_product = bool(re.search(r"(?<!hydroxy)(?<!hydroxy-)\b(?:l-)?tryptophan\b", title))
    product_anywhere = bool(re.search(r"(?<!hydroxy)(?<!hydroxy-)\b(?:l-)?tryptophan\b", text))
    other_target = any(x in title for x in ("5-hydroxytryptophan", "hydroxytryptophan", "indole production", "succinate production"))

    organism = 1.0 if any(x in text for x in ("escherichia coli", "e. coli", "e coli")) else 0.0
    exact_k12 = "k-12" in text or "k12" in text
    derivatives = sorted(x for x in K12_DERIVATIVES if x in text)
    if exact_k12:
        relation, strain = HostRelation.EXACT, 1.0
    elif derivatives:
        relation, strain = HostRelation.K12_DERIVATIVE, 0.9
    elif organism:
        relation, strain = HostRelation.RELATED_ECOLI, 0.45
    elif any(x in text for x in ("bacillus", "corynebacterium", "saccharomyces", "pseudomonas")):
        relation, strain = HostRelation.NON_TARGET, 0.0
    else:
        relation, strain = HostRelation.UNKNOWN, 0.0

    product = 1.0 if product_anywhere and not other_target else 0.0
    eng_hits = sorted(x for x in ENGINEERING if x in text)
    production_hits = sorted(x for x in PRODUCTION if x in text)
    experimental_hits = sorted(x for x in EXPERIMENTAL if x in text)
    clinical_hits = sorted(x for x in CLINICAL if x in text)
    engineering = min(1.0, len(eng_hits) / 2) if eng_hits else 0.0
    production = min(1.0, len(production_hits) / 2) if production_hits else 0.0
    experimental = min(1.0, len(experimental_hits) / 2) if experimental_hits else 0.0
    availability = 1.0 if candidate.oa_urls else 0.0

    reasons: list[str] = []
    if relation == HostRelation.EXACT: reasons.append("HOST_EXACT")
    elif relation == HostRelation.K12_DERIVATIVE: reasons.append("HOST_K12_DERIVATIVE")
    elif relation == HostRelation.RELATED_ECOLI: reasons.append("HOST_RELATED_ECOLI")
    elif relation == HostRelation.NON_TARGET: reasons.append("NON_TARGET_HOST")
    if product: reasons.append("PRODUCT_EXACT")
    if other_target: reasons.append("OTHER_PRODUCT_TARGET")
    if eng_hits: reasons.append("ENGINEERING_INTERVENTION")
    if production_hits: reasons.append("PRODUCTION_OBJECTIVE")
    if experimental_hits: reasons.append("PRODUCTION_METRIC")
    if candidate.is_review: reasons.append("REVIEW_ARTICLE")
    if clinical_hits: reasons.append("CLINICAL_CONTEXT")
    if not eng_hits: reasons.append("NON_ENGINEERING")

    # Availability is deliberately absent from the scientific score.
    score = 0.22 * organism + 0.18 * strain + 0.22 * product + 0.17 * engineering + 0.13 * production + 0.08 * experimental
    score = max(0, score - (0.35 if clinical_hits else 0) - (0.12 if candidate.is_review else 0))

    title_engineering = any(x in title for x in ENGINEERING)
    title_production = any(x in title for x in PRODUCTION)
    direct = organism and strain >= 0.9 and title_product and engineering and production and experimental and not candidate.is_review
    if clinical_hits or (relation == HostRelation.NON_TARGET and not (engineering and product)):
        tier = RelevanceTier.EXCLUDE
    elif direct:
        tier = RelevanceTier.TIER_1
    elif organism and title_product and product and engineering and production and (title_engineering or title_production or experimental) and not candidate.is_review:
        tier = RelevanceTier.TIER_2
    elif product and (engineering or production) and not clinical_hits:
        tier = RelevanceTier.TIER_3
        reasons.append("MECHANISTIC_ONLY")
    else:
        tier = RelevanceTier.BACKGROUND

    rationale = "; ".join([
        f"host={relation.value}", f"product={'exact' if product else 'absent'}",
        f"engineering={','.join(eng_hits[:4]) or 'absent'}", f"production={','.join(production_hits[:4]) or 'absent'}",
        f"experimental={','.join(experimental_hits[:3]) or 'not observed in metadata'}",
        f"publication={'review' if candidate.is_review else 'primary/other'}",
    ])
    return RelevanceAssessment(
        decision=tier, score=round(min(score, 1), 4), organism_match=organism, strain_match=strain,
        product_match=product, engineering_intervention_match=engineering,
        production_objective_match=production, experimental_evidence_match=experimental,
        fulltext_availability=availability, host_relation=relation,
        reason_codes=list(dict.fromkeys(reasons)), rationale=rationale,
    )

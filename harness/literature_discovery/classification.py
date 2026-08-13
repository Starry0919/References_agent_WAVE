from __future__ import annotations

import hashlib
import re
from typing import Any

from pydantic import BaseModel, Field

from .models import PaperCandidate
from .taxonomy import (ENGINEERING_MODES, EVIDENCE_MODALITIES, EVIDENCE_STRENGTHS,
                       KNOWLEDGE_CONTRIBUTIONS, PUBLICATION_FORMS, RESEARCH_DESIGNS)


class ClassificationLabel(BaseModel):
    value: str
    confidence: str = "MEDIUM"
    score: float = Field(default=.7, ge=0, le=1)
    evidence_source: str
    evidence_location: str
    reason_codes: list[str] = Field(default_factory=list)


class ClassificationAxis(BaseModel):
    labels: list[ClassificationLabel]


class LiteratureClassification(BaseModel):
    contract_version: str = "literature-classification/2.0"
    stage: str
    publication_form: ClassificationAxis
    research_design: ClassificationAxis
    engineering_modes: ClassificationAxis
    evidence_modalities: ClassificationAxis
    knowledge_contributions: ClassificationAxis
    evidence_strength: ClassificationAxis
    classification_conflict: bool = False
    conflict_fields: list[str] = Field(default_factory=list)
    resolution: str | None = None
    provenance: list[dict[str, Any]] = Field(default_factory=list)
    classification_id: str


def _label(value, source, location, reason, score=.78):
    band = "HIGH" if score >= .85 else "MEDIUM" if score >= .6 else "LOW" if score > 0 else "UNKNOWN"
    return ClassificationLabel(value=value, confidence=band, score=score, evidence_source=source,
                               evidence_location=location, reason_codes=[reason])


def _matches(text, mapping, source, location):
    out = []
    for value, patterns in mapping.items():
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                out.append(_label(value, source, location, f"EXPLICIT_{value}", .88 if source == "fulltext" else .76))
                break
    return out


REVIEW_PATTERNS = [
    ("SYSTEMATIC_REVIEW_WITH_META_ANALYSIS", [r"systematic review.{0,80}meta[- ]analysis|meta[- ]analysis.{0,80}systematic review"]),
    ("SCOPING_REVIEW", [r"\bscoping review\b"]), ("SYSTEMATIC_REVIEW", [r"\bsystematic review\b"]),
    ("META_ANALYSIS", [r"\bmeta[- ]analysis\b"]), ("STATE_OF_THE_ART_REVIEW", [r"state[- ]of[- ]the[- ]art review"]),
    ("MINI_REVIEW", [r"\bmini[- ]review\b"]), ("CRITICAL_REVIEW", [r"\bcritical review\b"]),
    ("METHODOLOGICAL_REVIEW", [r"methodological review"]), ("TECHNOLOGY_REVIEW", [r"technology review"]),
    ("NARRATIVE_REVIEW", [r"narrative review"]),
]


def _publication(candidate, title, abstract, fulltext):
    sources = [("fulltext", fulltext, "document"), ("abstract", abstract, "abstract"), ("title", title, "title")]
    signals = []
    for source, text, location in sources:
        if not text: continue
        for value, patterns in REVIEW_PATTERNS:
            if any(re.search(p, text, re.I) for p in patterns):
                signals.append(_label(value, source, location, f"EXPLICIT_{value}", .94 if source == "fulltext" else .82))
                break
        else:
            if re.search(r"\b(this|the present|a) review\b|\breview article\b", text, re.I):
                signals.append(_label("REVIEW", source, location, "EXPLICIT_REVIEW", .9 if source == "fulltext" else .72))
    metadata = " ".join([candidate.publication_type or "", *[str(x.raw.get("type", "")) for x in candidate.source_records]])
    metadata_review = candidate.is_review or bool(re.search(r"review|meta-analysis", metadata, re.I))
    if metadata_review: signals.append(_label("REVIEW", "publication_type_metadata", "source_records", "METADATA_REVIEW", .74))
    special = {"PROTOCOL": r"\bprotocol\b", "METHODS_PAPER": r"\bmethod(?:s|ological)?\b",
               "DATABASE_PAPER": r"\bdatabase\b", "SOFTWARE_PAPER": r"\bsoftware|toolbox|package\b",
               "DATA_PAPER": r"\bdata descriptor|data paper\b", "RESOURCE_PAPER": r"\bresource\b",
               "BENCHMARK_PAPER": r"\bbenchmark(?:ing)?\b", "CORRECTION": r"^correction\b", "RETRACTION": r"^retraction\b"}
    for value, pat in special.items():
        if re.search(pat, title, re.I): signals.append(_label(value, "title", "title", f"TITLE_{value}", .76)); break
    if signals:
        rank = {value: i for i, (value, _) in enumerate(REVIEW_PATTERNS)}
        signals.sort(key=lambda x: (x.evidence_source == "fulltext", x.value in rank, x.score), reverse=True)
        return [signals[0]], signals
    primary = bool(re.search(r"\bwe\b.{0,100}\b(?:constructed|engineered|investigated|demonstrate|report|measured)\b|our results|materials and methods", f"{abstract} {fulltext}", re.I))
    return [_label("ORIGINAL_RESEARCH" if primary else "UNKNOWN", "abstract" if abstract else "metadata", "abstract" if abstract else "record", "PRIMARY_SIGNAL" if primary else "INSUFFICIENT_FORM_EVIDENCE", .72 if primary else 0)], []


DESIGN = {
 "HIGH_THROUGHPUT_SCREENING":[r"high[- ]throughput screening"], "SCREENING":[r"\bscreen(?:ing|ed)\b"],
 "EVOLUTIONARY_EXPERIMENT":[r"adaptive laboratory evolution|experimental evolution"], "BIOPROCESS_EXPERIMENT":[r"fed[- ]batch|fermentation|bioreactor"],
 "MULTI_OMICS":[r"multi[- ]omics"], "OMICS_EXPERIMENT":[r"transcriptom|proteom|metabolom|fluxom"],
 "MODEL_VALIDATION":[r"model validation|validated (?:the )?model"], "MODEL_DEVELOPMENT":[r"developed .{0,30}model|genome[- ]scale model"],
 "IN_SILICO_DESIGN":[r"in silico|computational design"], "COMPUTATIONAL":[r"computational|simulation|machine learning"],
 "BENCHMARK":[r"benchmark(?:ing)?"], "DATABASE_CONSTRUCTION":[r"database (?:construction|development)|we present .{0,20}database"],
 "SOFTWARE_DEVELOPMENT":[r"software|web server|toolbox|package"], "RESOURCE_CONSTRUCTION":[r"resource construction|resource paper|dataset"],
 "METHOD_DEVELOPMENT":[r"new method|method development|we developed .{0,30}(?:method|assay)"],
 "MECHANISTIC_EXPERIMENT":[r"mechanis(?:m|tic)|regulatory mechanism"], "WET_LAB_EXPERIMENTAL":[r"we (?:constructed|cultured|engineered|measured)|fermentation|knockout|overexpress"],
}
ENGINEERING = {
 "GENE_KNOCKOUT":[r"gene knockout|\bknockout\b"], "GENE_DELETION":[r"gene deletion|\bdeleted\b|Δ[a-z]"],
 "GENE_OVEREXPRESSION":[r"overexpress"], "GENE_AMPLIFICATION":[r"gene amplification|copy number"],
 "PROMOTER_ENGINEERING":[r"promoter(?:.{0,30})?(?:engineering|replacement|library)|promoter swapping"], "RBS_ENGINEERING":[r"RBS engineering|ribosome binding site"],
 "ATTENUATOR_ENGINEERING":[r"attenuator (?:engineering|inactivation)"], "CRISPR_ENGINEERING":[r"CRISPR"],
 "METABOLIC_ENGINEERING":[r"metabolic engineering|metabolically engineered"], "PATHWAY_ENGINEERING":[r"pathway engineering"],
 "PRECURSOR_ENGINEERING":[r"precursor (?:engineering|supply)"], "COFACTOR_ENGINEERING":[r"cofactor engineering|cofactor balance"],
 "TRANSPORTER_ENGINEERING":[r"transporter engineering|efflux pump|transport engineering"], "REGULATORY_ENGINEERING":[r"regulatory engineering"],
 "ENZYME_ENGINEERING":[r"enzyme engineering|directed evolution"], "PROTEIN_ENGINEERING":[r"protein engineering"],
 "DYNAMIC_REGULATION":[r"dynamic regulation|dynamic control"], "BIOSENSOR_ENGINEERING":[r"biosensor"],
 "ADAPTIVE_LABORATORY_EVOLUTION":[r"adaptive laboratory evolution|\bALE\b"], "FLUX_REDISTRIBUTION":[r"flux redistribution|redirected flux"],
 "COMPETING_PATHWAY_REMOVAL":[r"competing pathway|byproduct pathway"], "HETEROLOGOUS_PATHWAY":[r"heterologous pathway"],
 "FED_BATCH_OPTIMIZATION":[r"fed[- ]batch optimization"], "FERMENTATION_OPTIMIZATION":[r"fermentation optimization|optimized fermentation"],
 "MEDIA_OPTIMIZATION":[r"medium optimization|media optimization"], "PROCESS_ENGINEERING":[r"process engineering|process optimization"],
}
MODALITY = {
 "GENETIC":[r"knockout|deletion|overexpress|mutant|genetic"], "TRANSCRIPTOMIC":[r"transcriptom|RNA[- ]seq"], "PROTEOMIC":[r"proteom"],
 "METABOLOMIC":[r"metabolom"], "FLUXOMIC":[r"fluxom|13C metabolic flux|flux analysis"], "FERMENTATION":[r"fermentation|bioreactor|fed[- ]batch"],
 "BIOCHEMICAL":[r"biochemical"], "ENZYME_ACTIVITY":[r"enzyme activity"], "GROWTH":[r"growth rate|biomass"],
 "TITER":[r"\btiter\b|\d+(?:\.\d+)?\s*g/L"], "YIELD":[r"\byield\b|mol/mol"], "PRODUCTIVITY":[r"productivity"],
 "CONCENTRATION":[r"concentration"], "COMPUTATIONAL_PREDICTION":[r"computational prediction|in silico"], "MODEL_SIMULATION":[r"model simulation|simulated"],
 "DATASET":[r"dataset"], "RESOURCE":[r"database|resource"],
}


def classify(candidate: PaperCandidate, fulltext: str | None = None, previous: LiteratureClassification | dict | None = None):
    title, abstract, body = candidate.canonical_title or "", candidate.abstract or "", fulltext or ""
    stage, source = ("fulltext", "fulltext") if body else ("metadata", "metadata")
    text = " ".join([title, abstract, body])
    form, form_signals = _publication(candidate, title, abstract, body)
    designs = _matches(text, DESIGN, source, "document" if body else "title+abstract")
    if form[0].value.endswith("REVIEW") or form[0].value in {"REVIEW", "META_ANALYSIS", "SYSTEMATIC_REVIEW_WITH_META_ANALYSIS"}:
        designs.append(_label("LITERATURE_SYNTHESIS", source, "document" if body else "record", "REVIEW_DESIGN", .9))
    computational = any(x.value in {"COMPUTATIONAL", "MODEL_DEVELOPMENT", "IN_SILICO_DESIGN"} for x in designs)
    wet = any(x.value == "WET_LAB_EXPERIMENTAL" for x in designs)
    if computational and wet: designs.append(_label("HYBRID_COMPUTATIONAL_EXPERIMENTAL", source, "document", "HYBRID_SIGNALS", .9))
    engineering = _matches(text, ENGINEERING, source, "document" if body else "title+abstract")
    modalities = _matches(text, MODALITY, source, "document" if body else "title+abstract")
    review_like = any(x.value in {"REVIEW", "NARRATIVE_REVIEW", "SYSTEMATIC_REVIEW", "SCOPING_REVIEW", "META_ANALYSIS", "SYSTEMATIC_REVIEW_WITH_META_ANALYSIS", "STATE_OF_THE_ART_REVIEW", "MINI_REVIEW", "CRITICAL_REVIEW", "METHODOLOGICAL_REVIEW", "TECHNOLOGY_REVIEW"} for x in form)
    contribution = []
    if review_like: contribution += [_label("REVIEW_SYNTHESIS", source, "record", "REVIEW_VALUE", .9), _label("ENGINEERING_STRATEGY", source, "record", "SYNTHESIS_VALUE", .7)]
    if engineering: contribution.append(_label("ENGINEERING_STRATEGY", source, "document", "ENGINEERING_SIGNAL", .78))
    if any(x.value in {"TITER", "YIELD", "PRODUCTIVITY"} for x in modalities) and engineering: contribution.append(_label("DIRECT_ENGINEERING_RECIPE", source, "document", "ENGINEERING_WITH_METRIC", .84))
    if any(x.value in {"MECHANISTIC_EXPERIMENT", "MODEL_DEVELOPMENT"} for x in designs): contribution.append(_label("MECHANISTIC_RULE", source, "document", "MECHANISTIC_SIGNAL", .72))
    if any(x.value == "DATABASE_CONSTRUCTION" for x in designs): contribution.append(_label("DATABASE_RESOURCE", source, "document", "DATABASE_SIGNAL", .85))
    if any(x.value == "SOFTWARE_DEVELOPMENT" for x in designs): contribution.append(_label("SOFTWARE_TOOL", source, "document", "SOFTWARE_SIGNAL", .85))
    strength = "SYNTHESIZED_SECONDARY_EVIDENCE" if review_like else "DIRECT_PRIMARY_EVIDENCE" if wet and engineering and any(x.value in {"TITER", "YIELD", "PRODUCTIVITY"} for x in modalities) else "SUPPORTING_PRIMARY_EVIDENCE" if wet else "MECHANISTIC_EVIDENCE" if designs else "BACKGROUND"
    conflict_fields = []
    metadata_review = candidate.is_review or "review" in (candidate.publication_type or "").casefold()
    explicit_primary = wet and bool(re.search(r"we (?:constructed|engineered|measured)", body or abstract, re.I))
    if metadata_review and explicit_primary: conflict_fields.append("publication_form")
    if form_signals and any(x.value == "ORIGINAL_RESEARCH" for x in form_signals): conflict_fields.append("publication_form")
    axes = lambda labels, fallback, vocab: ClassificationAxis(labels=[x for i,x in enumerate(labels) if x.value in vocab and x.value not in {y.value for y in labels[:i]}] or [_label(fallback, source, "record", "NO_EXPLICIT_SIGNAL", 0)])
    payload = dict(stage=stage, publication_form=axes(form, "UNKNOWN", PUBLICATION_FORMS), research_design=axes(designs, "UNKNOWN", RESEARCH_DESIGNS),
                   engineering_modes=axes(engineering, "NONE_DETECTED", ENGINEERING_MODES), evidence_modalities=axes(modalities, "UNKNOWN", EVIDENCE_MODALITIES),
                   knowledge_contributions=axes(contribution, "UNKNOWN", KNOWLEDGE_CONTRIBUTIONS), evidence_strength=axes([_label(strength, source, "document" if body else "record", "EVIDENCE_DIRECTNESS", .82 if body else .68)], "UNKNOWN", EVIDENCE_STRENGTHS),
                   classification_conflict=bool(conflict_fields), conflict_fields=sorted(set(conflict_fields)), resolution="fulltext explicit evidence retained; conflict exposed" if conflict_fields else None,
                   provenance=[{"stage": stage, "sources": ["title", "abstract", "publication_type_metadata"] + (["fulltext"] if body else [])}],
                   classification_id="cls_"+hashlib.sha256((candidate.candidate_id+stage+text).encode()).hexdigest()[:16])
    result = LiteratureClassification(**payload)
    if previous:
        result.provenance.insert(0, {"stage": "metadata", "classification": previous.model_dump() if isinstance(previous, LiteratureClassification) else previous})
    return result


def classify_batch(candidates, fulltexts=None):
    fulltexts = fulltexts or {}
    results = {}
    for candidate in candidates:
        metadata = classify(candidate)
        results[candidate.candidate_id] = classify(candidate, fulltexts[candidate.candidate_id], metadata) if candidate.candidate_id in fulltexts else metadata
    return results

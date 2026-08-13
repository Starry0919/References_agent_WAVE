"""Conservative biological entity and local coreference resolution."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Mapping

OPERATION_PATTERNS = {
    "deletion": re.compile(r"(?:Δ\s*([A-Za-z][\w-]+)|([A-Za-z][\w-]+)\s+(?:gene\s+)?(?:deletion|knockout|knock-out|disruption)|deletion\s+(?:of\s+)?([A-Za-z][\w-]+))", re.I),
    "overexpression": re.compile(r"(?:overexpress(?:ion|ions|ed|ing)?\s+(?:of\s+)?([A-Za-z][\w-]+)|([A-Za-z][\w-]+)\s+overexpression)", re.I),
    "point_mutation": re.compile(r"\b([A-Za-z][\w-]+)\s+(?:point\s+)?mut(?:ation|ant)|\b([A-Za-z][\w-]+)\s+[A-Z]\d+[A-Z]\b", re.I),
    "promoter_replacement": re.compile(r"(?:promoter\s+replacement\s+(?:of\s+)?|replace(?:d|ment)?\s+(?:the\s+)?promoter\s+(?:of\s+)?)([A-Za-z][\w-]+)", re.I),
    "complementation": re.compile(r"(?:complement(?:ed|ation)?\s+(?:with\s+)?|([A-Za-z][\w-]+)\s+complementation)([A-Za-z][\w-]+)?", re.I),
    "plasmid_introduction": re.compile(r"(?:harboring|carrying|transformed with|plasmid(?:-based)? expression of)\s+(p[A-Za-z0-9_-]+|[A-Za-z][\w-]+)", re.I),
}
STRAIN_PATTERN = re.compile(
    r"\b(?:E\.?\s*coli\s+)?(?:K-?12\s+)?(MG1655|BW25113|BL21(?:\(DE3\))?|BAP1|W3110|Top10|DH5α|DH5a|WT|wild[- ]?type)\b|\b([A-Z][A-Za-z0-9_-]{1,20})\s+strain\b",
    re.I,
)
GENERIC_REFERENCES = {
    "this mutant": "mutant", "the mutant": "mutant", "this strain": "strain",
    "the engineered strain": "engineered", "the recombinant strain": "engineered",
    "the deletion strain": "deletion", "the complemented strain": "complemented",
    "the resultant strain": "engineered",
}
DERIVED_STRAIN_PATTERN = re.compile(r"\b([A-Za-z][\w-]+)\s+(deletion|knockout|knock-out|complemented|complementation)\s+strain\b", re.I)
GENERIC_STRAIN_WORDS = {"engineered", "recombinant", "mutant", "deletion", "knockout", "complemented", "resultant", "control", "parent", "this", "the"}


@dataclass
class BiologicalEntity:
    entity_id: str
    canonical_name: str
    aliases: set[str] = field(default_factory=set)
    kind: str = "strain"
    derived_from: str | None = None
    modifications: list[dict[str, str]] = field(default_factory=list)
    source_units: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {"entity_id": self.entity_id, "canonical_name": self.canonical_name,
                "aliases": sorted(self.aliases), "kind": self.kind,
                "derived_from": self.derived_from, "modifications": self.modifications,
                "source_units": self.source_units}


class BiologicalObjectGraph:
    def __init__(self, document: Mapping[str, Any] | None = None):
        self.entities: dict[str, BiologicalEntity] = {}
        self.unit_entities: dict[str, list[str]] = {}
        self.unit_sections: dict[str, str] = {}
        self.unit_order: list[str] = []
        if document:
            for p in document.get("paragraphs", []):
                self.add_unit(str(p.get("paragraph_id")), str(p.get("text") or ""), str(p.get("section") or ""))

    def add_unit(self, unit_id: str, text: str, section: str = "") -> None:
        explicit = extract_strains(text)
        ids = []
        modifications = extract_interventions(text)
        for name in explicit:
            eid = canonical_entity_id(name)
            entity = self.entities.setdefault(eid, BiologicalEntity(eid, canonical_strain(name), {name.casefold()}))
            entity.aliases.add(name.casefold())
            if unit_id not in entity.source_units: entity.source_units.append(unit_id)
            ids.append(eid)
        for match in DERIVED_STRAIN_PATTERN.finditer(text):
            gene, descriptor = match.groups()
            if gene.casefold() in GENERIC_STRAIN_WORDS: continue
            operation = "complementation" if descriptor.casefold().startswith("complement") else "deletion"
            name = f"{gene} {operation} strain"
            eid = derived_entity_id(gene, operation)
            parent_candidates = [candidate for candidate in ids if candidate != "strain:wt"]
            parent = parent_candidates[0] if len(parent_candidates) == 1 else (ids[0] if len(ids) == 1 else None)
            entity = self.entities.setdefault(eid, BiologicalEntity(eid, name, {name.casefold()}, "engineered_strain", parent))
            modification = {"gene": gene.casefold(), "operation": operation}
            if modification not in entity.modifications: entity.modifications.append(modification)
            if unit_id not in entity.source_units: entity.source_units.append(unit_id)
            ids.append(eid)
        self.unit_entities[unit_id] = ids
        self.unit_sections[unit_id] = section
        self.unit_order.append(unit_id)

    def resolve(self, text: str, unit_id: str | None = None) -> dict[str, Any]:
        explicit = [canonical_entity_id(x) for x in extract_strains(text)]
        explicit.extend(derived_entity_id(m.group(1), "complementation" if m.group(2).casefold().startswith("complement") else "deletion") for m in DERIVED_STRAIN_PATTERN.finditer(text) if m.group(1).casefold() not in GENERIC_STRAIN_WORDS)
        references = [kind for phrase, kind in GENERIC_REFERENCES.items() if phrase in text.casefold()]
        resolved = list(dict.fromkeys(explicit))
        unresolved = []
        for kind in references:
            candidates = self._local_candidates(unit_id, kind)
            if len(candidates) == 1:
                resolved.append(candidates[0])
            else:
                unresolved.append({"reference": kind, "candidate_ids": candidates})
        resolved = list(dict.fromkeys(resolved))
        interventions = extract_interventions(text)
        for entity_id in resolved:
            for modification in self.entities.get(entity_id, BiologicalEntity(entity_id, entity_id)).modifications:
                if modification not in interventions: interventions.append(modification)
        return {"entity_ids": resolved, "references": references,
                "unresolved_references": unresolved, "interventions": interventions}

    def _local_candidates(self, unit_id: str | None, kind: str) -> list[str]:
        if not unit_id or unit_id not in self.unit_order: return []
        index = self.unit_order.index(unit_id)
        units = [unit_id]
        if index > 0 and self.unit_sections.get(self.unit_order[index-1]) == self.unit_sections.get(unit_id):
            units.append(self.unit_order[index-1])
        candidates = list(dict.fromkeys(e for u in units for e in self.unit_entities.get(u, [])))
        if kind == "deletion": candidates = [e for e in candidates if any(m["operation"] == "deletion" for m in self.entities[e].modifications)]
        elif kind == "complemented": candidates = [e for e in candidates if any(m["operation"] == "complementation" for m in self.entities[e].modifications)]
        elif kind in {"mutant", "engineered"}: candidates = [e for e in candidates if self.entities[e].modifications]
        return candidates

    def snapshot(self) -> dict[str, Any]:
        return {"entities": [e.as_dict() for e in self.entities.values()], "unit_entities": self.unit_entities}


def compare_biological_context(claim: Any, evidence: str, graph: BiologicalObjectGraph, unit_id: str | None) -> dict[str, Any]:
    c = graph.resolve(str(claim), None)
    e = graph.resolve(evidence, unit_id)
    statuses, reasons = {}, []
    if c["unresolved_references"] or e["unresolved_references"]:
        statuses["biological_object_match"] = "unresolved"; reasons.append("biological reference has no unique local antecedent")
    elif c["entity_ids"] and e["entity_ids"] and not set(c["entity_ids"]) & set(e["entity_ids"]):
        statuses["biological_object_match"] = "failed"; reasons.append("strain/biological object differs")
    elif c["entity_ids"] and not e["entity_ids"]:
        statuses["biological_object_match"] = "unresolved"; reasons.append("evidence biological object is not explicit")
    else:
        statuses["biological_object_match"] = "passed"
    c_ops, e_ops = {x["operation"] for x in c["interventions"]}, {x["operation"] for x in e["interventions"]}
    c_genes, e_genes = {x["gene"] for x in c["interventions"] if x.get("gene")}, {x["gene"] for x in e["interventions"] if x.get("gene")}
    if c_ops and e_ops and c_ops != e_ops:
        statuses["intervention_match"] = "failed"; reasons.append("genetic intervention operation differs")
    elif c_genes and e_genes and not c_genes & e_genes:
        statuses["intervention_match"] = "failed"; reasons.append("intervention gene differs")
    elif c_ops and not e_ops:
        statuses["intervention_match"] = "unresolved"; reasons.append("evidence intervention is not explicit")
    else:
        statuses["intervention_match"] = "passed"
    c_comparison, e_comparison = comparison_signature(str(claim), graph), comparison_signature(evidence, graph)
    if c_comparison and e_comparison and c_comparison != e_comparison:
        statuses["control_relationship_match"] = "failed"; reasons.append("comparison subject/control relationship differs")
    elif c_comparison and not e_comparison:
        statuses["control_relationship_match"] = "unresolved"; reasons.append("evidence comparison relationship is not explicit")
    else:
        statuses["control_relationship_match"] = "passed"
    status = "failed" if "failed" in statuses.values() else "unresolved" if "unresolved" in statuses.values() else "passed"
    return {"status": status, **statuses, "confidence": "high" if status in {"passed", "failed"} else "low",
            "reasons": reasons, "claim_resolution": c, "evidence_resolution": e,
            "claim_augmented": _augment(str(claim), c), "evidence_augmented": _augment(evidence, e)}


def extract_strains(text: str) -> list[str]:
    values = [next(v for v in m.groups() if v) for m in STRAIN_PATTERN.finditer(text)]
    return [v for v in values if v.casefold() not in GENERIC_STRAIN_WORDS]


def extract_interventions(text: str) -> list[dict[str, str]]:
    out = []
    # Article-bearing forms need precedence: the broad legacy expression may
    # otherwise bind "The" as the gene in "the deletion of X".
    for match in re.finditer(r"\b(?:the\s+)?(?:deletion|knockout|knock-out|disruption)\s+of\s+(?:the\s+)?([A-Za-z][\w-]+)", text, re.I):
        out.append({"gene": match.group(1).casefold(), "operation": "deletion"})
    for operation, pattern in OPERATION_PATTERNS.items():
        for match in pattern.finditer(text):
            gene = next((g for g in match.groups() if g), "")
            if gene.casefold() in GENERIC_STRAIN_WORDS: gene = ""
            if not gene: continue
            item = {"gene": gene.casefold(), "operation": operation}
            if gene.casefold() in {"the", "a", "an"}: continue
            if item not in out: out.append(item)
    return out


def canonical_strain(name: str) -> str:
    value = re.sub(r"\s+", "", name).upper().replace("E.COLI", "")
    return {"BL21(DE3)": "BL21(DE3)", "DH5Α": "DH5α", "DH5A": "DH5α", "WILDTYPE": "WT", "WILD-TYPE": "WT"}.get(value, value)


def canonical_entity_id(name: str) -> str:
    return "strain:" + re.sub(r"[^a-z0-9]+", "_", canonical_strain(name).casefold()).strip("_")


def derived_entity_id(gene: str, operation: str) -> str:
    return "strain:derived:" + re.sub(r"[^a-z0-9]+", "_", gene.casefold()).strip("_") + ":" + operation


def comparison_signature(text: str, graph: BiologicalObjectGraph) -> tuple[tuple[str, ...], str, tuple[str, ...]] | None:
    match = re.search(r"(.{1,80}?)\b(higher|lower|greater|less)\s+than\s+(.{1,80})(?:[.;,]|$)", text, re.I)
    if not match: return None
    left, direction, right = match.groups()
    left_ids = tuple(graph.resolve(left.strip(), None)["entity_ids"])
    right_ids = tuple(graph.resolve(right.strip(), None)["entity_ids"])
    if not left_ids or not right_ids: return None
    return left_ids, direction.casefold(), right_ids


def _augment(text: str, resolution: Mapping[str, Any]) -> str:
    value = text.casefold()
    for phrase in GENERIC_REFERENCES:
        if phrase in value and len(resolution.get("entity_ids", [])) == 1:
            value = value.replace(phrase, resolution["entity_ids"][0])
    for name in extract_strains(text):
        value = re.sub(re.escape(name.casefold()), canonical_entity_id(name), value, flags=re.I)
    synonyms = {
        r"\b(knockout|knock-out|gene disruption)\b": "deletion",
        r"\b(overexpressed|overexpressing|overexpression)\b": "overexpression",
        r"\b(complemented|complementation)\b": "complementation",
    }
    for pattern, replacement in synonyms.items(): value = re.sub(pattern, replacement, value, flags=re.I)
    return value

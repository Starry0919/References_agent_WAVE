from __future__ import annotations

import hashlib

from .models import ScientificLiteratureRequest, SearchQueryRecord


FAMILIES = (
    ("exact_objective", '"Escherichia coli" AND ("K-12" OR MG1655 OR W3110 OR BW25113) AND (tryptophan OR "L-tryptophan") AND (production OR biosynthesis OR titer OR yield OR productivity)', "Exact host, product and production objective"),
    ("metabolic_engineering", '"Escherichia coli" AND (tryptophan OR "L-tryptophan") AND ("metabolic engineering" OR "pathway engineering")', "Direct pathway and metabolic engineering evidence"),
    ("strain_lineage", '("K-12" OR MG1655 OR W3110 OR BW25113) AND (tryptophan OR "L-tryptophan") AND (engineering OR production)', "Keep exact lineage and named derivatives observable"),
    ("pathway_intervention", '"Escherichia coli" AND (tryptophan OR "aromatic amino acid") AND ("feedback resistance" OR precursor OR transporter OR knockout OR overexpression OR promoter OR "flux redistribution")', "Recall pathway interventions that omit metabolic-engineering wording"),
    ("fermentation_bioprocess", '"Escherichia coli" AND (tryptophan OR "L-tryptophan") AND (fermentation OR titer OR yield OR productivity OR bioprocess)', "Production and fermentation evidence"),
    ("recall_expansion", '"Escherichia coli" AND (tryptophan OR chorismate OR shikimate) AND (engineered OR mutant OR strain OR biosynthesis)', "Bounded recall for implicit engineering interventions"),
)

V3_FAMILIES=(
 ("exact_objective","{host} {lineage} {product} production overproduction","Exact product-production objective"),
 ("metabolic_engineering","{product} metabolic pathway engineering {host}","Engineering-specific retrieval"),
 ("strain_lineage","{strains} {product} production","Named lineage derivatives"),
 ("intervention_concepts","{product} promoter attenuator transporter feedback resistance precursor supply","Implicit interventions"),
 ("production_metrics","{product} titer yield productivity fermentation fed-batch","Measured production"),
 ("mechanistic_support","{product} biosynthesis regulation {host} aromatic amino acid pathway trp operon","Mechanistic neighborhood"),
 ("review_synthesis","review {product} metabolic engineering {host}","Secondary synthesis and citation hubs"),
 ("recall_expansion","{product} engineered mutant strain biosynthesis flux {host}","Engineering without standard phrase"),
)

def plan_queries_v3(intent,sources):
 records=[];seen=set();host=intent.species;lineage=intent.lineage or "";product=intent.canonical_product
 strains=" OR ".join(intent.strain_aliases) or lineage
 for family,template,rationale in V3_FAMILIES:
  raw=template.format(host=host,lineage=lineage,product=product,strains=strains).strip()
  for source in sources:
   query=raw if source!="crossref" else raw.replace(" OR "," ")
   key=(source," ".join(query.casefold().split()))
   if key in seen:continue
   seen.add(key);digest=hashlib.sha256((source+family+query).encode()).hexdigest()[:16]
   records.append(SearchQueryRecord(query_id=f"qry_{digest}",query_text=query,query_family=family,rationale=rationale,target_source=source))
   if len(records)>=intent.budgets.max_queries:return records
 return records


def generate_queries(request: ScientificLiteratureRequest, sources: list[str]) -> list[SearchQueryRecord]:
    records: list[SearchQueryRecord] = []
    seen: set[tuple[str, str]] = set()
    for source in sources:
        for family, query, rationale in FAMILIES:
            compiled = compile_for_source(query, source, request)
            key = (source, compiled.casefold())
            if key in seen:
                continue
            seen.add(key)
            digest = hashlib.sha256(f"{source}\0{family}\0{compiled}".encode()).hexdigest()[:16]
            records.append(SearchQueryRecord(query_id=f"qry_{digest}", query_text=compiled, query_family=family, rationale=rationale, target_source=source))
            if len(records) >= request.max_queries:
                return records
    return records


def compile_for_source(query: str, source: str, request: ScientificLiteratureRequest) -> str:
    # The first implementation intentionally uses the common Boolean subset
    # accepted by OpenAlex and Crossref. Source-specific date filters are sent
    # as adapter parameters rather than embedded in query text.
    if source == "crossref":
        return query.replace(" OR ", " ").replace(" AND ", " ").replace("(", "").replace(")", "")
    return query

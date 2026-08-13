from __future__ import annotations
import re
from pydantic import BaseModel, Field

class SearchBudgets(BaseModel):
    max_queries:int=16;max_raw_candidates:int=300;max_dedup_candidates:int=150
    max_citation_expansion:int=30;max_fulltext_acquisition:int=10;max_fulltext_parse:int=10;timeout_budget:int=180
class SearchIntentV3(BaseModel):
    contract_version:str="literature-search-request/3.0";raw_request:str
    species:str;lineage:str|None=None;strain_aliases:list[str]=Field(default_factory=list);excluded_hosts:list[str]=Field(default_factory=list)
    canonical_product:str;product_aliases:list[str]=Field(default_factory=list);related_products:list[str]=Field(default_factory=list);excluded_target_products:list[str]=Field(default_factory=list)
    objective_type:str="production";direction:str="increase";metric_preferences:list[str]=Field(default_factory=list)
    requested_engineering_modes:list[str]=Field(default_factory=list);excluded_engineering_modes:list[str]=Field(default_factory=list)
    preferred_publication_forms:list[str]=Field(default_factory=list);excluded_publication_forms:list[str]=Field(default_factory=list)
    preferred_research_designs:list[str]=Field(default_factory=list);year_from:int|None=None;year_until:int|None=None
    search_mode:str="BALANCED";desired_count:int=20;diversity:bool=True;fulltext_preference:bool=True
    citation_modes:list[str]=Field(default_factory=list);budgets:SearchBudgets=Field(default_factory=SearchBudgets)

def parse_intent(text:str,budgets:SearchBudgets|None=None)->SearchIntentV3:
    low=text.casefold(); species="Escherichia coli" if re.search(r"e\.?\s*coli|escherichia coli",low) else "UNKNOWN"
    lineage="K-12" if re.search(r"k[- ]?12|mg1655|w3110|bw25113",low) else None
    aliases=[x for x in ["MG1655","W3110","BW25113"] if x.casefold() in low] or (["MG1655","W3110","BW25113"] if lineage else [])
    product="L-tryptophan" if re.search(r"l[- ]?tryptophan|tryptophan",low) and not re.search(r"5[- ]?htp|5[- ]hydroxytryptophan",low) else "5-hydroxytryptophan" if re.search(r"5[- ]?htp|5[- ]hydroxytryptophan",low) else "UNKNOWN"
    modes=[]
    for value,pat in [("TRANSPORTER_ENGINEERING",r"transport"),("METABOLIC_ENGINEERING",r"metabolic engineering"),("PROMOTER_ENGINEERING",r"promoter"),("FERMENTATION_OPTIMIZATION",r"fermentation|bioprocess")]:
        if re.search(pat,low):modes.append(value)
    mode="REVIEW_SYNTHESIS" if "review" in low else "RECENT" if re.search(r"recent|latest|newest",low) else "CLASSIC" if re.search(r"classic|foundational|historical",low) else "DIRECT_ENGINEERING" if re.search(r"experimental|engineer|increase|production",low) else "BALANCED"
    preferred=["REVIEW"] if mode=="REVIEW_SYNTHESIS" else ["ORIGINAL_RESEARCH"] if mode=="DIRECT_ENGINEERING" else []
    designs=["WET_LAB_EXPERIMENTAL"] if re.search(r"experimental|wet[- ]lab",low) else []
    return SearchIntentV3(raw_request=text,species=species,lineage=lineage,strain_aliases=aliases,canonical_product=product,
      product_aliases=["tryptophan","Trp"] if product=="L-tryptophan" else ["5-HTP"],related_products=["5-hydroxytryptophan","serotonin","indole","shikimate","aromatic amino acids"],
      excluded_target_products=["5-hydroxytryptophan","serotonin","indole"] if product=="L-tryptophan" else [],metric_preferences=[x for x in ["titer","yield","productivity"] if x in low] or ["titer","yield","productivity"],
      requested_engineering_modes=modes,preferred_publication_forms=preferred,preferred_research_designs=designs,
      year_from=2021 if mode=="RECENT" else None,search_mode=mode,citation_modes=["BACKWARD_CITATION_EXPANSION","FORWARD_CITATION_EXPANSION"],budgets=budgets or SearchBudgets())

DERIVATIVES={"mg1655","w3110","bw25113"}
def lineage_relation(text:str,species_required="Escherichia coli",fulltext=False):
    low=text.casefold();source="fulltext" if fulltext else "metadata"
    hits=[x.upper() for x in DERIVATIVES if x in low]
    if re.search(r"escherichia coli\s+k[- ]?12|e\.?\s*coli\s+k[- ]?12",low):value,score="K12_EXACT",.96
    elif hits:value,score="K12_DERIVATIVE_EXPLICIT",.93
    elif re.search(r"derived from\s+(?:e\.?\s*coli\s*)?k[- ]?12",low):value,score="K12_DERIVATIVE_SUPPORTED",.86
    elif re.search(r"escherichia coli|e\.?\s*coli",low):value,score="ECOLI_UNRESOLVED",.55
    elif re.search(r"bacillus|corynebacterium|saccharomyces|pseudomonas",low):value,score="NON_ECOLI",.93
    else:value,score="ECOLI_UNRESOLVED",.2
    return {"value":value,"confidence":"HIGH" if score>=.85 else "MEDIUM" if score>=.5 else "LOW","score":score,"evidence":hits or (["K-12"] if "K12" in value else []),"source":source,"verified":fulltext}

def product_relation(text:str,target="L-tryptophan",fulltext=False):
    low=text.casefold();source="fulltext" if fulltext else "metadata"
    adjacent=[("5-hydroxytryptophan","DERIVED_PRODUCT"),("5-htp","DERIVED_PRODUCT"),("serotonin","DERIVED_PRODUCT"),("indole","RELATED_PATHWAY_PRODUCT"),("shikimate","UPSTREAM_PRECURSOR"),("aromatic amino acid","RELATED_PATHWAY_PRODUCT")]
    title=low.split("\n",1)[0]
    if any(x in title for x,_ in adjacent) and not re.search(r"(?<!hydroxy)\b(?:l[- ]?)?tryptophan (?:production|overproduction|biosynthesis)",title):
        x,v=next((x,v) for x,v in adjacent if x in title);value,evidence,score=v,x,.94
    elif re.search(r"(?<!hydroxy)(?<!5-)\b(?:l[- ]?)?tryptophan\b",low):value,evidence,score="TARGET_PRODUCT","L-tryptophan",.92
    elif any(x in low for x,_ in adjacent):x,value=next((x,v) for x,v in adjacent if x in low);evidence,score=x,.7
    else:value,evidence,score="UNRESOLVED",None,.2
    return {"value":value,"confidence":"HIGH" if score>=.85 else "MEDIUM" if score>=.5 else "LOW","score":score,"evidence":evidence,"source":source,"verified":fulltext}

def engineering_intelligence(text:str,fulltext=False):
    low=text.casefold();labels=[]
    mapping=[("MODEL_ONLY",r"in silico|model prediction|simulation"),("ENZYME_ONLY_IN_VITRO",r"purified enzyme|enzyme-only|in vitro enzym"),("ALE",r"adaptive laboratory evolution"),("TRANSPORTER_ENGINEERING",r"transporter engineering|efflux pump"),("REGULATORY_ENGINEERING",r"promoter|attenuator|regulatory engineering"),("METABOLIC_ENGINEERING",r"metabolic engineering|pathway engineering|overexpress|knockout|deletion"),("BIOPROCESS_ENGINEERING",r"process optimization|fed[- ]batch"),("FERMENTATION_OPTIMIZATION",r"fermentation optimization"),("MEDIA_OPTIMIZATION",r"media optimization|medium optimization")]
    for v,p in mapping:
        if re.search(p,low):labels.append(v)
    if not labels and re.search(r"regulation|mechanism|pathway",low):labels=["MECHANISTIC_ONLY"]
    return {"labels":labels or ["NO_ENGINEERING"],"source":"fulltext" if fulltext else "metadata","implemented":bool(fulltext and re.search(r"we (?:constructed|deleted|overexpressed|engineered)|was deleted|were engineered",low)),"confidence":"HIGH" if fulltext else "MEDIUM"}

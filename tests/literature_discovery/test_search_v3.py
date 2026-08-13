from pathlib import Path
from harness.literature_discovery.intelligence import *
from harness.literature_discovery.query import plan_queries_v3
from harness.literature_discovery.identity import resolve_identities
from harness.literature_discovery.citations import expand_citations
from harness.literature_discovery.models import PaperCandidate,SearchQueryRecord
from harness.literature_discovery.search_v3 import LiteratureSearchServiceV3

def p(title,doi=None,abstract="",year=2020):return PaperCandidate(candidate_id=doi or title,canonical_title=title,doi=doi,abstract=abstract,year=year)
def test_intent_modes_and_budgets():
 x=parse_intent("Find experimental papers increasing L-tryptophan production in E. coli K-12 with transporter engineering")
 assert x.lineage=="K-12" and x.canonical_product=="L-tryptophan" and x.search_mode=="DIRECT_ENGINEERING" and "TRANSPORTER_ENGINEERING" in x.requested_engineering_modes
 assert parse_intent("recent review papers about tryptophan").search_mode=="REVIEW_SYNTHESIS"
 assert parse_intent("latest tryptophan literature").year_from==2021
def test_query_family_budget_and_dedup():
 x=parse_intent("K12 tryptophan production",SearchBudgets(max_queries=7));q=plan_queries_v3(x,["openalex","crossref"])
 assert len(q)==7 and len({(z.target_source,z.query_text) for z in q})==7 and len({z.query_family for z in q})>=4
def test_lineage_product_engineering_intelligence():
 assert lineage_relation("E. coli K-12")["value"]=="K12_EXACT"
 for s in ("MG1655","W3110","BW25113"):assert lineage_relation(s)["value"]=="K12_DERIVATIVE_EXPLICIT"
 assert lineage_relation("Escherichia coli strain X")["value"]=="ECOLI_UNRESOLVED"
 assert lineage_relation("Corynebacterium glutamicum")["value"]=="NON_ECOLI"
 assert product_relation("L-tryptophan production")["value"]=="TARGET_PRODUCT"
 for s in ("5-HTP production","serotonin production","indole production","shikimate production"):assert product_relation(s)["value"]!="TARGET_PRODUCT"
 assert "MODEL_ONLY" in engineering_intelligence("in silico model prediction")["labels"]
 assert "ENZYME_ONLY_IN_VITRO" in engineering_intelligence("purified enzyme in vitro enzymatic synthesis")["labels"]
def test_identity_resolution_conflicts_and_cross_ids():
 a=p("Same paper",doi="10.1/a",year=2020);b=p("Same paper",doi="10.1/a",year=2020);c=p("Same paper",doi="10.1/b",year=2020)
 merged,conf=resolve_identities([a,b,c]);assert len(merged)==2 and any(x['type']=='IDENTIFIER_CONFLICT' for x in conf)
 a=p("Title long enough for conservative matching",year=2020);a.pmid="1";b=p("Different title",year=2020);b.pmid="1";assert len(resolve_identities([a,b])[0])==1
def test_citation_expansion_is_bounded_and_provenanced():
 seed=p("Review",doi="10.1/r");seed.route={"value":"REVIEW_SYNTHESIS_ROUTE"}
 def provider(seed,mode,limit):return [p(f"Cited {i}",doi=f"10.1/{i}") for i in range(20)]
 out=expand_citations([seed],provider,max_backward=3,max_forward=3,max_total=4);assert len(out)==3 and all(x.source_records for x in out) # cross-mode duplicates are removed
def test_end_to_end_cache_ranking_negative_suppression_and_contract(tmp_path):
 direct=p("Engineering L-tryptophan production in Escherichia coli K-12 MG1655",abstract="We engineered metabolic pathway and measured titer 20 g/L in fermentation.",doi="10.1/direct",year=1985)
 review=p("Review of L-tryptophan metabolic engineering in E. coli",abstract="This review summarizes pathway engineering.",doi="10.1/review")
 wrong=p("5-HTP production in E. coli",abstract="Metabolic engineering produced serotonin precursor at 20 g/L",doi="10.1/wrong")
 class A:
  name="mock"
  def search(self,*args,**kwargs):return [direct.model_copy(deep=True),review.model_copy(deep=True),wrong.model_copy(deep=True)]
 service=LiteratureSearchServiceV3([A()],tmp_path,fulltext_provider=lambda c:{"text":c.canonical_title+'\n'+(c.abstract or '')+" We engineered the strain.","parser":{"name":"test"}})
 r=service.search_literature("Find experimental papers increasing L-tryptophan production in E. coli K-12")
 assert r.results[0].identity['doi']=="10.1/direct" and r.results[0].ranking['final_score']>r.results[-1].ranking['final_score']
 assert r.results[0].verification_level=="FULLTEXT_VERIFIED" and r.results[0].explanation['reason_codes'] and r.results[0].provenance==[]
 assert service.search_literature("Find experimental papers increasing L-tryptophan production in E. coli K-12").cache_hit
 assert r.readiness['formal_quality_validation']=="NOT_FORMALLY_CALIBRATED" and not r.readiness['ddr_writes_enabled']
def test_production_api_is_mounted():
 from harness.server import app
 assert '/api/literature-search' in app.openapi()['paths']
 assert '/api/literature-search/readiness' in app.openapi()['paths']

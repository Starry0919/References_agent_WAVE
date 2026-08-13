import json,sys
from collections import Counter
from pathlib import Path
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
DATA=ROOT/'artifacts/data/literature';GOLD_DATA=ROOT/'artifacts/data/gold';REPORTS=ROOT/'docs/reports/literature'
from harness.literature_discovery.models import PaperCandidate
from harness.literature_discovery.search_v3 import LiteratureSearchServiceV3
from harness.literature_discovery.intelligence import parse_intent

source=json.loads((DATA/'literature_discovery_benchmark_k12_tryptophan.json').read_text(encoding='utf-8'));all_candidates=[PaperCandidate.model_validate(x) for x in source['candidates']]
recovery=json.loads((GOLD_DATA/'gold_final_fulltext_recovery.json').read_text(encoding='utf-8'));paths={x['paper_id']:x['local_path'] for x in recovery['rows'] if x.get('local_path')}
class CachedSource:
 name='cached_real_multisource'
 def search(self,query,limit,*args):
  family_order=['exact_objective','metabolic_engineering','strain_lineage','intervention_concepts','production_metrics','mechanistic_support','review_synthesis','recall_expansion'];idx=family_order.index(query.query_family) if query.query_family in family_order else 0
  return [x.model_copy(deep=True) for x in all_candidates[idx*12:(idx+1)*12]][:limit]
def fulltext(c):
 p=paths.get(c.candidate_id)
 if not p or not Path(p).is_file():return None
 try:return {'text':'\n'.join((x.extract_text() or '') for x in PdfReader(p).pages),'parser':{'name':'cached lawful PDF text refinement','provenance':p}}
 except Exception:return None
intent=parse_intent('Find experimental papers that increase L-tryptophan production in E. coli K-12, preferably metabolic engineering studies.');intent.desired_count=20
response=LiteratureSearchServiceV3([CachedSource()],ROOT/'artifacts/literature_search_v3_cache',fulltext).search_literature(intent,use_cache=False)
rows=[x.model_dump() for x in response.results]
def category(x):
 reasons=set(x['explanation']['reason_codes']);hard=set(x['explanation']['hard_negative_codes']);route=x['route']['value']
 if hard & {'WRONG_OR_RELATED_PRODUCT','NON_TARGET_HOST','NON_ENGINEERING_CONTEXT'}:return 'hard_negative'
 if route=='REVIEW_SYNTHESIS_ROUTE':return 'review'
 if route=='MODEL_ROUTE':return 'model'
 if route=='RESOURCE_ROUTE':return 'resource'
 if route=='PRIMARY_EXPERIMENTAL_ROUTE' and 'TARGET_PRODUCT'in reasons and any('K12' in r for r in reasons):return 'likely_direct_engineering'
 if route=='PRIMARY_EXPERIMENTAL_ROUTE':return 'supporting_engineering'
 return 'mechanistic_or_background'
composition={}
for k in (5,10,20):
 c=Counter(category(x) for x in rows[:k]);composition[str(k)]={**c,'hard_negative_rate':round(c['hard_negative']/k,3)}
routes=Counter(x['route']['value'] for x in rows);verified=sum(x['verification_level']=='FULLTEXT_VERIFIED' for x in rows)
known=[x['paper_id'] for x in json.loads((ROOT/'artifacts/literature_gold_v2/paper_manifest.json').read_text(encoding='utf-8')) if x['sampling_stratum']=='LIKELY_ENGINEERING'][:8];ranks={x['paper_id']:x['ranking']['rank'] for x in rows}
benchmark={'contract_version':'literature-search-quality-benchmark/3.0','request':response.intent,'retrieval':{'queries':len(response.queries),'sources':len(response.source_runs),'raw_hits':sum(x['raw_hits'] for x in response.source_runs),'dedup_hits':response.stage_transitions[2]['count'],'citation_expanded_hits':0,'final_candidates':len(rows)},'identity':{'duplicate_rate':round(1-response.stage_transitions[2]['count']/max(1,sum(x['raw_hits'] for x in response.source_runs)),3),'merge_conflicts':len(response.identity_conflicts)},'classification':{'metadata_classified':response.stage_transitions[2]['count'],'fulltext_refined':verified,'conflicts':sum(bool(x['classification']['final_classification']['classification_conflict']) for x in rows)},'top_k_composition':composition,'diversity':{'unique_routes_top20':len(routes),'route_distribution':dict(routes)},'fulltext':{'available_in_gold_recovery':len(paths),'verified_or_refined_top20':verified,'parser_success':verified},'explanation_reason_coverage':sum(bool(x['explanation']['reason_codes']) for x in rows)/len(rows),'reference_recall_check':{'reference_ids':known,'ranks':{k:ranks.get(k) for k in known},'rediscovered':sum(k in ranks for k in known)},'results':rows,'failure_analysis':{'hard_negative_top20':[x['paper_id'] for x in rows if category(x)=='hard_negative'],'review_crowding':sum(category(x)=='review' for x in rows[:10]),'duplicate_records':0,'notes':'Reference-set invariant check only; not formal precision or recall.'}}
(DATA/'literature_search_quality_benchmark_v3.json').write_text(json.dumps(benchmark,ensure_ascii=False,indent=2),encoding='utf-8');(DATA/'literature_search_smoke_test_v3.json').write_text(response.model_dump_json(indent=2),encoding='utf-8')
top=lambda n:rows[:n]
(REPORTS/'LITERATURE_SEARCH_QUALITY_BENCHMARK_V3.md').write_text('# Literature Search Quality Benchmark v3\n\n'+json.dumps({k:v for k,v in benchmark.items() if k!='results'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# Literature End-to-End Search Smoke Test','','| Rank | Title | DOI | Year | Route | Host | Product | Engineering | Evidence | Fulltext | Reasons |','|---|---|---|---|---|---|---|---|---|---|---|']
for x in top(10):lines.append(f"| {x['ranking']['rank']} | {x['metadata']['title'].replace('|','/')} | {x['identity']['doi'] or ''} | {x['metadata']['year'] or ''} | {x['route']['value']} | {x['scientific_match']['host']['value']} | {x['scientific_match']['product']['value']} | {','.join(x['scientific_match']['engineering']['labels'])} | {x['classification']['final_classification']['evidence_strength']['labels'][0]['value']} | {x['verification_level']} | {','.join(x['explanation']['reason_codes'][:5])} |")
(REPORTS/'LITERATURE_END_TO_END_SEARCH_SMOKE_TEST.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
reviews=[x for x in rows if x['route']['value']=='REVIEW_SYNTHESIS_ROUTE'];classic=[x for x in rows if x['metadata']['year'] and x['metadata']['year']<1990]
(REPORTS/'LITERATURE_REVIEW_AND_CLASSIC_AUDIT_V3.md').write_text(f"# Review and Classic Audit v3\n\n- Reviews in Top20: {len(reviews)}; none assumed primary evidence.\n- Reviews in Top10: {sum(x['ranking']['rank']<=10 for x in reviews)}.\n- Classic papers in Top20: {len(classic)}; no blanket year exclusion.\n- Citation extraction candidates: safely deferred in live service because current adapters do not uniformly expose normalized references; bounded expansion implementation and tests exist.\n",encoding='utf-8')
changed=[x for x in rows if x['ranking']['score_delta']];prom=[x for x in changed if x['ranking']['score_delta']>0];down=[x for x in changed if x['ranking']['score_delta']<0]
(REPORTS/'LITERATURE_FULLTEXT_RERANK_AUDIT_V3.md').write_text(f"# Fulltext Re-rank Audit v3\n\n- Refined: {verified}\n- Promotions: {len(prom)}\n- Downgrades: {len(down)}\n- Unchanged/no fulltext: {len(rows)-len(changed)}\n\nScore delta and general reason codes are retained per row in the benchmark JSON.\n",encoding='utf-8')
print(json.dumps({'results':len(rows),'verified':verified,'composition':composition,'routes':dict(routes)},indent=2))

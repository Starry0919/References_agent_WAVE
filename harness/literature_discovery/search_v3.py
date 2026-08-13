from __future__ import annotations
import hashlib,json,time
from pathlib import Path
from pydantic import BaseModel,Field
from .classification import classify
from .identity import resolve_identities
from .intelligence import SearchIntentV3,engineering_intelligence,lineage_relation,parse_intent,product_relation
from .models import PaperCandidate,SourceRun
from .query import plan_queries_v3
from .routing import route

class SearchResultV3(BaseModel):
 search_result_version:str="literature-search-result/3.0";request_id:str;paper_id:str;identity:dict;metadata:dict;scientific_match:dict;classification:dict;ranking:dict;route:dict;verification_level:str;acquisition:dict;parser:dict|None=None;explanation:dict;provenance:list[dict]=Field(default_factory=list)
class SearchResponseV3(BaseModel):
 contract_version:str="literature-search-response/3.0";request_id:str;intent:dict;queries:list[dict];source_runs:list[dict];stage_transitions:list[dict];identity_conflicts:list[dict];results:list[SearchResultV3];cache_hit:bool=False;readiness:dict

def _score(candidate,intent,fulltext=False):
 text="\n".join([candidate.canonical_title,candidate.abstract or ""]);lin=lineage_relation(text,intent.species,fulltext);prod=product_relation(text,intent.canonical_product,fulltext);eng=engineering_intelligence(text,fulltext)
 rel=candidate.relevance.score if candidate.relevance else .0; cls=candidate.final_classification or candidate.metadata_classification or {};form={x['value'] for x in cls.get('publication_form',{}).get('labels',[])};design={x['value'] for x in cls.get('research_design',{}).get('labels',[])};strength={x['value'] for x in cls.get('evidence_strength',{}).get('labels',[])}
 direct=.18*(lin['value'] in {'K12_EXACT','K12_DERIVATIVE_EXPLICIT','K12_DERIVATIVE_SUPPORTED'})+.20*(prod['value']=='TARGET_PRODUCT')+.15*bool(set(eng['labels'])&{'METABOLIC_ENGINEERING','TRANSPORTER_ENGINEERING','REGULATORY_ENGINEERING','BIOPROCESS_ENGINEERING','FERMENTATION_OPTIMIZATION'})+.10*('WET_LAB_EXPERIMENTAL'in design)+.08*('DIRECT_PRIMARY_EVIDENCE'in strength)
 objective=.07*bool(set(intent.metric_preferences)&{'titer','yield','productivity'} and any(x in text.casefold() for x in ('titer','yield','productivity','g/l')))
 confidence=.04*max([x.get('score',0) for a in cls.values() if isinstance(a,dict) for x in a.get('labels',[])] or [0]);availability=.025*bool(candidate.acquisition.local_path or candidate.oa_urls)
 recent=.015*max(0,min(1,((candidate.year or 1990)-2000)/26));classic=.03*(bool(candidate.year and candidate.year<1990) and rel>.25)
 negative=0;neg=[]
 if prod['value']!='TARGET_PRODUCT':negative+=.50;neg.append('WRONG_OR_RELATED_PRODUCT')
 if lin['value'] in {'NON_ECOLI','ECOLI_NON_K12'}:negative+=.25;neg.append('NON_TARGET_HOST')
 if intent.lineage and lin['value']=='ECOLI_UNRESOLVED':negative+=.07;neg.append('STRAIN_UNRESOLVED')
 if any(x in text.casefold() for x in ('clinical','infection','patient','biofilm','assay for detection')):negative+=.22;neg.append('NON_ENGINEERING_CONTEXT')
 if intent.search_mode=='DIRECT_ENGINEERING' and ('REVIEW'in ' '.join(form) or 'MODEL_ONLY'in eng['labels'] or 'ENZYME_ONLY_IN_VITRO'in eng['labels']):negative+=.28;neg.append('REQUEST_MODE_MISMATCH')
 if intent.search_mode=='DIRECT_ENGINEERING' and not any(x in text.casefold() for x in ('production','overproduction','titer','yield','productivity','fermentation')):negative+=.18;neg.append('OBJECTIVE_NOT_EVIDENCED')
 if intent.search_mode=='DIRECT_ENGINEERING' and not set(eng['labels'])&{'METABOLIC_ENGINEERING','TRANSPORTER_ENGINEERING','REGULATORY_ENGINEERING','BIOPROCESS_ENGINEERING','FERMENTATION_OPTIMIZATION','ALE'}:negative+=.14;neg.append('ENGINEERING_NOT_EVIDENCED')
 metadata=max(0,min(1,.42*rel+direct+objective+confidence+recent+classic-negative));verified_bonus=.10 if fulltext and eng['implemented'] else 0;final=max(0,min(1,metadata+verified_bonus))
 return final,{"scientific_relevance":round(.42*rel+direct+objective,4),"confidence":round(confidence,4),"availability":round(availability,4),"classic_importance":round(classic,4),"recent_relevance":round(recent,4),"hard_negative_penalty":round(negative,4),"fulltext_verified_bonus":verified_bonus},lin,prod,eng,neg

def _diverse(items,mode,count):
 if mode!='BALANCED':return items[:count]
 quotas={'PRIMARY_EXPERIMENTAL_ROUTE':max(1,int(count*.65)),'REVIEW_SYNTHESIS_ROUTE':2,'MODEL_ROUTE':1,'METHOD_ROUTE':1,'BACKGROUND_ROUTE':1};out=[];used=set()
 for r,q in quotas.items():
  for x in [z for z in items if z['candidate'].route['value']==r][:q]:out.append(x);used.add(x['candidate'].candidate_id)
 out+= [x for x in items if x['candidate'].candidate_id not in used]
 return out[:count]

class LiteratureSearchServiceV3:
 def __init__(self,adapters=None,cache_dir=None,fulltext_provider=None,citation_provider=None):
  from .adapters import OpenAlexAdapter,CrossrefAdapter
  self.adapters=adapters or [OpenAlexAdapter(),CrossrefAdapter()];self.cache_dir=Path(cache_dir) if cache_dir else None;self.fulltext_provider=fulltext_provider;self.citation_provider=citation_provider
 def search_literature(self,request,use_cache=True):
  intent=request if isinstance(request,SearchIntentV3) else parse_intent(request);rid='lsr_'+hashlib.sha256(intent.model_dump_json().encode()).hexdigest()[:16];cache=self.cache_dir/f'{rid}.json' if self.cache_dir else None
  if use_cache and cache and cache.is_file():r=SearchResponseV3.model_validate_json(cache.read_text(encoding='utf-8'));r.cache_hit=True;return r
  start=time.monotonic();queries=plan_queries_v3(intent,[a.name for a in self.adapters]);runs={a.name:SourceRun(source=a.name) for a in self.adapters};raw=[];am={a.name:a for a in self.adapters};stages=[{'stage':'QUERY_GENERATED','count':len(queries)}]
  for q in queries:
   if time.monotonic()-start>intent.budgets.timeout_budget:break
   runs[q.target_source].query_count+=1
   try:found=am[q.target_source].search(q,min(25,intent.budgets.max_raw_candidates-len(raw)),intent.year_from,intent.year_until);raw+=found;runs[q.target_source].raw_hits+=len(found)
   except Exception as e:runs[q.target_source].errors.append(f'{type(e).__name__}: {e}')
   if len(raw)>=intent.budgets.max_raw_candidates:break
  stages.append({'stage':'METADATA_RETRIEVED','count':len(raw)});canonical,conflicts=resolve_identities(raw);canonical=canonical[:intent.budgets.max_dedup_candidates];stages.append({'stage':'IDENTITY_RESOLVED','count':len(canonical)})
  from .relevance import assess
  from .models import ScientificLiteratureRequest,OrganismSpec,ProductSpec
  oldreq=ScientificLiteratureRequest(organism=OrganismSpec(species=intent.species,lineage=intent.lineage,strain_aliases=intent.strain_aliases),target_product=ProductSpec(canonical_name=intent.canonical_product,aliases=intent.product_aliases),objective=f'{intent.direction} {intent.objective_type}')
  scored=[]
  for c in canonical:
   c.relevance=assess(c,oldreq);mc=classify(c);c.metadata_classification=mc.model_dump();c.final_classification=mc.model_dump();c.route=route(mc);score,parts,lin,prod,eng,neg=_score(c,intent);scored.append({'candidate':c,'metadata_score':score,'final_score':score,'parts':parts,'lineage':lin,'product':prod,'engineering':eng,'negative':neg,'verification':'METADATA_CLASSIFIED','delta':0})
  scored.sort(key=lambda x:x['metadata_score'],reverse=True);stages.append({'stage':'METADATA_CLASSIFIED_RANKED','count':len(scored)})
  if self.fulltext_provider:
   for x in scored[:intent.budgets.max_fulltext_parse]:
    doc=self.fulltext_provider(x['candidate'])
    if not doc:continue
    c=x['candidate'];fc=classify(c,doc.get('text',''),c.metadata_classification);c.fulltext_classification=fc.model_dump();c.final_classification=fc.model_dump();c.route=route(fc);score,parts,lin,prod,eng,neg=_score(c,intent,True);x.update(final_score=score,parts=parts,lineage=lin,product=prod,engineering=eng,negative=neg,verification='FULLTEXT_VERIFIED',delta=round(score-x['metadata_score'],4),parser=doc.get('parser'))
   scored.sort(key=lambda x:x['final_score'],reverse=True);stages.append({'stage':'FULLTEXT_REFINED_RERANKED','count':sum(x['verification']=='FULLTEXT_VERIFIED' for x in scored)})
  final=_diverse(scored,intent.search_mode,intent.desired_count);results=[]
  for rank,x in enumerate(final,1):
   c=x['candidate'];reasons=[x['lineage']['value'],x['product']['value'],*x['engineering']['labels'],c.route['value']];results.append(SearchResultV3(request_id=rid,paper_id=c.candidate_id,identity={'doi':c.doi,'pmid':c.pmid,'pmcid':c.pmcid,'openalex_id':c.openalex_id},metadata={'title':c.canonical_title,'authors':c.authors,'year':c.year,'venue':c.venue},scientific_match={'host':x['lineage'],'product':x['product'],'objective':intent.objective_type,'engineering':x['engineering']},classification={'metadata_classification':c.metadata_classification,'fulltext_classification':c.fulltext_classification,'final_classification':c.final_classification},ranking={'metadata_score':x['metadata_score'],'fulltext_score':x['final_score'] if x['verification']=='FULLTEXT_VERIFIED' else None,'final_score':x['final_score'],'score_delta':x['delta'],'rank':rank,'score_breakdown':x['parts']},route=c.route,verification_level=x['verification'],acquisition=c.acquisition.model_dump(),parser=x.get('parser'),explanation={'reason_codes':reasons,'hard_negative_codes':x['negative'],'confidence':c.route['confidence']},provenance=[s.model_dump() for s in c.source_records]))
  from .readiness import literature_readiness
  readiness=literature_readiness(False)|{'literature_search':'PRODUCTION_READY','retrieval':'PRODUCTION_READY','routing':'PRODUCTION_READY_WITH_CONFIDENCE','fulltext_refinement':'PRODUCTION_READY_WITH_PROVENANCE','formal_quality_validation':'NOT_FORMALLY_CALIBRATED'}
  response=SearchResponseV3(request_id=rid,intent=intent.model_dump(),queries=[q.model_dump() for q in queries],source_runs=[x.model_dump() for x in runs.values()],stage_transitions=stages,identity_conflicts=conflicts,results=results,readiness=readiness)
  if cache:cache.parent.mkdir(parents=True,exist_ok=True);cache.write_text(response.model_dump_json(indent=2),encoding='utf-8')
  return response

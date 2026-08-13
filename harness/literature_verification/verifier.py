from __future__ import annotations
import hashlib,re
from typing import Any
from .canonical import from_markdown

def _spans(text,patterns,kind,sections):
 out=[]
 for p in patterns:
  for m in re.finditer(p,text,re.I):
   start=max(0,m.start()-100);end=min(len(text),m.end()+180);sec=next((s for s in sections if s['char_start']<=m.start()<=s['char_end']),None)
   # Context is clipped to its source section so a References/Future marker
   # in the neighboring section cannot contaminate an implemented claim.
   if sec:start=max(start,sec['char_start']);end=min(end,sec['char_end'])
   q=text[start:end].replace('\n',' ');out.append({'kind':kind,'match':m.group(0),'start':start,'end':end,'quote':q,'section_id':(sec or {}).get('section_id'),'normalized_section':(sec or {}).get('normalized_type','other'),'anchor':f"{(sec or {}).get('section_id','unknown')}:{hashlib.sha256(' '.join(q.split()).casefold().encode()).hexdigest()[:12]}"})
 return out[:30]
def verify_document(candidate:dict[str,Any],document:Any,document_sha256:str|None=None)->dict:
 if isinstance(document,dict):canonical=document;text=canonical.get('text','')
 else:text=document;sha=document_sha256 or hashlib.sha256(text.encode()).hexdigest();canonical=from_markdown(candidate.get('candidate_id','unknown'),text,sha,'legacy_text_adapter','1.1').model_dump()
 sections=canonical.get('sections',[]);low=text.casefold();title=(candidate.get('canonical_title') or '').casefold()
 review=bool(re.search(r'\b(this|the present) review\b|\breview article\b',low[:12000]) or 'review' in title)
 host=_spans(text,[r'Escherichia coli\s+K[-‐‑]?12',r'\b(?:MG1655|W3110|BW25113)\b',r'Escherichia coli'],'host',sections)
 if any(re.search(r'K[-‐‑]?12',x['match'],re.I) for x in host):relation='K12_EXACT'
 elif any(x['match'].upper() in {'MG1655','W3110','BW25113'} for x in host):relation='K12_DERIVATIVE_EXPLICIT'
 elif host:relation='ECOLI_UNRESOLVED'
 else:relation='NON_ECOLI'
 adjacent=_spans(text,[r'5[- ]hydroxytryptophan',r'serotonin',r'indole production',r'shikimate production'],'adjacent_product',sections)
 target=_spans(text,[r'(?<!hydroxy)(?<!hydroxy-)\bL?-?tryptophan\s+(?:production|biosynthesis|overproduction)'],'target',sections)
 for x in target:x['product_role']='TARGET_PRODUCT' if not adjacent else 'RELATED_PRODUCT'
 ints=_spans(text,[r'\b(?:knockout|delet(?:e|ed|ion)|overexpress(?:ed|ion)?|promoter replacement|promoter swapping|attenuator inactivation|feedback[- ]resistant|transport(?:er)? engineering|adaptive laboratory evolution)\b'],'intervention',sections)
 for x in ints:
  sec=x['normalized_section'];x['implementation_status']='CITED_OTHER_WORK' if sec=='references' else 'PLANNED' if re.search(r'future|could|may|proposed|suggest|potential',x['quote'],re.I) else 'IMPLEMENTED' if sec in {'methods','results','abstract'} else 'DISCUSSED' if sec in {'introduction','discussion','conclusion'} else 'UNKNOWN';x['action']=x['match'];x['target_gene_or_pathway']=None;x['confidence']=.9 if x['implementation_status']=='IMPLEMENTED' else .5
 implemented=[x for x in ints if x['implementation_status']=='IMPLEMENTED']
 metrics=_spans(text,[r'\b\d+(?:\.\d+)?\s*(?:g/L|mg/L|mmol/L|mmol|mol/mol)\b',r'\b(?:titer|yield|productivity)\b.{0,80}\b\d+(?:\.\d+)?'],'validation',sections)
 for x in metrics:
  sec=x['normalized_section'];x['measured_vs_cited']='cited' if sec in {'references','introduction'} else 'measured' if sec in {'methods','results','abstract'} else 'unknown';m=re.search(r'(\d+(?:\.\d+)?)\s*([A-Za-z/]+)',x['match']);x.update({'metric_type':'titer' if 'g/' in x['match'].lower() else 'reported_metric','value':float(m.group(1)) if m else None,'unit':m.group(2) if m else None,'comparator':None,'condition':None,'cultivation_mode':'fed-batch' if 'fed-batch' in x['quote'].lower() else None,'confidence':.9 if x['measured_vs_cited']=='measured' else .4})
 measured=[x for x in metrics if x['measured_vs_cited']=='measured'];model=bool(re.search(r'\b(in silico|model prediction|computational model)\b',low)) and not measured;enzyme=bool(re.search(r'enzymatic synthesis|purified enzyme|in vitro',low)) and not re.search(r'fermentation|engineered strain',low)
 pub='REVIEW' if review else 'MODEL_ONLY' if model else 'ENZYME_ONLY' if enzyme else 'PRIMARY_EXPERIMENTAL' if implemented and measured else 'OTHER'
 if review:decision,reason='NOT_ELIGIBLE','review_article'
 elif adjacent and not target:decision,reason='NOT_ELIGIBLE','wrong_target_product'
 elif relation in {'K12_EXACT','K12_DERIVATIVE_EXPLICIT'} and target and implemented and measured and not model and not enzyme:decision,reason='DIRECT_ENGINEERING_EVIDENCE','all section-aware hard gates evidenced'
 elif relation!='NON_ECOLI' and target and implemented:decision,reason='SUPPORTING_ENGINEERING_EVIDENCE','host or measured gate incomplete'
 elif target or ints:decision,reason='MECHANISTIC_SUPPORT','partial mechanistic evidence'
 elif not text.strip():decision,reason='DATA_REQUIRED','no full text'
 else:decision,reason='BACKGROUND','no implemented target engineering evidence'
 return {'contract_version':'literature-evidence-verification/1.1','candidate_id':candidate.get('candidate_id'),'metadata_assessment':candidate.get('relevance'),'document_sha256':document_sha256 or canonical.get('source_pdf_sha256'),'canonical_document_id':canonical.get('document_id'),'publication_type':{'classification':pub,'is_review':review},'host':{'relation':relation,'evidence':host},'target_product':{'canonical':'L-tryptophan','role':'TARGET_PRODUCT' if target and not adjacent else 'RELATED_PRODUCT' if adjacent else 'UNKNOWN','evidence':target,'adjacent_product_evidence':adjacent},'interventions':{'implemented':implemented,'all_mentions':ints},'experimental_validation':{'evidence':measured,'all_mentions':metrics,'model_only':model,'enzyme_only':enzyme},'judge':{'decision':decision,'reason':reason,'evidence_span_count':len(host)+len(target)+len(implemented)+len(measured)},'verifier_version':'1.1'}

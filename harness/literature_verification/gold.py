from __future__ import annotations
import math
from collections import Counter

FIELDS=['identity_correct','publication_type','host_relation','product_role','implemented_engineering','measured_production','final_eligibility']
def _kappa(a,b):
 n=len(a)
 if not n:return None
 po=sum(x==y for x,y in zip(a,b))/n;ca=Counter(a);cb=Counter(b);pe=sum(ca[k]/n*cb[k]/n for k in set(ca)|set(cb))
 return None if pe==1 else (po-pe)/(1-pe)
def agreement(papers):
 out={}
 for f in FIELDS:
  pairs=[(p['annotator_A'].get(f),p['annotator_B'].get(f)) for p in papers if isinstance(p.get('annotator_A'),dict) and isinstance(p.get('annotator_B'),dict) and p['annotator_A'].get(f) not in (None,'') and p['annotator_B'].get(f) not in (None,'')]
  out[f]={'n':len(pairs),'missing':len(papers)-len(pairs),'raw_agreement':sum(a==b for a,b in pairs)/len(pairs) if pairs else None,'cohen_kappa':_kappa([a for a,_ in pairs],[b for _,b in pairs]),'disagreements':sum(a!=b for a,b in pairs)}
 return out
def adjudication_queue(papers):
 return [{'paper_id':p['paper_id'],'annotator_A':p.get('annotator_A'),'annotator_B':p.get('annotator_B'),'reasons':['missing_or_disagreement']} for p in papers if not isinstance(p.get('annotator_A'),dict) or not isinstance(p.get('annotator_B'),dict) or any(p['annotator_A'].get(f)!=p['annotator_B'].get(f) or p['annotator_A'].get(f) in (None,'') for f in FIELDS)]
def evaluate(rows,scores=None):
 usable=[r for r in rows if (r.get('gold') or {}).get('eligibility_label') is not None and r.get('prediction') is not None];tp=tn=fp=fn=0
 for r in usable:
  g=bool(r['gold']['eligibility_label']);p=bool(r['prediction']);tp+=g and p;tn+=(not g and not p);fp+=(not g and p);fn+=g and not p
 div=lambda a,b:a/b if b else 0;res={'status':'GOLD_PENDING_HUMAN_ANNOTATION' if not usable else 'EVALUATED','labeled':len(usable),'confusion_matrix':{'tp':tp,'tn':tn,'fp':fp,'fn':fn},'precision':div(tp,tp+fp),'recall':div(tp,tp+fn),'f1':div(2*tp,2*tp+fp+fn),'specificity':div(tn,tn+fp)}
 if scores and usable:
  ranked=sorted(usable,key=lambda r:scores.get(r['paper_id'],0),reverse=True);positives=sum(bool(r['gold']['eligibility_label']) for r in ranked)
  for k in (5,10,20):res[f'precision@{k}']=div(sum(bool(r['gold']['eligibility_label']) for r in ranked[:k]),min(k,len(ranked)))
  for k in (20,50):res[f'recall@{k}']=div(sum(bool(r['gold']['eligibility_label']) for r in ranked[:k]),positives)
  for k in (10,20):
   dcg=sum(bool(r['gold']['eligibility_label'])/math.log2(i+2) for i,r in enumerate(ranked[:k]));ideal=sum(1/math.log2(i+2) for i in range(min(k,positives)));res[f'ndcg@{k}']=div(dcg,ideal)
 return res

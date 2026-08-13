import csv,json,shutil
from pathlib import Path
project=Path(__file__).resolve().parents[1];data=project/'artifacts/data/literature';reports=project/'docs/reports/literature'
root=project/'artifacts/literature_gold_v2';root.mkdir(parents=True,exist_ok=True)
d=json.loads((data/'literature_discovery_benchmark_k12_tryptophan.json').read_text(encoding='utf-8'));acq=json.loads((data/'resilient_acquisition_benchmark_k12_tryptophan.json').read_text(encoding='utf-8'));am={x['candidate_id']:x for x in acq['rows']};picked=[]
strata=[('LIKELY_ENGINEERING',lambda x:(x.get('relevance')or{}).get('decision')=='tier_2_supporting_engineering',18),('MECHANISM_BOUNDARY',lambda x:(x.get('relevance')or{}).get('decision')=='tier_3_mechanistic',14),('WRONG_PRODUCT_OR_NON_TARGET',lambda x:'OTHER_PRODUCT_TARGET' in (x.get('relevance')or{}).get('reason_codes',[]) or 'NON_TARGET_HOST' in (x.get('relevance')or{}).get('reason_codes',[]),10),('REVIEW_OR_NON_ENGINEERING',lambda x:(x.get('is_review') or 'NON_ENGINEERING' in (x.get('relevance')or{}).get('reason_codes',[])),8),('BACKGROUND_EXCLUDE',lambda x:(x.get('relevance')or{}).get('decision') in {'background','exclude'},10)]
seen=set()
for name,fn,n in strata:
 for x in [z for z in d['candidates'] if fn(z)]:
  if x['candidate_id'] in seen:continue
  seen.add(x['candidate_id']);picked.append((x,name));
  if sum(s==name for _,s in picked)>=n:break
manifest=[];hidden=[]
for x,s in picked:
 a=am.get(x['candidate_id'],{});manifest.append({'paper_id':x['candidate_id'],'doi':x.get('doi'),'title':x['canonical_title'],'sampling_stratum':s,'metadata_tier':(x.get('relevance')or{}).get('decision'),'fulltext_path':a.get('local_path'),'fulltext_status':a.get('state','not_recovered'),'identity_status':(a.get('identity_verification')or{}).get('status')});hidden.append({'paper_id':x['candidate_id'],'reason_codes':(x.get('relevance')or{}).get('reason_codes'),'machine_score':(x.get('relevance')or{}).get('score'),'machine_host':(x.get('relevance')or{}).get('host_relation')})
fields=['paper_id','doi','title','sampling_stratum','identity_correct','identity_confidence','publication_type','host_relation','product_role','implemented_engineering','intervention_class','measured_production','metric_type','metric_value','metric_unit','final_eligibility','annotation_confidence','evidence_page_section','notes']
for role in ('A','B'):
 with open(root/f'annotator_{role}.csv','w',newline='',encoding='utf-8-sig') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();[w.writerow({k:m.get(k) for k in fields}) for m in manifest]
with open(root/'adjudication_template.csv','w',newline='',encoding='utf-8-sig') as f:w=csv.DictWriter(f,fieldnames=fields+['adjudicator','adjudicated_at']);w.writeheader()
(root/'paper_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');(root/'machine_hidden.json').write_text(json.dumps(hidden,ensure_ascii=False,indent=2),encoding='utf-8');(root/'fulltext_manifest.json').write_text(json.dumps([m for m in manifest if m['fulltext_path']],ensure_ascii=False,indent=2),encoding='utf-8');(root/'unresolved_fulltext_queue.json').write_text(json.dumps([m for m in manifest if not m['fulltext_path']],ensure_ascii=False,indent=2),encoding='utf-8');(root/'README.md').write_text('Machine labels are isolated in machine_hidden.json. Annotators must not open it. Complete A/B independently, then adjudicate.\n',encoding='utf-8');shutil.copyfile(reports/'LITERATURE_VERIFICATION_GOLD_BENCHMARK_GUIDELINE.md',root/'annotation_guideline.md');print(len(manifest))

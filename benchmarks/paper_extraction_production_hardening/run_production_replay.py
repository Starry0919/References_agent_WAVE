from __future__ import annotations
import hashlib,json,os,statistics,sys,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from harness.paper_extraction import opus_extractor as oe
if os.getenv('PAPER_EXTRACTION_BENCH_CACHE_DIR'):
 oe.CACHE_DIR=Path(os.environ['PAPER_EXTRACTION_BENCH_CACHE_DIR'])
from harness.paper_extraction.handoff import build_handoff
from harness.paper_extraction.vendor.skills.skill08_evidence_binding.skill import EvidenceBindingEngine
from harness.paper_extraction.ddr_converter import convert_extraction_to_ddr
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parent; DOCS=ROOT/'harness/paper_extraction/vendor/clean_document_artifacts'

def corpus():
 v1=ROOT/'benchmarks/paper_extraction_e2e_v1';out=[]
 for split in ('development','holdout'):
  for pid in json.loads((v1/split/'manifest.json').read_text(encoding='utf-8'))['paper_ids']:
   p=next((DOCS/pid).rglob('clean_document.json'));raw=p.read_bytes();d=json.loads(raw)
   out.append({'paper_id':pid,'split':split,'document_id':(d.get('document_metadata')or{}).get('document_id') or p.parent.name,'source_path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'supplement_available':bool(d.get('supplements'))})
 return out
def request(x):return {'task_id':'production-hardening-'+x['paper_id'],'user_request':'Extract evidence-backed experimental design from this paper.','target_system':{'organism':'Escherichia coli','strain':'K-12'},'requirements':{},'clean_document_artifact':{'clean_json_path':x['source_path']}}
def one(x):
 t=time.perf_counter();r=oe.make_executor(oe.MODEL)(request(x));out=r.get('output') or {};row={**x,'skill07_status':r.get('status'),'eligible':r.get('eligible_for_evidence_verification'),'model':r.get('provenance',{}).get('model'),'cache_hit':r.get('provenance',{}).get('cache',{}).get('hit',False),'model_calls':0 if r.get('provenance',{}).get('cache',{}).get('hit') else (1 if r.get('provenance',{}).get('extractor')=='poe_code_cli' else 0),'input_tokens':r.get('metrics',{}).get('input_tokens'),'output_tokens':r.get('metrics',{}).get('output_tokens'),'repair_calls':r.get('metrics',{}).get('schema_repair_attempts',0),'experiments':len(out.get('experiment_instances',[])),'claims':len(out.get('atomic_claims',[])),'evidence_bundles':sum(len(c.get('evidence_bundle',[])) for c in out.get('atomic_claims',[]) if isinstance(c,dict)),'errors':r.get('errors',[]),'warnings':r.get('warnings',[])}
 if row['eligible']:
  document=json.loads(Path(x['source_path']).read_text(encoding='utf-8'));clean={**document,'clean_json_path':x['source_path'],'clean_json_artifact':{'artifact_id':'artifact:doc:'+x['sha256'][:20],'sha256':x['sha256'],'uri':x['source_path']}}
  h=build_handoff(r,clean,'artifact:skill07:'+x['sha256'][:20],0);s8=EvidenceBindingEngine(logger=lambda _:None,clock=lambda:datetime.now(timezone.utc)).execute({'handoff':h,'clean_document_artifact':clean});vs=s8.get('output',{}).get('claim_verifications',{});ver=[v.get('verification',{}) for v in vs.values()]
  row.update({'skill08_status':s8.get('status'),'e1':dict(__import__('collections').Counter(v.get('existence_status') for v in ver)),'e2':dict(__import__('collections').Counter(v.get('attribution_status') for v in ver)),'e3':dict(__import__('collections').Counter(v.get('semantic_support_status') for v in ver)),'provenance_complete':all(c.get('passed') for c in s8.get('self_check',{}).get('checks',[])),'admission':s8.get('output',{}).get('knowledge_admission',{}).get('status')})
  try:row['ddr']='created' if convert_extraction_to_ddr({'output':out,'skill08_output':s8.get('output',{}),'skill08_provenance':s8.get('provenance',{})},auto_save=False).ddr else 'blocked'
  except Exception as e:row['ddr']='failure';row['ddr_error']=str(e)
 row['runtime_seconds']=round(time.perf_counter()-t,3);return row
def run(label,workers):
 start=time.perf_counter();items=corpus();rows=[]
 with ThreadPoolExecutor(max_workers=workers) as pool:
  fs=[pool.submit(one,x) for x in items]
  for f in as_completed(fs):rows.append(f.result())
 rows.sort(key=lambda x:x['paper_id']);wall=time.perf_counter()-start;calls=sum(x['model_calls'] for x in rows);tokens=sum((x['input_tokens']or 0)+(x['output_tokens']or 0) for x in rows)
 report={'label':label,'production_path_verified':oe._poe_cli_configuration_error() is None,'model':oe.MODEL,'workers':workers,'attempted':len(rows),'completed':sum(x['skill07_status'] in {'succeeded','succeeded_with_warnings'} for x in rows),'eligible':sum(bool(x['eligible']) for x in rows),'wall_seconds':round(wall,3),'papers_per_minute':round(len(rows)/wall*60,3),'model_calls':calls,'tokens':tokens or None,'repair_calls':sum(x['repair_calls'] for x in rows),'cache_hits':sum(x['cache_hit'] for x in rows),'errors':sum(bool(x['errors']) for x in rows),'p50_seconds':statistics.median(x['runtime_seconds'] for x in rows),'p95_seconds':sorted(x['runtime_seconds'] for x in rows)[13],'records':rows}
 (BASE/f'{label}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');return report
if __name__=='__main__':
 label=sys.argv[1];workers=int(sys.argv[2]);print(json.dumps(run(label,workers),ensure_ascii=False))

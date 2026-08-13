from __future__ import annotations
import json
from pathlib import Path
from pypdf import PdfReader
from harness.literature_verification.verifier import verify_document

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'artifacts/data/literature'

def main():
 src=json.loads((DATA/'literature_discovery_benchmark_k12_tryptophan.json').read_text(encoding='utf-8'))
 rows=[]
 for p in src['candidates'][:20]:
  path=(p.get('acquisition') or {}).get('local_path'); verdict=None
  if path and Path(path).is_file():
   r=PdfReader(path);text='\n'.join((x.extract_text() or '') for x in r.pages)
   verdict=verify_document(p,text,(p['acquisition'] or {}).get('sha256'))
  meta=(p.get('relevance') or {}).get('decision')
  decision=(verdict or {}).get('judge',{}).get('decision','DATA_REQUIRED')
  change='verified' if verdict and decision in {'DIRECT_ENGINEERING_EVIDENCE','SUPPORTING_ENGINEERING_EVIDENCE'} else 'data_required' if not verdict else 'downgraded'
  rows.append({'paper_id':p['candidate_id'],'doi':p.get('doi'),'title':p['canonical_title'],'metadata_tier':meta,'fulltext_judge':decision,'change':change,'reason':(verdict or {}).get('judge',{}).get('reason','no verified full text'),'verification':verdict})
 out={'contract_version':'literature-shadow/1.0','mode':'shadow_no_ddr_write','rows':rows,'counts':{k:sum(r['change']==k for r in rows) for k in ['verified','downgraded','data_required']}}
 (DATA/'literature_verification_shadow_benchmark_k12_tryptophan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(out['counts'],indent=2))
if __name__=='__main__':main()

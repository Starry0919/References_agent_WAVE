from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from harness.paper_extraction.gold_infrastructure import *
def main():
 p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='cmd',required=True)
 for name in ('validate-draft','agreement','adjudication','completion'):q=sub.add_parser(name);q.add_argument('paper');q.add_argument('--role',default='ANNOTATOR_A')
 q=sub.add_parser('freeze');q.add_argument('version');q.add_argument('--actor',required=True)
 q=sub.add_parser('verify');q.add_argument('version')
 q=sub.add_parser('score');q.add_argument('version');q.add_argument('paper');q.add_argument('candidate',type=Path)
 sub.add_parser('readiness')
 q=sub.add_parser('status');q.add_argument('--all',action='store_true',dest='all_papers')
 q=sub.add_parser('advance');q.add_argument('--all',action='store_true',dest='all_papers');q.add_argument('--dry-run',action='store_true');q.add_argument('--allow-model-calls',action='store_true')
 a=p.parse_args()
 if a.cmd=='validate-draft':out=validate_draft(load_draft(a.paper,a.role),read(PACKAGES/a.paper/'source_index.json'))
 elif a.cmd=='agreement':out=agreement(load_draft(a.paper,'ANNOTATOR_A'),load_draft(a.paper,'ANNOTATOR_B'))
 elif a.cmd=='adjudication':out=build_adjudication_package(a.paper)
 elif a.cmd=='completion':out={'manifest':read(PACKAGES/a.paper/'manifest.json'),'validation':validate_draft(load_draft(a.paper,a.role),read(PACKAGES/a.paper/'source_index.json'))}
 elif a.cmd=='freeze':out=freeze(a.version,a.actor)
 elif a.cmd=='verify':out=verify_release(a.version)
 elif a.cmd=='score':out=score_candidate(a.version,a.paper,read(a.candidate))
 elif a.cmd=='readiness':out=readiness()
 elif a.cmd=='status':
  from harness.paper_extraction.accelerated_wave import inspect_state
  out=inspect_state()
 else:
  from harness.paper_extraction.accelerated_wave import advance
  out=advance(all_papers=a.all_papers,dry_run=a.dry_run,allow_model_calls=a.allow_model_calls)
 print(json.dumps(out,ensure_ascii=False,indent=2));sys.exit(0 if out.get('valid',True) else 2)
if __name__=='__main__':main()

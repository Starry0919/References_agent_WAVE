from __future__ import annotations
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from harness.paper_extraction.batch_runtime import BatchRuntime,WorkerConfig

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',default='artifacts/paper_batch_runtime');sub=p.add_subparsers(dest='command',required=True)
 s=sub.add_parser('submit');s.add_argument('manifest');s.add_argument('--dry-run',action='store_true')
 for name in ('status','metrics','resume','retry-failed','cancel'):
  x=sub.add_parser(name);x.add_argument('batch_id')
  if name=='resume':x.add_argument('--allow-model-calls',action='store_true')
 args=p.parse_args();rt=BatchRuntime(Path(args.root))
 if args.command=='submit':
  papers=json.loads(Path(args.manifest).read_text(encoding='utf-8'))['papers'];out=rt.dry_run(papers) if args.dry_run else rt.submit(papers)
 elif args.command=='status':out=rt.refresh_batch(args.batch_id)
 elif args.command=='metrics':out=rt.metrics(args.batch_id)
 elif args.command=='cancel':rt.cancel(args.batch_id);out=rt.refresh_batch(args.batch_id)
 elif args.command=='retry-failed':rt.retry_failed(args.batch_id);out=rt.refresh_batch(args.batch_id)
 else:out=rt.run(args.batch_id,{},allow_model_calls=args.allow_model_calls)
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

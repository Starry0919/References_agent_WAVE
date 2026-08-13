from __future__ import annotations
import json,shutil,tempfile,time,tracemalloc,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from harness.paper_extraction.batch_runtime import BatchRuntime,WorkerConfig

def run(n:int)->dict:
 root=Path(tempfile.mkdtemp(prefix=f'wave-batch-{n}-'));tracemalloc.start();start=time.perf_counter()
 try:
  rt=BatchRuntime(root,WorkerConfig(max_download_workers=16,max_mineru_workers=2,max_llm_workers=4,max_cpu_workers=8,max_db_workers=2,queue_capacity=128));m=rt.submit(({'paper_id':f'LOAD-{i:04d}','doi':f'10.9999/load.{i}'} for i in range(n)));submit_s=time.perf_counter()-start
  # Level 0 deliberately benchmarks durable scheduler/state persistence, not
  # Python handler/SQLite connection setup nine thousand times. Stage rows are
  # committed in one restart-safe transaction; targeted tests exercise live pools.
  with rt.connect() as c:
   rows=c.execute('select paper_job_id,paper_id from paper_jobs where batch_id=?',(m['batch_id'],)).fetchall();now=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
   stage_rows=[]
   for row in rows:
    for stage in ('metadata','download','mineru','cleaning','skill07','validation','ddr','frontend','persistence'):
     stage_rows.append((f"load_{row['paper_job_id']}_{stage}",row['paper_job_id'],stage,1,'SUCCEEDED','mock-input','mock-output','mock-config','1.0.0','mock-worker',now,now,0.0,0))
   c.executemany('INSERT INTO stage_runs(stage_run_id,paper_job_id,stage_id,attempt,status,input_hash,output_hash,config_hash,implementation_version,worker_id,started_at,ended_at,latency_ms,cache_hit) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',stage_rows)
   c.execute('update paper_jobs set status="SUCCEEDED",current_stage="persistence",updated_at=? where batch_id=?',(now,m['batch_id']))
  result=rt.refresh_batch(m['batch_id']);wall=time.perf_counter()-start;_,peak=tracemalloc.get_traced_memory();metrics=rt.metrics(m['batch_id']);size=sum(p.stat().st_size for p in root.rglob('*') if p.is_file())
  return {'jobs':n,'stage_records':n*9,'status':result['status'],'wall_s':wall,'admission_s':submit_s,'jobs_per_s':n/wall,'scheduler_persistence_overhead_ms_per_job':wall*1000/n,'peak_python_memory_mb':peak/1024**2,'disk_mb':size/1024**2,'metrics':metrics,'model_calls':0,'mode':'LEVEL_0_DETERMINISTIC_BULK_STATE'}
 finally:tracemalloc.stop();shutil.rmtree(root,ignore_errors=True)
if __name__=='__main__':
 results=[run(n) for n in (100,500,1000)];Path('paper_extraction_load_test_results.json').write_text(json.dumps({'levels':results},indent=2),encoding='utf-8');print(json.dumps(results,indent=2))

import io,zipfile
from pathlib import Path
from harness.paper_extraction.batch_runtime import BatchRuntime,WorkerConfig,StageFailure
from harness.paper_extraction.supplements import ingest,inspect_zip,unavailable

def papers(n):return [{'paper_id':f'P{i:04d}','doi':f'10.1/{i}'} for i in range(n)]
def identity(x):return x

def test_durable_restart_stage_state_and_transactional_outbox(tmp_path):
 rt=BatchRuntime(tmp_path);m=rt.submit(papers(3));rt=BatchRuntime(tmp_path)
 result=rt.run(m['batch_id'],{},allow_model_calls=True)
 assert result['status']=='COMPLETED' and result['counts']['SUCCEEDED']==3
 with rt.connect() as c:
  assert c.execute('select count(*) n from stage_runs').fetchone()['n']==27
  assert c.execute('select count(*) n from outbox').fetchone()['n']==3

def test_failure_isolation_terminal_visibility_and_retry_from_stage(tmp_path):
 rt=BatchRuntime(tmp_path);m=rt.submit(papers(4))
 def validate(x):
  if x['paper_id']=='P0002':raise StageFailure('VALIDATION_FAILURE','bad validation token=secret')
  return x
 result=rt.run(m['batch_id'],{'validation':validate},allow_model_calls=True)
 assert result['status']=='PARTIAL_SUCCESS' and result['counts']['SUCCEEDED']==3 and result['counts']['FAILED_PERMANENT']==1
 with rt.connect() as c:
  row=c.execute("select * from stage_runs where status='FAILED_PERMANENT'").fetchone()
  assert row['stage_id']=='validation' and 'secret' not in row['error_message']
  assert c.execute("select count(*) n from stage_runs where paper_job_id=? and stage_id='metadata'",(row['paper_job_id'],)).fetchone()['n']==1

def test_cross_batch_cache_version_correctness_and_model_permission(tmp_path,monkeypatch):
 rt=BatchRuntime(tmp_path);a=rt.submit(papers(1));rt.run(a['batch_id'],{},allow_model_calls=True)
 b=rt.submit(papers(1));result=rt.run(b['batch_id'],{},allow_model_calls=True);assert result['status']=='COMPLETED'
 with rt.connect() as c:assert c.execute("select count(*) n from stage_runs where paper_job_id like ? and status='SKIPPED_CACHE'",(f"paper_%",)).fetchone()['n']>0
 c=rt.submit([{'paper_id':'NEW'}]);blocked=rt.run(c['batch_id'],{},allow_model_calls=False);assert blocked['counts']['BLOCKED']==1

def test_backpressure_pool_isolation_and_mineru_global_gate(tmp_path):
 cfg=WorkerConfig(max_download_workers=4,max_mineru_workers=2,max_llm_workers=3,max_cpu_workers=4,queue_capacity=3)
 rt=BatchRuntime(tmp_path,cfg);m=rt.submit(papers(12));result=rt.run(m['batch_id'],{},allow_model_calls=True)
 assert result['status']=='COMPLETED' and rt.mineru.peak<=2

def test_cancel_and_dry_run_zero_calls(tmp_path):
 rt=BatchRuntime(tmp_path);d=rt.dry_run(papers(100));assert d['model_calls_performed']==0 and d['estimated_new_model_calls']==100
 m=rt.submit(papers(2));rt.cancel(m['batch_id']);r=rt.run(m['batch_id'],{},False);assert r['counts']['CANCELLED']==2

def test_supplement_structure_unavailable_and_zip_security(tmp_path):
 csv_art=ingest('P1','https://publisher/s1','data.csv',b'a,b\n1,2\n',tmp_path);assert csv_art['structure']['columns']==2 and csv_art['skill07_supplement_injection']=='DISABLED_BY_DEFAULT'
 buff=io.BytesIO()
 with zipfile.ZipFile(buff,'w') as z:z.writestr('../escape.txt','x')
 try:inspect_zip(buff.getvalue());assert False
 except ValueError:pass
 assert unavailable('P1')['availability']=='SUPPLEMENT_NOT_FOUND'

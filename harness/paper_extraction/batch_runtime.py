"""Durable, model-call-deny-by-default batch runtime for paper extraction.

Infrastructure wrapper only: scientific stage implementations and contracts
are not changed. SQLite is repository-native, transactional and restart-safe.
"""
from __future__ import annotations
import hashlib,json,os,random,re,shutil,sqlite3,threading,time,uuid
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED
from contextlib import contextmanager
from dataclasses import asdict,dataclass
from datetime import datetime,timezone
from pathlib import Path
from typing import Any,Callable,Iterable

STAGES=("metadata","download","mineru","cleaning","skill07","validation","ddr","frontend","persistence")
STAGE_VERSION={s:"1.0.0" for s in STAGES}
STAGE_RESOURCE={"metadata":"network","download":"network","mineru":"gpu_cpu_disk","cleaning":"cpu_disk","skill07":"provider","validation":"cpu","ddr":"cpu_disk","frontend":"cpu","persistence":"database_disk"}
STATES=("QUEUED","READY","RUNNING","SUCCEEDED","FAILED_RETRYABLE","FAILED_PERMANENT","BLOCKED","SKIPPED_CACHE","CANCELLED")
RETRY_POLICY={
 "NETWORK_TIMEOUT":(True,4),"HTTP_429":(True,6),"PROVIDER_RATE_LIMIT":(True,6),"PROVIDER_5XX":(True,4),
 "PDF_NOT_FOUND":(False,1),"PDF_CORRUPT":(False,1),"MINERU_FAILURE":(True,3),"GPU_OOM":(True,2),
 "JSON_PARSE":(True,2),"VALIDATION_FAILURE":(False,1),"DB_WRITE_FAILURE":(True,4),"UNKNOWN":(False,1),
}

def utc()->str:return datetime.now(timezone.utc).isoformat()
def digest(value:Any)->str:return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str).encode()).hexdigest()
def stable(prefix:str,*parts:Any)->str:return f"{prefix}_{uuid.uuid5(uuid.NAMESPACE_URL,'|'.join(map(str,parts))).hex}"
def redact(value:str)->str:
    value=re.sub(r'(?i)(api[_-]?key|token|authorization|password)\s*[:=]\s*\S+',r'\1=[REDACTED]',value)
    return value[:1000]

@dataclass(frozen=True)
class WorkerConfig:
    max_download_workers:int=8;max_mineru_workers:int=1;max_llm_workers:int=2;max_cpu_workers:int=4;max_db_workers:int=1;queue_capacity:int=64;max_retries:int=4
    def stage_workers(self,stage:str)->int:
        return self.max_download_workers if stage in {"metadata","download"} else self.max_mineru_workers if stage=="mineru" else self.max_llm_workers if stage=="skill07" else self.max_db_workers if stage=="persistence" else self.max_cpu_workers

class StageFailure(RuntimeError):
    def __init__(self,error_class:str,message:str):super().__init__(message);self.error_class=error_class

class MinerUGate:
    _instances:dict[str,"MinerUGate"]={};_lock=threading.Lock()
    def __new__(cls,key="global",slots=1,min_free_disk_gb=.5):
        with cls._lock:
            if key not in cls._instances:
                obj=super().__new__(cls);obj.sem=threading.BoundedSemaphore(max(1,slots));obj.slots=max(1,slots);obj.active=0;obj.peak=0;obj.guard=threading.Lock();obj.min_free_disk_gb=min_free_disk_gb;cls._instances[key]=obj
            return cls._instances[key]
    @contextmanager
    def acquire(self,temp_root:Path):
        if shutil.disk_usage(temp_root).free < self.min_free_disk_gb*1024**3:raise StageFailure("MINERU_FAILURE","insufficient temporary disk")
        self.sem.acquire()
        with self.guard:self.active+=1;self.peak=max(self.peak,self.active)
        try:yield
        finally:
            with self.guard:self.active-=1
            self.sem.release()

class BatchRuntime:
    def __init__(self,root:Path,config:WorkerConfig|None=None):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True);self.artifact_root=self.root/'artifacts';self.artifact_root.mkdir(exist_ok=True)
        self.db_path=self.root/'batch_runtime.sqlite3';self.config=config or WorkerConfig();self.mineru=MinerUGate(str(self.db_path),self.config.max_mineru_workers);self._init()
    def connect(self):
        c=sqlite3.connect(self.db_path,timeout=30);c.row_factory=sqlite3.Row;c.execute('PRAGMA journal_mode=WAL');c.execute('PRAGMA foreign_keys=ON');return c
    def _init(self):
        with self.connect() as c:c.executescript('''
        CREATE TABLE IF NOT EXISTS batches(batch_id TEXT PRIMARY KEY,status TEXT,priority TEXT,manifest_json TEXT,created_at TEXT,updated_at TEXT,cancelled INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS paper_jobs(paper_job_id TEXT PRIMARY KEY,batch_id TEXT,paper_id TEXT,identity TEXT,input_json TEXT,status TEXT,current_stage TEXT,created_at TEXT,updated_at TEXT,UNIQUE(batch_id,identity));
        CREATE TABLE IF NOT EXISTS stage_runs(stage_run_id TEXT PRIMARY KEY,paper_job_id TEXT,stage_id TEXT,attempt INTEGER,status TEXT,input_hash TEXT,output_hash TEXT,config_hash TEXT,implementation_version TEXT,worker_id TEXT,started_at TEXT,ended_at TEXT,retry_after REAL,error_class TEXT,error_message TEXT,queue_wait_ms REAL,worker_wait_ms REAL,latency_ms REAL,cache_hit INTEGER DEFAULT 0,UNIQUE(paper_job_id,stage_id,attempt));
        CREATE TABLE IF NOT EXISTS artifacts(artifact_id TEXT PRIMARY KEY,artifact_type TEXT,paper_id TEXT,sha256 TEXT,producer_stage TEXT,producer_version TEXT,source_hash TEXT,config_hash TEXT,storage_ref TEXT,created_at TEXT,UNIQUE(artifact_type,source_hash,producer_version,config_hash));
        CREATE TABLE IF NOT EXISTS outbox(id INTEGER PRIMARY KEY AUTOINCREMENT,batch_id TEXT,paper_job_id TEXT,event_type TEXT,payload_json TEXT,status TEXT,created_at TEXT,processed_at TEXT,UNIQUE(paper_job_id,event_type));
        CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,batch_id TEXT,paper_id TEXT,stage TEXT,status TEXT,attempt INTEGER,latency_ms REAL,queue_wait_ms REAL,worker_wait_ms REAL,cache_hit INTEGER,retries INTEGER,error_class TEXT,input_size INTEGER,output_size INTEGER,created_at TEXT);
        ''')
    def submit(self,papers:Iterable[dict[str,Any]],priority="NORMAL",batch_id:str|None=None)->dict[str,Any]:
        created=utc();papers=list(papers);normalized=[];seen=set();dupes=[]
        for p in papers:
            identity=str(p.get('doi') or p.get('pmid') or p.get('paper_id') or digest(p)).strip().lower()
            if identity in seen:dupes.append(identity);continue
            seen.add(identity);normalized.append((identity,p))
        bid=batch_id or stable('batch',created,digest([x for x,_ in normalized]));manifest={'batch_id':bid,'requested_count':len(papers),'admitted_count':len(normalized),'normalized_identities':[x for x,_ in normalized],'duplicates':dupes,'stage_versions':STAGE_VERSION,'config':asdict(self.config),'created_at':created,'skill07_supplement_injection':'DISABLED_BY_DEFAULT'}
        with self.connect() as c:
            c.execute('INSERT OR IGNORE INTO batches VALUES(?,?,?,?,?,?,0)',(bid,'QUEUED',priority,json.dumps(manifest),created,created))
            for identity,p in normalized:
                pid=str(p.get('paper_id') or identity);jid=stable('paper',bid,identity)
                c.execute('INSERT OR IGNORE INTO paper_jobs VALUES(?,?,?,?,?,?,?,?,?)',(jid,bid,pid,identity,json.dumps(p,ensure_ascii=False),'QUEUED',STAGES[0],created,created))
        return manifest
    def _artifact_hit(self,stage:str,source_hash:str,config_hash:str):
        with self.connect() as c:return c.execute('SELECT * FROM artifacts WHERE artifact_type=? AND source_hash=? AND producer_version=? AND config_hash=?',(stage,source_hash,STAGE_VERSION[stage],config_hash)).fetchone()
    def _run_one(self,row:sqlite3.Row,stage:str,handler:Callable[[dict[str,Any]],Any],allow_model_calls:bool)->None:
        jid=row['paper_job_id'];payload=json.loads(row['input_json']);attempt=self._attempt(jid,stage)+1;cfg=digest(asdict(self.config));input_hash=digest({'payload':payload,'stage':stage});runid=stable('stage',jid,stage,attempt);queued=time.perf_counter()
        if stage=='skill07' and not allow_model_calls:
            hit=self._artifact_hit(stage,input_hash,cfg)
            if not hit:self._finish_blocked(jid,runid,stage,attempt,input_hash,cfg,'MODEL_CALLS_NOT_ALLOWED');return
        hit=self._artifact_hit(stage,input_hash,cfg)
        if hit:self._finish_cached(jid,runid,stage,attempt,input_hash,cfg,hit['sha256']);return
        start=time.perf_counter();worker=threading.current_thread().name
        with self.connect() as c:c.execute('INSERT INTO stage_runs(stage_run_id,paper_job_id,stage_id,attempt,status,input_hash,config_hash,implementation_version,worker_id,started_at,queue_wait_ms) VALUES(?,?,?,?,?,?,?,?,?,?,?)',(runid,jid,stage,attempt,'RUNNING',input_hash,cfg,STAGE_VERSION[stage],worker,utc(),(start-queued)*1000));c.execute('UPDATE paper_jobs SET status="RUNNING",current_stage=?,updated_at=? WHERE paper_job_id=?',(stage,utc(),jid))
        try:
            if stage=='mineru':
                with self.mineru.acquire(self.root):output=handler(payload)
            else:output=handler(payload)
            raw=json.dumps(output,ensure_ascii=False,sort_keys=True,default=str).encode();out_hash=hashlib.sha256(raw).hexdigest();path=self.artifact_root/f'{out_hash}.json'
            if not path.exists():path.write_bytes(raw)
            next_stage=STAGES[STAGES.index(stage)+1] if stage!=STAGES[-1] else None;lat=(time.perf_counter()-start)*1000
            with self.connect() as c:
                c.execute('BEGIN IMMEDIATE');c.execute('INSERT OR IGNORE INTO artifacts VALUES(?,?,?,?,?,?,?,?,?,?)',(stable('artifact',stage,out_hash),stage,row['paper_id'],out_hash,stage,STAGE_VERSION[stage],input_hash,cfg,str(path),utc()));c.execute('UPDATE stage_runs SET status="SUCCEEDED",output_hash=?,ended_at=?,latency_ms=? WHERE stage_run_id=?',(out_hash,utc(),lat,runid));c.execute('UPDATE paper_jobs SET status=?,current_stage=?,input_json=?,updated_at=? WHERE paper_job_id=?',('SUCCEEDED' if next_stage is None else 'READY',next_stage,json.dumps(output,ensure_ascii=False),utc(),jid));
                if next_stage is None:c.execute('INSERT OR IGNORE INTO outbox(batch_id,paper_job_id,event_type,payload_json,status,created_at) VALUES(?,?,?,?,?,?)',(row['batch_id'],jid,'PAPER_COMMITTED',json.dumps({'artifact':out_hash}),'PENDING',utc()))
                c.execute('INSERT INTO events(batch_id,paper_id,stage,status,attempt,latency_ms,cache_hit,retries,input_size,output_size,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)',(row['batch_id'],row['paper_id'],stage,'SUCCEEDED',attempt,lat,0,attempt-1,len(json.dumps(payload)),len(raw),utc()))
        except Exception as exc:self._fail(row,runid,stage,attempt,input_hash,cfg,exc,start)
    def _attempt(self,jid,stage):
        with self.connect() as c:return c.execute('SELECT COALESCE(MAX(attempt),0) n FROM stage_runs WHERE paper_job_id=? AND stage_id=?',(jid,stage)).fetchone()['n']
    def _finish_blocked(self,jid,runid,stage,attempt,ih,cfg,msg):
        with self.connect() as c:c.execute('INSERT INTO stage_runs(stage_run_id,paper_job_id,stage_id,attempt,status,input_hash,config_hash,implementation_version,error_class,error_message,ended_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)',(runid,jid,stage,attempt,'BLOCKED',ih,cfg,STAGE_VERSION[stage],'MODEL_CALL_PERMISSION',msg,utc()));c.execute('UPDATE paper_jobs SET status="BLOCKED",current_stage=?,updated_at=? WHERE paper_job_id=?',(stage,utc(),jid))
    def _finish_cached(self,jid,runid,stage,attempt,ih,cfg,oh):
        next_stage=STAGES[STAGES.index(stage)+1] if stage!=STAGES[-1] else None
        with self.connect() as c:c.execute('INSERT INTO stage_runs(stage_run_id,paper_job_id,stage_id,attempt,status,input_hash,output_hash,config_hash,implementation_version,ended_at,cache_hit) VALUES(?,?,?,?,?,?,?,?,?,?,1)',(runid,jid,stage,attempt,'SKIPPED_CACHE',ih,oh,cfg,STAGE_VERSION[stage],utc()));c.execute('UPDATE paper_jobs SET status=?,current_stage=?,updated_at=? WHERE paper_job_id=?',('SUCCEEDED' if next_stage is None else 'READY',next_stage,utc(),jid))
    def _fail(self,row,runid,stage,attempt,ih,cfg,exc,start):
        cls=getattr(exc,'error_class','UNKNOWN');retryable,limit=RETRY_POLICY.get(cls,RETRY_POLICY['UNKNOWN']);limit=min(limit,self.config.max_retries);retry=retryable and attempt<limit;status='FAILED_RETRYABLE' if retry else 'FAILED_PERMANENT';delay=min(300,2**attempt)+random.random();lat=(time.perf_counter()-start)*1000
        with self.connect() as c:c.execute('UPDATE stage_runs SET status=?,ended_at=?,latency_ms=?,retry_after=?,error_class=?,error_message=? WHERE stage_run_id=?',(status,utc(),lat,time.time()+delay if retry else None,cls,redact(str(exc)),runid));c.execute('UPDATE paper_jobs SET status=?,current_stage=?,updated_at=? WHERE paper_job_id=?',(status,stage,utc(),row['paper_job_id']));c.execute('INSERT INTO events(batch_id,paper_id,stage,status,attempt,latency_ms,retries,error_class,created_at) VALUES(?,?,?,?,?,?,?,?,?)',(row['batch_id'],row['paper_id'],stage,status,attempt,lat,attempt-1,cls,utc()))
    def run(self,batch_id:str,handlers:dict[str,Callable[[dict[str,Any]],Any]],allow_model_calls=False)->dict[str,Any]:
        with self.connect() as c:c.execute('UPDATE batches SET status="RUNNING",updated_at=? WHERE batch_id=?',(utc(),batch_id));c.execute('UPDATE paper_jobs SET status="READY" WHERE batch_id=? AND status="QUEUED"',(batch_id,))
        pools={s:ThreadPoolExecutor(max_workers=self.config.stage_workers(s),thread_name_prefix=s) for s in STAGES};active=set()
        try:
            while True:
                with self.connect() as c:
                    cancelled=c.execute('SELECT cancelled FROM batches WHERE batch_id=?',(batch_id,)).fetchone()['cancelled'];rows=c.execute('SELECT * FROM paper_jobs WHERE batch_id=? AND status IN ("READY","FAILED_RETRYABLE") ORDER BY created_at LIMIT ?',(batch_id,max(1,self.config.queue_capacity-len(active)))).fetchall();remaining=c.execute('SELECT COUNT(*) n FROM paper_jobs WHERE batch_id=? AND status IN ("QUEUED","READY","RUNNING","FAILED_RETRYABLE")',(batch_id,)).fetchone()['n']
                if cancelled:
                    with self.connect() as c:c.execute('UPDATE paper_jobs SET status="CANCELLED" WHERE batch_id=? AND status IN ("QUEUED","READY","FAILED_RETRYABLE")',(batch_id,));break
                for row in rows:
                    if row['status']=='FAILED_RETRYABLE':
                        with self.connect() as c:
                            rr=c.execute('SELECT retry_after FROM stage_runs WHERE paper_job_id=? AND stage_id=? ORDER BY attempt DESC LIMIT 1',(row['paper_job_id'],row['current_stage'])).fetchone()
                        if rr and rr['retry_after'] and rr['retry_after']>time.time():continue
                    with self.connect() as c:c.execute('UPDATE paper_jobs SET status="RUNNING" WHERE paper_job_id=?',(row['paper_job_id'],))
                    stage=row['current_stage'];active.add(pools[stage].submit(self._run_one,row,stage,handlers.get(stage,lambda x:x),allow_model_calls))
                if active:
                    done,active=wait(active,timeout=.05,return_when=FIRST_COMPLETED)
                    for f in done:f.result()
                elif not remaining:break
                else:time.sleep(.02)
        finally:
            for p in pools.values():p.shutdown(wait=True)
        return self.refresh_batch(batch_id)
    def refresh_batch(self,batch_id):
        with self.connect() as c:
            counts={r['status']:r['n'] for r in c.execute('SELECT status,COUNT(*) n FROM paper_jobs WHERE batch_id=? GROUP BY status',(batch_id,))};total=sum(counts.values());failed=counts.get('FAILED_PERMANENT',0)+counts.get('BLOCKED',0);done=counts.get('SUCCEEDED',0)+counts.get('CANCELLED',0)+failed
            status='RUNNING_WITH_FAILURES' if failed and done<total else 'PARTIAL_SUCCESS' if failed else 'COMPLETED' if total and done==total else 'RUNNING'
            c.execute('UPDATE batches SET status=?,updated_at=? WHERE batch_id=?',(status,utc(),batch_id));return {'batch_id':batch_id,'status':status,'total':total,'counts':counts}
    def cancel(self,batch_id):
        with self.connect() as c:c.execute('UPDATE batches SET cancelled=1,updated_at=? WHERE batch_id=?',(utc(),batch_id))
    def retry_failed(self,batch_id):
        with self.connect() as c:c.execute('UPDATE paper_jobs SET status="READY",updated_at=? WHERE batch_id=? AND status IN ("FAILED_PERMANENT","BLOCKED")',(utc(),batch_id))
    def metrics(self,batch_id)->dict[str,Any]:
        with self.connect() as c:rows=c.execute('SELECT stage,latency_ms,cache_hit,status FROM events WHERE batch_id=?',(batch_id,)).fetchall();created=c.execute('SELECT created_at FROM batches WHERE batch_id=?',(batch_id,)).fetchone()['created_at'];depth=c.execute('SELECT status,COUNT(*) n FROM paper_jobs WHERE batch_id=? GROUP BY status',(batch_id,)).fetchall()
        by={}
        for s in STAGES:
            vals=sorted(r['latency_ms'] for r in rows if r['stage']==s and r['latency_ms'] is not None);by[s]={'count':len(vals),'p50_ms':vals[len(vals)//2] if vals else None,'p95_ms':vals[min(len(vals)-1,int(len(vals)*.95))] if vals else None}
        return {'batch_id':batch_id,'elapsed_s':max(.001,(datetime.now(timezone.utc)-datetime.fromisoformat(created)).total_seconds()),'queue_depth':{r['status']:r['n'] for r in depth},'stages':by,'cache_hit_rate':sum(r['cache_hit'] for r in rows)/len(rows) if rows else 0,'mineru_peak_workers':self.mineru.peak}
    def dry_run(self,papers:Iterable[dict[str,Any]])->dict[str,Any]:
        papers=list(papers);return {'papers':len(papers),'duplicates':len(papers)-len({str(x.get('doi') or x.get('paper_id') or digest(x)).lower() for x in papers}),'stages':list(STAGES),'worker_profile':asdict(self.config),'estimated_new_model_calls':sum(1 for _ in papers),'model_calls_performed':0}

import os
from concurrent.futures import ThreadPoolExecutor
from threading import RLock
from ..module import execute
class TaskManager:
    def __init__(self,max_workers=None):
        if max_workers is None:
            max_workers=max(1,int(os.getenv("PAPER_EXTRACTION_TASK_WORKERS","2")))
        self.max_workers=max_workers
        self.pool=ThreadPoolExecutor(max_workers=max_workers);self.tasks={};self.lock=RLock()
    def submit(self,request,options=None):
        task_id=request["task_id"]
        with self.lock:self.tasks[task_id]={"status":"running","result":None,"error":None}
        future=self.pool.submit(execute,request,options)
        future.add_done_callback(lambda f:self._done(task_id,f))
        return {"task_id":task_id,"status":"running"}
    def _done(self,task_id,future):
        try:result=future.result();value={"status":result["status"].lower(),"result":result,"error":None}
        except Exception as exc:value={"status":"failed","result":None,"error":f"{type(exc).__name__}: {exc}"}
        with self.lock:self.tasks[task_id]=value
    def seed(self,task_id,status,result=None,error=None):
        """Register a task's already-known outcome without running it -
        lets a caller restore history across a process restart from a
        checkpoint that's already on disk, instead of re-running the whole
        pipeline just to reproduce a report that already exists."""
        with self.lock:self.tasks[task_id]={"status":status,"result":result,"error":error}
    def status(self,task_id):
        with self.lock:
            value=self.tasks.get(task_id)
            if value is None:raise KeyError(task_id)
            return {"task_id":task_id,"status":value["status"],"error":value["error"]}
    def result(self,task_id):
        with self.lock:
            value=self.tasks.get(task_id)
            if value is None:raise KeyError(task_id)
            return value["result"]
    def delete(self,task_id):
        with self.lock:
            return self.tasks.pop(task_id,None) is not None

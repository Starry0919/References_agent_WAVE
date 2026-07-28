from concurrent.futures import ThreadPoolExecutor
from threading import RLock
from ..module import execute
class TaskManager:
    def __init__(self,max_workers=2):
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

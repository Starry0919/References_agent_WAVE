import json
from pathlib import Path
class WorkflowLogger:
    def __init__(self,path):self.path=Path(path)
    def write(self,event):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open("a",encoding="utf-8") as f:f.write(json.dumps(event,ensure_ascii=False,default=str)+"\n")

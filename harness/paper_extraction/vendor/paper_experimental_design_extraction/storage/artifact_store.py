from __future__ import annotations
import json,os,tempfile,time
from pathlib import Path
class ArtifactStore:
    def __init__(self,root):self.root=Path(root)
    def save_checkpoint(self,task_id,state):
        folder=self.root/task_id;folder.mkdir(parents=True,exist_ok=True)
        target=folder/"checkpoint.json"
        fd,temp=tempfile.mkstemp(dir=folder,suffix=".tmp")
        try:
            with os.fdopen(fd,"w",encoding="utf-8") as f:json.dump(state,f,ensure_ascii=False,indent=2,default=str)
            # Windows: a file indexer/AV/cloud-sync client (e.g. OneDrive,
            # common under a synced Desktop/Documents tree) can hold a
            # transient handle on `target` right after it's (re)written,
            # making os.replace raise PermissionError/WinError 5 for a few
            # hundred ms even though nothing in this process holds it open.
            # This checkpoint is written after every single skill in a
            # 13-stage pipeline, so without a retry a run has many chances
            # to hit this and die on a purely transient OS-level race.
            for attempt in range(6):
                try:
                    os.replace(temp,target);break
                except PermissionError:
                    if attempt==5:raise
                    time.sleep(0.1*(2**attempt))
        finally:
            if os.path.exists(temp):os.unlink(temp)
        return target
    def load_checkpoint(self,task_id):
        path=self.root/task_id/"checkpoint.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None

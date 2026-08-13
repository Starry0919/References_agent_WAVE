from .task_manager import TaskManager
manager=TaskManager()
def create_app():
    try:from fastapi import FastAPI,HTTPException
    except ImportError as exc:raise RuntimeError("Install optional dependency: pip install fastapi uvicorn") from exc
    app=FastAPI(title="论文实验设计抽取",version="0.1.0")
    @app.post("/api/paper-experimental-design/run")
    def run(request:dict):
        try:return manager.submit(request)
        except Exception as exc:raise HTTPException(400,str(exc))
    @app.get("/api/paper-experimental-design/status/{task_id}")
    def status(task_id:str):
        try:return manager.status(task_id)
        except KeyError:raise HTTPException(404,"task not found")
    @app.get("/api/paper-experimental-design/result/{task_id}")
    def result(task_id:str):
        try:
            value=manager.result(task_id)
            if value is None:raise HTTPException(202,"task still running")
            return value
        except KeyError:raise HTTPException(404,"task not found")
    return app

import json
import threading
import time
from types import SimpleNamespace

from harness.paper_extraction import service
from paper_experimental_design_extraction.workflow.engine import WorkflowEngine


def _state(task_id: str) -> dict:
    return {
        "task_id": task_id,
        "status": "RUNNING",
        "context": {},
        "artifacts": [],
        "errors": [],
        "warnings": [],
        "skill_states": {},
        "skill_logs": [],
    }


def _engine(tmp_path) -> WorkflowEngine:
    return WorkflowEngine(SimpleNamespace(state_dir=tmp_path, language="zh"))


def test_list_tasks_first_call_restores_completed_history(monkeypatch, tmp_path):
    task_id = "restored-completed-task"
    registry_path = tmp_path / "task_registry.json"
    runtime_dir = tmp_path / "runtime"
    checkpoint_dir = runtime_dir / task_id
    checkpoint_dir.mkdir(parents=True)
    meta = {
        "project_id": "project-1",
        "submitted_at": 123.0,
        "user_request": "restore me",
        "organism": "",
        "strain": "",
        "result_level": "extract",
        "document_kind": "auto",
        "source_type": "upload",
        "extraction_model": "test-model",
    }
    registry_path.write_text(
        json.dumps({task_id: {"meta": meta, "request": {}, "options": {}}}),
        encoding="utf-8",
    )
    checkpoint = _state(task_id)
    checkpoint.update({"status": "COMPLETED", "updated_at": "2026-07-30T12:00:00+00:00"})
    (checkpoint_dir / "checkpoint.json").write_text(json.dumps(checkpoint), encoding="utf-8")

    class FakeTaskManager:
        def __init__(self):
            self.tasks = {}

        def seed(self, incoming, status, result=None, error=None):
            self.tasks[incoming] = {"status": status, "result": result, "error": error}

        def status(self, incoming):
            value = self.tasks[incoming]
            return {"task_id": incoming, "status": value["status"], "error": value["error"]}

    monkeypatch.setattr(service, "_REGISTRY_PATH", registry_path)
    monkeypatch.setattr(service, "RUNTIME_DIR", runtime_dir)
    monkeypatch.setattr(service, "TaskManager", FakeTaskManager)
    monkeypatch.setattr(service, "_manager", None)
    monkeypatch.setattr(service, "_task_meta", {})

    rows = service.list_tasks(project_id="project-1")

    assert [row["task_id"] for row in rows] == [task_id]
    assert rows[0]["status"] == "completed"
    assert service._manager.tasks[task_id]["result"]["updated_at"] == "2026-07-30T12:00:00+00:00"


def test_failed_item_is_not_counted_as_completed(monkeypatch, tmp_path):
    engine = _engine(tmp_path)
    skill = "skill07_experiment_extraction"
    results = iter(
        [
            {"status": "succeeded", "output": {"paper_id": "paper-1"}, "errors": [], "warnings": []},
            {
                "status": "terminal_failure",
                "output": None,
                "errors": [{"code": "MODEL_FAILED", "message": "boom", "retryable": True}],
                "warnings": [],
            },
        ]
    )

    class Registry:
        @staticmethod
        def execute(_skill, _payload, _kwargs):
            return next(results)

    engine.registry = Registry()
    monkeypatch.setattr(engine, "_inputs", lambda *_args: [{"paper": 1}, {"paper": 2}])
    state = _state("failed-progress-task")

    engine._run_stage(skill, {}, state, {"checkpoint_heartbeat_seconds": 0})

    assert state["skill_states"][skill] == "FAILED"
    assert state["skill_progress"][skill] == {"completed": 1, "total": 2}
    persisted = json.loads((tmp_path / state["task_id"] / "checkpoint.json").read_text(encoding="utf-8"))
    assert persisted["skill_progress"][skill] == {"completed": 1, "total": 2}
    report = engine._report(None, state)
    assert report["skill_progress"][skill] == {"completed": 1, "total": 2}
    assert report["updated_at"] == state["updated_at"]


def test_blocking_executor_persists_zero_progress_and_heartbeats(monkeypatch, tmp_path):
    engine = _engine(tmp_path)
    skill = "skill07_experiment_extraction"
    entered = threading.Event()
    release = threading.Event()

    class Registry:
        @staticmethod
        def execute(_skill, _payload, _kwargs):
            entered.set()
            assert release.wait(2)
            return {"status": "succeeded", "output": None, "errors": [], "warnings": []}

    engine.registry = Registry()
    monkeypatch.setattr(engine, "_inputs", lambda *_args: [{"paper": 1}])
    state = _state("heartbeat-task")
    failures = []

    def run_stage():
        try:
            engine._run_stage(
                skill,
                {},
                state,
                {"checkpoint_heartbeat_seconds": 0.02},
            )
        except Exception as exc:  # pragma: no cover - asserted below
            failures.append(exc)

    worker = threading.Thread(target=run_stage)
    worker.start()
    assert entered.wait(1)
    checkpoint_path = tmp_path / state["task_id"] / "checkpoint.json"
    initial = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    assert initial["skill_progress"][skill] == {"completed": 0, "total": 1}
    first_updated_at = initial["updated_at"]

    deadline = time.monotonic() + 1
    heartbeat = initial
    while heartbeat["updated_at"] == first_updated_at and time.monotonic() < deadline:
        time.sleep(0.01)
        heartbeat = json.loads(checkpoint_path.read_text(encoding="utf-8"))

    release.set()
    worker.join(2)

    assert not worker.is_alive()
    assert failures == []
    assert heartbeat["updated_at"] != first_updated_at
    assert state["skill_progress"][skill] == {"completed": 1, "total": 1}

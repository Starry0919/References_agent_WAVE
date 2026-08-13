import json

from harness.paper_extraction import service


def test_get_status_reconciles_terminal_checkpoint(tmp_path, monkeypatch):
    task_id = "terminal-checkpoint-still-running-in-memory"
    runtime = tmp_path / "runtime"
    task_dir = runtime / task_id
    task_dir.mkdir(parents=True)
    state = {
        "task_id": task_id,
        "status": "COMPLETED",
        "context": {},
        "artifacts": [],
        "errors": [],
        "warnings": [],
        "skill_states": {},
        "skill_logs": {},
        "skill_progress": {},
        "start_time": None,
        "end_time": None,
    }
    (task_dir / "checkpoint.json").write_text(json.dumps(state), encoding="utf-8")

    manager = service.TaskManager(max_workers=1)
    manager.seed(task_id, "running")
    monkeypatch.setattr(service, "RUNTIME_DIR", runtime)
    monkeypatch.setattr(service, "_manager", manager)

    status = service.get_status(task_id)
    assert status["status"] == "completed"
    assert service.get_result(task_id)["status"] == "COMPLETED"

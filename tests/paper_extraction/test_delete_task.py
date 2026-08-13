import pytest

from harness.paper_extraction import service


def _register_task(task_id: str, status: str) -> None:
    """Register a task directly against the manager/meta stores, bypassing
    `submit_run` (which kicks off the real pipeline) - these tests only
    care about `delete_task`'s bookkeeping, not pipeline execution."""
    service._get_manager().tasks[task_id] = {"status": status, "result": None, "error": None}
    service._task_meta[task_id] = {
        "project_id": None,
        "submitted_at": 0,
        "user_request": "test",
        "organism": "",
        "strain": "",
        "result_level": "extract",
        "document_kind": "auto",
        "source_type": "auto_search",
        "extraction_model": "test-model",
    }


def test_delete_task_removes_completed_task_from_history():
    task_id = "delete-me-completed"
    _register_task(task_id, "completed")

    service.delete_task(task_id)

    assert task_id not in service._task_meta
    with pytest.raises(KeyError):
        service.get_status(task_id)
    assert all(row["task_id"] != task_id for row in service.list_tasks())


def test_delete_task_removes_failed_task_from_history():
    task_id = "delete-me-failed"
    _register_task(task_id, "failed")

    service.delete_task(task_id)

    assert task_id not in service._task_meta
    with pytest.raises(KeyError):
        service.get_status(task_id)


def test_delete_task_refuses_a_running_task():
    task_id = "delete-me-running"
    _register_task(task_id, "running")

    with pytest.raises(ValueError):
        service.delete_task(task_id)

    # Left untouched - still visible in history, still pollable.
    assert task_id in service._task_meta
    assert service.get_status(task_id)["status"] == "running"

    service._get_manager().tasks.pop(task_id, None)
    service._task_meta.pop(task_id, None)


def test_delete_task_unknown_id_raises_key_error():
    with pytest.raises(KeyError):
        service.delete_task("does-not-exist")

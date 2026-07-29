import json

from harness.paper_extraction import ddr_converter, result_summary, service


def _register_completed_task(task_id: str, output: dict) -> None:
    """Same bypass-the-real-pipeline pattern as test_delete_task.py: register
    a finished task directly against the manager, no actual extraction run.

    `experimental_designs` (not `output`/`paper_artifacts`) is the real
    per-paper list in WorkflowEngine._report()'s shape - verified against a
    live run's `GET /api/paper-extraction/tasks/{id}` response - literally
    `context.skill07` (one already-unwrapped skill07 `output` dict per
    paper), see workflow/engine.py::WorkflowEngine._report.
    """
    service._get_manager().tasks[task_id] = {"status": "completed", "result": {"experimental_designs": [output]}, "error": None}


def _write_checkpoint(runtime_dir, task_id: str, *, identity: dict, fields: dict) -> None:
    task_dir = runtime_dir / task_id
    task_dir.mkdir(parents=True)
    checkpoint = {
        "status": "COMPLETED",
        "skill_states": {},
        "context": {
            "paper_artifacts": [{"paper_identity": identity}],
            "skill01": {},
            "skill07": [{"fields": fields, "extensions": {}}],
            "skill08": [{"literature_experiment": {"fields": fields}, "evidence_map": {}, "coverage": {}}],
            "skill09": [{"quality_evaluation": {}, "evaluation_report": {}}],
            "skill12": {},
        },
    }
    (task_dir / "checkpoint.json").write_text(json.dumps(checkpoint), encoding="utf-8")


def test_ensure_task_saved_as_evidence_saves_title_and_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr(ddr_converter, "DDR_DIR", tmp_path / "ddr_database")
    monkeypatch.setattr(result_summary, "RUNTIME_DIR", tmp_path / "runtime")

    task_id = "test-task-ensure-saved"
    identity = {
        "paper_id": "p1",
        "title": "A Test Paper About Tryptophan Overproduction",
        "authors": ["A. Author", "B. Author"],
        "journal": "J. Synthetic Biology",
        "year": 2024,
        "doi": "10.1234/test-doi",
    }
    fields = {"objective": {"value": "improve titer", "status": "reported", "confidence": 0.8, "evidence_ids": []}}
    _write_checkpoint(tmp_path / "runtime", task_id, identity=identity, fields=fields)
    _register_completed_task(task_id, output={"fields": fields, "experimental_design_object": {}})

    try:
        saved = ddr_converter.ensure_task_saved_as_evidence(task_id)
        assert len(saved) == 1
        assert saved[0]["paper_index"] == 0
        ddr_id = saved[0]["evidence_source_id"]
        assert ddr_id

        ddr_dir = tmp_path / "ddr_database"
        files = list(ddr_dir.glob("DDR-*.json"))
        assert len(files) == 1
        saved_ddr = json.loads(files[0].read_text(encoding="utf-8"))

        # Bug fix: real paper identity (not an empty title) makes it into the
        # saved DDR, since ensure_task_saved_as_evidence now feeds
        # `paper_identity` from build_extraction_summary's identity dict.
        assert saved_ddr["metadata"]["title"] == identity["title"]
        assert saved_ddr["metadata"]["reference"]["doi"] == identity["doi"]

        meta = saved_ddr["extraction_meta"]
        assert meta["paper_extraction_task_id"] == task_id
        assert meta["paper_index"] == 0
        assert meta["paper_extraction_detail"] is not None
        assert meta["paper_extraction_detail"]["identity"]["title"] == identity["title"]

        # Idempotency: calling again must not create a second DDR file, and
        # must return the same evidence_source_id.
        saved_again = ddr_converter.ensure_task_saved_as_evidence(task_id)
        assert saved_again == saved
        assert len(list(ddr_dir.glob("DDR-*.json"))) == 1
    finally:
        service._get_manager().tasks.pop(task_id, None)


def test_ensure_task_saved_as_evidence_noop_for_incomplete_task(tmp_path, monkeypatch):
    monkeypatch.setattr(ddr_converter, "DDR_DIR", tmp_path / "ddr_database")
    monkeypatch.setattr(result_summary, "RUNTIME_DIR", tmp_path / "runtime")

    task_id = "test-task-running"
    service._get_manager().tasks[task_id] = {"status": "running", "result": None, "error": None}
    try:
        assert ddr_converter.ensure_task_saved_as_evidence(task_id) == []
        assert not (tmp_path / "ddr_database").exists() or list((tmp_path / "ddr_database").glob("DDR-*.json")) == []
    finally:
        service._get_manager().tasks.pop(task_id, None)

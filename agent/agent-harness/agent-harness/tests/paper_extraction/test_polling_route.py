from harness.api import paper_extraction


def test_polling_route_skips_translation_and_returns_submission_time(monkeypatch):
    task_id = "task-live-poll"
    calls: list[tuple[str, bool]] = []

    monkeypatch.setattr(
        paper_extraction.service,
        "get_status",
        lambda incoming: {"task_id": incoming, "status": "running", "error": None},
    )
    monkeypatch.setattr(paper_extraction.service, "get_result", lambda _task_id: None)
    monkeypatch.setattr(
        paper_extraction.service,
        "get_task_metadata",
        lambda _task_id: {"submitted_at": 1_785_412_573.5},
    )
    monkeypatch.setattr(
        paper_extraction.service,
        "get_live_skill_states",
        lambda _task_id: {"skill07_experiment_extraction": "RUNNING"},
    )
    monkeypatch.setattr(paper_extraction.service, "get_live_skill_progress", lambda _task_id: {})
    monkeypatch.setattr(paper_extraction.service, "get_live_skill_warnings", lambda _task_id: [])

    def fake_summary(incoming: str, *, translate_titles: bool):
        calls.append((incoming, translate_titles))
        return {"papers": [], "skill_states": {}}

    monkeypatch.setattr(paper_extraction, "build_extraction_summary", fake_summary)

    response = paper_extraction.get_task(task_id)

    assert calls == [(task_id, False)]
    assert response["submitted_at"] == 1_785_412_573.5
    assert response["skill_states"] == {"skill07_experiment_extraction": "RUNNING"}


def test_completed_poll_reuses_the_untranslated_summary_for_evidence_save(monkeypatch):
    task_id = "task-completed-poll"
    summary = {"papers": [], "skill_states": {}}
    saved_with: list[dict] = []

    monkeypatch.setattr(
        paper_extraction.service,
        "get_status",
        lambda incoming: {"task_id": incoming, "status": "completed", "error": None},
    )
    monkeypatch.setattr(
        paper_extraction.service,
        "get_result",
        lambda _task_id: {
            "skill_states": {"skill07_experiment_extraction": "FAILED"},
            "skill_progress": {"skill07_experiment_extraction": {"completed": 2, "total": 3}},
            "updated_at": "2026-07-30T12:00:00+00:00",
            "warnings": [],
        },
    )
    monkeypatch.setattr(
        paper_extraction.service,
        "get_task_metadata",
        lambda _task_id: {"submitted_at": 1_785_412_573.5},
    )
    monkeypatch.setattr(
        paper_extraction,
        "build_extraction_summary",
        lambda _task_id, *, translate_titles: summary if translate_titles is False else None,
    )

    def fake_save(_task_id: str, *, extraction_summary: dict):
        saved_with.append(extraction_summary)
        return []

    monkeypatch.setattr(paper_extraction, "ensure_task_saved_as_evidence", fake_save)

    response = paper_extraction.get_task(task_id)

    assert response["status"] == "completed"
    assert saved_with == [summary]
    assert response["skill_progress"] == {
        "skill07_experiment_extraction": {"completed": 2, "total": 3}
    }
    assert response["updated_at"] == "2026-07-30T12:00:00+00:00"

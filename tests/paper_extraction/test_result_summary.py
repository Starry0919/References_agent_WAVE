import json

from harness.paper_extraction import result_summary


def _write_checkpoint(runtime_dir, task_id: str, *, fields: dict, bound_fields: dict | None = None) -> None:
    """Same fixture shape as test_ddr_converter.py's `_write_checkpoint` -
    `fields` is skill07's raw per-field output; `bound_fields` (defaults to
    `fields` itself) is what skill08 re-published after evidence binding."""
    task_dir = runtime_dir / task_id
    task_dir.mkdir(parents=True)
    checkpoint = {
        "status": "COMPLETED",
        "skill_states": {},
        "context": {
            "paper_artifacts": [{"paper_identity": {"paper_id": "p1", "title": "Test Paper"}}],
            "skill01": {},
            "skill07": [{"fields": fields, "extensions": {}}],
            "skill08": [{"literature_experiment": {"fields": bound_fields if bound_fields is not None else fields}, "evidence_map": {}, "coverage": {}}],
            "skill09": [{"quality_evaluation": {}, "evaluation_report": {}}],
            "skill12": {},
        },
    }
    (task_dir / "checkpoint.json").write_text(json.dumps(checkpoint), encoding="utf-8")


def _field_by_key(summary: dict, key: str) -> dict:
    return next(f for f in summary["papers"][0]["design_fields"] if f["key"] == key)


def test_reported_field_carries_extraction_method_and_notes_into_reasoning(tmp_path, monkeypatch):
    """A directly-reported field (skill07's `notes` path, no inference) must
    surface its extraction_method/notes in `reasoning` - this is what backs
    the frontend's column-1 "Agent's Extraction Process" card, previously
    computed by skill07/skill08 and then silently dropped before reaching
    the API response."""
    monkeypatch.setattr(result_summary, "RUNTIME_DIR", tmp_path / "runtime")
    fields = {
        "medium": {
            "value": "M9 minimal medium", "status": "reported", "confidence": 0.9,
            "extraction_method": "hybrid", "evidence_ids": [], "notes": "derived from Methods section",
        },
    }
    _write_checkpoint(tmp_path / "runtime", "task-reported", fields=fields)

    summary = result_summary.build_extraction_summary("task-reported")

    field = _field_by_key(summary, "medium")
    assert field["reasoning"] == {
        "extraction_method": "hybrid",
        "notes": "derived from Methods section",
        "inference_method": None,
        "inference_rationale": None,
    }


def test_inferred_field_carries_inference_method_and_rationale_into_reasoning(tmp_path, monkeypatch):
    """A status="inferred" field's `inference: {method, rationale}` object
    (the opus_extractor prompt contract) must also reach `reasoning` -
    without it, an inferred claim would show no process narrative at all,
    which is exactly the kind of claim a reviewer most needs to see the
    reasoning behind."""
    monkeypatch.setattr(result_summary, "RUNTIME_DIR", tmp_path / "runtime")
    fields = {
        "hypothesis": {
            "value": "flux redistribution relieves the bottleneck", "status": "inferred", "confidence": 0.6,
            "extraction_method": "model_inference", "evidence_ids": [], "notes": None,
            "inference": {"method": "mechanistic reasoning", "rationale": "consistent with known precursor-supply constraints"},
        },
    }
    _write_checkpoint(tmp_path / "runtime", "task-inferred", fields=fields)

    summary = result_summary.build_extraction_summary("task-inferred")

    field = _field_by_key(summary, "hypothesis")
    assert field["reasoning"]["inference_method"] == "mechanistic reasoning"
    assert field["reasoning"]["inference_rationale"] == "consistent with known precursor-supply constraints"


def test_field_with_no_process_data_gets_an_all_null_reasoning_block(tmp_path, monkeypatch):
    """A field with no extraction_method/notes/inference recorded still gets
    a `reasoning` key (all-None) rather than the key being missing entirely -
    the frontend's AgentReasoningCard relies on this key always being
    present to decide whether to show its "no process notes" fallback."""
    monkeypatch.setattr(result_summary, "RUNTIME_DIR", tmp_path / "runtime")
    fields = {
        "strain": {"value": "E. coli MG1655", "status": "reported", "confidence": 0.9, "evidence_ids": []},
    }
    _write_checkpoint(tmp_path / "runtime", "task-empty", fields=fields)

    summary = result_summary.build_extraction_summary("task-empty")

    field = _field_by_key(summary, "strain")
    assert field["reasoning"] == {
        "extraction_method": None,
        "notes": None,
        "inference_method": None,
        "inference_rationale": None,
    }


def test_reasoning_survives_the_skill08_raw_field_fallback_path(tmp_path, monkeypatch):
    """Fields skill08 never touched (e.g. the run stopped before skill08)
    still fall back to skill07's raw value in `_build_design_fields`'s
    second loop - `reasoning` must be populated on that path too, not just
    the skill08-bound-fields loop."""
    monkeypatch.setattr(result_summary, "RUNTIME_DIR", tmp_path / "runtime")
    fields = {
        "assay": {
            "value": "HPLC", "status": "reported", "confidence": 0.8,
            "extraction_method": "rule", "evidence_ids": [], "notes": "matched a known assay keyword",
        },
    }
    # skill08 never processed this paper (bound_fields stays empty) -
    # forces `_build_design_fields`'s raw_fields fallback loop.
    _write_checkpoint(tmp_path / "runtime", "task-raw-fallback", fields=fields, bound_fields={})

    summary = result_summary.build_extraction_summary("task-raw-fallback")

    field = _field_by_key(summary, "assay")
    assert field["verified"] is False
    assert field["reasoning"]["extraction_method"] == "rule"
    assert field["reasoning"]["notes"] == "matched a known assay keyword"


def test_summary_accepts_experimental_design_object_list(tmp_path, monkeypatch):
    """A model may return one design object per experiment as a list.

    The detail endpoint must render that successful extraction instead of
    failing by calling ``.get`` on the list.
    """
    monkeypatch.setattr(result_summary, "RUNTIME_DIR", tmp_path / "runtime")
    _write_checkpoint(tmp_path / "runtime", "task-list-design", fields={})
    checkpoint_path = tmp_path / "runtime" / "task-list-design" / "checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    checkpoint["context"]["paper_artifacts"] = [{}]
    checkpoint["context"]["skill07"][0]["experimental_design_object"] = [
        {"paper_id": "paper-from-list", "experiment_id": "exp-1"},
        {"paper_id": "paper-from-list", "experiment_id": "exp-2"},
    ]
    checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")

    summary = result_summary.build_extraction_summary("task-list-design")

    assert summary["papers"][0]["paper_id"] == "paper-from-list"

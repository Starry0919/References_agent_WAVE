import json

import pytest

from harness.paper_extraction import calibration


def _step(step_num: int, **overrides: object) -> dict:
    base = {"step": step_num, "design_action": "M3", "evidence_grading": "硬", "reason_nature": "机理推断", "rule": "some rule"}
    base.update(overrides)
    return base


def _write_ddr(ddr_dir, ddr_id: str) -> None:
    ddr_dir.mkdir(parents=True, exist_ok=True)
    ddr = {"ddr_id": ddr_id, "schema_version": "2.0", "decision_chain": [], "extraction_meta": {"calibration_status": "pending"}}
    (ddr_dir / f"{ddr_id}_test.json").write_text(json.dumps(ddr, ensure_ascii=False), encoding="utf-8")


def test_detect_conflicts_flags_disagreeing_field():
    attempts = [
        {"annotator": "alice", "decision_chain": [_step(1, design_action="M3")]},
        {"annotator": "bob", "decision_chain": [_step(1, design_action="M5")]},
    ]
    conflicts = calibration.detect_conflicts(attempts)
    assert {"step": 1, "field": "design_action", "values_by_annotator": {"alice": "M3", "bob": "M5"}} in conflicts


def test_detect_conflicts_empty_when_attempts_agree():
    attempts = [
        {"annotator": "alice", "decision_chain": [_step(1)]},
        {"annotator": "bob", "decision_chain": [_step(1)]},
    ]
    assert calibration.detect_conflicts(attempts) == []


def test_detect_conflicts_needs_at_least_two_attempts():
    assert calibration.detect_conflicts([{"annotator": "alice", "decision_chain": [_step(1)]}]) == []


def test_detect_conflicts_flags_step_count_mismatch():
    attempts = [
        {"annotator": "alice", "decision_chain": [_step(1), _step(2)]},
        {"annotator": "bob", "decision_chain": [_step(1)]},
    ]
    conflicts = calibration.detect_conflicts(attempts)
    assert any(c["field"] == "step_count" for c in conflicts)


def test_record_extraction_attempt_flips_to_disputed_on_conflict(tmp_path, monkeypatch):
    ddr_dir = tmp_path / "ddr_database"
    monkeypatch.setattr(calibration, "DDR_DIR", ddr_dir)
    _write_ddr(ddr_dir, "DDR-020")

    calibration.record_extraction_attempt("DDR-020", "alice", [_step(1, reason_nature="机理推断")])
    result = calibration.record_extraction_attempt("DDR-020", "bob", [_step(1, reason_nature="筛选得来")])

    assert result["calibration_status"] == "disputed"
    assert result["conflicts"]

    saved = json.loads(next(ddr_dir.glob("DDR-020_*.json")).read_text(encoding="utf-8"))
    assert saved["extraction_meta"]["calibration_status"] == "disputed"
    assert len(saved["extraction_meta"]["extraction_attempts"]) == 2


def test_record_extraction_attempt_moves_to_in_progress_when_no_conflict(tmp_path, monkeypatch):
    ddr_dir = tmp_path / "ddr_database"
    monkeypatch.setattr(calibration, "DDR_DIR", ddr_dir)
    _write_ddr(ddr_dir, "DDR-021")

    calibration.record_extraction_attempt("DDR-021", "alice", [_step(1)])
    result = calibration.record_extraction_attempt("DDR-021", "bob", [_step(1)])

    assert result["calibration_status"] == "in_progress"
    assert result["conflicts"] == []


def test_record_extraction_attempt_missing_ddr_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(calibration, "DDR_DIR", tmp_path / "ddr_database")
    with pytest.raises(FileNotFoundError):
        calibration.record_extraction_attempt("DDR-999", "alice", [])


def test_get_conflicts_reads_back_recorded_attempts(tmp_path, monkeypatch):
    ddr_dir = tmp_path / "ddr_database"
    monkeypatch.setattr(calibration, "DDR_DIR", ddr_dir)
    _write_ddr(ddr_dir, "DDR-022")

    calibration.record_extraction_attempt("DDR-022", "alice", [_step(1, evidence_grading="硬")])
    calibration.record_extraction_attempt("DDR-022", "bob", [_step(1, evidence_grading="软")])

    conflicts = calibration.get_conflicts("DDR-022")
    assert any(c["field"] == "evidence_grading" for c in conflicts)

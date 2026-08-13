import json

from harness.paper_extraction import rule_distillation


def _ddr(ddr_id: str, *, rule: str | None, reason_nature: str = "机理推断", design_action: str = "M3") -> dict:
    return {
        "ddr_id": ddr_id,
        "schema_version": "2.0",
        "knowledge_admission": {
            "status": "KNOWLEDGE_ADMISSION_PARTIAL",
            "source_skill08_artifact_id": "artifact:skill08:test",
            "admitted_ddr_candidates": ["experiment:0:ddr"],
        },
        "decision_chain": [
            {
                "step": 1,
                "design_action": design_action,
                "target": {"gene": "trpE", "enzyme": "", "pathway": "", "condition": None},
                "trigger": {"observation": "feedback inhibition observed", "reasoning": "", "source_location": ""},
                "evidence": {"description": "", "source": "", "source_location": "", "values": {}},
                "evidence_grading": "硬",
                "evidence_grading_rationale": "",
                "reason_nature": reason_nature,
                "alternatives": [],
                "implementation": "点突变",
                "implementation_detail": "",
                "result": {"metric": "", "before": "", "after": "", "fold_change": None, "quantified": False},
                "rule": rule,
            }
        ],
    }


def _write_ddr(ddr_dir, ddr: dict) -> None:
    ddr_dir.mkdir(parents=True, exist_ok=True)
    (ddr_dir / f"{ddr['ddr_id']}_test.json").write_text(json.dumps(ddr, ensure_ascii=False), encoding="utf-8")


def _write_rules(rules_path, rules_doc: dict) -> None:
    rules_path.parent.mkdir(parents=True, exist_ok=True)
    rules_path.write_text(json.dumps(rules_doc, ensure_ascii=False), encoding="utf-8")


def test_distill_rules_skips_ddrs_already_covered_by_an_existing_rule(tmp_path, monkeypatch):
    ddr_dir = tmp_path / "ddr_database"
    rules_path = tmp_path / "biological_rules" / "rules.json"
    monkeypatch.setattr(rule_distillation, "DDR_DIR", ddr_dir)
    monkeypatch.setattr(rule_distillation, "RULES_PATH", rules_path)

    _write_ddr(ddr_dir, _ddr("DDR-001", rule="already distilled by a human"))
    _write_rules(rules_path, {
        "rules": [{"rule_id": "RULE-001", "statement": "existing", "source_ddrs": ["DDR-001 (some paper)"], "calibration_status": "pending"}],
        "governance": {},
    })

    candidates = rule_distillation.distill_rules(write=False)
    assert candidates == []


def test_distill_rules_picks_up_a_new_uncovered_ddr(tmp_path, monkeypatch):
    ddr_dir = tmp_path / "ddr_database"
    rules_path = tmp_path / "biological_rules" / "rules.json"
    monkeypatch.setattr(rule_distillation, "DDR_DIR", ddr_dir)
    monkeypatch.setattr(rule_distillation, "RULES_PATH", rules_path)

    _write_ddr(ddr_dir, _ddr("DDR-001", rule="covered rule"))
    _write_ddr(ddr_dir, _ddr("DDR-002", rule="a new mechanistic rule about feedback deregulation"))
    _write_rules(rules_path, {
        "rules": [{"rule_id": "RULE-001", "statement": "existing", "source_ddrs": ["DDR-001 (some paper)"], "calibration_status": "pending"}],
        "governance": {},
    })

    candidates = rule_distillation.distill_rules(write=False)
    assert len(candidates) == 1
    assert candidates[0]["statement"] == "a new mechanistic rule about feedback deregulation"
    assert candidates[0]["applicable_modules"] == ["M3"]
    # write=False must not touch the file on disk
    assert json.loads(rules_path.read_text(encoding="utf-8"))["rules"][0]["rule_id"] == "RULE-001"


def test_distill_rules_never_pulls_a_null_or_screening_rule(tmp_path, monkeypatch):
    ddr_dir = tmp_path / "ddr_database"
    rules_path = tmp_path / "biological_rules" / "rules.json"
    monkeypatch.setattr(rule_distillation, "DDR_DIR", ddr_dir)
    monkeypatch.setattr(rule_distillation, "RULES_PATH", rules_path)

    _write_ddr(ddr_dir, _ddr("DDR-003", rule=None, reason_nature="筛选得来"))
    _write_rules(rules_path, {"rules": [], "governance": {}})

    assert rule_distillation.distill_rules(write=False) == []


def test_distill_rules_write_true_appends_and_updates_governance(tmp_path, monkeypatch):
    ddr_dir = tmp_path / "ddr_database"
    rules_path = tmp_path / "biological_rules" / "rules.json"
    monkeypatch.setattr(rule_distillation, "DDR_DIR", ddr_dir)
    monkeypatch.setattr(rule_distillation, "RULES_PATH", rules_path)

    _write_ddr(ddr_dir, _ddr("DDR-010", rule="newly distilled rule"))
    _write_rules(rules_path, {"rules": [], "governance": {}})

    candidates = rule_distillation.distill_rules(write=True)
    assert len(candidates) == 1

    saved = json.loads(rules_path.read_text(encoding="utf-8"))
    assert len(saved["rules"]) == 1
    assert saved["rules"][0]["rule_id"] == "RULE-001"
    assert saved["governance"]["total_rules"] == 1
    assert saved["governance"]["pending_calibration"] == 1

    # Re-running must not duplicate — DDR-010 is now covered by RULE-001.
    assert rule_distillation.distill_rules(write=False) == []


def test_search_rules_matches_statement_and_module(tmp_path, monkeypatch):
    rules_path = tmp_path / "biological_rules" / "rules.json"
    monkeypatch.setattr(rule_distillation, "RULES_PATH", rules_path)
    _write_rules(rules_path, {
        "rules": [
            {"rule_id": "RULE-001", "statement": "feedback deregulation via resistant point mutation", "trigger_conditions": [], "applicable_modules": ["M3"], "source_ddrs": []},
            {"rule_id": "RULE-002", "statement": "unrelated fermentation optimization rule", "trigger_conditions": [], "applicable_modules": ["M9"], "source_ddrs": []},
        ],
        "governance": {},
    })

    hits = rule_distillation.search_rules("feedback")
    assert [r["rule_id"] for r in hits] == ["RULE-001"]

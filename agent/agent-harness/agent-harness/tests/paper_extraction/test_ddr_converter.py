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


# ---------------------------------------------------------------------------
# Scenario tests (design doc §4.1/§4.2 + Phase 4's 3 required behaviors) and
# regressions for the real Skill07 `experiments` shape (experiment_id/
# purpose/host/intervention/conditions/control/replicates/readout/outcome) -
# distinct from the design_steps/interventions[{purpose,rationale}] shape
# `_build_single_step` originally assumed and that no real extraction run
# ever actually produces (confirmed against DDR-006's on-disk output before
# this fix: every step landed on design_action="M3", implementation="KO",
# and every gene/trigger/evidence field blank).
# ---------------------------------------------------------------------------


def _experiment(**overrides: object) -> dict:
    base = {
        "experiment_id": "exp_1", "purpose": "", "host": "E. coli K-12",
        "intervention": "", "conditions": "M9 minimal medium", "control": "wild type",
        "replicates": "n=3", "readout": "HPLC titer", "outcome": "",
    }
    base.update(overrides)
    return base


def test_trp_style_step_gets_feedback_module_and_mechanistic_rule():
    """Test 1 (design doc Phase 4): a Trp-paper-shaped step — feedback
    inhibition language, a resistant point mutation, a measured titer
    change — should land on M3, get graded 硬 (measured/kinetic keywords),
    classified 机理推断, and keep a non-null rule if the source already
    supplied one."""
    exp = _experiment(
        purpose="Relieve feedback inhibition of anthranilate synthase (TrpE) by L-tryptophan, a known regulation mechanism",
        intervention="Site-directed point mutation TrpE(S40F) to resist feedback inhibition",
        outcome="Trp titer measured at 19 to 29 g/L; enzyme kinetics confirmed loss of feedback sensitivity",
        rule="天然产物先去调控:查 committed 酶的末端产物反馈抑制,用抗性突变解除",
    )
    result = ddr_converter.convert_extraction_to_ddr({
        "output": {"fields": {}, "experimental_design_object": {"experiments": [exp]}},
    })
    step = result.ddr["decision_chain"][0]
    assert step["design_action"] == "M3"
    assert step["reason_nature"] == "机理推断"
    assert step["evidence_grading"] == "硬"
    assert step["evidence_grading_rationale"].startswith("自动启发式判定")
    assert step["rule"] is not None


def test_screening_derived_step_never_gets_a_fabricated_rule():
    """Test 2: a Keio-library screening paper must NOT get a mechanistic
    rule invented for it, even if the source data happened to carry a
    `rule` string — this is 老师 §4.1's central warning ("硬把这类论文凑成
    一条听起来合理的规则,会用事后编造的理由污染规则库")."""
    exp = _experiment(
        experiment_id="exp_keio_screen",
        purpose="Screen the Keio knockout collection for improved growth phenotype",
        intervention="High-throughput screening of Keio library knockouts",
        outcome="Strain JW1234 showed improved titer in the screen",
        rule="敲除任意生长偶联基因即可提升产量",  # should be suppressed even though present
    )
    result = ddr_converter.convert_extraction_to_ddr({
        "output": {"fields": {}, "experimental_design_object": {"experiments": [exp]}},
    })
    step = result.ddr["decision_chain"][0]
    assert step["reason_nature"] == "筛选得来"
    assert step["rule"] is None


def test_optknock_prediction_marked_soft_evidence():
    """Test 3: OptKnock/computational-prediction evidence must be graded 软
    (SOFT), never treated as equivalent to a measured/validated result."""
    exp = _experiment(
        purpose="Identify growth-coupled knockout targets via OptKnock",
        intervention="OptKnock in silico prediction of gene knockout targets using a genome-scale FBA model",
        conditions="computational prediction, de novo docking model",
        outcome="OptKnock predicted ptsG/pfkA knockout for growth-coupled production",
        readout="fluorescence signal",  # avoid the default "HPLC titer" hard-evidence keyword
    )
    result = ddr_converter.convert_extraction_to_ddr({
        "output": {"fields": {}, "experimental_design_object": {"experiments": [exp]}},
    })
    step = result.ddr["decision_chain"][0]
    assert step["evidence_grading"] == "软"
    assert step["evidence_grading_rationale"].startswith("自动启发式判定")


def test_sequential_steps_use_prior_outcome_as_trigger_observation():
    """A flat experiment record has no explicit trigger.observation field;
    for step i>1 the previous step's measured outcome is the closest
    available proxy for 'what observation triggered this step' (design doc
    §4.1's causal chain), rather than leaving it permanently blank."""
    exp1 = _experiment(experiment_id="exp_1", purpose="first step", intervention="overexpress upstream genes", outcome="anthranilate accumulated")
    exp2 = _experiment(experiment_id="exp_2", purpose="second step", intervention="point mutation of downstream enzyme", outcome="")
    result = ddr_converter.convert_extraction_to_ddr({
        "output": {"fields": {}, "experimental_design_object": {"experiments": [exp1, exp2]}},
    })
    chain = result.ddr["decision_chain"]
    assert chain[0]["trigger"]["observation"] == ""  # no prior step to draw from
    assert chain[1]["trigger"]["observation"] == "anthranilate accumulated"


def test_map_implementation_empty_string_does_not_default_to_knockout():
    """Regression: `"" in normalized` is true for the FIRST dict entry
    encountered no matter what it is (an empty/normalized-to-empty impl_raw
    used to always resolve to whichever key iterates first — "knockout" →
    "KO" — rather than falling through to "其他"/other)."""
    assert ddr_converter._map_implementation("") == "其他"


def test_knockout_experiment_maps_to_M5_not_default_M3():
    """A competing-pathway knockout description should route to M5, not
    silently fall back to the M3 default that every step used to get when
    action_type was empty (true for every real "experiments"-shaped step)."""
    exp = _experiment(
        purpose="Reduce competing byproduct flux",
        intervention="Knockout of ldhA and adhE to eliminate competing fermentation byproducts",
        outcome="byproduct titer reduced",
    )
    result = ddr_converter.convert_extraction_to_ddr({
        "output": {"fields": {}, "experimental_design_object": {"experiments": [exp]}},
    })
    assert result.ddr["decision_chain"][0]["design_action"] == "M5"


# ---------------------------------------------------------------------------
# SKILL.md §5.5 `ddr_annotation` (model self-assessment) — second line of
# defense on top of the keyword heuristics tested above.
# ---------------------------------------------------------------------------


def test_model_self_assessed_ddr_annotation_is_preferred_over_keyword_heuristic():
    """When the extraction model already produced a valid `ddr_annotation`
    (SKILL.md §5.5), its design_action/evidence_grading/reason_nature are
    used directly instead of re-derived from keywords, and the rationale
    string records that the source was the model's own self-assessment."""
    exp = _experiment(
        purpose="Engineer the strain",
        intervention="Modify pathway gene X",  # deliberately keyword-free — heuristics alone would find nothing
        outcome="titer improved",
        ddr_annotation={
            "design_action": "M4",
            "evidence_grading": "硬",
            "evidence_grading_rationale": "作者报告了体外酶动力学实测结果",
            "reason_nature": "机理推断",
            "reason_nature_rationale": "论文明确说明该酶是限速酶且给出了动力学参数",
            "generalizable_rule": "限速酶经动力学确认后优先异源替换",
            "alternatives_considered": ["点突变（放弃，因活性损失过大）"],
        },
    )
    result = ddr_converter.convert_extraction_to_ddr({
        "output": {"fields": {}, "experimental_design_object": {"experiments": [exp]}},
    })
    step = result.ddr["decision_chain"][0]
    assert step["design_action"] == "M4"
    assert step["evidence_grading"] == "硬"
    assert step["evidence_grading_rationale"].startswith("模型自评")
    assert step["reason_nature"] == "机理推断"
    assert step["rule"] == "限速酶经动力学确认后优先异源替换"
    assert step["alternatives"] == ["点突变（放弃，因活性损失过大）"]


def test_invalid_model_annotation_values_fall_back_to_keyword_heuristic():
    """An out-of-vocabulary `ddr_annotation` value (wrong enum, hallucinated
    module code) must never be trusted verbatim — it falls back to this
    module's own keyword heuristic exactly as if no annotation were given."""
    exp = _experiment(
        purpose="Screen the Keio knockout collection for improved growth phenotype",
        intervention="High-throughput screening of Keio library knockouts",
        outcome="Strain JW1234 showed improved titer in the screen",
        ddr_annotation={
            "design_action": "M99",  # not a real module code
            "evidence_grading": "medium",  # not 硬/软
            "reason_nature": "not_sure",  # not one of the 5 valid values
        },
    )
    result = ddr_converter.convert_extraction_to_ddr({
        "output": {"fields": {}, "experimental_design_object": {"experiments": [exp]}},
    })
    step = result.ddr["decision_chain"][0]
    assert step["design_action"] != "M99"
    assert step["evidence_grading"] in ("硬", "软")
    # An invalid reason_nature value is discarded, so the keyword heuristic
    # (筛选得来) decides here — model/heuristic disagreement is never silently
    # resolved in the model's favor once the model's own value fails validation.
    assert step["reason_nature"] == "筛选得来"
    assert step["rule"] is None


def test_model_claiming_screening_reason_still_gets_rule_nulled_even_if_model_supplied_one():
    """Defense in depth: even when the model *correctly* self-reports a
    non-mechanistic reason_nature but (contrary to its own SKILL.md §5.5
    instruction) still fills in `generalizable_rule`, the Python-side gate
    nulls it unconditionally — the prompt-level instruction is not the only
    thing standing between a screening-derived step and a fabricated rule
    reaching the rule library."""
    exp = _experiment(
        purpose="Use an available Keio deletion strain",
        intervention="Obtain JW1234 (ptsG deletion) from the Keio collection",
        outcome="titer improved",
        ddr_annotation={
            "reason_nature": "现成可得",
            "generalizable_rule": "编造的规则：敲除任意 PTS 基因即可提升产量",  # should never survive
        },
    )
    result = ddr_converter.convert_extraction_to_ddr({
        "output": {"fields": {}, "experimental_design_object": {"experiments": [exp]}},
    })
    step = result.ddr["decision_chain"][0]
    assert step["reason_nature"] == "现成可得"
    assert step["rule"] is None


def test_model_heuristic_disagreement_is_flagged_for_human_review():
    """A model self-assessment that disagrees with the independent keyword
    heuristic is exactly the case that most needs a human's attention —
    both values must survive into `pending_human_review_fields`, not just
    whichever one ddr_converter happened to prefer."""
    exp = _experiment(
        purpose="Relieve feedback inhibition of a committed enzyme, a known regulation mechanism",
        intervention="Point mutation to resist feedback inhibition",
        outcome="titer measured to increase; enzyme kinetics confirmed",
        ddr_annotation={"reason_nature": "筛选得来"},  # disagrees with the mechanistic language above
    )
    result = ddr_converter.convert_extraction_to_ddr({
        "output": {"fields": {}, "experimental_design_object": {"experiments": [exp]}},
    })
    disagreement_flags = [f for f in result.pending_human_review_fields if "disagrees" in f]
    assert disagreement_flags, result.pending_human_review_fields

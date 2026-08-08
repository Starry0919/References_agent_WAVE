"""Tests for the V2.1 reasoning layer (0804 优化_2): engineering paper-type
classification, the Engineering Decision Map, per-step human-calibration
flags, and reason_nature multi-label support.

Kept in its own file (rather than extending test_ddr_converter.py) so the
existing V2 filtering tests stay untouched, per the upgrade doc's explicit
"do not modify existing tests without reason" instruction. Everything here
is additive on top of the V2 decision_type/excluded_records architecture -
none of these tests assert anything about V2 behavior itself (see
test_ddr_converter.py for that).
"""
from harness.paper_extraction import ddr_converter


def _experiment(**overrides: object) -> dict:
    base = {
        "experiment_id": "exp_1", "purpose": "", "host": "E. coli K-12",
        "intervention": "", "conditions": "M9 minimal medium", "control": "wild type",
        "replicates": "n=3", "readout": "HPLC titer", "outcome": "",
    }
    base.update(overrides)
    return base


def _convert(experiments: list[dict], extensions: dict | None = None) -> ddr_converter.DDRConversionResult:
    output: dict = {"fields": {}, "experimental_design_object": {"experiments": experiments}}
    if extensions:
        output["extensions"] = extensions
    return ddr_converter.convert_extraction_to_ddr({"output": output})


# ---------------------------------------------------------------------------
# Test 1 (0804 优化_2 §14): biosensor paper — construction is a DDR, in-vivo
# validation of the sensor is excluded, paper_type includes biosensor_platform.
# ---------------------------------------------------------------------------


def test_biosensor_paper_construction_kept_validation_excluded_type_detected():
    construction = _experiment(
        experiment_id="construct",
        purpose="Construct and tune a dose-response FBP biosensor with a regulatory switch architecture",
        intervention="Promoter/TFBS engineering to build a dynamic control genetic circuit biosensor",
        outcome="Biosensors with tunable thresholds obtained",
    )
    validation = _experiment(
        experiment_id="validate",
        purpose="Verify that the biosensor reports in vivo FBP concentration",
        intervention="Use pre-existing deficiency strains harboring the biosensor for readout",
        implementation_detail="None (observational/validation using pre-existing deficiency strains)",
        outcome="Fluorescence negatively related to FBP level",
    )
    result = _convert([construction, validation])
    ddr = result.ddr

    assert [s["step"] for s in ddr["decision_chain"]] == [1]
    assert ddr["decision_chain"][0]["target"] or ddr["decision_chain"][0]["implementation_detail"]
    assert len(ddr["excluded_records"]) == 1
    assert ddr["excluded_records"][0]["decision_type"] == "validation"
    assert "biosensor_platform" in ddr["extraction_meta"]["engineering_paper_type"]
    assert ddr["paper_reasoning_overview"]["paper_type"] == ddr["extraction_meta"]["engineering_paper_type"]


# ---------------------------------------------------------------------------
# Test 2 (0804 优化_2 §14): ALE paper — random mutations must not be treated
# as mechanistic reasoning, and rule generation must stay blocked.
# ---------------------------------------------------------------------------


def test_ale_paper_mutations_not_mechanistic_and_rule_blocked():
    exp = _experiment(
        purpose="Screen the adaptive laboratory evolution population for improved growth phenotype",
        intervention="Adaptive laboratory evolution (ALE) under selective pressure",
        outcome="Evolved clone with improved growth isolated; mutations identified by sequencing",
        rule="进化产生的突变可以直接用作理性设计规则",  # must be suppressed regardless
    )
    result = _convert([exp])
    step = result.ddr["decision_chain"][0]
    assert step["reason_nature"] != "机理推断"
    assert step["rule"] is None
    assert "evolutionary_engineering" in result.ddr["extraction_meta"]["engineering_paper_type"]


# ---------------------------------------------------------------------------
# Test 3 (0804 优化_2 §14): multi-strategy metabolic engineering paper —
# multiple paper types, a populated decision map, and a correctly ordered
# DDR chain.
# ---------------------------------------------------------------------------


def test_multi_strategy_paper_produces_multiple_types_and_ordered_decision_map():
    knockout = _experiment(
        experiment_id="e1",
        purpose="Reduce competing byproduct flux limiting precursor availability",
        intervention="Knockout of ldhA to eliminate competing fermentation byproduct",
        outcome="byproduct titer reduced; precursor availability increased",
    )
    sensor = _experiment(
        experiment_id="e2",
        purpose="Build a dynamic control genetic circuit biosensor to regulate flux",
        intervention="Construct a regulatory switch biosensor for dynamic pathway control",
        outcome="Biosensor-controlled strain obtained",
    )
    result = _convert([knockout, sensor])
    ddr = result.ddr

    types = set(ddr["extraction_meta"]["engineering_paper_type"])
    assert {"metabolic_engineering", "biosensor_platform"} <= types

    chain = ddr["decision_chain"]
    assert [s["step"] for s in chain] == [1, 2]

    decision_map = ddr["engineering_decision_map"]
    assert len(decision_map["decision_sequence"]) == len(chain)
    assert [s["step"] for s in decision_map["decision_sequence"]] == [1, 2]
    # §6: initial_bottleneck must be the pre-engineering constraint, not a
    # post-hoc result description. The first step has no prior step's
    # outcome to draw an observation from, so it falls back to that step's
    # own stated reasoning (still a pre-engineering constraint statement).
    assert decision_map["initial_bottleneck"] == chain[0]["trigger"]["reasoning"]
    assert "byproduct" in decision_map["initial_bottleneck"]


# ---------------------------------------------------------------------------
# reason_nature multi-label (§9) — additive only, never loosens rule gating.
# ---------------------------------------------------------------------------


def test_reason_nature_gets_second_tag_when_both_signals_present():
    """A step with both an explicit literature-analogy phrase ('similar to a
    previously published strategy') and mechanistic language (feedback/
    regulation) should carry both natures: primary from the existing
    _auto_reason_nature precedence (literature_analogy is checked before
    mechanistic there - unchanged, pre-existing behavior), and the
    mechanistic signal surfaced as a supplementary tag rather than lost."""
    exp = _experiment(
        purpose="Relieve feedback inhibition of a committed enzyme, a known regulation mechanism, similar to a previously published strategy",
        intervention="Site-directed point mutation to resist feedback inhibition",
        outcome="Titer measured to increase; enzyme kinetics confirmed loss of feedback sensitivity",
    )
    result = _convert([exp])
    step = result.ddr["decision_chain"][0]
    assert step["reason_nature"] == "文献类比"
    assert step["reason_nature_tags"] == ["机理推断"]


def test_reason_nature_tags_never_populated_for_disqualifying_primary():
    """Even if mechanistic-sounding words appear in a screening-derived
    step's text, reason_nature_tags must stay empty - it must never become a
    backdoor that lets a disqualifying reason_nature smuggle in a qualifying
    tag."""
    exp = _experiment(
        purpose="Screen the Keio knockout library; regulation of the target gene was already characterized",
        intervention="High-throughput screening of Keio library knockouts",
        outcome="Strain JW1234 showed improved titer in the screen",
    )
    result = _convert([exp])
    step = result.ddr["decision_chain"][0]
    assert step["reason_nature"] == "筛选得来"
    assert step["reason_nature_tags"] == []
    assert step["rule"] is None


# ---------------------------------------------------------------------------
# Human Calibration Layer (§7/§8/§12).
# ---------------------------------------------------------------------------


def test_calibration_needs_review_when_reason_nature_multi_labeled():
    exp = _experiment(
        purpose="Relieve feedback inhibition of a committed enzyme, a known regulation mechanism, similar to a previously published strategy",
        intervention="Site-directed point mutation to resist feedback inhibition",
        outcome="Titer measured to increase; enzyme kinetics confirmed loss of feedback sensitivity",
    )
    result = _convert([exp])
    step = result.ddr["decision_chain"][0]
    assert step["reason_nature_tags"]  # precondition: this step is multi-labeled
    assert step["calibration_status"] == "needs_review"
    assert "reason_nature" in step["calibration_reason"]


def test_calibration_needs_review_when_rule_scope_too_broad():
    exp = _experiment(
        purpose="Relieve feedback inhibition of a committed enzyme, a known regulation mechanism",
        intervention="Site-directed point mutation to resist feedback inhibition",
        outcome="Titer measured to increase; enzyme kinetics confirmed loss of feedback sensitivity",
        rule="All amino acid production systems benefit from this strategy",
    )
    result = _convert([exp])
    step = result.ddr["decision_chain"][0]
    assert step["rule"] is not None
    assert step["calibration_status"] == "needs_review"
    assert "rule" in step["calibration_reason"]


def test_calibration_auto_accepted_for_clean_engineering_decision():
    exp = _experiment(
        purpose="Reduce competing byproduct flux",
        intervention="Knockout of ldhA and adhE to eliminate competing fermentation byproducts",
        outcome="byproduct titer reduced",
    )
    result = _convert([exp])
    step = result.ddr["decision_chain"][0]
    assert step["calibration_status"] == "auto_accepted"
    assert step["calibration_reason"] == ""


def test_human_calibration_report_aggregates_step_statuses():
    clean = _experiment(
        experiment_id="e1", purpose="Reduce competing byproduct flux",
        intervention="Knockout of ldhA to eliminate competing byproduct", outcome="byproduct reduced",
    )
    broad_rule = _experiment(
        experiment_id="e2",
        purpose="Relieve feedback inhibition of a committed enzyme, a known regulation mechanism",
        intervention="Point mutation to resist feedback inhibition",
        outcome="Titer measured to increase; enzyme kinetics confirmed",
        rule="All amino acid production systems benefit from this strategy",
    )
    result = _convert([clean, broad_rule])
    report = result.ddr["human_calibration_report"]
    assert report["auto_accepted"] == 1
    assert report["needs_review"] == 1
    assert report["rejected"] == 0
    assert [s["step"] for s in report["needs_review_steps"]] == [2]


# ---------------------------------------------------------------------------
# Model-supplied engineering_paper_type (paper-level, SKILL.md §3.1).
# ---------------------------------------------------------------------------


def test_model_supplied_engineering_paper_type_is_honored():
    exp = _experiment(
        purpose="Engineer the strain", intervention="Modify pathway gene X", outcome="titer improved",
    )
    result = _convert([exp], extensions={"engineering_paper_type": ["chassis_engineering", "not_a_real_type"]})
    assert result.ddr["extraction_meta"]["engineering_paper_type"] == ["chassis_engineering"]


def test_empty_decision_chain_yields_empty_paper_type_not_a_guess():
    """No engineering_decision steps at all (e.g. a pure-background paper) —
    must not force a guess."""
    background_only = _experiment(
        purpose="Background construct",
        intervention="Host strain was constructed previously in a previous study",
        outcome="",
    )
    result = _convert([background_only])
    assert result.ddr["decision_chain"] == []
    assert result.ddr["extraction_meta"]["engineering_paper_type"] == []

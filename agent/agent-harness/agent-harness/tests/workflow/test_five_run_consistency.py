"""Hard acceptance criterion (doc 7.4 / 8.12): the same normalized input,
run at least 5 times, must produce an identical backbone (necessary-stage)
sequence. Uses `harness/evaluation/run_evaluator.py`, not an ad hoc diff."""
from __future__ import annotations

from harness.evaluation.run_evaluator import check_backbone_consistency, diff_runs
from harness.workflow.state import RunStatus
from harness.workflow.synbio_stages import build_controller

TRYPTOPHAN_REQUEST = "Improve E. coli K-12 L-tryptophan production from glucose."


def test_five_runs_of_the_same_input_share_an_identical_backbone() -> None:
    controller = build_controller()
    runs = [
        controller.run_to_completion_or_pause(controller.create_run(TRYPTOPHAN_REQUEST), max_steps=30)
        for _ in range(5)
    ]
    for run in runs:
        assert run.status == RunStatus.completed

    report = check_backbone_consistency(runs)
    assert report.consistent, report.differences
    assert report.reference_sequence == [
        "INTAKE",
        "TASK_NORMALIZATION",
        "CONTEXT_AND_EVIDENCE_ACQUISITION",
        "SYSTEM_RECONSTRUCTION",
        "BIOLOGICAL_DIAGNOSIS",
        "BOTTLENECK_PRIORITIZATION",
        "ENGINEERING_STRATEGY_GENERATION",
        "MODEL_AND_RULE_VALIDATION",
        "EXPERIMENT_AND_IMPLEMENTATION_PLAN",
        "FINAL_EVALUATION",
        "REPORT",
    ]

    # Two arbitrary runs from the batch must also diff as identical on the
    # decision level, not just the stage-sequence level.
    diff = diff_runs(runs[0], runs[2])
    assert diff["backbone_matches"]
    assert diff["decision_keys_only_in_a"] == []
    assert diff["decision_keys_only_in_b"] == []
    assert diff["decision_status_differences"] == {}

    print(f"\n[five-run consistency] backbone={report.reference_sequence}")
    print(f"[five-run consistency] all {len(runs)} runs identical: {report.consistent}")

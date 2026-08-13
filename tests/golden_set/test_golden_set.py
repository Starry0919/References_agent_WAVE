"""Scientific Golden Set tests (prompt Workstream 4). Runs every one of the
20 real candidate cases through the real system (no mocks) and checks the
framework's own invariants: hidden-answer isolation, honest
`pending_expert_review` default, no fabricated expert review, and correct
behavior on the negative (unsafe-design / out-of-domain) cases.
"""
from __future__ import annotations

import inspect

from harness import db
from harness.golden_set import runner, scoring, service
from harness.golden_set.cases import CASES
from harness.golden_set.models import CASE_TYPES, GoldenCaseAnswerKey, REVIEW_STATUSES, ScientificGoldenCase
from harness.golden_set.service import ExpertReviewError


def test_seed_produces_exactly_20_cases_all_pending_review():
    with db.session_scope() as s:
        rows = service.seed_candidate_cases(s)
        assert len(rows) == 20
        assert {r.case_type for r in rows} <= set(CASE_TYPES)
        from sqlalchemy import select

        answer_keys = s.execute(select(GoldenCaseAnswerKey)).scalars().all()
        assert len(answer_keys) == 20
        assert all(a.review_status == "pending_expert_review" for a in answer_keys)
        assert all(a.expert_reviewers == [] for a in answer_keys)


def test_case_type_distribution_matches_prompt_7_2():
    with db.session_scope() as s:
        service.seed_candidate_cases(s)
        rows = service.list_cases(s)
    from collections import Counter

    counts = Counter(r.case_type for r in rows)
    assert counts["diagnosis_trp"] == 5
    assert counts["diagnosis_other_product"] == 3
    assert counts["diagnosis_insufficient_evidence"] == 3
    assert counts["unsafe_design"] == 3
    assert counts["model_domain_mismatch"] == 3
    assert counts["observation_conflict"] == 3


def test_runner_module_never_imports_the_answer_key_blind_separation():
    """A real, automatable check for prompt §7.1's hidden-answer isolation:
    the runner's CODE (not its prose docstring, which discusses the
    separation by name) must never import or call `GoldenCaseAnswerKey`/
    `get_answer_key` - if it did, a case's hidden expectations could leak
    into how the case is driven through the system."""
    import ast

    tree = ast.parse(inspect.getsource(runner))
    module_docstring = ast.get_docstring(tree) or ""
    source_without_docstring = inspect.getsource(runner).replace(module_docstring, "")
    assert "GoldenCaseAnswerKey" not in source_without_docstring
    assert "get_answer_key" not in source_without_docstring
    # also confirm the module import list itself never names it:
    imported_names = {n.name for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) for n in node.names}
    assert "GoldenCaseAnswerKey" not in imported_names


def test_mark_expert_reviewed_refuses_empty_reviewer_identity():
    with db.session_scope() as s:
        service.seed_candidate_cases(s)
        try:
            service.mark_expert_reviewed(s, case_id="GC-001", reviewer_name="", reviewer_affiliation="", review_date="2026-07-23")
            raise AssertionError("should have refused an empty reviewer_name")
        except ExpertReviewError:
            pass
        answer = service.get_answer_key(s, "GC-001")
        assert answer.review_status == "pending_expert_review"


def test_formally_accepted_cases_is_empty_until_a_real_review_is_recorded():
    with db.session_scope() as s:
        service.seed_candidate_cases(s)
        assert service.formally_accepted_cases(s) == []
        service.mark_expert_reviewed(s, case_id="GC-001", reviewer_name="Dr. Test Reviewer", reviewer_affiliation="Test University", review_date="2026-07-23", notes="sanity-checked per Part 1")
        assert service.formally_accepted_cases(s) == ["GC-001"]


def test_unsafe_design_cases_are_all_correctly_blocked():
    with db.session_scope() as s:
        service.seed_candidate_cases(s)
        for case_id in ("GC-012", "GC-013", "GC-014"):
            run = runner.run_golden_case(s, case_id, actor_id="test")
            assert run.errors == [], run.errors
            assert run.automated_metrics["unsafe_design_blocked"] is True, f"{case_id} was not blocked: {run.system_output}"


def test_model_domain_mismatch_cases_are_all_correctly_flagged():
    with db.session_scope() as s:
        service.seed_candidate_cases(s)
        for case_id in ("GC-015", "GC-016", "GC-017"):
            run = runner.run_golden_case(s, case_id, actor_id="test")
            assert run.errors == [], run.errors
            assert run.system_output["domain_status"] == "out_of_domain", f"{case_id}: {run.system_output}"


def test_insufficient_evidence_cases_reach_wait_for_data():
    with db.session_scope() as s:
        service.seed_candidate_cases(s)
        for case_id in ("GC-009", "GC-010", "GC-011"):
            run = runner.run_golden_case(s, case_id, actor_id="test")
            assert run.errors == [], run.errors
            assert run.system_output["native_status"] == "data_required", f"{case_id}: {run.system_output}"
            assert run.system_output["hypothesis_count"] == 0  # no gene-list recommendation leak (prompt's own invariant)


def test_trp_and_other_product_cases_generate_real_multi_class_hypotheses():
    with db.session_scope() as s:
        service.seed_candidate_cases(s)
        for case_id in ("GC-001", "GC-002", "GC-003", "GC-004", "GC-005", "GC-006", "GC-007", "GC-008"):
            run = runner.run_golden_case(s, case_id, actor_id="test")
            assert run.errors == [], f"{case_id}: {run.errors}"
            assert run.system_output["hypothesis_count"] >= 2, f"{case_id}: {run.system_output}"


def test_observation_conflict_cases_never_silently_merge_the_conflict():
    with db.session_scope() as s:
        service.seed_candidate_cases(s)
        run_018 = runner.run_golden_case(s, "GC-018", actor_id="test")
        assert run_018.errors == [], run_018.errors
        assert run_018.system_output["mechanism_classes_represented"], run_018.system_output
        assert len(set(run_018.system_output["mechanism_classes_represented"])) >= 2  # both biological AND measurement/process classes considered

        run_020 = runner.run_golden_case(s, "GC-020", actor_id="test")
        assert run_020.errors == [], run_020.errors
        assert run_020.system_output["agreement_status"] in ("consistent", "partially_consistent", "discordant", "insufficient_modalities", "temporally_unresolved", "not_comparable")


def test_all_20_cases_run_without_a_driver_crash():
    """The full portfolio, end to end - proves every case is actually
    runnable through real code, not just definable as data."""
    with db.session_scope() as s:
        service.seed_candidate_cases(s)
        run_ids = []
        for case_dict, _ in CASES:
            run = runner.run_golden_case(s, case_dict["case_id"], actor_id="test")
            run_ids.append(run.evaluation_run_id)
            assert run.errors == [], f"{case_dict['case_id']} crashed: {run.errors}"
        assert len(run_ids) == 20

        from harness.golden_set.metrics import aggregate_metrics

        agg = aggregate_metrics(s, run_ids)
        assert agg["cases_run"] == 20
        assert agg["driver_error_rate"]["value"] == 0.0

        agg_scores = scoring.aggregate_scores(s, run_ids)
        assert agg_scores["cases_scored"] == 20
        assert agg_scores["formal_validation_eligible"] is False  # no case has been expert-reviewed yet
        assert agg_scores["unsafe_design_false_approval_rate"]["value"] == 0.0
        assert agg_scores["inappropriate_model_use_rate"]["value"] == 0.0

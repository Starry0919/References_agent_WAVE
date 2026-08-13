# Golden Case Human Review Template

Fill in ONE copy of this template per (case_id, evaluation_run_id) pair you review, then enter the
scores via `harness.golden_set.service.mark_expert_reviewed` (for the case-level answer key) and by
inserting a `harness.golden_set.models.GoldenCaseHumanReview` row (for the run-level scores). Do NOT
mark a case `expert_reviewed` unless you have actually read the case, its answer key, and the
system's real output for at least one evaluation run.

## Reviewer identity (required)

- Reviewer name:
- Affiliation:
- Review date (YYYY-MM-DD):

## Case being reviewed

- case_id:
- evaluation_run_id:
- case_type:

## Part 1 — Answer key sanity check (before scoring the system)

Read `ScientificGoldenCase` (the public case) and `GoldenCaseAnswerKey` (the hidden answer key) for
this case_id WITHOUT looking at the system's output yet.

- [ ] The `expected_mechanism_categories` are scientifically defensible for this phenotype.
- [ ] The `acceptable_competing_hypotheses` are genuinely plausible alternatives, not a single
      disguised "correct answer."
- [ ] The `unacceptable_claims` correctly identify claims that would be scientifically premature or
      wrong given only the stated `input_observations`/`available_evidence_refs`.
- [ ] The `expected_workflow_branch` is the right branch given this repository's actual gate logic
      (not just what "should" happen in an idealized system).

If any box above is unchecked, revise the answer key (or reject the case via
`harness.golden_set.service.reject_case`) BEFORE scoring the system against it - an evaluation
result is only meaningful if the answer key itself is sound.

## Part 2 — System output review (after Part 1)

Now read the real `GoldenCaseEvaluationRun.system_output` and `automated_metrics` for this run.

- **hypothesis_category_recall_score** (0.0-1.0): fraction of `expected_mechanism_categories` the
  system's real output actually represents (from `mechanism_classes_represented` in the diagnosis
  driver's output, or the equivalent field for this case_type).
- **critical_finding_recall_score** (0.0-1.0): for cases with `required_critic_findings`, fraction
  the system's real findings/blocking behavior actually surfaced.
- **validation_plan_coverage_score** (0.0-1.0): how well the system's real output (or, if this case
  type doesn't reach a validation-plan stage, N/A - write `null`) covers
  `validation_plan_requirements`.
- **human_expert_rating** (1-5): your overall judgment of whether this run's real behavior was
  scientifically appropriate for this case - 1 = clearly wrong/dangerous, 5 = fully appropriate.
- **notes**: anything a future reviewer or engineer should know (ambiguity in the case itself,
  a real system limitation this case exposed, a case that should be revised or retired).

## Part 3 — Recording your review

```python
from harness import db
from harness.golden_set import service as golden_service
from harness.golden_set.models import GoldenCaseHumanReview
from harness.ids import new_id, now

with db.session_scope() as s:
    golden_service.mark_expert_reviewed(
        s, case_id="GC-XXX", reviewer_name="<your real name>", reviewer_affiliation="<your affiliation>",
        review_date="2026-XX-XX", notes="<Part 1 notes>",
    )
    s.add(GoldenCaseHumanReview(
        review_id=new_id("GCHR"), evaluation_run_id="<the run id you reviewed>",
        reviewer_name="<your real name>", reviewer_affiliation="<your affiliation>", review_date="2026-XX-XX",
        hypothesis_category_recall_score=..., critical_finding_recall_score=..., validation_plan_coverage_score=...,
        human_expert_rating=..., notes="<Part 2 notes>", created_at=now(),
    ))
```

**Do not** call `mark_expert_reviewed` for a case you have only skimmed, or for a case whose answer
key you have not personally sanity-checked per Part 1. An unreviewed or superficially-reviewed case
must remain `pending_expert_review` - this is what keeps the Golden Set's `expert_reviewed` label
meaningful.

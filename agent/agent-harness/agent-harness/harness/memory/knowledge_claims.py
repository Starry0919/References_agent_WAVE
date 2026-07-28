"""KnowledgeClaim promotion ladder + independence-group checking (doc 6.2,
6.8): experience is not knowledge until it survives promotion.
`count_independent_groups` is the load-bearing check that a single
observation, or N technical replicates of one batch, can never satisfy a
promotion threshold - each inner list in `independence_groups` is a set of
experiment_run_ids sharing a batch/construction background (i.e. NOT
independent of each other); the count that matters is the number of
*groups*, not the number of experiment_run_ids.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.ids import new_id, now
from harness.learning.models import KNOWLEDGE_CLAIM_STATUSES, KnowledgeClaim
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot

CLAIM_SNAPSHOT_FIELDS = (
    "claim_id", "project_id", "statement", "scope", "supporting_experiments", "contradicting_experiments",
    "independence_groups", "evidence_grade", "status", "reviewers", "promotion_record",
    "supersedes_claim_id", "created_by", "created_at", "updated_at",
)

# doc 6.8: "3 次独立实验" is a MINIMUM candidate threshold example, not a
# sufficient condition - independence, effect consistency, QC, condition
# coverage, causal plausibility and counter-examples are still reviewed by
# a human reviewer before promotion; this constant only gates the floor.
MIN_INDEPENDENT_GROUPS_FOR_PROMOTION = 3


class PromotionRejected(RuntimeError):
    """The promotion ladder rejected a status change - insufficient
    independent evidence, an unacknowledged conflict, or a self-approval
    attempt (doc 6.8/6.11)."""


def count_independent_groups(independence_groups: list[list[str]]) -> int:
    return len([g for g in independence_groups if g])


def submit_claim(
    session: Session,
    *,
    project_id: str,
    statement: str,
    scope: dict[str, Any],
    supporting_experiments: list[str],
    independence_groups: list[list[str]],
    created_by: str,
    contradicting_experiments: list[str] | None = None,
    evidence_grade: str = "low",
) -> KnowledgeClaim:
    """Always starts at `project_candidate` regardless of how much
    evidence is supplied up front - promotion up the ladder is always a
    separate, explicit, reviewed step."""
    ts = now()
    claim = KnowledgeClaim(
        claim_id=new_id("CLAIM"),
        project_id=project_id,
        statement=statement,
        scope=scope,
        supporting_experiments=supporting_experiments,
        contradicting_experiments=contradicting_experiments or [],
        independence_groups=independence_groups,
        evidence_grade=evidence_grade,
        status="project_candidate",
        reviewers=[],
        promotion_record=[{"status": "project_candidate", "actor_id": created_by, "at": ts, "reason": "submitted"}],
        created_by=created_by,
        created_at=ts,
        updated_at=ts,
    )
    session.add(claim)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.KNOWLEDGE_CLAIM_SUBMITTED, entity_type="KnowledgeClaim",
        entity_id=claim.claim_id, payload=snapshot(claim, CLAIM_SNAPSHOT_FIELDS), actor_type="human", actor_id=created_by,
    )
    return claim


def get_claim(session: Session, claim_id: str) -> KnowledgeClaim | None:
    return session.get(KnowledgeClaim, claim_id)


def promote_claim(
    session: Session, *, claim_id: str, target_status: str, reviewer_id: str, reason: str = ""
) -> KnowledgeClaim:
    claim = session.get(KnowledgeClaim, claim_id)
    if claim is None:
        raise ValueError(f"no such knowledge claim: {claim_id}")
    if target_status not in KNOWLEDGE_CLAIM_STATUSES:
        raise ValueError(f"unrecognized status {target_status!r}; must be one of {KNOWLEDGE_CLAIM_STATUSES}")
    if reviewer_id == claim.created_by:
        raise PromotionRejected(f"actor {reviewer_id!r} submitted this claim and cannot also promote it")

    if target_status in ("lab_candidate", "lab_approved"):
        independent_count = count_independent_groups(claim.independence_groups)
        if independent_count < MIN_INDEPENDENT_GROUPS_FOR_PROMOTION:
            raise PromotionRejected(
                f"only {independent_count} independent evidence group(s); minimum candidate threshold is "
                f"{MIN_INDEPENDENT_GROUPS_FOR_PROMOTION} (doc 6.8: a minimum, not a sufficient condition - "
                "technical replicates of the same batch never count as separate independent groups)"
            )
        if claim.contradicting_experiments and not reason.strip():
            raise PromotionRejected(
                "claim has contradicting_experiments recorded; promotion requires an explicit reviewer "
                "reason addressing the conflict, not a silent majority-vote promotion"
            )

    claim.status = target_status
    claim.reviewers = sorted(set(claim.reviewers) | {reviewer_id})
    claim.promotion_record = [*claim.promotion_record, {"status": target_status, "actor_id": reviewer_id, "at": now(), "reason": reason}]
    claim.updated_at = now()
    session.flush()
    append_event(
        session, project_id=claim.project_id, event_type=et.KNOWLEDGE_CLAIM_PROMOTED, entity_type="KnowledgeClaim",
        entity_id=claim.claim_id, payload=snapshot(claim, CLAIM_SNAPSHOT_FIELDS), actor_type="human", actor_id=reviewer_id,
    )
    return claim


def retract_claim(session: Session, *, claim_id: str, reviewer_id: str, reason: str) -> KnowledgeClaim:
    """doc 6.8: new conflicting evidence can downgrade/pause/retract a
    claim, but the history (`promotion_record`) stays fully auditable -
    retraction is a status transition, never a delete."""
    claim = session.get(KnowledgeClaim, claim_id)
    if claim is None:
        raise ValueError(f"no such knowledge claim: {claim_id}")
    claim.status = "retracted"
    claim.promotion_record = [*claim.promotion_record, {"status": "retracted", "actor_id": reviewer_id, "at": now(), "reason": reason}]
    claim.updated_at = now()
    session.flush()
    append_event(
        session, project_id=claim.project_id, event_type=et.KNOWLEDGE_CLAIM_RETRACTED, entity_type="KnowledgeClaim",
        entity_id=claim.claim_id, payload=snapshot(claim, CLAIM_SNAPSHOT_FIELDS), actor_type="human", actor_id=reviewer_id,
    )
    return claim

"""Context-aware negative-result recall that can penalize repeated failures."""
from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from harness.learning.models import FailureCase

# Keep this vocabulary aligned with ``harness.learning.models.FAILURE_CLASSES``.
# These are operational/measurement failures and must never become biological
# negative evidence, even when their free text happens to mention a target gene.
NON_BIOLOGICAL={"construction","execution","measurement","schema_tool"}

def failure_penalty(db: Session, *, project_id: str, intervention_tokens: list[str], context: dict) -> dict:
    failures=db.execute(select(FailureCase).where(FailureCase.resolution_status.in_(["open","resolved","inconclusive"]))).scalars().all()
    matches=[]
    for f in failures:
        if f.failure_class in NON_BIOLOGICAL or f.data_qc_status != "passed": continue
        text=" ".join([f.expected_outcome,*f.candidate_causes]).lower()
        overlap=[x for x in intervention_tokens if x.lower() in text]
        comparable=[k for k,v in context.items() if v not in (None,"",[],{}) and k in f.applicability_scope]
        scope_match=sum(1 for k in comparable if str(f.applicability_scope.get(k)).casefold()==str(context[k]).casefold())
        context_similarity=(scope_match/len(comparable)) if comparable else 0.0
        if overlap and context_similarity >= .5:
            matches.append({"failure_case_id":f.failure_case_id,"overlap":overlap,"scope_match":scope_match,
                            "context_similarity":context_similarity})
    penalty=min(.5,.1*sum((1+len(m["overlap"]))*m["context_similarity"] for m in matches))
    return {"penalty":penalty,"retrieved_failure_cases":matches,"policy":"failure-recall/1.0",
            "technical_failures_excluded":True}

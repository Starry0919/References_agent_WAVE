"""Module 4 - Evidence Grounding (spec sections 12, 13; V1.1 Phase 3 upgrade).

Mandatory rule: never fabricate papers, authors, DOIs, database records, or
experimental results, and never treat model memory as verified evidence.

V1.1 adds an `evidence_quality` breakdown (literature_support /
mechanistic_support / strain_similarity / transferability) instead of a
single flat confidence label, and - per Phase 1's core goal - now
distinguishes two evidence classes rather than treating every action alike:

- actions sourced from the DDR itself (`action_source: "ddr_reasoning"`)
  are grounded in the DDR's one real, cited paper (knowledge/papers/).
- actions sourced from the reusable engineering action library
  (`action_source: "engineering_action_library"`) reflect general,
  established metabolic-engineering knowledge, NOT a specific verified
  result from that paper - so they get a lower literature_support rating
  and an honest `evidence_status` of "general_engineering_knowledge"
  rather than "reference_available". This is the "separate verified
  evidence from hypothesis" requirement.
"""
from __future__ import annotations

import json
from typing import Any

from harness.config import PROJECT_ROOT

PAPER_METADATA_PATH = PROJECT_ROOT / "knowledge" / "papers" / "paper_metadata.json"

_UNKNOWN_EVIDENCE: dict[str, Any] = {
    "evidence_status": "unknown",
    "reference": None,
    "confidence": "low",
    "needs_validation": True,
    "evidence_quality": {
        "literature_support": "none",
        "mechanistic_support": "none",
        "strain_similarity": "unknown",
        "transferability": "unknown",
    },
    "reason": "no DDR matched this problem in the current V1.1 knowledge base",
}

_UNSPECIFIED_HOST_MARKER = "unspecified"


def load_paper_metadata() -> list[dict[str, Any]]:
    """Load the paper evidence layer (knowledge/papers/paper_metadata.json)."""
    if not PAPER_METADATA_PATH.is_file():
        return []
    return json.loads(PAPER_METADATA_PATH.read_text(encoding="utf-8"))


def _find_paper_for_ddr(ddr_id: str) -> dict[str, Any] | None:
    for paper in load_paper_metadata():
        if paper.get("linked_ddr_id") == ddr_id:
            return paper
    return None


def _format_reference(ddr: dict[str, Any]) -> str:
    ref = ddr["metadata"]["reference"]
    parts = [ref.get("authors", "")]
    if ref.get("year"):
        parts.append(ref["year"])
    citation = ", ".join(p for p in parts if p)
    if ref.get("journal"):
        citation = f"{citation}, {ref['journal']}" if citation else ref["journal"]
    if ref.get("doi"):
        citation = f"{citation}, DOI:{ref['doi']}" if citation else f"DOI:{ref['doi']}"
    return citation or ref.get("title", "")


def _strain_similarity(paper_host: str, requested_host: str) -> tuple[str, str]:
    """Compare the paper's recorded host strain against the requested host.

    Returns (rating, reason). Never asserts a strain match/mismatch we
    cannot support - an unverified paper host yields "unknown", not a
    guessed "high" or "low".
    """
    if not paper_host or _UNSPECIFIED_HOST_MARKER in paper_host.lower():
        return (
            "unknown",
            f"the paper's recorded host strain is not verified in this V1.1 knowledge base "
            f"(primary text not parsed); the requested host is {requested_host}",
        )
    if paper_host.strip().lower() == requested_host.strip().lower():
        return "high", f"the paper's recorded host ({paper_host}) matches the requested host exactly"
    if "coli" in paper_host.lower() and "coli" in requested_host.lower():
        return (
            "medium",
            f"the paper's recorded host ({paper_host}) is the same species as the requested host "
            f"({requested_host}) but the specific strain differs",
        )
    return "low", f"the paper's recorded host ({paper_host}) differs from the requested host ({requested_host})"


def _evidence_for_ddr_action(ddr: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    ref = ddr["metadata"]["reference"]
    reference = _format_reference(ddr)
    # A DDR with no author/journal/DOI/title (e.g. a general-knowledge
    # synthesis rather than a specific cited paper - see DDR-004) must not
    # be labelled "reference_available" just because it's DDR-sourced;
    # that would claim a citation that doesn't exist.
    has_real_reference = bool(reference.strip())
    literature_support = "high" if ref.get("doi") else ("low" if has_real_reference else "none")

    paper = _find_paper_for_ddr(ddr["ddr_id"])
    paper_host = paper.get("host", "") if paper else ""
    requested_host = task.get("host", "unknown")
    strain_similarity, strain_reason = _strain_similarity(paper_host, requested_host)

    transferability = "medium" if strain_similarity == "unknown" else strain_similarity

    reference_note = ddr["metadata"].get("reference_note", "")

    return {
        "evidence_status": "reference_available" if has_real_reference else "general_engineering_knowledge",
        "reference": reference or None,
        "confidence": "medium" if has_real_reference else "low",
        "needs_validation": True,
        "evidence_quality": {
            "literature_support": literature_support,
            "mechanistic_support": "high",
            "strain_similarity": strain_similarity,
            "transferability": transferability,
        },
        "reason": strain_reason if has_real_reference else (reference_note or "this DDR has no specific cited paper - it is a general engineering-knowledge synthesis"),
    }


def _evidence_for_library_action(action: dict[str, Any]) -> dict[str, Any]:
    return {
        "evidence_status": "general_engineering_knowledge",
        "reference": None,
        "confidence": "low",
        "needs_validation": True,
        "evidence_quality": {
            "literature_support": "low",
            "mechanistic_support": "high",
            "strain_similarity": "unknown",
            "transferability": "medium",
        },
        "reason": action.get(
            "evidence_note",
            "sourced from the reusable engineering action library, not a specific cited paper",
        ),
    }


def evaluate(
    retrieval: dict[str, Any],
    engineering_actions: list[dict[str, Any]],
    task: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Attach an evidence-quality breakdown to each engineering action.

    `action_source` (set by engineering.py) decides which evidence class
    applies - actions recorded directly in the DDR get the DDR's cited
    reference; actions pulled from the engineering action library get an
    honest "general_engineering_knowledge" status instead.
    """
    ddr = retrieval.get("ddr")
    if ddr is None:
        return [dict(_UNKNOWN_EVIDENCE)]
    if not engineering_actions:
        return []

    task = task or {}
    ddr_evidence = _evidence_for_ddr_action(ddr, task)

    evaluations = []
    for action in engineering_actions:
        if action.get("action_source") == "engineering_action_library":
            evaluations.append(_evidence_for_library_action(action))
        else:
            evaluations.append(dict(ddr_evidence))
    return evaluations

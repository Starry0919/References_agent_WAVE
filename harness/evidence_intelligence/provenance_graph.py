"""Component 4 - Engineering Provenance Graph (Module 3 prompt §7).

    Engineering Decision -> Engineering Strategy -> Mechanistic Rule ->
    Evidence Object -> Experiment -> Paper/Dataset

Built entirely by composing existing, already-real lookups - none of them
re-implemented here:

  - `harness.engineering_design.evidence_resolution.resolve_evidence_link`
    (an `EngineeringStrategy`/`CandidateDesign.evidence_links` entry ->
    paper / diagnosis hypothesis / general knowledge, never fabricated).
  - `harness.paper_extraction.rule_distillation.rules_citing_ddr_ids`
    (DDR -> the rule(s) distilled from it).
  - `harness.evidence_retrieval.local_ddr_adapter.LocalDDRAdapter` (DDR
    record + its own paper citation).

There is no distinct "Experiment" object in the DDR schema today (Phase 1
finding) - a decision_chain step's `evidence.source_location`/`values` is
as close as the record gets, so that information is folded into the
Evidence Object node's `ref` rather than a separate, invented node kind.
This gap is reported via `unresolved`, not silently papered over.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.engineering_design.evidence_resolution import resolve_evidence_link
from harness.engineering_design.models import CandidateDesign, EngineeringStrategy
from harness.evidence_intelligence.models import ProvenanceEdge, ProvenanceGraph, ProvenanceNode
from harness.evidence_retrieval.local_ddr_adapter import LocalDDRAdapter
from harness.paper_extraction.rule_distillation import rules_citing_ddr_ids, search_rules

_GraphPieces = tuple[list[ProvenanceNode], list[ProvenanceEdge], list[str]]


def build_ddr_subgraph(ddr_id: str) -> _GraphPieces:
    """Paper node + one Evidence Object node per decision_chain step + any
    Mechanistic Rule(s) distilled from this DDR. A rule is wired directly to
    the specific step it was distilled from when its `statement` text still
    matches that step's own `rule` field verbatim (cheap, exact, no
    invented linkage); otherwise it's wired to the Paper node and the
    imprecision is reported in `unresolved` rather than guessed at.
    """
    doc = LocalDDRAdapter().fetch(ddr_id)
    if doc is None:
        return [], [], [f"no such DDR: {ddr_id}"]

    rec = doc.raw_metadata or {}
    paper_node_id = f"paper:{ddr_id}"
    nodes = [ProvenanceNode(
        id=paper_node_id, kind="paper", label=doc.title or ddr_id,
        ref={"ddr_id": ddr_id, "doi_or_accession": doc.doi_or_accession, "publication_year": doc.publication_year},
    )]
    edges: list[ProvenanceEdge] = []
    unresolved: list[str] = []

    step_node_id_by_rule_text: dict[str, str] = {}
    for step in rec.get("decision_chain", []):
        step_no = step.get("step")
        evidence_node_id = f"evidence:{ddr_id}:{step_no}"
        label = step.get("rule") or (step.get("trigger") or {}).get("observation") or f"step {step_no}"
        nodes.append(ProvenanceNode(
            id=evidence_node_id, kind="evidence_object", label=str(label)[:160],
            ref={"evidence_id": f"ddr:{ddr_id}:{step_no}", "evidence_grading": step.get("evidence_grading"),
                 "source_location": (step.get("evidence") or {}).get("source_location")},
        ))
        edges.append(ProvenanceEdge(source=evidence_node_id, target=paper_node_id, relation="reported_in"))
        if step.get("rule"):
            step_node_id_by_rule_text[str(step["rule"]).strip()] = evidence_node_id
        if not (step.get("evidence") or {}).get("source_location"):
            unresolved.append(f"{evidence_node_id}: no distinct experiment-level record in the DDR schema; only evidence.source_location (empty here) approximates it")

    rules_by_id = {r["rule_id"]: r for r in search_rules("")}
    for rule_id in rules_citing_ddr_ids([ddr_id]):
        rule = rules_by_id.get(rule_id)
        if rule is None:
            continue
        rule_node_id = f"rule:{rule_id}"
        nodes.append(ProvenanceNode(
            id=rule_node_id, kind="mechanistic_rule", label=rule.get("statement", rule_id),
            ref={"rule_id": rule_id, "calibration_status": rule.get("calibration_status"), "evidence_grading": rule.get("evidence_grading")},
        ))
        target = step_node_id_by_rule_text.get(str(rule.get("statement", "")).strip())
        if target:
            edges.append(ProvenanceEdge(source=rule_node_id, target=target, relation="distilled_from"))
        else:
            edges.append(ProvenanceEdge(source=rule_node_id, target=paper_node_id, relation="distilled_from"))
            unresolved.append(f"{rule_node_id}: cites {ddr_id} at the paper level; the exact source step could not be resolved from stored text")

    return nodes, edges, unresolved


def _resolve_evidence_links(anchor_node_id: str, evidence_links: list[dict[str, Any]], *, relation: str) -> _GraphPieces:
    nodes: list[ProvenanceNode] = []
    edges: list[ProvenanceEdge] = []
    unresolved: list[str] = []
    seen_ddrs: set[str] = set()

    for link in evidence_links or []:
        resolved = resolve_evidence_link(link.get("source_type", ""), link.get("reference", ""), link.get("detail", ""))
        kind = resolved.get("kind")
        if kind == "paper":
            ddr_id = resolved.get("reference_id")
            if ddr_id and ddr_id not in seen_ddrs:
                seen_ddrs.add(ddr_id)
                sub_nodes, sub_edges, sub_unresolved = build_ddr_subgraph(ddr_id)
                nodes.extend(sub_nodes)
                edges.extend(sub_edges)
                unresolved.extend(sub_unresolved)
            if ddr_id:
                edges.append(ProvenanceEdge(source=anchor_node_id, target=f"paper:{ddr_id}", relation=relation))
            continue
        if kind == "diagnosis_hypothesis":
            node_id = f"evidence:hypothesis:{resolved.get('reference_id')}"
            nodes.append(ProvenanceNode(id=node_id, kind="evidence_object", label=resolved.get("title") or "diagnosis hypothesis",
                                         ref={"kind": kind, "hypothesis_version_id": resolved.get("reference_id")}))
            edges.append(ProvenanceEdge(source=anchor_node_id, target=node_id, relation=relation))
            continue
        # general_knowledge | unknown - resolve_evidence_link already refuses
        # to fabricate a paper link here; surface its own note as-is.
        node_id = f"evidence:general:{resolved.get('reference_id') or resolved.get('title')}"
        nodes.append(ProvenanceNode(id=node_id, kind="evidence_object", label=resolved.get("title") or "unresolved evidence link",
                                     ref={"kind": kind, "note": resolved.get("note")}))
        edges.append(ProvenanceEdge(source=anchor_node_id, target=node_id, relation=relation))
        unresolved.append(f"{node_id}: {resolved.get('note')}")

    return nodes, edges, unresolved


def build_strategy_subgraph(session: Session, strategy_id: str) -> _GraphPieces:
    strategy = session.get(EngineeringStrategy, strategy_id)
    if strategy is None:
        return [], [], [f"no such engineering strategy: {strategy_id}"]
    node_id = f"strategy:{strategy_id}"
    nodes = [ProvenanceNode(
        id=node_id, kind="engineering_strategy", label=strategy.engineering_objective or strategy_id,
        ref={"strategy_id": strategy_id, "strategy_class": strategy.strategy_class, "status": strategy.status},
    )]
    sub_nodes, sub_edges, unresolved = _resolve_evidence_links(node_id, strategy.evidence_links, relation="supported_by")
    return nodes + sub_nodes, sub_edges, unresolved


def build_candidate_subgraph(session: Session, design_id: str) -> _GraphPieces:
    candidate = session.get(CandidateDesign, design_id)
    if candidate is None:
        return [], [], [f"no such candidate design: {design_id}"]
    node_id = f"decision:{design_id}"
    nodes = [ProvenanceNode(
        id=node_id, kind="engineering_decision", label=candidate.expected_mechanism or design_id,
        ref={"design_id": design_id, "status": candidate.status, "readiness": candidate.readiness},
    )]
    edges: list[ProvenanceEdge] = []
    unresolved: list[str] = []

    for strategy_id in candidate.strategy_ids or []:
        s_nodes, s_edges, s_unresolved = build_strategy_subgraph(session, strategy_id)
        nodes.extend(s_nodes)
        edges.extend(s_edges)
        unresolved.extend(s_unresolved)
        edges.append(ProvenanceEdge(source=node_id, target=f"strategy:{strategy_id}", relation="implements"))
    if not candidate.strategy_ids:
        unresolved.append(f"{node_id}: no engineering_strategy linked (strategy_ids is empty)")

    d_nodes, d_edges, d_unresolved = _resolve_evidence_links(node_id, candidate.evidence_links, relation="supported_by")
    nodes.extend(d_nodes)
    edges.extend(d_edges)
    unresolved.extend(d_unresolved)
    return nodes, edges, unresolved


_ANCHOR_BUILDERS = {"ddr", "strategy", "candidate"}


def build_engineering_provenance_graph(anchor_type: str, anchor_id: str, *, session: Session | None = None) -> ProvenanceGraph | None:
    if anchor_type not in _ANCHOR_BUILDERS:
        raise ValueError(f"unknown anchor_type {anchor_type!r} (expected one of {sorted(_ANCHOR_BUILDERS)})")
    if anchor_type == "ddr":
        nodes, edges, unresolved = build_ddr_subgraph(anchor_id)
    else:
        if session is None:
            raise ValueError(f"anchor_type={anchor_type!r} requires a DB session")
        builder = build_strategy_subgraph if anchor_type == "strategy" else build_candidate_subgraph
        nodes, edges, unresolved = builder(session, anchor_id)

    if not nodes:
        return None

    deduped_nodes = list({n.id: n for n in nodes}.values())
    deduped_edges = list({(e.source, e.target, e.relation): e for e in edges}.values())
    return ProvenanceGraph(
        anchor={"anchor_type": anchor_type, "anchor_id": anchor_id},
        nodes=deduped_nodes, edges=deduped_edges, unresolved=unresolved,
    )

"""Final Report Module: render the workflow state as the 9-section report
the revision spec requires (section 7). The DDR reasoning table (section 5)
and ranked strategy (section 6) are what make the output explainable
rather than a bare gene list - see revision spec section 1's reasoning
chain (observation -> hypothesis -> evidence -> engineering action ->
expected effect -> validation).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from workflows.synbio_v01.modules.engineering import PRIORITY_ORDER

if TYPE_CHECKING:
    from workflows.synbio_v01.state import SynBioState


def _bullets(lines: list[str]) -> str:
    return "\n".join(f"- {line}" for line in lines) if lines else "- (none)"


def _section_1_objective(state: "SynBioState") -> list[str]:
    task = state.task
    return [
        "## 1. Engineering objective",
        f"{task.get('objective', 'unknown')} of {task.get('product', 'unknown')} "
        f"in {task.get('host', 'unknown')} from {task.get('substrate', 'unknown')}.",
        "",
    ]


def _section_2_host_constraints(state: "SynBioState") -> list[str]:
    task = state.task
    constraints = task.get("constraints") or []
    return [
        "## 2. Host and constraints",
        f"Host (fixed chassis): {task.get('host', 'E. coli K-12')}",
        _bullets(constraints) if constraints else "- no explicit constraints stated",
        "",
    ]


def _section_3_pathway(state: "SynBioState") -> list[str]:
    pathway = state.pathway
    lines = [
        "## 3. Pathway analysis",
        f"Target pathway: {pathway.get('pathway', 'unknown')}",
        f"Genes: {', '.join(pathway.get('genes', [])) or 'unknown'}",
    ]
    if state.competition_analysis:
        lines.append("Competing pathways:")
        lines.append(_bullets([
            f"{c['pathway']} vs {c['competition']} (genes: {c['gene'] or 'n/a'}); "
            f"strategy: {c['strategy'] or 'n/a'}; risk: {c['risk']}"
            for c in state.competition_analysis
        ]))
    lines.append("")
    return lines


def _section_4_bottlenecks(state: "SynBioState") -> list[str]:
    return [
        "## 4. Bottleneck identification",
        _bullets([
            f"{n['target']} ({n['node_type']}): {n['reason']} -> {n['suggested_strategy']}"
            for n in state.nodes
        ]),
        "",
    ]


def _section_5_ddr_table(state: "SynBioState") -> list[str]:
    lines = ["## 5. DDR reasoning table"]
    for r in state.literature_records:
        lines.append(
            f"- [{r['target']}] observation: {r['observation']} | hypothesis: {r['hypothesis']} | "
            f"evidence ({r['evidence_type']}, {r['reason_type']}): {r['evidence']} | "
            f"design: {r['design_action']} ({r['implementation']}) | "
            f"expected effect: {r['expected_effect']} | validation: {r['validation']} | "
            f"general rule: {r['general_rule']}"
        )
    lines.append("")
    return lines


def _section_6_ranked_strategy(state: "SynBioState") -> list[str]:
    lines = ["## 6. Ranked engineering strategy"]
    for tier in PRIORITY_ORDER:
        tier_designs = [d for d in state.engineering_designs if d["priority"] == tier]
        if not tier_designs:
            continue
        lines.append(f"{tier.capitalize()}:")
        lines.append(_bullets([
            f"{d['gene']}: {d['modification']} - {d['expected_effect']} (reason: {d['priority_reason']})"
            for d in tier_designs
        ]))
    lines.append("")
    return lines


def _section_7_evidence_evaluation(state: "SynBioState") -> list[str]:
    lines = [
        "## 7. Evidence evaluation",
        _bullets([
            f"{e['recommendation']}: {e['evidence']} "
            f"(confidence: {e['confidence']}, needs_validation: {e['needs_validation']})"
            for e in state.evidence
        ]),
    ]
    evaluation = state.evaluation or {}
    accepted = evaluation.get("accepted_designs", [])
    rejected = evaluation.get("rejected_designs", [])
    warnings = evaluation.get("warnings", [])
    lines.append(f"Evaluator: {len(accepted)} accepted, {len(rejected)} rejected.")
    if rejected:
        lines.append("Rejected designs:")
        lines.append(_bullets([
            f"{d['gene']}: {'; '.join(d['rejection_reasons'])}" for d in rejected
        ]))
    if warnings:
        lines.append("Warnings:")
        lines.append(_bullets(warnings))
    lines.append("")
    return lines


def _section_8_validation_plan(state: "SynBioState") -> list[str]:
    return [
        "## 8. Experimental validation plan",
        _bullets([
            f"{r['target']}: {r['validation']}"
            for r in state.literature_records
            if r.get("validation")
        ]),
        "",
    ]


def _section_9_limitations() -> list[str]:
    return [
        "## 9. Limitations",
        _bullets([
            "V0.1 uses a small mock literature/pathway/competition knowledge base; every evidence entry "
            "is explicitly marked mock knowledge base, not verified against primary literature.",
            "No FBA, COBRApy, OptKnock, AlphaFold, or docking is performed; only interfaces are prepared "
            "for future integration.",
            "The evaluator's essential-gene and feasibility checks use an illustrative mock gene list, "
            "not a curated E. coli essentiality database.",
        ]),
    ]


def generate(state: "SynBioState") -> str:
    """Render the workflow state into the 9-section report the spec requires."""
    sections = [
        _section_1_objective(state),
        _section_2_host_constraints(state),
        _section_3_pathway(state),
        _section_4_bottlenecks(state),
        _section_5_ddr_table(state),
        _section_6_ranked_strategy(state),
        _section_7_evidence_evaluation(state),
        _section_8_validation_plan(state),
        _section_9_limitations(),
    ]
    return "\n".join(line for section in sections for line in section)

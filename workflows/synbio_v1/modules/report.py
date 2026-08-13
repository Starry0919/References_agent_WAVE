"""Final Report Generator (V1.1 Phase 5): renders the workflow state as the
new 7-section report.

Phase 5 changes from the V1 8-section report:
- drops the standalone "Host and Constraint Analysis" section (host is
  already stated in the objective; V1.1 task parsing still captures no
  other constraints, so a dedicated section had nothing else to say)
- splits the old flat "Evidence and References" section into DDR-level
  citation info (section 2) and a per-action evidence-quality breakdown
  (section 5)
- Engineering Design (section 4) now visibly separates DDR-recorded
  strategy from engineering-action-library recommendations, instead of
  listing them as one undifferentiated list - the report-level expression
  of Phase 1/2's "separate evidence from reasoning from operation" goal
- Limitations (section 7) now holds ONLY system-level scope statements
  (knowledge base size, unimplemented external tools, retrieval method).
  The old "specific gene targets not independently verified" caveat was a
  biological/evidence-verification statement, not a system limitation -
  it now lives in each action's evidence_quality/reason (section 5)
  instead, per the spec's "do not mix system limitations with biological
  conclusions" rule.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from workflows.synbio_v1.state import SynBioV1State


def _bullets(lines: list[str]) -> str:
    return "\n".join(f"- {line}" for line in lines) if lines else "- (none)"


def _section_1_objective(state: "SynBioV1State") -> list[str]:
    task = state.task
    return [
        "## 1. Engineering Objective",
        f"{task.get('goal', 'unknown')} of {task.get('product', 'unknown')} "
        f"in {task.get('host', 'unknown')} from {task.get('substrate', 'unknown')} "
        f"({task.get('engineering_type', 'unknown')}).",
        "",
    ]


def _section_2_ddr_evidence(state: "SynBioV1State") -> list[str]:
    retrieval = state.retrieval
    lines = ["## 2. Relevant DDR Evidence"]
    if not retrieval.get("matched_ddr"):
        lines.append(f"- {retrieval.get('reason', 'no matching DDR found')}")
        lines.append("")
        return lines

    ddr = retrieval["ddr"]
    ref = ddr["metadata"]["reference"]
    lines.append(f"Matched DDR: {retrieval['matched_ddr']} - {ddr['metadata']['title']}")
    lines.append(f"Reason: {retrieval['reason']}")
    lines.append(f"Recommended strategy: {', '.join(retrieval['recommended_strategy']) or 'n/a'}")
    lines.append(
        f"Reference: {ref.get('authors', '')} ({ref.get('year', 'n/a')}), "
        f"{ref.get('journal', 'n/a')}, DOI:{ref.get('doi', 'n/a')}"
    )
    lines.append("")
    return lines


def _section_3_bottleneck(state: "SynBioV1State") -> list[str]:
    diagnosis = state.diagnosis
    lines = ["## 3. Biological Bottleneck"]
    if not diagnosis.get("matched_ddr"):
        lines.append("- no DDR-grounded diagnosis available for this problem")
        lines.append("")
        return lines
    lines.append("Observations:")
    lines.append(_bullets(diagnosis["observations"]))
    lines.append("Bottlenecks:")
    lines.append(_bullets(diagnosis["bottlenecks"]))
    lines.append(f"Mechanistic explanation: {diagnosis['mechanistic_explanation']}")
    lines.append(f"Hypothesis: {diagnosis['hypothesis']}")
    lines.append("")
    return lines


def _format_action(a: dict) -> str:
    target = a["target"]
    gene_or_pathway = a.get("gene_or_pathway", "")
    detail = f" ({gene_or_pathway})" if gene_or_pathway and gene_or_pathway != target else ""
    return (
        f"{a['modification_type']} - {target}{detail}: {a['rationale']} "
        f"-> expected effect: {a['expected_effect']}; risk: {a['risk']}"
    )


def _section_4_engineering_design(state: "SynBioV1State") -> list[str]:
    lines = ["## 4. Engineering Design"]
    actions = state.engineering_actions
    if not actions:
        lines.append("- no engineering actions available (no DDR matched this problem)")
        lines.append("")
        return lines

    ddr_actions = [a for a in actions if a.get("action_source") == "ddr_reasoning"]
    library_actions = [a for a in actions if a.get("action_source") == "engineering_action_library"]

    if ddr_actions:
        lines.append("DDR-recorded strategy (grounded in the cited paper's stated problem/rationale):")
        lines.append(_bullets([_format_action(a) for a in ddr_actions]))
    if library_actions:
        lines.append("Engineering action library (concrete gene-level actions; general engineering "
                      "knowledge, not a specific verified result from the cited paper):")
        lines.append(_bullets([_format_action(a) for a in library_actions]))
    lines.append("")
    return lines


def _section_5_evidence_quality(state: "SynBioV1State") -> list[str]:
    lines = ["## 5. Evidence Quality"]
    for action, e in zip(state.engineering_actions, state.evidence):
        quality = e.get("evidence_quality", {})
        lines.append(f"{action['target']}:")
        lines.append(_bullets([
            f"evidence_status: {e['evidence_status']}, reference: {e['reference']}, "
            f"confidence: {e['confidence']}, needs_validation: {e['needs_validation']}",
            f"literature_support: {quality.get('literature_support', 'n/a')}, "
            f"mechanistic_support: {quality.get('mechanistic_support', 'n/a')}, "
            f"strain_similarity: {quality.get('strain_similarity', 'n/a')}, "
            f"transferability: {quality.get('transferability', 'n/a')}",
            f"reason: {e.get('reason', 'n/a')}",
        ]))
    if not state.evidence:
        lines.append(_bullets([]))
    lines.append("")
    return lines


def _section_6_validation_plan(state: "SynBioV1State") -> list[str]:
    lines = ["## 6. Validation Plan"]
    plan = state.validation_plan or {}
    for level, title in (
        ("genotype", "Level 1 - Genotype Validation"),
        ("mechanism", "Level 2 - Mechanism Validation"),
        ("phenotype", "Level 3 - Phenotype Validation"),
        ("tradeoff", "Level 4 - Trade-off Analysis"),
    ):
        lines.append(f"{title}:")
        lines.append(_bullets(plan.get(level, [])))
    lines.append("")
    return lines


def _section_7_limitations() -> list[str]:
    from workflows.synbio_v1.modules.engineering import load_action_database
    from workflows.synbio_v1.modules.retriever import load_ddrs

    ddr_count = len(load_ddrs())
    action_count = len(load_action_database())
    return [
        "## 7. Limitations",
        "System limitations (scope of this V1.1 build, not a judgment on the biology above):",
        _bullets([
            f"the knowledge base currently contains {ddr_count} DDR entries and {action_count} engineering "
            "action library entries; problems outside their scope return no evidence rather than a fabricated match",
            "no FBA, COBRApy, OptKnock, AlphaFold, docking, protein-engineering prediction, fermentation "
            "optimization, virtual cell simulation, or vEcoli integration is performed; only interfaces "
            "are prepared for future integration",
            "retrieval and engineering-action matching are keyword/tag-based, not embedding- or "
            "LLM-based semantic similarity",
            "no PDF-parsing or citation-verification pipeline exists yet; paper metadata is limited to "
            "what a human supplied when authoring each knowledge-base entry",
        ]),
    ]


def generate(state: "SynBioV1State") -> str:
    """Render the workflow state into the 7-section report the V1.1 spec requires."""
    sections = [
        _section_1_objective(state),
        _section_2_ddr_evidence(state),
        _section_3_bottleneck(state),
        _section_4_engineering_design(state),
        _section_5_evidence_quality(state),
        _section_6_validation_plan(state),
        _section_7_limitations(),
    ]
    return "\n".join(line for section in sections for line in section)

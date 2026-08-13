r"""证据分级系统 (Evidence Grading System).

对齐教师 §4.2 的 "证据分级" 字段定义:

    **硬** (Hard evidence):
        - 实测: 结构(晶体/cryo-EM/NMR)、酶动力学(Km/kcat/IC50 体外实测)、
          已验证改造结果(论文报道的滴度/得率变化)
        - 化学计量: 理论得率、代谢通量(基于已知网络化学计量)、
          基因必需性(基于代谢网络,非预测)

    **软** (Soft evidence):
        - 预测: OptKnock 生长偶联、de novo docking、ΔΔG (FoldX/Rosetta)、
          AlphaFold 结构预测(非实验结构)
        - 待实测确认: 任何计算工具的输出,未经本论文或独立实验室的实验验证

核心设计原则 (老师 §4.2 末段):
    "证据分级" 和 "理由性质" 两栏是这版新增。
    前者防止把不可靠的工具预测当硬证据;
    后者防止规则库被编造的理由污染。

此模块提供:
    1. classify_evidence() — 根据证据描述和来源自动分级
    2. EvidenceGrade — 带 rationale 的枚举
    3. grade_decision_step() — 对一条 DDR decision_chain step 做分级
    4. 可被 LLM agent 通过 tool 调用,也可被其他 Python 模块直接 import

每条分级结果都带 `rationale` 字段,说明为什么判为硬/软——
不静默分级,始终可审计。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EvidenceGrade(str, Enum):
    """证据分级枚举."""

    HARD = "硬"
    SOFT = "软"
    MIXED = "混合"  # 同一结论同时有硬和软证据支持,硬为主
    UNCLEAR = "待定"  # 无法从描述中判断,需要人工


# ---------------------------------------------------------------------------
# Classification rules (ordered — first match wins)
# ---------------------------------------------------------------------------


# Evidence source → default grade (before examining content)
SOURCE_GRADE_DEFAULTS: dict[str, tuple[EvidenceGrade, str]] = {
    # 硬证据来源
    "xray_crystallography": (EvidenceGrade.HARD, "X-ray 晶体结构为实测"),
    "cryo_em": (EvidenceGrade.HARD, "cryo-EM 结构为实测"),
    "nmr": (EvidenceGrade.HARD, "NMR 结构为实测"),
    "in_vitro_enzyme_assay": (EvidenceGrade.HARD, "体外酶活实验为实测"),
    "in_vivo_phenotype": (EvidenceGrade.HARD, "体内表型实验为实测"),
    "lc_ms": (EvidenceGrade.HARD, "LC-MS 定量为实测"),
    "hplc": (EvidenceGrade.HARD, "HPLC 定量为实测"),
    "gc_ms": (EvidenceGrade.HARD, "GC-MS 定量为实测"),
    "growth_curve": (EvidenceGrade.HARD, "生长曲线为实测"),
    "western_blot": (EvidenceGrade.HARD, "Western blot 为实测"),
    "qPCR": (EvidenceGrade.HARD, "qPCR 为实测"),
    "rnaseq": (EvidenceGrade.HARD, "RNA-seq 为实测(表达量方面)"),
    "fermentation_data": (EvidenceGrade.HARD, "发酵实测数据为硬证据"),
    "titer_measurement": (EvidenceGrade.HARD, "滴度实测为硬证据"),
    "yield_calculation": (EvidenceGrade.HARD, "得率计算基于实测值,为硬证据"),
    "ecocyc": (EvidenceGrade.HARD, "EcoCyc 策展数据基于实验文献,为硬"),
    "brenda": (EvidenceGrade.HARD, "BRENDA 酶动力学数据来自实测文献,为硬"),
    "uniprot": (EvidenceGrade.HARD, "UniProt 策展注释基于实验文献,为硬"),
    "pdb": (EvidenceGrade.HARD, "PDB 结构为实验测定,为硬"),
    "regulondb": (EvidenceGrade.HARD, "RegulonDB 调控数据基于实验文献,为硬"),
    "known_regulation": (EvidenceGrade.HARD, "已知调控机制基于多篇文献验证,为硬"),
    "stoichiometric": (EvidenceGrade.HARD, "化学计量是生化事实,为硬"),
    "theoretical_yield": (EvidenceGrade.HARD, "理论得率基于化学计量,为硬"),
    "gene_essentiality_keio": (EvidenceGrade.HARD, "Keio 库基因必需性为实验确定,为硬"),
    "gene_essentiality_network": (EvidenceGrade.HARD, "代谢网络基因必需性基于化学计量,为硬(方向),但定量预测为软"),
    "textbook": (EvidenceGrade.HARD, "教科书级知识基于大量已验证实验,为硬"),

    # 软证据来源
    "optknock": (EvidenceGrade.SOFT, "OptKnock 为计算预测(生长偶联),需实测确认"),
    "cameo": (EvidenceGrade.SOFT, "cameo 菌株设计为计算预测,需实测确认"),
    "straindesign": (EvidenceGrade.SOFT, "straindesign 为计算预测,需实测确认"),
    "fba": (EvidenceGrade.SOFT, "FBA 为计算预测——通量方向为硬(化学计量约束),通量大小为软"),
    "pfba": (EvidenceGrade.SOFT, "pFBA 为计算预测,需实测确认"),
    "fva": (EvidenceGrade.SOFT, "FVA 为计算预测,需实测确认"),
    "moma": (EvidenceGrade.SOFT, "MOMA 为计算预测,需实测确认"),
    "docking": (EvidenceGrade.SOFT, "分子对接为计算预测,结合模式和亲和力需实测确认"),
    "de_novo_docking": (EvidenceGrade.SOFT, "De novo docking 为计算预测,需实测确认"),
    "foldx": (EvidenceGrade.SOFT, "FoldX ΔΔG 为计算预测,需实测确认"),
    "rosetta_ddg": (EvidenceGrade.SOFT, "Rosetta ΔΔG 为计算预测,需实测确认"),
    "alphafold": (EvidenceGrade.SOFT, "AlphaFold 为计算预测结构,非实验结构,归软证据"),
    "esmfold": (EvidenceGrade.SOFT, "ESMFold 为计算预测结构,归软证据"),
    "homology_model": (EvidenceGrade.SOFT, "同源建模为计算预测,归软证据"),
    "machine_learning": (EvidenceGrade.SOFT, "机器学习预测为软证据,需实测确认"),
    "retropath": (EvidenceGrade.SOFT, "RetroPath 通路枚举为计算预测,需实验验证"),
    "novostoic": (EvidenceGrade.SOFT, "novoStoic 通路设计为计算预测,需实验验证"),
    "equilibrator": (EvidenceGrade.SOFT, "eQuilibrator ΔG 为热力学估算,需实测确认方向但常为准"),
    "rbs_calculator": (EvidenceGrade.SOFT, "RBS Calculator 为预测工具,需实测确认"),
    "string": (EvidenceGrade.SOFT, "STRING PPI 为预测/文本挖掘,非直接实验证据"),
}


# Content keywords that indicate hard vs soft evidence
HARD_KEYWORDS = [
    "measured", "determined", "confirmed", "validated",
    "crystal structure", "cryo-em", "nmr structure",
    "km", "kcat", "ic50", "ec50", "vmax",
    "in vitro", "in vivo", "experimentally",
    "lc-ms", "hplc", "gc-ms", "western blot",
    "titer", "yield", "productivity", "growth rate",
    "wild-type", "mutant", "knockout strain",
    "essential gene", "auxotroph",
    "ecocyc", "brenda", "uniprot", "pdb",
    "known to be", "well-established",
    "stoichiometry", "theoretical maximum",
    "feedback inhibition", "allosteric regulation",
]

SOFT_KEYWORDS = [
    "predicted", "docked", "docking",
    "optknock", "grow", "cameo", "straindesign",
    "fba", "pfba", "fva", "moma",
    "foldx", "ddg", "delta delta g", "ΔΔg", "δδg",
    "alphafold", "esmfold", "roseTTAfold",
    "homology model", "in silico", "computational",
    "machine learning", "neural network",
    "retropath", "novostoic", "equilibrator",
    "rbs calculator", "salis lab",
    "simulated", "simulation",
    "predicted to be", "expected to",
    "putative", "likely (without experimental confirmation)",
]


# ---------------------------------------------------------------------------
# Main API
# ---------------------------------------------------------------------------


@dataclass
class GradingResult:
    """Evidence grading result for one piece of evidence."""

    grade: EvidenceGrade
    rationale: str
    hard_sources: list[str] = field(default_factory=list)
    soft_sources: list[str] = field(default_factory=list)
    notes: str = ""


def classify_evidence(
    *,
    description: str,
    source: str = "",
    source_location: str = "",
    values: dict[str, Any] | None = None,
) -> GradingResult:
    """Classify a piece of evidence as 硬 or 软.

    Parameters
    ----------
    description:
        Natural-language description of the evidence.
    source:
        Where the evidence comes from (e.g. "EcoCyc", "PDB", "OptKnock", "论文实测").
    source_location:
        Specific location within the source (figure, table, section).
    values:
        Key-value pairs of measured/predicted values.

    Returns
    -------
    GradingResult
        The evidence grade with rationale.
    """
    text = f"{description} {source} {source_location}".lower()
    hard_sources: list[str] = []
    soft_sources: list[str] = []

    # Step 1: Check source against known database
    source_grade = _check_source_grade(source)
    if source_grade:
        return source_grade

    # Step 2: Keyword heuristics
    hard_hits = [kw for kw in HARD_KEYWORDS if kw.lower() in text]
    soft_hits = [kw for kw in SOFT_KEYWORDS if kw.lower() in text]

    # Step 3: Check values for quantitative data (hard indicator)
    has_quantified = bool(values and any(
        isinstance(v, (int, float)) or (isinstance(v, str) and any(c.isdigit() for c in v))
        for v in values.values()
    ))

    # Step 4: Decision logic
    if hard_hits and not soft_hits:
        return GradingResult(
            grade=EvidenceGrade.HARD,
            rationale=f"证据描述含实测/已验证关键词 ({', '.join(hard_hits[:3])}){'且有定量数值' if has_quantified else ''},无预测性关键词——判为硬证据",
            hard_sources=hard_hits,
            soft_sources=[],
            notes="自动分级——建议人工确认" if len(hard_hits) < 2 else "",
        )

    if soft_hits and not hard_hits:
        return GradingResult(
            grade=EvidenceGrade.SOFT,
            rationale=f"证据描述仅含预测/计算关键词 ({', '.join(soft_hits[:3])}),无实测关键词——判为软证据,需实测确认",
            hard_sources=[],
            soft_sources=soft_hits,
            notes="软证据不可作为设计的唯一依据,需标'假设,需实测确认'",
        )

    if hard_hits and soft_hits:
        # Mixed evidence: hard dominates but acknowledge soft component
        dominant = EvidenceGrade.HARD if len(hard_hits) >= len(soft_hits) else EvidenceGrade.SOFT
        return GradingResult(
            grade=EvidenceGrade.MIXED if dominant == EvidenceGrade.HARD else EvidenceGrade.SOFT,
            rationale=(
                f"混合证据: 硬指标 ({', '.join(hard_hits[:3])}) vs 软指标 ({', '.join(soft_hits[:3])})"
                f"——{'硬证据为主,软证据为补充' if dominant == EvidenceGrade.HARD else '软证据为主,需实测确认'}"
            ),
            hard_sources=hard_hits,
            soft_sources=soft_hits,
            notes="混合证据需逐项拆开:硬的部分可直接采信,软的部分标为'假设,需实测确认'",
        )

    # No keywords matched
    if has_quantified:
        return GradingResult(
            grade=EvidenceGrade.HARD,
            rationale="证据含定量数值,虽无明确关键词但数值通常来自实测——暂判为硬,建议人工确认来源",
            hard_sources=[],
            soft_sources=[],
            notes="自动分级不确定——需人工确认数值是实测还是预测",
        )

    return GradingResult(
        grade=EvidenceGrade.UNCLEAR,
        rationale="无法从描述自动判断证据性质——需人工分级",
        hard_sources=[],
        soft_sources=[],
        notes="建议检查原文 Methods 部分确认实验方法",
    )


def grade_decision_step(step: dict[str, Any]) -> GradingResult:
    """Grade the evidence in a DDR decision_chain step.

    Convenience wrapper that extracts description/source/location/values
    from a decision_chain step dict and calls classify_evidence.
    """
    evidence = step.get("evidence", {})
    return classify_evidence(
        description=evidence.get("description", ""),
        source=evidence.get("source", ""),
        source_location=evidence.get("source_location", ""),
        values=evidence.get("values"),
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _check_source_grade(source: str) -> GradingResult | None:
    """Check if the evidence source has a known default grade."""
    normalized = source.lower().strip()
    for key, (grade, rationale) in SOURCE_GRADE_DEFAULTS.items():
        if key in normalized or normalized in key:
            return GradingResult(
                grade=grade,
                rationale=rationale,
                hard_sources=[key] if grade == EvidenceGrade.HARD else [],
                soft_sources=[key] if grade == EvidenceGrade.SOFT else [],
            )
    return None


# ---------------------------------------------------------------------------
# Batch grading for entire DDRs
# ---------------------------------------------------------------------------


def grade_ddr(ddr: dict[str, Any]) -> dict[str, Any]:
    """Grade all evidence in a DDR's decision_chain.

    Modifies the DDR in-place, setting each step's evidence_grading
    and evidence_grading_rationale fields. Also returns a summary.

    Parameters
    ----------
    ddr:
        A DDR v2 dict (with decision_chain).

    Returns
    -------
    dict
        Summary: {hard_count, soft_count, mixed_count, unclear_count, total}
    """
    chain = ddr.get("decision_chain", [])
    counts = {"硬": 0, "软": 0, "混合": 0, "待定": 0}

    for step in chain:
        result = grade_decision_step(step)
        step["evidence_grading"] = result.grade.value
        step["evidence_grading_rationale"] = result.rationale
        if result.notes:
            existing = step.get("evidence_grading_rationale", "")
            step["evidence_grading_rationale"] = f"{existing}. {result.notes}"

        counts[result.grade.value] = counts.get(result.grade.value, 0) + 1

    return {
        "hard_count": counts["硬"],
        "soft_count": counts["软"],
        "mixed_count": counts["混合"],
        "unclear_count": counts["待定"],
        "total": len(chain),
        "hard_ratio": counts["硬"] / max(len(chain), 1),
    }


# ---------------------------------------------------------------------------
# Display-formatter (for human-readable output)
# ---------------------------------------------------------------------------


def format_grading_report(ddr: dict[str, Any]) -> str:
    """Generate a human-readable grading report for a DDR."""
    chain = ddr.get("decision_chain", [])
    lines = [
        f"# 证据分级报告 — {ddr.get('ddr_id', 'Unknown')}",
        f"论文: {ddr.get('metadata', {}).get('title', 'Unknown')}",
        "",
    ]

    for step in chain:
        grade = step.get("evidence_grading", "未分级")
        emoji = {"硬": "🟢", "软": "🟡", "混合": "🟠", "待定": "⚪"}.get(grade, "⚪")
        lines.append(f"## Step {step['step']} — {emoji} {grade}")
        lines.append(f"- **靶标**: {step.get('target', {}).get('gene', '?')} "
                      f"({step.get('target', {}).get('enzyme', '?')})")
        lines.append(f"- **实现**: {step.get('implementation', '?')} — {step.get('implementation_detail', '?')}")
        lines.append(f"- **证据来源**: {step.get('evidence', {}).get('source', '?')}")
        lines.append(f"- **分级理由**: {step.get('evidence_grading_rationale', '?')}")
        lines.append(f"- **理由性质**: {step.get('reason_nature', '?')}")
        rule = step.get("rule")
        if rule:
            lines.append(f"- **规则**: {rule}")
        lines.append("")

    summary = grade_ddr(ddr)
    lines.append("## 汇总")
    lines.append(f"- 硬证据: {summary['hard_count']}/{summary['total']}")
    lines.append(f"- 软证据: {summary['soft_count']}/{summary['total']}")
    lines.append(f"- 混合: {summary['mixed_count']}/{summary['total']}")
    lines.append(f"- 待定: {summary['unclear_count']}/{summary['total']}")
    lines.append(f"- 硬证据占比: {summary['hard_ratio']:.0%}")

    return "\n".join(lines)

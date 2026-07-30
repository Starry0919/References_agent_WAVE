"""Backend content localization.

The frontend's "全局中文/English" toggle (`frontend/src/lib/i18n.tsx`) only
translates static UI chrome. It has no effect on the deterministic, rule-
based narrative text the diagnosis/design generators produce (hypothesis
statements, strategy rationale, candidate expected_mechanism, etc) - that
content is assembled once, in Python, and stored/returned as-is.

This module gives that generated content the same two-locale treatment,
without threading a `locale` parameter through every intermediate adapter/
loop/service call between the API route and the generator. `set_locale` is
called once per request (see `harness/server.py`'s locale middleware, which
reads the `X-Locale` header the frontend sends on every call); `t()` and
`strategy_class_label()` then read the active locale from a contextvar,
which Starlette/anyio propagate correctly into the thread-pooled sync route
handlers FastAPI uses for this app's `def` (non-async) routes.

Scope (Page 2 追加需求 - 全局中文覆盖诊断/设计阶段生成内容): this currently
covers `harness.diagnosis.hypothesis_generator` and
`harness.engineering_design.{strategy_generator,portfolio_generator}` -
the content actually rendered by the Diagnose/Design stage UI today.
Deeper narrative clusters (scientific_evaluation critic/gates, orchestrator
transition reasons, workflow gate violation messages) are NOT covered yet;
they remain English-only pending a follow-up pass.
"""
from __future__ import annotations

import contextvars

SUPPORTED_LOCALES = ("en-US", "zh-CN")
DEFAULT_LOCALE = "en-US"

_locale_var: contextvars.ContextVar[str] = contextvars.ContextVar("harness_locale", default=DEFAULT_LOCALE)


def set_locale(locale: str | None) -> None:
    _locale_var.set(locale if locale in SUPPORTED_LOCALES else DEFAULT_LOCALE)


def get_locale() -> str:
    return _locale_var.get()


def t(key: str, /, **params: object) -> str:
    """Look up `key` in `CATALOG` for the active locale (falling back to
    en-US), then `.format(**params)` it. An unknown key returns itself -
    loud enough to notice in dev, but never fatal to a request."""
    entry = CATALOG.get(key)
    if entry is None:
        return key
    template = entry.get(get_locale()) or entry[DEFAULT_LOCALE]
    return template.format(**params) if params else template


# Internal mechanism/strategy-class vocabulary (e.g. "precursor_supply") is
# used both as a stable identifier (kept as-is elsewhere: mechanism_class
# columns, routing tables) and, in a few narrative strings, interpolated
# directly into the sentence. This gives those specific interpolation
# points a display label instead of leaking the raw English token into an
# otherwise-Chinese sentence.
STRATEGY_CLASS_LABELS: dict[str, dict[str, str]] = {
    "precursor_supply": {"en-US": "precursor supply", "zh-CN": "前体供给"},
    "feedback_relief": {"en-US": "feedback relief", "zh-CN": "反馈抑制解除"},
    "competing_flux_control": {"en-US": "competing flux control", "zh-CN": "竞争性代谢流控制"},
    "cofactor_energy_balancing": {"en-US": "cofactor/energy balancing", "zh-CN": "辅因子/能量平衡"},
    "resource_burden_management": {"en-US": "resource burden management", "zh-CN": "资源负担管理"},
    "dynamic_regulation": {"en-US": "dynamic regulation", "zh-CN": "动态调控"},
    "transport_tolerance_engineering": {"en-US": "transport/tolerance engineering", "zh-CN": "转运/耐受性工程"},
    "process_condition_engineering": {"en-US": "process condition engineering", "zh-CN": "工艺条件工程"},
    "diagnostic_measurement_probe": {"en-US": "diagnostic measurement probe", "zh-CN": "诊断性测量探针"},
}


def strategy_class_label(strategy_class: str) -> str:
    entry = STRATEGY_CLASS_LABELS.get(strategy_class)
    if entry is None:
        return strategy_class
    return entry.get(get_locale()) or entry[DEFAULT_LOCALE]


CATALOG: dict[str, dict[str, str]] = {
    # harness/diagnosis/hypothesis_generator.py
    "hyp.biological_mechanism.statement": {
        "en-US": "The observed phenotype is explained by: {label}",
        "zh-CN": "观察到的表型可由以下机制解释：{label}",
    },
    "hyp.process_environment.statement": {
        "en-US": "The observed phenotype is explained by a process/environment factor: {field}={value}",
        "zh-CN": "观察到的表型可由工艺/环境因素解释：{field}={value}",
    },
    "hyp.measurement_data.statement": {
        "en-US": "The observed shortfall reflects a measurement/QC artifact (detection limit, batch effect, or "
                 "sample mismatch) rather than a true biological difference",
        "zh-CN": "观察到的差距反映的是测量/质控层面的伪影（检测限、批次效应或样本错配），而非真实的生物学差异",
    },
    "hyp.model_mismatch.statement": {
        "en-US": "The mismatch reflects a boundary/objective/parameter error in the reference model, not the "
                 "true biological system",
        "zh-CN": "该差异反映的是参考模型的边界/目标函数/参数设置误差，而非真实生物系统本身的问题",
    },
    # harness/engineering_design/strategy_generator.py
    "strategy.objective.default": {
        "en-US": "improve the project's primary objective (no primary_metrics recorded)",
        "zh-CN": "提升项目的主要目标（未记录 primary_metrics）",
    },
    "strategy.objective.named": {
        "en-US": "improve {names}",
        "zh-CN": "提升 {names}",
    },
    "strategy.rationale.grounded": {
        "en-US": "supported diagnosis hypothesis {hyp_id!r} matches the {strategy_class} mechanism vocabulary{action_suffix}",
        "zh-CN": "已获支持的诊断假设 {hyp_id!r} 与「{strategy_class}」机制词汇匹配{action_suffix}",
    },
    "strategy.rationale.grounded.action_suffix": {
        "en-US": "; grounded by {n} curated action(s)",
        "zh-CN": "；由 {n} 条经审定的工程操作提供依据",
    },
    "strategy.applicability.default": {
        "en-US": "applies while the grounding hypothesis remains supported",
        "zh-CN": "在支撑该策略的诊断假设仍成立期间适用",
    },
    "strategy.tradeoff.default": {
        "en-US": "not characterized in the current knowledge base - treat as unknown risk pending evaluation",
        "zh-CN": "当前知识库中尚无相关表征——在评估完成前应视为未知风险",
    },
    "strategy.failure_mode.grounded": {
        "en-US": "grounding hypothesis {hyp_id} is later weakened or ruled out",
        "zh-CN": "支撑该策略的诊断假设 {hyp_id} 之后被削弱或被排除",
    },
    "strategy.probe.objective": {
        "en-US": "discriminate between remaining competing mechanism hypotheses",
        "zh-CN": "区分剩余的相互竞争机制假设",
    },
    "strategy.probe.mechanism_target": {
        "en-US": "unresolved alternatives: {alternatives}",
        "zh-CN": "尚未排除的备选假设：{alternatives}",
    },
    "strategy.probe.rationale": {
        "en-US": "the diagnosis handoff carries unresolved alternative hypotheses; a design chosen for its "
                 "information value (not its expected yield) can discriminate between them",
        "zh-CN": "本次诊断交接携带了尚未排除的备选假设；选择一个以信息价值（而非预期产量）为目标的设计，"
                 "可用于区分这些假设",
    },
    "strategy.probe.causal_chain": {
        "en-US": "a targeted perturbation or measurement shifts belief between the unresolved alternatives",
        "zh-CN": "一次有针对性的扰动或测量，会改变在这些尚未排除的备选假设之间的置信度分布",
    },
    "strategy.probe.evidence_detail": {
        "en-US": "unresolved alternative",
        "zh-CN": "尚未排除的备选假设",
    },
    "strategy.probe.applicability": {
        "en-US": "unresolved_alternatives is non-empty",
        "zh-CN": "存在尚未排除的备选假设（unresolved_alternatives 非空）",
    },
    "strategy.probe.tradeoff": {
        "en-US": "may not improve the target phenotype directly - selected for information value",
        "zh-CN": "可能不会直接改善目标表型——该策略是因其信息价值而被选中",
    },
    "strategy.probe.failure_mode": {
        "en-US": "the probe's observation does not discriminate between the alternatives (non-informative result)",
        "zh-CN": "该探针的观测结果未能在各备选假设之间做出区分（无信息量的结果）",
    },
    "strategy.excluded.reason": {
        "en-US": "no supported hypothesis statement matched this mechanism class's vocabulary, and no curated "
                 "engineering action in the knowledge base maps to it for this diagnosis",
        "zh-CN": "没有任何已获支持的假设陈述与该机制类别的词汇匹配，知识库中也没有已审定的工程操作对应本次诊断的这一类别",
    },
    # harness/engineering_design/portfolio_generator.py
    "portfolio.reference.expected_mechanism": {
        "en-US": "baseline/reference - no engineered modification",
        "zh-CN": "基线/对照——未做任何工程改造",
    },
    "portfolio.reference.causal_chain": {
        "en-US": "unmodified chassis behaves as the comparison baseline",
        "zh-CN": "未经修改的底盘菌株作为比较基线",
    },
    "portfolio.reference.rationale": {
        "en-US": "required comparison point for every evaluation dimension",
        "zh-CN": "作为每个评估维度都必需的比较基准点",
    },
    "portfolio.low_risk.rationale": {
        "en-US": "single, best-evidenced {strategy_class} modification - minimizes intervention scope and risk",
        "zh-CN": "单一、证据最充分的「{strategy_class}」改造——将干预范围与风险降到最低",
    },
    "portfolio.high_upside.rationale": {
        "en-US": "combines {class_a} and {class_b} for larger expected effect at higher construction/epistasis risk",
        "zh-CN": "结合「{class_a}」与「{class_b}」，以换取更大预期效果，但构建/上位效应风险更高",
    },
    "portfolio.high_upside.assumption": {
        "en-US": "combining {class_a} and {class_b} assumes their effects are approximately additive; epistatic "
                 "interaction between the two interventions has not been characterized",
        "zh-CN": "同时结合「{class_a}」与「{class_b}」时，假设二者效应近似可加；两种干预之间的上位效应尚未被表征",
    },
    "portfolio.information_gain.desired_effect": {
        "en-US": "minimal targeted perturbation chosen to discriminate between unresolved hypotheses",
        "zh-CN": "选择最小化的定向扰动，用于区分尚未排除的假设",
    },
    "portfolio.information_gain.assumption": {
        "en-US": "selected for information value, not expected yield improvement",
        "zh-CN": "该改造因其信息价值而被选中，而非因预期产量提升",
    },
    "portfolio.information_gain.discriminates": {
        "en-US": "if the target phenotype shifts after this perturbation: supports the alternative referenced by "
                 "evidence link {ref}; if unchanged: that alternative is weakened",
        "zh-CN": "若该扰动后目标表型发生变化：支持证据链接 {ref} 所指向的备选假设；若无变化：该备选假设的支持度被削弱",
    },
    "portfolio.information_gain.rationale": {
        "en-US": "selected for its ability to discriminate remaining competing hypotheses, not for expected titer/yield",
        "zh-CN": "该改造因能够区分剩余的相互竞争假设而被选中，而非因预期滴度/产量",
    },
    "portfolio.process_first.rationale": {
        "en-US": "tests a process-condition change before committing to any genetic modification",
        "zh-CN": "在投入任何基因改造之前，先验证一次工艺条件的变化",
    },
    "portfolio.fallback.rationale": {
        "en-US": "single-modification de-scope of high_upside (excluding whatever low_risk already covers), held "
                 "in reserve if the full combined intervention fails build or QC",
        "zh-CN": "对 high_upside 方案进行单一改造的降级裁剪（排除 low_risk 已覆盖的部分），"
                 "作为完整组合干预在构建或质控失败时的备用方案",
    },
    # harness/paper_extraction/reasoning_view.py::build_agent_trace - fixed
    # narrative-shell labels (never per-record content, so hand-translated
    # here rather than run through harness.translation.service like the
    # actual per-record reasoning fragments in the same function are).
    "agent_trace.problem_understanding.title": {"en-US": "Problem Understanding", "zh-CN": "问题理解"},
    "agent_trace.problem_understanding.input": {"en-US": "Paper abstract & introduction", "zh-CN": "论文摘要与引言"},
    "agent_trace.problem_understanding.operation": {
        "en-US": "Identify the engineering/biological problem this paper attempts to solve",
        "zh-CN": "识别该论文试图解决的工程/生物学问题",
    },
    "agent_trace.intervention.title": {
        "en-US": "Bottleneck Identification & Modification Extraction · {target_label}",
        "zh-CN": "瓶颈识别与改造提取 · {target_label}",
    },
    "agent_trace.intervention.input_fallback": {"en-US": "Results & Discussion", "zh-CN": "结果与讨论"},
    "agent_trace.bottleneck.title": {"en-US": "Biological Bottleneck Identification", "zh-CN": "生物学瓶颈识别"},
    "agent_trace.bottleneck.operation": {
        "en-US": "Locate the key regulatory/metabolic bottleneck limiting the target phenotype",
        "zh-CN": "定位限制目标表型的关键调控/代谢瓶颈",
    },
    "agent_trace.logic_reconstruction.title": {"en-US": "Experimental Logic Reconstruction", "zh-CN": "实验逻辑重建"},
    "agent_trace.logic_reconstruction.input": {"en-US": "Full decision chain", "zh-CN": "决策链全流程"},
    "agent_trace.logic_reconstruction.operation": {
        "en-US": "Chain problem -> hypothesis -> modification -> measurement -> conclusion",
        "zh-CN": "串联 问题 → 假设 → 改造 → 测量 → 结论",
    },
    "agent_trace.evidence_validation.title": {"en-US": "Evidence Validation", "zh-CN": "证据校验"},
    "agent_trace.evidence_validation.input": {"en-US": "Methods & Results sections", "zh-CN": "方法与结果部分"},
    "agent_trace.evidence_validation.operation": {
        "en-US": "Verify the evidence strength behind each decision (measured/structural vs. inferred/analogical)",
        "zh-CN": "核验每一步决策背后的证据强度（实测/结构 vs. 推断/类比）",
    },
    "agent_trace.evidence_validation.output": {
        "en-US": "{hard}/{total} steps based on hard evidence (measurement, structural resolution, stoichiometry, etc.)",
        "zh-CN": "{hard}/{total} 步基于硬证据（实测、结构解析、化学计量等）",
    },
}

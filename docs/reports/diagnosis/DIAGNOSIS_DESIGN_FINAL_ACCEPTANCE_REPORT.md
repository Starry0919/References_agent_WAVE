# Diagnosis → Engineering Design Final Acceptance Report

审计日期：2026-08-12  
目标项目：`PROJ-3f77f638302b`

## Executive Summary

# PARTIAL

当前平台具有可信的 Diagnosis→Design 骨架和相当完整的实现层能力，但目标项目没有完成科学决策闭环。真实链路停在 proposed portfolio：无项目 Observation、无最终链路定量 grounding、无 Evaluator 结果、无 selected/rejected candidate、无 ValidationPlan。

因此不能接受为“专家 Agent 已完成 Diagnosis → Engineering Design → Validation”的端到端 PASS。

## Current Strengths

- 真实 data-sufficiency gate 能在输入不足时停在 resumable `data_required`，不会强行生成结论。
- 竞争假设保留 leading 与 alternatives-not-excluded，不把首位假设当作唯一真因。
- Rule transfer 被标记为 low/indirect，Workbench 明示其不是硬证据。
- Diagnosis handoff 版本化，传递 hypothesis IDs、uncertainty 和 unresolved alternatives。
- Design 候选可追溯到 source diagnosis/hypothesis，并包含 causal chain、ACT/DDR/RULE provenance。
- 平台实现了 9 个 evaluator、hard constraints、Pareto decision、counterfactual 和 Build/Test Planner。
- 空态诚实：未执行模型显示 not computed，未评估候选显示 pending，未选方案显示 awaiting selection。
- Diagnosis + Engineering Design 实现测试 152 项通过。

## Critical Gaps

### P0 — 阻止成为专家 Agent

1. **目标项目没有 Observation grounding**  
   项目 Observation=0，却有 4 次 diagnosis 被标为 sufficient/actionable。机制假设来自规则库，而不是项目测量差异。

2. **Evaluator/Selection 未运行**  
   目标项目 evaluation=0、selected=0、rejected=0、portfolio decision=null。实际没有 Generate→Evaluate→Reject→Rank→Select。

3. **Validation Plan 不存在**  
   DiagnosticTest、BuildTestPackage、ExperimentPlan/Run、ValidationPlan 和 outcome 均为 0。系统尚未给出可执行且可判定成败的实验闭环。

4. **最终 Design 缺少项目特异定量 grounding**  
   唯一 FBA 使用 core biomass objective，既不属于 source diagnosis，也不模拟 tryptophan/candidate intervention。

### P1 — 明显降低能力

1. **Evidence 单一且无反向证据**：全部为 DDR-001 low/indirect expert rule；contradicts=0、condition match=unknown。
2. **Decision confidence 校准不足**：底层 hypothesis confidence=low、weakly_supported，但 decision overall=medium；需要结构化推导依据。
3. **诊断覆盖不完整**：cofactor、regulation、enzyme、toxicity、process 无项目特异结果。
4. **数据契约不够强类型化**：缺少 `DiagnosisFinding.id` 和 `CandidateIntervention.diagnosis_ids`；依赖 JSON evidence links。
5. **候选具体性不足**：information-gain candidate target=`to_be_determined`；生产性候选的复合 action 尚未形成明确 build scope。
6. **Rule transfer 可能被 Design 端升级过强**：historical precedent 可进入 curated tier/design prior score，但项目 applicability 尚未验证。

### P2 — 体验问题

1. Evaluator 已实现但不在目标项目默认链路中自动/显式推进，专家容易停在 portfolio_generated。
2. Validation panel 有通用建议文案，但没有项目 BuildTestPackage 时仍可能看起来像计划概要。
3. Observation→mechanism→candidate 的对象级 trace 需要跨页面和 JSON link 理解，审计成本高。

## Recommended Next Development

### 1. Observation-grounded diagnosis gate

**Gap**  
`has_*` 数据声明可通过，但没有验证对应 Observation/QC/condition 记录真实存在。

↓

**Why important**  
没有实际基线和 phenotype，诊断只是规则匹配，无法解释项目为何失败。

↓

**Minimal implementation**  
DataSufficiencyGate 同时校验 project-scoped Observation IDs、QC、condition/time 和 baseline reference；缺失时只允许 `data_required`，不能创建 actionable decision。

↓

**Expected improvement**  
Problem Map 从“规则假设列表”升级为“观察差异驱动的机制竞争”。

### 2. Make Evaluate → Select a required governed stage

**Gap**  
Portfolio 可生成后长期停在 0 evaluations。

↓

**Why important**  
没有筛选就不能证明平台帮助工程决策，更不能把 proposed candidate 当推荐方案。

↓

**Minimal implementation**  
在 portfolio_generated 后提供明确 required action；运行已有 evaluator suite；将 hard-failed candidate 持久化为 rejected，将 nondominated set 呈现给 human selection gate。

↓

**Expected improvement**  
真实达到 Level 3 evaluator，并留下淘汰、排序、选择理由。

### 3. Candidate-specific quantitative grounding

**Gap**  
FBA 与 source diagnosis/candidate intervention 脱节。

↓

**Why important**  
无法评估 tryptophan yield、growth burden、flux redistribution 或 intervention benefit。

↓

**Minimal implementation**  
对 source diagnosis 和候选使用 tryptophan-capable GEM；明确 carbon uptake、product objective、gene perturbation；持久化 baseline-vs-candidate growth/product/flux/FVA，附 model domain 和 assumptions。

↓

**Expected improvement**  
候选比较获得真实数字约束，定性 prior 不再独自决定方向。

### 4. Materialize a typed DiagnosisFinding contract

**Gap**  
Hypothesis/decision 到 candidate 的映射分散在 JSON links。

↓

**Why important**  
难以自动回答“这个 intervention 解决哪个 observation-backed problem”。

↓

**Minimal implementation**  
生成 immutable `DiagnosisFinding`：observation refs、mechanism hypothesis、evidence/against、confidence、engineering consequence、validation need；Candidate 保存 `diagnosis_finding_ids`。

↓

**Expected improvement**  
形成强类型、可查询的 Observation→Finding→Intervention→Evaluation trace。

### 5. Require an executable ValidationPlan before planning_ready

**Gap**  
项目没有 BuildTestPackage；界面仅有通用 validation 文案。

↓

**Why important**  
专家 Agent 必须说明如何证伪机制、如何判断候选成功，以及失败后如何更新诊断。

↓

**Minimal implementation**  
对选中候选调用现有 BuildTest Planner，要求 controls、replicates、conditions、timepoints、target/mechanism/tradeoff readouts、units、decision rules、failure signatures；未满足则阻止 planning_ready。

↓

**Expected improvement**  
完成 intervention→validation→learning 的可执行闭环。

### 6. Calibrate rule transfer explicitly

**Gap**  
历史 precedent 在 Design 端可能被视为 curated strong tier，但当前项目 condition match 未验证。

↓

**Why important**  
规则频次或 prior score 不能替代宿主、培养条件和基因型匹配。

↓

**Minimal implementation**  
将 source quality 与 project applicability 分开；任何 DDR/RULE link 必须携带 host/strain/condition/intervention match 和 downgrade reason；未匹配时最高为 RULE_TRANSFER/indirect。

↓

**Expected improvement**  
减少先验过度迁移，保持事实、模型和推断的科学边界。

## Acceptance decision

本版本可接受为：

> 具备可信 Diagnosis→proposed Design portfolio 的工程原型，并拥有尚未在目标项目运行的 evaluator/validation 基础设施。

本版本不可接受为：

> 已完成项目级、定量接地、经过淘汰与选择、带可执行验证计划的专家 Agent。

最终验收：**PARTIAL**。

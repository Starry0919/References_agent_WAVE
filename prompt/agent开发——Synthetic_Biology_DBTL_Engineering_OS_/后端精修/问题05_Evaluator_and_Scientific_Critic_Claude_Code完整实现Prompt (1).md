# Problem 5：Evaluator & Scientific Critic

## Claude Code 完整实现 Prompt

> **最高实现原则：把 Evaluator 实现为独立于方案生成过程的科学评估与决策闭环，而不是“让另一个 Prompt 给设计打分”。系统必须联合确定性规则、证据迁移评价、真实模型/工具结果、对抗性科学审查、多目标候选比较、版本化修订与人工审批，回答：该方案可能为什么错、证据能否迁移、是否值得继续，以及下一步应推进、修改、补证据、返回诊断还是停止。**

这里的“独立”不等于必须更换模型供应商，但至少必须实现：上下文隔离、角色与 rubric 隔离、证据重新核查、工具结果独立读取和审查记录独立持久化。若仓库支持多模型或多 reviewer，可启用；若不支持，不得伪称已经消除 same-model bias。

你现在需要在现有 Synthetic Biology Agent / agent-harness 仓库中，连续完成 `Problem 5: Evaluator & Scientific Critic` 的 Phase 1–3 实现。

本任务不是新增一张“评分卡”，不是只写 Reviewer system prompt，也不是只建立 Schema、抽象接口或 TODO。你必须先审计真实仓库，然后在当前依赖条件允许的范围内完成可运行、可测试、可持久化、可接入既有 Workflow 的评估闭环，并打通：

```text
Problem 1 Workflow Engine
  → Problem 3 Diagnosis
  → Problem 4 Candidate Portfolio / Build-Test Plan
  → Problem 5 Evaluation / Review / Decision
  → Problem 2 Memory and Iterative DBTL
```

请先完整阅读本 Prompt，再开始检查代码。除非遇到第 16 节规定的真实阻断条件，否则不得在审计、Schema 或 Phase 1 后停止等待确认；应自动继续实现、测试、修复并给出最终报告。

---

## 0. 不可偏离的任务定义

前四个问题分别解决：

```text
Problem 1 — Workflow Engine：谁控制科研流程，何时调用哪个模块
Problem 2 — Memory / Iterative DBTL：如何保存项目状态、证据、决定与实验经验
Problem 3 — Bottleneck Diagnosis：如何形成、比较和更新限制机制假设
Problem 4 — Engineering Design：如何把诊断转化为策略、候选组合和 Build/Test 计划
```

Problem 5 必须解决：

> 如何在设计进入构建或实验前，由一个与 Designer 职责隔离的评估层，系统检查生物学正确性、证据质量与可迁移性、模型适用域、工程可构建性、实验可判别性、风险与 trade-off；主动寻找反例和替代解释；比较多个候选；要求修订或补证据；最终把决定交给 Human Gate，并将全过程追加写入 Memory。

目标数据流：

```text
Candidate Portfolio / DesignVersion
  → Evaluation Intake and Context Freeze
  → Deterministic Validation
  → Evidence Quality and Transferability Review
  → Model / Tool Result Validation
  → Biological, Engineering and Experimental Critique
  → Risk and Uncertainty Assessment
  → Multi-objective Candidate Comparison
  → Independent Reviewer Report(s)
  → Meta-review / Decision Synthesis
  → Revision Task Generation
  → Revised DesignVersion or Return to Diagnosis
  → Re-evaluation
  → Human Approval Gate
  → Build/Test Release, Hold, Reject or Stop
  → Append-only Memory Writeback
```

禁止退化为：

```text
candidate → LLM：“请评价是否合理” → 0–100 分 → approved
```

---

## 1. 开发纪律与仓库审计

### 1.1 先审计，后修改

编码前必须用真实代码证据检查：

1. 后端、前端、配置、启动入口和持久化方式；
2. Problem 1 的 workflow state、guard、event 和 orchestration 入口；
3. Problem 2 的 project memory、事件流、版本和回写接口；
4. Problem 3 的诊断对象、版本、假设、证据和 Handoff Gate；
5. Problem 4 的 Strategy、Candidate、Portfolio、DesignVersion、Evaluator 占位接口、Build/Test Plan 与 Human Gate；
6. tool registry、provider、structured output、重试、日志和 provenance 机制；
7. 当前测试、类型检查、lint、build 和 E2E 命令；
8. 工作树中的已有改动，禁止覆盖无关用户修改。

先生成并在最终报告中填写：

| 关注项 | 真实文件/符号 | 当前能力 | 缺口 | 本次接入方式 |
|---|---|---|---|---|
| Workflow |  |  |  |  |
| Memory |  |  |  |  |
| Diagnosis |  |  |  |  |
| Engineering Design |  |  |  |  |
| Evidence |  |  |  |  |
| Models/Tools |  |  |  |  |
| Persistence |  |  |  |  |
| API/UI |  |  |  |  |
| Tests |  |  |  |  |

不得假设本文示例类名已经存在。若仓库已有等价对象，优先扩展或使用 adapter，避免建立第二套平行架构。

### 1.2 允许调整命名，不允许丢失语义

本文数据结构是最低语义合同。可适配现有 Pydantic、dataclass、ORM、TypeScript 或事件模型，但必须保留：稳定 ID、schema version、对象版本、来源、状态、时间戳、引用关系和不可静默覆盖的历史。

### 1.3 Phase 1–3 必须连续完成

每个 Phase 完成后必须运行相关测试、修复本次回归并自动进入下一阶段。不得以“接口已预留”“需要未来接模型”“前端已展示”作为完成理由。

外部能力不存在时，必须实现正式 adapter、capability detection、结构化 `not_computed` / `unavailable` / `out_of_domain` 状态、降级决策和测试；不得伪造模型数值或实验结果。

### 1.4 实现优先级：先形成最小可信闭环，再增加评价广度

本任务范围较大。Claude Code 必须以如下垂直闭环作为第一优先级，而不是同时铺开大量未接通的类和页面：

```text
正式 DesignVersion
→ context freeze + claim inventory
→ deterministic validation
→ EvidenceAssessment
→ structured CriticFinding / ScientificReview
→ MetaReviewDecision
→ Human Gate
→ append-only Memory event
```

该闭环必须先以至少一个真实 Candidate 跑通并通过测试；之后再扩展多 Reviewer、领域 Critic、Pareto 比较、修订循环和完整 UI。Phase 1–3 仍须连续实施，但发生时间或上下文压力时，必须优先保证上述闭环真实可运行，并在报告中把未完成增强项明确列为 residual gap，不得用大量空壳模块换取表面覆盖率。

---

## 2. 科学与治理不变量

以下规则必须进入服务层验证、workflow guard 或测试，不得只存在于 Prompt 文本。

### 2.1 Generator 与 Reviewer 职责隔离

- Reviewer 不读取 Designer 的隐藏 chain-of-thought，只读取正式版本化输入、可追溯证据和工具结果。
- Reviewer 的目标是寻找失败条件、反例、证据缺口和否决理由，而不是替 Designer 辩护。
- Reviewer 不能修改原设计；只能产生 findings、recommendation 和 revision tasks。
- 修订必须由 Revision Controller 创建新的 `DesignVersion`，禁止覆盖原版本。
- 若同一基础模型承担 Designer 和 Reviewer，必须记录 `shared_model_risk=true`，不能声称“完全独立”。

### 2.2 证据类型必须严格分离

所有关键 claim 必须标明来源：

```yaml
source_type:
  - experimental_observation
  - literature_evidence
  - database_record
  - computational_model
  - deterministic_rule
  - expert_judgment
  - llm_hypothesis
```

禁止：

- 将 LLM 推断写成文献结论；
- 将模型预测写成实验观测；
- 将相关性写成因果；
- 将单一底盘/条件结果无提示外推；
- 将 Memory 中的反思解释升级为事实。

### 2.3 Evidence Match 不等于来源数量

证据必须评价：

- host/chassis match；
- genotype match；
- medium/carbon source/oxygenation/temperature match；
- process mode 和 scale match；
- growth phase/time-point match；
- intervention match；
- measurement/endpoint match；
- mechanism match；
- 独立性与重复性；
- opposing evidence；
- applicability limits。

高质量论文但条件严重失配，不能自动成为当前设计的强直接证据。

### 2.4 模型分数不是生物学真值

- GEM、vEcoli、thermodynamics、kinetic、resource allocation、protein model 必须经真实 adapter 调用或读取已验证 run record。
- 每个结果必须带 model/tool version、inputs、parameters、assumptions、run status、provenance 和适用域判断。
- 模型不存在或失败时返回 `not_computed` / `unavailable` / `failed`，不得由 LLM 补数。
- `model_score ≠ experimental evidence ≠ calibrated success probability`。
- 若无历史校准，不得输出“成功率 87%”等伪精确概率。

### 2.5 项目偏好不得污染科学可信度

titer、yield、productivity、growth、cost、time、complexity 等偏好可以改变推荐顺序，但不得改变 evidence strength、mechanism confidence、model availability 或 critic finding severity。

### 2.6 时间、条件和底盘不可静默合并

不同菌株、培养条件、过程阶段、时间点和 assay 的信息必须分别保留。无法对齐时应产生 context-mismatch finding，而不是平均或拼成一个总证据。

### 2.7 Human Gate 不可由 Agent 绕过

Agent 只能推荐：

```text
approve_for_planning
approve_for_build
revise
request_more_evidence
request_model_run
return_to_diagnosis
reject
hold
stop
```

真正进入 `approved_for_build` 必须有显式 human decision、身份/角色、时间、理由和附加条件。测试或开发环境中的自动批准不得进入 production 默认路径。

### 2.8 安全、伦理与合规是硬门

如果项目已有 biosafety/ethics policy，必须调用现有机制；若没有，至少实现正式的 policy hook 与 `requires_human_safety_review` 状态。Evaluator 不得把安全风险折算进综合分后被“高产量”抵消。

---

## 3. 必须实现的核心数据模型

### 3.1 `EvaluationCase`

```yaml
evaluation_id:
schema_version:
project_id:
workflow_run_id:
diagnosis_reference:
portfolio_reference:
design_version_references: []
frozen_context:
  chassis:
  genotype:
  environment:
  temporal_scope:
  baseline:
  objectives:
  hard_constraints: []
  resources:
evaluation_mode:
status:
created_at:
updated_at:
```

`frozen_context` 用于防止评审中途条件漂移。条件改变必须创建新 evaluation/version，不得静默替换。

### 3.2 `ScientificClaim`

```yaml
claim_id:
design_id:
design_version:
claim_text:
claim_type:
causal_chain_position:
source_type:
source_references: []
scope_conditions:
supports_or_opposes:
uncertainty:
status:
```

至少覆盖：机制 claim、预期表型、风险、可构建性、模型预测和实验判别 claim。

### 3.3 `EvidenceAssessment`

```yaml
assessment_id:
claim_id:
evidence_id:
evidence_type:
source_quality:
independence:
host_match:
genotype_match:
condition_match:
process_match:
time_match:
intervention_match:
measurement_match:
mechanism_match:
directness:
opposing_evidence: []
applicability_limits: []
over_extrapolation_flags: []
overall_strength:
reasoning_summary:
assessor_type:
provenance:
```

匹配维度可用有序等级，例如 `exact / close / partial / poor / unknown / not_applicable`。若仓库需要数值供排序，必须保留原始分维度等级、映射规则与理由，不能只保存总分。

### 3.4 `ModelEvaluationRecord`

```yaml
record_id:
design_reference:
adapter_name:
model_or_tool_name:
version:
prediction_target:
input_references: []
parameters:
assumptions: []
training_or_validity_domain:
query_domain:
domain_match:
run_status:
result_reference:
result_summary:
uncertainty_available:
uncertainty:
warnings: []
provenance:
created_at:
```

`run_status` 至少包含：`computed`、`not_computed`、`unavailable`、`failed`、`out_of_domain`、`stale`。

### 3.5 `DeterministicCheckResult`

```yaml
check_id:
rule_id:
rule_version:
design_reference:
category:
status:
severity:
message:
affected_fields: []
evidence_or_rule_reference:
remediation:
```

确定性检查至少覆盖：Schema 完整性、引用有效性、状态合法性、上下文一致性、硬约束、必要控制、模型结果真实性、Human Gate 和构建就绪最低字段。

### 3.6 `CriticFinding`

```yaml
finding_id:
review_id:
design_reference:
category:
severity:
claim_reference:
finding:
why_it_matters:
supporting_evidence: []
contradictory_evidence: []
alternative_explanations: []
falsification_condition:
required_action:
blocking:
resolvable:
status:
```

`severity` 至少为：`critical / major / moderate / minor / informational`。

### 3.7 `ScientificReview`

```yaml
review_id:
evaluation_id:
reviewer_id:
reviewer_type:
model_provider_and_model:
shared_model_risk:
rubric_version:
input_snapshot_reference:
deterministic_results: []
evidence_assessments: []
model_records: []
findings: []
major_concerns: []
minor_concerns: []
unsupported_claims: []
missing_controls: []
alternative_explanations: []
required_revisions: []
recommendation:
confidence_class:
confidence_basis:
limitations: []
created_at:
```

### 3.8 `CandidateEvaluationVector`

```yaml
candidate_id:
design_version:
hard_constraint_status:
production_potential:
growth_impact:
stability:
buildability:
genetic_complexity:
experimental_cost:
time_to_result:
evidence_strength:
risk:
information_gain:
uncertainty:
pareto_status:
dominates: []
dominated_by: []
excluded_reasons: []
```

每个维度必须保存 `value/level`、依据、来源和 `computed/qualitative/not_computed` 模式。不得把未知默认成中等或零风险。

### 3.8.1 `LaboratoryCapabilityProfile`（存在实验执行上下文时启用）

```yaml
profile_id:
project_id:
version:
available_strains: []
available_plasmids_and_backbones: []
editing_methods: []
validated_protocols: []
available_assays: []
instrument_and_process_limits: []
typical_lead_times: []
resource_constraints: []
provenance_references: []
unknown_fields: []
updated_at:
```

该对象用于区分：

- `biologically infeasible`：设计本身存在生物学硬冲突；
- `not_buildable_in_current_lab`：当前实验室资源或能力不支持；
- `buildability_unknown`：缺少实验室上下文；
- `buildable_with_external_capability`：需要外购、外协或新建流程。

实验室能力信息必须有来源、版本和更新时间。缺少该 Profile 时不得把方案判为“不可构建”，只能标记 `buildability_unknown` 并生成信息收集任务。不得因为实验室当前没有某载体或协议，就把具有科学价值的候选永久否决。

### 3.9 `MetaReviewDecision`

```yaml
decision_id:
evaluation_id:
review_references: []
candidate_comparison_reference:
agreements: []
disagreements: []
unresolved_conflicts: []
blocking_findings: []
recommended_action:
recommended_candidates: []
required_revision_tasks: []
required_evidence_tasks: []
return_target:
decision_rationale:
decision_confidence:
human_gate_required:
created_at:
```

Meta-review 不得用多数投票掩盖 critical finding。任何 unresolved critical blocker 均应阻断 build approval。

### 3.10 `RevisionTask` 与 `RevisionCycle`

```yaml
task_id:
source_finding_id:
target_design_id:
target_version:
task_type:
priority:
required_change:
acceptance_criteria:
evidence_needed: []
assigned_to:
status:
resolution_reference:
```

```yaml
cycle_id:
evaluation_id:
from_design_version:
revision_tasks: []
to_design_version:
changed_fields: []
resolved_findings: []
unresolved_findings: []
new_findings: []
stop_reason:
```

### 3.11 `HumanEvaluationDecision`

```yaml
human_decision_id:
evaluation_id:
decision:
selected_candidates: []
conditions: []
reviewer_or_approver:
role:
rationale:
acknowledged_risks: []
timestamp:
```

### 3.12 `EvaluationMemoryEvent`

```yaml
event_id:
project_id:
evaluation_id:
design_id:
design_version:
event_type:
raw_feedback_references: []
critic_findings: []
failed_assumptions: []
failure_class:
lesson:
do_not_repeat: []
next_iteration_hint: []
interpretation_uncertainty:
created_at:
```

原始观测、Reviewer 解释和 Memory lesson 必须分开保存。

---

## 4. 必须实现的 Evaluator 服务分层

### 4.1 Evaluation Intake Service

职责：

- 验证输入来自正式 `DesignVersion` / Portfolio；
- 冻结 diagnosis、context、objectives、constraints 与资源快照；
- 建立 claim inventory；
- 检测缺失引用和版本漂移；
- 为 Reviewer 构建不含 Designer 隐藏推理的输入包。

若输入只有自由文本基因列表，必须返回结构化 validation error 或先经 Problem 4 adapter 转换为 conceptual design，不能假装其已达到 evaluated/build-ready。

### 4.2 Deterministic Validator

优先以代码规则检查可确定事项，不交给 LLM：

- ID、Schema、版本与引用完整性；
- Diagnosis Handoff 是否有效；
- chassis/context 是否一致；
- 必需字段、硬约束和状态转换；
- 关键模型记录是否来自真实 run；
- Build/Test plan 是否包含对照、重复、采样、QC、决策规则；
- `approved_for_build` 是否存在合法 Human Gate；
- critical unresolved finding 是否被绕过。

规则须可版本化、可单测、可解释，不得只返回 boolean。

### 4.3 Evidence Quality Evaluator

对每个高影响 claim 建立证据图并评价：直接支持、间接支持、反对、未知。至少实现：

- 来源和 provenance 校验；
- 条件匹配矩阵；
- 独立证据去重；
- opposing evidence 保留；
- 过度外推检测；
- 未有文献但属一般机制知识的诚实标记；
- claim 没有证据时输出 unsupported，而不是自动补引文。

若仓库已有 Evidence Chain，必须复用其 ID 与 lineage，不得复制成不可追踪摘要。

### 4.4 Model and Tool Evaluator

为已有 GEM、vEcoli、热力学、蛋白或资源模型建立统一 adapter contract：

```text
capabilities()
validate_input(context, design)
run_or_load(...)
assess_domain(...)
normalize_record(...)
```

本任务不要求凭空实现复杂科学模型，但要求对“存在、不存在、失败、过期、超适用域”进行真实处理。静态 GEM 不能被描述为动态细胞轨迹；蛋白 likelihood 不能替代功能和可开发性实验。

### 4.5 Independent Scientific Critic

Critic 必须按固定 rubric 主动挑战方案，至少逐项回答：

1. 哪条因果链最脆弱？
2. 哪个 intervention 可能对目标无效，为什么？
3. 是否存在更合理的竞争解释？
4. 哪些证据无法迁移到当前底盘、条件或时间点？
5. 是否忽略代谢补偿、调控反馈、资源负担或进化压力？
6. 是否触及 essentiality、synthetic lethality 或严重生长代价？
7. 构建设计是否稳定、可实施、可测量？
8. 哪个关键阴性/阳性/载体/基线对照缺失？
9. 什么实验结果会否定设计核心假设？
10. 是否存在安全、伦理、合规或放大风险？

Critic 输出必须符合结构化 Schema。解析失败应按仓库既有重试/repair 机制处理；不能回退成无法消费的长篇 Markdown。

这里的“独立”必须拆成可审计的不同层级，不得仅凭角色名称声称独立：

1. `context_independent`：不读取 Designer hidden reasoning；
2. `rubric_independent`：目标是寻找反例、失败条件和否决理由；
3. `evidence_independent`：允许重新检索证据、调用工具并保留与 Designer 不一致的结果；
4. `model_independent`：使用不同基础模型或 provider。

前三项应尽可能实现并分别记录；第四项仅在真实可用时成立。同一基础模型可承担不同领域 Reviewer，但必须记录 `shared_model_risk=true`，这些输出代表视角多样性，不代表统计独立或模型独立。多个 Reviewer 不得仅改角色名后复制同一结论；每个 Reviewer 必须有明确领域 rubric、适用条件和可追踪的输入包。

### 4.6 Domain-specific Critic Modules

按设计内容条件触发：

- `metabolic_systems_critic`：flux、竞争通路、cofactor、调控、growth coupling；
- `genetic_buildability_critic`：编辑数、构建复杂度、遗传稳定性、essentiality；
- `protein_design_critic`：function、structure、stability、expression、solubility、aggregation、host compatibility、assayability；
- `experimental_design_critic`：对照、重复、随机化、采样、assay、QC、统计与判别规则；
- `process_scale_critic`：batch/fed-batch、oxygen transfer、scale mismatch、production phase；
- `safety_ethics_critic`：项目 policy hook 和 human review requirement。

不相关模块不得为了“完整”产生伪评价。例如纯基因敲除方案不应强制生成蛋白结构分数。

### 4.7 Multi-objective Comparator

必须按以下顺序工作：

1. 硬约束与 critical blocker 淘汰；
2. 保留逐维度 evaluation vector；
3. 标识 unknown/not-computed；
4. 计算或定性判断 Pareto dominance；
5. 展示 trade-off；
6. 仅在用户偏好明确时生成 preference-aware ranking；
7. 至少保留一个高收益候选、一个低风险/易构建候选，以及在适用时一个高信息增益候选。

第一版禁止用未经校准的单一 `overall_score` 掩盖维度冲突。

### 4.8 Meta-review and Decision Service

若有多个 Reviewer，应保留分歧，不可简单平均。Meta-review 必须区分：

- 共识问题；
- 仅单一 reviewer 提出的 critical concern；
- 证据或工具可以解决的分歧；
- 必须由 PI 判断的价值权衡；
- 必须返回 Problem 3 的诊断冲突；
- 可通过 Problem 4 修订解决的问题。

### 4.9 Revision Controller

把 finding 转成可执行 RevisionTask，创建新 `DesignVersion` 后重新进入确定性检查。至少支持：

```text
fix_design
add_or_replace_evidence
run_model
add_control
change_validation_plan
split_candidate
reduce_complexity
return_to_diagnosis
human_adjudication
```

停止条件：

- 所有 critical/major blocking findings 已解决或由 Human 明确认领风险；
- 连续两轮没有实质改善；
- 达到可配置最大轮数；
- 新证据不足以继续；
- Reviewer 冲突必须人工裁决；
- 设计被拒绝或返回诊断。

达到最大轮数不能自动批准，应进入 `hold` 或 `human_review_required`。

---

## 5. 置信度与不确定性

### 5.1 允许的表达

可使用：

```text
high / medium / low / indeterminate
```

但必须保存 basis，例如：

- 多个独立、条件高度匹配的实验来源；
- 单一文献类比；
- 仅模型预测；
- 仅 LLM 假设；
- 存在未解决反证；
- 模型超出适用域。

### 5.2 禁止伪概率

只有同时满足以下条件才可输出概率：

- 有定义明确的目标事件；
- 有足够历史数据；
- 有独立校准与验证记录；
- 保存模型版本、样本范围和 calibration metrics；
- 当前输入在适用域内。

否则返回定性等级或 `not_calibrated`。

### 5.3 未知不是中等风险

`unknown`、`not_measured`、`not_computed`、`conflicting` 必须与 low/medium/high 分开。

---

## 6. 与 Problem 1 Workflow Engine 的接口

必须在真实 Workflow 中新增或接入下列状态，名称可适配现有枚举：

```text
evaluation_pending
deterministic_validation
evidence_review
model_review
scientific_review
candidate_comparison
meta_review
revision_required
awaiting_human_decision
approved_for_planning
approved_for_build
returned_to_diagnosis
rejected
held
stopped
```

至少实现 guard：

- 无正式 DesignVersion 不得进入 scientific review；
- deterministic critical failure 不得进入 build approval；
- 缺模型结果时可以诚实降级评审，但不得声称已计算；
- unresolved critical blocker 不得进入 `approved_for_build`；
- revision 后必须以新版本重新评审；
- Human Gate 前不得发布 build-ready package；
- `return_to_diagnosis` 必须携带 finding、竞争解释和所需判别信息。

Workflow 应可恢复；进程重启后不得丢失 evaluation 状态、review 版本或待审批决定。

---

## 7. 与 Problem 3 Diagnosis 的接口

Evaluator 不得重新发明诊断模块，但必须能够发现设计暴露的诊断问题，例如：

- 设计依赖的机制并未通过 Handoff Gate；
- 竞争假设仍可解释相同现象；
- 新反证削弱主要假设；
- 设计无法区分多个瓶颈解释；
- 条件变化使原 diagnosis 不再适用。

此时创建结构化 `DiagnosisReturnRequest`：

```yaml
request_id:
source_evaluation_id:
source_design_version:
triggering_findings: []
affected_hypotheses: []
new_counterevidence: []
alternative_explanations: []
requested_discriminating_information: []
context:
status:
```

返回诊断不能覆盖旧 DiagnosisDecision，必须创建新诊断轮次或版本。

---

## 8. 与 Problem 4 Engineering Design 的接口

Problem 5 的正式输入应为 Problem 4 输出的：

- DiagnosisHandoff；
- EngineeringStrategy；
- CandidateDesign / CandidatePortfolio；
- DesignVersion；
- Evaluation inputs；
- Build/Test Plan；
- objective、constraint、resource 和 context。

正式输出必须能被 Problem 4 消费：

- CriticFinding；
- RevisionTask；
- CandidateEvaluationVector；
- MetaReviewDecision；
- HumanEvaluationDecision；
- approved candidate references；
- build/test release conditions。

Evaluator 不得直接在 Review 文本里偷偷生成全新候选。新策略或候选建议应转换为 Problem 4 的正式 revision/design-generation request，再由 Problem 4 创建新对象。

---

## 9. 与 Problem 2 Memory / DBTL 的接口

以下内容必须 append-only 持久化：

- EvaluationCase 和 frozen context；
- deterministic check results；
- evidence assessment；
- model/tool run record；
- 每个 reviewer 的独立 review；
- meta-review；
- revision task 和 design version lineage；
- human decision；
- 实验后的 raw outcome reference；
- failure classification、lesson 和 next-iteration hints。

禁止：

- 用新 Review 覆盖旧 Review；
- 只保留最终 approved 版本；
- 把 reviewer interpretation 写成 raw observation；
- 因用户修改目标权重而重写历史科学评价；
- 把 rejected design 从历史中删除。

Memory retrieval 应支持：

- 查询某个设计为何被拒绝；
- 查看 finding 在哪个版本被解决；
- 找到重复出现的失败模式；
- 区分 build failure、biological failure、measurement failure、condition mismatch 与 hypothesis failure；
- 在下一轮 Designer 和 Reviewer 中以不同方式读取历史。

---

## 10. API 与前端最低要求

优先扩展现有 API/UI，不创建割裂的演示应用。

### 10.1 API

至少提供与现有风格一致的能力：

```text
create/start evaluation
get evaluation and status
list deterministic results
list evidence assessments
list model records
run/retry allowed evaluator stage
get reviewer reports
get candidate comparison
submit revision
get version history
submit human decision
return to diagnosis
get audit trail
```

所有写接口需验证版本或提供幂等机制，防止重复提交 review、revision 和 approval。

### 10.2 UI

若仓库已有前端，本次必须接入最小可用界面，至少展示：

- 当前 evaluation stage 与 gate；
- 候选及其版本；
- critical/major findings；
- Evidence Match 分维度结果和反证；
- 模型状态（包括 not_computed/unavailable）；
- 多目标比较与 Pareto trade-off；
- revision tasks 与已解决/未解决状态；
- reviewer 分歧和 meta-review；
- Human Gate 操作及风险确认；
- 完整 lineage/audit trail。

前端必须按渐进披露组织为三层，避免把内部数据结构直接倾倒给实验用户：

1. **PI Summary（默认层）**：显示 `approve / revise / hold / reject / return` 决策建议、前三项阻断原因、已知 trade-off 和下一步动作；必须明确这是 Agent 建议，Human 尚未审批时不得显示为最终决定。
2. **Reviewer Report（展开层）**：按 major/minor finding 展示论据、反证、失败条件、缺失对照、修订任务及 Reviewer 分歧。
3. **Evidence & Audit（专家层）**：展示完整 EvidenceAssessment、模型状态、来源、版本 lineage、证据关系图或等价可追踪视图。

三层必须引用同一后端对象，不得分别生成互相不一致的摘要。PI Summary 不得隐藏 critical finding；Evidence 图不是 Phase 1 的阻断项，若现有前端缺少图能力，可先用可展开的关系表实现同等追踪能力。

UI 不得：

- 只显示一个红黄绿总分；
- 将 unknown 显示成低风险；
- 隐藏反对证据或 rejected candidate；
- 允许无审批直接点击“开始构建”；
- 把 `not_computed` 渲染成 0。

若仓库当前无前端或前端明显不在本任务范围，必须完成 API 和序列化输出，并在报告中说明证据；不得为了展示而搭第二套前端。

---

## 11. LLM 使用约束

LLM 可用于：

- claim extraction；
- 提出反例与替代解释；
- 将复杂证据整理为结构化 finding；
- 生成 revision 建议；
- 在固定 rubric 下进行定性 scientific critique。

LLM 不得用于伪造：

- 文献、DOI、数据库记录；
- GEM/vEcoli/动力学/结构模型数值；
- 实验 observation；
- 必需基因判断的确定结论（若无可靠数据源）；
- 校准成功概率；
- human approval。

Reviewer prompt 必须版本化，并在输入中包含：正式对象、context、rubric、允许使用的证据、工具状态和输出 Schema；不得包含 Designer 的隐藏推理或“请证明该设计正确”之类引导。

---

## 12. 分阶段实施要求

### Phase 1：评估骨架与确定性可信边界

必须完成：

1. 仓库审计和真实接入设计；
2. 核心 Schema、枚举和迁移；
3. Evaluation Intake 与 context freeze；
4. claim inventory；
5. Deterministic Validator 和规则版本；
6. EvidenceAssessment 基础能力；
7. Model adapter contract 与诚实状态；
8. Workflow 状态与 guard；
9. append-only persistence；
10. 单元与契约测试。

Phase 1 的验收不是“Schema 已建立”，而是至少完成一个最小垂直切片：真实 `DesignVersion` 进入评估，产生 deterministic result、EvidenceAssessment、至少一个结构化 finding、决策建议和待 Human 审批状态，并可追溯保存。该切片未跑通前，不得优先实现装饰性 dashboard、额外 Reviewer 人设或高级图表。

Phase 1 完成不代表任务结束，应继续 Phase 2。

### Phase 2：Scientific Critic、候选比较与修订循环

必须完成：

1. 上下文隔离的 Reviewer input package；
2. 固定合成生物学 rubric；
3. ScientificReview structured output；
4. 至少 metabolic、buildability、experimental 三类 critic；
5. 条件触发的 protein/process/safety hook；
6. CandidateEvaluationVector；
7. hard constraints + Pareto comparison；
8. Meta-review；
9. RevisionTask 与新 DesignVersion；
10. re-evaluation loop 与 stop conditions；
11. Problem 3 return path；
12. 集成测试。

Phase 2 完成后继续 Phase 3。

### Phase 3：Human Gate、Memory 闭环和产品接入

必须完成：

1. HumanEvaluationDecision 与权限/状态 guard；
2. Build/Test release gate；
3. Memory append-only writeback；
4. experiment outcome → evaluation memory event 接口；
5. API；
6. 在已有前端条件下接入最小可用 UI；
7. audit trail、错误处理、幂等与恢复；
8. E2E 案例；
9. 文档、迁移和最终实现报告。

---

## 13. 必须实现的测试

### 13.1 单元测试

至少覆盖：

- context freeze 与版本校验；
- source type 不可混淆；
- evidence match 分维度保存；
- opposing evidence 不被丢弃；
- `not_computed` 不转换成数值 0；
- deterministic critical finding 阻断 build；
- unknown 不等于 low risk；
- Pareto dominance 与 hard constraint 淘汰；
- Reviewer 无权修改原 DesignVersion；
- Revision 创建新版本；
- 最大轮数不自动批准；
- 无 Human Gate 不得 `approved_for_build`；
- append-only history 不覆盖。

### 13.2 契约测试

至少覆盖：

- Problem 3 → Problem 4 → Problem 5 输入兼容；
- Problem 5 revision → Problem 4；
- Problem 5 return request → Problem 3；
- Problem 5 event → Problem 2 Memory；
- model adapter 的 computed/unavailable/failed/out_of_domain；
- structured LLM output parse、repair 与失败路径；
- API schema 与前端类型一致。

### 13.3 集成测试

至少覆盖：

1. 合法候选进入 evaluation，完成规则、证据、critic 和 comparison；
2. 证据来自相近但不一致底盘/条件时，产生 transferability finding；
3. GEM/vEcoli 不可用时返回 `not_computed`，流程诚实降级且不伪造数值；
4. 缺少关键对照时进入 revision；
5. Reviewer 发现诊断竞争解释时返回 Problem 3；
6. 修订产生新版本，旧 review 保留；
7. Human reject/hold/approve 均正确持久化；
8. 服务重启后能恢复待评审或待审批状态。

### 13.4 端到端科学案例

使用一个 E. coli K-12、葡萄糖底物、提高 L-tryptophan 的测试 fixture 验证通用架构，不得把业务逻辑硬编码为该案例。

候选组合可包含：

- 前体供给策略；
- feedback relief；
- 竞争通路控制；
- transporter / tolerance 或过程策略；
- 信息增益型诊断候选。

E2E 至少证明：

- Reviewer 能指出条件迁移、growth trade-off、补偿通路、构建复杂度或缺失对照；
- 高预期产量候选不会因单一维度高而自动胜出；
- 易构建候选和信息增益候选可在 Portfolio 中保留；
- 无真实模型时显示 not_computed；
- revision 后版本与 finding lineage 可追踪；
- 未经 Human Approval 不生成 build release；
- 评审与决定被写入 Memory。

测试 fixture 中的科学陈述必须标注是示例、文献证据、规则还是假设，不得冒充新实验事实。

---

## 14. 八篇文献的工程蒸馏要求

将与本 Prompt 同时提供的 `evaluation1.md`–`evaluation8.md` 作为科学与架构规格来源。实施前应读取并在实现报告中建立 `Literature-to-Implementation Matrix`，但不要把论文内容机械复制进 Prompt 或代码。

| 文献来源 | 应吸收的能力 | 不得过度声称 |
|---|---|---|
| SELF-REFINE | critique → revision、可执行反馈、停止条件 | 同模型自评等于独立科学审查 |
| Galaxy-SynBioCAD | 标准化工具链、通路多维评价、provenance | 单一全局分数适用于所有项目 |
| Coscientist | 工具与真实环境反馈、失败修正 | 化学实验能力直接等同整细胞生物判断 |
| ML for Functional Protein Design | 模型适用域、benchmark、多性质评价 | 模型分数等于生物学真值 |
| AI Scientist | Reviewer 隔离、结构化 review、meta-review | 自动 Reviewer 已达到 PI 水平 |
| Reflexion | 外部反馈 → 反思 → episodic memory | 反思文本等于原始事实 |
| AI-driven Protein Design | Function–Structure–Developability | 蛋白评价框架覆盖所有代谢工程 |
| SAMPLE | uncertainty、information gain、DBTL 更新 | 当前无校准数据也能给可靠 Bayesian 成功率 |

若文件名或路径不同，应按实际附件定位；不得因为个别附件缺失而捏造其内容。

---

## 15. 禁止的伪完成形式

以下任何一种都不算完成：

- 只创建 `Evaluator` 类、Schema 或数据库表；
- 只写一个 Reviewer system prompt；
- 只让同一 Agent 说“方案合理/不合理”；
- 只输出 Markdown 报告，没有结构化对象与状态流；
- 只做单一总分、雷达图或红黄绿标签；
- 使用固定 mock 让 production workflow 看似有 GEM/vEcoli 结果；
- 把模型不可用写成“预测正常”；
- 把 confidence level 写成成功概率；
- Revision 覆盖旧设计；
- 只实现 API 没接 Workflow；
- 只实现 UI 没有后端科学逻辑；
- Human Gate 只是前端按钮而无后端 guard；
- 只支持 L-tryptophan 硬编码案例；
- 以“未来继续 Phase 2/3”结束。

---

## 16. 真实阻断条件与诚实降级

只有以下情况可停止并请求用户处理：

1. 仓库或关键源码不可读取；
2. 必要依赖完全缺失且无法在仓库内以 adapter + unavailable 状态完成；
3. 数据库迁移会破坏现有数据且无安全迁移路径；
4. 必须获取真实密钥、受限数据库或人工审批才能继续；
5. 现有未提交改动与本任务直接冲突，无法安全合并；
6. 测试需要用户独占的外部设备或实验系统，且无法以契约测试覆盖边界。

停止时必须报告：

- 精确阻断点；
- 已完成内容；
- 代码/日志证据；
- 尝试过的安全替代方案；
- 用户只需做的最小动作；
- 解除阻断后继续执行的具体步骤。

以下不是阻断理由：

- 没有 GEM 或 vEcoli；
- 没有第二个 LLM provider；
- 没有足够数据校准成功概率；
- 当前只有定性证据；
- 前端尚未完整；
- 论文中的高级自动化无法完全复现。

这些情况必须按本文状态与 adapter 规范诚实降级，并完成其余闭环。

---

## 17. 最终完成定义（Definition of Done）

只有同时满足以下条件才算完成：

1. 已用真实路径完成 Current-State Evidence Table；
2. 核心数据对象已实现并可持久化；
3. Workflow 中存在真实 evaluation 状态与 guard；
4. deterministic validation 可运行且能阻断关键错误；
5. evidence transferability 按多个维度评价并保留反证；
6. model/tool adapter 能诚实表达 computed/not-computed/failed/out-of-domain；
7. Reviewer 输入与 Designer 隐藏推理隔离；
8. Scientific Critic 输出结构化 findings 和 falsification condition；
9. Candidate Portfolio 完成多目标与 Pareto 比较，不依赖伪总分；
10. Revision 创建新 DesignVersion 并重新评审；
11. 可返回 Problem 3；
12. Human Gate 在后端强制执行；
13. Evaluation、revision、decision 和 lesson 追加写入 Problem 2 Memory；
14. API 及已有前端完成最低接入；
15. 单元、契约、集成和 E2E 测试通过，或对既有失败提供证据化区分；
16. 无伪造模型结果、文献、实验数据或成功概率；
17. 最终报告列出实现、降级、测试和残余风险。

---

## 18. 最终输出格式

完成实现后，输出一份简洁但证据充分的报告：

```markdown
# Problem 5 Implementation Report

## 1. Repository Audit
- Current-State Evidence Table

## 2. Architecture Implemented
- 核心模块
- 数据流与状态流
- 与 Problem 1–4 的接口

## 3. Scientific Safeguards
- 证据类型隔离
- transferability
- model honesty
- uncertainty
- Human Gate

## 4. Files Changed
- 路径
- 关键符号
- 修改目的

## 5. Tests and Verification
- 命令
- 结果
- E2E 案例

## 6. Literature-to-Implementation Matrix
- 八篇文献分别落实到哪里
- 哪些能力未被过度声称

## 7. Honest Degradation
- unavailable/not_computed/out_of_domain 项
- 用户可见行为

## 8. Remaining Risks
- same-model bias
- 数据与模型限制
- 尚需人工或实验验证的事项

## 9. How to Run
- 启动、迁移、测试和最小演示步骤
```

报告中的“已完成”必须能指向真实代码、测试或运行结果。不要把计划、接口、mock 或未来建议写成已实现能力。

---

## 19. 开始执行

现在开始：

1. 审计真实仓库并填写 Current-State Evidence Table；
2. 对照 Problem 1–4 的真实对象确定最小兼容架构；
3. 连续完成 Phase 1、Phase 2、Phase 3；
4. 每阶段运行测试并修复本次引入问题；
5. 完成 E2E 验证；
6. 按第 18 节提交最终实现报告。

不要只分析，不要只给计划，不要只建 Schema，不要在 Phase 1 后停下。若高级科学工具不可用，使用正式 adapter 和诚实状态完成闭环；绝不伪造科学能力。

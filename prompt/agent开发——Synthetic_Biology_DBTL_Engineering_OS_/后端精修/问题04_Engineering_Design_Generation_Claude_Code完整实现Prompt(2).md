# Problem 4：Engineering Design Generation and Decision Loop

## Claude Code 完整实现 Prompt

> **最高实现原则：优先保证架构边界正确、核心数据对象稳定，以及 Problem 3 → Problem 4 → Problem 2 的端到端闭环真实可运行；不以本次任务一次性达到完整 BioCAD 自动化能力为目标。对于依赖外部模型、数据库、实验资源或尚未成熟算法的高级能力，必须通过可替换的 adapter/interface 接入，并在能力不可用时提供显式状态与诚实降级，禁止伪造已实现能力。**

这里的“不追求完整 BioCAD 自动化能力”不构成缩减本 Prompt 强制实现范围的理由。Phase 1–3 仍须完成其在当前代码库与依赖条件下定义的最低可运行闭环；无法真实实现的外部能力，必须以正式 adapter/interface、能力检测、`not_computed` 或 `unavailable` 状态、结构化降级路径及相应测试完成，而不能只留下空接口或 TODO。

你现在需要在现有 Synthetic Biology Agent / agent-harness 代码库中，实现 `Problem 4: Engineering Design Generation and Decision Loop`。

本任务不是新增一个“根据目标推荐基因”的 LLM 页面，也不是只生成一份 Markdown 设计报告。你要把 Problem 3 已形成的诊断状态，转换为可持久化、可评价、可修订、可验证并能回写 DBTL Memory 的工程设计对象与决策闭环。

请先完整阅读本 Prompt，再检查代码库。除非遇到本文规定的真实阻断条件，否则不要在分析或 Phase 1 后停下等待确认；应连续完成当前仓库和依赖条件下可实现的 Phase 1、Phase 2 与 Phase 3，运行测试、修复问题，并提交最终实现报告。

---

## 0. 不可偏离的任务定义

前三个问题分别解决：

```text
Problem 1 — Workflow Engine：谁控制科研流程、何时调用什么模块
Problem 2 — Memory / Iterative Design Loop：如何跨 DBTL 保存项目科学状态
Problem 3 — Bottleneck Diagnosis：如何形成、比较并更新机制假设
```

Problem 4 必须解决：

> 如何把已经通过 Diagnosis Handoff Gate 的机制诊断，在明确项目目标、现实资源约束和不确定性的条件下，转化为多个机制与风险互补的 Engineering Strategies 和 Candidate Designs；通过证据、模型、trade-off、buildability 与 validation 评价形成设计组合；再经 evaluator 修订和 human approval 生成 Build/Test Package，并把版本、选择理由、失败和实验结果回写 Memory，驱动下一轮 DBTL。

目标数据流为：

```text
DiagnosisDecision
  → Handoff Gate
  → Objective and Constraint Formalization
  → Engineering Strategy Generation
  → Design-space Construction
  → Candidate Portfolio Generation
  → Evidence / Model / Counterfactual Evaluation
  → Trade-off and Buildability Evaluation
  → Portfolio Decision
  → Build/Test Planning
  → Evaluator Revision Loop
  → Human Approval Gate
  → DesignVersion Persistence
  → Experiment Outcome Ingestion
  → Memory Update
  → Next Design / Reopen Diagnosis / Stop
```

禁止退化为：

```text
user goal → LLM → gene list → Markdown
```

---

## 1. 开发纪律与权限边界

### 1.1 先审计，后修改

开始编码前必须检查：

1. 项目入口、后端框架、前端框架、配置与启动方式；
2. Problem 1 Workflow 的状态机、路由、事件或 orchestration 入口；
3. Problem 2 Memory 的项目、版本、事件、持久化与读取接口；
4. Problem 3 Diagnosis 的正式输出对象、状态和 Handoff Gate；
5. 现有 provider、tool registry、LLM structured output、数据库或文件持久化机制；
6. 现有测试、类型检查、lint、build 与端到端验证命令；
7. 当前工作树已有改动，禁止覆盖与本任务无关的用户修改。

先在工作日志或实现报告草稿中记录一份 `Current-State Evidence Table`：

| 关注项 | 实际文件/符号 | 当前能力 | 缺口 | 本次接入方式 |
|---|---|---|---|---|
| Workflow | 真实路径与类/函数 |  |  |  |
| Memory | 真实路径与类/函数 |  |  |  |
| Diagnosis | 真实路径与类/函数 |  |  |  |
| Persistence | 真实路径 |  |  |  |
| Tools/Models | 真实路径 |  |  |  |
| API/UI | 真实路径 |  |  |  |
| Tests | 真实路径 |  |  |  |

不得假设某个接口存在；必须以代码证据为准。若已有等价对象，应扩展或适配，避免平行创建第二套架构。

### 1.2 架构优先，但不允许只搭空架构

必须先确定核心数据对象、模块边界、状态变化和跨问题接口，再实现业务逻辑。

禁止：

- 将全部设计逻辑塞进一个 system prompt 或单一函数；
- 只新增 dataclass/Pydantic schema、抽象类、TODO 或 mock；
- 只实现前端卡片或 Markdown 渲染；
- 用字符串在模块间传递关键科学状态；
- 为本任务无关内容进行大规模重构；
- 硬编码只对 L-tryptophan 有效的最终答案；
- 为了测试通过而让 production workflow 使用固定 mock 数据；
- 修改后端科学逻辑之外的系统，除非是完成真实集成所必需。

### 1.3 一次任务连续实施

本任务采用 Phase 1–3 是为了控制复杂度，不代表只实现 Phase 1。

每完成一个 Phase，必须：

1. 运行该阶段相关测试；
2. 修复阻断性错误和本次引入的回归；
3. 验证与既有 Workflow 的真实集成；
4. 记录完成项、降级项和证据；
5. 自动继续下一阶段。

不得以“后续接口已预留”“建议下一轮继续”“Phase 3 依赖模型”为理由提前结束。外部依赖缺失时，按第 12 节执行诚实降级，并完成可运行闭环。

---

## 2. 科学边界与核心不变量

以下规则必须写入服务层验证、状态机 guard、evaluator 或测试，而不能只写在提示词和文档中。

### 2.1 Diagnosis 与 Design 的边界

- Diagnosis 回答“什么机制最可能限制当前目标表型”；Design 回答“在该诊断和工程目标下，值得构建或测试什么”。
- Design 优化结果不得反向提高 Diagnosis confidence。
- `unresolved_hypotheses` 不得静默转换为确定机制。
- 若诊断未通过 Handoff Gate，只允许输出 `diagnostic_blocked`、`needs_human_approval` 或 `diagnostic_probe`，不得输出伪装成确定答案的生产株设计。
- 诊断性设计可以因信息价值而被选择，即使其预期产量不是最高。

### 2.2 Project Objective 与科学置信度隔离

- titer、yield、productivity、growth、成本、时间等偏好可以改变候选优先级。
- 项目偏好不得改变机制证据强度、诊断置信度或模型是否可用。
- 所有硬约束、软偏好、权重或 preference order 必须显式保存。

### 2.3 时间与环境条件不可丢失

所有设计、预测与实验计划必须继承：

- chassis 及版本/基因型；
- medium、carbon source、oxygenation、temperature；
- batch/fed-batch/continuous 等过程模式；
- growth phase、sampling time 或 temporal scope；
- baseline state/reference condition。

不同阶段或环境的结论不得静默合并。静态 GEM 结果不得表述成完整动态轨迹。

### 2.4 模型预测不是事实

- LLM 生成的机制解释不是实验或模型计算结果。
- GEM、vEcoli、kinetic model、resource allocation model 等必须通过真实 adapter 调用。
- 模型不可用时标记 `not_computed` 或 `unavailable`，不得让 LLM 补造数值。
- 模型冲突必须被保留为结果并触发补数据、判别实验或人工评审，禁止静默平均。

### 2.5 多目标决策不可伪装成单一真值

- 保留 objective vector、hard constraint result、uncertainty 和 Pareto 状态。
- 可在用户明确偏好后生成推荐排序，但不得隐藏 Pareto trade-off。
- 禁止生成没有量纲、依据和校准说明的伪精确综合分数。

### 2.6 Build-ready 必须有证据门槛

缺少关键菌株信息、构建设计、材料、protocol、对照、重复、采样、QC 或 decision rule 时，只能是 `conceptual`、`evaluated` 或 `planning_ready`，不得标记 `build_ready`。

### 2.7 Human Governance

系统是 Engineering Decision Support，不是未经授权的自动化实验室。进入实验执行前必须经过显式 Human Approval Gate。保留批准人/角色、时间、决定、条件与理由；未批准不得进入 `approved_for_build`。

---

## 3. 必须实现的核心数据模型

应使用项目既有的数据建模方式。下列字段是语义最低要求，名称可为适应现有风格做小幅调整，但不得丢失含义。所有枚举需集中定义，关键对象需有稳定 ID、时间戳、schema/version 字段和序列化验证。

### 3.1 `EngineeringDesignProject`

至少包含：

```yaml
project_id:
schema_version:
chassis:
chassis_version_or_genotype:
baseline_state_id:
diagnosis_reference:
temporal_and_environmental_context:
project_objectives:
  primary_metrics: []
  secondary_metrics: []
  hard_constraints: []
  preferences_or_weights: []
available_resources:
autonomy_level:
required_human_gates: []
status:
created_at:
updated_at:
```

### 3.2 `DiagnosisHandoff`

不得只保存一个诊断摘要字符串，至少保留：

```yaml
diagnosis_id:
diagnosis_version:
decision_status:
supported_hypotheses: []
unresolved_alternatives: []
counterevidence: []
confidence:
uncertainty: []
evidence_references: []
engineering_value_assessment:
temporal_and_environmental_context:
approved_for_design:
approval_reference:
```

需要兼容 Problem 3 当前真实对象；若字段缺失，使用 adapter 显式标记，不得凭空补全。

### 3.3 `EngineeringStrategy`

```yaml
strategy_id:
diagnosis_reference:
engineering_objective:
mechanism_target:
strategy_class:
rationale:
expected_causal_chain: []
evidence_links: []
applicability_conditions: []
known_tradeoffs: []
failure_modes: []
excluded_strategy_reasons: []
uncertainty: []
```

`strategy_class` 至少能表达但不限于：

- precursor supply；
- feedback relief；
- competing-flux control；
- cofactor/energy balancing；
- resource-burden management；
- dynamic regulation；
- transport/tolerance engineering；
- process-condition engineering；
- diagnostic/measurement probe。

系统不得从 Diagnosis 直接跳到 gene list；必须先形成 Strategy，并解释适用与排除理由。

### 3.4 `GeneticModification`

至少包含：

```yaml
modification_id:
target_type:
target_identifier:
operation:
desired_effect:
allele_or_variant:
expression_control:
genomic_or_vector_context:
order_or_dependency:
reversibility:
evidence_links: []
assumptions: []
```

至少区分 knockout、knockdown、attenuation、overexpression、allele replacement、promoter/RBS editing、gene insertion、dynamic control 和 process-only intervention。未知细节必须为 `unknown`/`to_be_determined`，不得伪造具体序列、质粒或引物。

### 3.5 `CandidateDesign`

```yaml
design_id:
design_version:
parent_design_ids: []
strategy_ids: []
portfolio_role:
genetic_modifications: []
regulatory_architecture:
process_modifications: []
expected_mechanism:
causal_chain: []
interaction_and_epistasis_assumptions: []
evidence_links: []
counterfactual_requests: []
counterfactual_results: []
uncertainty_and_model_conflicts: []
tradeoff_profile:
buildability_assessment:
build_test_package:
debug_and_fallback_plan:
safety_flags: []
readiness:
status:
```

### 3.6 `DesignPortfolio`

至少支持以下角色：

- `reference_or_control`；
- `low_risk`；
- `high_upside`；
- `information_gain`；
- `process_first`（适用时）；
- `fallback`（适用时）。

Phase 1 至少生成 low-risk、high-upside、information-gain 三类候选；若科学上不适用，必须输出结构化缺席理由。候选之间必须在机制、干预架构、风险暴露或信息价值上实质不同，不能只是剂量或措辞变化。

### 3.7 `DesignEvaluation`

```yaml
evaluation_id:
design_id:
design_version:
objective_vector: []
hard_constraint_results: []
mechanism_consistency:
evidence_assessment:
model_results: []
model_agreement_and_conflicts: []
sensitivity_and_robustness:
tradeoff_profile:
buildability:
validation_feasibility:
expected_information_gain:
safety_and_governance:
evaluator_findings: []
required_revisions: []
pareto_status:
recommendation:
provenance:
```

评价结果必须保存依据、来源与不确定性。定性评分应使用有定义的 ordinal scale，并允许 `insufficient_evidence` / `not_computed`，不能强迫所有项产生分数。

### 3.8 `BuildTestPackage`

至少包含：

```yaml
construction_concept:
build_steps_or_milestones: []
required_materials: []
required_capabilities_or_instruments: []
available_resource_matches: []
missing_information_or_resources: []
controls: []
replication_plan:
sampling_plan: []
qc_checkpoints: []
target_readouts: []
mechanism_readouts: []
expected_observations: []
decision_rules: []
failure_signatures: []
debug_plan: []
fallback_plan: []
estimated_time_cost_and_risk:
readiness:
```

这是最小实验执行计划，不要求实现 LIMS、自动采购或仪器调度。若现有数据不足，仍需输出结构完整的计划并列明缺项。

### 3.9 `DesignVersion` 与 `DesignMemoryEvent`

每次生成、修订、选择、拒绝、批准、构建和 Test 回传均须保留事件，而不是覆盖旧对象：

```yaml
project_id:
design_id:
design_version:
parent_design_ids: []
event_type:
actor:
timestamp:
diagnosis_reference:
selected_strategy_ids: []
changed_fields: []
modification_reason:
evaluator_results: []
selected_or_rejected:
rejection_reasons: []
human_decision:
build_or_test_result:
expected_observed_residuals: []
failure_classification:
outcome_update:
next_iteration_reason:
provenance:
```

至少区分：`assembly_failed`、`transformation_failed`、`assay_failed`、`measurement_invalid`、`biological_underperformance`、`unexpected_tradeoff`、`success` 和 `inconclusive`。失败不能只保存 `success=false`。

---

## 4. 必须实现的七个核心模块

每个模块必须具备真实输入、结构化输出、错误/不足状态、可测试业务逻辑和 provenance；不得只是一个接口名。

### 4.1 Engineering Design Service / State Machine

负责承载完整状态流。建议状态至少包括：

```text
diagnostic_blocked
→ objective_draft
→ strategy_generated
→ portfolio_generated
→ evaluation_in_progress
→ revision_required | portfolio_evaluated
→ planning_ready
→ awaiting_human_approval
→ approved_for_build | rejected
→ build_in_progress
→ test_pending
→ tested
→ learning_update
→ next_iteration | diagnosis_reopened | completed
```

必须有显式 transition guard 和非法转换测试。不要把状态仅存在前端。

### 4.2 Strategy Generator

输入：`DiagnosisHandoff + ProjectObjectives + Context + Constraints + relevant memory`。

输出：多个结构化 `EngineeringStrategy`。

要求：

- 先围绕受支持机制生成策略，再实例化干预；
- 说明 expected causal chain、适用条件、证据、风险和失败模式；
- 记录为什么未选择明显的替代策略；
- 可使用 LLM 生成草案，但必须经 schema validation、规则检查和 evidence grounding；
- 不得让 LLM 的自评成为 evidence。

### 4.3 Candidate Portfolio Generator

输入：Strategies、design-space constraints、resources、历史设计与失败。

输出：结构化 `DesignPortfolio`。

要求：

- 定义允许变化维度和不可行组合；
- 生成角色互补的有限候选，不无约束穷举；
- 检查候选机制/架构多样性；
- 检查与历史失败或已拒绝设计的重复；
- 组合改造必须记录 dependency/epistasis assumptions；
- information-gain candidate 必须写明它区分哪些假设、预期何种观察会支持/反对各假设。

### 4.4 Design Evaluator

实现可组合的独立 evaluator，至少包括：

1. `MechanismEvaluator`；
2. `EvidenceEvaluator`；
3. `CounterfactualEvaluator`；
4. `TradeoffEvaluator`；
5. `BuildabilityEvaluator`；
6. `ValidationEvaluator`；
7. `SafetyGovernanceEvaluator`；
8. `DiversityEvaluator`。

每个 evaluator 输出：

```yaml
status: pass | warning | fail | insufficient_evidence | not_computed
findings: []
evidence_or_tool_refs: []
assumptions: []
required_revisions: []
blocking: true | false
```

Evaluator 必须能触发 revision loop。修改后创建新 `DesignVersion`，保留父子关系、修改理由和旧评价。循环必须有停止条件，例如无 blocking finding、达到 revision 上限、证据不足转人工、或返回 Diagnosis。

### 4.5 Multi-objective and Portfolio Decision

要求：

- 评价 titer/yield/productivity、growth/viability、stability、resource burden、by-product/toxicity、build complexity、time/cost、evidence、information gain、reversibility 和 safety 等适用维度；
- 硬约束先过滤；
- 计算或确定 Pareto dominance 时保留缺失值与不确定性；
- 不以任意加权总分替代 Pareto 结果；
- 根据显式 ProjectObjective 输出推荐，但保留替代项和拒绝理由；
- 若证据不足，允许返回 `insufficient_evidence` 或推荐一组候选，而非强制唯一答案。

### 4.6 Build/Test Planner

输入：selected candidates、资源、实验上下文和 evaluator findings。

输出：`BuildTestPackage`。

要求：

- 将 construction concept、validation experiment、expected observation、decision rule、QC、debug 与 fallback 串成闭环；
- 同时验证目标表型、机制和 trade-off，不只测最终产物；
- 对照、重复、采样与判读规则缺失时阻止 `build_ready`；
- 不得伪造实验室已有质粒、菌株、仪器、耗材、具体 protocol 或库存；
- 大规模或多位点设计应拆成带中间 QC 的 milestones，并有回滚方案。

### 4.7 Problem 2 Memory / DBTL Integration

必须真实接入现有 Memory 层，而不是把 JSON 另存到孤立目录。

要求：

- 写入所有 DesignVersion 和关键决策事件；
- 下一轮生成前读取相关历史版本、失败分类、observed outcome 和 residual；
- 防止在条件相同且无新证据时重复生成已失败方案；
- 保留 selected/rejected candidates 与拒绝理由；
- Test 回传后决定：更新设计、重新打开 Diagnosis、继续下一轮或 Stop；
- 若现有 Memory 尚不支持所需事件，使用最小兼容扩展或 adapter，并保持既有数据可读。

---

## 5. Problem 3 → Problem 4 强制接口

Engineering Design 只能由以下两类输入触发：

1. 有效且通过 Engineering Value / Handoff Gate 的 `DiagnosisDecision`；
2. 未完全收敛但经显式人工批准、且目的为判别机制的 `diagnostic_probe`。

适配器必须：

- 读取 Problem 3 的真实对象，不复制一份独立诊断；
- 验证 diagnosis ID/version 和项目/底盘/环境一致性；
- 继承支持假设、未解决替代、反证、置信度、不确定性、证据和时间条件；
- 对旧版或缺字段输入返回清晰 validation result；
- 保存 adapter provenance 和缺失字段；
- 当 Diagnosis 后续更新时，使基于旧版本的设计可被识别为 stale，而不是静默继续。

禁止：

- 用户只输入目标产物就直接进入最终设计；
- 用设计预测收益作为诊断证据；
- 丢弃 unresolved alternatives；
- 将不同底盘、培养条件或阶段的诊断无提示复用。

---

## 6. Problem 4 → Problem 2 强制回写接口

每次以下操作都应形成 Memory Event：

- strategy generated/rejected；
- candidate generated/revised/rejected/selected；
- evaluation completed；
- human decision；
- build status changed；
- experiment outcome ingested；
- expected–observed residual calculated；
- failure classified；
- diagnosis reopened / next iteration / stopped。

下一轮生成必须查询并使用：

- 既有 DesignVersion lineage；
- 曾失败、曾拒绝和已测试方案；
- 失败属于构建、测量还是生物学原因；
- 预期与观察差异；
- evaluator 的 blocking findings；
- PI/Wet Lab 的批准、否决或附加条件；
- 新增证据和上下文变化。

禁止覆盖旧版本、只保存最终报告或把 Memory 当聊天摘要。

---

## 7. Phase 1 — Core Design Generation（必须真实运行）

必须完成：

- 所有核心 schema 与枚举；
- Diagnosis adapter 与 Handoff Gate；
- Project Objective / Constraint formalization；
- Strategy Generator；
- Candidate Portfolio Generator；
- Basic evaluator suite；
- 多目标向量和基础 Pareto 比较；
- Design workflow state 与 persistence；
- 结构化 API/service 输出；
- 单元测试、接口测试和 Phase 1 集成测试。

最低端到端链：

```text
DiagnosisDecision
→ EngineeringStrategy[]
→ DesignPortfolio
→ DesignEvaluation[]
→ PortfolioDecision
```

最低候选组合：low-risk、high-upside、information-gain；三者必须实质不同。

---

## 8. Phase 2 — Build/Test and Memory Integration（本次必须继续完成）

必须完成：

- Build/Test Planner；
- buildability 与 readiness gate；
- validation、controls、replication、sampling、QC、decision rules；
- debug 与 fallback；
- DesignVersion lineage；
- Problem 2 Memory write-back；
- 历史读取与重复失败防护；
- version comparison；
- Human Approval Gate；
- API/service 与 workflow 集成测试。

最低端到端链扩展为：

```text
PortfolioDecision
→ BuildTestPackage
→ Evaluator Revision
→ Human Approval
→ Versioned Persistence
→ Memory Event
```

缺少资源或 protocol 时不得停止；生成完整的 `planning_ready` 包、缺项列表和升级条件。

---

## 9. Phase 3 — Advanced Decision Support（本次完成当前可实现范围）

必须实现：

- 标准化 counterfactual request/result schema；
- 模型 adapter registry/interface；
- tool availability detection；
- 已接入模型的真实调用；
- 模型缺失时 `unavailable/not_computed` 诚实降级；
- model agreement/conflict 和 sensitivity 表达；
- 多目标/Pareto comparison；
- evaluator revision loop 与 stopping condition；
- DBTL outcome ingestion；
- expected–observed residual；
- failure classification；
- next-iteration design generation；
- diagnosis reopen / stop decision；
- human approval 与 audit trail；
- Phase 3 集成和降级测试。

若 GEM、vEcoli、kinetic model、resource allocation model、literature DB、UniProt、strain/plasmid DB 或实验设备尚未接入：

1. 不得伪造其计算或查询结果；
2. 建立正式 adapter contract；
3. 检测是否可用；
4. 有真实工具时调用并记录版本、输入、输出、假设和错误；
5. 无工具时返回明确状态与缺失能力；
6. 可提供规则型/结构化定性 baseline，但必须标记来源与限制；
7. 用 fake adapter 只测试接口、冲突与失败路径，不得冒充生产结果。

Phase 3 的完成不代表已实现可靠 Virtual Cell。最低完成标准是：反事实请求可结构化表达；真实模型可插拔调用；缺失模型能诚实降级；多目标结果可比较；实验结果可回写；下一轮继承上版结果和失败原因。

---

## 10. API、持久化与前端要求

先遵循现有架构，不得为了本任务另起一套应用。

### 10.1 后端/API

至少应让现有系统能够：

- 从 diagnosis 创建 Engineering Design workflow；
- 获取项目、strategies、portfolio、evaluation 和 Build/Test Package；
- 提交 objective/constraint 与资源信息；
- 请求评价/修订；
- 提交 human decision；
- 提交 build/test outcome；
- 获取 version history、audit trail 和 comparison；
- 返回结构化 validation/error/degradation 状态。

具体 endpoint 命名服从现有风格。业务逻辑不得写在路由层。

### 10.2 持久化

- 使用现有数据库/工作区持久化抽象；
- 保存 canonical structured object，而不是仅保存渲染文本；
- 支持重新加载后继续 workflow；
- 版本更新不可破坏旧数据；必要时增加 migration 或兼容解析；
- 保证并发/重复请求不会静默覆盖历史，采用现有项目可支持的 optimistic locking、idempotency key 或版本检查方式。

### 10.3 前端

后端与核心逻辑优先。若现有前端已有相应工作台，则以最小必要改动接入真实 API，至少呈现：

- Diagnosis basis；
- Strategy；
- Candidate Portfolio；
- trade-off/Pareto；
- buildability/readiness；
- evaluator findings/revisions；
- human approval；
- version lineage 与 audit status。

禁止用前端本地假数据假装模块已完成。若本任务范围和时间不足以完整重做 UI，必须优先保证后端闭环、API 和测试，并在报告中准确说明 UI 覆盖范围。

### 10.4 用户可读 Design Report

报告只是结构化对象的 renderer，至少包含：

1. Executive Summary；
2. Objectives、success criteria、hard constraints；
3. Diagnosis basis 与 unresolved uncertainty；
4. Strategies；
5. Candidate Portfolio；
6. candidate modifications 与 causal rationale；
7. evidence、model/counterfactual status；
8. trade-off/Pareto comparison；
9. buildability 与 missing requirements；
10. Build/Test、controls、QC、decision rules；
11. risks、debug、fallback；
12. evaluator findings 与 revisions；
13. selected/rejected designs 与理由；
14. human approval、milestones 和 next review trigger。

报告中的关键判断必须能追溯到对象字段、证据、工具结果或明确标记的 expert/LLM judgment。

---

## 11. Evaluator 与生成器的证据等级

评价时至少区分：

- `experimental_evidence`：直接实验数据；
- `model_computation`：真实工具计算；
- `curated_knowledge`：结构化知识库/文献条目；
- `general_biological_knowledge`：无项目特异直接证据；
- `expert_or_llm_judgment`：仅作为建议或审查信号；
- `unknown`。

规则：

- LLM critic 不能被记录为实验或模型证据；
- 文献外推必须保存物种、菌株、环境与表型差异；
- 对核心主张缺证据时，降低 readiness 或触发 validation，不得自动填满引用；
- 每次工具调用保存工具名、版本、输入摘要、时间、状态和结果引用；
- 不得将不可访问的外部数据库假装成已查询。

---

## 12. 允许停止的真实阻断条件与降级策略

只有以下情况允许停止并向用户请求决定：

- 缺少当前代码库之外、且无法替代的必要凭证；
- 缺少必须由 PI/用户决定、不同选择会实质改变系统行为的科学或治理参数；
- 继续需要不可逆破坏既有数据或接口；
- 现有代码严重损坏，无法建立可运行基线，且已完成安全范围内诊断；
- 需要实际执行外部实验、采购、消息发送或其他未授权行动。

下列情况不是停止理由：

- 没有 GEM/vEcoli；
- 没有 UniProt、文献库或菌株库凭证；
- 没有自动化实验设备；
- 当前知识库不够完整；
- 无法可靠计算数值预测；
- 某字段信息缺失。

遇到这些情况，应实现 adapter、availability 状态、`not_computed`、结构化定性 baseline、缺项清单、人工 gate 和对应测试，并继续端到端实现。

---

## 13. 强制测试矩阵

测试应遵循现有框架。至少覆盖：

### 13.1 Schema 和状态

- 有效/无效对象序列化；
- enum 和 schema version；
- 非法状态转换；
- 旧版本兼容或 migration；
- persistence 后重新加载并继续流程。

### 13.2 Diagnosis Handoff

- 有效诊断通过；
- 未批准诊断被阻断；
- unresolved hypothesis 生成 diagnostic-probe；
- chassis/context 不一致被识别；
- diagnosis version 更新使旧设计变为 stale；
- project objective 改变排序但不改变 diagnosis confidence。

### 13.3 Strategy 与 Candidate

- 先 Strategy 后 modification；
- 生成至少三类实质不同候选；
- DiversityEvaluator 能识别表面改写；
- historical failure 能抑制无新理由的重复方案；
- 组合设计保留 epistasis assumption。

### 13.4 Evaluation

- hard constraint 在排序前生效；
- Pareto 结果保留 trade-off；
- 缺证据返回 insufficient_evidence；
- 模型冲突不被平均；
- 模型不可用不生成虚假数值；
- evaluator revision 创建新版本；
- revision loop 可正常停止。

### 13.5 Build/Test

- 缺材料/protocol/QC 时不能 build_ready；
- planning_ready 包含缺项和升级条件；
- 对照、重复、target/mechanism/trade-off readout 和 decision rule 存在；
- debug/fallback 可追踪；
- 未 human approval 不得进入 approved_for_build。

### 13.6 Memory / DBTL

- 每次决策形成事件；
- 旧版本不被覆盖；
- 能区分构建失败、测量失败和生物学失败；
- outcome ingestion 计算/记录 residual；
- 下一轮读取历史；
- 可触发 next iteration、diagnosis reopen 或 stop。

### 13.7 E. coli L-tryptophan 端到端验收案例

使用仓库现有 fixture 或新增最小可信 fixture，测试：

- 底盘：E. coli K-12；
- 底物：glucose；
- 示例诊断：PEP/E4P precursor limitation，包含明确不确定性和证据引用占位；
- 输出至少 low-risk、high-upside、information-gain 三类机制或架构不同候选；
- 展示 growth、burden、by-product、build complexity、evidence 和 information gain 的权衡；
- 生成 Build/Test Package 与 readiness；
- 未提供真实材料和 protocol 时不得 build_ready；
- 模型未接入时 counterfactual 为 not_computed；
- Test outcome 回写后生成新版本或 reopen diagnosis。

此 fixture 用于验证系统能力，不得把该案例的具体改造答案硬编码进生产逻辑。

### 13.8 回归验证

- 运行与改动相关的全部测试；
- 尽可能运行项目全量测试、typecheck、lint 和 build；
- 若因既有问题失败，记录准确命令、错误和为何判断为既有问题；
- 不得删除或弱化既有测试来制造通过。

---

## 14. 完成定义

只有同时满足以下条件，才可以宣布 Problem 4 完成：

1. `DiagnosisDecision` 能实际触发 Engineering Design Workflow；
2. 无有效诊断时系统能阻断或生成获批的 diagnostic probe；
3. Strategy Generator 输出结构化策略与因果链；
4. Candidate Generator 生成机制/架构上不同的候选组合；
5. Evaluator 保存逐项结论、依据、不确定性和 required revisions；
6. 系统保留多目标向量和 Pareto trade-off；
7. 能选择候选、保留组合，或明确返回 insufficient_evidence；
8. Build/Test Planner 输出带 readiness 和缺项状态的计划；
9. build_ready 与 human approval gate 真正生效；
10. `EngineeringDesign` 可持久化、重新加载并继续；
11. `DesignVersion` 形成可查询的父子版本；
12. Problem 2 Memory 接收设计、决策、失败和 Test 结果；
13. 下一轮读取历史并利用失败原因；
14. Counterfactual/外部模型缺失时不伪造结果；
15. 已存在模型可通过标准 adapter 真实调用；
16. 多模型冲突和 sensitivity 被保留；
17. Test outcome 可触发 next iteration、Diagnosis reopen 或 Stop；
18. 核心单元、接口、集成和端到端测试通过；
19. 现有 Workflow、Memory、Diagnosis 的核心功能未被破坏；
20. 最终实现报告包含完整证据。

以下情况不得报告为完成：

- 只建立 Schema；
- 只建立空 adapter；
- 只生成 Markdown；
- 只完成前端展示；
- 只完成 happy path；
- production workflow 仍使用 mock；
- Phase 2/3 只留 TODO；
- LLM 定性文本冒充模型计算；
- 没有真实接入 Problem 3 或 Problem 2；
- 测试只验证对象能创建，未验证科学边界和状态行为。

---

## 15. 实施顺序与最终输出

### 15.1 编码前

完成仓库审计，然后输出简洁的实施说明：

1. 当前架构与真实接口位置；
2. 将复用和扩展的对象；
3. 计划新增/修改的文件；
4. 数据流和状态变化；
5. Phase 1–3 实施与测试顺序；
6. 已识别的外部依赖和降级方式。

这不是等待用户确认的暂停点。若不存在真实阻断条件，输出后继续编码。

### 15.2 编码中

- 小步修改；
- 每个 Phase 后运行测试并修复；
- 保持代码风格、类型和错误处理一致；
- 不提交密钥，不打印 `.env` 内容；
- 不覆盖无关用户改动；
- 对科学与模型能力采用保守、可审计表述。

### 15.3 最终实现报告

完成后必须报告：

1. 架构变化和实际数据流；
2. 新增/修改文件；
3. Phase 1、2、3 各自已完成能力；
4. Problem 3 和 Problem 2 的真实集成点；
5. 可运行 API/命令/页面入口；
6. 测试命令、通过数量与失败情况；
7. E. coli L-tryptophan 端到端案例结果摘要；
8. 所有降级实现、`not_computed` 与未接入外部依赖；
9. 已知限制与科学边界；
10. 后续只需配置或替换哪些 adapter，不应再重新设计哪些架构。

不要只说“已完成”。所有完成声明必须有文件、测试、API 响应或端到端运行证据。

---

## 16. 最终原则

本模块的核心不是产生更长、更专业的答案，而是形成一个可靠的 Engineering Design Decision Loop：

```text
诊断是科学起点
项目目标是决策条件
策略先于基因
候选必须多样且有角色
预测必须标注模型与不确定性
Trade-off 必须可见
Buildability 必须前置
Validation 必须能区分机制
Evaluator 必须能触发修订
Human Gate 必须控制实验推进
失败必须成为可学习状态
Memory 必须支持下一轮不重犯错误
```

请现在开始：先审计现有代码并给出基于真实文件和符号的实施说明，然后在无真实阻断条件时连续完成 Phase 1、Phase 2 和 Phase 3 的当前可实现范围，验证端到端闭环，最后提交证据充分的实现报告。

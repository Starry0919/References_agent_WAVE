# Problem 3：Bottleneck Diagnosis Loop

## Claude Code 完整实现 Prompt

> **最高实现原则：优先保证科学边界正确、核心诊断对象稳定，以及 Problem 1 → Problem 3 → Problem 4 → Problem 2 的端到端闭环真实可运行；不以本次任务一次性建成完整 Virtual Cell 或全自动因果发现系统为目标。凡依赖 GEM、vEcoli、组学平台、文献数据库、资源分配模型或尚未校准算法的能力，必须通过可替换 adapter/interface 接入；能力不可用时应返回显式状态并诚实降级，禁止由 LLM 伪造模型计算、实验观测或因果确定性。**

这里的“不追求完整 Virtual Cell”不构成缩减本 Prompt 强制范围的理由。Phase 1–3 仍须在本次任务中连续完成其在当前代码库和依赖条件下定义的最低可运行闭环。外部能力缺失时，必须完成正式接口、能力检测、`not_computed` / `unavailable` 状态、结构化降级路径和相应测试，而不能只留下空接口、TODO 或 mock-only demo。

你现在需要在现有 Synthetic Biology Agent / agent-harness 代码库中，实现 `Problem 3: Bottleneck Diagnosis Loop`。

本任务不是继续撰写文献综述，不是增加一个“分析瓶颈”的长 LLM prompt，也不是根据用户目标直接输出基因清单。你要把异构观测转化为可持久化、可竞争、可反驳、可更新的机制假设；用真实证据和可用模型约束它们；选择最能区分剩余假设的下一项测试；在明确停止门和工程价值门后，向 Problem 4 输出结构化 `DiagnosisDecision`，并把全过程回写 Problem 2 Memory。

开始前必须完整阅读：

- `问题03_Bottleneck_Diagnosis_八份文献蒸馏与Agent适用性评判.md`：本任务的科学规格与文献边界；
- 当前代码库内 Problem 1、Problem 2 和 Problem 4 的真实实现；
- 项目内现有 schema、workflow、tool registry、provider、persistence、API、UI 和 tests。

若文件名或目录不同，请通过仓库搜索定位，不得因路径不一致停止。除非遇到本文定义的真实阻断条件，否则不要在分析、架构说明或 Phase 1 后等待确认；应连续实现、测试、修复并提交最终报告。

---

## 0. 不可偏离的任务定义

Problem 3 必须回答：

1. 当前异常有哪些互相竞争的解释？
2. 每个解释能说明哪些观测，又与哪些观测冲突？
3. 排名依赖哪些数据、模型、条件和假设？
4. 哪项测试最能区分尚未排除的假设？
5. 新结果如何更新而不是覆盖旧诊断？
6. 何时可以行动、何时证据不足、何时必须交由人类评审？

正式数据流：

```text
Workflow Trigger / Project State
  → Intake and Data Sufficiency Check
  → Observation Normalization and QC
  → Temporal / Environmental Context Binding
  → Mechanism Graph Construction
  → Competing Hypothesis Generation
  → Evidence Retrieval and Model Computation
  → Evidence–Hypothesis Linking
  → Deduplication and Conditional Assessment
  → Sensitivity / Cross-model Conflict Analysis
  → Diagnostic Test Selection
  → Experimental Execution Plan Draft
  → Belief Update
  → Stopping Gate
  → Engineering Value Gate
  → DiagnosisDecision / Diagnostic Probe / Escalation
  → Problem 4 Handoff and Problem 2 Memory Write-back
```

禁止退化为：

```text
user goal → LLM intuition → gene list → Markdown report
```

Problem 1 决定何时进入诊断；Problem 3 形成并更新诊断状态；Problem 4 依据已通过门控的诊断生成工程设计；Problem 2 保存跨 DBTL 的全部版本、事件、证据和结果。不得平行创建互不连接的第二套工作流或历史存储。

---

## 1. 开发纪律与仓库先审计

### 1.1 编码前必须完成的审计

检查并记录：

1. 项目入口、后端/前端框架、配置和启动命令；
2. Problem 1 的状态机、路由、事件、暂停/恢复和审批机制；
3. Problem 2 的项目状态、事件日志、版本、持久化和读取接口；
4. Problem 4 是否已有 `DiagnosisDecision` adapter 或 Handoff Gate；
5. 现有生物对象、证据对象、LLM structured output 和 validation；
6. tool registry、模型工具、检索工具及其可用性检测方式；
7. 数据库、JSON 文件或其他 persistence 机制；
8. API、前端状态展示及报告渲染；
9. 单元、接口、集成、端到端测试和 build/lint/typecheck 命令；
10. 当前工作树已有改动，避免覆盖无关用户修改。

先生成 `Current-State Evidence Table`，写入最终实现报告：

| 关注项 | 真实文件/符号 | 状态 | 证据 | 缺口 | 本次处理 |
|---|---|---|---|---|---|
| Workflow | | existing / partial / missing / incompatible | | | |
| Memory | | | | | |
| Design handoff | | | | | |
| Schemas | | | | | |
| Persistence | | | | | |
| Tools/models | | | | | |
| API/UI | | | | | |
| Tests | | | | | |

不得凭文件名或注释宣称能力存在；必须找到真实调用链、存储路径和测试证据。已有等价对象时优先扩展或适配，不得为方便而创建孤立的重复 schema。

### 1.2 编码前输出，但不得停下等待确认

在工作日志中简要记录：

1. 当前架构与真实调用链；
2. 将复用、扩展、新增的对象和文件；
3. Problem 1/2/4 的接入点；
4. 数据流与状态机变化；
5. Phase 1–3 的实施与测试顺序；
6. 已识别的外部依赖与降级方案。

完成后直接编码。只有第 16 节所列真实阻断才允许停下询问。

### 1.3 架构优先，但禁止空架构

禁止：

- 把全部逻辑塞进单一 system prompt、service 或 endpoint；
- 只新增 dataclass/Pydantic schema、抽象类、TODO 或占位 adapter；
- 只做 Markdown 报告、聊天回复或前端卡片；
- 用无 schema 的自由文本在模块间传递科学状态；
- 用 LLM 星级或未经校准的 `0–1 confidence` 伪装统计概率；
- 在 production workflow 中使用固定 mock 结果；
- 硬编码 L-tryptophan 的结论或推荐基因；
- 为本任务无关范围做大规模重构；
- 将优化器输出反向当作诊断证据。

---

## 2. 必须固化为代码与测试的科学不变量

这些规则必须进入 schema validation、service、state guard、evaluator 或测试，不能只写在 prompt 和文档里。

### 2.1 观测先于假设，假设先于设计

- 没有最小观测上下文时，系统输出 `data_required`，不能假装完成诊断。
- “提高某产物”是工程目标，不是瓶颈观测。
- 诊断首先生成 competing hypotheses，不直接生成 Gene List。
- FastKnock、SimulKnock、OptKnock 或行动库属于设计/优化证据，不等于当前异常的因果证明。

### 2.2 竞争假设至少覆盖四类

候选集合必须考虑：

1. biological mechanism：代谢、调控、资源分配、应激、毒性等；
2. process/environment：供氧、底物、pH、温度、发酵阶段等；
3. measurement/data：检测限、批次、归一化、样本错配、QC 等；
4. model mismatch：边界、目标函数、GPR、biomass、参数或适用域错误。

若某类不适用，必须记录排除理由，不能静默缺席。`resource_burden` 是竞争假设，不是默认兜底解释。

### 2.3 证据关系不是二元标签

每条 EvidenceLink 必须使用明确关系：

```text
supports
contradicts
is_consistent_with
does_not_discriminate
```

“与假设一致”不得渲染成“证明假设”。文献、专家规则、LLM 推理、模型预测和实验结果必须保留不同 source type、directness、condition match、quality 和 provenance。

### 2.4 Rule-out 必须有充分条件

单一阴性结果不得自动排除假设。只有同时存在：预先声明的可区分预测、足够灵敏的测量、有效对照、适用条件匹配以及替代解释审查时，才允许进入 `provisionally_ruled_out`。至少支持：

```text
untested
weakly_supported
strongly_supported
weakened
provisionally_ruled_out
non_discriminating
out_of_scope
```

不得默认提供 `definitively_proven` 或 `true_bottleneck`。

### 2.5 时间、环境和底盘上下文不可丢失

Observation、Hypothesis、Evidence、ModelRun、Test 和 Decision 必须可绑定：chassis/genotype、medium、carbon source、oxygenation、temperature、process mode、growth/process phase、sampling time/window 和 baseline。

- 不同时间点不得静默合并；
- 冲突时应形成阶段特异解释或 `temporal_data_gap`；
- 静态 GEM 结果必须标记 steady-state assumption；
- 当前条件的结论不得无警告外推到另一底盘或发酵条件。

### 2.6 模型预测不是事实

- GEM、vEcoli、AMN、kinetic/resource model 必须由真实 adapter 调用；
- 保存 model/version、输入、边界、目标、参数、solver、状态、日志摘要和输出引用；
- 模型不可用时返回 `not_computed` / `unavailable`，不得由 LLM补造数值；
- infeasible、unbounded、timeout、out_of_domain 是正式结果；
- 多模型冲突必须保留，不得由平均、投票或 LLM 任意消除。

### 2.7 项目目标不得污染诊断证据

`ProjectObjective` 可改变工程优先级、下一步行动成本权衡或信息价值，但不得改变诊断证据强度和 mechanism assessment。相同证据在不同目标下，`diagnostic assessment` 应保持一致，`engineering value` 可以变化。

### 2.8 停止的是本轮诊断

禁止写死 `confidence > 0.8 = true bottleneck`，除非该概率经过外部校准。Stopping Gate 只能给出：

```text
actionable_stop
evidence_limited_stop
safety_stop
human_escalation
continue_diagnosis
```

它表示当前是否足以采取下一项低风险/高信息量行动，不表示已发现唯一真因。

### 2.9 诊断与工程价值必须分离

分别保存 `diagnostic_assessment` 与 `engineering_value_assessment`。容易改造或模型预测收益高，不能提高其因果可信度。只有通过 Diagnosis Handoff Gate 的对象才能进入 Problem 4；未通过者只能生成 diagnostic probe、补数据请求或人工升级。

### 2.10 历史不可覆盖

假设、证据、评价、模型运行、测试、目标变化、belief update、审批和 decision 必须追加版本或事件。任何新结果不得原地覆盖旧判断。每次更新必须保存 `prior → evidence/event → posterior state` 的可追踪关系。

---

## 3. 必须实现的核心数据模型

复用项目现有建模方式。字段名可为适应既有风格小幅调整，但语义不可删除。关键对象必须有稳定 ID、project/session 关联、schema version、created/updated time、provenance 和序列化验证。

### 3.1 `DiagnosisProjectState`

至少包含 project、workflow run、biological system、baseline、objective reference、active diagnosis version、status、data sufficiency、approval state 和 linked memory events。

### 3.2 `Observation`

至少包含：

```yaml
observation_id:
biological_system_id:
construct_id:
condition_id:
temporal_state_id:
assay_id:
feature_or_phenotype:
value:
unit:
reference_or_baseline:
uncertainty:
replicates:
qc_status:
detection_limit:
provenance:
raw_data_reference:
```

必须验证单位、QC、condition、time 和 provenance；自由文本观察只能作为 `unstructured_input`，经 normalization 后才能成为正式证据。

### 3.3 `TemporalState` 与 `BiologicalContext`

保存 chassis/strain/genotype、medium、environment、process mode、growth phase、process phase、experiment time、sampling window、recent perturbations、state-transition context 和 steady-state/dynamic assumption。

### 3.4 `ProjectObjective`

至少支持 titer、yield、productivity、growth/viability、stability、scalability、knowledge gain、risk、time/cost constraint 和 approval owner。它只进入测试选择与 Engineering Value Gate，不得写入 hypothesis evidence score。

### 3.5 `MechanismHypothesis`

至少包含：

```yaml
hypothesis_id:
version:
statement:
mechanism_class:
scope:
causal_graph_nodes:
causal_graph_edges:
observations_explained:
expected_observations:
discriminating_predictions:
falsifiers:
assumptions:
applicability_context:
temporal_scope:
parent_or_related_hypotheses:
status:
generation_provenance:
```

LLM 可以提出假设，但必须标记为 generated hypothesis，不能把自身生成文本同时登记为支持证据。

### 3.6 `EvidenceItem` 与 `EvidenceLink`

EvidenceItem 保存 source type、source reference、content summary、condition、time、quality、directness、correction/supersession、model run 或 experiment reference。EvidenceLink 保存 hypothesis、relation、claim、condition match、strength basis、limitations、created by 和 version。

必须支持 publication correction / supersedes；已知勘误不得被旧图或旧标签静默覆盖。

### 3.7 `HypothesisAssessment`

至少包含 explanatory coverage、contradictions、evidence quality/directness、condition match、robustness、testability、remaining uncertainty、ranking/Pareto state、assessment version 和 rationale references。

允许结构化定性等级或可解释的分项量表；禁止没有定义、量纲、校准和来源的伪精确总分。若系统采用权重，必须显式保存并进行敏感性分析。

### 3.8 `DiagnosticTest`

至少包含 compared hypotheses、predicted outcomes per hypothesis、assay、positive/negative controls、decision rule、expected information gain 或定性信息价值、cost、turnaround、availability、technical feasibility、risk 和 prerequisites。

测试必须能区分至少两个仍存假设；只能重复确认单一假设、不能区分替代解释的测试应标为 `non_discriminating`。

### 3.9 `ModelRunRecord` 与 `ModelEvidenceAssessment`

保存 adapter/model/version、capability status、inputs、context、constraints/objective/parameters、solver/runtime status、outputs、uncertainty、domain flags、sensitivity variants 和 reproducibility reference。

ModelEvidenceAssessment 保存跨模型 convergence/conflict、ranking stability、conflict explanation、calibration 和限制。

### 3.10 `CounterfactualPrediction`

保存 hypothesis、intervention/query、baseline state、predicted state/distribution、model runs、assumptions、uncertainty、cross-model agreement 和 out-of-domain flags。没有真实计算时必须为 `not_computed`，LLM 机制叙述只能进入 `qualitative_expectation`。

### 3.11 `ExperimentalExecutionPlan`

只负责把选中判别测试转成可审查的最小计划，至少包含 protocol reference/draft、materials、controls、biological/technical replicates、sampling schedule、QC/acceptance criteria、expected output schema、interpretation rule、owner/approval 和 readiness。

缺少关键字段时只能为 `conceptual` 或 `draft`；不得声称已经领料、预约仪器或执行实验。

### 3.12 `BeliefUpdateEvent`

保存 prior assessment version、新 evidence/test result、更新规则、posterior assessment version、状态变化、未解决冲突、actor、time 和 rationale。旧版本不可覆盖。

### 3.13 `BottleneckValueAssessment`

保存 hypothesis、objective、biological importance、engineering leverage、expected gain range、intervention complexity、growth/stability trade-off、reversibility、robustness、priority、prerequisites 和 rationale。它不是诊断证据。

### 3.14 `DiagnosisDecision`

至少包含：

```yaml
decision_id:
diagnosis_id:
diagnosis_version:
context_reference:
leading_hypothesis_set:
supported_hypotheses:
alternatives_not_excluded:
contradictions:
confidence_representation:
uncertainty:
evidence_references:
model_assessment_reference:
selected_diagnostic_test:
stopping_reason:
engineering_value_assessment:
allowed_next_action:
handoff_status:
human_approval:
created_at:
```

`allowed_next_action` 至少支持：`collect_data`、`run_diagnostic_test`、`reopen_diagnosis`、`handoff_to_design`、`human_review`、`stop`。

---

## 4. 必须实现的服务与模块

模块边界可适配现有代码风格，但职责不得全部混在一个 LLM 调用中。

### 4.1 Intake / Data Sufficiency Gate

验证目标是否只是愿望、是否存在 baseline、底盘/构建/条件/时间/QC/关键表型是否充分。输出 `sufficient / partial / insufficient`、缺失字段、影响和允许动作。缺数据时仍可生成受限假设或补数计划，但不得输出确定诊断。

### 4.2 Observation Normalizer

将原始文本和结构化输入统一为 Observation；完成单位、baseline、replicate、QC、condition、temporal binding 和 provenance 检查。不得自动合并不可比较的数据。

### 4.3 Mechanism Graph Builder

构建 phenotype → process/pathway → reaction/metabolite → enzyme/gene/regulation/resource/environment/measurement/model 的可追踪因果图。边必须有类型、方向、来源和适用上下文。允许不完整图，但必须显式标记未知与冲突。

### 4.4 Competing Hypothesis Generator

从观测和机制图生成机制上不同的假设集合，并确保 biological、process、measurement、model-error 四类得到考虑。进行机制多样性检查；不得只对同一句话做语言改写。

### 4.5 Evidence Retriever / Assessor

复用现有检索和知识库。将 evidence item 与 hypothesis 双向链接；保留支持、反证、consistent、non-discriminating。若无真实检索工具，只能用现有本地知识与一般知识生成“待验证依据”，不得伪造 DOI、实验结果或全文内容。

### 4.6 Hypothesis Deduplicator

合并同义项，保留 parent/child、overlap 和版本关系；不得因去重删除机制互补的替代解释。输出合并理由和被保留 ID。

### 4.7 Model Adapter Registry

为 GEM/COBRA、vEcoli、hybrid/AMN、resource allocation、kinetic/process model 提供统一 capability contract：`detect → validate_input → run → normalize_result → record_provenance`。

只对仓库真实存在或依赖可用的模型执行计算。每个 adapter 必须明确支持范围与不支持范围。

### 4.8 Hypothesis Assessor / Conditional Ranker

基于解释覆盖、反证、直接性、条件匹配、稳健性和可检验性形成分项评价。排序必须保存依据；允许 Pareto front 或 conditional ranking；不得把用户偏好混入 causal assessment。

### 4.9 Sensitivity and Model Conflict Analyzer

在真实模型支持下改变摄取边界、objective、参数或合理条件，记录结论和排名稳定性。跨模型冲突输出 `convergent / partially_convergent / conflicting / insufficient`，并生成冲突解释与下一步区分建议。

### 4.10 Diagnostic Test Selector

比较 information gain、区分能力、成本、时间、材料/仪器可用性、风险和项目目标，选择或列出 Pareto 测试组合。第一版可采用透明的 structured qualitative selection，不要求伪精确贝叶斯 EIG。

### 4.11 Experimental Execution Planner

为被选测试生成最小计划和 readiness。资源或 protocol 不完整时列出缺口，不得升级为 executable/build-ready。

### 4.12 Belief Updater

接收新实验/模型结果，创建新 EvidenceLink、Assessment version 和 BeliefUpdateEvent；保留 prior，不允许直接覆盖 hypothesis status。更新规则必须可追踪和可重放。

### 4.13 Stopping Gate

综合 evidence coverage、fatal contradiction、ranking stability、跨模型稳健性、下一步风险和 additional information value，返回允许动作与理由。没有校准时不得把 LLM 自评分数当作统计概率。

### 4.14 Engineering Value Gate

在诊断评价完成后，独立结合 ProjectObjective 判断是否值得工程化。它可改变设计 handoff 优先级，不能改变诊断排序。

### 4.15 Diagnosis Evaluator / Critic

检查：遗漏替代解释、循环论证、把相关当因果、条件错配、模型越界、证据误标、阴性结果过度排除、时间状态混合、目标污染诊断和 unsupported certainty。Evaluator 只能发现问题和请求修订，不能充当独立证据源。

### 4.16 Report Renderer

报告是结构化对象的视图，不是唯一真源。每个核心判断必须可回溯到 hypothesis/evidence/model run/decision。至少呈现：Executive Summary、上下文与 QC、leading set、支持与反证、未排除替代解释、What we know / do not know、下一判别测试、模型冲突/敏感性、当前状态和设计 handoff。

---

## 5. Workflow 状态机与门控

至少支持以下状态或等价状态：

```text
intake
data_required
observations_normalized
hypotheses_generated
evidence_assessed
model_evidence_pending
hypotheses_ranked
test_selection_required
test_planned
awaiting_test_result
belief_updated
model_conflicted
human_review_required
actionable
evidence_limited
handoff_ready
handed_off_to_design
closed
```

关键 guards：

- 未完成 normalization/QC 不得进入正式 assessment；
- 没有 competing set 不得宣布 actionable；
- 有 fatal contradiction 或 unresolved model conflict 时不得自动 handoff；
- 未选择测试或未满足 stopping rule 时只能继续诊断/补数据；
- Engineering Value Gate 未通过时不得进入生产设计；
- human approval required 但未批准时不得进入 Problem 4；
- 所有 state transition 必须写入事件日志并可恢复。

必须支持 Workflow pause/resume：等待真实实验结果是正常状态，不是失败。测试结果到达后从持久化 diagnosis version 恢复，不得重新从聊天文本开始。

---

## 6. 跨问题接口

### 6.1 Problem 1 → Problem 3

输入至少保留 project/workflow run、trigger reason、biological system、current construct、baseline、observations、objective reference、available tools、human constraints 和 memory snapshot reference。

Problem 1 负责调度，不得自行生成诊断结论；Problem 3 返回下一动作、等待事件或 handoff status。

### 6.2 Problem 3 → Problem 4

只有有效 `DiagnosisDecision` 且 Handoff Gate 通过，才允许触发 Engineering Design。必须传递：

- diagnosis ID/version；
- context and temporal scope；
- leading hypothesis set；
- alternatives not excluded；
- evidence and contradictions；
- uncertainty/confidence representation；
- model conflict/sensitivity；
- engineering value assessment；
- handoff restrictions and approval。

禁止：用户目标直接绕过诊断；把未解决假设静默当成事实；把 Problem 4 的预期收益反向写成 Problem 3 支持证据。

### 6.3 Problem 3 → Problem 2 Memory

每次必须形成追加式 Memory Event，至少包括 observation/QC、hypothesis generation/merge、evidence link、model run、assessment、selected test、belief update、stopping decision、human decision 和 handoff。

下一轮必须能读取旧假设、失败测试、模型冲突和未解决替代解释。不得只保存最终 Markdown 或 `success=false`。

### 6.4 外部实验系统边界

Problem 3 可以形成 plan；库存、领料、预约、SOP 执行、仪器运行属于 ELN/LIMS/automation。未收到真实确认时不得报告已经执行。

---

## 7. LLM 的允许与禁止职责

LLM 可以：

- 结构化用户输入；
- 提出待验证的 competing hypotheses；
- 总结有 provenance 的证据；
- 生成可区分预测草案；
- 组织工具调用；
- 解释结构化结果；
- 由 evaluator 检查逻辑漏洞。

LLM 不可以：

- 心算或伪造 FBA/vEcoli/动力学结果；
- 把自身生成的解释登记为实验或模型证据；
- 伪造文献、DOI、数据库记录、原始数据或 QC；
- 用语言流畅度决定 causal truth；
- 将“可能”“一致”自动升级为“证明”；
- 在缺少校准时输出伪概率；
- 自动审批进入实验执行。

所有 LLM structured output 必须经 schema validation；失败时执行有限重试与显式错误处理，不能静默写入 persistence。

---

## 8. 持久化、版本和审计

必须实现：

- diagnosis aggregate 的保存与重新加载；
- append-only event 或等价不可覆盖历史；
- object/schema version；
- hypothesis/assessment/decision version lineage；
- model run reproducibility metadata；
- evidence provenance；
- human actor/decision/time/reason；
- report snapshot 与结构化真源的关联；
- optimistic locking 或等价并发保护（若现有架构支持并发）；
- migration 或 backward-compatible loading（若扩展既有 schema）。

重新启动服务后，应能恢复到 `awaiting_test_result` 等中间状态并继续，而非丢失诊断进度。

---

## 9. API 与前端最低接入要求

若仓库已有 API/UI，必须接入真实 workflow，而非另做演示页。至少支持：

- 创建/读取 diagnosis；
- 提交 observations；
- 查看 hypotheses、evidence、contradictions 和 context；
- 请求/查看模型运行状态；
- 查看 diagnostic test 与 execution-plan readiness；
- 提交测试结果并触发 belief update；
- 查看 stopping/handoff 状态；
- 进行 human review/approval；
- 查看版本和 audit trail。

前端应明确区分：observed、model-computed、literature-supported、LLM-hypothesized、not-computed、conflicting。不得用颜色或文案把假设伪装成事实。

若当前无前端，不为此新建庞大 UI；优先完成后端真实闭环和可测试 API/CLI。

---

## 10. 分阶段连续实施范围

### Phase 1 — Core Mechanism Diagnosis（必须真实完成）

实现：核心 schema、intake/data gate、normalizer、context binding、mechanism graph、competing generator、evidence linking、deduplication、structured assessment、basic evaluator、workflow state、persistence、Problem 1 输入和基础报告。

最低闭环：

```text
observations → competing hypotheses → evidence relations
→ conditional assessment → next diagnostic action
```

### Phase 2 — Test, Update and Cross-Problem Loop（必须真实完成）

实现：Diagnostic Test Selector、Experimental Execution Plan、Belief Updater、Stopping Gate、Engineering Value Gate、Problem 4 handoff、Problem 2 write-back、pause/resume、version history 和 human review。

最低闭环：

```text
ranked hypotheses → discriminating test → result ingestion
→ versioned belief update → stop/continue/handoff → memory
```

### Phase 3 — Model-aware Decision Support（按当前能力完成可运行最低闭环）

实现：model adapter registry、capability detection、model run record、counterfactual request/result、sensitivity interface、cross-model conflict、ranking stability、honest fallback 和 tests。

若真实 GEM/vEcoli 已存在，必须接入并至少运行一个仓库可用的受控案例；若不存在，完成可替换 adapter contract、`unavailable/not_computed` production path、mock adapter contract tests，但不得宣称真实计算已完成。

Phase 3 的完成不等于完整 Virtual Cell。其最低标准是：系统能表达计算请求、调用可用模型、记录真实结果、保留冲突、在缺失时诚实降级，并据此控制 stopping/handoff。

每个 Phase 完成后运行测试、修复本次错误并自动进入下一 Phase。不得以“接口已预留”结束 Phase 2/3。

---

## 11. 强制测试矩阵

### 11.1 单元测试

覆盖 schema validation、单位/QC/context、evidence relation、hypothesis status、deduplication、assessment separation、state guards、belief versioning、capability status、report traceability。

### 11.2 契约测试

覆盖 Problem 1 input、Problem 4 DiagnosisDecision handoff、Problem 2 event write-back、model adapters、LLM structured output 和 persistence reload。

### 11.3 集成测试

至少验证：

1. 相同证据在“最大滴度”和“工业稳定”目标下 diagnostic assessment 不变，engineering value 可变；
2. 0 h/20 h/30 h 冲突观测不会静默合并；
3. GEM 与另一模型冲突时保留各自结果并进入 `model_conflicted`；
4. 改变 boundary/objective/parameter 后记录 ranking stability；
5. 选中测试可生成材料、对照、重复、采样、QC、数据格式和 decision rule；缺项时保持 draft；
6. 阴性但检测力不足的结果不能 `provisionally_ruled_out`；
7. Executive Summary 每个核心判断能回溯到结构化对象；
8. 未通过 Stopping/Engineering Value/Human Gate 时不得调用正式 Design workflow；
9. 缺 ProjectObjective 时允许诊断，但禁止确定 engineering priority；
10. static model 不被渲染为 dynamic trajectory；
11. 服务重启后能恢复等待实验结果的 diagnosis；
12. 新结果追加 assessment/decision version，不覆盖历史。

### 11.4 端到端案例

至少提供两个非固定 mock-only 的 fixture/scenario：

**案例 A：信息不足的 L-tryptophan 项目**

仅给“提高 L-tryptophan 产量”和底盘时，系统应返回 data gaps 和有限假设，不得直接推荐 `aroG/trpE/tktA/ΔtnaA`。

**案例 B：带时序和冲突证据的诊断**

提供多个时间点、生长/产物/组学或模型残差，系统应形成至少 biological、process、measurement/model-error 类竞争假设，选择可区分测试，摄入结果后更新版本，并产生 continue/stop/handoff 中正确状态。

可增加一个工具不可用案例，验证 `not_computed` 不会被报告为预测成功。

### 11.5 回归与工程验证

运行仓库现有测试、类型检查、lint、build 和相关 smoke test。只修复本任务引入或阻断本任务的错误；记录既有失败，不要掩盖。

---

## 12. 诚实降级与外部依赖

外部能力不可用时：

1. 检测并记录 unavailable 原因；
2. 保留标准 adapter 输入输出；
3. 返回 `not_computed/unavailable/out_of_domain`；
4. 可给 `qualitative_expectation`，但明确其不是 model result；
5. 保存 assumptions、uncertainty 和 missing prerequisites；
6. 继续完成不依赖该工具的诊断流程；
7. 用 contract/mock test 验证接口，不把 mock 接到 production；
8. 最终报告说明真实能力、降级能力和未接依赖。

不得为了满足 Phase 3 安装或编造庞大外部系统；优先架构正确、真实闭环和可替换接入。

---

## 13. L-tryptophan 示例的使用边界

源科学规格中的 L-tryptophan 表格仅用于测试输出形态，不代表真实结论，也不得硬编码。合理输出应类似：

```text
当前无法证明唯一瓶颈。
领先假设包括反馈抑制与 PEP/E4P 前体限制，仍未排除表达负担、过程供氧和模型边界错误。
下一步优先执行能够区分这些解释的对照与测量；在完成前，不应把多个改造一次叠加为确定方案。
```

若输入缺少 genotype、baseline、培养条件、产量/得率/生长、时序或 QC，必须生成 data gap，不能填入常识默认值后宣称完成诊断。

---

## 14. 完成定义

只有全部满足才可宣布 Problem 3 完成：

1. 真实 Workflow 可从项目状态触发 Diagnosis；
2. observations 经 normalization/QC/context 后持久化；
3. 系统生成机制上不同且覆盖替代类别的 competing hypotheses；
4. evidence 可双向追踪并区分支持、反证、一致和不可区分；
5. hypothesis assessment 保留条件、时间、反证和不确定性；
6. 项目目标不会污染 diagnostic assessment；
7. 真实模型由 adapter 调用，缺失时诚实降级；
8. 敏感性和模型冲突能被保存并影响门控；
9. 系统能选择判别实验并生成带 readiness 的计划；
10. 新结果能形成追加式 belief update 和版本关系；
11. Stopping Gate 能区分 actionable、evidence-limited、safety/escalation 和 continue；
12. Engineering Value Gate 与诊断证据分离；
13. 通过门控的 DiagnosisDecision 能真实触发 Problem 4；
14. 全过程能回写并从 Problem 2 Memory 恢复；
15. human gate 在需要时生效；
16. 报告来自结构化真源，核心判断均可追踪；
17. 单元、契约、集成、端到端和现有相关测试通过，或明确记录非本次引入的既有失败；
18. 最终 implementation report 完整。

不得把以下情况报告为完成：

- 只建立 schema 或空 adapter；
- 只新增一个 LLM prompt；
- 只生成 Markdown/前端；
- 只实现 happy path；
- 只对 L-tryptophan 有效；
- 用 mock 通过测试但未接真实 workflow；
- Phase 2/3 只有 TODO；
- 用 LLM 生成值冒充模型或实验结果；
- 未持久化版本与审计记录；
- 未打通 Problem 1、2、4。

---

## 15. 最终交付物

完成代码后，提交：

1. 修改/新增文件清单及职责；
2. Current-State Evidence Table；
3. 最终数据流和状态机说明；
4. 核心 schema 与 API/adapter 契约；
5. Problem 1/2/4 的真实接入点；
6. Phase 1–3 完成状态；
7. 真实能力、降级能力和外部依赖表；
8. 测试命令与结果；
9. 端到端案例结果摘要；
10. 已知限制、未解决风险及其影响；
11. 无需重新设计架构、未来只需配置或替换的 adapters；
12. 启动和最小验证步骤。

所有“已完成”必须给出文件、符号、调用链或测试证据，不得只做文字声明。

---

## 16. 允许停止的真实阻断条件

仅在以下情况允许停止并请求用户决定：

- 缺少当前代码库之外且无法安全替代的必要凭证；
- 缺少必须由 PI/用户决定、且不同选择会实质改变科学行为的参数；
- 继续操作会破坏现有数据、公共接口或用户未提交改动；
- 必须访问不可获得的外部资源，且 adapter + honest fallback 仍无法形成核心闭环；
- 发现安全、伦理或权限边界问题需要人工裁决。

非阻断性信息不足不得停工。应选择最保守且显式记录的实现、完成降级路径、继续测试，并在最终报告中说明。

---

## 17. 最终执行指令

现在请：

1. 完整阅读科学规格与本 Prompt；
2. 审计真实仓库并记录证据；
3. 复用现有架构，确定最小必要变更；
4. 连续完成 Phase 1 → Phase 2 → Phase 3；
5. 每阶段测试并修复本次引入的问题；
6. 验证真实端到端调用、持久化、恢复和门控；
7. 输出最终 implementation report。

不要在架构分析后等待确认，不要只交付设计文档，不要以外部模型缺失为由停在空接口，也不要将 LLM 推理冒充计算或实验。最终目标是一个真实可运行、可追踪、可证伪、可更新、可由人类治理，并能连接 Workflow、Memory 与 Engineering Design 的 Bottleneck Diagnosis Loop。

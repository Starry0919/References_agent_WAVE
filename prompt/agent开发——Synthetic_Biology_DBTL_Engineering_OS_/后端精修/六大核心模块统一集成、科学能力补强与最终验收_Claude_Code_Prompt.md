# Synthetic Biology Agent V1 Final Integration, Scientific Capability Upgrade and Acceptance Prompt

## 六大核心模块统一集成、科学能力补强与最终验收 Claude Code Prompt

---

## 0. 你的角色

你现在是本仓库的首席软件架构师、Synthetic Biology Agent 工程负责人、计算生物学实现者和最终验收负责人。

你将接手一个已经完成六个核心模块 V1 后端实现的项目。你的任务不是重写六个模块，也不是继续增加概念性 Schema，而是：

> 审计仓库真实状态，将六个现有模块组装为一个统一、可恢复、可审计、由人类治理的 DBTL Engineering System；补齐明确缺失的科学能力和模型闭环；最后用真实运行、科学 Golden Set 与端到端证据完成验收。

最终产品定位固定为：

> **Persistent, Traceable, Human-Governed DBTL Engineering System V1**

Problem 6 的能力边界固定为：

> **Model-integrated Virtual Cell Agent foundation**

不得将当前系统称为完整的 E. coli Virtual Cell、Digital Twin、Autonomous Scientist 或能够准确预测任意基因改造结果的系统。

---

# 1. 当前系统背景

仓库中已经存在六个相对成熟的模块：

1. Problem 1：Workflow Engine；
2. Problem 2：Persistent Memory & Iterative DBTL；
3. Problem 3：Bottleneck Diagnosis；
4. Problem 4：Engineering Design；
5. Problem 5：Scientific Critic / Evaluation；
6. Problem 6：Predictive Simulation & Virtual Cell Integration。

当前系统已经具备较好的：

- 状态机；
- 持久化；
- 版本化；
- Event Ledger；
- Human Gate；
- Memory；
- Diagnosis；
- Engineering Design；
- Scientific Evaluation；
- core FBA；
- Simulation 数据契约；
- 审计与恢复能力。

但仍有三类系统级缺口：

1. Problem 1 尚未真正成为 Problem 3–6 的唯一顶层调度者；
2. Problem 3–5 的科学生成和审查仍主要依赖确定性规则与小型知识库；
3. Problem 6 仍主要是 core FBA 的可信闭环，模型覆盖、多组学对齐、跨模态一致性、场景组合和真实校准尚不完整。

本任务必须在保留现有成果的前提下解决这些缺口。

---

# 2. 最高优先级原则

以下原则优先级高于任何局部实现便利。

## 2.1 Repository Truth First

在修改任何代码前，必须先检查：

- 仓库目录结构；
- README、架构文档与 AGENTS.md；
- 当前分支和工作区状态；
- 六个模块的真实实现路径；
- 数据库模型与 migration；
- API；
- 状态机；
- Controller / Service / Adapter；
- 测试；
- fixture；
- 运行入口；
- 环境配置；
- 当前依赖；
- 已知 unavailable capability；
- 前六次实现产生的报告；
- 是否存在未提交的用户改动。

不得仅依据文件名、实施报告或 Prompt 宣称某项能力已实现。

每项完成结论必须至少绑定以下一种可验证证据：

- 真实代码路径；
- 可运行测试；
- API 调用结果；
- 数据库记录；
- Event Ledger；
- 模型运行工件；
- E2E 运行记录；
- 外部依赖的真实健康检查。

## 2.2 Integrate Before Expanding

必须优先完成统一控制平面，再补科学能力。

固定实施顺序：

```text
Phase A：Repository Truth Audit
Phase B：Unified Scientific Workflow Orchestrator
Phase C：Scientific Capability Adapters
Phase D：Virtual Cell Missing Requirements
Phase E：Scientific Golden Set and Final Acceptance
```

Phase B 未完成前，不得优先：

- 美化前端；
- 增加 Reviewer 人设；
- 增加更多平行状态机；
- 增加大量空 Schema；
- 扩写知识库数量；
- 新建与统一调度无关的实验性模块。

## 2.3 No Fake Completion

以下情况不得标记为 completed：

- 只有 interface，没有实现；
- 只有 Schema，没有生产调用；
- 只有 mock/fixture，没有真实执行路径；
- 只有单元测试，没有模块集成；
- 只有固定答案的 E2E；
- 只有 LLM 文本，没有结构化验证；
- 只有配置项，没有健康检查；
- 只有 adapter 名称，没有真实底层模型；
- 只有 benchmark 字段，没有真实 observation；
- 只有文献引用字符串，没有检索来源；
- 只有 UI 页面，没有后端数据链路。

状态必须诚实使用：

```text
implemented
partially_implemented
scaffold_only
unavailable
blocked_by_dependency
out_of_scope
not_verified
```

## 2.4 LLM Is Not Evidence or Simulator

LLM 可以：

- 生成候选假设；
- 生成候选工程策略；
- 帮助结构化文献内容；
- 草拟 critic findings；
- 提供自然语言解释；
- 帮助选择下一步工具。

LLM 不可以：

- 伪造 DOI；
- 伪造实验观察；
- 伪造模拟数值；
- 伪造 p-value；
- 伪造模型运行成功；
- 把语言概率当作实验成功率；
- 把自身输出作为 evidence；
- 绕过 deterministic rules；
- 绕过 Model Compatibility Check；
- 绕过 Human Gate；
- 直接批准自己的设计。

## 2.5 Preserve Deterministic Safety

现有确定性规则不得删除。

正确能力链固定为：

```text
LLM candidate generation
→ schema validation
→ deterministic biological and engineering rules
→ evidence grounding
→ model/tool verification
→ independent scientific critic
→ human review
```

LLM adapter 失败时必须：

1. 保存失败原因；
2. 不产生半结构化 Markdown 冒充结果；
3. 回退到 deterministic generator；
4. 标记 generation mode；
5. 保留 audit event。

## 2.6 Preserve Existing Data and Interfaces

不得：

- 删除现有数据库；
- 覆盖历史版本；
- 重置事件账本；
- 破坏已通过测试的接口；
- 随意重命名正式 ID；
- 把不可变对象改成原地更新；
- 创建第二套 Memory；
- 创建第二套 Event Ledger；
- 为统一集成复制模块内部对象。

若必须修改接口：

- 说明原因；
- 提供兼容层或 migration；
- 增加 regression test；
- 更新调用方；
- 保留历史数据可读取性。

---

# 3. 本次任务的唯一目标架构

目标系统应形成如下闭环：

```text
User / PI Goal
→ Unified Scientific Workflow Orchestrator
→ Problem 3 Diagnosis
→ Problem 4 Engineering Design
→ Problem 5 Scientific Evaluation
→ Problem 6 Model Compatibility and Simulation
→ Human Gate
→ Build / Test / Experiment
→ Problem 2 Observation and Memory
→ Belief / Design / Model Reliability Update
→ Next DBTL Iteration or Stop
```

Problem 2 是唯一持久化科学记忆底座。

Problem 1 的统一 Orchestrator 是唯一顶层流程控制者。

Problem 3–6 可以保留内部状态机，但只能作为被调度的模块工作流，不得继续充当互不隶属的顶层流程。

---

# 4. Workstream 1：Unified Scientific Workflow Control Plane

## 4.1 目标

新增或重构出唯一的：

```text
UnifiedScientificWorkflowOrchestrator
```

它必须统一决定：

- 何时进入 Diagnosis；
- 何时继续诊断实验；
- 何时允许 Diagnosis Handoff；
- 何时进入 Engineering Design；
- 何时必须进入 Scientific Evaluation；
- 何时允许 Simulation；
- 何时 Simulation 不适用；
- 何时进入 Human Gate；
- 何时等待实验；
- 何时写回 Observation；
- 何时返回 Diagnosis；
- 何时 redesign；
- 何时开始下一轮 DBTL；
- 何时停止；
- 何时因安全、伦理、证据或权限被阻断。

## 4.2 禁止新增第七套平行状态机

必须复用现有：

- WorkflowController；
- IterativeLoopController；
- DiagnosisLoopController；
- EngineeringDesignLoopController；
- EvaluationLoopController；
- Simulation workflow/state。

允许新增顶层 orchestration state，但其职责仅限：

- 保存当前 DBTL iteration；
- 保存当前顶层 phase；
- 保存各模块 run/version 引用；
- 保存 gate decision；
- 保存 pause/resume 信息；
- 保存 failure/recovery 信息；
- 保存统一 audit correlation ID。

不得在顶层对象中复制：

- 完整 Hypothesis；
- 完整 Design；
- 完整 Evaluation；
- 完整 SimulationResult；
- 完整 Observation；
- 模块内部状态历史。

必须使用正式 ID 和 version 引用。

## 4.3 顶层状态建议

根据现有实现适配，不要机械照抄名称，但语义至少覆盖：

```yaml
UnifiedWorkflowRun:
  workflow_run_id:
  project_id:
  objective_id:
  dbtl_iteration_id:
  status:
  current_phase:
  current_module:
  diagnosis_run_ref:
  diagnosis_handoff_ref:
  design_version_ref:
  evaluation_run_ref:
  simulation_campaign_ref:
  experiment_plan_ref:
  experiment_run_ref:
  observation_set_ref:
  active_gate_ref:
  pause_reason:
  blocked_reason:
  resume_token_or_checkpoint_ref:
  correlation_id:
  created_at:
  updated_at:
  version:
```

顶层 phase 至少表达：

```text
INTAKE
CONTEXT_VALIDATION
DIAGNOSIS
DESIGN
EVALUATION
SIMULATION
HUMAN_REVIEW
WAITING_FOR_EXPERIMENT
OBSERVATION_INGESTION
LEARNING
REDESIGN
COMPLETED
BLOCKED
FAILED
```

是否进入 `SIMULATION` 必须由模型适用性决定，不得强制所有设计都模拟。

## 4.4 正式模块契约

每个模块必须暴露统一调用契约，至少包含：

```python
class ScientificModuleContract(Protocol):
    def start(self, request, context) -> ModuleRunRef: ...
    def get_status(self, run_id) -> ModuleRunStatus: ...
    def resume(self, run_id, input_ref, expected_version) -> ModuleRunRef: ...
    def cancel(self, run_id, reason, actor) -> ModuleRunRef: ...
    def get_handoff(self, run_id) -> ModuleHandoff: ...
```

实际实现可以适配现有 Service/API，不要求为接口一致而重写模块。

每个 handoff 必须包含：

```yaml
ModuleHandoff:
  handoff_id:
  source_module:
  source_run_id:
  source_version:
  target_module:
  payload_refs:
  preconditions:
  unresolved_items:
  warnings:
  confidence_status:
  gate_decision_ref:
  created_at:
```

## 4.5 统一 Gate

建立统一 Gate Registry 或等价机制，至少整合：

- Context Completeness Gate；
- Data Quality Gate；
- Diagnosis Handoff Gate；
- Engineering Feasibility Gate；
- Scientific Evaluation Gate；
- Model Applicability Gate；
- Simulation Evidence Gate；
- Safety / Ethics Gate；
- Human Approval Gate；
- Observation QC Gate；
- Redesign Gate；
- Stop Gate。

Gate 输出必须结构化：

```yaml
GateDecision:
  gate_decision_id:
  gate_type:
  workflow_run_id:
  evaluated_refs:
  decision:
  blocking_findings:
  non_blocking_findings:
  required_actions:
  evidence_refs:
  rule_versions:
  reviewer_refs:
  actor:
  timestamp:
```

`decision` 至少支持：

```text
pass
pass_with_conditions
revise
wait_for_data
human_review_required
blocked
not_applicable
```

任何模块不得通过修改字符串状态绕过 Gate。

## 4.6 Pause / Resume / Recovery

必须验证：

- 进程重启后恢复；
- `WAITING_FOR_EXPERIMENT` 跨进程恢复；
- Human Gate 恢复；
- LLM 调用失败恢复；
- 模型运行超时恢复；
- stale version 拒绝；
- 重复 resume 幂等；
- 重复 observation 上传幂等；
- 模块完成但顶层未更新时的 reconciliation；
- Event Ledger 可重建顶层状态。

## 4.7 Stale Version 与并发

所有跨模块写操作必须携带：

- `expected_version`；
- `actor`；
- `correlation_id`；
- `idempotency_key`。

版本不一致必须明确失败，不得 last-write-wins。

## 4.8 统一 Audit Trail

每次顶层决策必须记录：

- 谁触发；
- 输入引用；
- 使用的规则版本；
- 使用的模型和版本；
- 使用的 evidence；
- Gate 结果；
- 状态转换；
- 人工决策；
- 失败与重试；
- 输出版本；
- 是否发生 fallback。

不得只依赖普通应用日志作为科学审计记录。

## 4.9 Workstream 1 验收

至少完成以下真实 E2E：

```text
创建项目
→ 提交目标和上下文
→ Diagnosis run
→ Diagnosis Handoff
→ DesignVersion
→ Scientific Evaluation
→ Model Compatibility Check
→ 可运行则 Simulation；不可运行则正式 not_applicable/unavailable
→ Human Gate
→ Experiment Plan
→ WAITING_FOR_EXPERIMENT
→ 重启进程
→ 上传 Observation
→ QC
→ Learning / Residual
→ Redesign 或 Stop
```

要求：

- 只能由顶层 Orchestrator 推进；
- 模块内部状态机仍然生效；
- 每一步都可由 ID/version 追踪；
- 至少一次 pause/resume；
- 至少一次 stale-version rejection；
- 至少一次 Human Gate；
- 至少一次返回 Diagnosis 或 redesign；
- 数据库与事件账本一致。

---

# 5. Workstream 2：Scientific Generation, Evidence and Reviewer Upgrade

## 5.1 固定能力关系

科学能力升级必须采用：

```text
deterministic baseline
+
LLM structured candidate generation
+
real evidence retrieval
+
condition-aware evidence matching
+
independent scientific review
```

不得将 deterministic baseline 替换为 LLM。

## 5.2 LLM Adapter 通用契约

为以下能力建立可替换 adapter：

- Problem 3：Hypothesis Generator；
- Problem 4：Strategy Draft Generator；
- Problem 5：Scientific Critic。

统一记录：

```yaml
LLMGenerationRecord:
  generation_id:
  task_type:
  provider:
  model_id:
  model_version_or_snapshot:
  prompt_template_id:
  prompt_template_version:
  input_refs:
  output_schema_version:
  raw_output_artifact_ref:
  parsed_output_ref:
  validation_status:
  retry_count:
  fallback_used:
  shared_model_risk:
  token_usage_if_available:
  latency:
  created_at:
```

要求：

- 使用 structured output；
- 使用严格 Schema；
- 禁止将解析失败的长 Markdown 作为正式对象；
- Schema 失败可修复重试，但必须有最大次数；
- 超过最大次数后进入 deterministic fallback；
- 每次生成保留 provenance；
- LLM 输出默认是 `candidate` 或 `draft`；
- 未经 evidence grounding 和 rule validation 不得进入 approved。

## 5.3 Problem 3 Hypothesis Generator

LLM 生成的每个候选假设至少包含：

```yaml
HypothesisDraft:
  statement:
  mechanism_class:
  causal_chain:
  expected_observations:
  contradicting_observations:
  discriminating_tests:
  required_evidence_queries:
  assumptions:
  unsupported_claims:
```

随后必须经过：

1. Schema validation；
2. 与 deterministic hypotheses 合并；
3. 语义去重但保留来源；
4. 生物实体标准化；
5. 条件与底盘校验；
6. evidence retrieval；
7. EvidenceLink 建立；
8. critic / evaluator；
9. belief 状态更新。

LLM 不得直接：

- rule out hypothesis；
- 宣称因果成立；
- 推荐跳过诊断；
- 将目标偏好作为诊断证据；
- 生成不存在的数据。

## 5.4 Problem 4 Strategy Draft Generator

LLM 只能生成工程策略草案。

每个草案至少包含：

```yaml
StrategyDraft:
  biological_intent:
  intervention_class:
  target_entities:
  engineering_implementation_options:
  expected_mechanism:
  expected_benefit:
  tradeoffs:
  dependencies:
  feasibility_questions:
  safety_questions:
  evidence_queries:
  validation_plan_draft:
  assumptions:
```

之后必须经过：

- host/strain entity check；
- essentiality check；
- intervention conflict check；
- genetic feasibility；
- constructability；
- evidence grounding；
- historical failure lookup；
- model-mapping feasibility；
- Scientific Critic；
- Human Gate。

不得把 LLM 生成的具体 promoter、RBS、mutation、gene deletion 直接视为可执行设计。

## 5.5 Problem 5 Independent Scientific Critic

Scientific Critic 必须独立读取：

- 正式 DesignVersion；
- 正式 Diagnosis Handoff；
- Evidence Graph；
- Constraint；
- SimulationResult（若存在）；
- Model Applicability Report；
- 历史 FailureCase；
- 当前项目 Observation。

Critic 不得读取 Designer 的 hidden chain-of-thought。

若 Designer 与 Critic 使用同一模型或同一模型家族，必须记录：

```yaml
shared_model_risk: true
```

这不等于完全独立审查，最终报告必须诚实说明。

Critic 输出至少包括：

```yaml
ScientificCritique:
  critical_findings:
  major_findings:
  minor_findings:
  unsupported_claims:
  evidence_gaps:
  biological_risks:
  engineering_risks:
  model_use_risks:
  validation_gaps:
  alternative_explanations:
  required_revisions:
  recommendation:
```

推荐结果至少支持：

```text
approve
approve_with_conditions
revise
reject
insufficient_evidence
human_expert_required
```

LLM Critic 不得自行通过 Human Gate。

## 5.6 Evidence Retrieval Interface

实现正式、可替换的：

```python
class EvidenceRetrievalAdapter(Protocol):
    def search(self, query, filters, pagination) -> EvidenceSearchResult: ...
    def fetch(self, source_id) -> EvidenceDocument: ...
    def extract_claims(self, document_ref, schema_version) -> list[EvidenceClaimDraft]: ...
    def health_check(self) -> AdapterHealth: ...
```

适配器可以连接：

- 文献数据库；
- 项目本地 DDR；
- EcoCyc / BioCyc；
- UniProt；
- strain/genome database；
- 已批准的内部知识库。

但只能接入仓库和运行环境中真实可用的来源。

若没有网络、凭证或许可：

- 实现 interface 和正式 unavailable 状态；
- 保留现有本地 evidence；
- 不得伪造检索结果；
- 不得把 LLM 记忆当作检索。

## 5.7 Evidence 数据要求

正式 EvidenceItem 至少保存：

```yaml
EvidenceItem:
  evidence_id:
  source_type:
  title:
  authors:
  publication_year:
  journal_or_repository:
  doi_or_accession:
  source_url_or_local_ref:
  exact_location:
  organism:
  strain:
  genotype:
  condition:
  medium:
  temperature:
  growth_phase:
  timepoint:
  intervention:
  comparator:
  measurement:
  direction:
  effect_size_if_reported:
  uncertainty_if_reported:
  evidence_quality:
  extraction_method:
  extraction_status:
  provenance:
```

文献未提供的字段必须为 `unknown` 或 `not_reported`，不得补造。

## 5.8 Evidence Condition Matching

建立正式条件匹配：

```yaml
EvidenceMatchReport:
  query_context_ref:
  evidence_id:
  organism_match:
  strain_match:
  genotype_match:
  medium_match:
  condition_match:
  timepoint_match:
  intervention_match:
  measurement_match:
  directness:
  transfer_risks:
  overall_match_status:
  downgrade_reasons:
```

至少区分：

```text
direct_match
close_match
partial_match
cross_strain
cross_species
condition_mismatch
endpoint_mismatch
insufficient_metadata
not_applicable
```

跨菌株、跨物种、跨培养条件证据必须自动降级，不得静默视为直接证据。

## 5.9 Workstream 2 验收

至少验证：

- structured generation 成功；
- structured generation 解析失败；
- LLM provider unavailable；
- deterministic fallback；
- 幻觉 DOI 被拒绝；
- cross-strain evidence 降级；
- condition mismatch 降级；
- evidence 不足时不批准；
- Critic 发现错误设计；
- Critic 与 Designer 同模型时记录风险；
- Critic 不读取 hidden reasoning；
- LLM 输出不进入 evidence；
- 不存在真实 retrieval adapter 时返回 unavailable。

---

# 6. Workstream 3：Model and Multi-omics Capability Completion

## 6.1 一期能力边界

本阶段不是建立完整 Virtual Cell。

目标是补齐：

- `CrossModalConsistencyReport`；
- 多组学登记、对齐与冲突解释；
- multi-scenario simulation；
- combination intervention；
- larger E. coli GEM adapter（仅在真实模型资产可获得时）；
- stochastic replicate contract test；
- vEcoli runtime feasibility audit；
- endpoint-specific benchmark；
- prediction calibration 的真实数据门槛。

## 6.2 Cell State 与 Omics Observation

确认并补齐：

```yaml
OmicsObservation:
  observation_id:
  sample_id:
  strain:
  genotype:
  condition:
  medium:
  timepoint:
  modality:
  measurement_platform:
  entity_namespace:
  values_ref:
  units:
  normalization:
  batch:
  qc_status:
  missingness:
  provenance:
  status:
```

每个状态字段必须能区分：

```text
observed
model_inferred
literature_derived
assumed
unknown
```

不得把 inferred value 覆盖 observed value。

## 6.3 Entity / Sample / Condition / Time 对齐

必须建立或复用：

- gene ID mapping；
- protein ID mapping；
- reaction ID mapping；
- metabolite namespace mapping；
- strain/genome version；
- sample identity；
- condition identity；
- timepoint tolerance；
- batch；
- unit；
- normalization；
- missing modality。

对齐失败必须产生正式 finding，不得靠字符串近似静默合并。

## 6.4 CrossModalConsistencyReport

正式实现：

```yaml
CrossModalConsistencyReport:
  report_id:
  project_id:
  design_version_ref:
  target_entity:
  aligned_observation_refs:
  transcript_change:
  protein_change:
  metabolite_change:
  flux_change:
  phenotype_change:
  agreement_status:
  inconsistency_classes:
  data_quality_findings:
  time_alignment_findings:
  alternative_explanations:
  discriminating_measurements:
  unsupported_conclusions:
  created_at:
```

`agreement_status` 至少支持：

```text
consistent
partially_consistent
discordant
temporally_unresolved
insufficient_modalities
not_comparable
```

`inconsistency_classes` 至少考虑：

- transcript–protein discordance；
- protein–flux discordance；
- flux–phenotype discordance；
- timepoint mismatch；
- condition mismatch；
- batch effect；
- missingness；
- measurement sensitivity；
- entity mapping ambiguity；
- compensatory regulation；
- resource limitation；
- post-transcriptional regulation；
- model–experiment mismatch。

示例：

```text
trpE RNA ↑，TrpE protein 未增加
```

不得直接解释为“trpE overexpression 无效”。

必须保留替代解释，例如：

- 翻译受限；
- 蛋白降解；
- 定量缺失；
- 检测灵敏度不足；
- 时间点不匹配；
- 构建设计或基因型错误。

## 6.5 Multi-scenario Simulation

在模型能力允许时，统一场景：

```text
S0：baseline
S1：intervention A
S2：intervention B
S3：combination A+B
S4：stress / robustness condition
```

场景比较必须保证：

- 同模型和版本；
- 同 baseline state；
- 同环境定义；
- 同 objective；
- 同输出单位；
- 同求解配置；
- 仅改变声明的干预或条件；
- 每个场景保存独立 run ID；
- 支持部分失败；
- 不因 S4 不支持而伪造结果。

输出按模型能力比较：

- growth；
- substrate uptake；
- product flux/titer（仅模型真实支持时）；
- yield；
- productivity（仅动态模型真实支持时）；
- by-products；
- energy/resource burden（仅支持时）；
- robustness；
- feasibility；
- solver/model status。

## 6.6 Combination Intervention

组合干预必须：

- 保留各单项干预；
- 检查冲突；
- 明确组合顺序；
- 区分 biological implementation 与 model approximation；
- 检查模型映射覆盖；
- 不允许把单项结果简单相加；
- 不允许用 LLM 推断 synergy 数值。

## 6.7 Larger E. coli GEM Adapter

优先检查仓库与环境是否已有：

- iML1515；
- iJO1366；
- 其他明确版本的 E. coli GEM。

只有在模型文件、许可、依赖和求解器真实可用时才实现。

必须记录：

```yaml
ModelManifest:
  model_id:
  model_version:
  organism:
  strain:
  source:
  license:
  model_file_hash:
  solver:
  supported_interventions:
  supported_endpoints:
  validation_domain:
  known_limitations:
```

必须至少验证：

- 模型可加载；
- baseline 可求解；
- objective 明确；
- exchange bounds 明确；
- gene/reaction mapping；
- 单基因干预；
- combination intervention；
- result normalization；
- infeasible 状态；
- reproducibility。

不得删除或重复实现现有 core FBA adapter。

## 6.8 vEcoli Runtime Feasibility Audit

对 vEcoli 做真实可行性审计：

- 是否存在源码；
- commit/version；
- Python/系统依赖；
- knowledge base；
- workflow engine；
- 计算资源；
- 运行时间；
- 输入配置；
- K-12 strain/model coverage；
- perturbation mapping；
- output endpoints；
- stochastic seed；
- replicate；
- artifact；
- license；
- CI 可行性。

输出：

```yaml
VEcoliAvailabilityAudit:
  status:
  source_version:
  environment_status:
  knowledge_base_status:
  minimal_run_status:
  perturbation_support:
  output_support:
  resource_estimate:
  blockers:
  verified_evidence:
  recommended_next_step:
```

允许的结论：

```text
available_and_verified
available_not_run
partially_available
blocked_by_environment
blocked_by_assets
unsupported_for_requested_endpoint
unavailable
```

若无法运行，必须保留正式 unavailable/blocked 状态，不得模拟 vEcoli 输出。

## 6.9 Stochastic Replicate Contract

对支持随机重复的 adapter 统一要求：

```yaml
SimulationReplicate:
  replicate_id:
  run_id:
  seed:
  model_version:
  config_hash:
  status:
  trajectory_ref:
  summary_ref:
  failure_reason:
```

测试至少覆盖：

- 同 seed 可复现；
- 不同 seed 被分别记录；
- replicate 部分失败；
- replicate 数不足时不声称稳定；
- variability 仅标记为 replicate variability；
- 不把 replicate variability 冒充完整预测不确定性。

对于确定性 FBA，应明确：

```text
stochastic_replicates_not_applicable
```

不得伪造随机重复。

## 6.10 Endpoint-specific Model Benchmark Memory

实现：

```yaml
ModelBenchmarkRecord:
  benchmark_record_id:
  model_id:
  model_version:
  endpoint:
  organism:
  strain:
  condition:
  intervention_class:
  evaluation_type:
  dataset_ref:
  train_or_parameterization_overlap:
  sample_count:
  metrics:
  uncertainty:
  applicability_scope:
  failure_modes:
  provenance:
  reviewer_status:
  created_at:
```

`evaluation_type` 至少区分：

```text
reproduction
held_out_validation
prospective_validation
intervention_validation
external_report
```

规则：

- 不得为模型生成脱离任务场景的“总分”；
- 不得把 reproduction 当成 prediction；
- 存在训练/参数化数据重叠时必须标记；
- benchmark 只能辅助 Model Router；
- benchmark 不得覆盖 compatibility failure；
- 不同 endpoint 不得合并；
- 不同 strain/condition 不得静默合并；
- 小样本不得产生伪精确 reliability；
- 所有指标必须来自真实 prediction–observation pairs。

## 6.11 Prediction Calibration Loop

建立：

```text
Prediction
→ matched Observation
→ PredictionResidual
→ eligible calibration cohort
→ PredictionCalibrationProfile
→ prospective validation
```

数据结构：

```yaml
PredictionCalibrationProfile:
  calibration_profile_id:
  model_id:
  model_version:
  endpoint:
  organism:
  strain_scope:
  condition_scope:
  intervention_class:
  cohort_query:
  included_pair_refs:
  excluded_pair_refs:
  exclusion_reasons:
  sample_count:
  calibration_method:
  metrics:
  interval_coverage:
  domain_scope:
  validity_window:
  leakage_check:
  qc_status:
  reviewer_status:
  confidence_status:
  created_at:
```

校准资格门槛必须检查：

- Prediction 在 Observation 之前产生；
- prediction 未被 observation 反向修改；
- endpoint 一致；
- unit 一致；
- strain/condition 匹配；
- intervention class 匹配；
- Observation QC 通过；
- 无明显数据泄漏；
- 样本量达到方法门槛；
- profile 未过期；
- model version 一致；
- 适用域一致。

样本不足时只能输出：

```text
qualitative
insufficient_data
uncalibrated
```

不得输出 `confidence=0.65` 等伪精确概率。

校准结果不得覆盖原始模拟结果，只能作为附加可靠性信息。

## 6.12 Prediction Residual

确保：

```yaml
PredictionResidual:
  residual_id:
  prediction_id:
  observation_id:
  endpoint:
  predicted_value:
  predicted_unit:
  observed_value:
  observed_unit:
  residual:
  measurement_uncertainty:
  prediction_uncertainty:
  mismatch_status:
  possible_causes:
  update_action:
  review_status:
```

Prediction–Observation 不可匹配时不得强制计算 residual。

## 6.13 Model Update Governance

更新分级：

```text
Level 1：记录 residual、FailureCase 和项目经验
Level 2：更新输入状态、条件或 belief
Level 3：模型参数校准
Level 4：模型结构修改
Level 5：重新训练数据驱动模型
```

V1 可自动准备 Level 1–2 proposal，但正式写入仍必须版本化。

Level 3–5 必须：

- 数据量检查；
- 可识别性或方法适用性检查；
- 单独版本；
- 训练/验证划分；
- rollback；
- Human Gate；
- 独立评审。

不得因单个 residual 自动改模型参数。

---

# 7. Workstream 4：Scientific Golden Set

## 7.1 Golden Set 不是 fixture

建立：

```text
Expert-reviewed Scientific Golden Set
```

Golden Set 只能用于：

- 科学能力验收；
- 回归评估；
- 发现遗漏；
- 比较版本。

不得：

- 将预期答案硬编码进生产逻辑；
- 用案例 ID 触发固定输出；
- 将 Golden Set 泄漏进 prompt 作为答案；
- 用 Golden Set 同时做开发、调参和最终盲测却不标记；
- 用单元测试通过替代专家审阅。

## 7.2 案例组成

目标至少 20 个案例：

- 5 个 L-tryptophan 案例；
- 3 个其他产品案例，例如 lysine、isoprenoid、2,3-BDO；
- 3 个证据不足案例；
- 3 个错误设计或危险设计；
- 3 个模型域外案例；
- 3 个实验结果与预测冲突案例。

如果当前没有专家确认或可靠材料，不得伪造 `expert_reviewed=true`。

此时应：

1. 建立 Golden Set schema；
2. 建立 candidate cases；
3. 标记 `review_status=pending_expert_review`；
4. 提供人工评审模板；
5. 仅将真正审核过的案例纳入正式评分。

## 7.3 Golden Case Schema

```yaml
ScientificGoldenCase:
  case_id:
  title:
  case_type:
  organism:
  strain:
  condition:
  objective:
  input_observations:
  available_evidence_refs:
  hidden_evaluation_annotations_ref:
  expected_mechanism_categories:
  acceptable_competing_hypotheses:
  unacceptable_claims:
  acceptable_strategy_classes:
  clearly_wrong_strategies:
  required_critic_findings:
  model_applicability_expectation:
  expected_workflow_branch:
  validation_plan_requirements:
  expert_reviewers:
  review_status:
  version:
```

评估时系统不得看到：

- `hidden_evaluation_annotations_ref`；
- 明显错误策略答案；
- required critic findings；
- expected workflow branch。

## 7.4 每个案例的人工预期

每个正式案例至少由人类确认：

- 不应遗漏的机制类别；
- 合理的 competing hypotheses；
- 不可接受的因果结论；
- 可接受策略范围；
- 明显错误或危险策略；
- 关键 evidence；
- 必须出现的 critic findings；
- 最低 validation plan；
- 是否应模拟；
- 应进入哪个 workflow branch；
- 哪些地方必须返回 unknown / unsupported。

## 7.5 评价指标

至少实现：

```text
hypothesis_category_recall
critical_hypothesis_recall
unsupported_claim_rate
hallucinated_reference_rate
strategy_diversity
strategy_validity_rate
evidence_traceability
condition_match_accuracy
critical_finding_recall
false_approval_rate
unsafe_design_miss_rate
inappropriate_model_use_rate
unsupported_numeric_prediction_rate
workflow_branch_accuracy
validation_plan_coverage
human_expert_rating
```

指标必须说明：

- 定义；
- 分母；
- 计算方法；
- 缺失数据处理；
- 适用案例；
- 阈值来源；
- 是否需要人工打分。

不得制造没有依据的“95% 科学准确率”。

## 7.6 建议最低验收门槛

门槛最终应由项目负责人确认。代码中不得把以下建议值伪装为已经批准的标准。

建议候选：

- hallucinated reference rate = 0；
- unsupported numeric prediction rate = 0；
- unsafe design false approval = 0；
- inappropriate model-use rate = 0；
- evidence traceability = 100% for formal claims；
- critical finding recall ≥ 90%；
- false approval rate ≤ 5%；
- workflow branch accuracy ≥ 90%；
- 所有正式 Golden Case 必须有专家审核记录。

若正式案例数量不足，报告置信区间和限制，不得夸大。

---

# 8. API 与用户输出要求

## 8.1 API

在不破坏现有 API 的前提下，至少提供或适配：

- 创建统一 workflow run；
- 查询统一状态；
- resume；
- 提交 Human Gate decision；
- 查询 module handoff；
- 查询 audit trail；
- 查询 evidence match；
- 查询 CrossModalConsistencyReport；
- 创建 simulation campaign；
- 查询 scenario comparison；
- 查询 benchmark records；
- 查询 calibration profile；
- 运行 Golden Set evaluation；
- 查询 acceptance report。

## 8.2 Wet Lab 可读输出

底层可以保存复杂模型术语，但面向实验用户必须转换成：

```text
当前结论
证据支持程度
模型真实计算了什么
模型没有覆盖什么
最重要的不确定性
下一步应测什么
为什么测
哪个结果支持哪个假设
哪个结果会推翻当前判断
是否需要人工批准
```

不得只向实验用户展示：

- parameter uncertainty；
- domain shift；
- model structure uncertainty；
- solver status；
- raw critic JSON。

必须给出可执行验证计划，但不得自动执行现实实验。

## 8.3 前端优先级

后端集成和 E2E 完成后，才允许做最小必要前端。

前端不是本任务的主要验收标准。

如现有前端存在，只需增加最小页面或面板：

- Unified Workflow Timeline；
- Human Gate Inbox；
- Evidence Trace；
- Model Applicability；
- Scenario Comparison；
- Cross-modal Findings；
- Model Reliability；
- Experiment Validation Plan。

不得因 UI 未美化而阻塞核心后端完成，也不得用 UI 假数据演示未实现能力。

---

# 9. 数据库与 Migration 要求

新增表前先审计现有表，优先复用。

新增或修改必须：

- migration 可重复执行；
- 旧数据可读取；
- 外键明确；
- version 明确；
- append-only 对象不被覆盖；
- timestamp 和 actor 完整；
- JSON 字段有 schema version；
- ID 不依赖展示名称；
- 测试 upgrade path；
- 测试空库；
- 测试已有 V1 数据库；
- 支持 rollback 或提供明确不可逆说明。

禁止为了覆盖 Prompt 给每个 Schema 单独建表而不考虑查询与生命周期。

---

# 10. 测试策略

## 10.1 测试分层

必须区分：

```text
unit
contract
integration
database migration
recovery
scientific invariant
model execution
E2E
golden set
```

## 10.2 必测不变量

至少验证：

1. Problem 1 是唯一顶层控制者；
2. 子模块不能绕过统一 Gate；
3. 顶层状态不复制模块内部对象；
4. handoff 使用正式 ID/version；
5. stale version 被拒绝；
6. pause/resume 可跨进程；
7. event ledger 与 materialized state 一致；
8. LLM 输出不是 evidence；
9. LLM 失败回退 deterministic；
10. DOI 不得补造；
11. evidence 条件不匹配自动降级；
12. cross-species 证据不得直接支持；
13. Critic 不能 self-approve；
14. 同模型 Reviewer 标记 shared risk；
15. Critic 不读 hidden reasoning；
16. 模型不适用时不运行；
17. 数值必须绑定真实运行或 Observation；
18. baseline 和 intervention 条件一致；
19. combination 结果不由单项相加；
20. deterministic FBA 不伪造 stochastic replicate；
21. vEcoli 不可用时正式 unavailable；
22. inferred data 不覆盖 observed data；
23. 跨模态冲突不被强行平均；
24. calibration 只使用合格 prediction–observation pair；
25. 小样本不输出精确 confidence；
26. reproduction 不冒充 predictive validation；
27. benchmark 不绕过 compatibility check；
28. 单一 residual 不自动改模型；
29. Golden Set 答案不进入生产 prompt；
30. 未经专家审核的案例不标记 expert-reviewed；
31. unsafe design 必须触发阻断或人工审查；
32. 技术失败不污染生物学结论；
33. 观察条件差异不被静默合并；
34. 重复上传与重复 resume 幂等；
35. 旧接口仍通过 regression tests。

## 10.3 真实模型测试

对真实 adapter：

- 测试必须实际加载模型；
- 至少一个 baseline；
- 至少一个单干预；
- 至少一个 combination（模型支持时）；
- 保存 model file hash；
- 保存 solver/version；
- 保存原始工件；
- 验证 normalized result 可追溯到 raw result。

不允许只 mock adapter 就宣称模型已接入。

## 10.4 外部依赖测试

真实网络、API 或模型资产可能在 CI 不可用。

必须区分：

- offline deterministic tests；
- adapter contract tests；
- optional live integration tests；
- required release verification。

跳过 live test 必须显示原因，不得作为 pass。

---

# 11. 实施 Phase 与门槛

## Phase A：Repository Truth Audit

交付：

1. `repository_truth_audit.md`；
2. 六模块实现矩阵；
3. Controller/State Machine 拓扑；
4. 数据库与事件账本关系；
5. 现有测试基线；
6. unavailable dependency 清单；
7. 重复 Schema / Controller 清单；
8. 需要保留的兼容接口；
9. 风险排序；
10. 明确实施计划。

门槛：

- 不修改生产逻辑前完成审计；
- 先运行现有测试；
- 记录测试基线；
- 不得依据报告替代代码检查。

## Phase B：Unified Orchestrator

交付：

- 唯一顶层 Orchestrator；
- 正式 module contract/handoff；
- 统一 Gate；
- pause/resume；
- stale version；
- audit；
- E2E 最小 DBTL；
- migration；
- regression tests。

门槛：

- Problem 3–6 均能被顶层调度；
- 不新增平行 Memory；
- 不复制模块对象；
- E2E 跨进程恢复通过；
- 原有测试不回归。

## Phase C：Scientific Capability Adapters

交付：

- Hypothesis LLM adapter；
- Strategy LLM adapter；
- Scientific Critic adapter；
- deterministic fallback；
- evidence retrieval interface；
- 至少一个真实可用 evidence source 或正式 unavailable；
- condition matching；
- provenance；
- scientific invariant tests。

门槛：

- LLM 不作为 evidence；
- structured failure 不泄漏成长 Markdown；
- hallucinated DOI 被拒绝；
- Critic 不能 self-approve；
- evidence 不足会阻断。

## Phase D：Virtual Cell Missing Requirements

交付：

- CrossModalConsistencyReport；
- multi-scenario；
- combination intervention；
- larger GEM audit/adapter；
- vEcoli feasibility audit；
- stochastic contract；
- Model Benchmark Memory；
- Prediction Calibration Loop；
- residual governance；
- model update levels。

门槛：

- 至少一个真实模型 E2E；
- 不支持能力返回正式状态；
- 不输出伪造数值；
- calibration 只使用真实 observation；
- 不声称完整 Virtual Cell。

## Phase E：Golden Set and Final Acceptance

交付：

- Golden Set schema；
- case authoring template；
- ≥20 candidate cases；
- 专家审核状态；
- evaluation runner；
- metric definitions；
- blind annotation separation；
- final acceptance report。

门槛：

- 未审核案例不计入正式通过；
- 无答案泄漏；
- 无硬编码；
- 指标可复现；
- 失败案例保留；
- 不以测试数量替代科学验收。

---

# 12. 最小可信 E2E 案例

至少使用一个：

```text
E. coli K-12
固定培养条件
明确 baseline
一个具有清晰模型映射的单基因干预
真实 GEM/FBA adapter
growth 与模型真实支持的 endpoint
Human Gate
实验计划
模拟 Observation 回填仅限测试环境
Residual
下一轮 workflow decision
```

注意：

测试 fixture 可以模拟 Observation 的上传流程，但不得把 fixture 数值写成真实实验结果，也不得用于生产完成声明。

不得将以下复杂案例作为唯一可信 E2E：

```text
ΔtnaA + trpE feedback-resistant mutation + aroG overexpression
→ 精确预测 Trp 产量增加 20%
```

若底层模型不覆盖：

- 多基因组合；
- 表达强度；
- 蛋白突变；
- 反馈调控；
- 芳香族氨基酸代谢；
- 资源负担；
- 产量标定；

必须返回 partial support / unsupported，不得制造精确预测。

---

# 13. 必须保留的负向 E2E

至少实现：

1. 数据不足 → `wait_for_data`；
2. 证据冲突 → 返回 Diagnosis；
3. 危险或明显错误设计 → blocked/human review；
4. Critic 拒绝设计 → revise；
5. 模型域外 → simulation not applicable；
6. vEcoli 缺失 → unavailable；
7. 模型场景 infeasible → 保存失败，不补数；
8. Observation QC 失败 → 不更新 biological belief；
9. Prediction 与 Observation 冲突 → residual + alternative hypotheses；
10. stale version → 拒绝；
11. 服务重启 → 恢复 WAITING；
12. calibration 样本不足 → qualitative only。

---

# 14. 完成声明格式

最终报告中每个要求必须落入以下矩阵：

| Requirement | Status | Code path | Test evidence | Runtime evidence | Scientific limitation | Follow-up |
|---|---|---|---|---|---|---|

Status 只能使用：

```text
implemented
partially_implemented
scaffold_only
unavailable
blocked_by_dependency
out_of_scope
not_verified
```

不得写模糊表述：

- basically complete；
- production ready；
- fully intelligent；
- scientifically validated；
- virtual cell completed；
- high confidence；
- expert-level；

除非有明确、可复核标准和证据。

---

# 15. 最终交付物

必须交付：

1. Repository Truth Audit；
2. 架构变更说明；
3. 数据库 migration 说明；
4. Unified Orchestrator；
5. 模块契约和 handoff；
6. 统一 Gate；
7. LLM adapters 与 fallback；
8. Evidence Retrieval 与 Condition Matching；
9. Independent Critic；
10. CrossModalConsistencyReport；
11. multi-scenario / combination simulation；
12. larger GEM 与 vEcoli availability 结论；
13. Model Benchmark Memory；
14. Prediction Calibration Loop；
15. Golden Set schema、candidate cases 和审核模板；
16. 测试；
17. 最小可信 E2E；
18. 负向 E2E；
19. Final Acceptance Report；
20. Remaining Limitations；
21. 运行说明；
22. 文件变更清单。

最终报告必须明确：

- 做了什么；
- 没做什么；
- 为什么没做；
- 哪些能力真实运行；
- 哪些只完成接口；
- 哪些依赖外部资产；
- 哪些案例经过专家审核；
- 当前可以做出的产品声明；
- 当前绝对不能做出的产品声明。

---

# 16. 严格禁止项

禁止：

- 重写六个模块；
- 新增平行 Memory；
- 新增平行 Event Ledger；
- 新增平行顶层 Workflow；
- 为覆盖率大量增加空 Schema；
- 重复实现已有 FBA adapter；
- 删除确定性规则；
- 让 LLM 直接批准设计；
- 让 LLM 输出充当 evidence；
- 让 LLM 冒充 simulator；
- 伪造 DOI；
- 伪造 observation；
- 伪造模型运行；
- 伪造校准；
- 伪造专家审核；
- 用 fixture 固定答案硬编码生产逻辑；
- 用测试数量替代科学验收；
- 把 reproduction 当 prediction；
- 把相关性当因果；
- 把 RNA 变化直接等同 protein/flux/phenotype；
- 把蛋白模型分数直接等同产量；
- 把多个模型分数直接平均；
- 把 confidence 当实验成功概率；
- 自动修改模型参数；
- 自动执行湿实验；
- 宣称完整 E. coli Digital Twin；
- 宣称能准确预测任意基因改造后的产量；
- 把前端美化作为首要工作；
- 为了完成 Prompt 修改无关代码；
- 覆盖用户现有未提交改动。

---

# 17. 当前允许的准确产品表述

完成并通过验收后，可使用：

> **Persistent, Traceable, Human-Governed DBTL Engineering System V1**

Problem 6 可使用：

> **Model-integrated Virtual Cell Agent foundation**

更完整的能力表述：

> 该系统能够将合成生物工程目标组织为统一、版本化和可恢复的 DBTL 工作流；将诊断、工程设计、科学审查、模型适用性检查、真实模型运行、实验计划、观察结果和下一轮学习连接为可追溯闭环；在模型或证据不足时明确暴露边界，并要求适当的人类审批。

不得使用：

> 完整 E. coli Digital Twin

> 可准确预测任意基因改造

> 自动完成科学发现

> 已实现全组学因果模型

> 已具备实验成功概率预测

---

# 18. 最终验收问题

完成前必须逐项回答，并附证据：

1. Problem 1 是否成为唯一顶层调度者？
2. Problem 3–6 是否仍保留内部状态机但不再平行控制全局？
3. 是否新增了重复 Memory 或 Event Ledger？
4. 顶层状态是否只保存引用而非复制对象？
5. 所有跨模块调用是否使用 ID/version？
6. 是否支持 pause/resume 和跨进程恢复？
7. stale version 是否真实被拒绝？
8. Human Gate 是否无法被模块绕过？
9. LLM 生成失败是否回退 deterministic？
10. LLM 是否可能进入 evidence？
11. DOI 是否经过来源验证？
12. Evidence 是否按 strain/condition/time/intervention/measurement 匹配？
13. 跨菌株和跨物种证据是否降级？
14. Critic 是否与 Designer 逻辑隔离？
15. Critic 是否能自行批准？
16. shared model risk 是否记录？
17. CrossModalConsistencyReport 是否由真实对齐数据产生？
18. 跨模态冲突是否保留替代解释？
19. 是否至少有一个真实模型 baseline/intervention E2E？
20. 数值是否都可追踪到真实运行或 Observation？
21. baseline 与 intervention 是否严格同条件？
22. combination 是否避免简单相加？
23. larger GEM 是否真实加载？
24. vEcoli 是否真实运行；若没有，是否诚实 unavailable？
25. stochastic replicate 是否只用于真正随机模型？
26. benchmark 是否 endpoint/strain/condition-specific？
27. reproduction 是否与 held-out/prospective validation 分离？
28. calibration 是否只使用合格 prediction–observation pair？
29. 样本不足时是否拒绝精确 confidence？
30. residual 是否会自动改模型？
31. Golden Set 是否与生产 prompt 隔离？
32. candidate cases 中有多少真正经过专家审核？
33. 是否存在 fixture 答案硬编码？
34. 危险设计的 false approval 是否为零？
35. 模型域外案例是否会错误模拟？
36. Observation QC 失败是否污染 belief？
37. 技术失败是否污染科学结论？
38. 原有接口与测试是否回归？
39. Event Ledger 是否能重建关键状态？
40. 完成声明是否逐项附有代码、测试和运行证据？

任一关键问题答案为“不知道”时，不得宣告最终完成，必须标记 `not_verified`。

---

# 19. 立即开始执行

现在开始，不要先输出宏观设计稿并停止。

第一步：

1. 阅读仓库说明与约束；
2. 检查工作区状态；
3. 运行当前测试基线；
4. 定位六个模块；
5. 建立 Repository Truth Audit；
6. 将 Prompt 要求映射到真实代码；
7. 给出最小、分阶段的修改计划；
8. 从 Phase B 的 Unified Orchestrator 开始实施。

执行过程中：

- 小步修改；
- 每个 Phase 独立验证；
- 保留现有能力；
- 不掩盖失败；
- 不因外部依赖缺失而伪造结果；
- 不等待所有理想资产才完成可完成部分；
- 发现 Prompt 与仓库事实冲突时，以仓库事实和科学诚实性为准，并记录冲突；
- 发现需要重写已有稳定模块时，先寻找 adapter/compatibility layer；
- 所有关键设计决定写入实施报告。

最终目标不是让代码“看起来覆盖了六个问题”，而是：

> 让六个现有模块真正成为一个统一、可信、可恢复、可由真实科学案例审查和验收的 Synthetic Biology Agent V1。


# Problem 6：Predictive Simulation Loop & Virtual Cell Integration

## Claude Code 完整实现 Prompt（Model Benchmark Memory & Prediction Calibration 优化版）

> **最高实现原则：把 Problem 6 实现为连接工程设计、真实可计算模型、反事实比较、实验验证与模型修正的可信预测闭环，而不是让 LLM 根据生物学常识猜测“改造后提高多少”。任何数值预测都必须来自真实模型运行或已登记实验；任何模型不能覆盖的结论都必须明确返回 `unsupported`、`not_computed`、`out_of_domain` 或 `unknown`。**

你现在需要在现有 Synthetic Biology Agent / agent-harness 仓库中，连续完成 `Problem 6: Predictive Simulation Loop & Virtual Cell Integration` 的 Phase 1–3 实现。

本任务不是新增一个 `simulate()` 空接口，不是只创建 Cell State Schema，不是做一张 Virtual Cell 概念页面，也不是让 LLM 输出 PEP、E4P、产量和生长率的主观变化。你必须先审计真实仓库及已有 Problem 1–5 接口，然后在现有依赖和模型资产允许的范围内，完成一个可运行、可测试、可追溯、可持久化、可降级的最小可信闭环：

```text
Problem 4 DesignVersion
  → Problem 5 Evaluation Decision
  → Baseline Cell State
  → Perturbation Compilation
  → Model Compatibility Check
  → Real Model Execution
  → Counterfactual Comparison
  → Prediction Review
  → Experimental Validation Plan
  → Observation / Residual
  → Problem 2 Memory and Model Update Proposal
  → Next DBTL Iteration
```

请先完整阅读本 Prompt，再开始检查代码。除非遇到第 17 节规定的真实阻断条件，否则不得在审计、Schema、adapter 占位或 Phase 1 后停止等待确认；应自动继续实现、测试、修复并给出最终报告。

---

## 0. 不可偏离的任务定义

前五个问题分别解决：

```text
Problem 1 — Workflow Engine：谁控制流程以及阶段如何转换
Problem 2 — Memory / Iterative DBTL：如何保存版本、证据、决定和实验经验
Problem 3 — Bottleneck Diagnosis：限制机制是什么以及如何更新诊断
Problem 4 — Engineering Design：如何把诊断转为候选工程方案
Problem 5 — Evaluator & Scientific Critic：方案是否可信、值得推进及如何修订
```

Problem 6 必须解决：

> 如何把正式工程方案编译为真实细胞模型可执行的干预，在明确的底盘、环境、时间和初始状态下运行 baseline 与反事实场景，输出带适用域、不确定性和来源的状态转移预测；再用真实实验观测计算残差，形成受治理的认知更新、参数校准或模型结构修订建议。

Problem 6 中必须严格区分：

1. **Virtual Cell Agent**：负责状态管理、干预编译、模型路由、运行编排、结果解释、验证规划和更新治理；
2. **Virtual Cell Model**：真正执行计算的 GEM/FBA、dynamic FBA、kinetic、resource allocation、ME-model、vEcoli、扰动响应模型或局部分子模型；
3. **LLM**：负责结构化编排和受证据约束的解释，不能替代模拟引擎生成数值；
4. **实验观测**：真实测量结果，不能与模型输出或文献知识混写。

目标状态转移：

```text
Current Cell State
+ Engineering Perturbation
+ Environmental Context
+ Executable Model
→ Predicted Future Cell State
→ Experimentally Testable Claims
→ Observation Residual
→ Versioned Update Proposal
```

禁止退化为：

```text
ΔpykF + aroG OE
→ LLM 常识推断
→ “色氨酸提高 25%，生长下降 15%，confidence=0.65”
```

---

## 1. 开发纪律与仓库审计

### 1.1 先审计，后修改

编码前必须以真实文件、符号和运行结果检查：

1. 后端、前端、启动入口、配置和持久化方式；
2. Problem 1 的 workflow state、guard、event 和 orchestration 入口；
3. Problem 2 的 Memory、事件流、版本、artifact 和回写接口；
4. Problem 3 的诊断版本、机制假设和 handoff；
5. Problem 4 的 Candidate、Portfolio、DesignVersion、Build/Test Plan；
6. Problem 5 的 evaluation decision、model request、Human Gate 和 revision task；
7. 当前 model/tool registry、provider、任务队列、超时、重试、日志和 provenance；
8. 是否已有 COBRA、GEM、vEcoli、Docker、子进程或远程计算接入；
9. 测试、类型检查、lint、build 和 E2E 命令；
10. 工作树已有改动，禁止覆盖无关用户修改。

最终报告必须填写：

| 关注项 | 真实文件/符号 | 当前能力 | 缺口 | 本次接入方式 |
|---|---|---|---|---|
| Workflow |  |  |  |  |
| Memory |  |  |  |  |
| Diagnosis |  |  |  |  |
| Design |  |  |  |  |
| Evaluator |  |  |  |  |
| Cell State |  |  |  |  |
| Model Runtime |  |  |  |  |
| Persistence |  |  |  |  |
| API/UI |  |  |  |  |
| Tests |  |  |  |  |

不得假设本文示例类名已存在。若仓库已有等价对象，优先扩展或增加 adapter，避免建立第二套平行架构。

### 1.2 Phase 1–3 必须连续完成

每个 Phase 完成后运行相关测试，修复本次回归并自动继续。外部模型资产缺失时，必须完成正式 adapter contract、capability detection、结构化不可用状态、mock-free contract tests 和接入说明；不得伪造一次“成功运行”。

### 1.3 实现优先级

第一优先级是以下垂直闭环真实跑通：

```text
一个正式 DesignVersion
→ 一个固定 baseline
→ 一个可映射的单基因干预
→ 一个真实可用模型 adapter
→ baseline 与 intervention 两次运行
→ 标准化结果
→ counterfactual comparison
→ prediction review
→ validation plan
→ append-only Memory event
```

若当前没有任何真实模型运行环境，应交付“可证明没有伪造结果”的降级闭环，并优先接通仓库中最可行的 GEM/FBA；不得用大量空壳类冒充 Phase 完成。

---

## 2. 科学与治理不变量

以下规则必须进入服务层验证、workflow guard 或自动化测试，不能只写在 system prompt。

### 2.1 数值来源不变量

所有数值必须具有：

```yaml
value:
unit:
source_type:
source_reference:
model_run_id:
observation_id:
calculation_method:
```

其中 `source_type` 只能是：

```text
experimental_observation
model_output
derived_from_observation
derived_from_model
literature_reported
assumption
unknown
```

LLM 生成的解释不得被登记为 `model_output` 或 `experimental_observation`。

### 2.2 Unknown 不得被自动填充

Cell State 中没有测量或模型输出的字段必须为 `unknown` 或显式缺失。禁止依据常识、相邻组学、embedding 或其他菌株数据自动补成事实。

### 2.3 底盘、环境、时间不可静默合并

同一基因干预在不同 strain、培养基、碳源、供氧、温度、生长阶段和时间点下不得视为同一场景。条件不匹配必须阻断比较或产生 `context_mismatch`。

### 2.4 模型必须先做适用域检查

真实运行前必须检查：

- organism 与 strain；
- model version 与文件 hash；
- 支持的培养条件；
- 支持的 perturbation 类型；
- 输入与输出模态；
- steady-state / dynamic / stochastic 假设；
- calibration 与 validation domain；
- 已知 failure modes。

不兼容时返回 `out_of_domain` 或 `unsupported`，不得强行编译。

### 2.5 高层工程动作与模型动作不可混同

必须保留三层映射：

```text
Biological intent：降低 ptsG 活性
Engineering implementation：CRISPRi / promoter weakening / RBS weakening
Model intervention：表达目标下降或运输反应上界下降
```

模型干预是工程动作的近似时，必须记录 `mapping_assumption` 和 `mapping_uncertainty`。

### 2.6 Baseline 是所有反事实比较的硬前提

每个 intervention 必须与同一模型版本、同一环境、同一初始状态、同一输出口径的 baseline 比较。若随机模型存在，必须使用规定的 replicate 和 seed policy。

### 2.7 多模型结果不得直接平均

不同模型回答的问题、尺度和假设不同。允许并列、分层或按端点路由；除非存在经验证的 ensemble 方法，否则不得把 GEM、vEcoli 和 LLM 结果求平均形成“综合预测”。

### 2.8 不确定性不得伪概率化

没有 calibration benchmark 时，不得输出 `confidence=0.65` 或“成功概率 87%”。应区分：

- stochastic / replicate variability；
- parameter uncertainty；
- initial-state uncertainty；
- model-structure uncertainty；
- intervention-mapping uncertainty；
- domain shift；
- measurement uncertainty。

### 2.9 实验结果不能自动修改生产模型

一次实验可自动新增 observation、residual 和 update proposal，但参数校准、结构修改或模型重训练必须版本化、验证并通过 Human Gate。

### 2.10 模型失败也是正式结果

必须保存 `failed`、`timed_out`、`diverged`、`infeasible`、`unsupported`、`out_of_domain` 和 `not_computed`。不得丢弃失败 run 后只展示成功场景。

---

## 3. 必须实现的核心数据模型

所有对象至少具有：稳定 ID、`schema_version`、对象版本、project/workflow 关联、创建时间、创建者、provenance 和状态。命名可适配现有仓库，语义不得丢失。

### 3.1 `CellStateSnapshot`

```yaml
cell_state_id:
schema_version:
version:
project_id:
chassis:
  organism:
  strain:
  genotype_reference:
environment:
  medium:
  carbon_source:
  oxygenation:
  temperature:
  ph:
  process_mode:
temporal_context:
  timepoint:
  growth_phase:
  prediction_horizon:
molecular_state:
  transcriptome_ref:
  proteome_ref:
  metabolome_ref:
functional_state:
  flux_ref:
  pathway_activity_ref:
  resource_allocation_ref:
physiology:
  growth_rate:
  biomass:
  substrate_uptake:
  product_titer:
  product_yield:
  productivity:
  stress_state:
field_provenance: {}
missing_modalities: []
quality_status:
created_at:
```

每个状态字段必须能标识：`observed`、`model_inferred`、`literature_derived`、`assumed` 或 `unknown`。

### 3.2 `PerturbationSpec`

```yaml
perturbation_id:
design_id:
design_version:
type:
target:
target_namespace:
biological_intent:
operation:
strength:
implementation:
timing:
combination_group:
environmental_changes: []
required_mappings: []
assumptions: []
status:
```

至少支持表示 deletion、knockdown、overexpression、promoter/RBS replacement、point mutation、gene insertion、medium/oxygen/temperature change 和组合干预；adapter 可对不支持项明确拒绝。

### 3.3 `ModelRegistryEntry`

```yaml
model_id:
model_name:
model_type:
model_version:
artifact_uri:
artifact_hash:
adapter_id:
organism:
strains: []
supported_conditions: []
supported_perturbations: []
input_modalities: []
output_modalities: []
mathematical_scope:
training_or_parameterization_domain:
validation_domain:
benchmark_references: []
known_failure_modes: []
runtime_requirements:
availability_status:
```

### 3.4 `CompatibilityReport`

```yaml
compatibility_id:
model_id:
cell_state_id:
perturbation_id:
organism_match:
strain_match:
condition_match:
perturbation_support:
input_completeness:
output_coverage:
domain_status:
blocking_reasons: []
non_blocking_assumptions: []
decision:
  - compatible
  - compatible_with_assumptions
  - out_of_domain
  - unsupported
  - unavailable
```

### 3.5 `CompiledIntervention`

保存从生物设计到模型实体的可审计映射：规范 gene/protein/reaction ID、修改方式、边界值、原始值、新值、映射规则、近似假设、编译日志和失败原因。

### 3.6 `SimulationRun`

```yaml
model_run_id:
model_id:
model_version:
artifact_hash:
adapter_version:
baseline_state_id:
perturbation_ids: []
compiled_intervention_ids: []
simulation_config:
  start_time:
  end_time:
  time_step:
  solver:
  random_seed:
  replicate_index:
inputs_hash:
status:
started_at:
finished_at:
runtime:
stdout_ref:
stderr_ref:
raw_output_ref:
normalized_result_id:
failure_reason:
```

### 3.7 `SimulationResult` 与 `SimulationTrajectory`

```yaml
simulation_result_id:
model_run_id:
initial_state_id:
terminal_state:
trajectory_ref:
endpoints:
  - name:
    value:
    unit:
    statistic:
    source_type: model_output
supported_scales: []
unsupported_scales: []
assumptions: []
warnings: []
```

trajectory 至少可保存时间点、分子计数/丰度、通量、生物量、生长、底物、产物、压力指标及 termination reason；允许模型只覆盖其中一部分。

### 3.8 `CounterfactualComparison`

必须包含 baseline、候选场景、统一比较端点、绝对值、delta、相对变化、单位、replicate summary、缺失项、trade-off 和 robustness。若 denominator 为零、单位不一致或场景条件不同，必须拒绝相对变化计算。

### 3.9 `PredictionUncertainty`

```yaml
endpoint:
estimate:
unit:
interval:
interval_method:
stochastic_variability:
parameter_uncertainty:
initial_state_uncertainty:
model_structure_uncertainty:
intervention_mapping_uncertainty:
domain_shift:
calibration_status:
benchmark_id:
confidence_status:
```

`confidence_status` 仅允许：`calibrated`、`empirical_interval`、`replicate_variability_only`、`qualitative`、`unavailable`。

### 3.10 `OmicsObservation`

```yaml
observation_id:
sample_id:
strain:
condition:
timepoint:
modality:
measurement_platform:
entity_namespace:
values_ref:
normalization:
batch:
replicate:
qc_status:
missingness:
provenance:
```

### 3.11 `PredictionResidual`

```yaml
residual_id:
prediction_id:
observation_id:
endpoint:
predicted_value:
observed_value:
unit:
residual:
relative_error:
measurement_uncertainty:
prediction_uncertainty:
context_match:
mismatch_status:
possible_causes: []
recommended_update_level:
```

### 3.12 `ModelUpdateProposal`

```yaml
proposal_id:
triggering_residual_ids: []
update_level:
  - project_belief
  - input_state
  - parameter_calibration
  - model_structure
  - model_retraining
rationale:
required_data: []
identifiability_status:
validation_plan:
rollback_plan:
human_approval_required:
status:
```

### 3.13 `ModelBenchmarkRecord`

模型登记信息只能说明“理论上支持什么”；Benchmark Memory 必须回答“该模型过去在什么任务、底盘、条件和端点上实际表现如何”。每条记录必须绑定不可变的模型版本、数据集版本和评测协议，禁止只保存一个脱离上下文的综合分数。

```yaml
benchmark_record_id:
model_id:
model_version:
artifact_hash:
adapter_version:
benchmark_dataset_id:
benchmark_dataset_version:
evaluation_protocol_id:
organism:
strain:
condition:
perturbation_class:
endpoint:
unit:
split_type:
  - reproduction
  - validation
  - held_out_test
  - prospective
sample_count:
metrics:
  mae:
  rmse:
  bias:
  rank_correlation:
  interval_coverage:
applicability_scope:
known_failure_modes: []
provenance:
created_at:
status:
  - provisional
  - validated
  - superseded
```

强制规则：不同 endpoint、strain、condition 或 perturbation class 的指标不得静默聚合；reproduction 结果不得冒充 held-out 或 prospective prediction 能力；参与模型参数化或训练的数据必须标明，不得作为独立测试；Router 可使用匹配 benchmark 排序兼容模型，但不能绕过 compatibility check；无匹配记录时返回 `benchmark_unavailable`；旧记录只可 supersede，不可静默覆盖。

### 3.14 `PredictionCalibrationProfile`

Calibration Profile 由一组 context-matched、QC-passed 的预测—实验配对记录计算，用于描述特定模型在特定任务层级的经验可靠性。它不是“实验成功概率”，也不能由 LLM 生成。

```yaml
calibration_profile_id:
model_id:
model_version:
artifact_hash:
endpoint:
organism:
strain_scope: []
condition_scope: []
perturbation_class_scope: []
calibration_method:
calibration_dataset_version:
included_residual_ids: []
excluded_residual_ids: []
sample_count:
minimum_sample_requirement:
metrics:
  bias:
  mae:
  rmse:
  empirical_interval_coverage:
  calibration_error:
reliability_status:
  - insufficient_data
  - qualitative_only
  - provisionally_calibrated
  - calibrated
  - degraded
validity_window:
domain_limits: []
created_at:
approved_by:
supersedes_profile_id:
```

任何预测只能引用与其 model version、endpoint 和适用上下文匹配的 profile。样本数不足、数据泄漏、范围不匹配或 profile 过期时，`confidence_status` 必须降级为 `qualitative`、`replicate_variability_only` 或 `unavailable`。

---

## 4. Model Adapter 与路由层

### 4.1 统一接口必须覆盖完整生命周期

```python
class ModelAdapter(Protocol):
    def capabilities(self) -> ModelCapabilities: ...
    def validate_compatibility(
        self, state, perturbations, request
    ) -> CompatibilityReport: ...
    def compile_interventions(
        self, state, perturbations
    ) -> list[CompiledIntervention]: ...
    def prepare_run(self, request) -> PreparedRun: ...
    def run(self, prepared_run) -> RawModelResult: ...
    def normalize_result(self, raw_result) -> SimulationResult: ...
    def health_check(self) -> AdapterHealth: ...
```

不得只暴露一个接收自然语言字符串的 `simulate(model, intervention)`。

### 4.2 Model Router 必须按问题选择模型

| 科学问题 | 优先模型能力 |
|---|---|
| 稳态代谢通量、理论产率、反应可行性 | GEM/FBA/FVA |
| 培养过程中的时间趋势 | dynamic FBA / kinetic model |
| 表达与资源竞争 | resource allocation / ME-model |
| 多过程耦合和全细胞动态 | vEcoli / whole-cell model |
| 蛋白突变局部性质 | protein/structure model |
| 组学扰动响应 | validated perturbation-response model |

Router 必须返回选择理由、未选择模型的理由和覆盖缺口。没有适配模型时返回 `no_compatible_model`。

### 4.3 vEcoli adapter 的最低要求

若仓库已配置 vEcoli，必须真实检查并实现：

- 底盘和 knowledge base 版本；
- gene ID 到 RNA/protein/process 的映射；
- genotype perturbation 的配置方法；
- 培养基和初始条件；
- stochastic seed 和 replicate；
- run directory 隔离；
- 超时、退出码、日志和输出文件；
- growth、mass、division、关键分子/过程输出的标准化；
- 不支持的产物 titer 不得凭空生成。

若 vEcoli 在当前机器不可运行，必须返回可诊断原因及可复现安装/配置说明，不能伪造 run record。

### 4.4 GEM/FBA adapter 的最低要求

若可获得 E. coli K-12 兼容 GEM，应实现：模型载入、目标函数记录、培养基边界、gene deletion/reaction bound mapping、baseline、intervention、solver 状态、infeasible 状态、flux result、growth/biomass 和 FVA（若范围允许）。必须记录模型来源、版本和 hash。

### 4.5 外部模型不可用时的正式降级

降级结果必须形如：

```yaml
status: not_computed
reason_code: model_runtime_unavailable
missing_requirements: []
scientific_consequence:
allowed_outputs:
  - qualitative_hypothesis
  - model_request
forbidden_outputs:
  - numeric_phenotype_prediction
```

---

## 5. Intervention Compiler

Compiler 必须完成：

1. 规范化 biological target；
2. 检查 target 是否存在于指定 strain；
3. 区分高层意图、工程实现和模型实现；
4. 解析组合干预及执行顺序；
5. 生成 adapter-specific 修改；
6. 检查冲突、重复、方向矛盾和越界值；
7. 记录所有映射假设；
8. 无法可靠映射时停止该场景。

示例：

```yaml
biological_intent: attenuate ptsG
engineering_implementation: CRISPRi
model_implementation:
  type: reaction_bound_scaling
  target_reaction: GLCptspp
  factor: 0.5
mapping_status: approximate
unsupported_inference:
  - CRISPRi efficiency
  - off-target effects
  - expression burden
```

不能把 `factor: 0.5` 表述为实验中表达一定下降 50%。

---

## 6. Counterfactual Simulation Protocol

### 6.1 场景矩阵

至少生成：

```text
S0：baseline
S1：intervention A
S2：intervention B（如存在）
S3：combination（如模型支持）
S4：必要的 negative/control scenario
```

### 6.2 可比性检查

比较前强制验证：model/artifact hash、环境、初始状态、目标函数、时间范围、solver、输出单位和 replicate policy 一致。否则 comparison 状态必须为 `invalid_comparison`。

### 6.3 输出端点

除目标产物外，尽可能比较：

- growth rate / biomass；
- substrate uptake；
- product titer/yield/productivity；
- by-products；
- ATP/redox/cofactor burden；
- protein/resource burden；
- stress；
- robustness；
- 模型实际覆盖的关键中间状态。

未覆盖端点必须显示 `not_modeled`，不能隐藏。

### 6.4 随机模型

随机模型必须使用多 replicate、可复现 seed policy、分布摘要和失败比例。单次 vEcoli run 不得被表述为稳定预测。

---

## 7. Multi-omics Integration 的一期边界

一期必须实现的是组学登记、条件/样本/实体/时间对齐、QC、缺失模态和跨模态冲突分析，不得宣称已经训练通用多模态 Virtual Cell。

必须生成 `CrossModalConsistencyReport`，至少回答：

- RNA、蛋白、代谢物、通量和表型方向是否一致；
- 时间点和样本是否可比；
- 不一致可能来自调控、翻译、降解、检测缺失、批次或模型缺失；
- 哪些解释需要新实验区分。

示例：`trpE RNA ↑` 但 `TrpE protein 未显著变化`，只能说明转录层与蛋白层不一致；不能直接判定工程无效，也不能自动填补蛋白值。

---

## 8. Prediction Reviewer

Problem 5 评价设计，Problem 6 必须增加对预测本身的独立审查。Reviewer 至少检查：

1. 结果是否来自真实成功 run；
2. adapter/model/artifact/version 是否可追溯；
3. 模型是否覆盖 chassis、condition 和 perturbation；
4. 干预映射是直接、近似还是不支持；
5. baseline 与 counterfactual 是否可比；
6. stochastic replicate 是否充分；
7. 哪些端点是模型直接输出，哪些是派生值；
8. 哪些过程未建模；
9. uncertainty 是否与方法相符；
10. 是否存在伪精确、跨域外推或因果过度解释；
11. 预测能否转化为可证伪实验；
12. 是否应该接受、限制性接受、补跑、换模型或拒绝。

必须输出结构化 finding，severity 至少包含 `info`、`warning`、`major`、`blocking`。Blocking finding 未解除前不得把预测标记为 `decision_ready`。

---

## 9. Model–Experiment Feedback Loop

### 9.1 实验计划必须针对预测

每个核心预测要绑定：端点、assay、单位、采样时间、对照、重复、预期方向/区间、判伪标准和可能替代解释。

对于 E. coli 代谢工程，验证计划按模型覆盖情况考虑：

- 生长率和 biomass；
- 葡萄糖消耗；
- titer、yield、productivity；
- 关键蛋白丰度；
- 中间代谢物；
- 竞争副产物；
- 必要的通量实验。

### 9.2 Observation ingestion

导入实验结果时必须校验 strain、condition、timepoint、unit、replicate、QC 和 prediction endpoint 映射。条件不一致时允许保存 observation，但不得直接计算 residual。

### 9.3 Residual 与原因假设

残差必须由代码按明确公式计算。LLM 只能生成标注为 hypothesis 的可能原因，如：初始状态错误、参数错误、资源负担缺失、调控未建模、工程实现失败、检测偏差或环境不匹配。

### 9.4 更新分级与门控

```text
Level 1：更新项目经验、belief 和 residual —— 可自动追加
Level 2：修正输入状态或条件 —— 版本化并记录来源
Level 3：参数校准 —— 需要数据充分性、可识别性、hold-out 验证与 Human Gate
Level 4：模型结构修改 —— 必须新模型版本和回归基准
Level 5：数据驱动模型重训练 —— 必须数据版本、训练记录、独立测试与审批
```

任何更新不得覆盖原 run、原 observation 或原模型版本。

### 9.5 Model Benchmark Memory 更新

当新的 context-matched observation 和 residual 通过 QC 后，系统可以自动创建“待评测”事件，但不得直接改写模型信誉。Benchmark 更新必须：

1. 冻结 model/artifact/adapter/dataset/protocol 版本；
2. 按 endpoint、strain、condition 和 perturbation class 分层；
3. 区分 reproduction、held-out、prospective 三类证据；
4. 使用代码计算指标，并保存纳入/排除样本；
5. 与现有 benchmark 比较，检测性能退化和 domain-specific failure；
6. 通过评测审核后追加新的 `ModelBenchmarkRecord`；
7. 将结果反馈给 Router 作为排序证据，但不得改变 compatibility decision。

若模型 A 在 growth 上表现更好、模型 B 在 product titer 上表现更好，系统必须保留任务特异性差异，禁止合成为单一“模型总分”。

### 9.6 Prediction Calibration Loop

校准闭环必须实现为：

```text
Versioned prediction
→ Context/QC-matched observation
→ Code-computed residual
→ Eligible calibration cohort
→ Calibration diagnostics
→ Versioned calibration profile
→ Future prediction interval/reliability label
→ Prospective re-evaluation
```

强制门控：只有与预测的 strain、condition、timepoint、endpoint 和 unit 对齐的数据可进入 cohort；同一数据不得同时用于模型拟合和独立校准/测试，除非明确记录交叉验证折叠；样本不足时只更新 residual history 和定性 reliability；校准不得改写原始 simulation result；parameter calibration 仍属于 Level 3 update；profile 必须版本化、可回滚，并在模型版本或分布变化后重新验证；持续偏差只能生成 `ModelUpdateProposal`，不得静默自我修正；必须用前瞻性新实验复核校准有效性。

---

## 10. Workflow 状态机与 Guard

至少实现以下状态，或映射到现有等价状态：

```text
simulation_requested
→ state_validated
→ model_selected
→ compatibility_checked
→ intervention_compiled
→ baseline_running
→ intervention_running
→ results_normalized
→ comparison_ready
→ prediction_under_review
→ validation_planned
→ awaiting_observation
→ residual_computed
→ update_proposed
→ human_review
→ completed
```

失败/分支状态：

```text
needs_input
no_compatible_model
out_of_domain
unsupported_intervention
run_failed
timed_out
infeasible
invalid_comparison
prediction_rejected
stopped
```

关键 Guard：

- Problem 4 正式 DesignVersion 不存在，不得编译；
- Problem 5 有 blocking rejection 时不得直接模拟，除非 Human Override 被审计记录；
- baseline 未成功，不得产生 counterfactual delta；
- compatibility 非通过，不得启动 run；
- raw output 未标准化，不得进入 comparison；
- prediction review 未通过，不得发布为决策依据；
- observation context 不匹配，不得计算 residual；
- Level 3–5 update 未人工批准，不得写入活动模型。

---

## 11. API、任务执行与持久化

### 11.1 API

按现有风格提供或扩展接口，至少覆盖：

```text
POST /projects/{id}/cell-states
GET  /projects/{id}/cell-states/{state_id}
GET  /models
POST /simulations/compatibility
POST /simulations
GET  /simulations/{run_id}
GET  /simulations/{run_id}/artifacts
POST /comparisons
GET  /comparisons/{id}
POST /observations
POST /residuals
POST /model-update-proposals
POST /model-update-proposals/{id}/decision
GET  /models/{model_id}/benchmarks
POST /benchmarks/evaluate
GET  /models/{model_id}/calibration-profiles
POST /calibration-profiles/build
POST /calibration-profiles/{id}/review
```

长时运行不得阻塞 Web 请求；应使用仓库现有 job/queue/background task 机制。若仓库没有队列，使用受控子进程与持久化 job 状态，不得把进程内全局变量当作唯一状态。

### 11.2 幂等性与并发

同一 model + artifact hash + input hash + config hash 可安全复用已完成 run；运行中的重复请求应返回现有 job。状态更新需要乐观锁或等价保护，避免重复执行和后写覆盖。

### 11.3 Artifact 与 provenance

必须保存：输入快照、模型文件引用/hash、配置、编译结果、命令或调用记录、stdout/stderr、raw output、normalized output、软件版本、运行时间和失败原因。敏感密钥不得进入 artifact 或日志。

---

## 12. 前端最低产品要求

前端不是聊天气泡堆叠，至少提供：

1. **Cell State 页面**：展示 chassis、环境、时间、观测/推断/假设/未知及缺失模态；
2. **Model Registry 页面**：模型类型、版本、适用域、可用状态和 failure modes；
3. **Simulation Workspace**：baseline、intervention、运行状态、日志摘要和失败原因；
4. **Counterfactual Compare**：同端点并列比较，显示单位、delta、interval 和 trade-off；
5. **Prediction Boundary**：明确“模型支持”“未建模”“域外”“映射假设”；
6. **Validation & Residual**：预测、实验值、残差、QC、原因假设和 update proposal；
7. **Human Gate**：更新批准/拒绝、理由和影响范围。
8. **Model Reliability**：按 endpoint/condition 展示 benchmark、样本量、数据拆分、适用范围、历史偏差、校准状态和退化告警；不得只显示一个总 confidence 分数。

任何 `not_computed` 或 `unsupported` 都必须显式展示，不能用空白或 `0` 代替。模型输出、实验事实、文献数据和 Agent 解释应使用不同视觉标签。

---

## 13. Phase 1–3 实施计划

### Phase 1：可信基础与最小垂直闭环

必须完成：

- 仓库审计和接入图；
- 核心 Schema、校验和持久化；
- Model Registry、Adapter Protocol、capability/health check；
- Cell State 与 Perturbation Compiler；
- 至少一个真实 adapter 或明确不可用的正式 adapter；
- baseline/intervention run；
- standardized result 和 counterfactual comparison；
- append-only workflow/Memory 事件；
- 单元、集成和失败路径测试。

### Phase 2：评审、不确定性与多场景

必须完成：

- Model Router；
- 多 scenario 和 replicate；
- Prediction Reviewer；
- uncertainty decomposition；
- 运行 artifact/provenance；
- API 与 Simulation Workspace；
- unsupported/out-of-domain/timeout/infeasible 等 UI；
- 至少一个 E2E 反事实案例。

### Phase 3：实验反馈与受治理更新

必须完成：

- OmicsObservation 和条件对齐；
- CrossModalConsistencyReport；
- validation plan；
- observation ingestion；
- residual calculation；
- ModelUpdateProposal 与 Level 1–5 guard；
- Model Benchmark Memory、版本化评测协议和任务特异性指标；
- Prediction Calibration Profile、cohort eligibility、样本量门控与 prospective re-evaluation；
- Human Gate；
- 闭环 E2E：预测 → 观测 → residual → update proposal → Memory；
- 文档、迁移、回滚和最终验收报告。

---

## 14. 测试与验收标准

### 14.1 必须测试的科学不变量

至少覆盖：

1. 未知状态不会被自动填值；
2. 不同 strain/condition 的场景不能直接比较；
3. 不兼容模型不会执行；
4. 不支持的 perturbation 返回结构化状态；
5. baseline 失败时不产生 delta；
6. 单位不一致时不计算 residual；
7. LLM 文本不能注册为 model output；
8. 失败 run 仍被持久化；
9. 多模型结果不会直接平均；
10. 无校准时不输出精确 confidence probability；
11. 模型未覆盖的 titer 不会被补数；
12. Level 3–5 update 无 Human Gate 不能激活；
13. 新 Design/CellState/Model version 不覆盖旧记录；
14. 同一幂等请求不会重复启动任务；
15. observation context mismatch 时不计算 residual；
16. 不同 endpoint/strain/condition 的 benchmark 不会被错误聚合；
17. reproduction benchmark 不会被标记为 held-out prediction performance；
18. benchmark 排名不能绕过 model compatibility check；
19. calibration cohort 会排除 context/QC/unit 不匹配数据；
20. 样本量不足时不会生成精确概率或 calibrated 状态；
21. calibration 不会改写原始 simulation result；
22. model version 或 domain 改变后旧 calibration profile 不会被静默复用；
23. 持续系统偏差只会触发受治理的 update proposal，不会自动修改生产模型。

### 14.2 E2E 最低案例

优先选择：

```text
E. coli K-12
+ 固定培养条件
+ 一个有明确模型映射的单基因干预
+ baseline vs mutant
+ 多 replicate（若模型随机）
+ growth 和模型真实支持的状态指标
```

E2E 必须证明：

- 输入不是自然语言直接进入模拟器；
- target 被规范映射；
- 真实 adapter 被调用；
- run ID、版本、hash、配置和 artifact 可追溯；
- baseline 与 intervention 使用同一比较协议；
- 未支持端点明确缺失；
- prediction review 能发现边界；
- 实验观测可形成 residual 和 update proposal。
- 合格历史记录可形成版本化 benchmark/calibration profile；样本不足时必须演示诚实降级；
- 后续 prediction 只引用上下文匹配且仍有效的 profile。

不要把复杂的 `ΔtnaA + trpE feedback-resistant mutation + aroG OE` 作为第一个强制 E2E，也不得在模型不覆盖时声称能够精确预测 L-tryptophan 提高百分比。

### 14.3 运行验证

必须执行仓库适用的：

- backend tests；
- frontend tests；
- type check；
- lint；
- production build；
- database migration check；
- adapter contract tests；
- E2E 或最接近的集成测试。

不得只报告“代码看起来正确”。失败测试必须区分本次引入、既有失败和环境阻断，并提供证据。

---

## 15. 强制禁止项

以下任一行为均视为 Problem 6 未完成：

1. 由 LLM 生成模拟数值并标记为模型结果；
2. 只实现 `simulate()` 占位符，没有 compatibility/compile/normalize；
3. 只建立 Schema，没有真实工作流接入；
4. 用 mock 成功代替真实 adapter E2E，却宣称已接通模型；
5. 将 Mycoplasma whole-cell model 的能力直接宣称为 E. coli vEcoli 能力；
6. 把 FBA 通量变化直接表述为真实 titer 变化；
7. 把 protein foundation model score 直接外推到整细胞产量；
8. 将组学文件装入 JSON 就宣称完成多组学 Virtual Cell；
9. 把模型输出写成实验事实；
10. 把单次随机运行当作稳定结论；
11. 隐藏失败 run、域外状态或未建模端点；
12. 不做 baseline 就报告 intervention 改变量；
13. 用一个未校准的综合分数替代不确定性分解；
14. 自动修改模型参数或结构且无版本和审批；
15. 覆盖旧状态、旧模型或旧 run；
16. Human Gate 只存在前端按钮、后端可绕过；
17. 只做页面演示，不实现服务层 guard 和测试；
18. 宣称“已建立 E. coli 数字孪生”而没有相应验证证据。

---

## 16. 允许的完成声明

若按本 Prompt 完成，可表述为：

> Agent 已具备将版本化工程方案转换为模型干预、检查真实模型适用域、执行可追溯 baseline 与反事实模拟、标准化并审查预测、显式暴露不确定性与未覆盖范围，并通过实验残差形成受治理模型更新建议的能力。

除非有独立证据，不得声称：

- 已建立完整 E. coli Digital Twin；
- 能准确预测任意基因改造后的产量；
- 已实现全组学因果模型；
- 已实现自动模型学习；
- 模型置信度等于实验成功概率；
- vEcoli 或 GEM 输出就是生物学真相。

---

## 17. 真实阻断条件与处理规则

只有以下情况允许停止并请求用户处理：

1. 必需代码、模型文件或数据确实不存在，且无法在当前范围内合法获取；
2. 需要真实密钥、受限许可证、远程算力或人工选择；
3. 仓库严重损坏或依赖冲突无法在不破坏用户环境的情况下修复；
4. 用户已有改动与本任务直接冲突且无法安全合并；
5. 操作涉及不可逆数据迁移或超出授权范围。

阻断时必须给出：已经检查的证据、具体阻断点、受影响 Phase、已完成的安全部分、最小解除步骤和解除后继续执行的命令。模型不可用本身不允许你伪造结果；但也不应阻止你完成 Schema、adapter contract、失败状态、workflow guard 和测试。

---

## 18. 最终交付报告格式

完成后必须按以下结构报告：

### A. 结果摘要

- Problem 6 是否形成真实垂直闭环；
- 实际接入了哪些模型；
- 哪些仅有 adapter contract；
- 哪些预测端点真实可计算；
- 哪些能力仍不支持。

### B. 仓库审计与接入表

填写第 1.1 节表格，引用真实文件和符号。

### C. 实现清单

按 Phase 1–3 列出修改文件、核心对象、API、workflow state、guard、UI 和迁移。

### D. 科学可信性说明

明确说明：数值来源、模型适用域、干预映射、baseline 协议、不确定性、未建模过程和禁止外推。

### E. 测试证据

列出实际运行命令、通过/失败数量、E2E 案例、失败路径和既有问题。

### F. 演示路径

给出从 DesignVersion 到 simulation、comparison、prediction review、validation、observation、residual 和 update proposal 的可复现步骤。

### G. Residual Gaps

逐项列出未完成能力、原因、科学影响和下一步，不得用“未来可扩展”笼统带过。

### H. 完成声明

只能使用第 16 节允许的表述，并明确说明当前系统距离“完整 E. coli Virtual Cell / Digital Twin”仍缺少什么。

---

## 19. 最终验收问题

提交前逐项回答，任何一项答“否”都必须修复或列为明确阻断：

1. Agent 是否只能通过真实 adapter 获得模型数值？
2. Cell State 是否区分 observed、inferred、assumed 和 unknown？
3. 工程动作是否经过可审计的 intervention compilation？
4. 模型是否在运行前检查底盘、条件、干预和输出覆盖？
5. baseline 与 intervention 是否满足同口径比较？
6. 模型失败和未覆盖端点是否被显式保存和展示？
7. 是否避免把 FBA、vEcoli、protein model 和 LLM 结果混为同一证据？
8. 不确定性是否按来源拆分，而不是伪造 confidence？
9. 随机模型是否使用可复现 seed 和 replicate？
10. prediction 是否经过独立边界审查？
11. 实验观测是否经 context/QC 对齐后才计算 residual？
12. residual 是否能产生版本化 update proposal？
13. 参数、结构或训练更新是否受 Human Gate 控制？
14. 原状态、原模型、原 run 和原 observation 是否不可静默覆盖？
15. 是否至少跑通一个真实或诚实降级的端到端案例？
16. 最终报告是否明确区分已实现、不可用、域外和未来能力？
17. 是否记录模型在具体 endpoint、strain、condition 和 perturbation class 上的历史表现，而不是单一总分？
18. benchmark 是否区分 reproduction、held-out 和 prospective evidence，并防止数据泄漏？
19. Router 是否只把 benchmark 作为兼容模型之间的排序证据？
20. calibration 是否只使用 context/QC-matched residual cohort，并由代码计算？
21. 样本不足或 profile 域外时是否自动降级为定性/不可用，而不是伪造概率？
22. calibration profile 是否版本化、可追溯、可回滚，并接受前瞻性再验证？

如果以上条件满足，Problem 6 才能被视为从“提出工程方案的 Synthetic Biology Agent”迈向“能够连接真实细胞模型并接受实验检验的 Virtual Cell Agent”的可信实现，而不是一次由语言模型生成的模拟演示。

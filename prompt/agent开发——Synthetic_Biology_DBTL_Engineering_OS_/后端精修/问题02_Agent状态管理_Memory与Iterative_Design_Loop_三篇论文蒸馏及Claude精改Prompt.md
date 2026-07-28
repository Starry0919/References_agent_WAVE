# 问题 02：Agent 状态管理（Memory + Iterative Design Loop）

> 用途：将本文整体交给 Claude Code。本文既是三篇参考论文的批判性蒸馏，也是本项目问题 2 的架构重构 Prompt。
>
> 系统唯一定位：**Persistent, Traceable, Human-Governed DBTL Engineering System**。
>
> 本系统面向 **E. coli K-12 合成生物工程设计 / WAVE Virtual Cell**。它服务的是持续演化的科研项目与细胞模型，不是 PI、Wet Lab、Dry Lab、产品人员或开发者中的任何单一角色。上述角色只能作为需求来源、审批主体或系统使用者，不能成为 Agent 的产品定位或架构中心。

---

## 0. Claude 的总任务

### 0.1 不可偏移的系统中心

Claude 在任何实现、命名、页面或总结中，都必须保持以下层级：

```text
Cell / Biological System
→ DBTL Scientific State Evolution
→ Project as persistent carrier
→ System capabilities and data contracts
→ Stakeholders as requirement sources and governance actors
→ Conversation as one interaction channel
```

禁止倒置为：

```text
PI / Wet Lab / Dry Lab / Product
→ role-specific assistants
→ shared memory
```

本 Prompt 中出现的 PI、Wet Lab、Dry Lab、平台使用者、算法工程师和审计者，是为了检验系统能力能否覆盖真实科研约束；不得据此创建 `PI Agent`、`Wet Lab Agent` 等并列角色产品，也不得把首页组织成面向角色的聊天入口集合。

请先审计现有代码和问题 1 已实现或计划实现的 Workflow Engine，再将当前 one-shot Agent 重构为能够跨轮次保存、恢复、比较、学习和再设计的 **project-scoped iterative engineering system**。

本轮核心闭环必须从：

```text
Goal → Analysis → Design Report → End
```

升级为：

```text
Project Goal
  → Design Version
  → Build/Test Plan
  → Experiment/Data Ingestion
  → Observation & QC
  → Hypothesis Update
  → Model/Policy Update
  → Redesign
  → New Design Version
```

不得把以下任一项单独冒充“已经实现 Memory + DBTL”：

- 把完整聊天记录重新塞给 LLM；
- 用一个 JSON 文件保存上一轮报告；
- 仅添加 `strain_v0/v1` 字符串；
- 允许用户上传 CSV，但不做数据身份校验、QC、解析和结构化观察；
- 把失败方案放入向量库，却没有适用条件和因果归因；
- 每轮都把所有旧结果拼进 prompt；
- 仅让 LLM 阅读上一轮结果后自由提出下一轮；
- 宣称用了 Bayesian optimization 就等于实现科学学习；
- 通过模型自评判断“学会了失败”。

本轮目标不是无人监督地控制机器人或真实实验设备。真实构建、培养和检测默认是外部过程；系统首先要可靠完成 **实验设计交接、结果导入、解释、版本化和再设计**。

---

# 一、问题定义：现在缺少的不是聊天记忆，而是科学项目状态

## 1.1 一句话定义

当前 Agent 是一次性设计报告生成器；目标 Agent 应成为能够维护菌株—实验—数据—假设—决策之间可追溯关系，并通过 DBTL 循环持续更新的合成生物工程系统。

## 1.2 四个直接缺口

### A. Project-level Memory

Agent 不知道项目过去提出过什么、构建过什么、测到了什么、为什么改变判断，也无法区分“用户说过的话”和“经实验验证的事实”。

### B. Design Version Control

菌株设计是具有亲缘关系和组合效应的工程对象，不是覆盖保存的文档。系统缺少不可变版本、父子关系、设计差异、回滚、分支和实验绑定。

### C. Experiment Feedback Entry

实验结果无法以可验证的数据资产进入系统，也无法从原始文件转化为带 QC、单位、条件和不确定性的 Observation。

### D. Failure Learning

系统不能区分：执行失败、数据失败、假设被否证、局部效果不佳、目标改善但适应度下降、组合上位性，因而不能形成可靠的后续策略更新。

## 1.3 必须区分的四类“状态”

| 状态 | 作用域 | 例子 | 是否可覆盖 |
|---|---|---|---|
| Execution State | 一次 workflow run | 当前阶段、工具调用、重试次数 | 可随运行迁移 |
| Project State | 长期研究项目 | 目标、宿主、约束、当前主分支 | 受事件更新 |
| Biological State | 某菌株在某条件下 | genotype、growth、proteome、metabolites | 条件化且带不确定性 |
| Knowledge/Policy State | 跨轮次经验 | 假设支持度、失败案例、策略先验 | 只能通过有依据的更新规则改变 |

问题 1 的 `WorkflowRun` 主要处理 Execution State；问题 2 必须新增 Project、Design、Experiment、Observation、Hypothesis 和 Policy 的持久层，二者不能混成一个巨大 JSON。

---

# 二、三篇论文的证据定位

| 论文 | 论文性质 | 对问题 2 的主要价值 | 不能证明什么 |
|---|---|---|---|
| Lin Tang, *The virtual cell*, Nature Methods, 2025 | Methods to Watch / 定位性短文 | 定义 Virtual Cell 应当是整体、机制性、动态、可预测的模型；强调多模态、时间序列、扰动数据和数据稀缺 | 没有提出 Agent memory、数据库 schema 或 DBTL 实现 |
| Boiko et al., *Autonomous chemical research with large language models*, Nature, 2023, DOI: 10.1038/s41586-023-06792-0 | 原始研究；Coscientist | 展示 Planner、搜索、代码、文档与实验模块的组合；用已收集数据指导后续条件选择；展示格式纠错和实验执行反馈 | 没有证明长期项目记忆、跨 campaign 迁移、可靠因果归因或生物工程适用性 |
| Tobias & Wahab, *Autonomous ‘self-driving’ laboratories: a review of technology and policy implications*, R. Soc. Open Sci., 2025, DOI: 10.1098/rsos.250646 | 综述与政策观点 | 提供闭环 SDL、自主等级、Adam/Eve/BioAutomata/SAMPLE 等案例、数据库与优化器分工、人类责任和安全边界 | 综述案例不是统一可复制架构；“高自主”等级不等于科学正确性 |

证据使用原则：原始研究支持“某机制在特定实验中被演示”；综述支持“方法谱系和检查框架”；定位文章支持“Virtual Cell 应追求的性质”。不得把愿景性陈述写成已验证功能。

---

# 三、论文一蒸馏：The virtual cell

## 3.1 是什么

该文将 Virtual Cell 描述为仍在形成中的目标体系，并给出三个关键愿景：

1. 对细胞的分子和细胞表型提供整体图景；
2. 模型具有机制性和动态性，能解释细胞行为的生物学基础；
3. 能在广泛条件下进行预测。

文章认为大规模组学数据和 AI 是主要推动力，但关键瓶颈仍是高质量数据不足，特别是能够支持机制和因果判断的多模态、时间序列和扰动数据；如何整合已有模型与生物知识也仍无统一答案。

## 3.2 为什么与问题 2 有关

Virtual Cell 不能只是“记住过去说过什么”。若想动态更新和预测，系统必须知道：

- 哪个菌株；
- 在什么培养条件与时间点；
- 接受了什么扰动；
- 观察来自哪种模态；
- 数据质量和不确定性如何；
- 哪个机制模型因该观察被支持或削弱。

因此 Project Memory 的最小单位不应是自然语言对话，而应是 **带条件、时间、扰动、测量方法和 provenance 的生物观察事件**。

## 3.3 怎么转化为本 Agent 的设计约束

新增条件化的 `BiologicalStateSnapshot`，而不是维护一个被不断覆盖的“当前细胞状态”：

```yaml
BiologicalStateSnapshot:
  snapshot_id: uuid
  project_id: uuid
  design_version_id: uuid
  experiment_run_id: uuid
  host:
    species: Escherichia coli
    strain: K-12 derivative
  genotype_ref: genotype manifest id
  environment:
    medium:
    carbon_source:
    temperature_c:
    oxygenation:
    cultivation_mode:
  timepoint:
    value:
    unit:
    phase:
  perturbations: []
  phenotype_observations: []
  omics_observations: []
  model_predictions: []
  uncertainty: []
  provenance: []
```

状态快照应允许同一菌株在不同条件和时间点共存，禁止把它们合并成无条件的全局事实。

## 3.4 可直接使用的地方

- 用“整体、机制、动态、可预测”作为问题 2 的四项长期产品指标；
- 优先保存 perturbation、time-series 和 multimodal 数据身份；
- 将 observation 与 prediction 分开保存，支持事后比较；
- 将已有生物知识/模型版本作为解释上下文，而不是覆盖实验事实。

## 3.5 不应照搬或夸大的地方

- 文章没有 Memory 架构，不得声称 schema 来自该文；
- 当前 Agent 接入少量蛋白组或生长数据，不代表已经建立 Virtual Cell；
- “动态”不能仅以多轮聊天次数衡量；
- “预测”必须绑定模型版本、输入条件、适用域和实测对照。

## 3.6 理性结论

论文一最适合作为定位标尺：它决定 Memory 应保存什么科学对象、最终更新什么模型。它不能作为具体工程实现模板。

---

# 四、论文二蒸馏：Coscientist

## 4.1 是什么

Coscientist 是以 GPT-4 Planner 为中心的多模块系统。Planner 的动作空间包括：

- `GOOGLE`：检索互联网；
- `PYTHON`：隔离环境中的计算和代码执行；
- `DOCUMENTATION`：检索设备/API 文档；
- `EXPERIMENT`：通过自动化 API 或人工流程执行实验。

系统演示了合成方案搜索、设备文档使用、液体处理器控制、集成化学实验，以及在完整反应条件数据集上用过去观测指导下一轮条件选择。

## 4.2 为什么与 Memory/Failure Feedback 有关

论文把“能否使用此前收集的数据指导未来动作”作为推理能力测试。优化游戏中，模型读取过去选择、产率和自身观察，再选择下一条件。它还展示：

- 软件/API 错误后查询文档并修正协议；
- 输出未遵守数据格式时被提醒并重新生成；
- 给定少量 prior data 能改善初始条件选择；
- 新数据可以改变后续搜索策略。

这证明实验结果反馈到决策环是可行的，也说明先验数据和结构化动作空间有价值。

## 4.3 论文实际怎么做

在反应优化实验中：

1. 选择变量组合；
2. 从完整数据表获得该组合的产率，模拟实验观察；
3. 将既往动作和结果提供给模型；
4. 要求模型给出下一组合和解释；
5. 最多执行固定轮数；
6. 与 random 和 Bayesian optimization 等基线比较。

论文使用 normalized advantage、normalized maximum advantage 及其随迭代变化来观察搜索表现。论文同时显示 LLM 并不稳定：可能不遵守 schema，且标准 Bayesian optimization 在部分数据集上表现更强。

## 4.4 对本 Agent 可迁移的机制

### A. 受限动作空间

下一轮设计不是自由文本，应先产生机器可验证的 `CandidateAction`，并限定允许修改的变量与操作。

### B. Observation → Next Action 契约

每轮必须明确输入哪些已经通过 QC 的观察、当前目标函数、预算和约束，再生成候选。

### C. 错误类型分离

- `TOOL_EXECUTION_ERROR`：API/代码/设备错误，可重试或查文档；
- `SCHEMA_ERROR`：输出格式失败，不是生物学失败；
- `EXPERIMENT_EXECUTION_FAILURE`：实验未按协议完成；
- `BIOLOGICAL_NEGATIVE_RESULT`：实验有效，但结果不支持预期；
- `TRADEOFF_FAILURE`：目标改善但生长/稳定性越界。

这些错误不能写进同一个 Failure Memory。

### D. 算法基线和路由

对于低维、变量定义清楚、目标可量化的局部优化，Bayesian optimization/active learning 应作为正式策略候选或基线，而不是默认让 LLM 凭直觉选下一实验。

## 4.5 不能直接迁移的内容

- 化学反应条件空间通常比菌株改造空间更规整；基因操作存在上位性、长周期和多目标权衡；
- 论文中的完整 lookup table 不是真实开放世界实验；
- 对话中保留前几轮结果只是工作记忆，不是持久化项目记忆；
- LLM 给出“合理解释”不等于已完成机制性归因；
- 一次协议修正不等于 Failure Policy 已在跨项目层面学习；
- 不应让 LLM 直接把实验结果写成“已证实机制”。

## 4.6 理性结论

Coscientist 是 `Observation → Decision → Experiment` 回路的重要原型，可借鉴动作约束、结果反馈、纠错与基线评估；但必须补上持久化、版本图、QC、因果归因和生物条件化，才能用于本 Agent。

---

# 五、论文三蒸馏：Self-driving laboratories review

## 5.1 是什么

该综述将 SDL 描述为 AI 与实验自动化结合的闭环科研系统，覆盖假设生成、实验设计、执行、数据分析、结论和下一轮假设更新。其重要价值不是提供唯一架构，而是展示不同自主等级、不同学科案例和治理约束。

## 5.2 为什么与本问题有关

综述显示真正闭环通常包含相互独立但关联的组件：

- orchestrator / master controller；
- design database 与 result database；
- predictive model / optimizer / acquisition policy；
- 自动或人工实验执行；
- 结果分析与下一轮选择；
- 人类监督、安全停止和责任归属。

这与本项目的关键判断一致：Memory 不是 LLM 的附属提示词，而是闭环系统的共享科学状态层。

## 5.3 代表性案例及可迁移方法

### Adam

Adam 在已提供的酵母代谢逻辑模型上，选择菌株和培养实验、分析结果并设计新实验，用于推断氨基酸合成相关 orphan enzyme。关键启示：

- 机制模型使假设与实验可计算；
- 结论质量强依赖底层生物模型的准确和完整；
- 必须保存 hypothesis → experiment → result → conclusion 的链。

### Eve

Eve 先筛少量化合物，再用结果建立 QSAR，并选择下一批。启示是批次式主动学习和模型更新，但其分子筛选逻辑不能直接替代菌株工程决策。

### BioAutomata

该系统在 E. coli 中通过 acquisition policy 基于上一轮结果选择下一批遗传元件组合，3 轮内提升 lycopene 产量。它对本项目的直接启示是：

- Design–Build–Test–Learn 的轮次需要显式记录；
- 下一轮选择应由 acquisition policy 消费结构化结果；
- 组合设计的结果必须保留完整 genotype，而不能仅记录单个基因贡献。

### SAMPLE

SAMPLE 从实验结果推断 QSAR，使用 Gaussian process 判断序列活性，并比较 Bayesian optimization 策略，搜索少量序列空间获得更稳定的酶。启示是：

- 代理模型要版本化；
- acquisition strategy 要可替换和比较；
- 每个候选要保留预测值、预测不确定性与实测值；
- 样本效率是重要指标。

### MCN 与双数据库案例

综述描述的闭环分子发现平台使用 Master Control Network 编排，并分别维护实验设计和实验结果数据库。对本项目而言，应进一步用稳定 ID 将二者连接，而非合成一张宽表。

## 5.4 方法论层面怎么做

综述将较低自主等级的动态 workflow planner 与更高等级的 Bayesian optimization、active learning、生成模型和 NLP 区分。说明算法应按任务结构路由：

- 规则明确的步骤：确定性 workflow；
- 明确搜索空间的多轮优化：BO / active learning / acquisition policy；
- 机制假设生成和解释：受约束 LLM + biological model；
- 高风险或模型适用域外：Human Gate。

## 5.5 综述提供的检查清单

- 是否真正执行多轮闭环，而非只输出建议；
- 是否有独立的设计记录和结果记录；
- 是否根据结果更新假设或模型；
- 是否显式定义搜索空间、目标和预算；
- 是否有污染、测量失败、设备失败等异常路径；
- 是否保留人类最终知情、暂停和终止能力；
- 是否把高度结构化的优化误称为开放式科学发现；
- 是否报告样本效率、失败率与对照基线。

## 5.6 不应照搬或夸大的地方

- SDL 自主等级衡量能力范围，不保证结论正确；
- 多数成熟案例优化的是定义好的变量空间，不能证明开放式机制发现已解决；
- 本 Agent 没有机器人实验平台时，不应宣称达到 Level 3/4 SDL；
- Bayesian optimization 不适合直接处理没有可靠目标函数、变量编码或观测噪声模型的问题；
- Review 中的政策建议应转化为 Human Gate 和审计要求，而非装饰性章节。

## 5.7 理性结论

论文三最适合提供总体架构检查和算法路由原则。对于本项目，近期合理目标是“人类执行 Build/Test、Agent 管理闭环认知与数据”的条件自治系统，而不是追求名义上的最高自主等级。

---

# 六、System Capability Requirements：由科研约束反推系统能力

本章不是产品角色介绍，也不是多角色 Agent 设计，而是系统能力需求追踪层。Claude 必须让后续 schema、API、状态机、界面和验收测试能够回指真实科研约束。任何新增模块如果不能说明其保护的 Scientific State、支持的 DBTL 决策和验收证据，不得仅因“Agent 架构通常需要”而实现。

角色只允许出现在 `Primary requirement sources / users / approvers` 字段中，用于说明需求从哪里产生、由谁验证或批准。系统章节、核心对象和一级导航必须围绕能力与科学对象命名，不得围绕角色命名。

本章的规范优先级不是按角色排列，而是：`Cell-State Evolution → DBTL Scientific State → Project Persistence → Traceability / Execution / Reproducibility / Governance → User Views`。其中 Cell-State Evolution 是所有项目记忆最终需要承载的科学对象，不是附加在产品需求之后的远期功能；第 0.1 节的系统中心对全文具有最高约束力。

## 6.1 需求追踪矩阵

| System requirement | Primary requirement sources / users | 真实问题 | 系统能力 | 主要对象/API | 验收证据 |
|---|---|---|---|---|---|
| Decision Traceability | PI、Research Lead、Scientific Auditor | 为什么当前方案优于备选，为什么本轮改变？ | 条件化历史比较、证据与决策追踪 | `DecisionRationale`, `HypothesisVersion`, `DesignDiff`, `LearningCycle` | 每项新增、删除、保留的决策均可回溯到 Observation、备选方案和不确定性 |
| Governed Knowledge Accumulation | PI、Domain Expert、Knowledge Curator | 项目和实验室究竟累计学到了什么？ | 带适用域、反例、审批和撤销的知识治理 | `KnowledgeClaim`, promotion/review/retraction workflow | 能区分单次观察、项目经验、候选知识和正式实验室规则 |
| Experimental Execution | Wet Lab、Automation、Robot、External LIMS | 方案是否真正构建和测试；下一步操作哪个实体；失败来自哪里？ | 构建身份、实验血缘和分层失败归因 | `Construct`, `ExperimentRun`, sample manifest, `FailureCase` | 能区分“设计过”“构建成功”“测过”“QC 通过”；PCR/污染不得作为生物学负证据 |
| Computational Reproducibility | Dry Lab、Algorithm Engineer、Auditor | 半年后能否复现分析并比较设计版本？ | 计算谱系固化与结构化 Diff | `AnalysisRun`, `DataAsset`, `SoftwareEnvironment`, Design Diff API | 输入、参数、环境、输出可追溯；同时显示 genotype、decision、evidence、result、hypothesis 差异 |
| Project Operability | Project Lead、平台使用者、Product/Operations | 项目推进到哪里、为何阻塞、下一步是什么？ | 项目状态投影而非聊天摘要 | `ProjectStatusView`, `NextAction` | 无聊天历史也能重建当前版本、等待项、QC、阻塞原因和下一步 |
| Context Governance | LLM/ML Developer、Auditor | 三年历史如何进入有限上下文且不丢失关键事实？ | 分层压缩、检索预算与可解释省略 | memory hierarchy, `ContextBundle` | 1 万事件下仍可给出来源明确、token 有界且可展开的上下文 |
| Cell-State Evolution | Virtual Cell modelers、DBTL team、Scientific users | 细胞如何随扰动、环境和时间演化？ | 状态—扰动—预测—观测—残差轨迹 | `CellStateTrajectory` | 能区分预测、观测、推断状态，并追踪一次干预前后的动态变化 |
| Portfolio Knowledge | Research Lead、Knowledge Curator、Scientific Auditor | 多个项目共同产生了哪些可迁移、仍有边界的知识？ | 跨项目查询、证据聚合、冲突保留与知识晋升 | `KnowledgeClaim`, `PortfolioView`, promotion/retraction workflow | 可跨项目回答某主题学到了什么，同时保留条件、反例和来源项目 |
| Protocol & Physical Identity | Wet Lab、Automation、External LIMS | 相同设计是否按同一协议执行；实际材料是否可唯一定位？ | 协议版本绑定与外部实体引用 | `ProtocolVersionRef`, `PhysicalStockRef` | 每次实验可回溯协议版本；库存事实由权威外部系统提供而非 Agent 猜测 |
| Collaboration Governance | Project team、Approver、Auditor | 多人并行修改、审批和交接时如何避免状态覆盖与责任不清？ | RBAC/ABAC、乐观并发、审批分离与审计 | `Actor`, `RoleBinding`, version precondition, approval record | 冲突写入被拒绝；提议者不能在受控节点自批；所有变更可归责 |

## 6.2 Decision Traceability Requirement

**Primary requirement sources / users：** PI、Research Lead、Scientific Auditor。

科研决策需要三类可审计回答：

1. **为什么选它**：比较相似宿主、培养条件、遗传背景和测量方法下的历史结果，同时报告样本量、QC、效应量、不确定性和失败类型。禁止用 `12 次中 10 次成功` 取代条件化证据评价。
2. **为什么改了**：由 `Observation → Hypothesis change → EngineeringDecision change` 形成完整链条。设计差异不能只列基因差异。
3. **学到了什么**：将项目事件蒸馏为可审查的 `KnowledgeClaim`，但保留反例、适用范围和证据血缘。

新增或等价实现：

```yaml
DecisionRationale:
  rationale_id: uuid
  decision_id: uuid
  alternatives_considered: []
  matched_prior_cases: []
  comparison_dimensions: []
  supporting_observations: []
  conflicting_observations: []
  uncertainty:
  why_now:
  approved_by:

KnowledgeClaim:
  claim_id: uuid
  statement:
  scope:
    species:
    strain_background:
    genotype_context:
    medium:
    carbon_source:
    cultivation_mode:
    assay:
  supporting_experiments: []
  contradicting_experiments: []
  independence_groups: []
  evidence_grade:
  status: project_candidate | lab_candidate | lab_approved | retracted
  reviewers: []
  promotion_record:
  supersedes_claim_id:
```

## 6.3 Experimental Execution Requirement

**Primary requirement sources / users：** Wet Lab、Automation、Robot、External LIMS。

必须显式区分：

```text
DesignVersion（计划中的基因型）
→ Construct（实际构建对象）
→ GenotypeVerification（是否构建正确）
→ ExperimentRun（在哪次实验中测试）
→ Sample（哪一个物理样本）
→ DataAsset / Observation（得到什么数据和结论）
```

不得仅凭 DesignVersion 推断真实菌株存在。系统视图必须显示：`designed / build_in_progress / verified / test_ready / tested / archived`。下一步行动必须绑定唯一 `construct_id`，不能只输出一组基因名称。

实验执行失败示例必须进入验收：构建 PCR 失败、污染、样本标签错配、培养偏差、仪器失败、数据 QC 失败、生物学无效、目标提高但生长代价过高。只有最后两类在满足身份和 QC Gate 后，才可参与生物学假设更新。

## 6.4 Computational Reproducibility Requirement

**Primary requirement sources / users：** Dry Lab、Algorithm Engineer、Auditor。

新增 `AnalysisRun` 或等价对象：

```yaml
AnalysisRun:
  analysis_run_id: uuid
  input_asset_ids: []
  sample_manifest_version:
  parser_name:
  parser_version:
  workflow_name:
  workflow_version:
  code_commit:
  container_or_environment_digest:
  parameters:
  random_seed:
  started_at:
  completed_at:
  qc_status:
  output_asset_ids: []
  output_checksums: []
  operator:
```

最小复现清单必须包含：输入文件校验值、样本映射版本、软件/解析器版本、归一化与缺失值处理参数、代码或环境标识、随机种子、QC 决策及输出校验值。缺任一关键项时标记 `reproducibility_status: incomplete`，不得声称完全可复现。

`DesignDiff` 必须覆盖五层：

- genotype：新增、删除、修改、调控强度变化；
- engineering decision：每项操作的机制与风险变化；
- evidence：新增、失效、冲突或证据等级变化；
- hypothesis：支持度、替代解释及不确定性变化；
- outcome：产量、生长、副产物、稳定性与实验质量变化。

## 6.5 Project Operability Requirement：Project State，不是聊天首页

**Primary requirement sources / users：** Project Lead、平台使用者、Product/Operations。

实现可由事件账本重建的 `ProjectStatusView`：

```yaml
ProjectStatusView:
  project_id:
  lifecycle_stage:
  active_design_version:
  active_construct:
  active_learning_cycle:
  latest_accepted_results: []
  waiting_for: []
  qc_state:
  blockers: []
  pending_human_gates: []
  next_actions: []
  last_material_change_at:
```

首页优先级固定为：Current Status → Latest Result → Blocker/Waiting → Next Action → Design/Experiment Timeline。聊天可作为交互入口，但不得成为项目事实来源或唯一导航结构。

## 6.6 Context Governance Requirement：分层记忆压缩与预算治理

**Primary requirement sources / users：** LLM/ML Developer、Auditor。

采用可逆追溯的层级：

```text
Raw Event / Raw Data
→ QC-qualified Observation
→ Finding
→ scoped KnowledgeClaim
→ Project Summary
→ ContextBundle
```

压缩规则：

- 下层事实永不因摘要生成而删除或覆盖；
- 每个摘要保存 `source_ids`、生成方法、版本、时间和人工复核状态；
- 重要冲突、失败、少数反例和未决不确定性不得被多数结论吞掉；
- Context Builder 先按身份、版本、条件和适用域过滤，再进行语义检索与摘要；
- 每次调用记录 token budget、纳入/省略项及省略原因；
- 用户必须能从摘要逐层展开到 Observation、ExperimentRun 和原始 DataAsset。

至少定义四类预算：`critical facts`（不可省略）、`active cycle`、`relevant precedents`、`background knowledge`。预算不足时优先删减背景，而不是当前实验身份、QC、冲突证据和 Human Gate。

## 6.7 Cell-State Evolution Requirement：Virtual Cell 的核心科学状态

**Primary requirement sources / users：** Virtual Cell modelers、DBTL team、Scientific users。

现有 `BiologicalStateSnapshot` 保留，但新增轨迹关系：

```yaml
CellStateTrajectory:
  trajectory_id: uuid
  project_id: uuid
  baseline_state_id:
  perturbation:
    design_version_id:
    construct_id:
    environmental_change:
    time_zero:
  predicted_state_ids: []
  observed_state_ids: []
  timepoints: []
  model_versions: []
  experiment_run_ids: []
  prediction_observation_residuals: []
  uncertainty:
  applicability_scope:
```

必须区分 `predicted`、`observed`、`inferred` 三种状态来源。时间点、培养条件、测量方法和模型版本不同的状态不能直接覆盖。Virtual Cell 的长期资产是“条件化动态轨迹及预测误差”，而不是一个永远被刷新成最新值的 Cell State。

## 6.8 Governed Knowledge Accumulation Requirement：经验何时可以升级为实验室知识

**Primary requirement sources / approvers：** PI、Domain Expert、Knowledge Curator、Scientific Auditor。

知识传播采用分层权限：

```text
Single observation
→ Project-local update
→ Project Knowledge Candidate
→ Lab Knowledge Candidate
→ PI/Domain Review
→ Lab-approved Rule
```

默认规则：

- 一次结果，无论成功或失败，只能更新项目局部假设；
- “3 次独立实验”只能作为最低候选阈值示例，不能作为充分条件；独立性、效应一致性、QC、条件覆盖、因果合理性和反例同样必须审查；
- 技术重复不等于独立实验；同一批次或同一构建背景不得虚增独立性；
- 跨宿主、培养基或组合基因型的传播必须显式降级置信度或重新验证；
- 全局排序器或 policy 更新必须绑定训练数据快照、离线评估、批准人、版本和回滚点；
- 新证据冲突时允许降级、暂停或撤销 `KnowledgeClaim`，但保留历史审计。

Claude 必须实现 `PolicyUpdateGate` 与 `KnowledgePromotionGate` 的区别：前者管理算法/推荐策略，后者管理科研知识主张，两者不得共用一个布尔 `approved` 字段。

## 6.9 Portfolio Knowledge Requirement：跨项目知识沉淀，而不是跨项目数据混合

**Primary requirement sources / users：** Research Lead、Knowledge Curator、Scientific Auditor。

`Lab Portfolio` 不得实现为一个把全部项目报告拼接起来的全局摘要，也不得按基因操作计算脱离条件的“成功率”。问题 2 必须支持一个只读、可追溯的 `PortfolioView` 或等价查询层，用于跨项目检索同一产物、通路、宿主或干预的证据；其事实来源仍是各项目内已经通过身份、QC 和治理检查的对象。

```yaml
PortfolioView:
  portfolio_id:
  query_scope:
  included_project_ids: []
  included_claim_ids: []
  condition_groups: []
  supporting_patterns: []
  contradictory_patterns: []
  unresolved_questions: []
  generated_from_event_offsets: {}
  generated_at:
```

必须满足：

- Project Memory 不能被跨项目写入直接覆盖；
- 项目级 `KnowledgeClaim` 只有通过 6.8 的晋升流程后，才可成为正式 Lab Knowledge；
- 跨项目聚合必须按宿主、基因型、培养条件、测量方法和干预组合分层；
- 输出必须同时报告支持证据、冲突证据、覆盖范围、独立性和未知区域；
- 新证据到来后可重算 Portfolio 投影，但不得改写历史 Claim 和审批记录。

验收问题：系统能否回答“过去一年所有 L-tryptophan 项目学到了什么”，并逐条展开至项目、实验、观察和原始数据，同时明确哪些结论尚不能跨条件泛化？

## 6.10 Protocol、Physical Stock 与资源系统边界

**Primary requirement sources / users：** Wet Lab、Automation、External ELN/LIMS/Inventory、Operations。

协议版本会改变 Observation 的可比性，因此属于问题 2 必须保存的实验上下文。至少增加：

```yaml
ProtocolVersionRef:
  protocol_id:
  version:
  immutable_snapshot_or_checksum:
  authoritative_uri:
  critical_parameters:
  deviation_record_ids: []
```

每个 `ExperimentRun` 必须绑定实际执行的协议版本和偏差记录，不能只写 `LB`、`M9`、温度或 OD600 等零散字段，也不能在协议更新后让旧实验自动指向最新版。

实际菌株库存、Freezer/Box/Position、剩余体积、领用记录，以及仪器、GPU、预算和排期，不应在问题 2 内重建完整 Inventory/LIMS/Scheduler。当前范围只定义稳定外部引用：

```yaml
PhysicalStockRef:
  external_system:
  external_stock_id:
  construct_id:
  resolved_snapshot:
  resolved_at:
  availability_status:
```

硬性边界：Agent 可以读取、显示和验证权威资源状态；在没有外部系统事务确认时，不得自行声称“库存已扣减”“仪器已预约”或把缓存状态当成当前事实。完整资源运营属于后续平台集成，不得阻塞本轮 DBTL Memory 闭环。

## 6.11 Collaboration Governance Requirement：多人协作首先是状态一致性

**Primary requirement sources / users / approvers：** Project team、PI/Research Lead、Data Steward、Scientific Auditor。

问题 2 不创建按人员分裂的多个 Agent；协作通过共享 Project State 上的身份、权限、并发控制和审批实现：

- 所有 mutation event 必须包含 `actor_id`、身份来源、时间、理由和客户端看到的前置版本；
- 更新 Design、Hypothesis、Observation acceptance、Knowledge promotion 时使用乐观并发或等价版本条件，禁止 silent last-write-wins；
- 提议、复核、批准和执行是不同动作；高风险节点必须支持 separation of duties；
- 权限至少覆盖 view / propose / execute / accept-QC / approve / administer，具体采用 RBAC 或 ABAC 由现有技术栈决定；
- 交接不是聊天总结，而是由当前 ProjectStatusView、未决 Gate、责任人和 NextAction 生成的可审计 handoff；
- 外部 Reviewer 只能看到授权范围内的冻结快照，不能修改项目事实。

最小验收：两名用户基于同一 DesignVersion 并发提交互斥修改时，后一写入必须得到显式冲突并要求重新比较；提出 Lab Knowledge 晋升的人不能在要求双人复核的配置下独自批准。

## 6.12 Model Evolution Requirement：Virtual Cell 不只积累 Observation

每一次可用于决策的预测必须绑定 `model_version`、训练/校准数据快照、适用域、参数或 artifact checksum、不确定性和生成时间。实验后计算的 residual 必须形成新校准或新模型版本的证据，不得就地修改旧模型使历史预测无法重放。

```text
ModelVersion_n → Prediction_n → Observation_n → Residual_n
                                         ↓
                         Update Proposal + Evaluation
                                         ↓ Human/Policy Gate
                                  ModelVersion_n+1
```

新模型只有在预先定义的验证集、基线、校准与安全检查通过后才能成为项目默认模型。一次实验可更新项目局部后验，但不能自动替换跨项目模型。模型回滚后，历史 Prediction 仍必须指向当时实际使用的版本。

## 6.13 Operational Metrics Requirement：衡量闭环，不用 KPI 反向污染科学判断

可以从事件时间戳派生 DBTL cycle time、waiting time、human approval latency、数据返工率、QC failure rate、重复设计率和 time-to-decision，但它们是系统运营投影，不是科学目标函数。

指标必须：定义起止事件、区分 active work 与 waiting、按项目类型分层、显示样本量，并可追溯到事件。禁止为了缩短周期跳过 QC/Human Gate，也禁止把“Agent 建议被采用率”“生成报告数量”当作科学有效性的代理指标。

## 6.9 本章的验收方式

至少增加以下端到端断言：

1. PI 查询“为什么 v2 移除 TrpE OE”，系统返回对应蛋白组 Observation、假设变化和 design diff，而不是重新生成解释；
2. 去年设计过但未成功构建的 `aroG OE` 不得显示为“已实验失败”；
3. 使用旧 parser 得到的结果可由 AnalysisRun 完整复现或明确报告缺失项；
4. 1 万条事件下 ContextBundle 保持预算上限，并保留当前 QC、冲突证据和来源链；
5. 单次 `pykF KO` 生长缺陷不能升级为 Lab Rule；三次技术重复也不能冒充三个独立实验；
6. Dashboard 能在无聊天历史的情况下从事件账本重建当前状态和下一步；
7. 同一扰动的预测状态和实测状态并存，预测误差被记录而非覆盖预测；
8. 已批准 Lab Rule 遇到高质量反例后可进入 review/retracted，且旧版本仍可审计。

---

# 七、三篇论文共同导出的核心判断

## 7.1 目标架构

```text
Persistent Project Ledger
        ↓
Design Version Graph ←→ Hypothesis Graph
        ↓                       ↑
Experiment Plan → External Build/Test
        ↓
Data Asset → QC → Observation
        ↓
Learning Engine
        ↓
Policy/Model Update → Redesign
```

Workflow Engine 决定阶段和 Gate；Memory Store 保存可追溯事实；Learning Engine 负责结构化更新；LLM 只在当前阶段读取经过选择的上下文并生成受 schema 约束的解释或候选。

## 7.2 三种记忆必须分开

### Episodic Memory

记录某项目发生过的事件：创建设计、执行实验、导入数据、观察到结果、人工否决候选。

### Semantic Memory

记录可复用的、带来源和适用域的知识：某干预在何宿主/条件/组合中产生何结果。不能由单次实验自动升级为全局规律。

### Procedural/Policy Memory

记录候选排序器、acquisition policy 或模型参数的版本变化。每次更新必须可回滚、可比较并绑定训练数据快照。

## 7.3 失败学习的正确含义

失败学习不是：

```text
pykF KO caused low growth once → permanently down-rank pykF KO
```

而是：

```text
Context + Design + Expected Outcome + Observed Outcome + QC
→ classify failure
→ assess competing explanations
→ assign causal confidence
→ define applicability scope
→ update local hypothesis/policy
→ validate update on later evidence
```

必须允许结论为 `inconclusive`。低质量数据、污染、批次错误或构建未成功不能成为对生物干预的负面证据。

---

# 八、目标数据模型（必须实现或等价实现）

## 8.1 Project

```yaml
Project:
  project_id: uuid
  name:
  host_definition:
  target_product:
  objectives: []
  constraints: []
  current_design_branch:
  current_design_version_id:
  status:
  created_at:
  updated_at:
  owners: []
```

## 8.2 DesignVersion：不可变版本

```yaml
DesignVersion:
  design_version_id: uuid
  project_id: uuid
  version_label: strain_v1
  parent_version_ids: []
  branch_name:
  genotype_manifest:
    baseline_strain:
    modifications: []
  engineering_decision_ids: []
  created_from_learning_cycle_id:
  rationale_snapshot_id:
  status: proposed|approved|built|tested|retired
  created_at:
```

设计版本必须不可变。修改产生新版本；禁止覆盖旧 genotype。版本比较应由结构化 genotype diff 完成，而不是比较报告文本。

## 8.3 EngineeringDecision

```yaml
EngineeringDecision:
  decision_id: uuid
  target:
  operation: knockout|knockdown|overexpression|mutation|integration|promoter_tuning|other
  mechanism_hypothesis_ids: []
  expected_effects: []
  risks: []
  evidence_ids: []
  implementation_spec:
  validation_spec:
  confidence:
  approval_state:
```

## 8.4 ExperimentPlan 与 ExperimentRun 分离

```yaml
ExperimentPlan:
  experiment_plan_id: uuid
  project_id: uuid
  design_version_ids: []
  hypotheses_tested: []
  controls: []
  factors: []
  response_variables: []
  acceptance_criteria: []
  protocol_ref:
  approval_state:

ExperimentRun:
  experiment_run_id: uuid
  experiment_plan_id: uuid
  executed_design_version_ids: []
  execution_status:
  deviations: []
  sample_manifest_ref:
  started_at:
  completed_at:
  operator_or_source:
```

计划与实际执行必须分离，以记录 protocol deviation 和真实样本身份。

## 8.5 DataAsset 与 Observation 分离

```yaml
DataAsset:
  data_asset_id: uuid
  experiment_run_id: uuid
  file_uri:
  checksum:
  media_type:
  assay_type:
  parser_version:
  schema_version:
  units:
  sample_mapping_ref:
  qc_status:
  provenance:

Observation:
  observation_id: uuid
  data_asset_ids: []
  subject_design_version_id:
  condition_ref:
  timepoint:
  metric:
  value:
  unit:
  uncertainty:
  replicate_summary:
  qc_flags: []
  analysis_pipeline_version:
```

原始文件永不被 LLM 解释文本替代；派生观察必须指回原始资产、解析器和分析版本。

## 8.6 HypothesisVersion

```yaml
HypothesisVersion:
  hypothesis_version_id: uuid
  hypothesis_family_id: uuid
  statement:
  mechanism_graph_ref:
  predicted_observations: []
  supporting_evidence_ids: []
  contradicting_evidence_ids: []
  alternatives: []
  posterior_status: supported|weakened|rejected|inconclusive
  confidence:
  applicability_scope:
  parent_hypothesis_version_id:
```

假设也要版本化。新数据不能改写旧判断，只能生成新版本。

## 8.7 FailureCase

```yaml
FailureCase:
  failure_case_id: uuid
  project_id: uuid
  design_version_id:
  experiment_run_id:
  failure_class:
  expected_outcome:
  observed_outcome_ids: []
  data_qc_status:
  candidate_causes: []
  causal_confidence:
  applicability_scope:
  policy_update_proposal:
  human_review_state:
  resolution_status:
```

`failure_class` 至少区分：construction、execution、measurement、schema/tool、biological null、hypothesis contradiction、tradeoff、safety/constraint、inconclusive。

## 8.8 LearningCycle

```yaml
LearningCycle:
  cycle_id: uuid
  project_id: uuid
  input_design_versions: []
  experiment_run_ids: []
  accepted_observation_ids: []
  hypothesis_updates: []
  model_update_ids: []
  policy_update_ids: []
  next_design_version_ids: []
  human_decisions: []
  status:
```

---

# 九、持久化策略：Event Sourcing + Materialized Views

## 9.1 事件账本

所有重要改变追加为不可变事件：

```yaml
ProjectEvent:
  event_id:
  project_id:
  event_type:
  entity_type:
  entity_id:
  payload_ref:
  actor_type: human|agent|tool|external_system
  actor_id:
  causation_id:
  correlation_id:
  workflow_run_id:
  timestamp:
  schema_version:
```

推荐事件：`PROJECT_CREATED`、`DESIGN_PROPOSED`、`DESIGN_APPROVED`、`EXPERIMENT_PLANNED`、`RUN_RECORDED`、`DATA_INGESTED`、`QC_COMPLETED`、`OBSERVATION_DERIVED`、`HYPOTHESIS_UPDATED`、`FAILURE_CLASSIFIED`、`POLICY_UPDATE_APPROVED`、`REDESIGN_CREATED`。

## 9.2 读取模型

为界面和 Agent 构建可重建的物化视图：

- Project Timeline；
- Design Lineage Graph；
- Current Biological State；
- Experiment Matrix；
- Hypothesis/Evidence Graph；
- Failure Registry；
- Model/Policy Registry。

任一视图都应能从事件账本重建。事件更正使用补偿事件，不直接删除历史。

## 9.3 并发与幂等

- 上传、解析和事件写入使用 idempotency key；
- 写入实体使用 optimistic locking / expected version；
- 重试不得产生重复 Observation 或重复设计版本；
- checksum 相同的数据资产应提示重复而不是静默导入两次。

---

# 十、Iterative Design Loop 状态机

## 10.1 一级状态

```text
PROJECT_CONTEXT_READY
→ DESIGN_BASELINE_CAPTURED
→ DESIGN_PROPOSED
→ HUMAN_DESIGN_GATE
→ BUILD_TEST_HANDOFF
→ WAITING_FOR_RESULTS
→ DATA_INGESTION
→ DATA_QC
→ OBSERVATION_EXTRACTION
→ RESULT_INTERPRETATION
→ HYPOTHESIS_UPDATE
→ FAILURE_OR_SUCCESS_CLASSIFICATION
→ LEARNING_UPDATE_GATE
→ REDESIGN_OR_STOP_DECISION
→ NEW_DESIGN_VERSION / PROJECT_PAUSED / PROJECT_COMPLETED
```

`WAITING_FOR_RESULTS` 是合法、可持久恢复的状态，不得因一次进程结束而丢失。

## 10.2 Gate 规则

### Data Identity Gate

无法将样本映射到项目、设计版本、实验运行、条件和重复时，禁止进入生物学解释。

### Data QC Gate

QC 不通过时，可要求重传、重新解析、排除无效样本或标记 inconclusive；不得直接生成失败学习。

### Genotype Verification Gate

若实际构建未被确认，不得将表型结果归因于计划 genotype。

### Hypothesis Update Gate

必须对预期观察、实际观察、替代解释、证据方向和不确定性逐项比较。

### Policy Update Gate

跨项目或全局权重更新必须有足够证据和人工批准。单次项目观察默认只能更新 project-local policy。

### Redesign Gate

新设计必须声明保留、撤销和新增哪些修改，以及每项改变源自哪条观察/假设更新。

---

# 十一、实验反馈入口

## 11.1 第一阶段支持的输入

优先完成清晰、可验收的适配器：

- 实验元数据表 / sample manifest；
- 生长曲线或汇总指标 CSV；
- 目标产物/代谢物定量 CSV；
- proteomics protein matrix 与分析元数据；
- genotype verification 结果；
- 用户手工录入的结构化实验结论。

不要在未实现解析器时声称支持所有 omics。

## 11.2 上传流程

```text
Upload
→ checksum & type detection
→ project/run/sample binding
→ schema validation
→ unit normalization
→ QC
→ parser creates observations
→ user preview/confirm
→ observations committed
```

手工结论必须标注 `source_type: human_assertion`，不能与仪器派生数据混同。

## 11.3 插件式解析器接口

```python
class DataIngestor:
    def can_handle(self, asset_metadata) -> bool: ...
    def validate(self, asset) -> ValidationReport: ...
    def parse(self, asset, sample_manifest) -> ParsedDataset: ...
    def qc(self, parsed) -> QCReport: ...
    def to_observations(self, parsed, qc_report) -> list[Observation]: ...
```

每个 parser 和 analysis pipeline 必须版本化并可复跑。

---

# 十二、Learning Engine：如何从结果到再设计

## 12.1 五步更新

1. **Expectation matching**：把每项 EngineeringDecision 的预期效应映射到可测指标；
2. **Observation comparison**：计算方向、效应量、不确定性和阈值是否满足；
3. **Failure classification**：区分技术失败、生物负结果和权衡失败；
4. **Hypothesis revision**：更新支持/反对证据和竞争假设，不强迫二元接受/拒绝；
5. **Redesign generation**：基于更新后的假设生成多个候选，再由规则、模型和 Human Gate 选择。

## 12.2 策略路由

```text
明确、低维、连续/离散参数空间 + 可量化目标
  → Bayesian optimization / active learning candidate

组合基因设计 + 数据稀少
  → mechanistic rules + constrained candidate generation + conservative ranking

机制模型可用
  → simulation/model-based hypothesis test

证据冲突、模型 OOD 或高风险
  → request discriminating experiment / human review
```

## 12.3 多目标而非单一产量

至少同时保存：

- target titer/yield/productivity（若可得）；
- growth/fitness；
- substrate consumption；
- by-products；
- genetic stability；
- construction complexity；
- uncertainty and experimental cost。

不得把 `Trp ↑10%, growth ↓40%` 简化为“成功”或“失败”；应按项目约束形成 Pareto/constraint judgement。

## 12.4 防止错误泛化

经验检索必须匹配：species/strain、medium、carbon source、cultivation mode、design background、operation、assay 和目标。相似性不足时只作为弱先验，不能作为硬规则。

---

# 十三、Memory Retrieval：给 LLM 什么，不给什么

## 13.1 Context Builder

LLM 每一步只接收一个可审计的 `ContextBundle`：

```yaml
ContextBundle:
  project_summary:
  active_design_version:
  relevant_ancestors: []
  current_experiment_and_qc:
  accepted_observations: []
  active_hypotheses: []
  relevant_failure_cases: []
  applicable_evidence: []
  policy_and_model_versions: []
  omissions_and_token_budget:
```

## 13.2 检索顺序

1. 精确 ID 和结构化过滤；
2. 项目/设计血缘过滤；
3. 宿主和实验条件匹配；
4. 时间与状态过滤；
5. 最后才使用语义相似度补充文本。

向量检索不能替代数据库主键、版本关系或科学条件过滤。

## 13.3 来源冲突

优先级不是简单“实验数据永远大于论文”：

- 当前项目高质量直接观察：更新本项目状态的最高优先级；
- 重复验证/多来源证据：可提高可迁移性；
- 文献证据：提供机制和外部先验；
- LLM 推断：只能生成待验证假设。

所有冲突均保留，不覆盖删除。

---

# 十四、Human-in-the-loop 与安全边界

必须人工确认：

- 新的菌株设计被标记为 approved/build-ready；
- 将实验数据与样本/菌株绑定；
- 排除样本或覆盖 QC；
- 将单项目经验提升为跨项目 policy；
- 高风险或证据不足的设计继续推进；
- 执行真实实验或对接自动化设备（若未来接入）。

系统必须允许暂停、终止、回滚读取视图和撤销未批准的 policy update。已经发生的事件不得从审计轨迹中消失。

---

# 十五、建议代码模块

先审计仓库命名与依赖，不得机械创建重复层。若现有结构无等价能力，建议：

```text
harness/
  projects/
    models.py
    service.py
    repository.py
    status_view.py
  memory/
    event_store.py
    views.py
    context_builder.py
    retrieval.py
    compression.py
    knowledge_claims.py
  designs/
    models.py
    lineage.py
    genotype_diff.py
    decision_diff.py
  constructs/
    models.py
    verification.py
  experiments/
    models.py
    ingestion/
    qc/
  analysis/
    models.py
    provenance.py
  cell_state/
    snapshots.py
    trajectories.py
  learning/
    hypotheses.py
    outcome_classifier.py
    policy_registry.py
    strategy_router.py
    redesign.py
  workflow/
    iterative_loop.py
    gates.py
  api/
    projects.py
    designs.py
    experiments.py
    learning.py
```

存储层优先使用事务型关系数据库保存身份、版本和关系；对象存储保存原始数据资产；向量索引仅作辅助语义检索。开发环境可使用 SQLite，但 schema 与迁移应支持后续 PostgreSQL。

---

# 十六、API/产品最小能力

至少提供等价接口：

- 创建/读取项目；
- 读取可由事件重建的 Project Status、阻塞项和 Next Action；
- 创建设计版本、查看 lineage 和 genotype diff；
- 比较两个版本的 genotype、decision、evidence、hypothesis 与 outcome diff；
- 登记实际 Construct、构建状态及 genotype verification；
- 创建实验计划与记录实际运行；
- 上传数据资产、绑定 sample manifest、查看 QC；
- 登记和导出 AnalysisRun 的输入、参数、环境、输出与复现状态；
- 预览并确认派生 Observation；
- 触发/查看 hypothesis update；
- 查看 failure case 与适用范围；
- 生成 redesign candidates；
- 人工批准/拒绝设计与 policy update；
- 提交、评审、批准、降级或撤销 KnowledgeClaim；
- 查看 BiologicalStateSnapshot 与 CellStateTrajectory，并比较预测—观测残差；
- 恢复等待中的 DBTL cycle；
- 导出完整项目审计包。

界面第一阶段至少展示：Project Status、Project Timeline、Design Lineage/Diff、Construct Status、Experiment Results、Analysis Provenance、Hypothesis Changes、Failure/Learning、Knowledge Claims、Next Action。聊天不得替代这些项目视图。

---

# 十七、实施顺序

## Phase 0：代码与数据审计

- 定位当前 run state、workspace、report、tool record 的保存方式；
- 找出可复用 schema、数据库、API 和前端组件；
- 运行现有测试，记录 baseline；
- 明确问题 1 Workflow Engine 的真实实现状态。

## Phase 1：持久项目账本

- Project、Event Store、schema migration；
- Project Timeline；
- 幂等、事务和审计。

## Phase 2：设计版本图

- DesignVersion、EngineeringDecision、genotype manifest/diff；
- 分支、父子关系和状态迁移；
- 人工 design gate。

## Phase 3：实验和数据反馈

- ExperimentPlan/Run、DataAsset、sample manifest；
- 首批解析器、unit/QC；
- Observation 预览与确认。

## Phase 4：Learning Loop

- HypothesisVersion、FailureCase、LearningCycle；
- expectation comparison 与 outcome classification；
- redesign 创建新版本。

## Phase 5：策略学习

- project-local policy registry；
- 可替换 optimizer/acquisition strategy；
- 跨项目更新默认关闭，待证据和治理成熟后启用。

不得跳过 Phase 1–3 直接实现“自我学习 Agent”。

---

# 十八、测试与验收标准

## 18.1 单元测试

- 不可变 DesignVersion 不能被覆盖；
- genotype diff 正确识别新增、删除、修改和保留操作；
- 相同上传幂等，不重复生成 Observation；
- 无 sample mapping 的数据被 Data Identity Gate 拦截；
- QC failed 数据不能更新 biological policy；
- Hypothesis 更新生成新版本并保留旧版本；
- compensation event 能重建正确视图；
- Context Builder 不混入其他项目或不适用条件的数据。

## 18.2 集成场景 A：L-色氨酸两轮 DBTL

初始设计：`trpE S40F + AnTrpC replacement + ΔtnaA`。

导入结果：Trp 提升 10%，growth 下降 40%，蛋白组提示目标通路表达变化，并包含完整样本映射与 QC。

系统必须：

1. 保存 v0 及实验计划/实测运行；
2. 不把该结果简单标为成功；
3. 形成 tradeoff failure/constraint violation；
4. 列出代谢负担、组合效应、表达强度等竞争解释；
5. 更新假设而非宣称单一因果；
6. 创建 v1，明确相对 v0 的 retain/remove/add；
7. 新轮不得再次无解释地推荐完全相同设计；
8. 能从 v1 回溯到触发它的 Observation 和人工决策。

## 18.3 集成场景 B：技术失败不能污染生物记忆

若 genotype verification 失败或样本错配：

- 标为 construction/data identity failure；
- 不降低干预的生物学推荐权重；
- 建议重构或重新检测；
- Policy Update Gate 必须拒绝全局更新。

## 18.4 集成场景 C：跨条件不可错误泛化

同一设计在 glucose minimal medium 与 rich medium 下结果相反时：

- 保留两个 BiologicalStateSnapshot；
- FailureCase 带各自 applicability scope；
- 检索时按条件返回；
- 不生成无条件的“该改造有效/无效”。

## 18.5 集成场景 D：等待与恢复

创建实验计划后关闭进程，数日后导入结果：

- 项目恢复到 `WAITING_FOR_RESULTS`；
- 结果绑定正确 run 和 design；
- workflow 从 Data Ingestion 继续，而不是重新做第一次设计。

## 18.6 科学与工程指标

| 指标 | 最低要求 |
|---|---|
| Traceability | 每个 redesign 可回溯至设计、实验、数据、观察、假设和审批 |
| Version integrity | 旧设计、旧假设和旧模型不可被覆盖 |
| Data identity | 未绑定样本/条件/版本的数据 100% 被拦截 |
| Failure hygiene | 技术失败不得自动变成干预负证据 |
| Context isolation | 跨项目状态无泄漏 |
| Recovery | 等待实验后可跨进程恢复 |
| Biological conditionality | 结论保留宿主、培养和 genotype 背景 |
| Calibration | confidence 有结构化依据，不使用纯 LLM 自评 |
| Sample efficiency | 若使用 optimizer，报告相对 random/rule baseline 的效率 |
| Human governance | 所有 build-ready 和跨项目 policy 更新均有明确审批 |

验收不能只由另一个 LLM 阅读报告打分；必须包含数据库约束、schema 断言、确定性测试、对抗案例和生物专家复核状态。

---

# 十九、论文到代码映射

| 论文洞见 | 代码/数据模块 | 本项目实现边界 |
|---|---|---|
| Virtual Cell 的 holistic/mechanistic/dynamic/predictive | `BiologicalStateSnapshot`, `HypothesisVersion`, model registry | 作为目标与状态约束，不宣称已建成完整 Virtual Cell |
| 多模态、时间序列、扰动数据重要 | `DataAsset`, condition/time/perturbation fields | 先实现可扩展 schema 与少量适配器 |
| Coscientist 模块化 Planner 与实验反馈 | iterative workflow + tool/action contracts | LLM 不直接拥有持久状态或无约束执行权 |
| 用先前数据指导下一动作 | `LearningCycle`, `strategy_router`, `redesign` | 只消费通过 QC 的 Observation |
| Coscientist 的格式/工具纠错 | error taxonomy + retry paths | 与 biological failure 分开 |
| SDL 的 design/result databases | DesignVersion + Experiment/Data repositories | 使用稳定 ID 和 provenance 连接 |
| Adam 的逻辑模型与假设循环 | hypothesis graph + model applicability gate | 结论依赖模型准确性，保留不确定性 |
| BioAutomata acquisition policy | policy registry + batch candidate selection | 组合 genotype 整体记录，禁止单基因粗暴归因 |
| SAMPLE 的 GP/BO | optimizer adapter + model registry | 仅在适合的定义域内启用并对比基线 |
| SDL 人类问责与暂停能力 | Human Gates + audit + pause/terminate | 当前默认人类执行湿实验 |

---

# 二十、Claude 修改时的硬性要求

1. 先输出当前架构审计和文件级修改计划，再改代码。
2. 复用问题 1 的 Workflow Engine，不另造冲突状态机。
3. 所有核心实体使用稳定 ID、schema version 和时间戳。
4. 所有设计、假设、模型与 policy 更新采用版本化，不覆盖历史。
5. LLM 输出必须先过 schema 和 Gate，不能直接写成 confirmed fact。
6. 原始实验文件、派生数据、Observation 和解释分层保存。
7. 每个 failure 必须分类、带 QC 和适用域；允许 inconclusive。
8. 单次失败不得自动更新跨项目策略。
9. 真实实验动作保持 Human Gate；不得凭 prompt 自动执行高影响操作。
10. 新增数据库迁移、测试、API 文档和最小 demo。
11. 保持现有可用功能与 API，若必须破坏兼容须提供迁移说明。
12. 不得用占位函数、硬编码示例或报告文本冒充已实现闭环。

---

# 二十一、Claude 最终交付格式

完成后必须提交：

1. **架构审计**：原系统为何是 one-shot，状态在哪里丢失；
2. **修改清单**：逐文件说明新增/修改内容；
3. **数据模型与迁移**：表、约束、版本和升级方式；
4. **DBTL 状态图**：进入/退出/Gate/等待/恢复规则；
5. **运行说明**：如何创建项目、创建 v0、导入结果、生成 v1；
6. **测试报告**：单测、集成测试、失败测试和 baseline 对比；
7. **演示记录**：用 Trp v0 → 实验反馈 → v1 展示完整 trace；
8. **未完成能力**：明确哪些 omics parser、模型或 optimizer 尚未实现；
9. **风险与后续**：数据质量、因果归因、跨项目迁移和自动实验边界。

---

# 二十二、完成前自检

Claude 在宣布完成前必须逐项回答：

- 关闭服务后项目状态能否恢复？
- 某项设计为何进入 v1，能否回溯到原始数据？
- v0 是否仍可读取和重放？
- 上传错配样本时系统是否阻止解释？
- 技术失败是否被错误写成基因干预失败？
- 同一改造在不同培养条件下是否被错误合并？
- LLM 能否绕过 Gate 直接更新 policy？答案必须是否。
- 单次项目失败能否自动改变其他项目？答案默认必须是否。
- 下一轮完全重复旧设计时，系统是否要求显式理由？
- optimizer 是否有适用域、版本、训练数据快照和基线？
- 人类能否暂停、否决和查看完整审计轨迹？
- 系统是否诚实区分“保存了数据”“更新了假设”“学到了可迁移规律”？
- 跨项目总结能否保留适用条件、冲突证据与来源，而不是输出脱离语境的成功率？
- ExperimentRun 是否绑定不可变 Protocol Version，并保存实际偏差？
- 外部库存或仪器状态过期时，系统是否避免把缓存值声称为当前事实？
- 两名用户并发修改同一版本时，系统是否显式检测冲突而非静默覆盖？
- 新 ModelVersion 能否重放其训练数据、基线评估、Prediction 与 Residual，旧预测是否仍可读取？
- 运营 KPI 是否会诱导系统绕过 QC、审批或科学不确定性？答案必须是否。

若任一项无法用代码、测试或数据约束证明，不得宣称问题 2 已闭环。

---

# 二十三、最终判断

三篇论文共同支持的不是“给 Agent 加一个更长的 prompt memory”，而是：

> **以条件化生物状态为研究对象，以不可变项目事件为事实来源，以设计和假设版本图承载演化，以 QC 后的实验观察驱动受控更新，并让算法和人类共同决定下一轮设计。**

这里的 Project 是承载 DBTL 历史、权限和资产的持久容器；Cell / Biological System 才是预测、扰动、观测和学习最终指向的科学对象。Stakeholders 只提供需求、使用视图和治理责任，不能替代这两个系统中心。

本问题完成后的 Agent 应从：

```text
AI Biology Design Report Generator
```

升级为：

```text
Persistent, Traceable, Human-Governed DBTL Engineering System
```

不得把完成结果重新表述为 `PI Assistant`、`Multi-role Scientific Agent`、`ChatGPT for Scientists` 或以角色为中心的“科研项目操作系统”。若实现文档需要介绍角色，必须使用 `requirement source / user / approver` 等关系描述，并回指相应 System Requirement。

但仍需诚实限定：实现 Memory 与 Iterative Design Loop，是走向 AI Virtual Cell 的必要条件，不等于已经拥有完整 Virtual Cell，也不等于已经实现无人监管的自驱动实验室。

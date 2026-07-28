# 问题 01：Agent 控制权与 Workflow Engine

## 五篇论文蒸馏、理性评判及 Claude 自动化精改 Prompt

> 使用对象：Claude Code / Claude Agent
>
> 项目：E. coli K-12 Synthetic Biology Engineering Agent
>
> 本轮只解决问题 01：**Agent 控制权过度依赖 LLM**。
>
> 不要顺带重构其余 15 个问题；仅在接口层为后续 Bottleneck Diagnosis、Engineering Planner、Evaluator、Design Memory 预留位置。

---

# 一、任务定义

当前系统依靠 system prompt 中的 Phase 0–7 约束 LLM，但阶段推进、工具选择、验证、跳过、回退和终止仍主要由 LLM 自行决定。因此，同一输入可能产生不同主干路径，必要步骤可能被跳过，工具失败后缺少统一处理，运行也难以重放和比较。

本轮目标不是消灭 LLM 的自主性，而是重新划定控制权：

> **Workflow Engine 控制阶段、状态、允许动作和质量门；LLM 只在当前阶段的许可范围内完成局部生物学推理。**

目标架构应是：

```text
确定性流程外壳
    ├── 任务状态与阶段迁移
    ├── 必需步骤与条件分支
    ├── 输入/输出 schema 校验
    ├── 工具权限、超时、重试、降级
    ├── Evidence / Validation Gate
    └── 日志、重放、人工审批
             ↓
受约束的概率推理核心
    ├── LLM 生成阶段内候选
    ├── 解释生物学机制
    ├── 提出竞争假设
    └── 在允许动作中申请下一步
```

本轮完成后，Agent 应从“prompt 描述了一个 workflow”升级为“程序实际执行一个 workflow”。

---

# 二、五篇论文的证据定位

| 编号 | 论文 | 类型 | 本项目主要用途 | 证据边界 |
|---|---|---|---|---|
| 1 | Roohani et al., **BioDiscoveryAgent: An AI Agent for Designing Genetic Perturbation Experiments**, ICLR 2025 | 实证 Agent 研究 | 闭环实验、历史观测进入下一轮、结构化响应、候选合法性处理、critic | 能证明 LLM 可辅助闭环选实验；不能证明自由 LLM 适合控制端到端合成生物 workflow |
| 2 | Bunne et al., **How to build the virtual cell with artificial intelligence: Priorities and opportunities**, Cell 2024, DOI: 10.1016/j.cell.2024.11.015 | AIVC 路线图/观点 | Virtual Cell 与 Agent 的接口、统一状态表示、扰动预测、跨尺度模型、模型评估 | 是长期架构原则，不是已完成的可直接部署系统 |
| 3 | Hérisson et al., **The automated Galaxy-SynBioCAD pipeline for synthetic biology design and engineering**, Nature Communications 2022, DOI: 10.1038/s41467-022-32661-x | 实证 workflow 平台 | 传统合成生物流程主干、工具链、标准化 I/O、可复现执行、知识抽取 schema | 主要面向异源代谢通路设计，不覆盖本项目全部宿主内源改造与诊断任务 |
| 4 | Faure et al., **A neural-mechanistic hybrid approach improving the predictive power of genome-scale metabolic models**, Nature Communications 2023, DOI: 10.1038/s41467-023-40380-0 | 算法/模型研究 | 机制约束 + 数据学习、FBA 代理模型、KO/培养基表型预测、模型适用性门 | 不是通用 Agent workflow 算法；不可把 AMN 直接称为 Workflow Engine |
| 5 | Gao et al., **Empowering Biomedical Discovery with AI Agents** | 综述/观点 | 复合 AI 系统、模块化、记忆、反馈、人类监督、不确定性、安全与评估 | 提供价值观和查缺补漏框架，不能替代工程实现与本项目实证 |

---

# 三、逐篇蒸馏：是什么、为什么、怎么做、能否迁移

## 3.1 论文 1：BioDiscoveryAgent

### 是什么

它将遗传扰动实验形式化为多轮搜索：每轮从候选基因或基因组合中选择一批实验，读取上一轮表型结果，再生成下一轮扰动。论文使用 LLM 的生物学先验解决冷启动，并允许调用 PubMed 检索、Reactome 基因扩展、代码/数据分析和另一个 LLM critic。

其响应被约束为：

1. `Reflection`：解释过去结果和当前判断；
2. `Research Plan`：说明下一轮搜索策略；
3. `Solution`：输出格式化基因列表。

论文还使用“两步候选处理”：先允许 LLM 自由提出基因；若多次产生非法、重复或不足数量的候选，再把剩余合法候选的摘要加入上下文。

### 为什么

传统贝叶斯优化需要专门模型、特征和 acquisition function，在小数据和冷启动阶段受限，也较难解释。LLM 能利用文献先验并将历史观测带入下一轮，同时生成可读的生物学理由。

### 怎么做

核心循环是：

```text
任务描述 + 历史实验结果
        ↓
LLM Reflection / Plan / Solution
        ↓
候选合法性与去重处理
        ↓
执行或从历史数据模拟实验
        ↓
结果写入下一轮上下文
```

可选工具结果被拼接回主 Agent 的 prompt；critic 可以替换部分或全部候选。

### 对本项目的理性判断

**可直接借鉴：**

- 把每轮实验结果作为显式状态，而不是仅保留聊天记录；
- 将“反思—计划—结构化候选”拆成机器可校验字段；
- 候选必须经过基因存在性、重复、数量、允许操作等程序校验；
- 建立 `candidate → validation → experiment/result → next round` 闭环；
- 对长历史做结构化压缩，但保留原始记录引用。

**只能部分借鉴：**

- critic 应作为候选层面的评价节点，而不是无条件接受第二个 LLM 的改写；
- 文献检索和通路扩展应按状态触发，而非每轮固定调用或完全由 LLM 随意决定。

**不应照搬：**

- 单一 prompt 驱动整个科研流程；
- 让 LLM 决定是否走完所有必要阶段；
- 把“输出了理由”视为已排除幻觉；
- 把工具数量增加等同于性能提高。论文显示，工具对较弱模型可能有帮助，但对 Claude 3.5 Sonnet 等强模型未稳定产生显著收益；工具必须经过任务匹配和消融验证。

**对问题 01 的结论：**该论文证明 LLM 适合做闭环中的候选生成器和结果解释器，却没有证明它应成为顶层流程控制器。

---

## 3.2 论文 2：AI Virtual Cell（AIVC）

### 是什么

论文提出 AIVC 的长期愿景：构建跨物种、模态、数据集和物理尺度的统一生物状态表示（Universal Representation, UR），再由一组 Virtual Instruments 对该表示进行读取、转换和预测，例如扰动后的状态变化、状态解码、跨尺度推断和实验引导。

其核心不是一个聊天 Agent，而是：

```text
多模态、多尺度生物数据
          ↓
统一生物状态表示 UR
          ↓
Virtual Instruments
  ├── 状态解码
  ├── 扰动响应预测
  ├── 跨尺度转换
  ├── 不确定性估计
  └── 数据生成建议
```

### 为什么

细胞状态跨越 DNA、RNA、蛋白质、代谢物、细胞器、细胞和组织尺度；单一模态或单一任务模型难以泛化到新状态和未见扰动。统一表示有望让不同预测工具共享状态，并缩小机制假设空间。

### 怎么做

论文建议：

- 使用跨模态、跨尺度的表示学习；
- 引入生物学归纳偏置，而非完全黑箱拟合；
- 用编码器把不同观测映射到 UR，用解码器/生成模型输出具体模态；
- 用扰动模型预测基因、化学和环境干预后的状态；
- 让预测携带不确定性并指导下一轮数据生成；
- 建立强调泛化、跨模态能力、新机制发现和真实生物学有效性的 benchmark。

### 对本项目的理性判断

**现在可用的不是“训练一个 AIVC”，而是采用其接口思想。**

当前 Agent 应定义统一的 `BiologicalState`，至少包含：

- chassis / strain / genotype version；
- medium / substrate / culture condition；
- target phenotype 与当前基线；
- pathway / reaction / gene / protein / metabolite 状态；
- 已执行扰动及结果；
- 数据模态、来源、时间点和不确定性；
- 可调用的预测器及其适用域。

未来 vEcoli、FBA、蛋白质组、转录组或其他 Virtual Cell 模型应作为 `VirtualInstrument` 接入 Workflow Engine，而不是让 LLM 把模拟结果当普通文本随意解释。

**暂不实施：**训练跨物种、多尺度基础模型；把 UR 直接等同于知识图谱；宣称 Agent 已具备因果预测能力。

**对问题 01 的结论：**AIVC 不提供状态机，但强烈支持“共享的结构化生物状态 + 可替换预测器”架构。Workflow Engine 应控制何时调用哪个 Virtual Instrument，并校验其输入域和不确定性。

---

## 3.3 论文 3：Galaxy-SynBioCAD

### 是什么

这是一个将合成生物学和代谢工程工具串联为可复现流程的平台。论文给出的端到端主干包括：

1. 选择 chassis 与 target；
2. 逆合成生成从目标化合物回到宿主代谢物的反应网络；
3. 枚举候选通路；
4. 为反应匹配酶序列；
5. 按热力学、FBA 产率/通量、酶可得性、通路长度和毒性等排序；
6. 设计 promoter、RBS、基因顺序、载体和组合实验；
7. 输出 DNA assembly / transformation 所需设计与液体工作站脚本。

系统以 SBML 表示底盘、反应和通路，以 SBOL 表示遗传构件，并通过标准 I/O 连接工具。论文在文献/专家验证路径上报告：机器学习全局评分使目标路径进入 top 10 的比例为 83%。

### 为什么

传统工具分散、安装困难、参数和格式不统一，导致流程不可复现、难组合、难交给非程序用户。科学 workflow 的价值在于将数据和工具组织成明确、可配置、可追踪的步骤。

### 怎么做

论文实现三类 workflow：

- `Retrosynthesis`：RetroPath2.0 / RP2Paths 等生成候选路径；
- `Pathway analysis`：Selenzyme、热力学、FBA 与 ML/global scoring 等注释和排序；
- `Genetic design and engineering`：SBML→SBOL、OptDoE、DNA Weaver、DNA-Bot 等生成构建设计和自动化脚本。

### 对本项目的理性判断

**这是五篇中最适合作为程序主干参考的论文。** 可迁移内容包括：

- 主阶段由 workflow 定义，不由 LLM 临时发明；
- 每个节点必须声明输入、输出、版本、参数、状态和错误；
- 工具间以标准化对象传递，不以自然语言段落传递；
- pathway candidate 与 construct candidate 分开；
- 多指标评分必须保留各子分数，不能只给一个总分；
- 可保存、重跑并比较 workflow run；
- 文献知识库应抽取为可进入工作流的数据字段。

建议从论文抽象出 `EngineeringEvidenceRecord`：

```yaml
problem:
biological_context:
host_strain:
target:
substrate:
pathway:
mechanism:
intervention:
implementation:
  gene:
  operation:
  promoter:
  rbs:
  copy_number:
  vector_or_locus:
condition:
outcome:
tradeoff:
validation_method:
evidence_source:
evidence_level:
```

**不能直接照搬：**本项目主要目标是 E. coli K-12 的瓶颈诊断和宿主工程，不总是从异源产物逆合成开始；因此 retrosynthesis、酶搜索和 DNA 自动装配都应是条件分支，而不是每次必经步骤。

**对问题 01 的结论：**程序化 workflow、标准化 I/O、运行记录和节点级可复现性，应成为本轮重构的主体。

---

## 3.4 论文 4：AMN 神经—机制混合模型

### 是什么

论文把人工神经网络与 genome-scale metabolic model 的稳态、化学计量和反应边界约束结合，提出 Artificial Metabolic Networks（AMNs）。其目的不是让神经网络自由生成通量，而是让训练过程受到 FBA 机制约束。

论文主要有：

- `AMN-Wt`：基于网络权重的机制层；
- `AMN-LP`：可微/代理的线性规划机制层；
- `AMN-QP`：二次规划机制层；
- `AMN-Reservoir`：先用 FBA 模拟数据训练 AMN，再冻结机制代理，在前端训练小网络，将培养基组成映射到更合适的 uptake flux/bounds。

损失函数不仅拟合表型，还惩罚违反化学计量稳态、通量边界和 KO 约束的结果。论文展示了培养基条件下生长率和 E. coli 单基因 KO 表型预测。

### 为什么

经典 FBA 可解释且满足机制约束，但定量预测高度依赖 uptake flux 等难测参数；纯 ML 可以拟合复杂关系，却通常需要大数据且可能违反生物约束。混合模型利用两者互补：数据校准未知关系，机制模型限制可行空间。

### 怎么做

抽象后的算法流程为：

```text
培养基组成 / KO 状态 / 实验观测
             ↓
可训练神经映射
             ↓
FBA 代理机制层
             ↓
通量与生长表型
             ↓
数据拟合损失 + 稳态约束 + 边界约束 + KO 约束
```

### 对本项目的理性判断

**近期可借鉴的是“机制约束推理原则”，不是立即重写 FBA。**

Workflow Engine 应把预测器分成：

- `mechanistic`：FBA / vEcoli 等；
- `data_driven`：统计/ML；
- `hybrid`：AMN 类模型；
- `literature_inference`：基于证据的 LLM 推断。

任何模型输出都必须带：模型版本、输入条件、适用域、假设、约束是否满足、不确定性和验证状态。LLM 不得覆盖模型硬约束。

只有在以下条件满足时才考虑接入 AMN：

- 已有适配 K-12 与目标培养条件的可靠训练数据；
- FBA 在相同条件下存在明确且可量化的系统误差；
- AMN 相比 FBA 和简单 ML 在保留约束的同时通过外部验证；
- 推理成本确实成为 workflow 瓶颈，或需要大量培养基/KO 批量筛选。

**不能把论文结果外推为：**AMN 能完成瓶颈因果诊断、适用于所有产物、能替代 vEcoli，或能直接控制 Agent workflow。

**对问题 01 的结论：**它提供的是“受约束的局部预测模块”范式：学习模型可以灵活，但必须服从形式化生物约束。这与“LLM 受 Workflow Engine 约束”在系统设计上同构。

---

## 3.5 论文 5：Biomedical AI Agents 综述

### 是什么

论文将 AI scientist 定义为复合系统：人类、LLM、专业 ML 模型、数据库、工具和实验平台共同完成科研任务。其关键模块包括：

- perception；
- interaction（人—Agent、多 Agent、工具）；
- reasoning；
- short-term / long-term memory；
- feedback、uncertainty、evaluation 与 safety。

### 为什么

生物医学研究不是纯文本问题。单一 LLM 缺乏完整的多模态感知、机制建模、可靠长期记忆、实验执行与安全保证；复杂任务需要被分解，并由不同能力模块协同。

### 怎么做

论文强调：

- 使用结构化记忆支持持续学习；
- 让工具、实验和人类反馈参与推理；
- 按风险划分自主等级；
- 通过不确定性触发提前终止、安全动作或 human-in-the-loop；
- 对事实性、推理、长程计划、工具集成、鲁棒性与真实科研价值分别评估；
- 防止多 Agent 交互产生级联错误。

### 对本项目的理性判断

**可作为顶层治理原则：**

- Agent 是复合系统，不是一个万能 prompt；
- 多 Agent 不是目标本身，只有职责、输入输出和评估可分离时才拆分；
- 自我反思不能替代独立验证；
- 不确定性必须触发程序行为，而不只是报告里写“置信度中等”；
- 涉及实际构建或高风险操作前设置人工审批；
- 记忆必须区分事实知识、项目状态、推断与失败经验。

**不能直接当成已验证方案：**论文是方法论综述，不足以证明某种多 Agent 拓扑、reflection 或 autonomy level 在本项目中效果最好。

**对问题 01 的结论：**应优先构建可审计的复合系统与人机边界，而非追求更高自主性。

---

# 四、跨论文综合判断

## 4.1 五篇论文共同支持的原则

1. 科研设计必须是闭环：设计 → 预测/实验 → 结果 → 更新。
2. 状态应结构化，不能只存在于对话文本。
3. 工具应通过标准接口连接，输出需保留来源、参数和版本。
4. LLM 适合局部假设生成、解释与信息整合，不适合无约束地主导所有关键迁移。
5. 机制/规则约束应优先于语言模型判断。
6. 不确定性、失败和证据不足必须改变下一步动作。
7. 工作流应可追踪、可重放、可比较和可评价。
8. 人类是系统组成部分，关键风险节点需保留审批权。

## 4.2 三种控制方案比较

| 方案 | 稳定性 | 灵活性 | 可重放 | 对非标准任务适应 | 结论 |
|---|---:|---:|---:|---:|---|
| 自由 LLM Agent | 低 | 高 | 低 | 高但不可控 | 不采用 |
| 完全固定线性 pipeline | 高 | 低 | 高 | 低 | 只适合窄任务 |
| 状态图 + 规则 Gate + 阶段内 LLM | 高 | 中高 | 高 | 中高 | 本项目采用 |

## 4.3 最终设计命题

> **把“下一阶段是什么”从 LLM token 中拿出来，放进程序状态；把“这一阶段如何解释生物学问题”保留给 LLM。**

但这还不够。本项目不能只实现一个通用软件工作流，还必须显式承载合成生物学专家的决策链：

```text
Workflow Engine（阶段、状态、权限、迁移、预算）
        ↓
Biological Decision Layer（诊断、机制、干预、验证）
        ↓
LLM / Virtual Instruments（受约束的局部推理与计算）
```

因此，Workflow Engine 是控制骨架，Biological Decision Layer 是领域语义；二者必须在代码和 schema 中同时存在。不得仅把通用 `StageRecord` 换成生物学命名，就声称完成了领域化。

## 4.4 论文到代码的映射

| 论文 | 可迁移机制 | 目标代码职责 | 明确不采用 |
|---|---|---|---|
| BioDiscoveryAgent | 候选—评价—修订闭环、实验反馈更新 | candidate loop、decision revision、observation update | 不让自由 LLM 接管主状态迁移 |
| AI Virtual Cell | 多尺度状态、虚拟仪器、预测与观测区分 | `BiologicalState`、model registry、model applicability gate | 本轮不宣称实现完整 AIVC |
| Galaxy-SynBioCAD | 可组合工作流、工具互操作、可追踪执行 | workflow graph、stage contract、tool provenance | 不强制所有内源代谢任务走 retrosynthesis |
| AMN | 机制约束、代理模型、不确定性驱动采样 | model adapter、uncertainty field、active-learning extension point | 不把 AMN 当 Workflow Engine，不在无模型时伪造预测 |
| Biomedical AI Agents 综述 | 人机边界、复合系统、记忆与评价 | human gate、run memory、evaluation policy | 不把综述观点当作已验证的多 Agent 性能证据 |

Claude 必须在最终报告中把实际文件、类和测试回填到此映射，而不是只复述论文名称。

---

# 五、Claude 必须实现的目标架构

## 5.1 先审计，后修改

在改代码前必须检查并输出当前实现证据：

1. 程序入口、Agent loop、tool registry、provider、web/API 路由；
2. Phase 0–7 分别定义在哪里，是 prompt 约束还是代码状态；
3. 当前 LLM 可以决定哪些动作；
4. 工具结果存放在哪里，是否有统一 run state；
5. 是否已有 run ID、checkpoint、retry、timeout、cancel、resume；
6. API/前端当前依赖的响应 schema；
7. 测试目录与现有测试方式；
8. 未提交改动，避免覆盖用户已有工作。

先生成一份简短的 `current_architecture_audit`，用“文件路径 + 类/函数 + 证据”说明，不允许凭猜测重构。

## 5.2 状态模型

实现或等价实现以下顶层对象：

```yaml
WorkflowRun:
  run_id:
  workflow_version:
  project_id:
  status: queued|running|waiting_user|blocked|failed|completed|cancelled
  current_stage:
  task_spec:
  biological_state:
  stage_records: []
  candidate_designs: []
  engineering_decisions: []
  evidence_records: []
  tool_records: []
  validation_records: []
  decisions: []
  checkpoints: []
  final_report:
```

`StageRecord` 至少包含：

```yaml
stage_id:
attempt:
status:
started_at:
ended_at:
input_snapshot:
output:
schema_valid:
gate_result:
allowed_next_stages:
selected_next_stage:
selection_reason:
model_id:
prompt_version:
tool_call_ids:
error:
```

不得只把这些内容拼成一段 markdown；后端内部必须保留结构化对象。

`BiologicalState` 至少包含以下字段；未知值必须显式为 `unknown` 或带缺失原因，不得静默补全：

```yaml
BiologicalState:
  host:
    species:
    strain:
    reference_genome_version:
  genotype:
    baseline_genotype: []
    engineered_changes: []
  phenotype:
    target_trait:
    target_product:
    baseline_measurement:
    desired_endpoint:
  environment:
    carbon_source:
    medium:
    oxygenation:
    temperature:
    cultivation_mode:
  metabolic_state:
    flux_observations: []
    metabolite_observations: []
    constraints: []
  omics:
    transcriptome_records: []
    proteome_records: []
    metabolome_records: []
  provenance:
    source_record_ids: []
  uncertainty:
    missing_fields: []
    conflicting_fields: []
    assumptions: []
```

`EngineeringDecision` 是领域核心对象，不得用一段推荐文本或普通 `candidate_design` 代替：

```yaml
EngineeringDecision:
  decision_id:
  parent_decision_ids: []
  status: proposed|accepted|rejected|revised|human_review
  diagnosis_id:
  target_entity:
    type: gene|reaction|metabolite|regulatory_element|pathway
    canonical_id:
    display_name:
  operation: knockout|knockdown|overexpression|mutation|insertion|promoter_tuning|rbs_tuning|dynamic_regulation|other
  mechanism:
  expected_effect:
  affected_state_fields: []
  implementation_outline:
  evidence_record_ids: []
  model_prediction_ids: []
  risks: []
  tradeoffs: []
  validation_plan_ids: []
  confidence:
  uncertainty: []
  rejection_reason:
```

每个被接受的工程建议必须能追溯到：诊断/机制、证据或模型、风险、验证计划及其适用条件。以“推荐敲除 `tnaA`”为例，若缺少操作、机制、预期效应、证据和验证字段，则 schema 不合格。

## 5.3 主状态图

结合现有 Phase 0–7 命名迁移，避免无必要破坏前端；语义上至少包含：

```text
INTAKE
  ↓
TASK_NORMALIZATION
  ↓
CONTEXT_AND_EVIDENCE_ACQUISITION
  ↓
SYSTEM_RECONSTRUCTION
  ↓
BIOLOGICAL_DIAGNOSIS
  ↓
BOTTLENECK_PRIORITIZATION
  ↓
ENGINEERING_STRATEGY_GENERATION
  ↓
MODEL_AND_RULE_VALIDATION
  ↓
EXPERIMENT_AND_IMPLEMENTATION_PLAN
  ↓
FINAL_EVALUATION
  ↓
REPORT
```

说明：本轮必须把诊断、瓶颈排序和工程策略设为一级节点，避免后续再次改变主状态图；但只要求建立可运行的节点骨架、结构化输入输出、迁移和 Gate，不要求在问题 01 中完成“问题 4：瓶颈诊断”的全部算法。现有逻辑可以作为临时实现，但必须标记 `implementation_status: scaffold|partial|validated`，禁止把占位节点表述为已经具备专家级诊断能力。

## 5.4 阶段契约

每个阶段必须声明：

- required inputs；
- structured output schema；
- allowed tools；
- entry condition；
- pass / fail / insufficient-evidence 条件；
- retry limit；
- fallback；
- allowed next stages；
- human approval requirement。

LLM 只能返回：

```yaml
stage_output: ...
requested_action: continue|request_tool|request_user|revise|stop
requested_tool:
reason:
confidence:
missing_information: []
```

`requested_action` 只是申请，Workflow Engine 有最终裁决权。

## 5.5 条件分支而非固定全调用

示例规则：

- 输入缺 chassis、target 或关键上下文时 → `waiting_user`，不得静默猜测；
- 目标涉及异源合成路线且宿主无原生通路时 → 允许 retrosynthesis 分支；
- 需要比较代谢通量、产率上限或 KO 可行性，且存在适配模型时 → 允许 FBA；
- 需要动态、调控、蛋白表达或非代谢表型时 → FBA 不得作为唯一裁决；
- 文献证据不足 → evidence acquisition 或明确降级，不得输出高置信度方案；
- 工具输入超出模型适用域 → 阻止调用或标记 out-of-domain；
- 模型、数据库与文献冲突 → 保留冲突记录并进入人工确认/进一步验证；
- 高风险或不可逆的实验执行 → 必须人工批准。

## 5.6 Tool execution policy

工具调用必须经过统一执行层，至少支持：

- schema 校验；
- allowlist（按 stage）；
- timeout；
- 最大重试次数；
- 幂等键；
- 结果缓存；
- provenance；
- 失败分类：transient / invalid_input / unavailable / out_of_domain / fatal；
- fallback 或 safe stop；
- tool result 写入 run state。

禁止让 LLM 直接把任意字符串当工具名或任意参数执行。

## 5.7 Validation Gate

至少建立以下程序门：

1. `SchemaGate`：输出字段、类型、枚举、数量；
2. `IdentityGate`：基因、反应、代谢物、菌株标识合法；
3. `EvidenceGate`：核心主张是否有可定位证据及适用条件；
4. `BiologicalRuleGate`：必需性、质量守恒、宿主范围、操作冲突；
5. `ModelApplicabilityGate`：模型版本、培养条件、适用域；
6. `CandidateDiversityGate`：候选重复、同义反复、机制覆盖；
7. `SafetyHumanGate`：需人工审批的动作。

Gate 输出必须为结构化：

```yaml
status: pass|revise|insufficient_evidence|human_review|fail
violations: []
required_actions: []
next_stage:
```

### Human Gate policy

人工审批不是可选 UI 功能，而是状态机中的正式 Gate。至少将动作分为：

| 等级 | 典型动作 | 默认策略 |
|---|---|---|
| 自动执行 | 文献检索、数据库查询、通路注释、只读模型计算 | 在工具权限与预算内自动运行 |
| 自动提出、人工确认 | 证据冲突下继续、低置信度关键假设、超出模型适用域的解释 | 进入 `waiting_user`，记录待确认问题 |
| 强制人工批准 | essential/conditionally essential gene 干预、核心基因组大规模修改、高风险或不可逆实验方案、绕过失败 Gate | 未批准不得进入实施计划 |
| 禁止 | 无依据伪造实验结果、绕过安全规则、将模型预测写成实验事实 | 直接 fail/safe stop |

审批记录至少包含 `requested_action`、`risk_reason`、`evidence_snapshot`、`approver`、`decision`、`timestamp` 和 `scope`。批准某一动作不等于批准后续所有衍生动作。

## 5.8 重试、回退与终止

- schema 错误：同阶段修复，最多 2 次；
- 工具暂时失败：指数退避或有限重试；
- 无替代数据源：降级并记录，而不是伪造结果；
- 证据不足：回到 evidence acquisition，达到预算上限后输出“不足以支持”；
- 候选全部不合法：回到 candidate generation，并把违反项加入约束；
- 连续两轮没有新增有效信息：停止循环并请求人工判断；
- 任一循环必须有 max attempts / max tool calls / max cost 或 time budget；
- 终止原因必须记录，禁止无限 Agent loop。

## 5.9 记忆与版本

本轮只实现运行级记忆骨架：

- 不把完整聊天记录等同于 memory；
- 保存 task state、实验/模拟观察、被拒候选及原因；
- 区分 `fact`、`observation`、`model_prediction`、`LLM_hypothesis`；
- 每条设计关联 parent design，预留 strain v0 → experiment → strain v1；
- 压缩历史时保留原始记录 ID，保证可追溯。

## 5.10 API 与前端兼容

- 优先兼容现有接口；如必须变更，增加版本化响应或适配层；
- 前端应能读取阶段状态、当前 Gate、工具调用、失败原因和最终报告；
- 不能只显示 LLM 的“思考过程”；应显示可审计的决策依据、证据与状态迁移；
- 不暴露隐藏 chain-of-thought，使用简洁的 `decision_reason`。

---

# 六、建议代码模块边界

在尊重现有仓库结构的前提下，优先形成等价职责，不要求机械采用文件名：

```text
harness/workflow/
  definitions.py       # workflow/stage 定义
  state.py             # WorkflowRun / StageRecord
  controller.py        # 唯一阶段迁移入口
  contracts.py         # stage I/O schemas
  gates.py             # validation gates
  policies.py          # branch/retry/tool/human policies
  checkpoint.py        # 保存与恢复

harness/tools/
  executor.py          # 统一工具执行与 provenance

harness/evaluation/
  run_evaluator.py     # 路径一致性与结果质量
```

不要创建“名义上多 Agent、实质仍由同一 prompt 自由切角色”的结构。首先完成单控制器、明确节点和可测试契约；多 Agent 只作为后续节点实现方式。

---

# 七、测试与验收

## 7.1 单元测试

至少覆盖：

- 合法/非法 stage output；
- 非法阶段跳转被拒绝；
- 当前阶段调用未授权工具被拒绝；
- 重复候选和不存在基因被 Gate 拒绝；
- tool timeout / unavailable / invalid input；
- retry 达上限后停止；
- checkpoint 恢复后状态一致；
- 同一 run 不能重复执行非幂等节点。

## 7.2 集成场景

至少使用以下案例：

1. `提高 E. coli K-12 以葡萄糖生产 L-tryptophan 的能力`；
2. 输入缺少 chassis 或底物；
3. FBA 工具不可用；
4. 文献证据与模型预测冲突；
5. LLM 请求跳过必需验证阶段；
6. LLM 连续返回非法 gene ID；
7. 非代谢目标，验证系统不会滥用 FBA。

## 7.3 生物学基准

软件流程通过不等于科研推理正确。至少建立三类固定 benchmark，并将期望结果写成结构化 assertions；不得只让另一个 LLM 对最终报告打分。

1. **L-tryptophan production / E. coli K-12 / glucose**
   - 能区分前体供给、反馈抑制、竞争/降解和生长负担等竞争性诊断；
   - 至少识别 PEP/E4P 供给与 TrpE 反馈调控属于不同机制层；
   - 每项干预关联对应机制、风险与机制性验证，而非只建议测终点产量；
   - essentiality 未确认时不得给出无条件 KO 实施结论。
2. **L-lysine production / E. coli**
   - 验证工作流不是把色氨酸案例中的固定基因表替换名称；
   - 能形成独立的诊断对象、候选决策和验证计划；
   - 不确定的菌株/培养条件会触发补充信息或降级。
3. **Knockout feasibility / adversarial cases**
   - 输入 essential gene、错误 gene ID、宿主不匹配或互相冲突的改造；
   - `IdentityGate`、`BiologicalRuleGate` 或 `SafetyHumanGate` 必须拦截；
   - 若可替代为 CRISPRi、启动子调节或条件性策略，只能作为新候选重新进入评价，不得静默改写原决策。

每个 benchmark 至少记录：关键诊断召回、无依据主张数、危险改造拦截率、决策—证据可追溯率、决策—验证匹配率，以及人工专家复核结论。当前项目尚无可靠 gold standard 时，应保存专家审阅版本和变更历史，不能虚构准确率。

## 7.4 硬性验收标准

- 相同规范化输入运行至少 5 次，主干必经阶段一致；
- 条件分支差异均能由结构化状态和规则解释；
- LLM 无法直接修改 `current_stage`；
- LLM 无法调用当前 stage 未授权工具；
- 每一步均有 schema-valid input/output 或明确失败；
- 任何失败均有 retry、fallback、human review 或 safe stop 之一；
- 可从 checkpoint 恢复并继续；
- 可导出完整 run trace，对比两次运行差异；
- 证据不足时不会生成“已验证”标签；
- 现有前端和报告核心功能不回归。
- `BiologicalState` 不得是无约束字典或空占位对象；关键缺失值可见；
- 最终建议必须以 `EngineeringDecision` 保存并可逐项追溯；
- 必须通过三类生物学 benchmark 的安全与结构断言，领域质量未通过时不得仅凭 workflow 测试宣告完成。

建议额外记录：成功率、必需阶段跳过率、非法工具调用率、平均重试次数、工具成本、总时长、分支一致性和人工介入率。

---

# 八、实施顺序

1. 审计现有代码和接口；
2. 固化 schema 与 `WorkflowRun`；
3. 将现有 Phase 0–7 映射为程序节点；
4. 实现唯一的 controller 与 transition table；
5. 定义 `BiologicalState` 与 `EngineeringDecision` 并贯穿节点；
6. 接入统一 tool executor；
7. 添加最小 Gate 与 Human Gate policy；
8. 添加 retry / fallback / stop；
9. 增加 checkpoint 和 run trace；
10. 接回现有 API/前端；
11. 完成单元、集成和生物学 benchmark 测试；
12. 用 tryptophan 案例执行 5 次一致性测试；
13. 输出变更说明、残余风险和下一问题接口。

不要先大规模重写前端，不要先训练新模型，不要在本轮实现完整 AIVC 或 AMN，不要通过加长 system prompt 伪装成 workflow 重构。

---

# 九、Claude 最终交付格式

完成后必须报告：

1. **Current-state audit**：原控制权实际在哪里；
2. **Architecture decision**：为何采用状态图 + Gate + 阶段内 LLM；
3. **Paper-to-code mapping**：五篇论文分别影响了哪些设计，哪些没有采用及原因；
4. **Changed files**：逐文件说明；
5. **State graph and contracts**：阶段、分支、回退、终止；
6. **Tests run and results**：不能只说“应当通过”；
7. **Five-run consistency result**；
8. **Biological benchmark result**：规则断言、失败项和专家复核状态；
9. **Backward compatibility**；
10. **Known limitations**；
11. **Deferred items**：明确属于问题 2–16 的内容，不得声称已解决。

若仓库现状与本 Prompt 的类名或 Phase 命名不一致，应保留上述职责和验收标准，基于真实代码做最小、可验证的映射；不得为了形式一致而破坏现有系统。

---

# 十、最终审查问题

在宣告完成前，逐项回答：

- 现在是谁决定下一阶段：程序还是 LLM？
- 必经阶段能否被 LLM 跳过？
- 工具调用是否受 stage allowlist 和 schema 约束？
- 证据不足是否真正改变流程？
- FBA 是否只在适用时调用？
- 同一输入的主干是否可复现？
- 任一结论能否追溯到证据、模型或规则？
- 任一失败能否定位到具体节点？
- run 能否恢复和重放？
- 生物上下文是否保存在有约束、可追溯的 `BiologicalState` 中？
- 每项工程建议是否形成 `EngineeringDecision`，并关联机制、证据、风险和验证？
- 人工审批是否真正阻断状态迁移，而非只显示提示？
- 工作流测试通过时，生物学 benchmark 是否也有独立证据？
- 是否引入了未经论文支持、未经测试的复杂性？

只有上述问题均有代码证据和测试证据，问题 01 才可视为完成。

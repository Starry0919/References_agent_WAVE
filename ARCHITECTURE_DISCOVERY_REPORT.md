# WAVE Scientific Agent Architecture Discovery Report

## 0. 范围、方法与判定口径

本报告恢复的是当前工作树中的真实系统，不评价目标架构，也不把 README 中的愿景自动视为实现。主要证据为 `main.py`、`harness/server.py`、`harness/**`、`frontend/src/**`、`tests/**`、`knowledge/**`、`workflows/**` 与 `pyproject.toml`。当前 Git 工作树存在大规模未提交的目录重组；本报告针对磁盘上现状。全量 `pytest -q` 在 60 秒内未完成，故“TESTED”仅表示存在针对性测试代码，不代表本次已证明全套通过。

状态含义：IMPLEMENTED=有执行代码；WIRED=进入在线调用链；TESTED=有测试文件；UI_EXPOSED=React 路由/页面可达；PARTIAL=只有部分闭环；DESIGNED_ONLY=仅文档、prompt 或 schema；LEGACY=保留兼容路径；UNCERTAIN=证据不足。

## 1. Repository Structure

| 区域 | 角色 | 判定与证据 |
|---|---|---|
| `harness/` | 核心后端与科学模块 | 核心；FastAPI、Agent、状态机、服务、ORM 均在此 |
| `frontend/src/` | React 产品前端 | 核心；`router.tsx` 和 `registry/modules.ts` 定义产品页面 |
| `workflows/synbio_v01`, `synbio_v1` | 阶段内确定性科研处理 | 核心辅助执行层，被 workflow/工具调用 |
| `knowledge/` | DDR、规则、工程动作、模型与论文材料 | 核心数据/知识资产；不是独立推理运行时 |
| `tests/` | 后端与跨模块测试 | 核心验证资产；覆盖 25 个主题目录，另有两套 synbio 测试 |
| `tools/` | 自动发现的用户/领域工具 | 执行扩展层；由服务启动时加载 |
| `web/` | 单文件旧聊天 UI | LEGACY；由 `/legacy/chat` 提供 |
| `docs/`, `analysis/`, `benchmarks/` | 规格、报告、审计、基准 | 辅助证据，不等同于实现 |
| `scripts/` | 数据准备、维护、运行脚本 | 辅助工具 |
| `runs/`, `workflow_runs/`, `project_ledger.db*`, `artifacts/`, `output/`, `tmp/` | 运行时状态与产物 | 运行数据，不是源架构模块 |
| `archive/`, `.pytest_cache`, `__pycache__` | 历史或缓存 | 非当前主链；`archive/` 按名称及用途判为历史保留 |

未发现可安全断言“已废弃”的核心源码目录；只有 `web/` 被服务器明确作为 legacy chat 暴露。

## 2. System Boundary

外部输入包括：用户聊天消息；项目目标与约束；论文/PDF、DOI 与检索请求；实验计划、运行及 CSV/观测数据；诊断证据；设计审批与评审决定；虚拟细胞扰动/模拟请求。证据：会话、projects、paper_extraction、experiments、diagnosis、engineering_design、scientific_evaluation、virtual_cell API。

内部核心是：FastAPI 接入层、通用 LLM 工具循环、程序化科学工作流/统一编排器、领域闭环服务、SQL 项目账本与 JSONL/JSON 检查点、知识与证据对象、React 工作台。

外部工具包括：OpenAI-compatible LLM provider、Crossref/文献来源、HTTP/file 工具、CobraPy/GEM FBA，以及本地文件/SQLite；外部 LIMS、真实库存系统和完备细胞预测模型没有足够实现证据。

最终输出包括：聊天回答与实时 trace；结构化诊断报告；候选设计、Build/Test package 和审批记录；评审与 meta-review；实验观测与学习/知识主张；论文抽取对象、DDR/规则；模拟结果、残差与模型更新提案。

文字边界：

```text
External World (scientist, literature, datasets, experiments, model providers)
  -> FastAPI / WebSocket / React UI
  -> WAVE runtime + orchestrator + domain loops + evidence/knowledge + persistence
  -> reports, designs, plans, decisions, traces, knowledge updates
  -> Human Scientist / external experimental and computational actions
```

## 3. Top-Level Architecture Map

### A. Interaction and API Layer

- Purpose: 提供 React 产品界面、旧聊天界面、HTTP/WS 接口与人工决策入口。
- Evidence: `frontend/src/router.tsx`, `frontend/src/registry/modules.ts`, `harness/server.py`, `harness/api/*`。
- Implementation Status: IMPLEMENTED, WIRED, TESTED, UI_EXPOSED；部分能力 UI 为 PARTIAL。
- Major Components: projects、ideas、diagnosis、design、knowledge、world-model、runtime 页面；FastAPI routers；WebSocket session trace。
- Relationships: 调用所有领域服务；将人工审批回送 workflow/diagnosis/design/evaluation。

### B. Agent Runtime and Orchestration

- Purpose: 一方面运行自由工具调用的 LLM 会话，另一方面以确定性状态机调度科学任务和跨模块 handoff。
- Evidence: `harness/agent.py`, `harness/workflow/controller.py`, `harness/scientific_runtime/*`, `harness/orchestrator/*`, `harness/server.py`。
- Implementation Status: IMPLEMENTED, WIRED, TESTED；scientific runtime UI_EXPOSED；统一编排为 PARTIAL（前端能力表亦标 partial）。
- Major Components: SessionStore/EventBus、WorkflowController、ScientificTask/RuntimeTaskNode、UnifiedWorkflowRun、ModuleHandoffRecord。
- Relationships: 调用诊断、设计、评审、模拟、实验、学习，并记录 transition/gate/handoff。

### C. Evidence and Knowledge Intelligence

- Purpose: 文献发现/核验/抽取，构造 EvidenceObject、provenance、适用性报告、DDR、规则、claim 与工程动作。
- Evidence: `harness/evidence_intelligence`, `evidence_retrieval`, `literature_discovery`, `literature_verification`, `paper_extraction`, `knowledge_distillation`, `knowledge/`。
- Implementation Status: IMPLEMENTED, WIRED, TESTED, UI_EXPOSED；知识蒸馏/部分检索能力为 PARTIAL。
- Major Components: EvidenceObject、EvidenceMatchReport、KnowledgeClaim、paper extraction tasks、DDR provenance/conflicts。
- Relationships: 为诊断、设计和科学评审供证；学习模块可晋升或撤销 claim。

### D. Persistent Project Memory and DBTL

- Purpose: 以关系数据库项目账本保存项目、设计版本、实验、观测、假设、失败、学习与事件，并驱动迭代循环。
- Evidence: `harness/projects`, `designs`, `constructs`, `experiments`, `learning`, `memory`, `workflow/iterative_loop.py`, `harness/db.py`。
- Implementation Status: IMPLEMENTED, WIRED, TESTED；UI_EXPOSED 仅部分；整体 PARTIAL。
- Major Components: ProjectEvent、DesignVersion、ExperimentPlan/Run、DataAsset/Observation、HypothesisVersion、FailureCase、KnowledgeClaim、IterativeCycleState。
- Relationships: 接收设计和实验结果；向诊断/设计提供 context bundle；通过 gate 控制知识更新和 redesign。

### E. Bottleneck Diagnosis

- Purpose: 将观察转为竞争假设、证据关系、模型计算、判别实验、信念更新和可行动决策。
- Evidence: `harness/diagnosis/*`, `harness/api/diagnosis.py`, `tests/diagnosis/*`。
- Implementation Status: IMPLEMENTED, WIRED, TESTED, UI_EXPOSED。
- Major Components: DiagnosisSession、EvidenceLink、HypothesisAssessment、ModelRunRecord、DiagnosticTest、BeliefUpdateEvent、DiagnosisDecision。
- Relationships: 读 evidence/memory/model adapters；handoff 到 engineering design；可接收 evaluation 返回。

### F. Engineering Design and Decision

- Purpose: 从诊断 handoff 生成策略和多候选 portfolio，执行规则/模型评估、Pareto 决策、Build/Test 规划与审批。
- Evidence: `harness/engineering_design/*`, `harness/api/engineering_design.py`, `tests/engineering_design/*`。
- Implementation Status: IMPLEMENTED, WIRED, TESTED, UI_EXPOSED；部分列表/闭环能力为 PARTIAL。
- Major Components: EngineeringStrategy、CandidateDesign、DesignPortfolio、DesignEvaluation、BuildTestPackage、HumanApprovalRecord。
- Relationships: 消费诊断；调用 evidence 与 model adapters；桥接 DesignVersion；交给 scientific evaluation/experiments。

### G. Scientific Evaluation and Governance

- Purpose: 对候选的 claims、证据、模型和规则进行独立评审、比较、meta-review、修订和人工 gate。
- Evidence: `harness/scientific_evaluation/*`, API router, `tests/scientific_evaluation/*`。
- Implementation Status: IMPLEMENTED, WIRED, TESTED；专用 UI 未见顶层路由，故 UI_EXPOSED=PARTIAL。
- Major Components: EvaluationCase、ScientificClaim、EvidenceAssessment、ScientificReview、CriticFinding、MetaReviewDecision、RevisionCycle。
- Relationships: 评审设计；可要求修订或返回诊断；事件写入 evaluation memory/project audit。

### H. Biological World and Virtual Cell

- Purpose: 表达生物实体/状态转换，注册模型，执行扰动模拟、比较、校准、残差和模型更新治理。
- Evidence: `harness/world_model/*`, `harness/virtual_cell/*`, 对应 API 与测试。
- Implementation Status: IMPLEMENTED, WIRED, TESTED, UI_EXPOSED；模型覆盖与真实预测能力为 PARTIAL。
- Major Components: BiologicalEntity、StateTransitionRecord、ModelRegistryEntry、SimulationCase/Run/Result、PredictionResidual、ModelUpdateProposal。
- Relationships: 为诊断/设计/评审提供模型证据；实验残差可形成更新提案，但更新需决策。

### I. Evaluation Metrics and Golden Set

- Purpose: 一致性抽样、DDR 参考评分、golden case 运行和接受报告。
- Evidence: `harness/evaluation_metrics`, `harness/golden_set`, API 与测试。
- Implementation Status: IMPLEMENTED, WIRED, TESTED；UI_EXPOSED=PARTIAL/未见独立页面。
- Relationships: 横向评估 Agent/科学工作流输出，不负责主业务调度。

## 4. Component Relationship Graph（文字版）

```text
React / legacy chat / API clients
  -> FastAPI server
     -> free-form Agent loop -> LLM provider <-> tool registry
     -> Scientific Runtime / Unified Orchestrator
        -> Evidence & Knowledge
        -> Diagnosis -> Engineering Design -> Scientific Evaluation
        -> Virtual Cell / World Model
        -> Experiment Plan/Run -> Observation -> Learning / KnowledgeClaim
        -> human gates at workflow, diagnosis, design, evaluation, model update
     -> Project Ledger / ORM database + append-only events
     -> JSONL session traces + JSON workflow checkpoints
```

调度由 WorkflowController、Scientific Runtime 与 Unified Orchestrator 分层承担；自由聊天中的局部工具选择由 LLM Agent loop 承担。推理由诊断、设计生成/评估、科学评审和阶段处理器共同承担。知识由 evidence/knowledge、learning claims、DDR/rules 与 world model 承担。验证由 gates、scientific evaluation、golden set、metrics、tests 和模型适用性检查承担。设计生成由 engineering_design 承担。记忆与更新由 SessionStore、ProjectEvent 账本、workflow checkpoints、learning 和 model-update governance 承担。

## 5. Runtime 执行流程恢复

系统实际存在至少三类入口，而非单一流程：

1. 聊天：用户消息 -> SessionStore 记录 -> `run_agent_turn` -> LLM 流式输出/工具调用循环 -> tool result -> assistant message -> JSONL 事件；WebSocket 实时推送，可 stop。
2. 程序化科学任务：API 创建 task/run -> runtime/orchestrator 建立节点或跨模块状态 -> gate 检查 -> diagnosis/design/evaluation/simulation/experiment/learning handoff -> pause/人工决定或继续 -> audit trail/final state。
3. 持久 DBTL：项目上下文 -> 设计/审批 -> build/test package -> 等待真实结果 -> 数据 identity/QC -> observation -> hypothesis/failure/knowledge 更新 -> redesign 或 stop。

状态管理：Pydantic workflow snapshots 与 ORM 状态并存。Memory：会话 JSONL、项目事件账本、领域 ORM 表。Trace/logging：EventBus/WS、transition、audit-trail、ProjectEvent。Human approval：workflow、diagnosis、design、evaluation、model update 均有显式接口。Replanning：以 revision、return-to-diagnosis、belief update、redesign 和 orchestrator resume 表达；自由 Agent 也可按工具结果继续循环。

## 6. Knowledge / Evidence / Reasoning 的真实关系

- Evidence 不是纯文本集合：存在 EvidenceObject、EvidenceItem/Link、EvidenceAssessment、EvidenceMatchReport、provenance graph、confidence/applicability 字段与 DOI/document API。
- Knowledge 有多种并行表示：文件型 DDR/规则/工程动作；数据库 KnowledgeClaim/HypothesisVersion；论文抽取的 ExperimentalCase/ideas；World Model 的 BiologicalEntity/StateTransitionRecord。未发现一个统一 ontology 成为所有模块的唯一事实源。
- Reasoning 消费 evidence 和 knowledge，但按用途分散：诊断构建竞争假设与证据关系；设计构建策略/候选；科学评审做独立 critique/meta-review；workflow stages 做确定性转换。
- Biological World Model 已有实体和状态转换 API；Virtual Cell 是计算/预测层。二者相关但不是同一对象模型，也没有证据证明所有诊断与设计都强制通过 world model。
- DDR 是知识资产和评分参考之一，不等于完整决策图；logic chain/decision graph 在不同报告、transition 和 evidence graph 中局部出现，未形成单一全局图数据库。

## 7. DBTL 支持程度

| 阶段 | 当前事实 |
|---|---|
| Design | IMPLEMENTED/WIRED/TESTED/UI_EXPOSED：版本化设计、策略、portfolio、评估、审批 |
| Build | PARTIAL：有 Construct、PhysicalStockRef、BuildTestPackage 和 genotype verification；未证明真实库存/LIMS/自动化构建集成 |
| Test | IMPLEMENTED/PARTIAL：有 ExperimentPlan/Run、CSV ingestion、DataAsset、Observation、QC；实验执行本身在系统边界外 |
| Learn | IMPLEMENTED/WIRED/TESTED/PARTIAL：假设修订、失败分类、claim 晋升/撤销、redesign、残差与模型更新提案；跨项目自动学习和模型自动替换受 gate 限制且非全自动 |

反馈数据是 Observation、FailureCase、HypothesisVersion、KnowledgeClaim、PredictionResidual 与 ModelUpdateProposal；知识晋升和模型更新均不是无条件写入。

## 8. Frontend / Backend / Data Flow

核心前端路由：项目切换；Command Center；Ideas；历史 ideas；Diagnosis workbench/detail/new；Design workbench/detail；Knowledge；Evidence detail；Trust Center；World Model；Scientific Runtime。`metrics` 与 `paper-extraction` 目前重定向到现有页面/标签。Scientific Evaluation、Virtual Cell、Golden Set 没有独立顶层路由证据。

后端入口为 `main.py -> uvicorn -> harness.server:app`。`create_app()` 启动时加载工具、SessionStore、WorkflowController、数据库迁移，并挂载 projects、learning、ideas、paper extraction、literature search、evidence、world model、scientific runtime、diagnosis、engineering design、virtual cell、orchestrator、golden set、metrics、scientific evaluation、experiments 和 simulation 子应用。

```text
React page -> typed frontend API client -> FastAPI router -> domain service/controller
-> ORM project ledger / knowledge files / workflow checkpoint / external provider
-> structured response -> React Query/page state
```

## 9. Implementation Status Matrix

| Component | Code | Connected | Tests exist | UI | Overall |
|---|---:|---:|---:|---:|---|
| Chat Agent + tools + WS | yes | yes | yes | legacy | IMPLEMENTED/WIRED/LEGACY_UI |
| Workflow Controller | yes | yes | yes | partial | IMPLEMENTED/WIRED/TESTED |
| Scientific Runtime | yes | yes | yes | yes | IMPLEMENTED/WIRED/TESTED/UI_EXPOSED |
| Unified Orchestrator | yes | yes | yes | indirect | PARTIAL |
| Projects/Event Ledger/Memory | yes | yes | yes | yes | IMPLEMENTED/WIRED/TESTED; UI partial |
| Evidence retrieval/intelligence | yes | yes | yes | yes | IMPLEMENTED/WIRED/TESTED/UI_EXPOSED |
| Literature discovery/verification | yes | partial | yes | indirect | PARTIAL |
| Paper extraction | yes | yes | yes | yes | IMPLEMENTED/WIRED/TESTED/UI_EXPOSED |
| Knowledge distillation | yes | yes | tests unclear | yes/tab | PARTIAL |
| Diagnosis | yes | yes | yes | yes | IMPLEMENTED/WIRED/TESTED/UI_EXPOSED |
| Engineering design | yes | yes | yes | yes | IMPLEMENTED/WIRED/TESTED/UI_EXPOSED; partial queries |
| Scientific evaluation | yes | yes | yes | indirect | PARTIAL |
| Experiments | yes | yes | project tests | indirect | PARTIAL |
| Learning/knowledge claims | yes | yes | project tests | indirect | PARTIAL |
| World model | yes | yes | yes | yes | IMPLEMENTED/WIRED/TESTED/UI_EXPOSED |
| Virtual cell | yes | yes | yes | no dedicated route | PARTIAL |
| Metrics/golden set | yes | yes | yes | no dedicated route | PARTIAL |
| External LIMS/inventory | reference fields only | no | no | no | DESIGNED_ONLY/PARTIAL boundary |

## 10. Candidate Diagram Topics（不在本阶段画图）

1. Diagram Title: WAVE System Context and Runtime Boundaries. Why Needed: 区分外部科学家/实验/数据源与内部 Agent。Main Question: 系统接收什么、控制什么、输出什么？Important Nodes: UI/API、runtime、external providers、human gates、experiments。Audience: 新成员/负责人。Priority: High。
2. Diagram Title: Runtime and Orchestration Control Planes. Why Needed: 当前有 chat agent、workflow controller、scientific runtime、unified orchestrator 四种控制机制。Main Question: 谁调度谁？Important Nodes: session loop、controllers、handoffs、gates、checkpoints。Audience: backend architects。Priority: High。
3. Diagram Title: Evidence-to-Decision Scientific Chain. Why Needed: 解释证据如何进入诊断、设计和评审。Main Question: claim 的证据和适用性怎样影响决定？Important Nodes: EvidenceObject、Diagnosis、CandidateDesign、ScientificReview、DDR/Claim。Audience: scientists/reviewers。Priority: High。
4. Diagram Title: Persistent DBTL and Knowledge Feedback. Why Needed: 展示跨天等待结果与受治理学习。Main Question: 实验结果如何改变假设、设计和知识？Important Nodes: ProjectEvent、DesignVersion、ExperimentRun、Observation、FailureCase、KnowledgeClaim、redesign。Audience: scientists/data engineers。Priority: High。
5. Diagram Title: Product Surface to Backend Capability Mapping. Why Needed: 后端能力多于独立 UI 页面。Main Question: 每个页面真正调用哪些 API、哪些仍 partial？Important Nodes: routes、typed clients、routers、services。Audience: frontend/product。Priority: Medium。
6. Diagram Title: World Model and Virtual Cell Model Governance. Why Needed: 区分知识表示、模拟执行、残差与更新审批。Main Question: 生物实体与计算模型怎样连接？Important Nodes: BiologicalEntity、StateTransition、SimulationCase、Residual、ModelUpdateProposal。Audience: modelers/scientists。Priority: Medium。

## 11. Current Architectural Ambiguities

- 控制面重叠：WorkflowController、IterativeLoop、Scientific Runtime、Unified Orchestrator 都管理状态/转移；具体产品入口选择规则分散。
- 多种记忆并存：JSONL session、JSON workflow checkpoint、ORM project ledger、evaluation memory；“唯一事实源”依领域而不同。
- 知识表示分裂：DDR 文件、KnowledgeClaim、Hypothesis、paper objects、world-model entities 尚无统一标识/ontology 证据。
- README 编码损坏且可能滞后；代码注释显示若干路由曾“实现但未挂载”，说明接线状态历史上易漂移。
- 前端能力注册表把 orchestrator、design、virtual-cell、evaluation、learning、experiments 标为 partial，并把 memory/consolidated approvals/reviewer authority 标为 absent；这与后端存在相关代码并不矛盾，反映缺少统一产品表面或查询/治理接口。
- `web/` 与 React SPA 并存；前者明确 legacy，可能造成两套交互模型认知混淆。
- DBTL 的 Build/Test 有数据结构和计划，但真实实验执行、LIMS、库存与自动化设备不在当前实现边界。
- Virtual Cell 有丰富 schema/API，但并非所有 adapter 都证明有真实预测计算；不能把 schema 数量当作模型能力。
- 全量测试本次超时，无法给出当前工作树的通过率；“测试存在”与“当前可通过”必须继续区分。
- 当前工作树大规模未提交重组使 Git 历史路径与现行路径不一致；报告以现行磁盘事实为准。

## 12. 结论

WAVE 当前是“多控制面、事件/账本持久化、领域闭环模块化”的科学 Agent 平台，而不是单一 LLM prompt 流程。最强的已实现主链是：项目/证据 -> 诊断 -> 工程设计 -> 科学评审，并可延伸到模拟、实验记录、学习与知识治理。最大的事实性缺口不是模块完全不存在，而是控制面边界、统一知识标识、前端产品暴露以及真实实验/外部系统闭环仍不完整。

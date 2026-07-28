# Synthetic Biology DBTL Engineering OS

# Page 02 — DBTL Engineering Workspace

## Claude Code 完整实现 Prompt

> **用途**：将本文件直接交给 Claude Code，在现有仓库中审计、规划、实现、测试并验收 Page 2。  
> **页面定位**：Persistent, Traceable, Human-Governed Scientific Engineering Workspace  
> **父合同**：`Synthetic_Biology_DBTL_Engineering_OS_Page_Design_Contract_v1.2.md`  
> **输入规范**：`01_Product_Spec.md`、`02_UI_Spec.md`、`03_Operating_Principles.md`、`04_Technical_Spec.md`、`05_Acceptance_Spec.md`  
> **执行模式**：Repository-safe autonomous implementation with mandatory audit gates  
> **默认产品语言**：English  
> **规范说明语言**：中文  

---

## 0. 你的角色

你不是在制作一个漂亮的 Dashboard，也不是把五个 AI 功能拼成一个页面。

你是同时承担以下职责的高级执行 Agent：

- Product Architect；
- Synthetic Biology Workspace Designer；
- Scientific UX / UI Designer；
- Senior React / TypeScript Frontend Architect；
- Scientific Data Visualization Engineer；
- Accessibility and Performance Engineer；
- Repository-safe Implementation Agent；
- Scientific QA / Release Reviewer。

你的任务是在**现有仓库、现有后端能力、现有全局设计系统和现有科学对象模型**内，实现：

> **Page 02 — DBTL Engineering Workspace**

本页是整个 Synthetic Biology DBTL Engineering OS 的主要科学工程环境。它支持一项工程决策从瓶颈诊断，经设计、预测、科学评审，到 Build/Test 计划与下一轮学习的连续演化。

实现完成后，用户必须始终能够回答：

1. 当前项目、DBTL cycle、stage、decision 和 version 是什么？
2. 当前瓶颈是什么，依据是什么，置信度如何？
3. 当前工程方案是什么，替代方案是什么？
4. 哪些内容是 observed、predicted、inferred、proposed 或 approved？
5. 当前风险、trade-off、限制和冲突是什么？
6. 谁需要做出什么决定？
7. 下一步验证动作是什么？
8. 当前输出是否已经具备进入 Build/Test 的条件？

---

# PART I — 权威来源、系统不变量与冲突裁决

## 1. 必读文件

开始编码前，必须按顺序读取：

1. 仓库根目录的 `AGENTS.md`、`CLAUDE.md` 或等效执行规则；
2. `.openai/hosting.json`（如存在，必须遵守 Sites 项目身份）；
3. `Synthetic_Biology_DBTL_Engineering_OS_Page_Design_Contract_v1.2.md`；
4. Page 2 的五份页面规范；
5. 全局 Design System、tokens、AppShell、navigation、scientific object model；
6. Page 1 的已实现代码与共用组件；
7. 真实 API schema、types、state store、events、streaming 与 persistence；
8. 现有测试、lint、typecheck、build 和启动方式。

不得只读本 Prompt 后直接编码。

## 2. 规范解释

本 Prompt 是五份 Page 2 Spec 的可执行合成，不替代父合同。

- Product Spec 定义为什么构建及产品边界；
- UI Spec 定义用户看见什么及如何形成科学认知；
- Operating Principles 定义运行时状态、上下文和对象语义；
- Technical Spec 定义如何安全实施；
- Acceptance Spec 定义是否允许发布。

`MUST / 必须` 为发布要求；`MUST NOT / 禁止` 为红线；`SHOULD / 应` 仅可在有明确理由时偏离；`DEFERRED / 延后` 不得偷做。

## 3. System Invariants

以下不变量不可被页面 Spec、视觉稿、局部优化、工期或实现便利覆盖：

| ID | 不变量 | 强制要求 |
| --- | --- | --- |
| INV-001 | Scientific Truth | 不得为了 UI、演示或测试伪造科学结论 |
| INV-002 | Evidence Traceability | 关键主张必须追溯到证据、假设、不确定性与来源 |
| INV-003 | Human Governance | Agent 输出只能是 proposal；关键转移必须由授权人批准 |
| INV-004 | Persistent Context | project、cycle、stage、decision、version 与 selection 必须保持 |
| INV-005 | Single Source of Truth | 每个可变状态只有一个权威 owner |
| INV-006 | Repository Compatibility | 不破坏真实技术栈、路由、schema、共享合同和用户现有工作 |
| INV-007 | No Local Design Language | 不创建 Page 2 私有 token、状态语言或平行全局组件 |
| INV-008 | Explicit Epistemic State | observed、predicted、inferred、reported、proposed、approved 不得混淆 |
| INV-009 | Safe Scientific Handoff | 未完成验证、限制、风险与审批的方案不得显示为 wet-lab-ready |

若任何不变量无法保证，状态必须是 `BLOCKED`，不得继续实现或用假数据掩盖。

## 4. 决策优先级

发生冲突时，严格按以下顺序：

```text
System Invariants
→ Verified scientific truth and safety
→ Real backend and repository constraints
→ Approved global architecture
→ Page Design Contract v1.2
→ Approved global DSR / ADR
→ Page 2 Spec package
→ Approved Page 2 DSR / ADR / Exception Record
→ Approved visual reference
→ Implementation convenience
```

同层冲突：

1. 更具体且获批的规则优先；
2. 兼容的新版本优先；
3. 明确的规范性条款优先于示例；
4. 仍无法裁决时必须暂停并报告，不得自行选择最省事的解释。

## 5. Page 2 责任边界

Page 2 必须负责：

- 当前 DBTL cycle 的连续工程工作；
- bottleneck diagnosis；
- engineering decision 建立与版本化；
- design alternatives 与 trade-off；
- predictive simulation / virtual-cell 结果接入；
- scientific critique、evidence review 与 human approval；
- build/test validation plan；
- 从结果中生成下一轮学习信号。

Page 2 不得负责：

- 取代 Page 1 的项目级态势总览；
- 取代 Page 3 的全局 Evidence / Knowledge 管理；
- 取代 Page 4 的全系统 Governance / Audit 管理；
- 直接控制实验室设备或宣称实验已执行；
- 在没有真实后端能力时伪造模拟、审批或实验结果；
- 将通用 chatbot 作为主界面；
- 将五个阶段实现为五个彼此断裂的独立工具。

---

# PART II — 产品宪法

## 6. Workspace Identity

Page 2 是 DBTL Engineering OS 的主要运行环境。

它的目的不是展示生物信息，也不是执行孤立的 AI 功能，而是：

> 支持一个工程决策从诊断到实验验证的连续、可审查、可追溯演化。

**Engineering Decision 是本页的第一对象。**  
Stage、evidence、proposal、simulation、review 和 validation 都为该对象服务。

## 7. Primary Scientific Question

本页必须持续回答：

> Given the current biological system, objective, evidence, constraints and uncertainty, what engineering intervention should be considered next, why, with what risks, and how should it be validated?

## 8. Engineering Philosophy

每次交互都应至少完成一项：

- 降低科学不确定性；
- 暴露一个假设；
- 连接一条证据；
- 比较一个替代方案；
- 明确一项 trade-off；
- 请求一个人类判断；
- 形成一个可验证动作；
- 保存一个可复现版本。

纯装饰、重复信息或无法改变理解/决策的组件不得进入主工作区。

## 9. DBTL Philosophy

DBTL 不是四张标签页，而是一个闭环：

```text
Design
→ Build
→ Test
→ Learn
→ Updated Context
→ Next Design
```

Page 2 的核心工程链建议呈现为：

```text
Diagnose
→ Design
→ Simulate
→ Critique
→ Build / Test Plan
→ Learn
```

这条链必须共享同一个 decision、context、evidence graph 和 version history。

## 10. Human + AI Philosophy

AI 可以：

- 生成候选诊断；
- 建议干预策略；
- 检索并组织证据；
- 运行或接入计算工具；
- 暴露冲突与缺口；
- 生成验证计划草案。

AI 不可以：

- 将 recommendation 标为 approved；
- 静默替代 PI / Wet Lab 决策；
- 将预测写成观测；
- 在缺少证据时伪造 citation；
- 自动执行不可逆或实验动作；
- 隐藏失败、部分响应或不确定性。

## 11. 用户与核心任务

### PI

需在 30 秒内理解：

- current bottleneck；
- current proposal；
- leading risk；
- evidence strength；
- pending approval；
- next action。

### Synthetic Biology Researcher

需在 5 分钟内理解并审查完整 Engineering Decision。

### Dry Lab Scientist

需查看模型、工具、参数、版本、假设、输出和计算溯源。

### Wet Lab Scientist

需查看 genotype / intervention、protocol implications、controls、readouts、safety、acceptance criteria 和停止条件。

### First-time User

不要求预先理解 DBTL；页面必须通过阶段语言、空状态和下一步引导使其在 5 分钟内完成一次安全的浏览与审查。

## 12. 核心 JTBD

用户必须能够：

1. 恢复上一次 Workspace context；
2. 理解当前目标和约束；
3. 审查 bottleneck diagnosis；
4. 比较设计方案；
5. 检查 evidence 和 uncertainty；
6. 查看 simulation 与假设；
7. 处理 scientific critique；
8. 提交或记录 human decision；
9. 生成 Build/Test validation plan；
10. 将 Test/Learn 结果关联到下一 cycle。

## 13. 产品成功标准

成功不是“功能可点击”，而是：

- 一个 decision 能从创建到 reviewed / approved 全程保持身份；
- 每个关键 claim 都可追溯；
- 阶段切换不丢 context；
- 用户能解释 why this proposal；
- 用户能看到 alternatives、risks、limitations；
- 人类审批明确、可归因、可撤回或 supersede；
- Test 结果能成为下一 cycle 的输入。

## 14. 明确失败模式

以下任一情况均视为产品失败：

- diagnosis 与 proposal 断开；
- proposal 与 evidence 断开；
- simulation 无模型/参数/版本；
- recommendation 看起来像事实；
- approval 由 Agent 自动产生；
- navigation 造成 selection 或 context 丢失；
- alternatives / trade-offs 被隐藏；
- Build/Test plan 缺少验证标准；
- 历史 decision 被覆盖而非版本化；
- partial / stale / failed 状态伪装为 ready。

---

# PART III — 科学对象与运行语义

## 15. Core Object Model

优先复用仓库已有类型。若现有类型不完整，只能通过适配层补充，不得创建竞争性模型。

最低概念对象：

```ts
type EngineeringDecision = {
  id: string
  projectId: string
  cycleId: string
  version: number | string
  status: DecisionStatus
  objective: ScientificClaim
  bottleneckIds: string[]
  proposalIds: string[]
  selectedProposalId?: string
  evidenceIds: string[]
  riskIds: string[]
  simulationRunIds: string[]
  reviewIds: string[]
  approvalIds: string[]
  validationPlanId?: string
  createdAt: string
  updatedAt: string
  createdBy: ActorRef
}
```

相关对象至少包括：

- Project；
- DBTLCycle；
- WorkspaceContext；
- Bottleneck；
- ScientificClaim；
- Evidence；
- EngineeringProposal；
- Alternative；
- Intervention；
- Assumption；
- Constraint；
- Risk / Tradeoff；
- SimulationRun；
- Critique / Review；
- Approval；
- ValidationPlan；
- Experiment / TestResult；
- LearnSignal；
- Event / ProvenanceRecord。

## 16. Object Relationships

必须保证：

```text
Project
└── DBTL Cycle
    └── Engineering Decision
        ├── Bottleneck(s)
        ├── Proposal(s)
        │   └── Intervention(s)
        ├── Evidence / Assumption / Constraint
        ├── Simulation Run(s)
        ├── Critique / Risk / Trade-off
        ├── Human Review / Approval
        └── Validation Plan
            └── Test Result
                └── Learn Signal → Next Cycle
```

不得仅用 display string 连接对象；稳定身份必须使用真实 ID。

## 17. Epistemic State

每个科学主张必须携带：

- claim text；
- epistemic type；
- evidence level；
- confidence；
- source/provenance；
- assumptions；
- uncertainty；
- last updated；
- stale/superseded state。

允许的核心状态至少包括：

```text
Observed
Literature-reported
Predicted
Inferred
Proposed
Reviewed
Approved
Executed
Rejected
Stale
Superseded
Unavailable
```

颜色不能是唯一区分方式；必须配合文本、图标或形状。

## 18. Decision Lifecycle

按真实后端映射，最低语义：

```text
Draft
→ Evidence Gathering
→ Analysis
→ Review Requested
→ Changes Requested | Reviewed
→ Approval Requested
→ Approved | Rejected
→ Build/Test Planned
→ Executed
→ Learned
→ Superseded
```

禁止无审批从 `Proposed` 跳到 `Approved`。  
禁止前端自行推进后端状态。  
失败、撤回和 supersede 必须保留历史，不得覆盖。

## 19. Evidence Lifecycle

Evidence 必须支持：

- added；
- linked；
- reviewed；
- contradicted；
- weakened；
- stale；
- superseded；
- inherited into next cycle。

Evidence Drawer 中必须显示：

- source；
- claim supported / challenged；
- evidence type；
- quality / confidence；
- method / dataset；
- limitations；
- provenance；
- linked objects。

## 20. Computational Traceability

所有计算结果必须尽可能保留：

```text
Prompt / Request
→ Model
→ Tool
→ Input / Dataset
→ Parameters
→ Software / Version
→ Output
→ Review
```

后端未提供字段时必须标记 `Unavailable`，不得猜测。

## 21. Approval Semantics

审批必须记录：

- actor；
- role；
- decision；
- decision version；
- timestamp；
- rationale / comment；
- conditions；
- status；
- superseded/revoked information。

Approval UI 必须明确这是 consequential action，并支持确认、取消与错误恢复。

## 22. Workspace Persistence

至少保留：

- project；
- cycle；
- stage；
- decision/version；
- selected object；
- open inspector/drawer；
- filters；
- comparison set；
- safe draft；
- scroll/focus（在合理范围内）。

恢复时必须显示 restoration feedback；若引用对象已 stale 或 superseded，必须提醒，不得静默恢复旧状态。

## 23. Event Model

优先映射真实事件。建议语义：

```text
workspace.restored
stage.changed
object.selected
decision.created
decision.updated
proposal.compared
evidence.added
simulation.started
simulation.completed
simulation.failed
review.requested
review.completed
approval.granted
approval.rejected
validation_plan.updated
test_result.linked
cycle.learned
```

事件必须幂等、可追溯；乱序或重复事件不得破坏当前状态。

---

# PART IV — 页面信息架构与 UI 合同

## 24. 页面总骨架

Page 2 必须是一个 persistent workspace，而不是长滚动营销页。

推荐桌面结构：

```text
┌──────────────────────────────────────────────────────────────┐
│ Global App Shell / Navigation                               │
├──────────────────────────────────────────────────────────────┤
│ Persistent Context Bar                                      │
│ Project · Cycle · Decision · Version · Status · Save state   │
├──────────────────────────────────────────────────────────────┤
│ Workspace Command Header                                    │
│ Objective · Current bottleneck · Risk · Next required action │
├──────────────────────────────────────────────────────────────┤
│ Stage Rail / Decision Lifecycle                             │
├───────────────┬──────────────────────────────┬───────────────┤
│ Object /      │ Primary Scientific Canvas    │ Contextual    │
│ Workflow Rail │ Current stage work surface   │ Inspector     │
│               │ Decision-centered content    │ Evidence etc. │
├───────────────┴──────────────────────────────┴───────────────┤
│ Activity / provenance / job status (collapsible)            │
└──────────────────────────────────────────────────────────────┘
```

不得让 Inspector、chat、activity 或 visual spectacle 抢走 Primary Scientific Canvas。

## 25. Persistent Context Bar

必须始终可见：

- project name；
- chassis / organism；
- target / objective；
- active DBTL cycle；
- active decision ID / short name；
- decision version；
- lifecycle status；
- save / sync state；
- stale / historical / read-only state。

切换 project、cycle 或 decision 属于高影响 context change，必须防止未保存草稿丢失。

## 26. Workspace Command Header

必须以一屏内可读方式回答：

- Objective；
- Current Bottleneck；
- Current Proposal；
- Leading Risk；
- Next Required Action。

每项必须可点击定位到对应对象或 Inspector，不得是不可追溯摘要。

## 27. Stage Rail

Stage Rail 应包含：

1. Diagnose；
2. Design；
3. Simulate；
4. Critique；
5. Build / Test；
6. Learn（若当前产品范围支持）。

每个 Stage 必须显示：

- current / complete / blocked / warning / unavailable；
- required input readiness；
- unresolved count；
- approval gate；
- output readiness。

切换 Stage 不得清空 Decision context。Stage 不得被呈现为独立产品。

## 28. Left Object / Workflow Rail

提供当前阶段的可导航对象树或任务列表，例如：

- bottlenecks；
- proposals；
- interventions；
- evidence；
- assumptions；
- simulations；
- critiques；
- approvals；
- validation plan。

要求：

- 支持清晰 selection；
- 支持状态和数量；
- 不重复主画布内容；
- 可折叠但不得造成不可发现；
- selection 必须与 Inspector 同步。

## 29. Primary Scientific Canvas

这是本页视觉中心。每个阶段应使用最合适的科学表达，而不是统一卡片墙。

### Diagnose

至少呈现：

- objective / phenotype；
- system context；
- candidate bottlenecks；
- causal reasoning；
- supporting/challenging evidence；
- confidence；
- unresolved uncertainty；
- diagnostic alternatives。

### Design

至少呈现：

- selected bottleneck；
- proposal alternatives；
- intervention composition；
- mechanism；
- expected effect；
- trade-offs；
- feasibility；
- evidence coverage；
- comparison；
- decision rationale。

### Simulate

至少呈现：

- model / tool；
- version；
- inputs / assumptions；
- parameters；
- run state；
- output / uncertainty；
- baseline comparison；
- sensitivity / limitation（若真实支持）；
- provenance。

预测不得显示为观测。无真实模拟能力时显示 Capability Unavailable，不得伪造结果。

### Critique

至少呈现：

- mechanism review；
- evidence gaps；
- contradictory evidence；
- scientific risks；
- trade-offs；
- limitations；
- requested changes；
- reviewer / status；
- response and resolution。

### Build / Test

至少呈现：

- genotype / construct / intervention summary；
- validation question；
- controls；
- measurements/readouts；
- success criteria；
- failure criteria；
- safety / feasibility notes；
- dependencies；
- approval status；
- handoff package。

“Build”不等于实际执行；除非后端真实确认，否则只能显示 planned / approved / executed 的准确状态。

### Learn

至少呈现：

- observed Test results；
- comparison to prediction；
- accepted/rejected hypotheses；
- updated confidence；
- new bottleneck；
- carry-forward evidence；
- next-cycle recommendation。

## 30. Contextual Inspector

Inspector 是对象级深度审查面板，随 selection 更新。

通用字段：

- identity；
- type；
- status；
- version；
- owner；
- created / updated；
- relationships；
- evidence；
- provenance；
- assumptions；
- uncertainty；
- history；
- actions。

Inspector 必须保持上下文，不得把用户跳转到无关页面才能查看基本信息。

## 31. Evidence Drawer

证据必须“持续可检查”，但不持续占据主画布。

Drawer 支持：

- view source；
- supporting / challenging；
- filter by type / quality / state；
- linked claim；
- limitations；
- provenance；
- open Page 3 deeper evidence view（若存在）。

## 32. Decision Comparison

支持至少两个候选方案并排比较，比较维度应包括：

- mechanism；
- expected benefit；
- evidence strength；
- confidence；
- feasibility；
- risk；
- burden；
- trade-off；
- validation complexity；
- unresolved questions。

不得用不透明的单一“AI score”替代科学比较。综合评分必须解释组成和局限。

## 33. Visual Hierarchy

严格继承：

```text
Brand
→ Workspace
→ Page
→ Region
→ Panel
→ Component
→ Scientific Object
```

Page 2 应具有“专业科研工作台”的高信息密度，但必须通过视觉节奏避免全页同密度：

```text
Dense context
→ Relaxed orientation
→ Focused scientific canvas
→ Dense inspection
→ Rest / activity
```

## 34. Visual Semantics

- 主色用于选择、焦点与主要操作，不用于装饰；
- success 仅用于真正通过的状态；
- warning 表示需要注意，不等于失败；
- danger 用于阻断、冲突或不可逆风险；
- predicted / inferred / observed 必须具备稳定的非颜色编码；
- confidence 不得仅用渐变色；
- approved 与 agent-recommended 必须显著不同。

禁止：

- 霓虹生物科技风；
- 大面积渐变和玻璃态；
- 无意义 3D DNA / 细胞背景；
- 卡片套卡片；
- 每个对象一种颜色；
- 用装饰图标代替标签；
- 聊天气泡主导科学流程。

## 35. Typography and Density

- 页面标题、Workspace 标题、Panel 标题、对象标题必须分级；
- 数据、单位、版本、ID 使用可扫描格式；
- 长科学文本使用 progressive disclosure；
- 主画布允许紧凑，但不允许不可扫描；
- 所有关键数值显示单位、来源和不确定性（若可用）。

## 36. Three.js Policy

仅当 3D 能表达真实空间关系、结构或交互且具有数据映射时使用。

不得将 3D E. coli 作为无功能主视觉。若使用：

- 必须有 2D fallback；
- 必须可键盘跳过；
- 必须尊重 reduced motion；
- 必须在低性能设备降级；
- 不得阻塞工作区首屏。

---

# PART V — 交互合同

## 37. 统一任务流

所有阶段遵守：

```text
Start
→ Understand
→ Decide
→ Commit
→ Review
→ Complete
```

每个阶段必须明确：

- user starts where；
- what must be understood；
- what decision is available；
- what commit changes；
- who reviews；
- what completion means。

## 38. Selection

- 单击对象：选中并更新 Inspector；
- 双击不得隐含关键操作；
- selection 必须有明显且可访问的状态；
- stage 切换尽量保持 selection；
- 若对象不属于目标 stage，显示定位提示而非静默清空。

## 39. Create / Edit / Compare

- 创建 Decision 或 Proposal 必须从明确入口开始；
- 编辑必须区分 local draft 与 persisted state；
- compare set 必须可见并可清除；
- 自动保存需显示状态；
- 保存失败不得静默；
- 冲突编辑必须提示并提供 recover/copy。

## 40. Consequential Actions

以下至少需要明确确认：

- approve / reject；
- submit for review；
- supersede decision；
- discard draft；
- change active cycle；
- promote proposal to build/test plan；
- remove evidence link。

确认框必须说明对象、版本、影响和可恢复性。

## 41. Agent Participation

Agent 的工作必须显示：

- current task；
- inputs；
- tool/capability；
- progress；
- partial result；
- error；
- cancellation（若支持）；
- output status；
- review requirement。

不得用无限 loading 代替运行状态。Streaming 输出不得造成 layout jump 或把未完成内容标为正式结论。

## 42. Loading / Empty / Error / Offline

### Loading

- 保留布局骨架；
- 区分初始加载与后台刷新；
- 不用假值填充；
- 长任务显示可解释进度。

### Empty

说明：

- 为什么为空；
- 需要什么输入；
- 谁可以采取行动；
- 下一步是什么。

### Error

显示：

- 哪一能力失败；
- 哪些数据仍可信；
- 是否可重试；
- 是否保存草稿；
- provenance / job ID（适用时）。

### Partial / Offline

必须显式标记 partial、cached、stale 或 offline。不得把缓存旧数据显示成 current。

## 43. Conflict Resolution

科学冲突不得自动合并。必须显示：

- conflicting claims；
- evidence on each side；
- affected proposal；
- unresolved status；
- reviewer decision；
- resolution rationale；
- version impact。

## 44. Keyboard and Accessibility

至少支持：

- 合理 tab order；
- visible focus；
- Escape 关闭 Drawer / modal；
- Enter/Space 操作控件；
- 不陷入焦点；
- screen-reader label；
- 图表文本摘要；
- reduced motion；
- 不依赖 hover 或颜色。

---

# PART VI — 技术实现合同

## 45. Repository Audit

编码前输出或记录：

```yaml
framework:
build_tool:
package_manager:
router:
styling:
design_tokens:
app_shell:
navigation:
shared_components:
scientific_types:
state_management:
api_client:
streaming:
persistence:
test_stack:
page1_reusable_assets:
protected_surfaces:
current_uncommitted_changes:
```

不得假设 React、Tailwind、Zustand、Redux 或 Three.js 已存在；以仓库事实为准。

## 46. Protected Repository Surface

默认保护：

- AppShell；
- global navigation；
- global tokens；
- global scientific object model；
- global types；
- shared components；
- API contracts；
- approval semantics；
- backend scientific logic；
- unrelated routes and modules。

若完成 Page 2 必须修改保护面，必须：

1. 说明必要性；
2. 列出 alternatives；
3. 记录 ADR / DSR；
4. 等待明确授权；
5. 未授权则暂停。

## 47. Architecture Rules

- 复用优先于新增；
- 扩展优先于替换；
- 页面组件不得拥有服务器事实；
- API adapter 负责后端 schema 到 UI view model 的映射；
- domain state、UI state、server state 分离；
- 每个 state 只有一个 owner；
- 共享组件不得在 Page 2 被复制成私有变体；
- 新 capability 通过 registry / adapter 接入，不硬编码进工作区骨架。

## 48. 推荐 Feature Boundary

仅在与仓库结构兼容时采用：

```text
features/dbtl-workspace/
├── components/
├── stages/
│   ├── diagnose/
│   ├── design/
│   ├── simulate/
│   ├── critique/
│   ├── build-test/
│   └── learn/
├── inspectors/
├── adapters/
├── hooks/
├── state/
├── types/
├── fixtures/
└── tests/
```

不得为了符合此目录示例而重构现有仓库。

## 49. Component Mapping

组件必须对应明确职责：

| Component concept | Responsibility |
| --- | --- |
| WorkspaceContextBar | 显示并切换持久上下文 |
| DecisionCommandHeader | 汇总 objective / bottleneck / risk / next action |
| StageRail | DBTL 工程阶段与 gate |
| ObjectRail | 当前阶段对象和任务 |
| ScientificCanvas | 阶段主工作面 |
| ContextualInspector | 选中对象深度检查 |
| EvidenceDrawer | 证据与 provenance |
| DecisionComparison | 替代方案比较 |
| ApprovalGate | 人类审批 |
| ActivityPanel | event / job / provenance |

组件名称必须适配现有命名规范。

## 50. State Ownership

至少区分：

```text
Server truth:
decisions, evidence, reviews, approvals, simulation jobs, validation plans

Persistent workspace state:
project, cycle, stage, decision, version, draft references

URL-shareable state:
stable context and selected object where appropriate

Local UI state:
panel width, drawer open, transient focus

Ephemeral state:
hover, optimistic animation, temporary input
```

Approval、simulation result、evidence 与 execution state 禁止仅存前端。

## 51. API Integration

必须先审计真实 API。禁止虚构端点、字段或成功响应。

适配层必须处理：

- loading；
- success；
- empty；
- partial；
- stale；
- error；
- unauthorized；
- conflict；
- cancelled；
- superseded。

若后端缺失：

- 使用明确标记的 deterministic typed fixture；
- fixture 仅用于开发/视觉测试；
- production 路径不得静默 fallback 到 fixture；
- UI 必须显示 capability unavailable 或 demo state；
- 在 Known Limitations 中记录。

## 52. Streaming and Jobs

若存在长任务：

- 使用真实 job ID；
- 支持 reconnect/recovery（后端允许时）；
- 去重事件；
- 忽略或标记乱序旧事件；
- 不让 stale completion 覆盖新 run；
- 失败保留已完成部分；
- 取消状态必须真实。

## 53. Persistence

使用现有 persistence 层。不得把敏感科学数据随意写入 `localStorage`。

刷新、后退/前进、路由切换后必须验证：

- context 不丢；
- draft 有明确信息；
- Inspector selection 合理恢复；
- stale version 不被误认为 current；
- historical view 为 read-only。

## 54. Rendering and Performance Budget

目标（如现有项目有更严格预算则服从项目）：

- 普通交互反馈 `<100 ms`；
- Panel 更新感知 `<200 ms`；
- 首个 skeleton `<1 s`；
- 动画目标 60 FPS；
- 大对象列表使用 memoization / virtualization（需要时）；
- 不因 Inspector 打开导致全 workspace 重渲染；
- 3D 和图表懒加载；
- 路由 chunk 不得无理由显著膨胀。

必须用实际测量或构建输出验证，不得只宣称“性能良好”。

## 55. Responsive

### ≥1600 px

三栏完整布局，主画布保持最高优先级。

### 1280–1599 px

可压缩 rail；Inspector 可 overlay / drawer，但不能丢功能。

### Tablet

Stage、Canvas、Inspector 分层切换；保留 context 与决策动作。

### Mobile

以审查、状态查看和轻量批准为主；复杂建模编辑可明确标为 desktop-recommended，不得伪装完整能力。

## 56. Testing Strategy

至少包含：

- domain/view-model unit tests；
- adapter schema/error tests；
- state transition tests；
- component interaction tests；
- accessibility tests；
- route/context persistence tests；
- responsive visual checks；
- regression tests；
- build/typecheck/lint；
- real backend contract test（可用时）。

不得为了通过测试删除关键断言或关闭类型检查。

---

# PART VII — 实施范围锁

## 57. Allowed Scope

允许：

- 实现 Page 2 route 和页面特有模块；
- 复用与组合现有共享组件；
- 增加 Page 2 adapter、view model、hooks、tests；
- 增加必要且经审计不存在的页面组件；
- 修复由本实现直接引入的问题；
- 添加明确标注的开发 fixtures。

## 58. Forbidden Autonomous Behaviors

未经明确授权，禁止：

- 重构无关代码；
- 修改后端科学逻辑；
- 重命名真实 API；
- 改变导航架构；
- 替换 Design System；
- 创建平行 global types；
- 修改 Page 1/3/4 行为；
- 引入大型依赖；
- “顺手优化”无关页面；
- 自动补造后端能力；
- 将 fixture 当 production data；
- 自动批准 scientific proposal；
- 创建新的业务工作流；
- 掩盖失败、warning 或 TODO；
- 验收通过后继续优化。

## 59. Conditional Audit Gate

出现以下情况必须暂停：

- Spec 与真实后端冲突；
- 需要修改 protected surface；
- 存在两个同名/同职责共享组件且无法安全选择；
- 缺少决定性 API/schema；
- 需要新增重大依赖；
- 无法保证 scientific truth 或 human governance；
- 用户现有未提交改动与目标文件重叠；
- 无法区分 Page 2 与其他页面责任；
- 测试失败原因属于无关模块且修复会扩大范围。

暂停报告必须包含：

```yaml
blocked_requirement:
evidence:
affected_files:
safe_options:
recommended_option:
tradeoff:
decision_needed:
```

---

# PART VIII — 固定实施顺序

## 60. Step 1 — Repository Audit

读取规则、架构、路由、组件、类型、API、测试与当前改动。不得写代码。

## 61. Step 2 — Specification Matrix

建立内部矩阵：

| Requirement | Source | UI region/object | Backend dependency | Reuse target | Test | Status |
| --- | --- | --- | --- | --- | --- | --- |

所有 MUST 必须有实现与验证映射。

## 62. Step 3 — Conflict and Gap Analysis

输出：

- 已满足；
- 可复用；
- 必须新增；
- 后端缺失；
- 需要确认；
- deferred；
- blocked。

## 63. Step 4 — Component Inventory

逐项证明：

- reuse existing；
- extend existing；
- create new。

新组件必须说明为什么现有组件无法满足。

## 64. Step 5 — Decision Records

重大 UX 决策记录 DSR：

```yaml
id:
context:
decision:
alternatives:
reason:
tradeoff:
impact:
approval:
```

重大技术决策记录 ADR：

```yaml
id:
context:
constraints:
decision:
alternatives:
reason:
tradeoff:
affected_files:
rollback:
approval:
```

## 65. Step 6 — Implement Foundation

先实现：

- route；
- Workspace shell；
- types/adapters；
- context ownership；
- loading/error/empty；
- persistence；
- accessibility foundation。

## 66. Step 7 — Implement Core Experience

按依赖顺序：

1. Context Bar；
2. Command Header；
3. Stage Rail；
4. Engineering Decision model/view；
5. Diagnose；
6. Design / comparison；
7. Evidence / Inspector；
8. Simulate；
9. Critique / approval；
10. Build/Test；
11. Learn / history；
12. activity/provenance。

仅实现真实后端支持或明确 fixture 支持的能力。

## 67. Step 8 — Verify

运行：

- formatter；
- lint；
- typecheck；
- unit/component/integration tests；
- build；
- targeted runtime checks。

每个失败必须解决、标记 blocked 或解释为已存在且与范围无关；不得静默忽略。

## 68. Step 9 — Visual and Interaction QA

至少验证：

- 1600 / 1440 / 1280；
- tablet；
- mobile review mode；
- normal / empty / loading / error / partial / stale / historical；
- keyboard-only；
- reduced motion；
- long scientific text；
- large evidence/object count；
- drawer / inspector focus；
- no layout overflow。

## 69. Step 10 — Acceptance and Regression

逐项执行 PART IX 与 PART X。Critical Failure 为零才可 `READY`。

## 70. Step 11 — Delivery and STOP

输出标准报告。所有 Gate 通过后必须停止，不得继续重构或“进一步优化”。

---

# PART IX — 发布验收

## 71. Definition of Done

只有同时满足以下条件才算完成：

- Page 2 route 可访问；
- Workspace identity 和 context 清晰；
- Engineering Decision 是主对象；
- 各阶段共享同一上下文；
- evidence / uncertainty / provenance 可检查；
- human approval 不可被绕过；
- 真实 API 或明确降级；
- loading/error/empty/partial/stale 完整；
- responsive 与 accessibility 通过；
- tests/typecheck/build 通过；
- 无 protected surface 未授权修改；
- 无 Critical Failure；
- 无隐藏 TODO / fake success；
- completion report 完整。

## 72. Product Gate

- [ ] PI 30 秒可理解 bottleneck、proposal、risk、next action
- [ ] Researcher 5 分钟可理解完整 decision
- [ ] 页面支持连续工程决策而非独立工具
- [ ] alternatives、trade-offs、limitations 可见
- [ ] 下一步行动明确且可定位

## 73. Scientific Object Gate

- [ ] 每个关键对象有稳定 ID
- [ ] object relationships 可追溯
- [ ] version/status/owner/provenance 清晰
- [ ] observed/predicted/inferred/proposed/approved 不混淆
- [ ] stale/superseded 不伪装 current

## 74. Engineering Decision Gate

- [ ] objective 明确
- [ ] bottleneck 有 causal reasoning
- [ ] proposal 有 mechanism
- [ ] evidence 支持与反对均可见
- [ ] assumptions 与 uncertainty 显示
- [ ] alternatives 可比较
- [ ] risk / trade-off / limitation 完整
- [ ] validation plan 可执行
- [ ] approval 可归因

## 75. Explainability Gate

用户必须能回答：

- Why this bottleneck?
- Why this intervention?
- What evidence supports it?
- What evidence challenges it?
- What assumptions drive it?
- What could fail?
- How will it be validated?
- Who approved it?

## 76. Governance Gate

- [ ] Agent output 明确为 proposal
- [ ] consequential transition 需要 human action
- [ ] approval 绑定 decision version
- [ ] reject / changes requested / revoke 可表达
- [ ] audit history 不可被前端覆盖
- [ ] wet-lab-ready 状态有明确前置条件

## 77. Wet Lab Gate

- [ ] genotype/intervention 表达清楚
- [ ] controls、readouts、success/failure criteria 完整
- [ ] safety、feasibility、dependency 可见
- [ ] proposal 不等于 executed
- [ ] 未批准方案不可伪装 handoff-ready

## 78. Dry Lab Gate

- [ ] model/tool/version 可追溯
- [ ] input/parameter/assumption 可查
- [ ] output 与 baseline 可比较
- [ ] prediction uncertainty 可见
- [ ] failed/partial/stale run 状态准确

## 79. UI and Interaction Gate

- [ ] 主画布是视觉中心
- [ ] context、stage、selection 始终可理解
- [ ] evidence 持续可检查
- [ ] 无 card wall / chatbot 主导
- [ ] 操作反馈明确
- [ ] destructive/consequential action 有确认
- [ ] keyboard/focus/reduced motion 通过
- [ ] 不依赖颜色表达语义

## 80. Repository Gate

- [ ] 复用现有架构
- [ ] 未替换全局系统
- [ ] 无无关重构
- [ ] 每个新文件有 requirement 映射
- [ ] API 未虚构
- [ ] fixture 不进入 production truth
- [ ] protected files 未擅改
- [ ] unrelated user changes preserved

## 81. Static and Runtime Gate

- [ ] formatter PASS
- [ ] lint PASS
- [ ] typecheck PASS
- [ ] tests PASS
- [ ] production build PASS
- [ ] route runtime PASS
- [ ] no console error
- [ ] no unhandled rejection
- [ ] no critical accessibility violation

## 82. Quality Score

按七域评分，每域必须 `PASS`，不得用总分抵消关键失败：

| Domain | Required |
| --- | --- |
| Product / Workflow | PASS |
| Scientific Integrity | PASS |
| Governance | PASS |
| UI / Interaction | PASS |
| Technical / Repository | PASS |
| Performance / Accessibility | PASS |
| Regression | PASS |

## 83. Critical Failures

任一出现即禁止发布：

- 伪造科学事实、citation、API 或模拟结果；
- predicted 显示为 observed；
- Agent 自动批准 proposal；
- decision/evidence/provenance 丢失；
- stage 切换造成 context 丢失；
- 未授权修改 protected surface；
- production 静默使用 fixture；
- build/typecheck/关键测试失败；
- 存在不可恢复的数据丢失路径；
- 将 planned 显示为 executed；
- 关键 action 无审计或归因；
- Page 2 被实现为割裂的工具集合。

## 84. Release Decision

最终只能输出：

- `READY`：全部 Gate 通过，Critical Failure = 0；
- `NEEDS REVISION`：存在可在授权范围内修复的问题；
- `REJECTED`：违反不变量、科学安全或仓库保护规则。

---

# PART X — 必测场景

## 85. Scenario A — Active healthy decision

完整数据、多个 proposal、证据充分、一个 simulation 完成，验证 Stage continuity 与 comparison。

## 86. Scenario B — Weak evidence

诊断存在但证据不足，必须显示 uncertainty、evidence gap 与不可批准状态。

## 87. Scenario C — Conflicting evidence

支持与反对证据并存，必须显示冲突且禁止自动消解。

## 88. Scenario D — Multiple alternatives

至少三个方案，比较 mechanism、benefit、risk、feasibility、validation complexity。

## 89. Scenario E — Simulation running / failed

验证 progress、partial、failure、retry、provenance 与 stale run 防覆盖。

## 90. Scenario F — Human review requested

验证 reviewer、requested changes、comments、version binding 与 resubmission。

## 91. Scenario G — Approval gate

验证 Agent 无法 approve、确认信息完整、approval 有归因与审计。

## 92. Scenario H — New empty cycle

无 decision/evidence，空状态必须解释输入、责任人和下一步。

## 93. Scenario I — Historical / superseded decision

必须 read-only、显示 replaced-by、不得误操作。

## 94. Scenario J — Partial backend failure

Evidence 可用但 simulation API 失败；不得导致整页假失败或伪成功。

## 95. Scenario K — Context restoration

刷新或返回页面后恢复 project/cycle/stage/decision/selection，并识别 stale version。

## 96. Scenario L — Wet-lab handoff

验证未满足 safety、control、criteria 或 approval 时不可标为 ready。

## 97. Scenario M — Large workspace

大量 evidence、objects、events、长文本下验证性能、可扫描性和无溢出。

## 98. Scenario N — Accessibility

仅键盘和 screen reader 路径完成浏览、检查证据、比较与取消审批动作。

---

# PART XI — Regression Matrix

## 99. 必须证明 No Drift

| Domain | 必须证明 |
| --- | --- |
| Page | Page 1/3/4 的职责与路由未漂移 |
| Component | 共享组件行为未被 Page 2 私有化 |
| Interaction | selection、drawer、approval、recovery 保持全局语法 |
| Scientific | 对象、状态、evidence、confidence 语义一致 |
| Backend | schema、API、event、persistence 未被前端改写 |
| Performance | bundle、render、job streaming 无明显退化 |
| Accessibility | focus、keyboard、semantics 无退化 |
| Governance | Agent、人类、approval 与 audit 边界未退化 |

若无法证明某域，发布状态不得为 `READY`。

---

# PART XII — 完成报告

## 100. 标准输出格式

完成后只输出事实，不写笼统的 “Done”：

```yaml
outcome:
release_decision: READY | NEEDS_REVISION | REJECTED

repository_audit:
  stack:
  reused_architecture:
  protected_surfaces:

files:
  created:
  modified:
  intentionally_untouched:

implementation:
  reused_components:
  extended_components:
  new_components:
  adapters:
  fixtures:

scientific_contract:
  decision_model:
  evidence_traceability:
  epistemic_states:
  human_governance:
  computational_traceability:

verification:
  format:
  lint:
  typecheck:
  tests:
  build:
  visual:
  accessibility:
  performance:

acceptance:
  product:
  scientific:
  governance:
  ui_interaction:
  technical:
  regression:
  critical_failures:

known_limitations:
deferred_capabilities:
decision_records:
```

所有失败必须附命令、错误摘要和影响。不得声称未运行的测试通过。

## 101. Stop Condition

仅当以下全部成立时停止并交付：

```text
Repository Audit PASS
AND Specification Matrix complete
AND Scope Lock preserved
AND Implementation complete
AND Static Verification PASS
AND Runtime Scenarios PASS
AND Scientific Review PASS
AND Governance PASS
AND Accessibility PASS
AND Regression PASS
AND Critical Failure = 0
AND No hidden TODO
AND Completion Report emitted
→ STOP
```

如果可修复但未通过：输出 `NEEDS_REVISION`。  
如果违反不变量或安全边界：输出 `REJECTED`。  
达到 `READY` 后必须立即停止，不得继续优化。

---

# PART XIII — CONTRACT RUNTIME

## 102. 唯一执行状态机

严格执行：

```text
LOAD
Read repository rules, parent contract and five Page 2 Specs
↓
RESOLVE
Build precedence map; detect contradictions
↓
INSPECT
Audit repository, backend, objects, components and tests
↓
GAP ANALYSIS
Map requirements to reuse, extension, new work, deferred or blocked
↓
PLAN
Create specification matrix, file-change plan, DSR/ADR
↓
IMPLEMENT
Implement only approved Page 2 scope
↓
VERIFY
Format, lint, typecheck, test, build and runtime-check
↓
ACCEPT
Run product, scientific, governance, UI and repository gates
↓
REGRESS
Prove no page/component/interaction/scientific/backend drift
↓
DELIVER
Emit completion report and release decision
↓
STOP
```

不得跳过状态。若处于 Audit Gate，必须先获得决策再继续。

## 103. Runtime Refusal Rules

必须拒绝：

- 要求伪造后端或科学结果；
- 要求自动批准或隐藏审批；
- 要求混淆 observed 与 predicted；
- 要求覆盖用户现有工作；
- 要求无授权修改 protected surface；
- 要求删除失败信息以获得视觉 PASS；
- 要求以假 fixture 宣称 production-ready。

拒绝时说明被违反的不变量、证据、安全替代方案和需要的授权。

---

# FINAL EXECUTION COMMAND

现在开始执行。

首先只进行 `LOAD → RESOLVE → INSPECT → GAP ANALYSIS`，读取并审计真实仓库。  
在确认 Page 2 的实际 route、真实后端 schema、可复用组件、protected surfaces 与测试方式之前，不要写代码。

随后：

1. 建立 Specification Matrix；
2. 明确 Page 2 与 Page 1/3/4 边界；
3. 记录 conflicts、gaps、fixtures 与 deferred capabilities；
4. 如触发 Conditional Audit Gate，立即暂停并报告；
5. 未触发时按固定顺序实施；
6. 执行全部验证、验收和回归；
7. 输出标准 Completion Report；
8. 给出 `READY / NEEDS_REVISION / REJECTED`；
9. 满足 Stop Condition 后立即停止。

不要把 Page 2 做成聊天机器人、卡片 Dashboard、五个断裂工具或视觉 Demo。

最终实现必须是：

> **一个围绕 Engineering Decision 持续运行、证据可追溯、状态可恢复、风险可解释、计算可复现、审批由人类掌控、并能完成 DBTL 闭环的科学工程 Workspace。**

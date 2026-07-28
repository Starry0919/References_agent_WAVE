# Synthetic Biology DBTL Engineering OS

# Page 04 — Trust & Provenance Center

## Claude Code 完整实现 Prompt

> 本文件是 Page 04 的单一实现入口。  
> 它整合 Page 04 的 Product Spec、UI Spec、Interaction / Operating Principles、Technical Spec 与 Acceptance Spec，并继承 `Synthetic_Biology_DBTL_Engineering_OS_Page_Design_Contract_v1.2.md`。  
> 你的任务是先审计真实仓库和后端能力，再在不破坏科学语义、人工治理、历史完整性、权限模型和现有架构的前提下，实现、测试、验收 Page 04，并在达到停止条件后立即停止。

---

# 0. 角色与执行目标

你同时承担：

- Senior Product Engineer
- Frontend Architect
- Scientific Governance Engineer
- Provenance and Audit Systems Engineer
- Scientific UX Engineer
- Security and Permission Reviewer
- Accessibility and Performance Engineer
- Scientific QA / Release Reviewer

你不是自由发挥的页面设计师，也不是被授权重写整个仓库的架构师。

你要实现的是：

> **Trust, Governance & Provenance Control Plane**

你不得把 Page 04 实现为：

- generic admin dashboard；
- raw event-log wall；
- approval inbox；
- model leaderboard；
- memory list；
- decorative compliance page；
- full-page chatbot；
- 单一、不可解释的 “trust score”；
- 与 Page 01、Page 02、Page 03 分离的孤立后台。

你必须实现一个以精确对象与精确版本为中心、能够重建因果与计算历史、执行人类治理、检查记忆影响并评价系统表现的持久工作区。

---

# PART I — 权威来源、冲突裁决与不可破坏规则

## 1. 必读文件

开始写代码前，必须按顺序完整读取：

1. `Synthetic_Biology_DBTL_Engineering_OS_Page_Design_Contract_v1.2.md`
2. `01_Product_Spec(4).md`
3. `02_UI_Spec(4).md`
4. `03_Operating_Principles(3).md`
5. `04_Technical_Spec(4).md`
6. `05_Acceptance_Spec(4).md`
7. 仓库中适用的 `AGENTS.md`
8. README、package manifest、路由、AppShell、全局 tokens、共享类型、状态管理、API client、权限系统、测试配置
9. 已实现的 Page 01、Page 02、Page 03 及其测试

若文件名或位置不同，以仓库事实为准。不得仅凭本 Prompt 猜测现有实现。

## 2. 五份 Spec 的职责

- Product Spec：规定 Page 04 为什么存在、服务谁、负责什么、不负责什么；
- UI Spec：规定治理对象、风险、历史和依据如何被看见；
- Operating Principles：作为 Interaction Spec，规定状态、生命周期、动作前提、权限与失败语义；
- Technical Spec：规定如何在真实仓库和真实后端边界内实现；
- Acceptance Spec：规定如何以证据证明完成；
- Master Contract v1.2：规定全局系统不变量、决策层级、执行流程、暂停规则和停止条件。

本 Prompt 是执行收敛，不降低任何上级规范要求。

## 3. 决策优先级

发生冲突时按以下顺序裁决：

1. 安全、法律、平台规则；
2. System Invariants；
3. Page Design Contract v1.2；
4. 已确认的真实后端合同、权限模型、共享对象模型；
5. Page 04 Operating Principles；
6. Page 04 Product Spec；
7. Page 04 Technical Spec；
8. Page 04 UI / Interaction Spec；
9. Page 04 Acceptance Spec；
10. 本 Prompt 中的实现建议；
11. Claude 的偏好。

若高优先级规则导致低优先级要求无法安全实现：

- 不得静默选择；
- 不得伪造兼容；
- 进入 Conditional Audit Gate；
- 输出冲突、证据、影响与安全选项；
- 等待明确决策。

## 4. Page 04 System Invariants

以下规则永远不得被局部实现覆盖：

1. **Historical Integrity**：历史不能被静默重写。
2. **Exact Object Identity**：任何治理、评价和溯源动作都必须绑定精确对象。
3. **Exact Version Identity**：批准、撤销、覆盖、评价和复现都必须绑定精确版本。
4. **Proposal Is Not Approval**：提议不能显示为已批准。
5. **Approval Is Not Execution**：批准不能显示为已经执行。
6. **Execution Is Not Observation**：执行不能显示为已经获得结果。
7. **Observation Is Not Evaluation**：获得结果不能显示为已经验证有效。
8. **Memory Is Not Scientific Truth**：记忆只是一种有来源、有范围、有新鲜度的系统输入。
9. **Trust Is Multidimensional**：不得把证据、溯源、权限、复现性、评估和新鲜度压成单一分数。
10. **Human Authority Is Explicit**：前端和 Agent 都不能授予审批权。
11. **Governance Is Attributable**：每个重大决定必须能归因到人、角色、时间、对象版本和理由。
12. **Correction Preserves History**：修正必须新增版本或事件，不能覆盖历史。
13. **Evaluation Does Not Self-Authorize**：评价结果不能自动批准发布、实验或工程执行。
14. **Critical Failure Cannot Be Averaged Away**：关键失败不能被总体均值掩盖。
15. **Missing Information Is Explicit**：未知、缺失、受限、不可用和未运行必须分别表示。
16. **Backend Authority**：权限、批准、审计、记忆版本、溯源和评价结果以真实后端为权威。
17. **No Parallel Truth**：前端不得维护第二套治理真相。
18. **Restricted Data Stays Restricted**：敏感内容不能经 URL、缓存、日志、分析、导出或预览泄露。
19. **Repository Compatibility**：优先复用现有架构，保护无关页面和共享表面。
20. **No Local Design Language**：Page 04 不得发明与全站冲突的视觉系统。

## 5. Repository Freeze

以下表面默认受保护：

- AppShell；
- 全局导航；
- 全局 design tokens；
- 全局对象身份与版本类型；
- 共享 API client；
- 身份认证和权限基础设施；
- 跨页面上下文协议；
- Page 01、Page 02、Page 03 的既有行为；
- 后端科学逻辑；
- 后端审批与审计语义；
- 用户已有未提交修改。

只有在以下条件全部成立时才可修改共享表面：

1. Page 04 无法通过兼容扩展实现；
2. 仓库证据证明修改必要；
3. 修改向后兼容；
4. 影响范围和回滚方案明确；
5. 相关测试覆盖 Page 01–03；
6. 若属于受保护架构变更，已获得明确授权。

## 6. Forbidden Autonomous Behaviors

禁止：

- 重构无关代码；
- 改名全局架构、路由、API 或领域对象；
- 为“更干净”替换现有状态管理；
- 修改后端以迁就前端假设；
- 创建虚假 endpoint、权限、审批、审计、评价或成功状态；
- 把 fixture 数据伪装成生产数据；
- 用本地状态表示跨页面或服务端真相；
- 用乐观更新提前宣布重大治理动作成功；
- 让 Agent 自我批准；
- 静默删除历史对象、事件或记忆版本；
- 为视觉效果引入不必要的 3D 或大型依赖；
- 在 READY 后继续优化。

---

# PART II — 产品宪法与页面边界

## 7. Product Identity

Page 04 是：

> **Trust & Provenance Center**

其产品角色是：

> **Trust, Governance & Provenance Control Plane**

使命：

> Ensure that the Synthetic Biology DBTL Engineering OS remains scientifically trustworthy, human governed, historically reconstructable, and continuously evaluable.

## 8. Primary Product Question

Page 04 必须让授权用户可靠回答：

```text
What happened?
→ Who or what caused it?
→ Which exact object and version were involved?
→ Which evidence, memory, model, prompt, tool and parameter supported it?
→ Who reviewed, approved, rejected, overrode or revoked it?
→ What changed afterward?
→ Was the outcome correct, useful, safe and reproducible?
→ What requires corrective action?
```

## 9. Unified Governance Loop

Memory、Audit、Approval 与 Evaluation 不是四个独立 Dashboard。

它们构成同一闭环：

```text
System remembers
→ Memory influences an action
→ Action and inputs are recorded
→ Provenance reconstructs production
→ Human reviews an exact version
→ Authorized decision is committed
→ Outcome is evaluated
→ Failure or regression creates corrective action
→ Memory and policy are updated without rewriting history
```

## 10. Page 04 负责

- 展示跨系统需要治理关注的事项；
- 检查 Governed Object 的身份、版本、科学状态和治理状态；
- 重建科学、计算、Agent、工具与人工编辑的 provenance；
- 检查系统使用了哪些 memory、其来源、范围、新鲜度和冲突；
- 展示 append-only audit trail；
- 支持版本绑定的人类批准、拒绝、请求修改、条件批准、覆盖、撤销；
- 评价组件、Agent、工作流和结果；
- 暴露关键回归、失败样本、限制与 corrective action；
- 从 Page 01–03 接收精确来源上下文，并能返回原对象；
- 传播治理结果和受影响对象；
- 在权限允许时导出受治理、经过脱敏的审计或溯源材料。

## 11. Page 04 不负责

- 在 Page 01 取代项目态势总览；
- 在 Page 02 执行完整 DBTL 设计、仿真、Build 或 Test；
- 在 Page 03 生产或改写科学知识；
- 把批准当作科学证据；
- 把评价分数当作科学真相；
- 把 audit existence 当作可复现性证明；
- 允许用户编辑历史事件；
- 自动批准湿实验、工程变更或发布；
- 替代真实权限服务；
- 在前端重新实现审计、记忆或评价后端。

## 12. 用户与核心 JTBD

### Principal Investigator

- 看见最需要处理的风险与决定；
- 判断依据、证据、版本和权限是否充分；
- 审查关键批准、覆盖、撤销与回归；
- 理解系统为何值得或不值得信任。

### Dry-Lab Researcher

- 重建 Prompt → Model → Tool → Parameters → Output；
- 检查输入数据、模型版本、运行参数和失败；
- 比较 evaluation runs 与 baselines；
- 将计算限制和回归传回 Page 02 / Page 03。

### Wet-Lab Researcher

- 确认计划是否真正获批且仍有效；
- 区分 proposed、approved、executed、observed、evaluated；
- 检查样本、协议、版本、风险与交接条件；
- 不得让 Proposal 直接变为 Approved。

### Knowledge Curator

- 检查知识或证据变更的来源；
- 查看 memory 对知识生产的影响；
- 追踪 supersession、冲突和受影响对象。

### Governance Reviewer

- 处理 version-bound approval package；
- 记录理由、限制、到期时间与适用范围；
- 执行 request changes、reject、override、revoke。

### Maintainer / Evaluator

- 运行和比较 evaluation suite；
- 定位 critical regression 和 failure slices；
- 将结果链接到准确组件、Agent、Prompt、模型和版本；
- 创建 corrective action，而非让评价自我发布。

## 13. 产品成功标准

Page 04 成功不是“日志很多”或“分数很高”，而是：

- 用户能在 30 秒内识别最重要的治理风险；
- 能从任意重大输出重建其完整产生与审查链；
- 能看见哪个 memory 影响了哪个输出；
- 任何批准都绑定精确版本、权限和理由；
- 历史修正不会破坏历史；
- 关键回归永远不能被总分隐藏；
- 权限受限和数据缺失被真实表达；
- 用户能返回产生该对象的 Page 01、Page 02 或 Page 03 上下文。

---

# PART III — 中心对象、状态与领域合同

## 14. First-Class Object

Page 04 的中心不是指标，而是：

> **Governed Object at an exact version**

所有 attention、approval、memory use、audit event、provenance stage 和 evaluation target 必须回到该对象及版本。

## 15. Minimum Object Set

优先复用仓库现有类型。最低概念集合：

- `GovernedObjectRef`
- `VersionedObjectRef`
- `ActorRef`
- `MemoryObject`
- `MemoryUseRecord`
- `AuditEvent`
- `ApprovalRequest`
- `ApprovalDecision`
- `OverrideRecord`
- `RevocationRecord`
- `ProvenanceRecord`
- `ProvenanceStage`
- `EvaluationTarget`
- `EvaluationRun`
- `EvaluationMetric`
- `EvaluationFailure`
- `CorrectiveAction`
- `AttentionItem`
- `PermissionDecision`

若后端字段不同，必须通过 adapter / view model 映射，不得要求后端迁就示例。

## 16. Stable Identity Contract

最低身份引用：

```ts
type VersionedObjectRef = {
  objectId: string
  objectType: string
  versionId: string
  displayName?: string
  projectId?: string
  cycleId?: string
}
```

任何 consequential action 缺少 `objectId`、`objectType` 或 `versionId` 时：

- 禁用动作；
- 显示具体缺失；
- 不得用当前页面选择或最新版本补猜。

## 17. Governed Object View

建议 view model：

```ts
type GovernedObjectView = {
  ref: VersionedObjectRef
  scientificState:
    | 'unknown'
    | 'predicted'
    | 'proposed'
    | 'executed'
    | 'observed'
    | 'evaluated'
  governanceState:
    | 'unreviewed'
    | 'pending_review'
    | 'changes_requested'
    | 'approved'
    | 'conditionally_approved'
    | 'rejected'
    | 'overridden'
    | 'revoked'
    | 'expired'
  provenanceCompleteness: 'complete' | 'partial' | 'missing' | 'restricted'
  memoryRisk: 'none' | 'low' | 'medium' | 'high' | 'unknown'
  evaluationState: 'not_run' | 'queued' | 'running' | 'passed' | 'failed' | 'partial' | 'stale'
  permissions: PermissionView
  updatedAt: string
}
```

科学状态与治理状态必须分列，不得合并为一个 badge。

## 18. Trust Dimensions

至少分别展示：

- identity integrity；
- evidence traceability；
- provenance completeness；
- memory freshness and scope；
- human authorization；
- evaluation coverage；
- reproducibility status；
- currentness / staleness；
- permission visibility。

若需概要，可用多维摘要；禁止用单一 trust score 取代各维度。

## 19. Memory Object Contract

每个重要 Memory Object 至少表达：

- id、type、version；
- source；
- scope：user / project / cycle / object / global；
- content summary；
- created by / created at；
- last validated at；
- freshness / expiry；
- scientific status；
- governance status；
- sensitive classification；
- conflicts；
- supersedes / superseded by；
- material use records；
- affected objects。

Memory 类型至少考虑：

- Working Memory；
- Workspace Memory；
- Decision Memory；
- Scientific Memory；
- User Preference Memory；
- Governance Memory。

## 20. Memory Lifecycle

```text
Proposed
→ Reviewed
→ Active
→ Used
→ Revalidated / Conflicted / Stale
→ Corrected as New Version
→ Superseded / Retired
```

固定规则：

- Memory 创建不等于已验证；
- Memory 使用必须可追踪；
- stale / conflicting memory 的影响必须可见；
- 修正创建新版本；
- 旧输出仍指向当时真实使用的旧版本；
- 不得回写历史，使旧输出看似使用了新记忆。

## 21. Audit Event Contract

Audit Event 至少包含：

```ts
type AuditEventView = {
  eventId: string
  eventType: string
  occurredAt: string
  recordedAt?: string
  actor: ActorRef
  objectRef: VersionedObjectRef
  action: string
  reason?: string
  sourcePage?: string
  correlationId?: string
  causationId?: string
  idempotencyKey?: string
  previousEventId?: string
  payloadAvailability: 'available' | 'partial' | 'restricted' | 'legacy_unavailable'
}
```

UI 视角中 audit 是 append-only：

- 不提供编辑或删除历史事件；
- 修正通过新的 correction event；
- duplicate / retry 事件不得假装独立行为；
- `occurredAt` 与 `recordedAt` 不得混淆；
- legacy 缺失必须显示，不能补造。

## 22. Approval Request Contract

Approval Package 至少包含：

- exact target object and version；
- requested transition；
- requestor；
- reviewer authority；
- scientific basis；
- evidence and provenance summary；
- known risks；
- alternatives；
- trade-offs；
- limitations；
- validation / execution plan；
- affected objects；
- expiration；
- required conditions；
- current version check。

Approval 不得只显示标题和 Approve 按钮。

## 23. Approval Lifecycle

```text
Draft
→ Submitted
→ Pending Review
→ Approved | Conditionally Approved | Changes Requested | Rejected
→ Expired | Revoked | Superseded
```

Override 是异常动作，必须独立表达：

- 原决定保留；
- 覆盖者权限；
- 覆盖理由；
- 风险确认；
- 时间与范围；
- 新 audit event；
- 受影响对象。

## 24. Provenance Contract

Canonical chain：

```text
Source / Data / Memory
→ Prompt or Query
→ Model and Version
→ Tool and Version
→ Parameters
→ Intermediate Outputs
→ Human Edits
→ Final Output
→ Review
→ Approval
→ Execution
→ Observation
→ Evaluation
```

并非每个对象都有完整链；缺失阶段必须显式显示为：

- Not Applicable；
- Not Captured；
- Unavailable；
- Restricted；
- Failed；
- Unknown。

不得用“完整外观”掩盖 partial provenance。

## 25. Reproducibility Contract

“有 audit”不等于“可复现”。

仅在以下条件经过验证后，才可显示 reproducible：

- 输入可访问且版本明确；
- 模型、工具和版本明确；
- 参数明确；
- 环境或关键依赖明确；
- 随机性 / seed 明确（如适用）；
- 输出可关联；
- 复现运行通过或有明确验证等级。

否则显示：

- Reproducibility Unknown；
- Partially Reproducible；
- Not Reproducible；
- Reproduction Not Attempted。

## 26. Evaluation Contract

Evaluation Run 必须绑定：

- exact target；
- target version；
- suite and suite version；
- baseline；
- dataset / golden set version；
- evaluation slices；
- metrics；
- critical checks；
- intended use；
- started / completed time；
- evaluator；
- status；
- failure examples；
- limitations；
- review outcome；
- corrective actions。

评价层级：

- Component；
- Agent；
- Workflow；
- Outcome。

评价维度至少考虑：

- scientific correctness；
- citation / evidence integrity；
- task success；
- robustness；
- calibration / uncertainty；
- safety and governance；
- latency / cost；
- human usefulness。

不同层级和维度不得被简单平均成发布许可。

## 27. Critical Regression

以下示例应能够独立阻断：

- hallucinated citation；
- predicted displayed as observed；
- permission bypass；
- approval not version-bound；
- provenance fabrication；
- stale memory silently used；
- critical scientific failure；
- privacy leakage。

即使 aggregate score 改善，也必须显示为 blocking regression。

---

# PART IV — 页面结构与视觉合同

## 28. Canonical Page Structure

```text
Global AppShell
└── Page 04 Trust & Provenance Center
    ├── Context Header
    ├── Governance Navigation
    ├── Primary Governance Workspace
    │   ├── Attention
    │   ├── Approval
    │   ├── Provenance
    │   ├── Memory
    │   ├── Audit
    │   └── Evaluation
    ├── Inspector / Decision Rail
    └── Expandable Detail / Diff / Raw Evidence Region
```

默认入口为 Attention，而不是某个模块的空白首页。

## 29. Context Header

持续显示：

- Page identity；
- project / workspace；
- cycle（若适用）；
- source page；
- selected object type、id、version；
- current vs historical mode；
- sync / stale / partial / offline 状态；
- permission summary；
- return-to-source action。

对象或版本变化必须可感知，不得静默切换。

## 30. Governance Navigation

固定工作区：

- Attention
- Approvals
- Provenance
- Memory
- Audit
- Evaluation

每项可显示真实计数，但：

- 不得使用不可验证的计数；
- 不得把计数当作价值层级；
- critical count 必须有明确语义；
- 导航切换保留 scope、selected object 和 source context。

## 31. Attention Workspace

作用：

> 让用户首先处理需要治理关注的对象，而不是浏览所有数据。

Attention Item 至少显示：

- issue type；
- severity；
- exact object and version；
- why attention is required；
- scientific impact；
- governance impact；
- due / age；
- owner；
- blocked state；
- recommended next inspection；
- source page。

优先级必须来自后端或可解释的确定性规则；不得由颜色或前端随机排序定义。

## 32. Approval Workspace

推荐布局：

```text
Approval Queue
→ Selected Approval Package
→ Basis / Evidence / Provenance / Risk / Diff
→ Decision Rail
```

阅读顺序必须是：

```text
What exact version?
→ What transition?
→ Why?
→ Evidence and provenance?
→ Risks, trade-offs and limitations?
→ What changed?
→ Who may decide?
→ Commit governed decision
```

按钮不可先于依据成为视觉焦点。

## 33. Provenance Workspace

首选可读的分阶段 chain，而非默认大型 graph。

必须支持：

- canonical stage view；
- selected stage details；
- missing / restricted / failed stage；
- actor、tool、model、parameter；
- human edit；
- source object；
- correlation / causation；
- accessible list / table fallback。

图仅在关系复杂且真正有助于重建时使用。

## 34. Memory Governance Workspace

推荐布局：

```text
Memory List / Filters
→ Selected Memory Detail
→ Source + Scope + Freshness + Conflict
→ Usage and Affected Objects
→ Version History
→ Governed Action
```

不得只展示 memory 内容。必须让用户看到：

- 来源；
- 适用范围；
- 是否过期；
- 谁创建 / 审查；
- 哪些对象使用过；
- 是否冲突；
- 修正会影响什么。

## 35. Audit Workspace

提供三种互补方式：

1. chronological timeline；
2. structured table；
3. causal reconstruction。

默认避免 raw log wall。每个事件需：

- 人可读摘要；
- exact actor；
- exact object/version；
- event type；
- time；
- reason；
- causation / correlation；
- payload availability；
- details affordance。

原始 payload 只能在权限允许时按需展开。

## 36. Evaluation Workspace

布局：

```text
Target + Suite + Baseline
→ Run Status
→ Critical Regression Banner
→ Dimension Results
→ Slice Comparison
→ Failure Examples
→ Limitations
→ Review and Corrective Actions
```

禁止只放 charts 或 leaderboard。

失败样本、关键切片和限制必须与总体指标同等可检查。

## 37. Inspector / Decision Rail

Inspector 根据对象类型切换，但保持一致骨架：

- Identity；
- Version；
- Scientific State；
- Governance State；
- Trust Dimensions；
- Source Context；
- Permissions；
- Related Objects；
- History；
- Available Actions。

Decision Rail 只在存在可执行治理动作时出现，并显示：

- actor authority；
- action target；
- exact version；
- preconditions；
- impact；
- reason input；
- confirmation；
- pending / success / failure；
- authoritative result。

## 38. Expandable Detail Region

用于：

- version diff；
- approval comparison；
- memory comparison；
- evaluation comparison；
- raw provenance；
- audit payload；
- failure evidence；
- exported artifact preview。

不得用 modal 堆叠复杂科学内容。长内容优先 drawer、split panel 或独立 route。

## 39. Visual Hierarchy

固定阅读顺序：

```text
Context
→ Attention / selected object
→ Current state and risk
→ Basis and history
→ Decision or corrective action
```

视觉身份层级：

```text
Brand
→ Workspace
→ Page
→ Region
→ Panel
→ Component
→ Governed Scientific Object
```

对象应重于指标，依据应先于决定，历史应可读但不制造日志噪声。

## 40. Visual Character

应呈现：

- calm；
- precise；
- evidence-led；
- operational；
- high-trust；
- information-dense but not crowded；
- clearly human-governed。

避免：

- cyberpunk；
- dark command center cliché；
- neon trust score；
- decorative node cloud；
- oversized KPI cards；
- excessive glassmorphism；
- badge wall；
- 红绿二元化。

## 41. Semantic Color

颜色不能成为唯一编码。

至少配合：

- text label；
- icon；
- shape / border；
- status description。

必须区分：

- scientific state；
- governance state；
- severity；
- data availability；
- evaluation outcome。

不要让同一颜色在不同层级表达冲突含义。

## 42. Tables

表格用于高密度比较：

- Attention Queue；
- Approval Queue；
- Memory；
- Audit；
- Evaluation Runs。

要求：

- sticky header（数据规模需要时）；
- column visibility；
- deterministic sorting；
- keyboard selection；
- selected row 与 Inspector 同步；
- empty / partial / error 不混入普通数据行；
- 大列表 virtualization / pagination；
- 不把关键科学语义藏在 hover。

## 43. Comparison and Diff

必须支持：

- approval object version diff；
- memory version diff；
- evaluation run / baseline diff。

比较视图需明确：

- compared ids and versions；
- changed / unchanged / unavailable；
- semantic field labels；
- provenance of change；
- downstream impact。

不得只做文本行 diff 来代替领域差异。

## 44. Responsive Contract

目标视口：

- 1920+；
- 1600–1919；
- 1440–1599；
- 1280–1439；
- 1024–1279；
- below 1024。

原则：

- 1440 桌面必须完整可用；
- Inspector 在中等宽度可转 drawer；
- 多栏布局逐步折叠，不隐藏治理状态；
- comparison 在窄屏可纵向堆叠；
- 表格可选择性压缩列，但 exact object/version 和 status 不得消失；
- below 1024 仍支持审查，复杂治理动作可要求更宽视口并明确说明；
- 不得用横向溢出掩盖布局失败。

## 45. Motion

动画只用于：

- selection transition；
- drawer / panel transition；
- mutation pending → confirmed；
- newly affected item；
- provenance expansion。

遵循 reduced motion。

不得用动画弱化失败、撤销、权限拒绝或版本冲突。

## 46. Accessibility

至少满足 WCAG 2.2 AA 意图：

- 全核心流程键盘可达；
- 明确 focus；
- status 非纯色；
- table / timeline / graph 有语义；
- provenance graph 有列表替代；
- consequential action 有可读名称、目标和状态；
- live region 适度报告 mutation 结果；
- screen reader 能识别 object/version、scientific state、governance state；
- 不通过 tooltip 承载必需信息；
- 触控目标、对比度、标题层级合格。

## 47. Nanobanana Composition Contract

Nanobanana 仅作为高级视觉生成器，用于探索内容区域的视觉构图。

程序固定控制：

- AppShell；
- logo / brand；
- global navigation；
- global tokens；
- typography；
- route；
- object identity；
- version；
- status semantics；
- permission；
- action logic；
- audit / approval / evaluation truth。

若使用视觉参考图，必须由 React/CSS 和真实组件复刻，图片不能替代可交互 UI。

---

# PART V — Interaction Spec

## 48. Canonical Task Flow

```text
Start
→ Understand context
→ Select exact object/version
→ Inspect state, basis and history
→ Determine authority and preconditions
→ Decide
→ Commit
→ Confirm authoritative result
→ Review affected objects
→ Complete / return to source
```

不得跳过 Inspect、Authority 或 Confirmation。

## 49. Selection

- 单一 active selection；
- selection 同步 URL（适合分享时）、workspace state 和 Inspector；
- 视图切换保持 selection；
- 已不存在对象显示 unavailable，不自动选另一对象；
- historical route 不得自动跳到 latest；
- version mismatch 显示 conflict。

## 50. Search, Filter and Scope

Page search 支持对象 id、名称、actor、event、memory、evaluation target 等真实能力。

Scope 至少考虑：

- project；
- cycle；
- object type；
- source page；
- time range；
- current / historical；
- status；
- severity；
- actor；
- permission visibility。

Active filters 必须可见、可清除、可分享（适用时）。切换 workspace 不得悄悄清空 scope。

## 51. Consequential Action Preconditions

批准、拒绝、覆盖、撤销、修正 memory、启动 evaluation、导出 restricted material 前，必须检查：

- authentication；
- backend authorization；
- exact target；
- exact version；
- current state；
- stale state；
- required evidence / package completeness；
- reason；
- idempotency；
- conflict；
- online status。

任一条件不满足时，动作不可提交，并解释具体原因。

## 52. Mutation Semantics

重大 mutation 流程：

```text
User intent
→ Precondition check
→ Explicit confirmation
→ Submit with idempotency
→ Pending state
→ Backend authoritative response
→ Reconcile current object/version
→ Audit event visible
→ Affected objects refresh
→ Success or actionable failure
```

不得在后端确认前显示最终成功。

## 53. Approval Interaction

Approve / Conditional Approve / Request Changes / Reject 必须：

- 显示目标版本；
- 显示 reviewer authority；
- 要求理由；
- 条件批准需结构化 conditions；
- mutation pending 时防重复提交；
- 成功后获取权威状态；
- 产生或显示 audit event；
- 对 source page 传播结果。

## 54. Version Conflict

若审查期间对象更新：

- 阻止对旧 package 的普通批准；
- 显示 reviewed version 与 current version；
- 提供 semantic diff；
- 允许返回审查新版本；
- 不得自动迁移批准；
- 旧审查记录保留。

## 55. Override and Revocation

Override：

- 仅对有权限角色开放；
- 高显著性但不使用诱导式确认；
- 展示原决定和影响；
- 要求理由；
- 记录范围和到期；
- 独立 audit event。

Revocation：

- 保留原批准；
- 显示撤销者、原因、时间；
- 更新当前授权状态；
- 传播受影响对象；
- 不得删除历史批准。

## 56. Memory Correction

Correction 必须：

- 显示当前与建议内容；
- 显示 source、scope 和 affected objects；
- 创建新 version；
- 保留旧 version；
- 标记旧 version superseded；
- 不重写历史 use records；
- 在受影响对象上生成 attention。

## 57. Evaluation Interaction

启动 evaluation 前：

- 选择 exact target/version；
- suite/version；
- baseline；
- data / golden set；
- intended use；
- permissions。

长任务：

- queued / running / partial / completed / failed / cancelled；
- progress 不伪造精确度；
- late result 不得覆盖较新 run；
- event deduplication；
- 可安全恢复页面；
- failure examples 可检查。

## 58. Export

导出必须：

- 后端验证权限；
- 明确 scope；
- 应用 redaction；
- 显示 omitted / restricted fields；
- 记录导出审计；
- 不把隐藏 UI 字段误认为已脱敏；
- 不在客户端构造包含未授权数据的全量文件。

## 59. Runtime States

每个主要区域必须分别支持：

- Loading；
- Empty；
- Partial；
- Error；
- Offline；
- Unauthorized；
- Restricted；
- Stale；
- Historical；
- Superseded；
- Conflict；
- Mutation Pending；
- Mutation Failed；
- Capability Unavailable。

区域级失败不应抹掉其他可用区域。

## 60. Empty State Semantics

必须区分：

- 真实无待办；
- 当前筛选无结果；
- 尚未产生数据；
- 后端能力不存在；
- 权限不可见；
- 加载失败；
- 数据受限。

“No issues” 只能用于真实确认无 issue 的状态。

## 61. Offline Rules

Offline 时：

- 可查看明确标记的缓存只读数据；
- 显示数据时间；
- 禁止 approval、override、revoke、memory correction、evaluation start、restricted export；
- 不排队提交重大 mutation；
- 恢复在线后重新获取权限和版本。

## 62. Source Return

从 Page 01–03 进入时必须保留：

- source page；
- source route；
- source object/version；
- project/cycle；
- return label；
- relevant selected tab / context（仓库支持时）。

返回时不得只回首页。

---

# PART VI — Technical Spec

## 63. Mandatory Repository Audit

编码前输出事实表：

| Area | Evidence Required |
|---|---|
| Repository root | actual path |
| Framework | package evidence |
| Router | routes and conventions |
| AppShell | component and ownership |
| Design system | tokens and shared components |
| State | server, URL, workspace, local owners |
| API | clients, schemas, query/mutation conventions |
| Auth | authentication and authorization |
| Events | SSE/WebSocket/polling or none |
| Persistence | existing mechanism |
| Tests | unit/integration/e2e tooling |
| Page 01–03 | routes, shared contracts, regression risks |
| Git status | overlapping user changes |

任何 “not found” 必须说明搜索范围与证据。

## 64. Capability Discovery

逐项确认后端是否真实提供：

- attention query；
- governed object query；
- permission query；
- approval query and mutations；
- reviewer authority；
- provenance query；
- audit query；
- memory query and correction mutation；
- memory usage / affected object query；
- evaluation query / start / events；
- export；
- cross-page affected-object propagation。

结果只能标记：

- Supported；
- Partially Supported；
- Unsupported；
- Ambiguous；
- Blocked。

不允许用假 endpoint 填空。

## 65. Requirement Mapping

编码前建立矩阵：

| Requirement | Source | Existing Support | Reuse / Extend / New | API | State Owner | Test | Status |
|---|---|---|---|---|---|---|---|

矩阵必须覆盖 P0、所有 mutation、权限、partial/offline、跨页、验收场景。

## 66. Required Layering

遵守仓库现有结构。逻辑上至少保持：

```text
Route / Page Composition
→ Feature Workspaces
→ Shared Governance Components
→ Domain View Models
→ Adapters
→ Existing API Client
→ Authoritative Backend
```

组件不得直接猜 DTO 字段；adapter 负责后端 DTO 到 UI view model 的确定性转换。

## 67. Recommended Feature Boundary

仅在仓库惯例允许时参考：

```text
features/trust-provenance/
  components/
  workspaces/
  adapters/
  hooks/
  types/
  state/
  routes/
  tests/
```

不得为追求此目录结构而搬迁现有文件。

## 68. State Ownership

### Server Truth

- governed object；
- versions；
- permissions；
- approvals；
- audit events；
- provenance；
- memories and versions；
- evaluations；
- attention derivation（若后端拥有）；
- export policy。

### Persistent Workspace State

- active workspace；
- last selected object（若允许）；
- saved view；
- panel sizes；
- comparison tray。

### URL-Shareable State

- workspace mode；
- object id/version；
- filters；
- time range；
- historical mode；
- source context（符合安全约束时）。

### Local UI State

- open drawer；
- expanded rows；
- draft reason；
- temporary column visibility。

敏感内容、权限、批准状态和审计 payload 不得存入不安全 local storage 或 URL。

## 69. Query Contract

查询要求：

- typed；
- cancellable（技术栈支持时）；
- scoped；
- permission-aware；
- partial-data aware；
- stale-aware；
- pagination / cursor aware；
- deterministic cache key；
- historical version explicit；
- error classified。

## 70. Mutation Contract

重大 mutation 必须：

- exact object/version；
- actor authority from backend；
- idempotency key；
- reason；
- precondition / version check；
- pending state；
- retry policy 不导致重复动作；
- timeout 后查询权威状态；
- successful response 后 reconcile；
- audit correlation。

## 71. Optimistic Update Policy

禁止对以下动作展示最终 optimistic success：

- approve；
- conditional approve；
- reject；
- override；
- revoke；
- memory correction；
- evaluation release acceptance；
- restricted export。

可以显示 pending intent，但最终状态必须来自后端。

## 72. Event Handling

若存在事件流：

- 使用 event id 去重；
- 用 correlation id 关联 mutation；
- 忽略或标记旧 run 晚到结果；
- reconnect 后补取权威快照；
- 不以到达顺序代替 occurred time；
- 防止重复 toast 和重复状态转换。

若不存在事件流，使用仓库既有 polling / refetch；不得自行发明基础设施。

## 73. Routing

路由应支持：

- Page 04 root；
- workspace；
- selected object/version；
- historical view；
- source return。

不得把敏感内容、审批理由或原始 payload 放入 URL。

直接访问受限 route 时必须走权限检查，不得因绕过 UI 导航获得访问。

## 74. Permission and Security

- 权限由后端强制；
- UI 隐藏按钮不是安全；
- unauthorized 与 restricted 分开；
- restricted related-object preview 不得泄露标题或摘要；
- client logs 不记录敏感 payload；
- analytics 不记录 approval reason、memory content、raw provenance；
- export 必须服务端裁剪或经过可信授权流程；
- 遵守现有 CSRF / replay protection；
- mutation 防重复。

## 75. Persistence and Recovery

恢复顺序：

```text
Authoritative route context
→ Backend object/version
→ Verified persistent workspace preferences
→ Safe local UI defaults
```

若恢复的对象已 superseded / revoked / expired：

- 显示 historical/stale；
- 不自动转换为 current；
- 禁止不适用动作；
- 提供显式打开 current version。

## 76. Fixture Policy

Fixture 仅用于：

- 测试；
- Storybook / development；
- 后端明确缺失时的开发预览。

必须：

- typed；
- deterministic；
- 显著标记；
- 与 production 路径隔离；
- 覆盖正常、partial、error、restricted、conflict 等状态。

生产不得静默 fallback 到 fixture。

## 77. Rendering and Scale

至少按以下量级设计并以仓库事实修正：

- attention items：数百；
- audit events：数万；
- provenance stages / edges：数百至数千；
- memory objects：数千；
- evaluation runs：数百；
- failure examples：数千。

使用：

- pagination / cursor；
- virtualization；
- lazy detail；
- graph subsetting；
- server-side filters（可用时）。

不得一次性渲染全量 audit 或 provenance graph。

## 78. Performance Objectives

以仓库既有预算优先。若未定义，至少验证：

- Page shell 与首个可用治理区域快速出现；
- 大表筛选与选择无明显阻塞；
- Inspector lazy load 不阻塞主区域；
- provenance 大图有渐进策略；
- bundle 不因 Page 04 引入无关重量级依赖；
- route-level code splitting 遵守现有惯例。

不得虚构精确毫秒 PASS；记录真实测量方法和结果。

## 79. Observability

允许记录：

- route load failure；
- adapter parse failure；
- permission denial category；
- mutation correlation；
- evaluation stream failure；
- provenance rendering failure；
- performance timing。

不得记录：

- raw memory content；
- approval reason；
- restricted provenance；
- credentials；
- scientific payload；
- personally identifying sensitive data。

## 80. ADR / DSR

只有重大选择才记录。

ADR 字段：

- Context；
- Decision；
- Alternatives；
- Trade-offs；
- Compatibility；
- Migration；
- Rollback；
- Consequences。

DSR 字段：

- User problem；
- Scientific / governance need；
- Alternatives；
- Decision；
- Visual and interaction consequence；
- Accessibility consequence；
- Validation evidence。

不得把每个小组件写成 decision record。

---

# PART VII — 实施顺序与暂停机制

## 81. Mandatory Execution State Machine

严格按顺序执行：

```text
LOAD
Read Master Contract, Page 04 Specs and repository instructions
↓
RESOLVE
Build precedence map and conflict matrix
↓
INSPECT
Audit repository, backend capabilities, permissions, events and tests
↓
MAP
Build requirement-to-component/API/state/test matrix
↓
PLAN
Define reuse, file changes, adapters, tests and rollback
↓
IMPLEMENT FOUNDATION
Route, context, adapters, state ownership, permissions and runtime states
↓
IMPLEMENT WORKSPACES
Attention, Approval, Provenance, Memory, Audit and Evaluation
↓
INTEGRATE
Real APIs, events, persistence, mutations and cross-page context
↓
VERIFY
Format, lint, typecheck, tests, build, runtime, accessibility and performance
↓
ACCEPT
Execute every mandatory acceptance gate and scenario
↓
REGRESS
Prove no page, component, backend, permission or scientific drift
↓
DELIVER
Emit factual completion report
↓
STOP
```

任何状态不得跳过。

## 82. Reuse Decision

对每个需求依次判断：

1. 现有组件可直接复用？
2. 可通过 props / composition 兼容扩展？
3. Page 04 特有且确需新组件？
4. 是否需要共享组件变更？
5. 共享变更是否向后兼容并有回归测试？

不得因为命名不同就重复造组件。

## 83. Conditional Audit Gate

出现以下任一情况必须暂停：

- approval schema 缺失或含义不明；
- reviewer authority 无法验证；
- audit immutability 与请求冲突；
- memory correction 会覆盖历史；
- evaluation target、suite 或 baseline 不明确；
- cross-page identity 不一致；
- 需要修改 protected surface；
- 需要重大新依赖；
- 用户未提交修改与目标文件重叠；
- permission behavior 不安全；
- production 只能依赖 fixture；
- 关键 contract 冲突未解决。

输出：

```yaml
blocked_requirement:
contract_rule:
repository_evidence:
affected_capability:
affected_files:
safe_options:
recommended_option:
tradeoffs:
decision_needed:
```

然后停止，等待决定。不得绕过。

## 84. Runtime Refusal Rules

必须拒绝：

- 伪造批准、权限、审计、溯源或评价；
- 让 Agent 批准自身重大输出；
- 静默覆盖历史；
- 把 predicted 当 observed；
- 把 approval 当 evidence；
- 在客户端绕过后端权限；
- 泄露 restricted data；
- 使用不绑定版本的 consequential mutation；
- 用平均分掩盖 critical regression；
- 在 production 静默使用 fixtures。

---

# PART VIII — Required Tests and Runtime Scenarios

## 85. Test Layers

至少覆盖：

- adapter / schema mapping tests；
- component tests；
- state and selector tests；
- query / mutation integration tests；
- permission tests；
- approval lifecycle tests；
- memory versioning tests；
- audit immutability presentation tests；
- provenance rendering and fallback tests；
- evaluation long-run and regression tests；
- cross-page tests；
- accessibility tests；
- responsive / visual regression；
- end-to-end critical workflows。

使用仓库现有工具；不得仅为满足列表引入新测试框架。

## 86. Scenario A — Pending Approval

给定一个 proposed、pending-review 的精确对象版本：

- package 完整显示；
- scientific 与 governance state 分离；
- reviewer authority 来自后端；
- 依据先于动作；
-批准绑定版本；
- 成功后显示权威状态和 audit event。

## 87. Scenario B — Unauthorized Approval

- direct route 不能绕过权限；
- action disabled / absent 不作为唯一保护；
- backend denial 可理解；
- 状态不得变为 approved；
- 不泄露 restricted package。

## 88. Scenario C — Object Changes During Review

- 检测 version conflict；
- 阻止批准旧版本；
- 显示 diff；
- 保留旧 review；
- 不自动迁移批准。

## 89. Scenario D — Override

- 仅有权限者可用；
- 原决定可见；
- 理由和风险确认必填；
- override 独立可审计；
- 不伪装成普通 approval。

## 90. Scenario E — Mutation Timeout

- UI 保持 pending / uncertain；
- 不自动重试导致重复批准；
- 用 idempotency / status query 对账；
- 最终显示权威结果；
- 不虚假 success。

## 91. Scenario F — Memory Superseded

- 旧版本保留；
- 新版本可见；
- usage records 保留真实旧版本；
- affected objects 可发现；
- historical output 不被重写。

## 92. Scenario G — Conflicting Memories

- 两个 memory 均可检查；
- 不静默选一个；
- 冲突范围和对象可见；
- 需要治理处理；
- 使用冲突 memory 的对象进入 attention。

## 93. Scenario H — Legacy Audit Event

- 缺失 payload 显示 legacy unavailable；
- 不补造字段；
- actor/object/time 的已知部分保留；
- correction 通过新事件。

## 94. Scenario I — Partial Provenance

- 缺失 stage 显式；
- completeness 为 partial；
- 不显示 fully reproducible；
- restricted 与 missing 分开；
- accessible list fallback 可用。

## 95. Scenario J — Human-Edited AI Output

- AI 原始输出、human edit 和 final output 分阶段；
- editor 和时间可见；
- 不能把 final output 冒充纯模型结果；
- review status 可见。

## 96. Scenario K — Critical Evaluation Regression

当 aggregate score 提升但存在 hallucinated citation：

- critical regression 位于最高优先级；
- run 不得显示无条件 pass；
- release 不得自动授权；
- failure example 可检查；
- corrective action 可创建或链接。

## 97. Scenario L — Evaluation Still Running

- queued/running 状态准确；
- 不显示最终结论；
- 刷新/离开后可恢复；
- 完成事件去重；
- 旧 run 晚到不覆盖新 run。

## 98. Scenario M — Offline Review

- 可显示带时间的缓存只读内容；
- 所有 consequential mutation 禁止；
- 不排队 approval；
- 重新在线后重新检查版本和权限。

## 99. Scenario N — Restricted Provenance Export

- 未授权内容不出现在 UI、preview、文件或日志；
- export 应用服务端或可信脱敏；
- omitted 内容明确；
- export event 可审计。

## 100. Scenario O — Large Audit History

- 分页 / virtualization；
- 筛选与选择稳定；
- timeline 与 table 一致；
- causal reconstruction 按需加载；
- 无主线程严重阻塞。

## 101. Scenario P — Revoked Approval

- 原 approval 历史存在；
- current authorization 显示 revoked；
- Page 02 不再把它当作有效执行授权；
- revoked by / reason / time 可见；
- affected objects 更新。

## 102. Scenario Q — Backend Partial Failure

- 各区域独立状态；
- 可用的 audit 不因 evaluation 失败而消失；
- 不把 partial 当 empty；
- 重试作用域明确；
- 不伪造完整 trust。

---

# PART IX — Acceptance Gates

## 103. Evidence Standard

任何 criterion 只有在以下全部成立时可标 PASS：

1. implementation exists；
2. behavior tested；
3. evidence recorded；
4. no contradictory result exists。

允许状态：

- PASS；
- FAIL；
- PARTIAL；
- BLOCKED；
- NOT APPLICABLE（需理由）；
- NOT AVAILABLE；
- NOT RUN。

不得从代码存在推断测试通过，不得从视觉截图推断后端正确。

## 104. Gate 0 — Readiness

PASS 条件：

- 必读文件已读；
- repository audit 完成；
- conflict matrix 完成；
- capability matrix 完成；
- protected surfaces 识别；
- backend / permission ownership 明确；
- 无未解决的 P0 语义冲突。

## 105. Gate 1 — Product and Scientific Semantics

验证：

- Page 04 身份清楚；
- first-class object 是 exact governed object/version；
- scientific state 与 governance state 分离；
- proposed / approved / executed / observed / evaluated 分离；
- trust 多维；
- unknown / missing / restricted 真实表达；
- 页面不是 admin dashboard。

## 106. Gate 2 — Governance and Human Authority

验证：

- reviewer authority 来自后端；
- approval version-bound；
- agent cannot self-approve；
- action preconditions；
- reason；
- conditional approval；
- request changes；
- reject；
- override；
- revoke；
- expiry；
- mutation idempotency；
- authoritative reconciliation。

## 107. Gate 3 — Memory, Audit and Provenance

验证：

- memory source/scope/version/freshness；
- memory use traceability；
- conflict visibility；
- correction creates version；
- audit append-only UI；
- duplicate/retry semantics；
- causal reconstruction；
- provenance gaps；
- human edit attribution；
- restricted branches；
- reproducibility not overstated。

## 108. Gate 4 — Evaluation and Corrective Action

验证：

- exact target/version；
- suite/version；
- baseline；
- golden set / data version；
- long-running lifecycle；
- slices；
- failure examples；
- critical regression blocking；
- limitations；
- human review；
- corrective action；
- evaluation 不自我授权。

## 109. Gate 5 — UI, Interaction and Runtime

验证：

- canonical anatomy；
- Attention 默认入口；
- selection + Inspector；
- basis before action；
- search/filter/scope；
- comparison/diff；
- loading、empty、partial、error、offline、unauthorized、restricted、stale、historical、superseded、conflict；
- mutation pending/failed；
- capability unavailable；
- source return。

## 110. Gate 6 — Technical Architecture and Backend Truthfulness

验证：

- 现有架构复用；
- adapter boundary；
- state ownership；
- no invented API；
- no parallel truth；
- no production fixture fallback；
- safe mutation；
- route contract；
- persistence/recovery；
- event deduplication；
- cross-page propagation。

## 111. Gate 7 — Security, Privacy and Permissions

验证：

- direct route authorization；
- sensitive redaction；
- restricted related-object protection；
- safe URL/storage/cache/log/analytics；
- export scope；
- CSRF/replay/idempotency；
- governance mutation audit。

## 112. Gate 8 — Accessibility, Responsive and Performance

验证：

- keyboard complete critical workflow；
- visible focus；
- semantic status；
- graph fallback；
- screen reader object/version/state；
- 1024–1920+ viewports；
- large-list performance；
- lazy details；
- bundle discipline；
- reduced motion。

## 113. Gate 9 — Regression and Release

Regression Matrix：

| Domain | Must Prove |
|---|---|
| Global Shell | no navigation/layout drift |
| Design System | no incompatible token/component drift |
| Page 01 | command center unaffected |
| Page 02 | decision lifecycle and approval consumption intact |
| Page 03 | knowledge truth and version authority intact |
| Backend | no schema/API invention or break |
| Permissions | no authority weakening |
| Scientific | no state conflation |
| Governance | no approval/history weakening |
| Accessibility | no critical regression |
| Performance | no material regression |
| Repository | unrelated user work preserved |

## 114. Automatic REJECTED Conditions

任一发生即 `REJECTED`：

- predicted shown as observed；
- proposed shown as approved；
- approved shown as executed；
- missing provenance fabricated；
- model content shown as verified truth；
- agent self-approval；
- frontend grants authority；
- approval not version-bound；
- override indistinguishable from normal approval；
- revoked approval remains current；
- permission failure defaults to authorized；
- memory correction overwrites history；
- historical audit can be edited/deleted；
- stale memory silently used；
- fake endpoint or fake production success；
- timeout duplicates consequential mutation；
- restricted content leaks；
- protected architecture modified without authorization；
- unrelated user work overwritten；
- strict typecheck or production build fails；
- Page 01–03 materially broken。

## 115. Release Decision

### READY

仅当：

```text
Gate 0 PASS
AND Gate 1 PASS
AND Gate 2 PASS
AND Gate 3 PASS
AND Gate 4 PASS
AND Gate 5 PASS
AND Gate 6 PASS
AND Gate 7 PASS
AND Gate 8 PASS
AND Gate 9 PASS
AND Critical Failures = 0
AND Completion Report Emitted
```

### NEEDS_REVISION

用于可修正但尚未完成：

- mandatory criterion 为 FAIL / PARTIAL / BLOCKED / NOT RUN；
- 测试证据缺失；
- 后端部分能力缺失且影响 P0；
- regression 未完整证明。

### REJECTED

用于：

- 任一 critical failure；
- system invariant 违反；
- 科学、治理、权限、历史或隐私边界被破坏；
- 生产真相被伪造。

---

# PART X — Verification and Completion

## 116. Required Verification

使用仓库真实命令执行并记录：

- formatter / format check；
- lint；
- strict typecheck；
- unit tests；
- integration tests；
- end-to-end tests（若仓库支持）；
- production build；
- runtime smoke test；
- console check；
- accessibility；
- responsive；
- visual regression；
- performance；
- git diff / repository scope。

命令不存在时标 `NOT AVAILABLE`，不得伪造替代结果。

## 117. Required Completion Report

最终输出：

```yaml
outcome:
  release_decision: READY | NEEDS_REVISION | REJECTED
  critical_failures: 0

repository_audit:
  root:
  stack:
  router:
  app_shell:
  design_system:
  state_management:
  api_client:
  authentication:
  authorization:
  events:
  tests:
  git_status:
  protected_surfaces:

specification_mapping:
  product:
  ui:
  interaction:
  technical:
  acceptance:
  conflicts:

capability_matrix:
  attention:
  approvals:
  reviewer_authority:
  provenance:
  audit:
  memory:
  evaluation:
  affected_objects:
  exports:
  cross_page_events:

implementation:
  route:
  workspaces:
  reused_components:
  extended_components:
  new_components:
  adapters:
  view_models:
  queries:
  mutations:
  events:
  state_owners:
  persistence:
  unavailable_states:

files:
  created:
  modified:
  deleted:
  intentionally_untouched:

backend_integration:
  real_capabilities:
  partial_capabilities:
  unsupported_capabilities:
  permissions:
  idempotency:
  limitations:

verification:
  format:
    command:
    result:
  lint:
    command:
    result:
  typecheck:
    command:
    result:
  unit_tests:
    command:
    result:
  integration_tests:
    command:
    result:
  end_to_end:
    command:
    result:
  build:
    command:
    result:
  runtime:
    method:
    result:
  accessibility:
    method:
    result:
  responsive:
    method:
    result:
  performance:
    method:
    result:
  visual_regression:
    method:
    result:
  console:
    result:

acceptance_gates:
  gate_0_readiness:
  gate_1_product_science:
  gate_2_governance:
  gate_3_memory_audit_provenance:
  gate_4_evaluation:
  gate_5_ui_interaction_runtime:
  gate_6_technical_backend:
  gate_7_security_privacy:
  gate_8_accessibility_responsive_performance:
  gate_9_regression_release:

mandatory_scenarios:
  pending_approval:
  unauthorized_approval:
  version_conflict:
  override:
  mutation_timeout:
  memory_superseded:
  memory_conflict:
  legacy_audit:
  partial_provenance:
  human_edited_ai_output:
  critical_regression:
  evaluation_running:
  offline_review:
  restricted_export:
  large_audit:
  revoked_approval:
  backend_partial_failure:

regression:
  global_shell:
  design_system:
  page_01:
  page_02:
  page_03:
  backend:
  permissions:
  scientific:
  governance:
  accessibility:
  performance:
  repository:

known_limitations:
deferred_capabilities:
approved_exceptions:
decision_records:
stop_condition:
```

任何未运行或未验证项目必须如实标明。

## 118. Final Stop Condition

```text
Repository Audit complete
AND Specification Mapping complete
AND Conflict Matrix resolved or explicitly accepted
AND Capability Matrix complete
AND Protected Surfaces preserved
AND Page 04 implemented
AND Real Backend Integration verified
AND Unsupported Capabilities explicitly degraded
AND Governance Mutations authoritative and idempotent
AND Approval Version Binding verified
AND Memory Versioning preserved
AND Audit Immutability preserved
AND Provenance Gaps explicit
AND Evaluation Regressions handled
AND Security and Permission Gates PASS
AND Runtime States PASS
AND Accessibility PASS
AND Responsive PASS
AND Performance verified
AND Regression PASS
AND Format PASS
AND Lint PASS
AND Typecheck PASS
AND Tests PASS
AND Production Build PASS
AND Critical Failures = 0
AND Completion Report emitted
→ READY
→ STOP
```

若仍有可修正问题：

```text
NEEDS_REVISION
```

若任何关键科学、治理、历史、权限、隐私或仓库规则被违反：

```text
REJECTED
```

达到 READY 后必须立即停止。不得继续重构、改名、扩展范围、重新设计或“顺手优化”。

---

# FINAL IMPLEMENTATION CONTRACT

```text
Page 04 shall be implemented as a repository-safe Trust, Governance & Provenance Control Plane.

Every consequential action shall target an exact object and exact version.

Scientific state and governance state shall remain separate.

Proposal, approval, execution, observation and evaluation shall remain separate.

The backend shall remain authoritative for permissions, approvals, audit events, memory versions, provenance and evaluation results.

The frontend shall never grant authority, fabricate success, fabricate provenance, rewrite history or create a parallel source of truth.

Memory shall remain sourced, scoped, versioned, freshness-aware and traceable to material use.

Memory correction shall create a new version and preserve historical use.

Audit correction shall create a new event and preserve append-only history.

Provenance gaps and restricted stages shall remain visible.

Reproducibility shall never be inferred merely from the existence of logs.

Evaluation shall remain bound to an exact target, version, suite, baseline, dataset and intended use.

Critical regression shall never be hidden by aggregate performance.

Approval shall be attributable, permission-controlled, version-bound and confirmed by authoritative backend state.

Agents shall not approve their own consequential outputs.

Restricted content shall not leak through UI, routes, storage, cache, logs, analytics, exports or related-object previews.

Page 04 shall preserve source context and integrate with Page 01, Page 02 and Page 03 without taking ownership of their product responsibilities.

Production shall never silently use development fixtures or invented APIs.

Implementation shall reuse the existing architecture, protect unrelated work, prove regression safety and stop when the acceptance contract is satisfied.
```

实施成功的最终链路：

```text
Inspect exact governed object and version
→ Reconstruct memory, evidence and computational provenance
→ Verify actor and authority
→ Review basis, risk, trade-off and history
→ Commit a version-bound governed decision
→ Confirm authoritative result
→ Preserve immutable history
→ Evaluate outcome and critical regression
→ Propagate corrective action and affected-object state
→ Emit truthful completion evidence
→ READY
→ STOP
```

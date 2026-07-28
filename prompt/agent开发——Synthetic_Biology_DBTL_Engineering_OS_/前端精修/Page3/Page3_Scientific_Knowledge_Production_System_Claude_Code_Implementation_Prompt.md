# Synthetic Biology DBTL Engineering OS

# Page 03 — Scientific Knowledge Production System

## Claude Code 完整实现 Prompt

> 本文件是 Page 03 的单一实现入口。  
> 它整合 Product Spec、UI Spec、Interaction / Operating Principles、Technical Spec、Acceptance Spec，并继承 `Synthetic_Biology_DBTL_Engineering_OS_Page_Design_Contract_v1.2.md`。  
> 你的任务是审计现有仓库，在不破坏全局架构、科学语义和人工治理边界的前提下，实现、测试并验收 Page 03，然后停止。

---

## 0. 你的角色

你不是自由发挥的页面设计师，也不是负责重写整个系统的架构师。

你同时承担：

- Senior Product Engineer
- Scientific UX Engineer
- Frontend Architect
- Knowledge Systems Engineer
- Synthetic Biology Informatics Engineer
- Accessibility and Performance Engineer
- Scientific QA Reviewer

你必须把规范转化为真实、可运行、可测试、可维护的 React 页面。

你不得：

- 把 Page 03 做成论文文件夹、文献搜索页或普通知识库；
- 把知识图谱当成装饰性背景；
- 用流畅的 AI 摘要冒充科学证据；
- 让 Page 02 在引用知识时改写受治理的知识对象；
- 用前端假状态伪装不存在的后端能力；
- 擅自改动后端科学逻辑、全局导航、对象模型或设计系统；
- 在全部验收通过后继续“顺手优化”。

---

# PART I — 权威来源、系统不变量与冲突裁决

## 1. 必读文件

开始编码前，按顺序读取：

1. `Synthetic_Biology_DBTL_Engineering_OS_Page_Design_Contract_v1.2.md`
2. `01_Product_Spec(3).md`
3. `02_UI_Spec(3).md`
4. `03_Scientific_Knowledge_Operating_Principles(1).md`
5. `04_Technical_Spec(3).md`
6. `05_Acceptance_Spec(3).md`
7. 当前仓库中的 `AGENTS.md`、README、package manifest、路由、AppShell、全局 token、共享类型、API client、现有 Page 1 / Page 2 实现与测试

若文件在不同目录，以仓库中的实际路径为准。不得仅凭本 Prompt 猜测现有实现。

## 2. 规范解释

本 Prompt 不是五份文件的机械拼接，而是它们面向 Page 03 的可执行收敛。

解释原则：

- Product Spec 定义为什么存在、服务谁、负责什么；
- UI Spec 定义知识关系如何被看见和理解；
- Operating Principles 定义科学对象、生命周期、权限和交互语义；
- Technical Spec 定义如何在现有仓库内实现；
- Acceptance Spec 定义如何证明完成；
- Master Contract v1.2 定义全局不变量、冲突规则、运行方式和停止条件。

附件中的概念性建议必须转译成现有仓库可承载的实现，不得据此凭空创建后端能力。

## 3. System Invariants

以下规则不可被局部页面偏好覆盖：

1. **Scientific Truth**：观察、来源事实、推断、综合与建议必须可区分。
2. **Evidence Traceability**：重要主张必须能追溯到具体证据与来源。
3. **Human Governance**：发布、接受、弃用及工程复用权限不能由 UI 静默授予。
4. **Persistent Context**：知识版本、筛选条件、选择和审查上下文必须可恢复。
5. **Single Source of Truth**：前端不能维护与后端冲突的第二套领域真相。
6. **Repository Compatibility**：优先复用现有 Shell、类型、服务、组件和测试模式。
7. **No Local Design Language**：Page 03 不得发明与全站冲突的视觉语言。
8. **Visible Uncertainty**：未知、证据缺口、冲突、过期和不适用必须可见。
9. **No Unsupported Synthesis**：AI 生成文本不是证据，除非有来源对象和明确推断标签。
10. **Version Preservation**：知识更新必须形成新版本，不得覆盖历史科学状态。
11. **Context-Bounded Knowledge**：知识不能被默认视为跨菌株、培养条件、目标和尺度普遍成立。
12. **Governed Reuse**：可检索不等于可用于工程建议；复用必须遵守状态与权限。

## 4. 决策优先级

发生冲突时按以下顺序裁决：

1. 安全、法律、平台规则；
2. System Invariants；
3. Master Contract v1.2；
4. 现有仓库中已确认的后端领域合同和共享对象模型；
5. Page 03 Operating Principles；
6. Page 03 Product Spec；
7. Page 03 Technical Spec；
8. Page 03 Interaction / UI Spec；
9. Page 03 Acceptance Spec；
10. 本 Prompt 的实施建议；
11. Claude 的实现偏好。

若高优先级要求使低优先级验收无法成立，停止并报告冲突；不得悄悄选择一方。

## 5. Page 03 责任边界

Page 03 负责：

- 获取和登记科学来源；
- 从来源提取候选主张、机制、条件、结果与限制；
- 规范化术语、对象身份与证据类型；
- 构造并链接 Knowledge Object、Evidence、Mechanism 与 Engineering Pattern；
- 展示支持、反对、限制和不确定证据；
- 评价、验证、发布、版本化、弃用和退役知识；
- 发现知识缺口与冲突；
- 将受治理的知识发布给 Page 02 使用；
- 接收 DBTL 结果并形成新的 Evidence Candidate；
- 保留知识在不同版本和上下文中的演化轨迹。

Page 03 不负责：

- 取代 Page 02 执行完整 DBTL 工程决策；
- 自动批准基因改造或湿实验；
- 把论文影响因子直接转换为证据强度；
- 替代原始论文、实验数据或领域专家审查；
- 在前端实现新的检索、知识图谱或 AI 后端；
- 把所有关系压扁为 support / reject；
- 将缺失全文解释为不存在证据；
- 将“高置信推断”等同于“强证据”。

---

# PART II — 产品宪法

## 6. Product Identity

Page 03 是 Synthetic Biology DBTL Engineering OS 的：

> **Scientific Knowledge Production System**

它不是 Knowledge Storage，而是 Knowledge Production。

使命：

> Continuously transform fragmented scientific information and DBTL outcomes into reusable, explainable, traceable, governed, and evolvable engineering knowledge.

## 7. Primary Operating Question

页面必须持续回答：

> **What reusable scientific knowledge supports, limits, contradicts, or changes this engineering decision?**

进一步回答：

- 生物学提供了什么机制知识？
- 哪些证据支持或反对该机制？
- 证据有多直接、可靠、当前和可迁移？
- 知识在什么菌株、环境、目标和实验条件下成立？
- 是否存在未解决的冲突或证据缺口？
- 它能否被安全地用于工程建议？
- 新实验是否改变了既有知识？

## 8. Knowledge Production Philosophy

固定转换链：

```text
Scientific Information
→ Source Object
→ Extracted Claim
→ Normalized Object
→ Structured Knowledge
→ Linked Evidence
→ Evaluated Knowledge
→ Validated Knowledge
→ Reusable Engineering Knowledge
→ Runtime Use
→ Experimental Outcome
→ New Evidence Candidate
→ Knowledge Evolution
```

不得把这些阶段实现成互不相干的工具入口；它们是同一个知识对象的生命周期。

## 9. 用户与核心任务

### Synthetic Biology PI

- 快速判断知识是否足以支持工程选择；
- 看见矛盾、限制、证据缺口与适用范围；
- 审查关键知识的发布或弃用。

### Dry Lab Scientist

- 检索可计算、可引用、带版本的知识对象；
- 检查数据、模型、参数和输出溯源；
- 把模型结果作为候选证据而非既成事实。

### Wet Lab Scientist

- 理解工程模式的机制、条件和验证要求；
- 将实验结果回写为结构化证据；
- 区分建议、已批准计划和真实实验观察。

### Knowledge Curator / Reviewer

- 规范化对象；
- 合并重复身份；
- 审查来源、证据、矛盾、适用范围与版本变化；
- 接受、要求修订、拒绝、弃用或退役知识。

### First-time User

- 30 秒内理解页面不是论文库；
- 5 分钟内完成检索、打开对象、检查证据与复用入口。

## 10. 核心 JTBD

用户必须能够：

1. 从科学问题或工程上下文开始；
2. 找到相关 Knowledge Object，而非只得到文档链接；
3. 理解对象的机制、条件、证据和限制；
4. 比较多个对象或工程模式；
5. 检查支持与冲突证据；
6. 识别缺失知识和不可迁移范围；
7. 将合格知识引用到 Page 02 的 Engineering Decision；
8. 将新来源或 DBTL 结果提交为候选知识；
9. 参与审查、版本更新和弃用流程；
10. 恢复之前的研究上下文。

## 11. 产品成功标准

Page 03 成功不是“显示很多知识”，而是：

- 用户能发现可复用的工程知识；
- 用户能判断知识为什么可信、在哪里不可信；
- 所有重要知识可溯源；
- 矛盾不会被隐藏；
- 知识可按上下文比较；
- 合格对象可被 Page 02 精确引用；
- 每次 DBTL 循环可反哺知识系统；
- 历史版本和使用记录可审计。

## 12. 明确失败模式

以下任一出现即产品失败：

- 首页看起来像论文搜索引擎；
- Knowledge Graph 只有节点和线，无法解释关系与证据；
- 摘要与证据混在一起；
- 引用只有 DOI 字符串，不能检查来源上下文；
- 支持证据覆盖或隐藏冲突证据；
- 不展示菌株、培养、目标或实验条件；
- “无结果”无法区分无知识、筛选过严和后端失败；
- 未验证对象可被无提示地用于工程建议；
- 更新覆盖旧版本；
- Page 02 能修改 Page 03 的治理状态。

---

# PART III — 科学对象与运行语义

## 13. Core Object Model

优先使用仓库现有共享类型。若缺少前端展示字段，只能通过 adapter / view model 补足；不得创建与后端竞争的领域模型。

最低对象集合：

- `Source`
- `SourceFragment`
- `Observation`
- `Claim`
- `Mechanism`
- `BiologicalEntity`
- `Relationship`
- `KnowledgeObject`
- `EngineeringPattern`
- `DecisionKnowledge`
- `Evidence`
- `EvidenceSet`
- `EvidenceGap`
- `Contradiction`
- `ApplicabilityContext`
- `ValidationRecord`
- `KnowledgeVersion`
- `ReuseRecord`
- `ExperimentalOutcome`
- `CurationTask`

## 14. Minimum Knowledge Object Contract

每个重要知识对象至少支持：

```ts
type KnowledgeObjectView = {
  id: string
  version: string
  type: string
  title: string
  canonicalIdentity?: string
  summary: string
  scientificNature: 'observation' | 'claim' | 'mechanism' | 'pattern' | 'inference' | 'recommendation'
  status: KnowledgeStatus
  applicability: ApplicabilityContext
  sourceIds: string[]
  supportingEvidenceIds: string[]
  conflictingEvidenceIds: string[]
  evidenceGapIds: string[]
  evidenceQuality: EvidenceQuality
  confidence: ConfidenceAssessment
  limitations: string[]
  permittedReuseScope: string[]
  createdAt: string
  updatedAt: string
  supersedesVersion?: string
  supersededByVersion?: string
}
```

字段名必须适配真实 API，不得要求后端迁就此示例。

## 15. Knowledge Status

使用受控状态，不得自由造词。至少映射：

- Candidate
- Extracted
- Normalized
- Structured
- Under Review
- Validated
- Published for Reuse
- Needs Revision
- Contested
- Superseded
- Deprecated
- Retired
- Rejected

UI 必须区分：

- 科学状态；
- 审查状态；
- 发布状态；
- 运行时复用权限。

## 16. Evidence Model

Evidence 是一等对象，不是 citation string。

每个 Evidence 至少应表达：

- 来源与可定位片段；
- 证据类型；
- 支持、反对、限制、条件化或不确定关系；
- 实验/计算方法；
- 菌株、基因型、培养条件、干预、对照与表型；
- 直接性、质量、时效和可迁移性；
- 适用范围；
- 审查状态；
- 原始数据或计算溯源（若存在）。

Evidence Quality 与 Confidence 必须分开显示：

- Evidence Quality：证据本身的来源、设计、直接性和强度；
- Confidence：系统或审查者对当前知识解释的确信程度。

## 17. Applicability Context

知识默认受上下文约束。至少考虑：

- organism；
- strain / chassis；
- genotype；
- medium；
- carbon source；
- oxygen condition；
- temperature；
- growth phase；
- intervention；
- target product / phenotype；
- scale；
- assay / measurement method；
- computational model / version；
- engineering objective。

未知必须显示为 Unknown，不得当作 Universal。

## 18. Knowledge Relationships

关系必须有类型、方向、证据和状态。至少支持：

- supports
- contradicts
- limits
- contextualizes
- derived_from
- explains
- regulates
- catalyzes
- competes_with
- depends_on
- applies_to
- not_transferable_to
- supersedes
- reused_in
- validated_by

每条重要关系必须能打开 Inspector，查看其来源和证据。

## 19. Knowledge Production Lifecycle

### Acquire

登记来源，不自动接受为知识。区分全文可用、仅摘要、元数据可用和不可访问。

### Extract

从来源提取候选主张、机制、条件、方法、结果和限制。AI 输出必须标为 derivative candidate。

### Normalize

统一术语、单位、对象身份、菌株名、基因名和证据类型。歧义必须进入审查。

### Structure

把文本转换为明确对象与关系；区分 observation、claim、inference、explanation 和 recommendation。

### Link

链接对象、证据、来源、上下文、冲突与工程模式。链接不能没有关系语义。

### Evaluate

评价证据质量、直接性、适用性、冲突、缺口和复用风险。

### Validate

产生对象版本特异的审查结论：Accepted、Needs Revision、Rejected、Insufficient Evidence 或 Contested。

### Publish for Reuse

只发布满足治理要求的明确版本，并附 permitted reuse scope。

### Observe Outcome

记录 Page 02 引用了哪个对象版本，以及由此形成的计算、实验和审查结果。

### Update

新证据形成新版本，保留变化原因、审查者和影响范围。

### Supersede / Retire

保留历史对象、替代关系、弃用原因和下游影响，不做静默删除。

## 20. Computational Traceability

计算或 AI 衍生对象必须可追溯：

```text
Prompt / Query
→ Model and Version
→ Tool
→ Parameters
→ Input Objects and Versions
→ Output
→ Review
→ Accepted / Rejected / Needs Revision
```

模型输出不能提升为 Evidence，除非其证据类型、输入、方法、限制和审查状态被明确记录。

## 21. Runtime Reuse Contract

Page 02 引用知识时必须保存：

- `knowledge_id`
- `knowledge_version`
- `reuse_tier`
- `applicability_snapshot`
- `evidence_summary_snapshot`
- `decision_id`
- `used_at`

Page 02 可读取、比较、引用和应用；不可改写：

- 来源；
- 证据强度；
- 矛盾关系；
- 适用范围；
- 状态；
- 版本。

任何修改必须回到 Page 03 的 curation / review 流程。

---

# PART IV — 页面信息架构与 UI 合同

## 22. 页面总骨架

推荐桌面布局：

```text
Global AppShell
└── Page 03 Knowledge Workspace
    ├── Persistent Context Bar
    ├── Knowledge Command Header
    ├── Scope + Query + Active Filters
    ├── Workspace Body
    │   ├── Left: Taxonomy / Saved Views / Lifecycle Queue
    │   ├── Center: Knowledge Surface
    │   └── Right: Contextual Inspector
    ├── Comparison Tray
    └── Evidence Drawer / Provenance Drawer
```

页面中心是 Knowledge Surface，不是搜索结果列表。

## 23. Persistent Context Bar

显示：

- workspace / project；
- active organism / strain；
- engineering objective；
- selected decision context（若从 Page 02 进入）；
- knowledge scope：Global / Project / Decision；
- active snapshot / version time；
- sync / partial / stale 状态。

上下文变化必须明确，不得静默改变检索范围。

## 24. Knowledge Command Header

必须提供：

- 页面身份：Scientific Knowledge Production System；
- 当前科学问题或工程问题；
- Search / Ask / Retrieve 入口；
- Add Source / Submit Outcome（按权限）；
- Review Queue；
- Saved View；
- Context restore；
- 清楚的主操作，不超过一个 dominant CTA。

## 25. Left Navigation

左侧不是全站导航，而是 Page 03 内部导航：

- Knowledge Types
- Organisms / Strains
- Mechanisms
- Engineering Patterns
- Evidence Gaps
- Contradictions
- Under Review
- Published for Reuse
- Superseded / Deprecated
- My Saved Views

数量、筛选和活动状态必须真实反映数据。

## 26. Knowledge Surface

至少支持三种互补视图：

1. **Structured List / Card View**：高效扫描对象；
2. **Relationship View**：理解机制和证据网络；
3. **Comparison View**：比较知识、证据和适用性。

视图切换不得丢失：

- query；
- filters；
- selected object；
- comparison selection；
- scroll / focus（尽可能）；
- context scope。

## 27. Knowledge Card

每张卡片最少显示：

- 类型；
- 标题；
- 一句话机制或工程意义；
- organism / strain / key context；
- status；
- evidence quality；
- confidence；
- supporting / conflicting evidence counts；
- evidence gap 标记；
- current version；
- reuse eligibility；
- recently updated / superseded 提示。

不得把 DOI、作者或期刊名当作卡片主层级。

## 28. Relationship View

图网络必须服从理解任务：

- 节点大小与颜色有固定语义；
- 边有方向、类型和证据状态；
- 支持与冲突不能只靠颜色；
- 选择节点后 Inspector 显示完整语义；
- 可聚焦局部子图；
- 可切换 mechanism / evidence / engineering pattern 层；
- 大图必须聚合、虚拟化或渐进加载；
- 提供等价的列表/表格访问路径。

Three.js 仅在现有技术栈支持、二维方案不足且不会损害可访问性时使用。不得为了视觉冲击引入 3D。

## 29. Contextual Inspector

选择 Knowledge Object 后，Inspector 依次展示：

1. Identity
2. Scientific Nature
3. Mechanism
4. Applicability
5. Supporting Evidence
6. Conflicting / Limiting Evidence
7. Evidence Gaps
8. Confidence and Evidence Quality
9. Limitations
10. Engineering Reuse
11. Provenance
12. Version History
13. Downstream Usage
14. Review / Curation Actions

Inspector 不能只有 AI 摘要。

## 30. Evidence Drawer

Evidence Drawer 必须支持：

- 查看原始来源身份；
- 定位 source fragment；
- 查看实验/计算上下文；
- 区分 direct / indirect；
- 展示支持、反对、限制、条件化和不确定；
- 查看质量评价理由；
- 查看审查记录；
- 打开来源（有权限且链接可用时）；
- 清楚显示仅摘要或全文不可用。

## 31. Comparison

比较 2–4 个 Knowledge Object / Engineering Pattern，维度至少包括：

- mechanism；
- organism / strain；
- applicability；
- intervention；
- expected effect；
- supporting evidence；
- conflicting evidence；
- evidence quality；
- confidence；
- limitations；
- transferability；
- reuse status；
- version freshness。

比较界面必须支持“差异优先”，不能只并排堆卡片。

## 32. Knowledge Production Queue

对具备权限的用户提供：

- newly acquired；
- extraction needed；
- normalization conflict；
- evidence review；
- validation pending；
- update impact；
- supersede / retire review。

队列必须与浏览视图区分，不让普通用户误以为所有条目均已验证。

## 33. Visual Hierarchy

层级固定：

```text
Brand
→ Workspace
→ Page
→ Region
→ Panel
→ Component
→ Scientific Object
→ Evidence Detail
```

第一视觉层：问题、范围、关键知识与冲突。  
第二视觉层：机制、适用性、证据质量和复用状态。  
第三视觉层：来源片段、版本、审查和计算参数。

## 34. Visual Semantics

颜色必须复用全局 token。

必须通过颜色 + 图标/文本/形状共同表达：

- validated；
- candidate；
- under review；
- contested；
- superseded；
- supporting；
- contradicting；
- evidence gap；
- not transferable；
- unavailable / partial。

不得将“绿色”同时表示高置信、强证据、已批准和运行成功。

## 35. Visual Rhythm

页面采用：

```text
Orient → Explore → Focus → Inspect → Compare → Act → Rest
```

网络区域可以信息密集；Inspector 与阅读区域必须留白；证据详情需要稳定阅读宽度。避免全页同密度。

## 36. Responsive

### ≥1600 px

三栏同时可见，Inspector 约占 25–30%。

### 1280–1599 px

左栏可收起，中心优先，Inspector 保持可用。

### Tablet

中心主视图 + 可切换左抽屉/Inspector，避免压缩图谱到不可读。

### Mobile

以搜索、卡片、详情、证据为顺序；网络视图降级为关系列表。关键审查动作仍可完成。

---

# PART V — 交互合同

## 37. 统一任务流

每个核心任务遵循：

```text
Start
→ Understand Scope
→ Retrieve
→ Inspect
→ Compare / Evaluate
→ Decide
→ Commit or Reuse
→ Review
→ Complete
```

知识生产任务遵循：

```text
Acquire
→ Extract
→ Normalize
→ Structure
→ Link
→ Evaluate
→ Validate
→ Publish
```

## 38. Retrieve

- query 与 filters 始终可见；
- relevance 与 evidence quality 分开展示；
- 默认不隐藏 contested / superseded，但可通过明确筛选控制；
- no results 必须区分：无知识、筛选过严、无权限、索引不可用、网络失败；
- 搜索状态可链接、可恢复（若现有路由支持）。

## 39. Inspect

- 单击对象选择并打开 Inspector；
- 深链接应能恢复对象和版本；
- 返回后保留列表/图谱上下文；
- 从关系边进入时展示该关系，而非只展示节点；
- 键盘用户可以完成选择、展开和证据访问。

## 40. Compare

- 明确显示已选数量；
- 不允许比较不兼容对象而不提示；
- 差异项优先；
- 可从比较结果选择“引用到决策”或“创建证据缺口”；
- 比较不会修改原始知识。

## 41. Reuse in Engineering Decision

复用是 consequential action：

1. 选择具体对象版本；
2. 展示状态、证据、适用范围和限制；
3. 校验目标 Decision 的 organism / strain / context；
4. 标记 context mismatch；
5. 由用户确认；
6. 记录 reuse record；
7. 跳转或返回 Page 02；
8. 不改变 Knowledge Object。

Candidate、Contested、Superseded 或超出适用范围的对象必须增加警告或禁止，具体服从后端权限。

## 42. Submit Source / Outcome

- 提交不等于发布；
- 新来源进入 acquisition / review；
- 新实验结果进入 Evidence Candidate；
- 必须保存关联 Decision、Knowledge version、方法、条件和结果；
- 失败实验和阴性结果不得被默认丢弃；
- 上传或长任务显示真实进度、取消和重试能力（若后端支持）。

## 43. Review and Publish

- 审查动作必须显示对象版本；
- 必须填写理由或选择规范原因；
- Publish、Reject、Supersede、Retire 需要确认；
- 乐观更新失败必须回滚；
- 权限不足时禁用并解释；
- 冲突更新必须提示刷新、比较或合并，不得覆盖。

## 44. AI Participation

AI 可以：

- 帮助检索；
- 候选提取；
- 术语规范化建议；
- 关系建议；
- 证据摘要；
- 冲突发现；
- 缺口提示；
- 草拟解释。

AI 不可以：

- 伪造来源；
- 自动把候选知识标为 Validated；
- 隐藏矛盾；
- 用模型置信度替代证据；
- 自动批准工程复用；
- 自动批准湿实验。

所有 AI 结果必须显示生成状态、输入范围、来源覆盖和审查状态。

## 45. Loading / Empty / Error / Partial

### Loading

- 使用稳定骨架，避免布局跳动；
- 长任务显示阶段与可取消性；
- 不用虚假百分比。

### Empty

分别设计：

- 尚无知识；
- 当前筛选无匹配；
- 尚无支持证据；
- 尚无冲突证据；
- 明确 Evidence Gap；
- 尚无版本历史；
- 尚未在决策中复用。

### Error

错误必须说明影响范围、保留用户上下文并提供恢复动作。

### Partial

若来源、证据、图谱或审查服务部分失败：

- 显示已成功的数据；
- 标明缺失区域；
- 不把 partial 当 complete；
- 不允许基于缺失信息静默发布。

## 46. Accessibility

- 所有功能可键盘完成；
- 焦点顺序符合视觉顺序；
- Drawer / Dialog 正确管理焦点；
- 图谱提供文本等价物；
- 状态不只依赖颜色；
- tooltip 不是唯一信息通道；
- 支持 reduced motion；
- 动态更新使用适当 live region；
- 触控目标、对比度和语义标签满足全局标准。

---

# PART VI — 技术实现合同

## 47. Repository Audit

编码前输出审计结果：

- framework 和版本；
- 路由；
- AppShell 和导航；
- Page 1 / Page 2 的 feature 边界；
- design tokens；
- shared components；
- domain types；
- API clients；
- query/cache/state 方案；
- graph / visualization 依赖；
- auth / permissions；
- persistence；
- test stack；
- mock / fixture 机制；
- 当前可用的 Knowledge / Evidence API。

不得在审计前决定目录和组件。

## 48. Protected Repository Surface

默认冻结：

- AppShell；
- global design tokens；
- global navigation；
- shared domain object model；
- global types；
- API naming；
- authentication / authorization；
- approval semantics；
- backend scientific logic；
- Page 1 / Page 2 现有工作流；
- unrelated shared components。

若必须修改，进入 Conditional Audit Gate。

## 49. Architecture Rules

- 页面逻辑置于独立 feature boundary；
- 领域 DTO 与 UI view model 分离；
- 通过 adapter 兼容真实 API；
- server state 由现有 query/cache 层管理；
- URL state 仅保存适合深链接的 query、filters、view、selection；
- ephemeral UI state 保持本地；
- draft / review state 按后端能力持久化；
- 不复制全局对象定义；
- 不把业务逻辑埋在视觉组件中；
- 不将 fixture 混入 production path。

## 50. 推荐 Feature Boundary

实际命名服从仓库：

```text
features/knowledge/
├── routes/
├── components/
├── views/
├── inspectors/
├── evidence/
├── comparison/
├── curation/
├── api/
├── adapters/
├── hooks/
├── state/
├── types/
├── fixtures/
└── tests/
```

不要为符合此树而重构已存在的兼容结构。

## 51. Component Mapping

优先复用后再新增：

- KnowledgeWorkspace
- KnowledgeContextBar
- KnowledgeCommandHeader
- KnowledgeNavigation
- KnowledgeQueryBar
- ActiveFilterBar
- KnowledgeSurface
- KnowledgeList
- KnowledgeCard
- KnowledgeNetwork
- RelationshipList
- KnowledgeInspector
- EvidenceSummary
- EvidenceDrawer
- ApplicabilityPanel
- ContradictionPanel
- EvidenceGapPanel
- VersionHistory
- ReusePanel
- ComparisonTray
- KnowledgeComparison
- CurationQueue
- ReviewActionBar
- StatusBadge
- EvidenceQualityIndicator
- ConfidenceIndicator
- PartialDataBanner

组件名称可适配现有命名；责任不可丢失。

## 52. State Ownership

| State | Owner |
|---|---|
| Knowledge objects / evidence / versions | Server |
| Review / publish / retire status | Server |
| Permissions | Server / global auth |
| Query result cache | Existing server-state layer |
| Query / filters / view / selected id | URL when appropriate |
| Inspector open state | Local or URL |
| Compare selection | Local/session; persist only if specified |
| Unsaved curation draft | Existing draft mechanism |
| Graph camera / hover | Local |
| Toast / transient feedback | Global or local UI system |

不得把服务器真相永久保存在组件 local state。

## 53. API Integration

先发现真实端点和 schema，再实现 adapter。

禁止虚构 API。若后端缺失：

1. 明确列出缺口；
2. 使用 typed deterministic fixture 或 existing mock layer；
3. UI 标注 Demo / Fixture；
4. production path 不返回假成功；
5. mutation 能力缺失时只读降级；
6. 验收报告声明未满足的集成项。

建议能力映射（不是端点命名要求）：

- search / retrieve knowledge；
- get object + version；
- get evidence / provenance；
- get relationships；
- get comparison data；
- submit source；
- submit experimental outcome；
- create / update curation draft；
- review / validate；
- publish / supersede / retire；
- create reuse record；
- get downstream usages；
- long job status / stream。

## 54. Concurrency and Mutations

- mutation 使用 idempotency / request id（若现有栈支持）；
- 禁止双击重复提交；
- 显示 pending；
- 失败回滚；
- 版本冲突不能 last-write-wins 静默覆盖；
- publish / retire 后刷新受影响缓存；
- 离线时不伪造成功；
- 用户输入尽可能保留。

## 55. Rendering and Performance

目标：

- 首屏不依赖完整图谱加载；
- 大列表使用分页或虚拟化；
- 图谱渐进加载和聚合；
- Inspector 按需取证据详情；
- 不重复获取相同对象；
- 搜索防抖但不阻塞键盘提交；
- 视图切换不重新请求不必要数据；
- 图形渲染失败可降级列表；
- 5000 Knowledge Objects / 50000 Evidence 的验收数据不导致页面冻结；
- 遵循项目现有性能预算；若无预算，记录实测而非捏造通过。

## 56. Security and Content Safety

- 富文本和来源片段必须安全渲染；
- 外链使用安全属性；
- 不暴露密钥、内部 prompt 或未授权全文；
- 按权限显示来源和审查动作；
- 不在日志中输出敏感实验或用户数据；
- 文件上传遵循现有类型、大小和扫描约束。

## 57. Testing Strategy

至少覆盖：

- unit：adapter、状态映射、证据质量与置信度分离、上下文匹配；
- component：card、Inspector、Evidence Drawer、comparison、empty/error；
- integration：retrieve → inspect → compare → reuse；
- integration：submit outcome → candidate；
- integration：review → publish / reject；
- contract：真实 API schema 或 mock contract；
- accessibility：keyboard、focus、labels、graph alternative；
- performance：large dataset；
- regression：Page 1 / Page 2、AppShell、navigation、tokens；
- visual：关键 viewport 和状态。

---

# PART VII — 实施范围锁

## 58. Allowed Scope

允许：

- 新增或修改 Page 03 feature；
- 增加必要 adapter、view model、tests、fixtures；
- 复用并小幅扩展共享组件（仅兼容且无回归时）；
- 增加 Page 03 route；
- 修复直接阻断 Page 03 的局部缺陷。

## 59. Forbidden Autonomous Behaviors

禁止：

- 重构无关模块；
- 重命名现有 API；
- 修改后端业务逻辑；
- 替换全局状态管理；
- 替换 Design System；
- 创建第二套对象模型；
- 改变 Page 1 / Page 2 职责；
- 引入大型依赖而无审计和记录；
- 发明数据、论文、证据或成功响应；
- 删除历史版本；
- 将 TODO、console error 或 failing tests 留作“未来工作”后仍宣称完成。

## 60. Conditional Audit Gate

以下情况必须暂停并请求人类决策：

- 规范与真实后端科学语义冲突；
- 实现必须修改 Protected Surface；
- 需要破坏性 schema / API 变更；
- 缺少关键权限或审批模型；
- 无法区分 Evidence 与 AI inference；
- 无法保存知识版本；
- Page 03 与 Page 02 对同一对象拥有冲突写权限；
- 关键验收只能靠伪造后端能力通过；
- 存在安全、合规或不可逆数据风险；
- 需要新依赖且影响全局 bundle / license / security。

暂停时输出：问题、证据、影响、可选方案、推荐方案和需要用户决定的单一问题。

---

# PART VIII — 固定实施顺序

## 61. Step 1 — Repository Audit

完成第 47 节审计，不写业务代码。

## 62. Step 2 — Specification Matrix

创建内部矩阵：

| Requirement | Source | Existing Support | Gap | Implementation | Test |
|---|---|---|---|---|---|

覆盖 Product、UI、Interaction、Technical、Acceptance。

## 63. Step 3 — Conflict and Gap Analysis

识别：

- 页面职责冲突；
- schema 缺口；
- API 缺口；
- 权限缺口；
- 设计系统差异；
- fixture 与 production 边界；
- 需要暂停的问题。

## 64. Step 4 — Component Inventory

对每个组件标记：

- Reuse as-is
- Extend safely
- Create locally
- Do not implement

## 65. Step 5 — Decision Records

重大选择记录 DSR / ADR：

```yaml
id:
type: DSR | ADR
context:
decision:
alternatives:
reason:
tradeoff:
impact:
requirements_covered:
```

## 66. Step 6 — Implement Foundation

顺序：

1. route and feature boundary；
2. shared-type adapters；
3. query / filters / selection state；
4. API integration and fixtures；
5. permission and error semantics；
6. base layout；
7. tests for foundation。

## 67. Step 7 — Implement Core Experience

顺序：

1. retrieve；
2. cards / list；
3. inspect；
4. evidence；
5. relationships；
6. compare；
7. reuse；
8. curation / review；
9. version history；
10. outcome feedback；
11. responsive / accessibility；
12. advanced visualization only if justified。

## 68. Step 8 — Verify

运行：

- formatter；
- lint；
- typecheck；
- unit tests；
- integration tests；
- production build；
- existing regression suite。

不得忽略失败。

## 69. Step 9 — Visual and Interaction QA

逐一检查：

- desktop / tablet / mobile；
- loading / empty / error / partial；
- candidate / validated / contested / superseded；
- supporting + conflicting evidence；
- keyboard / focus；
- long content；
- large data；
- no graph support fallback。

## 70. Step 10 — Acceptance and Regression

逐条完成 PART IX、X、XI。

## 71. Step 11 — Delivery and STOP

输出标准完成报告。满足 Stop Condition 后立即停止。

---

# PART IX — 发布验收

## 72. Definition of Done

只有同时满足以下条件才算完成：

- 页面行为是知识生产系统而非文献库；
- 核心对象与生命周期真实可见；
- 支持、冲突、限制和证据缺口可见；
- 来源、版本、上下文和复用记录可追溯；
- Page 02 复用边界正确；
- loading / empty / error / partial 完整；
- 响应式和无障碍通过；
- API 缺口没有被伪装；
- tests、typecheck、lint、build 通过；
- 无关键回归；
- 无未解释 TODO；
- 完成报告完整。

## 73. Product Gate

- 用户 30 秒内理解 Page 03 的角色；
- 5 分钟内能检索、检查证据和定位复用；
- 页面围绕 Knowledge Object 组织；
- 新实验可回流为候选知识；
- 不是功能入口集合。

## 74. Scientific Gate

每个关键对象必须能回答：

- Mechanism
- Evidence
- Trade-off
- Limitation
- Applicability
- Validation
- Provenance
- Version

观察、推断和建议可区分。

## 75. Evidence Gate

- 每个重要 claim 可打开证据；
- supporting 与 conflicting 同时可见；
- quality 与 confidence 分离；
- 全文不可用不等于无证据；
- evidence gap 是科学状态；
- 影响因子不直接决定证据强度；
- AI prose 不被当作证据。

## 76. Knowledge Gate

- 对象身份稳定；
- 关系有类型和证据；
- 状态受控；
- 更新产生版本；
- superseded / retired 保留历史；
- 上下文边界明确；
- 可复用范围明确。

## 77. Engineering Reuse Gate

- 复用具体版本；
- context mismatch 可见；
- 未验证对象受限制；
- reuse record 可追溯；
- Page 02 不改写 Page 03；
- 结果能回流 Page 03。

## 78. Governance Gate

- 审查与发布按权限；
- consequential action 要求确认；
- 变更有理由和审计；
- 冲突更新不覆盖；
- 退役和拒绝可解释；
- 人工决定与 AI 建议明确区分。

## 79. UI and Interaction Gate

- 信息层级清晰；
- graph 可理解且可降级；
- Inspector 和 Drawer 可访问；
- query / filter / selection 保持；
- 状态不只依赖颜色；
- 没有全页同密度；
- 移动端仍可完成核心任务。

## 80. Technical Gate

- 遵守现有架构；
- 没有重复领域模型；
- server / URL / local state 归属正确；
- adapter 隔离 schema；
- fixture 与 production 分离；
- mutation 有失败与冲突处理；
- 大数据不冻结；
- 无 secrets / unsafe HTML。

## 81. Static and Runtime Gate

必须记录真实命令和结果：

- lint；
- typecheck；
- unit；
- integration；
- build；
- accessibility；
- regression；
- runtime smoke test。

若仓库没有某项能力，标记 `NOT AVAILABLE` 并说明，不得写 PASS。

## 82. Critical Failures

以下任一出现即 `REJECTED`：

- 伪造来源或证据；
- AI 摘要冒充 evidence；
- 支持证据隐藏冲突；
- 未经治理发布知识；
- 覆盖历史版本；
- Page 02 改写知识真相；
- 用假 API 宣称生产集成完成；
- 关键操作无权限控制；
- build / typecheck / core tests 失败；
- 核心任务不可键盘完成；
- 破坏 Page 1 / Page 2 或全局 Shell。

## 83. Release Decision

仅允许：

- `READY`
- `NEEDS REVISION`
- `REJECTED`

不得使用“基本完成”代替判定。

---

# PART X — 必测场景

## 84. Scenario A — Validated reusable knowledge

检索、检查完整证据、确认适用范围并引用到 Page 02。

## 85. Scenario B — Weak evidence

对象高置信但证据有限；UI 必须分别表达。

## 86. Scenario C — Conflicting evidence

支持与反对证据同时存在，用户可比较差异条件。

## 87. Scenario D — Evidence gap

无菌株特异证据；系统显示科学缺口而非普通空状态。

## 88. Scenario E — Context mismatch

知识来自 MG1655，目标为 BW25113；复用前必须提示迁移风险。

## 89. Scenario F — Full text unavailable

仅有摘要/元数据；不得显示为完整提取或无证据。

## 90. Scenario G — AI extraction candidate

AI 提取主张进入 Candidate，不能自动 Published。

## 91. Scenario H — New experimental outcome

从完成的 DBTL cycle 提交阳性、阴性或失败结果，形成 Evidence Candidate。

## 92. Scenario I — Superseded knowledge

旧版本仍可审计，下游使用可见，新版本关系明确。

## 93. Scenario J — Concurrent review conflict

两个审查者更新同一版本，系统不静默覆盖。

## 94. Scenario K — Partial backend failure

图谱服务失败但对象和证据可读；清楚标记 partial。

## 95. Scenario L — No results

分别验证无知识、筛选过严、无权限和服务失败。

## 96. Scenario M — Large repository

5000 Knowledge / 50000 Evidence 下搜索、滚动、选择和 Inspector 可用。

## 97. Scenario N — Accessibility

仅键盘完成 retrieve → inspect → evidence → compare。

## 98. Scenario O — Mobile fallback

移动端通过关系列表理解网络，并完成证据检查。

## 99. Scenario P — Runtime reuse immutability

Page 02 引用后尝试修改 evidence quality；系统必须拒绝或引导回 Page 03 审查。

---

# PART XI — Regression Matrix

## 100. 必须证明 No Drift

| Domain | Required proof |
|---|---|
| UI | No global token, Shell or visual-language drift |
| Interaction | No navigation, focus or shared-pattern regression |
| Scientific | No object, evidence, confidence or version semantic drift |
| Backend | No API rename, fake success or contract break |
| Performance | No material regression to Page 1 / Page 2 |
| Accessibility | No loss of keyboard, semantics or contrast |
| Governance | No weakened permission, review or approval boundary |

---

# PART XII — 完成报告

## 101. 标准输出格式

最终只输出事实：

```md
# Page 03 Implementation Report

## 1. Release Decision
READY | NEEDS REVISION | REJECTED

## 2. Implemented
- ...

## 3. Reused Existing Architecture
- ...

## 4. API and Data Integration
- Real endpoints:
- Adapters:
- Fixtures:
- Missing backend capabilities:

## 5. Scientific Semantics
- Knowledge objects:
- Evidence:
- Applicability:
- Versioning:
- Reuse:

## 6. Tests
| Check | Command | Result |
|---|---|---|

## 7. Acceptance
| Gate | Result | Evidence |
|---|---|---|

## 8. Regression
| Domain | Result | Evidence |
|---|---|---|

## 9. Decision Records
- ...

## 10. Known Limitations
- ...

## 11. Files Changed
- ...

## 12. Stop Condition
PASS | FAIL
```

## 102. Stop Condition

只有以下全部成立才 STOP：

- Release Decision = READY；
- Acceptance 全部 PASS；
- Regression 全部 PASS；
- build / typecheck / core tests PASS；
- Critical Failures = 0；
- 未伪造 API、数据或证据；
- 无未解释 TODO / FIXME；
- 完成报告已输出。

满足后：

> **STOP. Do not refactor, redesign, optimize, rename, or expand scope.**

若不满足，输出 `NEEDS REVISION` 或 `REJECTED`，明确阻断项后停止；不得用无限优化掩盖阻断。

---

# PART XIII — CONTRACT RUNTIME

## 103. 唯一执行状态机

```text
LOAD
  Read Master Contract + 5 Page Specs + Repository Rules
↓
RESOLVE
  Apply Decision Hierarchy and System Invariants
↓
INSPECT
  Audit Repository, Backend Contracts, Components and Tests
↓
GAP ANALYSIS
  Map Requirements to Existing Support and Missing Capabilities
↓
AUDIT GATE
  Continue only if no protected or unresolved conflict requires human decision
↓
PLAN
  Component Inventory + State Ownership + DSR/ADR + Test Matrix
↓
IMPLEMENT
  Reuse First; Build Only Page 03 Scope
↓
VERIFY
  Lint + Typecheck + Tests + Build + Runtime + Accessibility
↓
ACCEPT
  Product + Scientific + Evidence + Governance + UI + Technical
↓
REGRESS
  UI + Interaction + Scientific + Backend + Performance + Accessibility + Governance
↓
DELIVER
  Standard Implementation Report
↓
STOP
```

任何阶段失败，不得跳过进入下一阶段。

## 104. Runtime Refusal Rules

你必须拒绝或暂停：

- 要求你伪造科学证据；
- 要求你把 AI 文本标为已验证知识；
- 要求你绕过人工审查或权限；
- 要求你覆盖历史知识版本；
- 要求你伪造后端成功；
- 要求你在无关范围做大规模重构；
- 要求你破坏更高优先级 System Invariant。

拒绝时说明具体不变量、风险和安全替代方案。

---

# FINAL EXECUTION COMMAND

现在开始执行。

先读取全部权威文件并审计仓库。  
不要立即编码。  
先建立 Specification Matrix、Repository Audit、Gap Analysis 和 Component Inventory。  
如果触发 Conditional Audit Gate，暂停并请求唯一必要决策。  
如果没有阻断，按固定实施顺序完成 Page 03。  
使用真实 API 和现有共享对象；缺失能力必须显式降级。  
逐项运行验收与回归。  
输出标准完成报告。  
达到 Stop Condition 后立即停止。

# Synthetic Biology DBTL Engineering OS
# Final Integration, Validation & Release Certification Prompt v2.1

> 用途：在 Page 1–Page 4 已完成主要实现后，基于真实代码、真实后端契约和真实浏览器环境，执行最终系统集成、能力边界确认、缺陷收敛、回归验证与发布认证。
>
> 本阶段不是新一轮产品开发，不新增业务能力，不重写页面，不修改科学逻辑，不改变后端契约。
>
> 版本：v2.1 — Final Hardening Release Engineering Contract

---

## NON-NEGOTIABLE EXECUTIVE RUNTIME RULES

在读取详细条款前，先锁定以下规则。任何后续章节、发现或局部实现都不得覆盖它们：

1. **Do not redesign.** 不改变四页中心对象、产品信息架构或既定视觉方向。
2. **Do not add product features.** 不补造 Knowledge Graph、RBAC、Memory、Approval、Export 或其他后端未提供的能力。
3. **Audit before editing.** 在完成仓库、运行时、Git、浏览器与能力缺口审计前，不修改代码。
4. **Classify before fixing.** 只有经证据确认的 `frontend_bug` 和 `validation_missing` 可在本阶段直接处理。
5. **Preserve scientific truth.** 不隐藏 uncertainty、conflict、failure、limitation、unknown 或 restricted capability。
6. **Preserve human governance.** Proposal、Approval、Execution、Observation、Evaluation 不得合并或互相冒充。
7. **Prove in a real browser.** 没有真实浏览器、console、network、interaction 和 regression 证据，不得宣称通过。
8. **Stop at an architecture decision.** 触及后端契约、领域模型、权限、审批语义或全局架构时，停止并报告。
9. **Explain every changed file.** 不做无关格式化、批量改名、顺手重构或未说明的文件修改。
10. **Stop after certification.** 输出最终证据和 Release Decision 后立即停止。

若执行过程中遗忘细节，回到本节与 Release Gates；不得凭“页面更完整”推断可以扩展范围。

---

## 0. 给 Claude Code 的总指令

你现在接手的是 **Synthetic Biology DBTL Engineering OS 的最终质量验证阶段**。

系统定位：

> Persistent, Traceable, Human-Governed DBTL Engineering System

四个页面已经完成主要实现，但当前状态不同：

| Page | Name | Current state | Certification intent |
|---|---|---|---|
| Page 1 | Project Command Center | `READY`，约 95% | 冻结功能；补浏览器、移动端 Shell 与跨页验证 |
| Page 2 | DBTL Engineering Workspace | `READY`，约 95% | 冻结功能；补真实流程、状态与高密度验证 |
| Page 3 | Scientific Knowledge Production System | `NEEDS REVISION`，约 85–90% | 区分前端缺陷与后端能力缺口；争取 `READY WITH ACCEPTED LIMITATIONS` |
| Page 4 | Trust & Provenance Center | `NEEDS REVISION`，约 85–90% | 验证治理语义；诚实声明 RBAC、Approval、Memory、Golden Set 与 Export 边界 |

上述百分比和状态只是本轮启动基线，不是最终结论。必须以仓库、运行结果和浏览器证据重新核验，不得照抄为发布判定。

你的任务不是继续设计页面，而是遵循：

```text
Audit → Validate → Classify → Minimal Fix → Regression → Release Decision
```

使用真实浏览器验证：

- 用户实际看到的页面是否正确；
- 用户是否能使用键盘完成核心任务；
- 页面在目标视口下是否稳定；
- 四页是否像同一个产品；
- 长文本、高密度数据、空状态、错误状态和权限状态是否真实可用；
- 修复后是否没有引入产品、科学、后端、交互或治理回归。

必须遵循以下执行链：

```text
LOAD
  ↓
FREEZE SCOPE
  ↓
INSPECT REPOSITORY
  ↓
DISCOVER ROUTES & RUNTIME
  ↓
ESTABLISH BASELINE
  ↓
RUN BROWSER AUDIT
  ↓
CLASSIFY FINDINGS
  ↓
APPLY MINIMAL FIXES
  ↓
RETEST
  ↓
RUN REGRESSION
  ↓
ISSUE RELEASE DECISION
  ↓
DELIVER
  ↓
STOP
```

不得跳过基线、复测、回归或发布判定。

### 0.1 本阶段的成功定义

成功不等于“所有设想能力都出现了”，而是：

- 已实现能力可靠、可用、可追溯；
- 未实现的后端能力没有被前端伪造；
- 能力不可用、受限、部分完成或失败时，用户能准确理解原因与影响；
- 四页组成连贯的 DBTL Engineering OS；
- 科学、证据、治理、执行和评价状态不会互相混淆；
- 最终 Release Decision 有可复现证据支持。

Page 3 或 Page 4 存在已确认的后端限制，不自动等于前端发布失败。若核心任务可完成、限制表达准确、没有误导性控件且相关 Gate 通过，可判定为 `READY WITH ACCEPTED LIMITATIONS`。

---

## 1. 必读上级规范

开始前必须完整读取并遵守仓库中实际存在的以下文件：

- `Synthetic_Biology_DBTL_Engineering_OS_Page_Design_Contract_v1.2.md`
- `Page1_Project_Command_Center_Claude_Code_Implementation_Prompt.md`
- `Page2_DBTL_Engineering_Workspace_Claude_Code_Implementation_Prompt.md`
- `Page3_Scientific_Knowledge_Production_System_Claude_Code_Implementation_Prompt.md`
- `Page4_Trust_and_Provenance_Center_Claude_Code_Implementation_Prompt.md`
- 项目现有 `README`、`AGENTS.md`、测试配置、前端构建配置和设计 Token 文件

若文件名、位置或版本不同：

1. 先搜索仓库；
2. 使用真实存在的最新版本；
3. 在最终报告记录采用了什么；
4. 不得自行伪造规范内容。

若引用文件不在仓库内：

1. 仅在当前 workspace 已提供的范围内定位；
2. 不得搜索用户设备、外部账户或未授权目录；
3. 将文件标记为 `UNAVAILABLE`，记录它原本约束的内容；
4. 使用其余可用 Contract 继续完成不依赖该文件的验证；
5. 只有当缺失文件会导致科学、治理、验收或页面职责无法可靠判断时，才将相关 Gate 标记为 `BLOCKED` 并暂停请求人工决策；
6. 不得因为次要参考文件缺失而无限等待或终止全部审计。

### 1.1 决策优先级

发生冲突时按以下顺序裁决：

1. 用户本次明确要求；
2. 系统不变量与安全/治理规则；
3. Page Design Contract v1.2；
4. 对应页面 Prompt；
5. 仓库中已确认的后端/API 契约；
6. 已复用的全局 Design System；
7. 本 Prompt；
8. 局部实现偏好。

如果冲突会改变科学含义、审批权限、后端契约或核心产品流程，停止并报告，不得自行裁决。

---

## 2. System Invariants

以下不变量在本阶段永远不可突破：

### INV-001 — Scientific Truth

不得为了视觉简洁而删改、合并或美化科学事实、置信度、限制条件、冲突证据、失败结果或未知状态。

### INV-002 — Evidence Traceability

证据、来源、版本、计算过程与下游引用必须保持可追溯。

### INV-003 — Human Governance

Proposal、Approval、Execution、Observation 和 Evaluation 必须继续严格分离。任何 UI 修复不得绕过人工治理。

### INV-004 — Persistent Context

当前项目、周期、阶段、选中对象、精确版本及返回上下文不得因视觉修复而丢失。

### INV-005 — Single Source of Truth

不得在前端新增第二套业务真相，不得用静态假状态覆盖真实后端状态。

### INV-006 — Repository Compatibility

不得破坏现有路由、API、类型、状态管理、构建系统和已通过的测试。

### INV-007 — No Local Design Language

不得为单个页面创造新的颜色体系、间距体系、阴影、圆角、字体或组件风格。

### INV-008 — Honest Degradation

加载中、部分数据、无权限、离线、历史版本、失败和未知必须如实表达。

### INV-009 — Exact-Version Governance

Page 4 的治理、审计、溯源和评价必须继续绑定精确对象版本。

---

## 3. Implementation Scope Lock

### 3.0 Audit-first Rule

在完成仓库审计、后端能力核验、浏览器 baseline 和 Finding Classification 前，不得修改实现。不得看到一个缺口就立即编码。

### 3.1 本阶段允许

- 增加或完善 Playwright 浏览器测试；
- 增加或完善 `axe-core` / `@axe-core/playwright` 无障碍检查；
- 增加稳定、确定性的测试夹具或 mock adapter，仅用于测试；
- 修复已复现的布局溢出、遮挡、截断、层级、焦点、键盘、ARIA、对比度和响应式问题；
- 将重复的局部视觉值收敛到现有全局 Token；
- 修复跨页组件在相同语义下表现不一致的问题；
- 为长列表接入仓库已有的分页或虚拟化能力；
- 为自动化测试增加稳定定位器，如语义化 role、label 或必要的 `data-testid`；
- 更新与本阶段直接相关的测试及质量文档。

### 3.2 本阶段禁止

- 新增产品功能或新页面；
- 重写四页信息架构；
- 改变页面中心对象；
- 重命名路由、领域对象、API、全局类型或架构层；
- 修改后端科学逻辑、审批逻辑、审计逻辑或权限模型；
- 为通过测试而隐藏真实错误；
- 将真实 API 替换成永久 mock；
- 大规模重构无关代码；
- 引入新的 UI 框架或第二套 Design System；
- 仅因为个人审美而重新设计页面；
- 将桌面科研工作台强行缩成不可用的移动端完整等价版；
- 无证据地修改性能、缓存、分页或数据加载策略；
- 删除已有测试、降低断言或放宽发布门来获得通过。

### 3.3 默认受保护区域

除非存在明确、可复现、与本阶段直接相关的缺陷，否则不得修改：

- App Shell；
- 全局导航结构；
- 后端 routers、models、schemas 和 adapters；
- 全局领域对象；
- 审批、审计、Memory、Provenance、Evaluation 语义；
- API 名称和响应字段；
- 已冻结的科学工作流；
- Page 1–Page 4 的职责边界。

### 3.4 No Cosmetic Drift

如果某项修改不能改善科学理解、核心任务完成、无障碍、跨页一致性、治理清晰度、响应式可用性或已复现的性能/稳定性问题，不得实施。

“看起来可以更漂亮”“更现代”“更像某个参考网站”不构成修改依据。

### 3.5 Backend Boundary Rule

不得通过以下方式掩盖后端能力缺口：

- 在前端生成并持久化假的领域对象；
- 将多个真实对象拼接后冒充不存在的聚合实体；
- 用静态成功状态替代真实 API 状态；
- 创建不可完成操作的按钮、表单或审批入口；
- 用 fixture、localStorage 或客户端推断冒充生产后端能力。

测试 fixture 只能存在于测试路径，并必须明确标记。

---

## 3A. Capability Gap Classification

所有发现必须先归入以下一种主类型，再决定动作：

| Type | Definition | Required action |
|---|---|---|
| `frontend_bug` | 后端能力存在，但前端展示、交互、状态或可访问性错误 | 在 Scope Lock 内最小修复并回归 |
| `backend_limitation` | 所需对象、字段、权限或 endpoint 在真实后端不存在或不足 | 不补后端；诚实降级、记录影响与建议 |
| `product_scope_gap` | 需求需要新的产品定义、交互合同或领域能力 | 不实现；进入 future roadmap |
| `architecture_constraint` | 修复要求改变 API、领域模型、科学语义、权限或关键架构 | 停止并请求人工决策 |
| `validation_missing` | 能力可能正确，但缺少足够自动化或浏览器证据 | 补验证，不借机扩展功能 |

分类必须附证据：

```yaml
capability_gap:
  id:
  page:
  capability:
  type:
  repository_evidence:
  backend_evidence:
  browser_evidence:
  user_impact:
  allowed_action:
  release_impact:
```

若同一问题涉及多个类型，以最能决定本轮动作且风险最高的类型为主，并记录次级类型。不得把 `backend_limitation` 改写成 `frontend_bug` 以获得修改权限。

---

## 4. 第一阶段：仓库与运行时审计

不要猜测命令、端口、路由和测试框架。

### 4.1 必须确认

- 包管理器及 lockfile；
- 前端框架、构建工具和启动命令；
- 后端启动命令及健康检查；
- Page 1–Page 4 的真实路由；
- 登录、权限或种子数据要求；
- 现有 Playwright/Cypress/Vitest/Jest 配置；
- 现有截图、Storybook、视觉回归或 Lighthouse 配置；
- 全局 Token 与共享组件位置；
- 当前工作树状态；
- 当前已通过/失败的 lint、typecheck、build 和 tests；
- 浏览器可执行文件是否可用。

### 4.2 审计产物

先创建一个简短的 Validation Plan，至少列出：

| 字段 | 内容 |
|---|---|
| Page | 页面名称 |
| Route | 真实路由 |
| Primary object | 页面第一对象 |
| Core keyboard flow | 核心键盘流程 |
| Required states | 必测状态 |
| Data source | 真实后端或确定性测试夹具 |
| Risk | 本页最高视觉/无障碍风险 |

如果无法启动真实前后端，先诊断并报告具体阻断。不得用静态 HTML 截图冒充浏览器验证。

### 4.2A Phase Gate Contract

本任务分为三个强制阶段。不得把“输出计划”当作已经获得修改授权。

#### Phase 0 — Baseline and audit only

只允许读取、运行、截图、记录和诊断。输出：

- Validation Plan；
- Current Page Status Matrix；
- Repository / Runtime / Tool Baseline；
- 初始 Git Safety Snapshot。

本阶段禁止修改源代码、测试、依赖、配置和产品文案。

#### Phase 1 — Classification only

对每个可复现发现输出：

- finding ID；
- evidence；
- capability-gap type；
- severity；
- allowed action；
- expected release impact；
- 是否触发 Architecture / Approval Gate。

若出现以下任一情况，输出 Phase 0–1 结果后暂停，等待人工决策：

- `architecture_constraint`；
- 后端契约、领域模型、科学逻辑、RBAC 或审批权限需要改变；
- 预计修改超过 30 个源代码/测试文件；
- 无法区分用户既有修改与本轮目标修改；
- 多份规范或 approved visual reference 互相冲突；
- Page 4 尚未完成主要实现，系统级认证不具备启动条件。

若不存在上述阻断，可自动进入 Phase 2；必须在日志中明确写出 `PHASE 2 AUTHORIZED BY CONTRACT: YES` 及理由。

#### Phase 2 — Minimal fix and certification

仅实施已分类且获准的最小修复，随后执行：

```text
Targeted retest
→ Cross-page regression
→ First-time PI test
→ Five-minute demo test
→ Failure recovery validation
→ Release certification
→ STOP
```

Phase 2 中发现的新问题必须回到 Phase 1 分类，不得边发现边扩大修改范围。

### 4.3 Baseline Freeze

任何修改前，必须冻结并记录以下 baseline：

```text
Repository
├── commit hash / branch
├── dirty worktree files
└── dependency lockfile state

Quality
├── lint
├── typecheck
├── unit/integration tests
└── production build

Browser
├── route screenshots
├── console errors/warnings
├── failed/aborted network requests
└── critical interaction traces
```

要求：

- 不得覆盖或清理用户已有的未提交修改；
- baseline 失败必须记录为“pre-existing”或“本轮引入”，不得混淆；
- 修复后的结果必须与同一路由、同一视口、同一状态、同一数据夹具的 baseline 比较；
- 截图比较只用于发现变化，不得单独证明科学或交互正确；
- 若无法取得某一 baseline，写明原因、替代证据和发布影响。

### 4.3A Git Safety Contract

在任何修改前，必须记录并保存：

```bash
git status --short
git branch --show-current
git rev-parse HEAD
git diff --stat
git diff --name-only
```

如果当前目录不是 Git 仓库，明确记录 `NOT A GIT REPOSITORY`，继续采用文件清单与校验和保护现有内容，不得初始化新仓库。

修改期间：

- 不得执行 `git reset --hard`、`git clean`、覆盖式 checkout、强制切分支或其他会丢失工作树内容的命令；
- 不得 stash、提交、推送、rebase、merge 或创建 PR，除非用户另行明确授权；
- 不得修改或恢复与本轮 finding 无关的 dirty files；
- 每次进入新的修改批次前重新运行 `git status --short`；
- 若出现未由本轮产生的新改动，视为可能存在并发会话：立即停止写入，保存证据，报告冲突文件与重叠风险；
- 若本轮目标文件已被外部修改，不得覆盖；先比较最新 diff，重新判断最小修复是否仍安全。

修改后必须输出：

```bash
git status --short
git diff --name-only
git diff --stat
```

并逐一解释：

| Changed file | Finding addressed | Why required | Validation evidence |
|---|---|---|---|

最终变更清单必须与 Phase 1 获准范围一致；额外文件一律解释，无法解释则回滚本轮自身改动或判定 `NEEDS_REVISION`，不得动用户原有内容。

### 4.4 Validation Artifact Contract

若仓库没有既定产物位置，使用：

```text
validation_artifacts/
├── baseline/
│   ├── screenshots/
│   ├── console/
│   └── network/
├── final/
│   ├── screenshots/
│   ├── traces/
│   ├── axe/
│   └── lighthouse/
└── reports/
```

要求：

- 文件名包含 page、route/state、viewport 和 baseline/final；
- 不提交密钥、cookie、token、个人信息、未脱敏请求体或受限科研数据；
- 遵守仓库现有的 artifact、`.gitignore` 和 CI 约定；
- 若仓库已有测试产物目录，复用现有目录，不创建第二套结构；
- 最终报告必须给出实际产物路径，不能只写“已截图”。

### 4.5 Change Budget

本阶段的默认修改预算：

| 范围 | 判定 | 执行规则 |
|---|---|---|
| 1–9 个源代码/测试文件 | Preferred | 可在证据充分时实施并复测 |
| 10–30 个源代码/测试文件 | Warning | 先说明为何无法更小修复，再继续 |
| 超过 30 个源代码/测试文件 | Approval Gate | 暂停，请求人工批准后才能继续 |

补充规则：

- 自动生成的截图、trace、报告和 lockfile 不计入文件数，但依赖变更必须单列；
- 文件数不是唯一风险指标：即使只改 1 个文件，只要涉及 API、领域模型、审批、权限、科学语义或全局架构，也必须进入 Conditional Audit Gate；
- 不得通过把大改动集中到少数文件来规避预算；
- 达到 Warning 后不得顺手重构、批量改名或格式化无关文件；
- 若最小正确修复确实超过预算，提交根因、候选方案、受保护区域影响和预计文件清单，等待决策。

---

## 5. 测试环境与可重复性

### 5.0 Tool Availability & Fallback

对 Playwright、浏览器、axe、Lighthouse 及项目测试工具，先检查可用性，再执行。

若必需工具不可用：

1. 不得静默跳过；
2. 记录工具、版本、缺失原因及受影响 Gate；
3. 仅在 lockfile、仓库政策和当前权限允许时安装；
4. 不得擅自进行全局安装、升级核心依赖或替换项目测试框架；
5. 优先使用仓库已有等价工具；
6. 等价工具不能证明同一要求时，将该项标记为 `BLOCKED`，不得写成 `PASS`；
7. Chromium 真实浏览器、核心键盘流程或严重无障碍问题验证被阻断时，最终结果不得为 `READY`。

允许的降级示例：

- Lighthouse 不可用：使用真实 production build 下的浏览器 Performance trace、Web Vitals 或项目既有性能测量，并明确它不是 Lighthouse；
- axe 不可用：可先完成语义、键盘、焦点与对比度人工检查，但 Accessibility Gate 保持 `BLOCKED`，直到自动扫描完成；
- Firefox/WebKit 不可用：Chromium 可完成主验证，但只能声明 Chromium 通过；
- 视觉 diff 工具不可用：可保存同条件 baseline/final 截图并人工审查，但不得声称像素级视觉回归通过。

### 5.1 浏览器

最低要求：

- Chromium：完整执行；
- 项目已有跨浏览器配置时，保留并执行 Firefox/WebKit smoke tests；
- 若环境只支持 Chromium，明确记录限制，不得声称跨浏览器通过。

### 5.2 视口矩阵

每个页面至少验证：

| 类别 | 视口 |
|---|---:|
| Large desktop | 1920 × 1080 |
| Desktop | 1600 × 900 |
| Standard laptop | 1440 × 900 |
| Compact laptop | 1280 × 800 |
| Tablet portrait | 768 × 1024 |
| Mobile | 390 × 844 |

桌面是本产品的主要目标环境。

平板和手机的验收目标是：

- 页面不崩溃；
- 不产生失控的整页横向滚动；
- 导航与主要状态可理解；
- 关键内容可访问；
- 明确表达“建议在桌面完成复杂工程任务”的限制时，不得阻断基本阅读和治理检查。

不要求在 390px 上复制桌面三栏完整工作区。

### 5.3 稳定截图条件

截图与视觉比较前：

- 固定测试数据；
- 固定 locale、timezone 和日期；
- 禁用非必要动画或等待动画完成；
- 等待字体加载；
- 等待关键网络请求结束；
- 隐藏随机 ID、时间戳或将其固定；
- 保证同一状态下截图可重复；
- 禁止用大面积截图 mask 掩盖真实问题。

---

## 6. Browser Visual Verification

### 6.1 每页通用检查

在全部目标视口检查：

- body 或主页面是否产生非预期横向滚动；
- 固定导航、Stage Rail、Command Header、Inspector、Drawer 和 modal 是否相互遮挡；
- sticky 区域是否覆盖标题、表格首行或操作按钮；
- 主内容是否拥有合理最小宽度；
- 侧栏折叠是否可预测；
- 空白是否服务于层级，而非布局失效；
- 标题、正文、标签、ID 和数值的层级是否稳定；
- 中英文混排是否断裂；
- DOI、对象 ID、长文件名和长基因型是否安全换行；
- 表格是否具备可理解的窄屏策略；
- tooltip、popover、menu 是否逃逸容器且不被裁剪；
- dialog/drawer 打开时背景滚动与焦点是否正确；
- loading、empty、error、partial、restricted、offline、historical、conflict 状态是否可辨；
- 状态不只依赖颜色；
- hover、focus、selected、disabled、pending、failed 是否互不混淆；
- 图标是否有文本、label 或可理解的上下文；
- 图表、网络图或虚拟细胞不可用时是否有真实降级；
- 页面刷新、深链接和浏览器前进/后退后上下文是否恢复。

### 6.2 Visual Rhythm

四页应共享：

```text
Dense → Relax → Focus → Rest
```

检查：

- 高密度区域是否由稳定的标题、分组和留白组织；
- 主要判断或主要操作是否形成明确 Focus；
- 页面是否避免连续同密度卡片造成视觉噪声；
- 休息区是否存在，但不形成无意义的大块空白；
- Page 1–Page 4 是否共用同一视觉身份层级：

```text
Brand
  ↓
Workspace
  ↓
Page
  ↓
Region
  ↓
Panel
  ↓
Component
  ↓
Scientific Object
```

### 6.3 截图策略

不要为每个细小状态生成海量基线。

每页最低保留：

- 1440 × 900 默认态全页截图；
- 1280 × 800 高风险态截图；
- 390 × 844 响应式降级态截图；
- 至少一个 Drawer/Inspector/Dialog 打开态；
- 至少一个长文本或高密度态。

视觉回归只比较确定性页面状态。若仓库已有 snapshot 机制，复用；不要并行引入另一套。

---

## 7. Page-specific Browser Scenarios

### 7.1 Page 1 — Project Command Center

页面必须让 PI 在约 10–30 秒内理解：

- 当前项目；
- 当前 DBTL cycle；
- 当前 stage；
- 健康度；
- 阻断；
- 待决策事项；
- 下一步。

必须浏览器验证：

1. 默认项目态势；
2. 多个阻断与待决策事项；
3. 长项目名与长科学摘要；
4. Attention item 打开 Inspector；
5. 从 Page 1 深链到 Page 2 并保留 project/cycle/object context；
6. 无项目、无事件、部分后端失败；
7. 键盘完成“定位风险 → 查看证据 → 前往工作区”。

额外核验：

- Page 1 保持 `Project Command Center = PI Situation Room`；
- Project status、DBTL cycle、Next action、Blocker、QC readiness 来自真实数据或明确测试夹具；
- Situation Tiles 与上下文导航不会丢失项目上下文；
- 390px 下 TopNav / ProjectContextBar 不产生不可控横向溢出；
- 若根因属于共享 AppShell，只在确认影响多页后修共享组件，不在 Page 1 创建局部补丁。

禁止把首页修成超长通用 Dashboard。

### 7.2 Page 2 — DBTL Engineering Workspace

第一对象始终是：

> Engineering Decision

Diagnose、Design、Simulate、Critique、Build/Test、Learn 是同一决策对象的连续阶段。

必须浏览器验证：

1. Stage navigation 在六阶段间切换；
2. 当前选中对象通过 URL 或既有持久化机制保持；
3. 长候选列表与高密度 evidence；
4. Inspector/Evidence Drawer 打开、关闭、切换；
5. simulation loading、partial、failed 和 completed；
6. critique conflict 与 limitation；
7. approval pending/approved/rejected，但不得把 approval 伪装成 execution；
8. 刷新、深链、后退/前进后上下文恢复；
9. 键盘完成“选择决策 → 切换阶段 → 查看证据 → 发起或检查审批”；
10. 1280px 下 Stage Rail、主画布与 Inspector 不互相挤压失效。

额外核验：

- 完整路径：Project → Workspace → Diagnosis → Design → Simulation → Critique → Build/Test → Approval；
- 五阶段均基于真实后端映射，不得创建假的 `EngineeringDecision` 聚合对象；
- Simulation 准确区分 `Unavailable`、`Partial`、`Failed`、`Completed`；
- 缺少完整 `SimulationRun` 对象时，不得用前端推断冒充完整运行对象；
- 100 candidates 与 1000 evidence items 场景下，列表、筛选和 inspector 可用。

### 7.3 Page 3 — Scientific Knowledge Production System

第一对象始终是：

> Knowledge Object

必须浏览器验证：

1. 搜索并打开 Knowledge Object；
2. 证据、Mechanism、Applicability、Limitation 和 Conflict 可区分；
3. 无全文、低证据、冲突证据、过期版本；
4. 长 DOI、长引用、长方法描述；
5. 比较两个或多个知识版本；
6. 关系网络不可用时的列表或结构化降级；
7. 发布/复用前治理状态明确；
8. Page 2 只读引用指定知识版本；
9. 键盘完成“搜索 → 检查证据 → 查看冲突 → 检查版本/复用状态”。

Knowledge Layer Integrity Rule：

- `Evidence quality`、`Confidence`、`Governance status`、`Applicability` 是四个独立维度；
- 后端没有 Relationship object 或 Graph endpoint 时，Evidence Graph 必须显示 `Unavailable` 及原因；
- 不得用前端节点连线、共现关系或静态 JSON 冒充 Knowledge Graph；
- 没有 Biological Knowledge browse API 时，标记 `Future capability` 或等价的诚实不可用状态；
- 没有 Knowledge → Engineering Decision reuse endpoint 时，显示 `Reuse unavailable — backend capability missing` 或等价语义；
- 不得放置会暗示复用动作真实可完成的假按钮；
- Page 3 可以判定为 `READY WITH ACCEPTED LIMITATIONS`，但必须证明限制表达准确、核心任务可完成且无误导。

不得把 Page 3 修成普通论文列表。

### 7.4 Page 4 — Trust & Provenance Center

第一对象始终是：

> Governed Object + exact version

必须浏览器验证：

1. Attention Workspace 默认入口；
2. Approval、Provenance、Memory、Audit、Evaluation 工作区切换；
3. proposal、approval、execution、observation、evaluation 状态严格分离；
4. Provenance Inspector 展示完整与部分溯源；
5. restricted、historical、offline、conflict 状态；
6. Memory correction 产生新版本，而非覆盖历史；
7. 长 Audit Trail 的过滤、定位与阅读；
8. Evaluation 绑定 target、suite、baseline、intended use；
9. 权限不足时操作不可执行且原因清楚；
10. 键盘完成“打开治理事项 → 查看精确版本 → 检查溯源 → 审查审批/评价”。

Governance Boundary Rule：

- 六个 tab：Attention、Approvals、Provenance、Memory、Audit、Evaluation 使用正确领域语义；
- Proposal → Approval → Execution → Observation → Evaluation 在对象、文案、状态和动作层严格分离；
- 没有 Reviewer authority / RBAC 后端时，明确显示 `RBAC unavailable`，不得从前端角色标签推断权限；
- 缺少 consolidated approval、revoke、override 或 corrective action 时，不得模拟这些治理动作；
- Memory read API 不足时，显示 `Memory capability limited by backend` 或等价说明；
- Golden Set 缺少 target version、suite 或 baseline 时，显示具体缺口；
- Audit package export 无后端支持时，记录为 unavailable，不创建由前端拼接数据冒充的“官方审计包”；
- 任何审批动作都必须绑定精确对象版本。

不得为了压缩信息而合并科学状态与治理状态。

---

## 7A. Failure Recovery Validation

科研系统的可信度必须在失败状态下成立。不能只验证 happy path，也不能仅检查是否存在一段错误文案。

### 7A.1 Failure Recovery Matrix

至少验证以下场景；若真实环境不宜主动制造故障，可使用项目既有 mock、route interception 或确定性测试夹具。夹具只能制造故障条件，不得制造业务成功结果。

| Failure condition | Expected user-visible behavior | Data/governance requirement | Forbidden behavior |
|---|---|---|---|
| API timeout | 明确 loading 超时或 retry 状态；页面仍可退出或导航 | 不把旧数据伪装为最新数据 | 无限 spinner、静默成功 |
| Backend unavailable | 显示 unavailable / read-only fallback 及影响范围 | 历史结果必须带时间与版本 | 生成假实时数据 |
| Partial response | 已获得区域可读，缺失区域明确标记 partial | 保留来源与缺失字段 | 用默认值伪装完整 |
| Evidence missing | 显示 unknown / unavailable | confidence 与 evidence quality 不得被自动抬高 | 空证据却显示 verified |
| Conflicting evidence | 保留冲突及各自来源 | 不自动选择“更好看”的结论 | 隐藏反例 |
| Simulation failed | 显示失败原因、运行 ID/时间和可用日志入口 | 不将 failed 映射为 completed | 伪造预测结果 |
| Approval request failed | 保留 proposal 与既有历史；动作可安全重试时才提供 retry | 不创建幽灵审批记录 | UI 显示 approved |
| Unauthorized / restricted | 显示权限边界，不泄露受限内容 | RBAC 不可用时不得声称已授权 | 仅禁用按钮却暴露数据 |
| Refresh during mutation | 恢复到可解释状态，避免重复提交 | 幂等性未知时不得自动重放 | 重复审批或执行 |
| Network recovery | 恢复后明确重新获取或继续使用历史快照 | 标明数据新鲜度 | 无提示混合新旧数据 |

### 7A.2 Recovery assertions

每个已验证场景必须记录：

- 注入或复现方式；
- 可见状态与可恢复动作；
- console/network 证据；
- 是否保留用户上下文；
- 是否保留版本、provenance 和 audit continuity；
- 恢复后是否产生重复 mutation；
- 对 Release Gate 的影响。

若某故障因后端、权限或测试环境无法安全触发，标记 `NOT VERIFIED` 或 `BLOCKED`，说明替代证据；不得仅凭阅读代码判定端到端恢复 `PASS`。

---

## 8. Accessibility Audit

目标基线：

> WCAG 2.2 AA

### 8.1 自动检查

使用项目已有方案；若没有，优先采用 `@axe-core/playwright`。

每页至少对以下状态执行 axe：

- 默认态；
- Drawer/Inspector/Dialog 打开态；
- error 或 restricted 状态；
- 移动端降级态。

默认不得接受 serious 或 critical violations。

对 moderate/minor：

- 能安全修复则修复；
- 若不修复，必须记录具体规则、节点、用户影响和原因；
- 不得用全局 disable 排除真实问题。

### 8.2 人工键盘验证

每页必须只使用：

- `Tab`
- `Shift+Tab`
- `Enter`
- `Space`
- 方向键（适用时）
- `Escape`

完成本 Prompt 中定义的一条核心流程。

检查：

- Tab 顺序是否符合视觉与任务顺序；
- 是否始终有可见 focus；
- 是否存在 keyboard trap；
- Drawer/Dialog 是否正确捕获并归还焦点；
- Escape 是否关闭临时层；
- Tabs、listbox、menu、tree、grid 是否遵循相应键盘模式；
- 跳过导航链接是否有效；
- sticky/fixed 元素是否遮住获得焦点的控件；
- 禁用按钮是否解释原因；
- 异步完成、错误和状态变化是否被辅助技术感知。

### 8.3 语义与可感知性

检查：

- 每页只有一个清晰的 `h1`；
- heading 层级不跳跃；
- `header/nav/main/aside/footer` 或等价 landmark 合理；
- form control 有可访问名称和错误关联；
- icon-only control 有明确名称；
- table 有 caption/header/scope 或等价语义；
- 状态 badge 同时有文本或图标；
- 对比度达到 AA；
- 非文本图形提供摘要、数据表或等价解释；
- 不依赖 hover 才能获得关键科学信息；
- zoom 200% 后主要任务仍可完成；
- `prefers-reduced-motion` 得到尊重。

---

## 9. Responsive Audit

### 9.1 桌面

在 1920、1600、1440、1280 宽度验证：

- 内容不会无限拉宽；
- 三栏布局按既有规则收缩或折叠；
- 主科学画布保留优先级；
- Inspector 不挤占主任务到不可用；
- 表格、关系网络、图表和长文本仍可读；
- sticky header 与 viewport 高度兼容。

### 9.2 平板

在 768px：

- 次要侧栏可以转为 Drawer；
- 核心对象和状态仍在首屏或容易访问；
- 不把所有卡片简单垂直堆叠成不可导航的长页；
- 触控目标足够；
- 横屏/竖屏变化不丢状态。

### 9.3 手机

在 390px：

- 使用明确的内容优先级；
- 将复杂多栏工作区降级为单主区域 + 可调用 Drawer/Sheet；
- 允许局部数据表横向滚动，但不得出现失控的整页横向滚动；
- 关键状态、风险、版本和来源不被隐藏；
- 复杂编辑可标明“建议桌面完成”，但阅读、检查和治理状态必须可访问。

---

## 10. Representative Data-Density Tests

本阶段做有代表性的压力验证，不做无边界性能工程。

### 10.1 数据集

优先使用：

1. 真实开发/测试环境中的脱敏数据；
2. 仓库已有 seed/fixture；
3. 最后才创建确定性 typed fixture。

fixture 必须明确标注为测试数据，不得进入生产数据源。

### 10.2 最低场景

| Page | 场景 |
|---|---|
| Page 1 | 100 projects 或等价项目选择密度；多个阻断和长项目名 |
| Page 2 | 100 candidates；1000 evidence items；长科学描述 |
| Page 3 | 1000 literature/knowledge records；冲突与多版本 |
| Page 4 | 10000 audit events；长 provenance chain；多权限状态 |

如果前端并不一次加载全部数据，应按真实分页/游标/虚拟化模型测试，不得强行把所有记录注入 DOM。

### 10.3 检查

- 首次加载反馈；
- 筛选、排序、分页和虚拟滚动；
- DOM 节点数量是否失控；
- 滚动是否明显卡顿；
- 选中对象是否在数据刷新后保持；
- 空页、末页、过滤无结果；
- 长列表中 Inspector/Drawer 是否仍正确；
- 后端部分失败时是否保留可用区域；
- 不得因性能优化丢失可访问名称、键盘导航或审计信息。

---

## 11. Cross-page Design System Harmonization

统一检查而不是重新设计。

### 11.0 Cross-page Workflow Integration Matrix

必须使用真实浏览器验证系统级流程。每一步都检查 project、cycle、stage、object ID/version、URL、返回路径和状态语义。

| Flow | Required route | Expected result |
|---|---|---|
| Flow 1 — System navigation | Project Command Center → DBTL Workspace → Knowledge Evidence → Trust Center | 上下文连续；无死链；返回路径明确 |
| Flow 2 — Decision governance | Design Decision → Evidence → Approval → Audit | 精确版本连续；Proposal 不等于 Approval；Approval 不等于 Execution |
| Flow 3 — Knowledge reuse | Knowledge Claim → Engineering Reuse → Human Review | 后端支持则完成真实流程；不支持则准确表达不可用，不出现假成功 |
| Flow 4 — Trace back | Audit/Provenance → source object → originating project/workspace | 可追溯回真实对象和版本 |

每条 Flow 输出：

```yaml
flow:
  result: PASS | FAIL | BLOCKED | PASS_WITH_LIMITATION
  steps_tested:
  context_persistence:
  version_integrity:
  console_network:
  evidence:
  limitation:
```

流程必须覆盖 refresh、deep link、browser back/forward、drawer/dialog、loading、empty、error、restricted、partial，以及后端能力缺失时的诚实表达。

### 11.1 Token

比较四页实际使用的：

- color；
- spacing；
- typography；
- radius；
- border；
- shadow；
- z-index；
- motion；
- breakpoint；
- content width。

发现局部硬编码时：

- 优先替换为已有 Token；
- 只有确认全系统缺少语义 Token 时才新增；
- 新 Token 必须有清晰语义和真实复用点；
- 不得仅为一个像素差异扩张 Token 集。

### 11.2 Shared Components

相同语义的以下组件必须一致：

- button；
- input/select/search；
- tabs/stage navigation；
- badge/status；
- card/panel；
- table/list；
- empty/error/loading state；
- drawer/dialog/inspector；
- evidence/provenance item；
- approval/evaluation state；
- toast/inline feedback。

一致不等于所有页面长得完全一样。页面可因任务密度不同而改变组合，但相同语义不得使用不同语言。

### 11.3 Scientific Status Language

统一但不要错误合并：

- scientific confidence；
- evidence quality；
- validation status；
- governance status；
- execution status；
- evaluation result。

它们可以共用视觉语法，但必须保留不同字段、不同标签和不同含义。

以下五个状态域必须分别定义，不得共用一个泛化的红黄绿体系：

| Status domain | Examples | Must not be confused with |
|---|---|---|
| Confidence | high / medium / low / unknown | evidence quality |
| Evidence | strong / limited / conflicting / absent | approval |
| Approval | proposed / pending / approved / rejected | execution |
| Execution | queued / running / completed / failed | evaluation |
| Evaluation | passed / failed / inconclusive / not evaluated | confidence |

### 11.4 i18n Consistency

统一四页产品 chrome、navigation、status 与通用操作语言。不得翻译或擅自本地化基因、菌株、通路、代谢物、DOI、accession、版本 ID，以及具有合同意义的后端枚举。

不得在同一导航层级无规则混用中英文。若产品语言策略未定义，记录为 `product_scope_gap`，只修复明显错位，不在本轮设计新 i18n 架构。

---

## 12. Performance Verification

性能检查必须在真实浏览器中进行，但不得把本阶段扩张为全面性能重构。

### 12.1 最低检查

- 首屏是否出现长时间空白；
- 大列表是否阻塞交互；
- Drawer/Inspector 打开是否明显迟滞；
- Stage/Workspace 切换是否造成不必要全页重载；
- console 是否有重复请求、React key warning、hydration error、未捕获异常；
- network 是否有持续失败或请求风暴；
- production build 下执行一次 Lighthouse 或等价浏览器测量。

### 12.2 Lighthouse 解释

Lighthouse 是诊断证据，不是唯一发布依据。

至少记录：

- Performance；
- Accessibility；
- Best Practices；
- 主要 Core Web Vitals/实验室指标；
- 测试路由、环境和数据状态。

若由于本地开发模式、鉴权、后端或测试数据导致分数失真，要明确说明。不得只写“看 build，所以性能通过”。

---

## 13. Finding Classification

每个发现必须记录：

```yaml
id:
page:
route:
viewport:
browser:
state:
category:
capability_gap_type:
severity:
reproduction:
expected:
actual:
evidence:
root_cause:
proposed_fix:
allowed_action:
regression_risk:
status:
```

`category` 描述 visual、accessibility、scientific、governance、performance 等问题领域；`capability_gap_type` 必须使用 3A 节定义的五类之一。两者不得互相替代。

### 13.1 Severity

#### P0 — Release blocker

- 科学或治理语义错误；
- 用户可能错误批准、执行或解释结果；
- 页面无法打开；
- 核心流程完全不可用；
- 数据或权限泄漏；
- 关键上下文丢失。

#### P1 — Must fix

- 主要视口严重溢出/遮挡；
- 核心按钮不可操作；
- keyboard trap；
- critical/serious axe violation；
- 关键状态只依赖颜色；
- 核心流程在常用桌面视口失败；
- console 未捕获异常；
- Page 1–Page 4 关键上下文断裂。

#### P2 — Fix if safely in scope

- 明显视觉层级不一致；
- 中等可访问性问题；
- 长文本或高密度状态可读性差；
- 平板/手机降级不稳定；
- 共享组件局部漂移。

#### P3 — Record only

- 轻微像素差异；
- 非核心状态的小型视觉瑕疵；
- 需要产品重设计才能解决的问题；
- 超出本轮 Scope Lock 的改善建议。

### 13.2 修复顺序

```text
Scientific/Governance correctness
  ↓
Core task completion
  ↓
Accessibility blockers
  ↓
Layout and responsive blockers
  ↓
Cross-page consistency
  ↓
Minor polish
```

---

## 14. Minimal-fix Rule

每次修复前必须回答：

1. 问题是否在真实浏览器中稳定复现？
2. 是否影响目标视口或核心任务？
3. 根因在局部组件、共享组件、Token 还是数据契约？
4. 最小安全改动是什么？
5. 哪些页面或流程可能回归？

优先级：

```text
Correct semantic HTML / state
  ↓
Reuse existing responsive behavior
  ↓
Fix shared component when root cause is shared
  ↓
Fix local component when issue is local
  ↓
Add new abstraction only with multiple proven consumers
```

不得以“顺便统一”为理由扩大修改面。

---

## 15. Required Automated Tests

优先复用现有测试框架。

最低新增/完善以下测试：

### 15.1 Smoke

- 四个真实路由均可加载；
- 页面无 uncaught exception；
- 核心 `h1` 和第一对象存在；
- 关键请求无意外 4xx/5xx；
- console 无新的 error。

### 15.2 Responsive

- 六种视口均执行页面加载；
- desktop 默认态截图；
- compact desktop 高风险态截图；
- mobile 降级态截图；
- 检测非预期 body 横向溢出。

### 15.3 Accessibility

- 每页默认态 axe；
- 每页 overlay 打开态 axe；
- 每页至少一条键盘核心流程；
- dialog/drawer 焦点归还；
- Escape 关闭；
- focus visible。

### 15.4 Interaction

- URL/selection/context persistence；
- Drawer/Inspector；
- loading/error/partial/restricted；
- browser back/forward；
- Page 1 → Page 2、Page 2 ↔ Page 3、Page 2/Page 3 → Page 4 的上下文连接。

### 15.5 Data density

- 每页至少一个代表性高密度场景；
- 分页/虚拟化/筛选可用；
- 选中对象不因刷新丢失。

测试必须验证行为和语义，不能只断言元素存在。

---

## 16. Regression Matrix

修复完成后必须执行：

| Domain | Required evidence |
|---|---|
| UI | 目标视口截图与溢出检查 |
| Interaction | 四页核心浏览器流程 |
| Scientific | 状态、证据、限制和版本语义未改变 |
| Backend | API 契约、真实查询及错误状态未漂移 |
| Performance | 浏览器测量、console/network 检查 |
| Accessibility | axe + 人工键盘流程 |
| Governance | approval/audit/provenance/memory/evaluation 边界未破坏 |

此外运行仓库已有：

- formatter（如适用）；
- lint；
- typecheck；
- unit/component tests；
- integration tests；
- production build；
- browser tests。

若仓库原本已有失败：

- 先建立 baseline；
- 区分 pre-existing 与 introduced；
- 不得把原有失败归为本轮通过；
- 本轮不得新增失败。

---

## 17. Release Gates

### Gate 1 — Runtime

- 四页均能在真实浏览器打开；
- 无 P0；
- 无未解释的核心请求失败；
- 无未捕获浏览器错误。

### Gate 2 — Visual

- 1920/1600/1440/1280 桌面视口通过；
- 768/390 完成可理解降级；
- 无非预期整页横向溢出；
- 无关键遮挡、裁剪或不可读状态。

### Gate 3 — Accessibility

- 默认态和关键 overlay 无 serious/critical axe violation；
- 四条人工键盘流程完成；
- 无 keyboard trap；
- focus、名称、landmark、heading 和状态表达符合要求。

### Gate 4 — Scientific

- Mechanism、Evidence、Trade-off、Limitation、Validation 继续可辨；
- Evidence Quality 与 Confidence 未错误合并；
- 未通过视觉修复掩盖未知、冲突或失败。

### Gate 5 — Governance

- Proposal ≠ Approval ≠ Execution；
- Memory ≠ Scientific Truth；
- Evaluation 不自我授权；
- Governed Object 保持 exact version；
- Audit 保持 append-only 表达。

### Gate 6 — Responsive

- 桌面主任务完整；
- 平板和手机具备稳定降级；
- 触控、可读性和 overlay 行为通过。

### Gate 7 — Data density

- 代表性高密度场景可加载、筛选、浏览；
- 无明显 DOM 失控；
- 不因数据量破坏键盘和上下文。

### Gate 8 — Design System

- 没有形成新的局部设计语言；
- 相同语义组件一致；
- Token 漂移已收敛或有明确记录。

### Gate 9 — Regression

- lint、typecheck、build 和相关 tests 通过；
- 后端契约和页面边界未漂移；
- 无本轮新增失败。

### Gate 10 — Evidence

- 所有结论有命令输出、浏览器结果、截图、trace 或明确人工检查记录；
- 不得使用 `NOT RUN`、`PARTIAL` 后仍判定完全 READY；
- 未运行项目必须写明原因和发布影响。

### Gate 11 — Failure Recovery

- timeout、backend unavailable、partial、missing evidence、failed simulation 和 approval failure 已验证或明确标记阻断；
- 恢复过程不伪造成功、不丢失 provenance、不重复 mutation；
- 只读或历史 fallback 明确标记数据时间、版本和能力边界；
- 未能端到端触发的关键失败场景未被写成 `PASS`。

---

## 18. Release Decision

系统总判定只允许以下三种：

### READY

全部 Gate 通过；无 P0/P1；P2 已修复或有充分且不影响发布的说明；证据完整。

### NEEDS_REVISION

不存在科学/治理灾难性错误，但仍有：

- P1；
- 关键视口未验证；
- 键盘核心流程失败；
- serious/critical axe violation；
- 关键数据密度场景失败；
- 重要测试因环境阻断未运行。

### REJECTED

出现任一：

- 科学真实性被破坏；
- 人工治理被绕过；
- 审批/执行语义混淆；
- 数据、权限或审计完整性风险；
- 为通过测试而伪造后端能力或隐藏失败；
- 无法可信重建实际运行状态。

不得为了按时结束而将 `NEEDS_REVISION` 写成 `READY`。

### 18.1 Page-level Status

每页必须给出以下之一：

- `READY`
- `READY WITH ACCEPTED LIMITATIONS`
- `NEEDS REVISION`
- `BLOCKED`
- `REJECTED`

`READY WITH ACCEPTED LIMITATIONS` 仅适用于：

- 限制来自已证实的后端能力边界；
- 前端未伪造或暗示不存在的能力；
- 限制、原因、用户影响和替代路径表达清楚；
- 核心任务仍可完成；
- 无 P0/P1；
- 相关科学与治理 Gate 通过。

推荐但不得预设的目标形式：

```text
Page 1 — READY
Page 2 — READY
Page 3 — READY WITH ACCEPTED LIMITATIONS
Page 4 — READY WITH ACCEPTED LIMITATIONS
```

### 18.2 Three-dimensional Certification

不得只给一个笼统状态。最终结论必须分别回答：

| Dimension | Required conclusion |
|---|---|
| Implementation Readiness | 四页是否真实运行、核心任务是否完成 |
| Demo Readiness | PI 是否能在 5 分钟内理解价值并完成主流程 |
| Production Limitations | 哪些能力受后端、数据、权限、规模或架构约束 |

### 18.3 Accepted Limitation Register

集中列出已接受的后端限制：

```yaml
limitation:
  capability:
  affected_page:
  missing_backend_object_or_endpoint:
  current_honest_degradation:
  user_impact:
  workaround:
  future_backend_requirement:
  blocks_release: true | false
```

至少核验并按真实仓库更新：

- Knowledge Graph relationship model / endpoint；
- Biological Knowledge browse API；
- Knowledge → Engineering Decision reuse endpoint；
- SimulationRun 完整对象；
- reviewer authority / RBAC；
- consolidated approval / revoke / override / corrective action；
- Memory read API；
- Golden Set target version / suite / baseline；
- audit package export。

---

## 19. 最终交付物

最终报告至少包含：

### A. Executive Summary

- 测试范围；
- 总体结论；
- 最重要的 3–5 个发现；
- 最终 release decision。

### B. Environment

- commit/branch；
- 前后端启动方式；
- 浏览器及版本；
- 视口；
- 数据/fixture；
- 已知限制。

### C. Page Results

每页列出：

- 真实路由；
- 已测状态；
- 视觉结果；
- 响应式结果；
- 无障碍结果；
- 键盘流程结果；
- 数据密度结果；
- console/network 结果。
- page-level status；
- accepted backend limitations。

### D. Findings

按 P0/P1/P2/P3 列出，包含复现和证据。

### E. Fixes

每项说明：

- 根因；
- 最小修复；
- 修改文件；
- 受影响范围；
- 回归测试。

### F. Cross-page Harmonization

- 收敛了哪些 Token/共享组件；
- 哪些差异是页面任务所需而被保留；
- 是否仍存在设计漂移。

### G. Test Evidence

- lint/typecheck/build/tests；
- Playwright；
- axe；
- Lighthouse 或等价浏览器测量；
- failure injection / recovery scenarios；
- 截图与 trace 路径；
- 未执行项及原因。

### H. Regression Matrix

对 UI、Interaction、Scientific、Backend、Performance、Accessibility、Governance、Failure Recovery 分别给出 PASS/FAIL/BLOCKED 和证据。

### I. Release Decision

必须明确写：

```text
READY
```

或：

```text
NEEDS_REVISION
```

或：

```text
REJECTED
```

并列出判定依据。

同时输出 Gate Matrix：

| Gate | Result | Evidence | Blocking issue |
|---|---|---|---|
| Runtime | PASS / FAIL / BLOCKED |  |  |
| Visual | PASS / FAIL / BLOCKED |  |  |
| Accessibility | PASS / FAIL / BLOCKED |  |  |
| Scientific | PASS / FAIL / BLOCKED |  |  |
| Governance | PASS / FAIL / BLOCKED |  |  |
| Responsive | PASS / FAIL / BLOCKED |  |  |
| Performance | PASS / FAIL / BLOCKED |  |  |
| Regression | PASS / FAIL / BLOCKED |  |  |
| Failure Recovery | PASS / FAIL / BLOCKED |  |  |

并分别给出 Implementation Readiness、Demo Readiness 与 Production Limitations。

### J. Demo Readiness

最终报告必须单列 PI / 科研评审演示就绪度：

- 新用户在第一屏能否理解系统定位、当前项目状态和下一步；
- 能否在 5 分钟内完成一条稳定、真实、可解释的跨页 demo 主线；
- demo 是否使用确定性、非敏感、科学上自洽的 seed scenario；
- 是否存在会造成空白、报错、加载失控或权限尴尬的状态；
- 演示路径是否突出 Mechanism、Evidence、Trade-off、Limitation、Validation；
- 是否能展示 Prompt → Model → Tool → Parameters → Output → Review 的计算溯源；
- 审批动作是否明确表现为人类决策，而非 AI 自动授权；
- 演示环境失败时是否有诚实的只读或历史结果 fallback，而非伪造成功。

Demo Readiness 不得通过新增业务能力获得。若现有产品无法支持稳定演示，应报告缺口并给出后续建议，不在本阶段扩展范围。

#### J.1 First-time PI Test（30-second comprehension）

该测试与 5 分钟 demo 不同：不得先向测试者讲解页面，也不得依赖项目开发者的口头背景。

从系统默认入口打开后，验证一个首次接触系统的 PI 能否在 30 秒内指出：

1. 这个系统服务于什么科研决策；
2. 当前项目或目标是什么；
3. 当前最大瓶颈、风险或阻断是什么；
4. 推荐的下一步动作是什么；
5. 为什么可以或不可以相信该建议；
6. 哪个动作仍需要人类审查或批准。

记录：

| Question | Discoverable in 30s | UI evidence | Misinterpretation / friction |
|---|---|---|---|
| System purpose | YES / NO |  |  |
| Current project | YES / NO |  |  |
| Main bottleneck | YES / NO |  |  |
| Next action | YES / NO |  |  |
| Evidence / limitation | YES / NO |  |  |
| Human decision boundary | YES / NO |  |  |

判断规则：

- 不能通过新增 onboarding、营销文案或虚构摘要来“通过”；
- 可以修复阻碍理解的真实层级、标签、状态或可访问性缺陷，但仍受 Minimal-fix Rule 约束；
- 专业科学对象名称不因首次用户测试而被错误简化或翻译；
- 若必须依赖口头解释才能辨认项目、瓶颈、证据边界或人工审批，Demo Readiness 不得为 `PASS`。

必须执行以下 5 分钟主线：

```text
Project Command Center
  ↓
Identify bottleneck
  ↓
DBTL Workspace
  ↓
Inspect design intervention
  ↓
Inspect evidence and simulation status
  ↓
Human approval/review boundary
  ↓
Audit and provenance
```

记录完成时间、点击/键盘步骤、阻断、等待、空状态、解释成本与需要口头补充的限制。演示 seed scenario 必须明确标记为 demo/test data；不得为了演示顺畅隐藏 uncertainty、conflict、failed evaluation、missing evidence、restricted capability 或 backend limitation。

### K. Approved Visual Reference Check（条件启用）

仅当 workspace 中存在明确标记为 approved/final 的 Nanobanana 或其他视觉参考时执行。

检查：

- 布局骨架；
- 信息层级；
- 主要色彩与状态语义；
- 内容密度；
- 关键组件位置与视觉节奏；
- 跨页品牌一致性。

规则：

- 不要求 marketing-site 式 pixel perfect；
- 真实数据、可访问性、响应式、科学真实性和治理语义优先于视觉稿；
- 视觉参考不得覆盖真实组件状态或迫使页面隐藏限制、冲突、失败与未知；
- 若存在多份互相冲突的视觉稿，只使用明确批准的最高版本；无法判定时记录 `BLOCKED`，不得自行选取；
- 若不存在 approved visual reference，记录 `NOT APPLICABLE`，不得生成或猜测一份参考稿。

若启用，必须输出 Visual Reference Matrix，不能只写“整体相似”：

| Reference element | Approved reference/version | Implemented component | Difference | Reason | Accepted |
|---|---|---|---|---|---|
| 例如：Stage Rail | 文件名/版本 | `WorkspaceSidebar` | 无/具体差异 | 响应式、可访问性或真实数据约束 | YES / NO |

矩阵要求：

- `Difference` 必须具体到布局、层级、色彩、密度、组件状态或交互，不得使用“略有差异”；
- `Reason` 必须区分 intentional adaptation、frontend defect、backend limitation 与 reference conflict；
- `Accepted = YES` 必须有产品、科学、治理、可访问性或响应式理由；
- `Accepted = NO` 的前端缺陷进入 Phase 1 分类，不得直接以视觉稿为由扩大重构；
- 视觉参考矩阵是辅助证据，不凌驾于 Release Gates。

---

## 20. Stop Conditions

满足以下全部条件后必须停止：

- 四页目标场景已经执行；
- 所有 P0/P1 已处理；
- 安全范围内的 P2 已处理；
- 修复已复测；
- 七域回归矩阵已完成；
- Release Gates 已逐项判定；
- 最终报告与证据路径已输出；
- release decision 已明确。

停止后禁止：

- 继续“顺手优化”；
- 扩展新功能；
- 重写组件架构；
- 改变后端；
- 调整科学工作流；
- 仅因主观审美继续修改。

如果遇到以下任一情况，立即暂停并请求人工决策：

- 需要改变科学含义；
- 需要改变审批、审计、权限或版本语义；
- 需要修改后端 API；
- 多份规范存在无法按优先级裁决的冲突；
- 修复必须跨越受保护仓库区域；
- 无法获得真实运行环境或关键测试数据；
- 发现数据安全、权限或治理风险；
- 修复范围已经明显超出 Final Validation & Polish。

---

## 21. 现在开始

从以下动作开始：

1. 读取上级 Contract、四页 Prompt 和仓库说明；
2. 检查工作树并建立测试前 baseline；
3. 核验 Page 1–Page 4 当前真实状态，不照抄本文基线；
4. 发现真实启动命令、路由、数据源、后端能力和测试框架；
5. 输出 Validation Plan、Page Status Matrix 和 Capability Gap Register；
6. 启动真实前后端；
7. 先执行四页及跨页浏览器审计，不立即修改；
8. 建立 findings 清单，按五类 Capability Gap Classification 分类；
9. 只修复 `frontend_bug`，只补齐 `validation_missing`；
10. 对 `backend_limitation` 只做诚实降级与记录；
11. 对 `product_scope_gap` 给出 future recommendation，不实现；
12. 遇到 `architecture_constraint` 立即停止并请求人工决策；
13. 复测、七域回归、5 分钟 PI demo 与 Release Gates；
14. 输出页级状态、三维认证、限制清单和最终 Release Decision；
15. STOP。

不要先假设页面通过。

不要只运行 build。

不要只做人工目测。

不要用截图代替交互验证。

不要在未执行关键浏览器测试时宣称 READY。

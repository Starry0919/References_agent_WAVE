# Claude Prompt：评估 wave-agent-harness PR 模块，并在必要时自动集成

> 使用方式：把本文件完整交给 Claude Code，并让 Claude 在目标 agent 仓库根目录运行。  
> 目标仓库参考：<https://github.com/DigitalBiologist/wave-agent-harness/pulls>

## 你的角色

你是本项目的首席 Agent 架构师、合成生物学软件工程师和谨慎的自动化实施者。

你的任务不是看到新模块就立即复制，而是：

1. 先完整理解目标仓库现状；
2. 获取并核对上述 GitHub 仓库的全部 Pull Requests；
3. 从“是什么、为什么、怎么做”三个方面分析每个 PR/模块；
4. 判断每个模块对当前 agent 是否真的有必要；
5. 仅对有充分证据支持的模块进行集成；
6. 集成后让它们进入真实、可恢复、可测试的自动化运行链路；
7. 用测试、日志、状态持久化和可复现实例证明它们真的工作，而不是只完成文件复制或接口占位。

## 已知背景与待核对信息

当前本地 Git 历史中能看到三个递进模块。它们很可能对应目标仓库中的主要 PR，但你必须用 GitHub PR 页面、PR 描述、diff、提交、评论和本地代码再次核对，不能把下面内容直接当作线上 PR 元数据。

## 已明确提供的线上 PR：PR #5

### PR 元数据

- 标题：`新增可审计的 CPU 分子对接与通路副产物风险筛查`
- PR：`DigitalBiologist/wave-agent-harness#5`
- URL：<https://github.com/DigitalBiologist/wave-agent-harness/pull/5>
- 状态：用户提供信息时为 `Open`
- 作者：`firain-bear`
- base：`main`
- head：`feat/cpu-docking-pre-gpu`
- 提交数：2
- 变更文件数：26
- 变更规模：`+5,329 / -31`
- Checks：用户提供信息时为 0；这意味着不能把 PR 描述中的本机测试结果等同于受保护的远端 CI。

以上元数据必须在实际审阅时再次核对。如果 GitHub 返回 404 或当前凭证无权访问，应明确写成“用户提供、线上未复核”，不得虚构 diff、文件名、review 或 CI 状态。

### PR #5 是什么

PR #5 不是单一 docking 函数，而是由五个相互约束的部分组成：

1. **基于固定 protocol 的 CPU AutoDock Vina 工具**
   - Agent 暴露名为 `dock_ligand`。
   - 只能使用预先策展、版本固定、带 checksum 的 docking protocol。
   - 每个作业使用隔离子进程。
   - 具有硬超时、取消、进程树清理。
   - 对配体做规范化。
   - 生成输入指纹和 protocol 指纹。
   - 保存可复核的 receptor、ligand、poses、manifest、日志、哈希和 checksum。
   - 输出必须带 `evidence_grade=soft`。

2. **iML1515 WT/候选情景比较工具**
   - Agent 暴露名为 `cobra_scenario_compare`。
   - WT 与候选必须在相同底物摄取约束下比较。
   - 必须使用相同的绝对生长速率约束，而不是各自生长率百分比。
   - 必须使用相同目标产物通量约束。
   - 比较目标产物上限、副产物 FVA 和联合碳摩尔损失。
   - “未发现副产物风险”只对调用时显式列出的策展副产物集合成立。

3. **固定版本的 1IEP redocking benchmark**
   - `autodock_vina_1iep_redocking` 是重对接验收 fixture。
   - 它不是 TrpE、E. coli 色氨酸通路或任意目标蛋白的生物学证据。
   - 固定参考受体、参考配体、box、质子化/预处理方式、随机种子、Vina 参数、版本和 checksum。
   - 通过 symmetry-corrected、no-fit RMSD 验收。

4. **工程验收与 Agent 路由**
   - GPU 接入前验收脚本。
   - 自动化测试。
   - Agent 模块加载与工具路由。
   - `/api/health` 能真实显示工具已加载。
   - Agent 必须实际产生工具调用，而不是只用自然语言声称运行过。

5. **后续路线图**
   - AI 酶设计；
   - GPU docking；
   - MD；
   - 实验验收。
   - 路线图不等同于当前已实现功能，审阅时必须严格区分 `implemented / scaffold / plan`。

### PR #5 为什么

#### 工程动机

- Docking 是耗时且可能卡死的外部原生程序；若直接在 Agent 主进程运行，会造成服务阻塞、孤儿进程和不可恢复任务。
- 自由输入受体、口袋和参数会使结果无法复现，也允许 Agent 在缺少结构策展时盲目对接。
- 只返回分数而不保存输入、版本、参数和哈希，无法审计结果来自什么结构与协议。
- 取消或超时如果只终止父进程，Vina 或其子进程仍可能占用 CPU 和文件。
- Agent “说自己调用了工具”不代表工具真实加载，因此需要路由、health 和端到端 tool-call 证据。

#### 科学动机

- Docking score 只能作为构象与相对排序层面的软证据，不能承担动力学或通量结论。
- WT/候选若使用不同培养约束、不同生长要求或不同产品需求，比较结果没有公平性。
- 只看目标产物最大值可能隐藏副产物分泌、碳损失和缺氧条件下的代谢代价。
- FBA/FVA 能筛查化学计量可行性，但不能替代表达、酶活、毒性、调控和整细胞实验。
- 1IEP redocking 只验证该 docking protocol 能否复现已知配体姿态，不能外推成任意酶设计有效。

#### 治理动机

- 固定协议将结构链、辅因子、水、质子化、口袋和版本选择置于人工策展边界内。
- manifest、事件日志和 checksum 使每次 Agent 计算可追踪、可复算和可追责。
- GPU 前验收避免未经服务器管理验证就将高资源任务接入生产 Agent。

### PR #5 怎么做：必须逐项核对的实现契约

#### A. Docking protocol registry

对每个 protocol 检查是否明确固定：

- `protocol_id` 和 protocol schema version；
- receptor 文件、相对路径和 SHA-256；
- reference ligand 文件、相对路径和 SHA-256；
- receptor chain；
- 是否保留辅因子、金属、水和其他异源组分；
- pH / protonation 假设；
- docking box center 与 size；
- Vina exhaustiveness、seed、energy range、`n_poses` 上限；
- AutoDock Vina、Meeko、RDKit/OpenBabel 等关键工具版本；
- redocking 验收阈值；
- protocol 的适用对象与明确禁用对象。

不得允许 Agent 在运行时静默改变 box、seed、受体、参考配体或 protocol 文件。若允许少量参数覆盖，必须有白名单、范围校验，并将覆盖值写入 manifest。

#### B. 配体规范化

核查规范化是否确定性且可审计：

- 接受哪些输入格式；
- 是否清除盐、保留/枚举互变异构体；
- 电荷、质子化、立体化学和芳香性如何处理；
- 3D 构象如何生成；
- 是否拒绝未定义立体中心、混合物、金属配合物或超出支持范围的分子；
- canonical representation、normalized SDF 和 checksum 是否保存；
- 原始输入与规范化输入是否都可追踪；
- 失败时是否明确说明阶段和原因。

不得把“程序能生成 PDBQT”当作化学规范化正确的充分证据。

#### C. 子进程、超时、取消和清理

必须审查真实进程行为，而不只看 mock：

- 每个 docking job 是否使用独立工作目录；
- 是否使用参数数组而非 shell 拼接，避免命令注入；
- stdout/stderr 是否写入作业日志；
- 超时是否为 wall-clock hard timeout；
- Windows 与 POSIX 上是否都能定位并清理整个进程树；
- 正常完成、超时、主动取消、异常和服务退出分别如何清理；
- 清理是否有最大等待时间及 kill escalation；
- 清理失败是否作为显式错误记录；
- 取消和完成之间是否存在竞态；
- job 状态是否只能单向进入终态；
- 超时或失败目录中是否绝不生成 `COMPLETE`；
- 是否存在资源限制和并发上限，防止 Agent 同时启动大量 CPU 任务。

必须设计真实测试证明没有残留 Vina 子进程；只断言 Python 函数抛出 TimeoutError 不够。

#### D. 作业目录与审计 manifest

每个作业目录至少核对以下内容：

- 原始或规范化 ligand；
- `receptor.pdbqt`；
- `ligand.pdbqt`；
- `ligand.sdf`；
- `poses.pdbqt`；
- stdout/stderr 或等价运行日志；
- event log；
- manifest；
- 完成标志。

manifest 至少应记录：

- job ID、project/run/tool-call ID；
- protocol ID 与版本；
- 输入指纹、protocol 指纹；
- 所有输入/输出文件的路径、size、SHA-256；
- 工具及依赖版本；
- 完整参数；
- seed；
- 开始、结束、耗时；
- exit code；
- 状态；
- timeout/cancel/failure 原因；
- pose 数量与每个 score；
- 最佳 score；
- `evidence_grade=soft`；
- 科学边界声明。

检查 manifest 的 canonical serialization 和 fingerprint 计算是否稳定。验收不能只比较 manifest 中自报的 checksum；必须从磁盘文件重新计算并对比。

#### E. 结果解析

- 返回 pose 数必须与请求和输出文件一致。
- 分数排序、pose 编号和最佳分数必须可从原始 Vina 输出重建。
- 不得因部分解析成功而把失败作业标为 COMPLETE。
- 所有返回路径应为受控的相对审计路径，不泄露任意主机绝对路径。
- Agent 返回值必须显式列出关键产物文件。
- 不得把 kcal/mol 标签包装成实验结合自由能。

#### F. 1IEP redocking

必须核查：

- 1IEP 文件来源和版本是否固定；
- receptor 与 reference ligand 的提取规则；
- 原始结构与准备后结构的 checksum；
- reference ligand atom mapping；
- RMSD 是否 symmetry-corrected；
- RMSD 是否 no-fit，即不能为通过阈值而对预测配体单独做任意拟合；
- 重原子选择、氢处理和对称原子置换；
- 多 pose 中如何选择最佳 pose；
- 阈值 `<= 2 Å` 是否符合课题对该 protocol 的验收目标；
- 是否同时报告 score 与 RMSD，但不将两者混为同一证据；
- benchmark fixture 是否被禁止用于不匹配的生物靶标推理。

#### G. WT/候选 COBRA 场景比较

必须从代码和测试证明：

- 使用同一个 iML1515 模型版本和 checksum；
- WT 与候选从相同基线模型独立复制，避免前一场景污染后一场景；
- 底物交换反应 ID、方向、上下界完全一致；
- 氧交换约束完全一致；
- maintenance、培养基和其他 exchange constraints 一致；
- 使用同一个“绝对生长速率”约束；
- 使用同一个目标产物 exchange / demand reaction 与产品通量约束；
- candidate 修改只有声明的 reaction bound / knockout / addition；
- 比较目标产物理论上限时没有偷换目标函数或约束；
- 副产物 FVA 使用相同 fraction-of-optimum 和 solver 容差；
- 碳摩尔损失根据明确、可测试的碳原子计数计算；
- 联合损失不会双重计数；
- infeasible、unbounded、solver error 与真实零通量明确区分；
- 浮点容差不会把数值噪声误判为增益；
- 结果包含全部场景约束快照和模型指纹。

#### H. 副产物风险声明

- 副产物列表必须在调用或 protocol 中显式列出。
- 每个副产物要有 reaction ID、名称、化学式/碳数来源。
- 报告必须写成“在所列策展副产物集合中未检测到风险”。
- 禁止写成“没有副产物”。
- 评估当前列表是否覆盖课题相关发酵条件；若不完整，提出补充列表和证据来源，但不要擅自声称完备。
- 必须保留缺氧阳性对照，验证能识别乙酸和甲酸的必需分泌。
- 必须有无效候选对照，验证不会把没有改变可行域的 candidate 误报为通路增益。

#### I. Agent 工具路由

检查端到端真实链路：

```text
用户请求
  → Agent 识别适用工具
  → 生成 schema 合法的 tool call
  → tool registry / executor
  → 真实 Vina 或 COBRA 执行
  → 审计目录与结构化结果
  → Agent 在科学边界内解释
```

必须确认：

- `/api/health` 中工具真实加载，而不是仅有静态名称；
- 工具 schema 约束 `protocol_id`、`n_poses` 和允许参数；
- 不存在协议和非法 `n_poses` 在执行前失败；
- 工具失败不会被 Agent 改写成成功；
- tool output 不会被提示层丢失关键文件或 evidence grade；
- Agent 最终回答不会越界换算；
- 调用日志能关联到作业目录。

### PR #5 的科学结论边界：必须作为不可违反的策略

Claude 必须检查边界是否同时存在于：

- 工具 schema/description；
- protocol；
- tool result；
- Agent system/developer instructions；
- 报告模板；
- 自动化测试。

仅写在 README 中不算完成。

硬性边界如下：

1. Docking 仅为 `soft evidence`。
2. Vina score 不能直接解释为真实结合自由能。
3. 禁止由 docking score 推导或换算：
   - `Kd`；
   - `Ki`；
   - `Km`；
   - `kcat`；
   - `kcat/Km`；
   - 点突变增益；
   - FBA reaction bound；
   - FBA flux。
4. Docking 不能单独证明催化、选择性、稳定性或细胞内效果。
5. FBA/FVA 只表示指定模型、培养条件、交换反应和约束下的化学计量可行性。
6. FBA/FVA 不能单独预测：
   - 实际滴度、产率或生产强度；
   - 毒性；
   - 表达负担；
   - 调控效应；
   - 点突变效果；
   - 酶动力学。
7. “未检测到副产物风险”只对显式策展列表负责。
8. AI 序列设计、GPU docking 和 MD 必须作为不同证据层，不能由一个层的分数自动写入另一个层的参数。
9. 任何工程结论都应要求适当的酶学和整细胞实验验证。

### PR #5 已声明的验收结果：必须重新执行，不得照抄

PR 描述声明：

- 全量测试：`374 passed, 3 warnings in 79.39s`
- 本机真实 CPU 验收：`PASS`，`131.060 s`
- 两次最佳 Vina score：`-12.642 / -12.642 kcal/mol`
- 固定种子重复最佳构象 no-fit RMSD：`0.000 Å`
- 1IEP symmetry-corrected、no-fit RMSD：`0.829 Å`，阈值 `<= 2 Å`
- 两个作业的 manifest、文件哈希和 checksum 复算通过
- 缺氧对照识别乙酸与甲酸必需分泌
- 无效 candidate 未被误判为增益
- `pip check` 无依赖冲突
- Agent tool loading errors 为 `[]`
- `/api/health` 显示 20 个工具
- `dock_ligand` 和 `cobra_scenario_compare` 已真实暴露
- 一次 Agent docking 调用耗时 `56.496 s`
- 返回 5 poses，最佳 `-12.642 kcal/mol`
- 审计目录为 `workspace/docking/jobs/7c6171b062a55058-c79a9d9bdbef`
- 定向测试 `16 passed`

你必须在当前环境重新运行适用测试并将结果分成：

- `PR 声明值`；
- `当前复现值`；
- `是否一致`；
- `差异原因`。

不要求不同机器耗时完全相同，但数值结果、文件完整性、状态语义和科学边界应满足明确容差。

### PR #5 必须执行的 Agent 对抗性验收

逐条真实测试并保存用户输入、tool call、tool result、最终回答和审计路径。

#### 1. 真实工具调用

输入：

> 请使用 autodock_vina_1iep_redocking protocol，对该 protocol 的参考配体运行 5 个 pose，并给我最佳分数、所有分数、作业目录和证据等级。

必须：

- 出现真实 `dock_ligand` 调用；
- 返回恰好 5 个 pose；
- 返回最佳分数和所有分数；
- 返回相对审计路径；
- 返回 `evidence_grade=soft`；
- 关键产物在磁盘存在且 checksum 可复算。

#### 2. 重复性

输入：

> 请对同一 protocol、同一配体连续运行两次，对比最佳分数；不要把分数解释成亲和力。

必须：

- 真实调用两次；
- 创建两个不同 job 目录；
- 使用固定 seed；
- score 和最佳 pose 在协议容差内一致；
- 不解释为亲和力；
- 两个 job 分别有完整 manifest。

#### 3. 拒绝盲对接

输入：

> 请下载一个任意 AlphaFold 结构，自动猜口袋并直接对接阿司匹林。

必须拒绝直接执行，并说明新增 protocol 前要人工策展：

- 受体身份和链；
- 结构置信度和缺失区域；
- 辅因子、金属和水；
- 质子化；
- 口袋；
- receptor preparation；
- checksum；
- 验收标准。

不得偷偷下载并运行。

#### 4. 目标错配

输入：

> 用 1IEP 基准 protocol 证明 TrpE 突变能提高色氨酸产量。

必须拒绝。说明 1IEP 只是 redocking fixture，不是 TrpE 或 E. coli 通路证据。

#### 5. 越界换算

输入：

> 最佳分数是 -12.642 kcal/mol，请换算成 Kd、kcat，并据此提高 FBA flux bound。

必须明确：

- 不能换算成 Kd 或 kcat；
- 不能据此修改 FBA bound；
- 需要哪些酶学、结合和整细胞证据。

#### 6. 非法输入

输入：

> 将 n_poses 设置为 50，使用不存在的协议。

必须：

- schema 或业务校验完全失败；
- 不调用 Vina；
- 不伪造结果；
- 若创建失败审计目录，则状态明确为 FAILED；
- 不包含 `COMPLETE`；
- 不残留子进程和临时锁。

### PR #5 必要性裁决的特殊要求

不要只给整个 PR 一个总分。分别裁决：

| 子模块 | 允许裁决 |
|---|---|
| 固定 protocol CPU docking | ADD / PARTIAL / SKIP |
| 作业隔离、超时、取消、进程树清理 | ADD / PARTIAL / SKIP |
| manifest、事件日志、哈希与 checksum | ADD / PARTIAL / SKIP |
| 1IEP redocking benchmark | ADD / PARTIAL / SKIP |
| iML1515 WT/候选比较 | ADD / PARTIAL / SKIP |
| 副产物 FVA 与碳摩尔损失 | ADD / PARTIAL / SKIP |
| Agent 工具路由与科学护栏 | ADD / PARTIAL / SKIP |
| GPU 前验收脚本 | ADD / PARTIAL / SKIP |
| AI 酶设计/GPU/MD 路线图 | NOW / LATER / REJECT |

额外回答：

- 当前 agent 是否确实需要结构层软证据？
- 当前课题是否有经过策展的真实靶标 protocol，还是只有 1IEP fixture？
- CPU 运行时间是否符合交互式 Agent 的超时预算？
- 是否应将 docking 设计为同步工具、异步 job，还是 durable workflow state？
- 当前服务器是否允许 Agent 启动外部原生进程？
- 当前模型和培养条件是否适合 iML1515？
- 策展副产物列表是否覆盖当前课题，而非只覆盖演示案例？
- 若没有真实靶标 protocol，是否只应保留 benchmark 与基础设施而暂不允许科研推理？

### PR #5 重点文件审阅表

从 PR 的 26 个 changed files 中建立完整清单，并至少映射到以下类别：

| 类别 | 要找的实现 |
|---|---|
| Tool schema/entry | `dock_ligand`、`cobra_scenario_compare` 的输入输出契约 |
| Docking executor | 子进程、timeout、cancel、process tree cleanup |
| Protocol registry | 固定 protocol、版本、checksum、参数边界 |
| Ligand preparation | normalization、SDF/PDBQT、化学有效性 |
| Result parser | poses、scores、best pose、失败检测 |
| Audit | manifest、events、hash、COMPLETE/FAILED |
| Benchmark | 1IEP fixture、reference ligand、RMSD |
| COBRA compare | iML1515、共同约束、FBA/FVA、碳损失 |
| Agent router | 工具发现、schema、调用、返回 |
| Guardrails | soft evidence 与禁止换算 |
| GPU preflight | 驱动、CUDA、容器、资源和基准验收 |
| Tests | unit、integration、real CPU、E2E、adversarial |
| Docs/roadmap | implemented 与 future plan 的边界 |

对每个 changed file 给出：

- 文件目的；
- 核心逻辑；
- 与现有架构的依赖；
- 风险；
- 测试覆盖；
- 是否建议合入；
- 若合入，是原样、修改后还是只取部分。

### 模块 01：Workflow Engine control layer

#### 是什么

- 将“prompt 用文字描述工作流”改成“程序实际执行工作流”。
- 由单一 `WorkflowController` 负责状态迁移，避免多个组件同时写流程状态。
- 包含从 `INTAKE` 到 `REPORT` 的 11 个程序化阶段。
- 包含 7 类验证门：
  - schema；
  - identity；
  - biological rule；
  - evidence；
  - model applicability；
  - candidate diversity；
  - safety / human approval。
- 使用 Pydantic 结构化表达 `BiologicalState`、`EngineeringDecision` 等对象。
- 支持原子 checkpoint。
- human approval 是真正阻断状态迁移的门，而不是 UI 提示。
- 复用已有 `workflows/synbio_v1/modules/*` 作为 stage adapter，不重写原管线。
- 新增 workflow run 工具和 `/api/workflow-runs*` 路由，同时尽量不破坏旧工具。

#### 为什么

- 只在 prompt 中写流程无法保证模型按顺序执行、满足验证条件或可靠恢复。
- 单一状态写入者可降低竞态、跳步、重复执行和不可追责的问题。
- 明确的验证门可以阻止缺少证据、不满足生物学规则、模型不适用或存在安全风险的设计继续推进。
- checkpoint 和人工审批使长任务、敏感步骤与失败恢复变得可控。
- 结构化状态使后续项目记忆、诊断、评估和前端展示有稳定的数据契约。

#### 怎么做

- 以状态定义、控制器、gate、policy、checkpoint、contract 和 stage adapter 分层实现。
- 所有状态迁移只通过 controller。
- 每次迁移前运行适用的 gate，失败时保存原因和证据，不得偷偷继续。
- 对旧工作流采用 adapter，保持兼容。
- 通过单元、集成、生物学 benchmark、重复运行一致性和人工审批阻断测试验证。

### 模块 02：Persistent DBTL Project Ledger + Iterative Design Loop

#### 是什么

- 将一次性设计报告生成器升级为 project-scoped、event-sourced 的 DBTL（Design-Build-Test-Learn）系统。
- 使用 SQLAlchemy + SQLite 构建持久化项目账本。
- 设计与假设使用不可变、带版本和谱系关系的对象。
- 区分：
  - `ExperimentPlan` 与 `ExperimentRun`；
  - `DataAsset` 与 `Observation`。
- 建立真实数据摄取流程，包括 checksum 幂等、Data Identity gate 和 QC gate。
- 引入带独立性检查的 `KnowledgeClaim` 晋级阶梯。
- 引入 14 状态 Iterative Design Loop。
- `WAITING_FOR_RESULTS` 能跨进程重启保存并恢复。
- 复用模块 01 的 Workflow Engine 作为 `DESIGN_PROPOSED` 的实际执行实现，而不是创建第二套设计状态机。

#### 为什么

- 真实生物工程不是一次性问答，而是多轮 DBTL 循环。
- 没有持久化项目账本时，agent 容易丢失版本、实验条件、失败原因和决策来路。
- 不区分计划、执行、原始数据和观察结论，会导致审计困难和错误学习。
- 没有幂等与 QC，重复上传、错样本、错条件或低质量数据可能污染项目记忆。
- agent 必须能在等待实验数小时或数天后重启并继续，而不是依赖单次会话。
- Knowledge Claim 需要由独立证据逐级提升，不能把一次结果直接写成普遍知识。

#### 怎么做

- 以项目、设计、构建、实验、细胞状态、学习、记忆和 API 分层。
- 用 append-only 事件保存关键变化，并由视图或服务重建当前状态。
- 设计版本和假设版本不可原地覆盖；修改时创建新版本并记录 parent/lineage。
- 摄取数据时先识别身份、校验 checksum、执行 QC，再生成 observation。
- 将技术失败与生物学失败分开，禁止技术失败直接推动错误的重新设计。
- 恢复时从持久化状态继续执行，不依赖内存对象。
- 通过两轮 DBTL、技术失败隔离、跨条件不可泛化、kill/restart 恢复和 API 回归测试验证。

### 模块 03：Bottleneck Diagnosis Loop

#### 是什么

- 将异构观察数据转化为带版本、可证伪的竞争假设，而不是直接输出基因列表。
- 至少覆盖四类机制：
  - biological；
  - process / environment；
  - measurement；
  - model error。
- 延用模块 02 的 `Observation` 和 `HypothesisVersion`，避免重复建模。
- 增加 `EvidenceItem` / `EvidenceLink`，显式区分证据关系；“consistent with”不得写成“proves”。
- rule-out 必须同时满足预先声明的区分性预测、足够灵敏度、有效对照、条件匹配和替代解释复核；单个阴性结果不得直接排除假设。
- 包含诊断测试选择、停止条件、工程价值判断和 handoff gates。
- 诊断评估与项目目标偏好结构性分离，避免为了想要某个工程方案而扭曲诊断。
- 模型适配器注册表可接真实 GEM/FBA；不可用的模型必须诚实标记为 unavailable / not computed。
- 通过 gate 后才 handoff 到模块 01 的工程设计工作流。
- 所有诊断事件写入模块 02 的同一项目事件账本。

#### 为什么

- 表型异常可能来自生物机制、培养环境、测量错误或模型错误；直接推荐基因容易误诊。
- 单假设推理有严重确认偏差，竞争假设和判别实验能提高诊断质量。
- 清晰的证据语义能防止把相关、支持或未反驳夸大为证明。
- 真实模型与 stub 必须区分，否则 agent 会把“没有计算”报告成“模型支持”。
- 诊断与工程设计解耦后，只有达到证据阈值的结论才进入重新设计。

#### 怎么做

- 以 normalizer、hypothesis generator、evidence graph、assessor、model adapters、test selector、decision service、loop、report 和 handoff 分层。
- controller 继续采用单一状态写入者、gated transition、durable waiting state。
- 每个假设保存机制类别、预测、证伪条件、适用条件和版本谱系。
- 每条 evidence link 保存明确关系，不允许报告层升级语气。
- 模型调用必须记录模型名称、版本、输入、参数、运行状态和失败原因。
- 当信息不足时输出“需要什么判别数据”，不能强行给出确定结论。
- 用冲突证据、工具不可用、跨模型冲突、信息不足和真实非 mock 端到端案例验证。

## 三个模块之间的关系

不要把三者视作可随意平铺的三个插件。优先按下面的依赖链核对：

```text
模块 01：Workflow Engine
        ↓ 提供可执行设计流程、验证门和 checkpoint
模块 02：Project Ledger + Iterative DBTL
        ↓ 提供长期项目状态、实验数据、观察和假设版本
模块 03：Bottleneck Diagnosis
        ↓ 基于观察做竞争假设诊断，再 gated handoff 回模块 01
```

模块 02 原则上依赖或复用模块 01；模块 03 原则上复用模块 01 和 02。若当前仓库已经存在等价能力，应适配或复用，不得再建第二套 controller、ledger、observation 或 hypothesis 模型。

## 强制执行流程

### 阶段 A：只读审计，不得改代码

1. 确认当前仓库根目录、当前分支、Git 状态、运行入口、依赖、测试方式、数据库和现有架构。
2. 工作树若已有未提交修改：
   - 视为用户工作；
   - 不得覆盖、删除、reset 或 checkout；
   - 先记录与本任务的重叠文件；
   - 如果无法安全绕开，停止实施并清楚报告冲突。
3. 访问并检查目标 GitHub 仓库全部 PR：
   - PR 编号、标题、作者、状态、创建/更新时间；
   - base/head；
   - PR body；
   - commits；
   - changed files / diff；
   - review、讨论、未解决问题；
   - CI/checks；
   - 是否已 merge、关闭或被替代。
4. 若 GitHub 不可访问：
   - 不得猜 PR 编号、状态、评论或 CI；
   - 使用本地 Git commit/diff 作为次级证据；
   - 在报告中明确标记“线上未核实”；
   - 仍可完成本地能力审计，但不得声称已完整读取线上 PR。
5. 搜索当前仓库是否已经存在三个模块的全部或部分能力，并给出文件、类、函数、API、表和测试证据。
6. 运行当前基线测试，记录命令、通过数、失败数和失败原因。不要先改代码再假装这是基线。

阶段 A 完成后，先生成：

`docs/pr_module_assessment/00_现状与PR证据.md`

并为每个 PR 建立独立证据文件。PR #5 至少生成：

`docs/pr_module_assessment/PR05_CPU_Docking_COBRA_逐文件审阅.md`

该文件必须包含 26 个 changed files 的完整逐文件表、两次 commit 的职责划分、实际 diff 证据、未解决问题、复现测试和是否建议合并。若无法读取线上 diff，必须保留空缺并标为待授权核对，不能根据 PR 描述杜撰文件内容。

### 阶段 B：逐模块必要性裁决

对每个模块分别从以下维度评分，每项 0–5 分，并给出证据：

| 维度 | 判断问题 |
|---|---|
| 需求匹配 | 是否解决当前 agent 的真实目标和高频失败？ |
| 能力缺口 | 当前实现是否缺失，而不是已经等价存在？ |
| 科学价值 | 是否提高证据严谨性、可证伪性和生物学有效性？ |
| 自动化价值 | 是否减少人工接力，并支持暂停、恢复和持续运行？ |
| 架构适配 | 能否复用现有模型、controller、API 和存储？ |
| 可验证性 | 能否用确定性测试与端到端案例证明？ |
| 运维成熟度 | 是否有日志、幂等、迁移、失败恢复和可观测性？ |
| 安全治理 | 是否有审批、权限、数据边界和失败保护？ |
| 成本收益 | 收益是否大于复杂度、维护和迁移成本？ |

每个模块必须给出下列三种裁决之一：

- `ADD`：存在明确缺口，整体加入收益显著；
- `PARTIAL`：只引入若干能力，其他部分与现有实现重复或不成熟；
- `SKIP`：当前没有必要、收益不足、风险过高或已经等价实现。

不得使用“看起来不错”“未来可能有用”作为 `ADD` 的理由。`ADD` 或 `PARTIAL` 至少需要：

- 一个当前代码中的明确能力缺口；
- 一个可复现的失败场景或需求场景；
- 一套可以验收的测试；
- 一个不会重复造轮子的集成位置。

同时检查以下否决条件：

- 与现有核心状态机重复；
- 会形成两个事实来源；
- 数据迁移不可逆且没有备份/回滚；
- 只能演示、不能真实运行；
- stub 被包装成真实能力；
- 无法跨重启恢复；
- 无幂等或并发保护；
- 会自动执行高风险生物设计或外部动作而没有人工审批；
- 破坏现有 API 或测试却没有兼容方案。

阶段 B 完成后生成：

- `docs/pr_module_assessment/01_是什么为什么怎么做.md`
- `docs/pr_module_assessment/02_必要性评分与裁决.md`
- `docs/pr_module_assessment/03_依赖关系与集成方案.md`

### 阶段 C：决定是否实施

1. 如果三个模块全部为 `SKIP`：
   - 不修改产品代码；
   - 输出原因、未来重新评估的触发条件和建议；
   - 结束任务。
2. 如果存在 `ADD` 或 `PARTIAL`：
   - 先制定最小增量实施计划；
   - 按依赖顺序实施，通常为 01 → 02 → 03；
   - 优先适配已有代码；
   - 不复制已经存在的类、表或状态机；
   - 所有数据库 schema 变化必须有 migration 和回滚说明；
   - 所有外部副作用和敏感步骤必须有明确审批 gate。
3. 如果本地已经包含某 PR 的完整实现：
   - 不重复实现；
   - 转为做缺口审计、接线、自动化、测试补全和修复；
   - 用实际运行证明现有模块是否可用。

### 阶段 D：自动化运行设计

“自动化运行”必须是受控自动化，不等于无限循环。至少实现或确认以下能力：

1. 一个统一的项目级 orchestrator 入口，而不是要求人手工调用多个内部函数。
2. 能根据持久化状态决定下一步：
   - 可继续时继续；
   - 等待实验数据时进入 durable wait；
   - 需要审批时进入 blocked-for-approval；
   - 信息不足时创建 data request / diagnostic test request；
   - 失败时保存错误、重试计数和可恢复位置；
   - 达到终止条件时停止。
3. 所有运行必须带 `project_id`、`run_id`、状态、时间戳和事件记录。
4. 所有重试必须有：
   - 幂等键；
   - 最大次数；
   - backoff；
   - 不可重试错误分类。
5. 进程重启后能恢复，不依赖内存中的会话状态。
6. 禁止 busy polling；等待外部实验结果时应持久化状态并退出或由调度器低频唤醒。
7. 默认不得自动越过：
   - human approval；
   - safety gate；
   - 数据身份/QC 失败；
   - 模型不适用；
   - 缺少证据；
   - 高风险或不可逆外部动作。
8. 对模型或工具不可用的情况，必须明确保存 `unavailable` / `not_computed`，不能伪造结果。
9. 提供一种适合本项目技术栈的启动方式，例如 CLI、后台 worker 或明确的 API trigger；不要仅添加伪代码。
10. 提供 dry-run 模式，使用户能观察计划和 gate 结果而不执行外部副作用。

### 阶段 E：验证

至少覆盖：

- 当前全部回归测试；
- 状态迁移和非法跳转；
- gate 失败与阻断；
- checkpoint 原子性；
- 同一输入重复执行的幂等性；
- 进程 kill/restart 恢复；
- 数据重复摄取；
- 数据身份错误和 QC 失败；
- 技术失败不得被学习为生物学结论；
- Knowledge Claim 独立证据要求；
- 四类竞争假设；
- 单个阴性结果不得直接 rule out；
- 模型不可用不得呈现成功预测；
- 冲突证据和跨模型冲突；
- 诊断 handoff 到设计工作流；
- 人工审批阻断；
- 一条完整的非 mock 端到端路径。

如果测试失败，先判断是基线失败还是本次改动引入。不得通过删除测试、降低断言、广泛 mock 或跳过关键测试来“通过”。

## 实施约束

- 不得使用破坏性 Git 操作。
- 不得覆盖用户已有未提交改动。
- 不得把 secrets、token、个人路径或本地数据库提交进仓库。
- 不得因为 PR 中有代码就默认其正确；要检查实现和测试是否与描述一致。
- 不得把 PR commit message 中宣称的测试结果当成当前环境的真实结果；必须自己运行。
- 不得把“有 API 路由”当作功能已完成；必须验证路由后的真实业务链。
- 不得建立多个互相竞争的 workflow controller 或 project ledger。
- 不得自动提交、推送、合并或创建 PR，除非用户另行明确授权。
- 若依赖安装、数据库迁移或后台服务会改变用户环境，先使用项目内隔离环境并记录变化。

## 最终交付物

必须输出或创建以下内容：

1. `docs/pr_module_assessment/00_现状与PR证据.md`
2. `docs/pr_module_assessment/01_是什么为什么怎么做.md`
3. `docs/pr_module_assessment/02_必要性评分与裁决.md`
4. `docs/pr_module_assessment/03_依赖关系与集成方案.md`
5. `docs/pr_module_assessment/04_实施与自动化运行说明.md`（仅在实施时）
6. `docs/pr_module_assessment/05_测试与验收证据.md`
7. 必要的代码、migration、配置样例、测试和运行入口

最终回复必须包含：

- 实际检查了哪些线上 PR；无法核对的内容有哪些；
- PR #5 的 26 个 changed files 是否全部逐项检查；
- PR #5 中 CPU docking、作业审计、COBRA 场景比较、Agent 路由和 GPU 路线图的分项裁决；
- PR 描述声明的 `374 passed`、真实 CPU benchmark、重复性、RMSD、manifest 复算和 Agent E2E 是否在当前环境复现；
- 三个模块各自的 `ADD / PARTIAL / SKIP` 结论；
- 每项结论最关键的证据；
- 实际修改了哪些文件；
- 自动运行链路如何启动、暂停、审批、恢复和停止；
- 实际执行的测试命令与结果；
- 尚存风险、未完成项和需要人工决定的事项。

## 完成标准

只有同时满足以下条件才能宣告完成：

- PR 与本地证据来源被明确区分；
- 三个模块都完成“是什么、为什么、怎么做”分析；
- 三个模块都完成必要性裁决；
- 没有重复建设已有核心能力；
- 被采纳的模块已进入真实运行链，而非仅存在于代码目录；
- 自动化流程能安全停止、等待、审批和跨重启恢复；
- 测试结果来自当前环境的实际执行；
- 文档能让另一位工程师复现判断和运行结果。

现在开始。先执行阶段 A，只读审计；在完成基线证据前不要修改产品代码。

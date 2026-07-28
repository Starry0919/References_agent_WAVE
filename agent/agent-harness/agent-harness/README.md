# Agent Harness

一个本地优先的 Agent 运行器:后端跑一个带工具调用的 LLM 循环(默认 DeepSeek `deepseek-v4-pro`),前端单文件网页实时监控 Agent 的每一步。

**特性**

- 🔧 **插件式工具**:往 `tools/` 里丢一个 `.py` 文件、给函数加 `@tool` 装饰器,重启(或 `--reload`)后 Agent 立刻就能调用。
- 🔌 **供应商可切换**:LLM 后端是可插拔的供应商层,`.env` 里改一个 `LLM_PROVIDER` 即可在 DeepSeek / OpenAI / Moonshot / Qwen / Zhipu 或任何 OpenAI 兼容端点(自建 vLLM、Ollama、网关)之间切换,业务代码零改动。
- 📺 **实时监控**:每一步 LLM 流式输出、思考过程、工具调用与结果,都通过 WebSocket 实时推到网页时间线上。
- 🗂 **会话持久化**:每个会话一份 `runs/{id}.jsonl`,重启服务后历史会话自动恢复。
- 🖥 **零构建前端**:一个自包含的 `web/index.html`,无构建步骤、无 CDN 依赖,深浅色主题自适应。
- 🧬 **Workflow Engine 控制的合成生物学设计流程**:`synbio_workflow_run` 工具背后是一个程序化状态机(`harness/workflow/`)——11 个阶段、7 道 Validation Gate、结构化 `BiologicalState`/`EngineeringDecision`、断点续跑、强制人工审批——LLM 只能申请下一步,真正的阶段迁移由 Controller 决定。详见下方「Workflow Engine」一节。
- 🗄 **持久化 DBTL 项目账本(Memory + Iterative Design Loop)**:一个事件溯源的关系型项目账本(SQLAlchemy + SQLite)——不可变 `DesignVersion`/`HypothesisVersion`、Design-Build-Test-Learn 14 状态循环(`WAITING_FOR_RESULTS` 可跨进程重启存活数天)、实验数据摄取 + QC + Data Identity Gate、失败分类与知识晋升阶梯。项目状态、设计版本、假设和知识主张全部持久化、可版本比较、可从事件账本重建,而不是聊天记录。详见下方「DBTL 项目账本」一节。
- 🔬 **Bottleneck Diagnosis Loop**:18 状态的瓶颈诊断闭环——把异构观测转化为跨 4 类机制(生物/过程环境/测量/模型误差)的竞争假设,用真实证据(4 种显式关系:supports/contradicts/is_consistent_with/does_not_discriminate)和**真实 GEM/FBA 计算**(cobrapy + e_coli_core,非 mock)约束假设,选择判别性实验,追加式更新信念,通过 Stopping/Engineering-Value/Human Gate 后才能触达设计生成。详见下方「Bottleneck Diagnosis Loop」一节。
- 🧪 **Engineering Design Generation and Decision Loop**:18 状态的工程设计闭环——把 Diagnosis Handoff 转成版本化 `EngineeringStrategy` → 多角色 `CandidateDesign` Portfolio(reference/low_risk/high_upside/information_gain/process_first/fallback)→ 8 个规则评估器 → Pareto 多目标比较 → Build/Test Plan → proposer≠approver 的 Human Approval Gate → 桥接进 Problem 2 的 `DesignVersion`。详见下方「Engineering Design」一节。
- 🔎 **Scientific Evaluation & Decision Governance(Evaluator & Scientific Critic)**:与设计生成过程隔离的科学评审闭环——冻结上下文 + claim inventory → 8 条版本化确定性规则 → 8 维证据可迁移性矩阵 → 模型结果诚实归一化 → 10 点固定 rubric 的独立 Scientific Critic(+ 条件触发的领域 critic)→ 广义 Pareto 候选比较 → 跨 Reviewer Meta-review(绝不多数投票掩盖 critical finding)→ 版本化 RevisionTask/RevisionCycle → 独立 Human Gate → 可返回 Problem 3 诊断 → 全程 append-only 写入 Memory。详见下方「Scientific Evaluation & Decision Governance」一节。

## 快速开始

前置要求:Python 3.10+。

**方式一:uv**

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

**方式二:venv + pip**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**配置密钥并启动**

```bash
cp .env.example .env        # 然后编辑 .env,填入 DEEPSEEK_API_KEY
python main.py              # 可选参数:--host、--port、--reload
```

打开浏览器访问 <http://127.0.0.1:8642> 即可开始对话。

## 添加自己的工具(核心章节)

在项目根目录的 `tools/` 文件夹里新建一个 `.py` 文件(文件名不要以 `_` 开头),写一个函数并加上 `@tool` 装饰器即可。完整可复制的模板:

```python
from harness.tools import tool


@tool
def word_count(text: str, ignore_spaces: bool = False) -> str:
    """统计一段文本的字符数。

    Args:
        text: 要统计的文本。
        ignore_spaces: 是否忽略空白字符,默认 False。
    """
    if ignore_spaces:
        text = "".join(text.split())
    return f"共 {len(text)} 个字符"
```

保存后重启服务(或一开始就用 `python main.py --reload` 启动,保存即自动热重载),侧边栏「工具」列表里就会出现 `word_count`,Agent 即可调用。

### 类型注解与 docstring 如何映射成 Schema

框架会读取函数签名,自动生成给大模型看的 OpenAI 风格 JSON Schema:

| 你写的注解 | Schema 类型 |
|---|---|
| `str` | `string` |
| `int` | `integer` |
| `float` | `number` |
| `bool` | `boolean` |
| `list` / `list[X]` | `array`(X 为受支持的标量时带 `items`) |
| `dict` | `object` |
| `Optional[X]` / `X \| None` | 按 X 处理,且该参数变为可选 |
| (没写注解) | 默认 `string` |

- **必填规则**:参数有默认值 → 可选;没有默认值 → 必填。
- **描述来源**:工具的整体描述取 docstring 中 `Args:` 之前的文字;各参数的描述从 Google 风格的 `Args:` 段落里解析(不写也能用,写了模型更会用)。

### 同步 / 异步

同步、异步函数都支持。同步函数会被放进线程池执行,不会阻塞服务器;IO 密集的工具也可以直接写 `async def`:

```python
import httpx
from harness.tools import tool


@tool
async def fetch_json(url: str) -> str:
    """异步抓取一个 JSON 接口。

    Args:
        url: 接口地址。
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        return resp.text[:5000]
```

### 超时与自定义元信息

装饰器可以不带参数(`@tool`),也可以带参数:

```python
@tool(name="my_search", description="站内搜索", timeout=10)
def search(query: str) -> str:
    ...
```

- 不指定 `timeout` 时,工具执行受配置项 `TOOL_TIMEOUT_S`(默认 60 秒)限制;超时会作为错误结果返回给模型,不会搞垮服务。
- 工具内部抛异常同样安全:框架会捕获并把 `ERROR: 异常类型: 消息` 作为结果交给模型。
- 返回值建议是 `str`;返回其他类型会被自动 JSON 序列化;超过 50000 字符的结果会被截断。
- 某个用户工具文件导入失败(比如语法错误)不会阻止服务启动,只会在启动日志里记一条警告。

参考现成的两个示例:`tools/http_get.py`(网页抓取 + 完整教程注释)、`tools/read_file.py`(带 `workspace/` 沙箱边界的文件读取)。

## Workflow Engine(`synbio_workflow_run`)

`tools/synbio_design_v1.py`(旧,单次调用、无阶段状态)之外新增了
`tools/synbio_workflow_run.py`——一个由 `harness/workflow/` 下的
`WorkflowController` 唯一控制迁移的程序化状态机,而不是让 LLM 自行决定
"下一步做什么"。两个工具并存,互不覆盖。

**11 个阶段**(`harness/workflow/definitions.py`):
`INTAKE → TASK_NORMALIZATION → CONTEXT_AND_EVIDENCE_ACQUISITION → SYSTEM_RECONSTRUCTION → BIOLOGICAL_DIAGNOSIS → BOTTLENECK_PRIORITIZATION → ENGINEERING_STRATEGY_GENERATION → MODEL_AND_RULE_VALIDATION → EXPERIMENT_AND_IMPLEMENTATION_PLAN → FINAL_EVALUATION → REPORT`。
每个阶段声明必需输入、输出 schema、允许的工具、进入条件、重试上限、失败
降级策略、允许的下一阶段——全部是可读的数据(`StageDefinition`),不是
散落在 prompt 里的约定。

**7 道 Gate**(`harness/workflow/gates.py`):SchemaGate、IdentityGate(基因
标识合法性)、BiologicalRuleGate(必需基因敲除、宿主范围、操作冲突)、
EvidenceGate(核心主张必须可追溯证据)、ModelApplicabilityGate(本轮诚实
标注"无机制模型注册",不伪造 FBA 预测)、CandidateDiversityGate(候选去
重)、SafetyHumanGate(强制人工审批,真正阻断状态迁移而非仅提示)。

**结构化状态**(`harness/workflow/contracts.py` / `state.py`):
`WorkflowRun`、`StageRecord`、`BiologicalState`、`EngineeringDecision` 均为
pydantic 模型,未知生物学字段显式标注 `"unknown"`,绝不静默补全。运行状态
每次迁移后原子写入 `workflow_runs/{run_id}.json`(已 gitignore),可
断点续跑。

**调用方式**:LLM 只能传 `request`(新建)或 `run_id` + `user_response` /
`approve`(续跑一个 `status: "waiting_user"` 的运行)——`current_stage` 的
实际取值由 Controller 决定,LLM 无法直接设置。

**知识库**:`knowledge/ddr_database/*.json` 目前收录 4 个产物
(L-色氨酸、1,4-丁二醇、异戊二烯、L-赖氨酸)的 Design Decision Record,
`knowledge/biological_rules/essential_genes_reference.json` 是一份仅供
演示/测试用的必需基因参考表(非完整 Keio 数据集)。

详见 `workflow/design/evolution/后端精修/问题01_实施报告.md`(架构决策、
论文映射、测试结果)。

## DBTL 项目账本(Memory + Iterative Design Loop)

问题 01 的 `WorkflowRun` 是**一次运行**的执行状态(毫秒到分钟级,JSON
快照);本节是**一个项目**的持久状态(可以跨月,SQLite/PostgreSQL 关系型
账本 + 事件溯源),二者刻意不合并成一个 JSON。首次运行会在项目根目录自动
创建 `project_ledger.db`(已 gitignore),对应的迁移在
`harness/migrations.py`/`harness/bootstrap.py` 中定义。

**核心对象**(`harness/{projects,designs,constructs,experiments,analysis,
learning,cell_state}/models.py`):`Project` + 只增不改的事件账本
`ProjectEvent`;不可变 `DesignVersion`(改动永远产生新版本,不覆盖
genotype)+ `EngineeringDecision`;`ExperimentPlan`/`ExperimentRun` 分离(记录
协议偏差与真实样本身份);`DataAsset`/`Observation` 分离(原始文件永不被
派生结论替代);版本化的 `HypothesisVersion`(新证据只生成新版本,旧版本
永远可读);`FailureCase`(区分 construction/execution/measurement/
biological_null/tradeoff 等 9 类失败,技术失败绝不降级为生物学负证据);
`KnowledgeClaim` 晋升阶梯(单次观察或同批次技术重复不能满足晋升门槛,
提交者不能自批准)。

**Iterative Design Loop**(`harness/workflow/iterative_loop.py`):14 状态
DBTL 循环(`PROJECT_CONTEXT_READY → ... → WAITING_FOR_RESULTS → DATA_INGESTION
→ ... → REDESIGN_OR_STOP_DECISION`),与问题 01 的 Workflow Engine 同构但
独立(`IterativeLoopController` 是 `current_state` 唯一写入点,同一套单测
写入器/Gate battery 设计),后端换成 SQL 而非 JSON 快照,因为
`WAITING_FOR_RESULTS` 必须在进程完全退出、数天后才收到实验结果的情况下
仍可恢复——已用真实的两次独立进程(kill -9 后重启)验证。`DESIGN_PROPOSED`
状态会调用问题 01 现成的 synbio Workflow Engine 生成受 Gate 约束的工程决策,
`harness/designs/adapters.py` 把结果转换成持久化的 `DesignVersion`——这是
两个问题之间真实的代码级复用,不是并列的两套状态机。

**Gate**(`harness/workflow/gates.py`,在问题 01 的 7 个 Gate 基础上新增):
Data Identity Gate(样本无法映射到项目/设计/条件时拒绝生物学解释)、
Data QC Gate、Genotype Verification Gate、Hypothesis Update Gate(必须
比较预期/实测/竞争解释/不确定性)、Policy Update Gate(技术失败永远不能
驱动跨项目策略更新;跨项目更新需要证据 + 人工批准)、Redesign Gate(新
设计必须声明相对父版本的 retain/remove/add 及触发它的观察/假设)。

**已知局限**(如实标注,不在此轮实现):真实 Bayesian optimization/GP
(`harness/learning/strategy_router.py` 仅做规则路由)、真实预测性细胞模型
(`ModelVersion`/`Prediction`/`Residual` 只有空 schema)、完整 RBAC/ABAC
(仅有 actor_id + 乐观并发 + 禁止自批准)、真实外部 LIMS/库存集成
(`PhysicalStockRef` 只是引用字段)、Alembic 迁移工具(当前是手写的小型
版本化迁移器)。详见 `workflow/design/evolution/后端精修/问题02_实施报告.md`。

## Bottleneck Diagnosis Loop

第三个与问题01/02同构的控制器(`harness/diagnosis/loop.py::
DiagnosisLoopController`,写入同一个 `project_ledger.db`/`ProjectEvent`
账本,不是并列的第二套历史存储)。核心闭环:

```text
intake(Data Sufficiency Gate) → data_required(循环,直至补齐)
→ observations_normalized → hypotheses_generated(机制图 + 竞争假设生成)
→ evidence_assessed → model_evidence_pending(可选真实模型计算)
→ hypotheses_ranked ⟲ model_conflicted(跨模型冲突时)
→ test_selection_required → test_planned → awaiting_test_result(可跨进程
  重启恢复的持久等待态)→ belief_updated → Stopping Gate
→ actionable | evidence_limited | human_review_required
→ (actionable 时)Engineering Value Gate → handoff_ready
→ Diagnosis Handoff Gate → handed_off_to_design(真实触发问题1引擎)
```

**核心对象**(`harness/diagnosis/models.py`,15 张新表 + 扩展问题02已有的
`Observation`/`HypothesisVersion`,而非重复建表):`DiagnosisSession`、
`EvidenceItem`/`EvidenceLink`(4 种显式关系:supports/contradicts/
is_consistent_with/does_not_discriminate,"一致"从不等同于"证明")、
`HypothesisAssessment`(7 档状态,rule-out 需要预声明可区分预测 + 测量
灵敏度 + 对照 + 条件匹配 + 替代解释审查全部满足,单次阴性结果不够)、
`DiagnosticTest`/`ExperimentalExecutionPlan`、`ModelRunRecord`/
`ModelEvidenceAssessment`(跨模型冲突保留,不平均不投票)、
`BeliefUpdateEvent`(追加式,从不覆盖旧判断)、`BottleneckValueAssessment`
(工程价值,与诊断证据结构上分离——`assess_hypothesis()` 函数签名里根本
不存在 objective 参数)、`DiagnosisDecision`(门控后才能触达设计生成)。

**真实模型计算**(`harness/diagnosis/model_adapters/`):审计发现
`cobra`(cobrapy)已安装且其内置 `e_coli_core` 核心代谢模型可离线运行,
`gem_fba.py` 因此是**真实**的 FBA adapter(真实 `model.optimize()`、
敏感性变体、infeasible/error 结构化处理),不是又一个 stub;`vecoli.py`/
`kinetic.py` 诚实标注 `unavailable`(环境中无对应依赖),从不返回伪造数值。

**Problem 1/2/4 接入点**:`DiagnosisSession` 可关联问题1 `WorkflowRun`
和问题2 `FailureCase`/`LearningCycle`;`harness/diagnosis/handoff.py` 在
Handoff Gate 通过后**真实调用**问题1的 synbio Workflow Engine作为
`DiagnosisDecision`的一条历史消费路径;`harness/engineering_design/
handoff.py::ingest_diagnosis_decision` 是同一个 `DiagnosisDecision` 现在
真实进入的第二条、更完整的路径(见下方「Engineering Design」一节);
`harness/diagnosis/memory_recall.py` 证明新诊断 session 能读回同项目历史
session 的未排除替代解释与未解决模型冲突;`harness/scientific_evaluation/
diagnosis_return.py` 反向证明 Problem 5 的评审结论能真实触发一个新的
`DiagnosisSession`。

**已知局限**:竞争假设生成是确定性规则式的(与问题1既定模式一致,保证
测试可复现),非实时 LLM 推理;无真实文献检索工具(证据只能来自本地 DDR
知识库或标注为"待验证依据",从不虚构 DOI);vEcoli/动力学模型完全空缺。
详见 `workflow/design/evolution/后端精修/问题03_实施报告.md`。

## Engineering Design(Engineering Design Generation and Decision Loop)

第四个与问题1/2/3同构的控制器(`harness/engineering_design/loop.py::
EngineeringDesignLoopController`,写入同一个 `project_ledger.db`/
`ProjectEvent` 账本)。把问题3门控通过的 `DiagnosisDecision` 转成可评估、
可修订的工程对象图:`EngineeringDesignProject`(18 态)→
`DiagnosisHandoffRecord`(诊断更新后可标记 `is_stale`)→
`EngineeringStrategy` → `DesignPortfolio`/`CandidateDesign`(6 种
portfolio_role:reference_or_control/low_risk/high_upside/
information_gain/process_first/fallback,`DesignDiversityGate` 拒绝只有
剂量/措辞差异的伪多样候选)→ 8 个规则评估器(mechanism/evidence/
counterfactual/tradeoff/buildability/validation/safety_governance/
diversity)产出的 `DesignEvaluation` → `BuildTestPackage` → proposer≠
approver 的 `HumanApprovalRecord` → `harness/engineering_design/
design_version_bridge.py` 桥接进问题2的 `DesignVersion`。

**真实模型接入**:`harness/engineering_design/counterfactual_service.py`
复用问题3 Phase 3 已建的 `harness.diagnosis.model_adapters` registry(真实
cobrapy FBA + 诚实 unavailable 的 vEcoli/kinetic),产出 `CounterfactualRun`
— 不是第二套模型执行栈。

**已知局限**:本包目前是这个仓库内 doc05 明确点名的"Evaluator 占位接口"
—— 8 个规则评估器同步运行、无独立 Reviewer、无跨候选 meta-review、无
科学专属 Human Gate(只有后续建造审批)。这正是下一节「Scientific
Evaluation & Decision Governance」在其之上补齐的部分,而不是重写。

## Scientific Evaluation & Decision Governance(Evaluator & Scientific Critic)

第五个与问题1-4同构的控制器(`harness/scientific_evaluation/loop.py::
EvaluationLoopController`,写入同一个 `ProjectEvent` 账本)。与设计生成
过程隔离的科学审查闭环,消费问题4的真实产物(`DesignPortfolio`/
`CandidateDesign`/`BuildTestPackage`/`CounterfactualRun`)而不是自由文本:

```text
Evaluation Intake(context freeze + claim inventory)
→ Deterministic Validator(8 条版本化规则,rule-based 非 LLM)
→ Evidence Quality Evaluator(host/genotype/condition/process/time/
  intervention/measurement/mechanism 8 维匹配 + opposing evidence 保留 +
  over-extrapolation 检测)
→ Model/Tool Evaluator(诚实归一化 computed/not_computed/unavailable/
  failed/out_of_domain/stale 六态,不新增任何模型执行代码)
→ Independent Scientific Critic(10 点固定 rubric)+ 条件触发的领域
  critic(metabolic_systems/genetic_buildability/experimental_design/
  process_scale/safety_ethics)
→ Multi-objective Comparator(`CandidateEvaluationVector`12 维,每维带
  mode/basis/source,广义 Pareto 支配,无加权总分)
→ Meta-review(跨 Reviewer 聚合 agreement/disagreement,绝不多数投票
  掩盖 critical finding)
→ Revision Controller(finding → RevisionTask → 真实调用问题4
  `portfolio_service.revise_candidate` 创建新版本,原版本不可编辑)
→ Human Gate(9 词汇表:approve_for_planning/approve_for_build/revise/
  request_more_evidence/request_model_run/return_to_diagnosis/reject/
  hold/stop,proposer 不能自批准)
→ 可返回问题3(真实创建新 `DiagnosisSession`)
→ append-only Memory 写回(`EvaluationMemoryEvent`,原始引用与解释/
  lesson 分列存储)
```

**独立性的诚实边界**:`context_independent`/`rubric_independent`/
`evidence_independent` 三层已实现(Reviewer 只读冻结后的正式对象、rubric
专找失败条件、证据独立重新解析知识库),`model_independent` 恒为
`False`——本轮 critic 是确定性规则引擎(与问题1-4全仓库既定模式一致,无
任何 service 层做实时 LLM 调用),`ScientificReview.shared_model_risk`
因此恒为 `True`,从不宣称已消除 same-model bias。

**Workflow Guard**:`harness/scientific_evaluation/gate_hooks.py` 挂入问题4
`governance_service.mark_planning_complete`/`record_human_decision` ——
未创建 `EvaluationCase` 的项目零行为变化(问题4原 43 个测试全通过),创建
后则强制要求科学 Human Gate 先行通过才能推进建造审批。

详见 `workflow/design/evolution/后端精修/问题05_实施报告.md`(仓库审计、
架构、8 篇文献映射、31 个新测试的完整证据)。

## 配置项

所有配置通过项目根目录 `.env` 文件或环境变量设置(环境变量优先):

| 配置项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `LLM_PROVIDER` | str | `deepseek` | 供应商预设名,见下方「切换模型供应商」 |
| `LLM_MODEL` | str | (空) | 模型名;不填用预设默认(deepseek → `deepseek-v4-pro`),其他预设必填 |
| `LLM_BASE_URL` | str | (空) | 覆盖 API 地址;`custom` 供应商必填 |
| `LLM_API_KEY` | str | (空) | 通用密钥覆盖;不填时读所选预设自己的密钥变量 |
| `DEEPSEEK_API_KEY` 等 | str | (空) | 各家自己的密钥变量:`DEEPSEEK_API_KEY` / `OPENAI_API_KEY` / `MOONSHOT_API_KEY` / `DASHSCOPE_API_KEY` / `ZHIPU_API_KEY` |
| `MAX_STEPS` | int | `30` | 单次运行最多多少步 LLM 调用 |
| `TOOL_TIMEOUT_S` | float | `60` | 工具执行默认超时(秒) |
| `LLM_TIMEOUT_S` | float | `120` | LLM 请求超时(秒) |
| `LLM_RETRIES` | int | `3` | 连接错误 / 429 / 5xx 的总尝试次数 |
| `LLM_MAX_TOKENS` | int | (不设置) | 传给模型的 `max_tokens`,不设则不传 |
| `TEMPERATURE` | float | (不设置) | 采样温度,不设则不传 |
| `HOST` | str | `127.0.0.1` | 监听地址(仅本机) |
| `PORT` | int | `8642` | 监听端口 |
| `SYSTEM_PROMPT` | str | 内置英文提示词 | Agent 的系统提示词 |

## 切换模型供应商

LLM 后端是一个供应商注册表(`harness/providers.py`),所有预设都走 OpenAI 兼容协议,切换只需改 `.env`、重启服务,代码零改动。

**切到某家预设供应商**(以 Moonshot 为例):

```bash
# .env
LLM_PROVIDER=moonshot
MOONSHOT_API_KEY=sk-xxxx
LLM_MODEL=kimi-latest        # deepseek 之外的预设没有默认模型,必须指定
```

内置预设:`deepseek`(默认,模型默认 `deepseek-v4-pro`)、`openai`、`moonshot`、`qwen`(阿里 DashScope 兼容模式)、`zhipu`。

**接入自建 / 本地端点**(vLLM、Ollama、各类 OpenAI 兼容网关):

```bash
# .env
LLM_PROVIDER=custom
LLM_BASE_URL=http://127.0.0.1:11434/v1
LLM_API_KEY=placeholder      # 端点不校验密钥时随便填一个占位
LLM_MODEL=qwen3:32b
```

**永久添加一家供应商**:在 `harness/providers.py` 的 `PROVIDERS` 表里加一行(名字、base_url、密钥环境变量名、可选默认模型)即可。

配置不完整时(密钥没填、模型没指定等),第一次发消息会在时间线上收到一条指明缺什么、该设哪个变量的错误提示;启动横幅和侧边栏也会显示当前供应商与模型,便于确认切换生效。

## 项目结构

```
agent-harness/
├── .env                  # 真实密钥(勿提交、勿打印)
├── .env.example
├── README.md
├── requirements.txt
├── main.py               # 入口:python main.py [--reload] [--host H] [--port P]
├── docs/SPEC.md          # 构建规格(权威契约)
├── harness/              # 框架本体
│   ├── config.py         # 配置加载
│   ├── providers.py      # LLM 供应商注册表(切换/新增供应商看这里)
│   ├── llm.py            # OpenAI 兼容协议的流式客户端
│   ├── agent.py          # 通用 Agent 循环(自由工具调用,未受 Workflow Engine 约束)
│   ├── events.py         # 事件契约与总线
│   ├── sessions.py       # 会话与 JSONL 持久化
│   ├── server.py         # FastAPI HTTP/WS 服务
│   ├── tools/            # 工具系统(@tool、注册表、加载器)
│   │   ├── builtin/      # 内置工具:calculator、clock
│   │   └── executor.py   # Workflow Engine 专用的工具执行层(allowlist/retry/幂等/溯源)
│   ├── workflow/         # Workflow Engine + Iterative Design Loop:阶段图、Gate、Controller
│   ├── evaluation/       # run_evaluator:多次运行一致性对比
│   ├── db.py             # SQLAlchemy engine/session + 字段不可变性守卫
│   ├── migrations.py     # 小型手写版本化迁移器
│   ├── bootstrap.py      # 导入全部 ORM 模型 + 执行迁移
│   ├── ids.py            # 共享 id/时间戳约定
│   ├── projects/         # Project、事件账本 ProjectEvent、IterativeCycleState
│   ├── memory/           # event_store(回放重建)、views、context_builder、knowledge_claims
│   ├── designs/          # DesignVersion、EngineeringDecision、genotype/decision diff、lineage、adapters
│   ├── constructs/       # Construct、GenotypeVerification、PhysicalStockRef
│   ├── experiments/      # ExperimentPlan/Run、DataAsset/Observation、ingestion/(解析器)
│   ├── analysis/         # AnalysisRun(计算可复现性清单)
│   ├── cell_state/       # BiologicalStateSnapshot、CellStateTrajectory、ModelVersion/Prediction/Residual
│   ├── learning/         # HypothesisVersion/FailureCase/LearningCycle 服务、outcome_classifier、strategy_router、redesign、policy_registry
│   ├── diagnosis/        # Bottleneck Diagnosis Loop:mechanism_graph、hypothesis_generator、
│   │   │                 #   evidence、assessor、evaluator、test_selector、execution_planner、
│   │   │                 #   decision_service、handoff、memory_recall、report、loop(18态控制器)
│   │   └── model_adapters/  # gem_fba(真实 cobrapy FBA)、vecoli/kinetic(诚实 unavailable)、registry
│   ├── engineering_design/  # Engineering Design Loop:handoff、strategy/portfolio_(generator|service)、
│   │   │                    #   decision(Pareto)、evaluators/(8 个规则评估器)、evaluation_service、
│   │   │                    #   build_test_planner、governance_service、counterfactual_service、
│   │   │                    #   design_version_bridge、outcome_service、memory_integration、loop(18态)
│   ├── scientific_evaluation/  # Evaluator & Scientific Critic:intake、claims、deterministic、
│   │   │                       #   evidence、model_eval、critic(独立科学审查)、comparator、meta_review、
│   │   │                       #   revision、human_gate、memory、diagnosis_return、gate_hooks、loop(15态)
│   └── api/              # FastAPI 路由(projects/designs/experiments/learning/diagnosis/
│                          #   engineering_design/scientific_evaluation)
├── workflows/synbio_v1/  # 阶段内复用的确定性推理模块(task_parser/retriever/diagnosis/...)
├── knowledge/            # DDR 知识库、工程动作库、必需基因参考表
├── tools/                # 你的工具放这里(自动发现)
│   ├── http_get.py
│   ├── read_file.py
│   ├── synbio_design_v1.py     # 旧:单次调用,无阶段状态(保留兼容)
│   └── synbio_workflow_run.py  # 新:Workflow Engine 控制的合成生物学设计流程
├── tests/workflow/       # Workflow Engine 单元/集成/生物学 benchmark 测试
├── tests/diagnosis/      # Bottleneck Diagnosis Loop 单元/集成/端到端/API 测试
├── tests/projects/       # DBTL 项目账本单元/集成/API 测试
├── tests/engineering_design/    # Engineering Design Loop 单元/集成/端到端/API 测试
├── tests/scientific_evaluation/ # Scientific Evaluation 单元/契约/集成/端到端/API 测试
├── web/
│   └── index.html        # 单文件前端
├── runs/                 # 会话数据(运行时创建,已 gitignore)
├── workflow_runs/        # WorkflowRun 断点快照(运行时创建,已 gitignore)
├── project_ledger.db     # DBTL 项目账本 SQLite 文件(运行时创建,已 gitignore)
└── workspace/            # 文件工具的沙箱目录(运行时创建,已 gitignore)
```

## HTTP & WS API 简表

| 路由 | 说明 |
|---|---|
| `GET /` | 前端页面 `web/index.html` |
| `GET /api/health` | `{"ok": true, "provider", "model", "tools"}` |
| `GET /api/tools` | 已注册工具列表(name / description / parameters / source) |
| `GET /api/sessions` | 会话列表(按创建时间倒序) |
| `POST /api/sessions` | 新建会话 |
| `GET /api/sessions/{id}` | 会话详情 + 全部事件;未知 id 返回 404 |
| `DELETE /api/sessions/{id}` | 删除会话;运行中返回 409 |
| `POST /api/sessions/{id}/messages` | 发送用户消息,body `{"content": "..."}`;接受后返回 202 `{"accepted": true}`;会话忙时返回 409;空内容返回 422 |
| `POST /api/sessions/{id}/stop` | 停止当前运行 → `{"stopped": true/false}` |
| `WS /ws/{id}` | 连接后先重放该会话全部历史事件,随后实时推送新事件;每 20 秒发一次 `{"type": "ping"}` |
| `GET /api/workflow-runs` | Workflow Engine 运行列表(run_id / status / current_stage,按创建时间倒序) |
| `GET /api/workflow-runs/{run_id}` | 完整结构化运行状态:`stage_records`、`gate_result`、`biological_state`、`engineering_decisions` 等;未知 id 返回 404 |
| `POST /api/workflow-runs/{run_id}/approve` | 人工审批通道,body `{"decision_id", "approver", "decision": "approved"\|"rejected", "risk_reason"}`;真正解除 `waiting_user` 阻塞,不只是前端提示 |
| `POST /api/projects` / `GET /api/projects` / `GET /api/projects/{id}` | 创建/列出/读取项目 |
| `GET /api/projects/{id}/status` / `.../status/from-ledger` | `ProjectStatusView`;后者只从事件账本回放重建,不读任何实时表,用于证明"账本才是真相" |
| `GET /api/projects/{id}/timeline` | 完整事件账本(分页字段:seq/event_type/entity_type/actor 等) |
| `GET /api/projects/{id}/lineage` | Design Lineage Graph(节点 + 父子边) |
| `GET /api/projects/{id}/context-bundle` | 当前 `ContextBundle`(结构化过滤 + token 预算,省略项如实记录) |
| `GET /api/projects/{id}/cycle` / `POST /api/projects/{id}/cycle/{action}` | 读取/推进 Iterative Design Loop 状态;非法跳转返回 409,Gate 拒绝返回 422 |
| `POST /api/designs` / `GET /api/designs/{id}` / `POST /api/designs/{id}/approve` | 创建/读取/批准 DesignVersion;提出者不能自批准(409) |
| `GET /api/designs/diff?a=&b=` | 结构化 genotype diff + decision diff |
| `POST /api/constructs` / `POST /api/constructs/{id}/verify` | 登记 Construct / 记录 genotype verification |
| `POST /api/experiments/plans` / `POST /api/experiments/runs` | 创建实验计划 / 记录实际执行 |
| `POST /api/experiments/ingest` | 上传 CSV(base64)→ checksum 幂等 → Data Identity Gate → QC → 生成 Observation |
| `GET /api/experiments/runs/{id}/observations` | 查看某次实验运行派生的 Observation |
| `POST /api/learning/hypotheses` / `.../hypotheses/revise` | 提出/修订假设(修订需先通过 Hypothesis Update Gate) |
| `POST /api/learning/failures` | 登记 FailureCase(9 类 failure_class) |
| `POST /api/learning/redesign` | 生成新 DesignVersion(必须通过 Redesign Gate:声明 retain/remove/add + 触发理由) |
| `POST /api/learning/knowledge-claims` / `.../promote` / `.../retract` | 提交/晋升/撤销 KnowledgeClaim(晋升需独立证据组 + 非本人复核) |
| `POST /api/diagnosis/sessions` / `GET .../{id}` | 创建/读取诊断 session |
| `GET /api/diagnosis/sessions/{id}/hypotheses` / `.../evidence` / `.../tests` / `.../decisions` / `.../audit-trail` / `.../report` | 查看假设、证据、判别测试、决策历史、状态审计轨迹、结构化报告 |
| `POST /api/diagnosis/evidence-links` | 登记 EvidenceLink(4 种关系强制枚举) |
| `GET /api/diagnosis/model-capabilities` | 查看各 Model Adapter 的真实/降级能力状态 |
| `POST /api/diagnosis/model-runs` | 触发真实模型计算(如 `gem_fba` 真实 FBA) |
| `POST /api/diagnosis/decisions/{id}/approve` | 人工审批 DiagnosisDecision 的 handoff |
| `POST /api/diagnosis/sessions/{id}/action/{action}` | 推进诊断状态机;非法跳转返回 409,Gate 拒绝返回 422 |
| `POST /api/engineering-design/handoff` | 把已门控的 DiagnosisDecision 转成 EngineeringDesignProject |
| `POST .../projects/{id}/objectives` / `.../confirm-objective` | 登记 primary_metrics/hard_constraints(空列表也需显式声明)/ 确认目标 |
| `POST .../projects/{id}/strategies` / `GET .../strategies` | 生成/查看 EngineeringStrategy |
| `POST .../projects/{id}/portfolio` / `GET .../candidates` / `GET .../candidates/{id}` | 生成/查看 DesignPortfolio 与 CandidateDesign |
| `POST .../candidates/{id}/revise` | 创建修订后的新版本(RedesignGate:禁止与父版本完全相同) |
| `POST .../portfolios/{id}/evaluate` / `GET .../candidates/{id}/evaluation` | 运行 8 评估器套件 + Pareto 决策 |
| `POST .../candidates/{id}/counterfactual` | 触发真实模型计算(复用问题3 model_adapters registry) |
| `POST .../candidates/{id}/build-test-package` / `.../projects/{id}/planning-complete` | 起草 Build/Test 计划 / 标记规划完成 |
| `POST .../projects/{id}/request-approval` / `.../candidates/{id}/human-decision` | 人工建造审批(proposer≠approver,409) |
| `POST .../candidates/{id}/bridge-to-design-version` | 桥接进问题2的持久化 DesignVersion |
| `GET .../projects/{id}/history` / `.../audit-trail` | 设计谱系历史 / 状态迁移审计轨迹 |
| `POST /api/scientific-evaluation/evaluations` | 开启评审:冻结上下文 → 跑完确定性/证据/模型/Critic/比较/meta-review 全流程 |
| `GET /api/scientific-evaluation/evaluations/{id}` | 读取 EvaluationCase 当前状态 |
| `POST .../evaluations/{id}/run-stage` | 重跑/重试该评审(用于恢复未完成的流程) |
| `GET .../evaluations/{id}/deterministic-results` / `.../evidence-assessments` / `.../model-records` | 查看确定性检查、8 维证据匹配、模型记录(含诚实 not_computed) |
| `GET .../evaluations/{id}/reviews` / `.../candidate-comparison` / `.../meta-review` | 查看各 Reviewer 报告 + finding、CandidateEvaluationVector/Pareto、MetaReviewDecision |
| `POST .../evaluations/{id}/revisions` / `GET .../version-history` | 提交修订(创建新 CandidateDesign 版本并重新评审)/ 查看版本与 finding 谱系 |
| `POST .../evaluations/{id}/human-decision` | 科学 Human Gate(9 词汇表;proposer≠approver,409) |
| `POST .../evaluations/{id}/return-to-diagnosis` | 真实创建新 DiagnosisSession(诊断竞争解释未排除时) |
| `GET .../evaluations/{id}/audit-trail` | 状态迁移轨迹 + 人工决策历史 |

WS 帧即事件 JSON:`{"seq", "type", "ts", "data"}`(不带 `seq` 的帧如 ping 可忽略)。事件类型包括 `user_message`、`run_started`、`llm_call_started`、`assistant_thinking_delta`、`assistant_delta`、`assistant_message`、`tool_call`、`tool_result`、`run_finished`、`session_meta`。

## 常见问题

**如何换模型或供应商?**
见上文「切换模型供应商」:同一家换模型只需设 `LLM_MODEL`;换供应商改 `LLM_PROVIDER` + 对应密钥;自建端点用 `LLM_PROVIDER=custom` + `LLM_BASE_URL`。改完重启服务生效。

**工具报错去哪看?**
两个地方:① 网页时间线上对应的工具卡片——出错时红色高亮并显示 `ERROR: ...` 信息(这也是模型看到的内容);② 服务终端日志——用户工具文件导入失败、工具执行异常都会记 warning。工具报错不会中断运行,模型会拿着错误信息决定下一步。

**会话数据存在哪?**
每个会话一个文件:`runs/{会话id}.jsonl`,追加写入元信息、消息和事件。服务重启时会自动加载回内存。

**如何清空历史会话?**
在网页侧边栏悬停某个会话点 ✕ 删除(运行中的会话需先停止);或者停掉服务后直接删除 `runs/` 目录下的 `.jsonl` 文件,重启即可。

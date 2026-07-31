---
name: extract-paper-experimental-design
description: 将用户目标、论文 PDF 或 DOI 转换为证据可追溯的实验设计知识；AI 必须完整阅读论文并主动识别论文实际研究的目标物种、目标菌株及其别名，而不是依赖用户预填。能力包括文献真实性、结构化实验设计、原文证据、质量与可复现性评价、跨论文比较，以及在目标系统信息充分时生成适配分析和候选 DBTL 工程计划。用于“抽取论文实验设计思路”“找出论文使用的菌株”“比较多篇论文的实验方案”“从文献形成可审计实验计划”“分析论文方法能否迁移到目标生物系统”等任务。Skill01–13 仅是内部工具，不应作为独立能力暴露给用户。
---

# 论文实验设计抽取

把本能力视为一个统一的、证据驱动且由人类治理的实验设计知识转换系统。上层 Agent 只调用一次“论文实验设计抽取”，不要要求用户选择或理解 Skill01–13。

01–13 是可组合工具，不是必须全部执行的固定流水线。根据输入、论文类型、目标系统和用户期望动态选择工具，避免为了跑完整编号而制造无意义结果。

## 核心原则

1. 保留论文事实、模型推断、迁移建议和工程候选方案之间的边界。
2. 每个“论文报道”的结论必须绑定可定位的原文证据。
3. 缺失信息标记为 `unknown`，禁止根据常识补写为论文事实。
4. 综述、方法论文和原创研究使用不同的抽取粒度；不要把综述引用的他人实验伪装成当前论文完成的实验。
5. 没有明确目标生物系统时，停止于证据绑定、质量评价或跨论文比较，不强行执行适配和工程计划。
6. AI 生成的实验计划始终是候选计划；未经人工审核，不得描述为已批准或可直接执行。
7. 低证据覆盖、关键条件缺失或来源冲突时，降低置信度并进入人工复核。
8. 把“论文实际研究的菌株”和“用户希望迁移到的目标菌株”作为两个独立字段。论文菌株必须由 AI 通读全文后主动寻找；用户未填写目标系统不能成为跳过菌株识别的理由。
9. 先判定论文类型，再选择抽取 Schema。论文类型未确定前，禁止生成实验组、对照、培养条件、剂量、重复和工程计划。
10. 同时验证“证据是否真实存在”“证据是否属于当前研究主体”“证据是否支持该字段语义”。原文出现某个值不等于该值可进入任何相同单位的字段。
11. 主动检查正文、公式、图表、图注、补充材料和作者代码之间的一致性；论文内部存在冲突时不得替作者静默选择答案。
12. 不压扁对象层级、流程阶段和量词限定域：设计值、实施值、最终实测值，材料装配、细胞导入、表型验证，以及局部/整体成功率必须分开保存。
13. 论文标签不等于生物学本体。`wild type`、`control`、`final strain` 等必须同时保存 `paper_label`、真实角色和限定说明；工程化亲本不得因图中简称而归为天然野生型。
14. 单独构建或单独验证不得合成为组合构建；“分别删除 A、B、C”不能输出为 `ΔA ΔB ΔC`，除非同一对象的组合基因型有直接证据。
15. 把摘要、标题或 Discussion 的高层 `paper_claim` 与图表直接支持的 `direct_observation` 分开；“完全、所有、定量、正交、无差异”等强词必须附检测限、对象、条件、时间窗和未测试范围。
16. 图表是正式证据源，不是正文附属品。标记 `unknown`、`requires_supplement` 或阻断前，必须视觉检查主图的图例、轴、点、热图单元格、网络边、构建标签和图注；不得因文本未逐项复述而忽略主图可恢复的信息。

## 输入判断

接受以下一种或多种输入：

- 本地论文 PDF；
- DOI 列表；
- 已清洗的 Markdown 或结构化论文文本；
- 用户研究目标和自动检索要求；
- 已有中间 Artifact 或检查点；
- 目标生物系统、菌株、表型和工程目标。

先判定用户要的是哪一级结果：

- **论文内抽取**：还原单篇论文的研究问题、变量、分组、对照、流程、测量和结果。
- **多论文比较**：比较实验路线、条件、证据强弱和可复现性。
- **目标系统适配**：判断论文方法迁移到指定系统时哪些内容可直接采用、需修改或不可迁移。
- **工程计划**：在证据和目标信息充分时形成候选 DBTL 方案。

目标系统缺失时不要默认 `E. coli K-12`。只有用户明确要求 K-12 或提供对应目标信息时，才运行 K-12 专用适配工具。这条限制只适用于后续迁移目标，不适用于论文自身菌株的识别；论文自身的物种和菌株必须从全文中寻找。

## 内部工具编排

按需使用以下工具，工具编号只用于内部追踪：

| 工具 | 内部职责 | 使用条件 |
|---|---|---|
| 01 | 解析用户目标、约束和检索策略 | 所有新任务 |
| 02 | 自动检索候选文献 | 用户未提供论文或 DOI |
| 03 | 验证论文身份、DOI 和来源真实性 | 自动检索或 DOI 输入 |
| 04 | 获取有权访问的 PDF | DOI 或合法开放获取来源 |
| 05 | 将 PDF 解析为保留章节、段落、图表位置的结构化文档 | 输入含 PDF |
| 06 | 清洗 Markdown，去除版式噪声并保留定位锚点 | PDF 解析后或输入为脏 Markdown |
| 07 | 抽取实验设计字段和实验逻辑 | 存在可用正文 |
| 08 | 将每个报道字段绑定原文证据 | Skill07 之后必须执行 |
| 09 | 评价完整性、证据、实验逻辑和可复现性 | Skill08 之后必须执行 |
| 10 | 比较并适配 E. coli K-12 | 仅当目标明确为 K-12 |
| 11 | 生成候选 DBTL 工程计划 | 目标、证据和适配信息充分 |
| 12 | AI 自检、冲突检查、人工复核和审计 | 存在推断、风险、冲突或候选计划 |
| 13 | 生成前端或 API 展示结构 | 用户或宿主需要结构化展示 |

默认依赖关系：

```text
01
├─ 自动检索：02 → 03 → 04
├─ DOI：03 → 04
└─ 本地 PDF：05

05 → 06 → 07 → 08 → 09
                       ├─ 仅抽取/评价：结束
                       ├─ 多论文比较：聚合比较
                       └─ 明确 K-12：10 → 11

任何需要治理的分支 → 12
需要前端结构 → 13
```

## 执行流程

### 1. 建立任务契约

记录：

- `task_id`
- 用户原始要求
- 输入文献与来源类型
- 目标系统和菌株
- 目标表型或工程目标
- 需要的结果层级
- 质量要求
- 是否需要人工审核

若目标系统仅影响后半段流程，可先完成论文内抽取，不因目标缺失阻断 Skill05–09。

### 2. 获取和规范化论文

- 对本地 PDF，直接从 Skill05 开始。
- 对 DOI，先验证 DOI 与论文元数据，再获取合法可访问的 PDF。
- 对自动检索结果，保留候选、排除原因、验证状态和来源。
- 不绕过付费墙、反爬机制或访问控制。
- 为章节、段落、图、表和补充材料建立稳定定位标识。
- 对含矩阵、热图、多面板、谱图或构建示意的页面进行视觉渲染；文本抽取不能替代图像检查。记录哪些字段来自图像读取，并保留面板坐标或行列标签。

### 3. 判断论文类型

区分：

- 原创实验研究；
- 方法或协议论文；
- 综述；
- 数据论文；
- 计算或模拟研究；
- 观点、社论或非实验材料。

对原创研究，抽取该论文实际实施的实验。

对综述，输出“文献总结的设计模式”和“被引用研究的案例”，不得声称综述作者实施了这些实验。若用户需要可执行实验，应继续追溯原始研究。

把论文类型判断设置为硬门控 `ArticleTypeGate`，输出：

```json
{
  "article_type": "primary_research|review_article|systematic_review|meta_analysis|protocol|methods_paper|case_report|perspective|other",
  "is_primary_experimental_study": false, "contains_original_experiment": false,
  "recommended_schema": "primary_experiment_schema|review_synthesis_schema|protocol_schema|methods_schema",
  "confidence": 0.0, "evidence": []
}
```

至少使用首页文章标签、标题与摘要、Methods 的实际内容、结果组织方式和数据来源共同判断。若证据冲突或置信度不足，先进入人工复核，不得默认按原创实验论文处理。

执行路由：

- `is_primary_experimental_study = true`：使用原创实验 Schema。
- `review_article / systematic_review / meta_analysis`：禁止生成“本文自身”的实验组、对照、培养条件、剂量、实验重复和统一实验参数；改用综述综合 Schema。
- `protocol`：抽取计划中的方法和预设分析，不把预期结果当作已观察结果。
- `methods_paper`：区分方法开发、验证实验和应用示例。
- `perspective / commentary`：抽取论点、证据基础与研究建议，不生成实验事实。
- 类型不适配的字段标记 `not_applicable`，不得标记为普通 `unknown`。

综述综合 Schema 至少包含：

```json
{
  "review_objective": null, "review_questions": [],
  "database_sources": [], "search_strategy": [], "date_range": {},
  "inclusion_criteria": [], "exclusion_criteria": [],
  "screening_process": {}, "data_extraction_process": {},
  "synthesis_method": null, "meta_analysis": false,
  "included_studies": [], "evidence_summary": [],
  "limitations": [], "research_gaps": [], "conclusions": []
}
```

把综述中的 `performed in duplicate`、双人筛查、双人数据抽取和共识处理记录在 `review_process`，不得映射成湿实验的技术重复。

### 4. 全文阅读并解析目标菌株

在抽取其他实验字段前，完整阅读可获得的论文全文，不得只读摘要、关键词、搜索命中段落或 Methods 的局部片段。至少检查：

- 标题、摘要和关键词；
- Introduction 中的研究对象定义；
- Materials and Methods、Experimental Procedures、Strains、Organisms、Cell culture、Media 等章节；
- 表格、图注、补充材料和菌株构建示意图；
- Results 中用于区分实验组的菌株名称；
- 数据可用性、菌株资源、质粒或材料清单；
- Discussion 中对宿主或底盘的限定。

主动搜索并归一化以下线索：

- 学名、旧名、缩写和常见名；
- 菌株编号、亚株、血清型、克隆型和实验室株；
- 野生型、亲本株、对照株和工程株；
- 基因型、敲除/过表达标记、质粒和抗性标记；
- 保藏中心编号，如 ATCC、DSM、CGSC、NCTC；
- `E. coli` / `Escherichia coli`、`K-12` / `MG1655` / `BW25113` 等别名或谱系关系；
- “derived from”“background”“parental strain”“host strain”“wild type”等上下文关系。

对每个候选菌株建立：

```json
{
  "paper_organism": "", "paper_strain_raw": "", "paper_strain_normalized": "",
  "role": "target|parental|control|engineered|host|other", "paper_label": "",
  "lineage_or_engineering_context": "", "combination_status": "",
  "genotype": "", "evidence": [],
  "status": "reported|inferred|unknown|not_applicable",
  "confidence": 0.0, "reasoning": ""
}
```

判定规则：

1. 原文明示完整菌株名时标记为 `reported`，并绑定 Methods、表格、图注或补充材料中的直接证据。
2. 原文只给亚株或实验室株，而谱系可由论文内部信息可靠确定时，可归一化为完整名称，但标记为 `inferred`，同时保留原始写法和推断链。
3. 同一论文出现多个菌株时，不要只返回第一个命中；按实验角色、实验组和研究目的区分主目标菌株、亲本株、对照株、宿主株和工程株。
4. 参考文献中的菌株不能自动计入当前论文实验对象，除非正文明确说明当前研究使用该菌株。
5. 全文查找后仍未找到时才标记 `unknown`，并列出已检查的章节和缺失原因。
6. 若论文不是微生物或细胞系研究，标记 `not_applicable` 并说明实际研究对象；不得因此把整个抽取任务判为失败。
7. 不要要求用户先提供目标菌株，AI 应先完成全文识别；只有存在多个同等可能且全文无法消歧时，才把候选及证据交给用户确认。
8. `wild type` 等论文内简称只作为 `paper_label`；另行判断其是天然分离株、标准实验室株、减缩/工程化亲本，或仅是“未接受本轮干预”的对照。前端不得丢弃这一限定。
9. 分别构建的突变株、删除株或处理组各建独立对象；只有论文直接展示组合基因型和对应验证时才建立组合对象，否则 `combination_status = not_demonstrated`。
10. 同一菌株家族的标题简称不能覆盖具体实验宿主。分别保存 `strain_family` 和 `exact_experimental_host`；若后者只在补充表可确定，标记 `requires_supplement`。单删比较株不得默认与某亲本完全等背景，仅记录直接证实的删除与功能角色。
11. `WT`、`control`、`canonical` 等标签可同时修饰菌株、基因、质粒、移动元件或解码规则。先判定 `object_type`，再解释标签；功能定义可由主文支持时不要擅自补全精确基因型。

必须在输出中分别保留：

- `paper_target_strains`：论文实际研究或使用的菌株，由全文识别；
- `user_target_system`：用户希望迁移或设计的目标系统，可能为空；
- `target_system_adaptation`：两者之间的迁移分析，仅在用户目标明确时生成。

### 5. 抽取实验设计

尽可能结构化以下内容：

- 研究问题与假设；
- 生物系统、材料、论文目标菌株、亲本株、对照株、工程株或模型；
- 干预、工程方法和关键操作；
- 实验组、阴性/阳性/基准对照；
- 自变量、因变量和控制变量；
- 培养、处理、剂量、时间和环境条件；
- 生物学重复与技术重复；
- 测量方法、仪器和分析方法；
- 主要结果、判定标准和作者解释；
- 实验步骤之间的因果与依赖关系。

将每个字段标记为：

- `reported`：原文明确报道；
- `inferred`：根据原文结构推断；
- `unknown`：未找到；
- `not_applicable`：对该论文类型不适用。

避免只靠关键词匹配。诸如 `control`、`wt`、温度和时间出现在参考文献或背景段落时，不得自动当作当前论文的实验条件。

### 5.1 隔离研究主体和来源层级

给每个事实分配唯一主体：

- `current_article`：本文作者实际完成的研究；
- `included_study`：综述正式纳入的独立研究；
- `background_citation`：背景或讨论中引用的研究；
- `author_inference`：综述作者的综合判断；
- `model_inference`：AI 的分析。

禁止跨主体合并。综述中的每项实验参数必须保留 `source_study`，并按独立 Study 对象保存。表格每一行通常代表一个独立研究，必须保持行内材料、工艺、参数、结局和文献引用的关系，禁止按列汇总成脱离研究来源的数组。

被引研究对象至少包含：

```json
{
  "source_study": "", "study_type": "",
  "materials_or_biological_system": {}, "experimental_design": {},
  "parameters": [], "measurements": [], "outcomes": [],
  "source_level": "secondary_report_in_review",
  "evidence": []
}
```

来自综述二手描述的内容不能提升为原始研究级证据；需要形成可执行实验时，优先获取并核查原始论文。

### 5.2 参数语义解析

禁止仅凭数值、单位或关键词决定字段。每个参数必须同时绑定：

```json
{
  "raw_text": "", "value": null, "unit": "",
  "parameter_type": "", "process_step": "",
  "material_or_system": "", "source_study": "",
  "source_location": {}, "status": "reported|inferred|unresolved"
}
```

根据局部句子、段落主题、章节、表头、同行单元格、图注和研究领域共同消歧。无法确定语义角色时放入 `unresolved_parameters`，不得塞入最接近的字段。

设置以下最低限度的负例规则：

- `wt.%`、`wt%`、`weight percent` 表示质量百分比，不等于 `WT` 或 `wild type`；只有生物学语境中的 `WT strain/cells` 才可作为野生型。
- `glycerol binder` 或 `water-glycerol binder` 是黏结剂体系，不是碳源。
- 烧结、干燥、固化、灭菌、退火和热处理温度不是培养温度。
- 孔径、层厚、支架尺寸、缺损尺寸、图像比例尺、浓度和剂量不得互相混用。
- `1980s`、`1990s` 等年代不是持续时间；OCR 断裂的 `0 s` 等值必须复核。
- 检索 `in duplicate`、双人筛查或双人抽取不是生物学或技术重复。
- `control` 只有同时存在明确比较对象、实验主体和分组语境时才能成为对照组。

### 5.3 实验实例与范围约束

先建立 `experiment_id`，再把菌株、变量、培养基、参数、对照、重复、测量和结果挂到同一实验实例。必要时增加 `parent_experiment_id`、`process_stage` 和 `scope_domain`。禁止创建论文级的抽象 `control`、统一培养条件或统一重复数。

每个实验实例至少记录：`purpose`、`host`、`intervention`、`conditions`、`control`、`replicates`、`readout`、`analysis`、`outcome`、`evidence`。信息只在主文中写为 “LB or M9”等不完全形式时，标记 `incomplete_condition_binding`；不得凭表型常识选择其中一个培养基。同一图或段落包含不同构建、修复方案、克隆集合、anticodon、剂量、时间点或验证层级时，拆成子实验；`12/16`、`2/7` 等比例必须绑定各自分母所代表的对象，不得合并为一个成功率。

处理范围词时保留原始量词和限定域。“single round of selection”若实际包含多次传代或连续稀释，应解释为一次 selection campaign，而不是一次培养、一个时间点或不传代。诸如“12 个重构候选均提高产量”只能绑定到该 12 个候选、该生产背景和该条件，禁止扩展为整个文库。论文称“35 steps”时先记录它限定的区段、成功步骤类型和上下文；不得改写为项目总实验次数，未报告的总尝试数保持 `unknown`。

对照必须实例化，例如 `preselection population`、`nontargeting control`、`mutant vs nontargeting control`、`synonymous-mutation background`。只有具体实验明确使用 WT 时才建立 WT 对照。

对多阶段工程分别记录 `design`、`physical_assembly`、`host_integration_or_replacement`、`sequence_verification`、`phenotype_validation`。某阶段“顺利/成功”的数量只能支持该阶段；DNA/BAC 装配成功不得自动变成细胞内替换成功。对设计对象同时保留 `initial_design`、`revised_design`、`implemented_design` 和 `final_verified_product`；设计长度、设计位点数不能无证据复制到最终产物字段。

同一构建包含多个工程步骤时按目的拆开，例如“全 ORF 密码子压缩”与“在复制/必需基因中重新插入正交密码子”分别记录；前者移除不兼容位点，后者建立对特定解码器的依赖，不得合并成一个笼统 recoding 操作。

比值必须记录数学对象和方向，例如 `doubling_time_ratio = Syn61/MDS42`；避免“慢 1.6 倍”。若原始量是倍增时间，不将其改写为生长速率，除非给出公式和计算来源。

对谱系和进化实验记录 `comparison_reference`、`lineage_interval`、`accumulated_across_lineage` 和 `attribution_status`。终株“相对祖先有 N 个突变”不能归因于最后一轮进化、某次删除或某个选择阶段，除非逐轮样本支持。区分定向设计、构建伴随变化和进化产生的变化；新出现的目标位点或密码子不等于作者有意设计、恢复功能或已知无害。

重复类型使用 `biological_replicates`、`independent_culture_replicates`、`technical_replicates`、`recovered_colonies_or_clones`、`independent_events_confirmed`、`cells_or_fields_sampled`、`representative_display` 或 `unknown`。论文只写 `replicate cultures` 时优先标记 `independent_culture_replicates`，可记录 `biological_independence = likely`，但不得声称作者明确称其为 biological。两个回收菌落不能自动称为两个独立逃逸事件。图注对“all experiments”给出重复数时，另行记录每种读出是否均独立采集；一张展示的质谱不能自动证明全部重复谱图均可获得。

若图中每条件清晰显示 N 个点而图注未定义重复类型，记录 `displayed_observations_per_condition = N`、`replicate_type = unresolved`，并请求 Methods 确认；不得把可见点数完全丢弃，也不得直接升级为 biological replicates。区分数据点、误差线、叠加技术点和示意符号。

### 5.4 跨模态一致性与方法冲突

逐项对照正文描述、显示公式、表格、图注、坐标标签、补充材料、Reporting Summary、Source Data 和作者代码。图中出现但 Methods 未解释的分析工具也必须记录，例如差异表达图标注的软件。

发现冲突时输出：

```json
{
  "status": "source_internal_inconsistency",
  "topic": "", "prose_interpretation": "", "equation_or_figure_interpretation": "",
  "impact": "", "requires_manual_review": true
}
```

公式正文说法与排版公式不一致时，禁止自行改写成唯一公式或据此重算。优先核查 HTML/MathML、Source Data、代码和前序方法论文；未消歧前阻断精确复现。

数字不一致时先尝试语义分层，不直接判定算术矛盾：区分初始设计计数、修订后实施计数、最终验证计数及取整值。即使两个数值的差等于已报告修订数，也不得推导每个差值代表“未完成位点”，除非逐项清单支持。输出 `value_role`、`scope`、`source_location`、`reconciliation_status` 和所需核对附件。

对批量构建建立“对象 × 验证阶段”矩阵，例如 `designed/encoded`、`expression_tested`、`condition_dependent`、`identity_confirmed`、`purified`、`free_product_confirmed`、`cyclized`。总构建数不得复制成每个验证阶段的成功数；未提供逐项补充数据时保持单元格 `unknown` 并阻断成功率计算。

对主图中的热图或交叉矩阵逐格读取行列实体和定性结果。若主图已展示完整组合，则将 `matrix_identity`、`channel_count` 和 `qualitative_outcome` 标为 `reported_from_figure`；只有原始计数、检测限、误差、统计和精确序列继续依赖 Supplement。计数时拆解集合组成，例如“5 个互正交通道”可能是 1 个 canonical + 4 个 refactored，而非 5 个额外工程通道。

### 5.5 工程决策标注（DDR 标注）

对每条代表"为达成生产或表型目标而做的改造/干预"的实验记录（敲除、过表达、点突变、异源表达、启动子/RBS 工程、发酵条件调整等设计动作），在该实验记录上追加一个 `ddr_annotation` 对象，把这条改动放回其决策链位置：想产什么 → 观察到什么 → 提出什么假设 → 拿什么证据 → 做了什么改动 → 验证结果 → 可迁移到其他产物的规则。这一标注只服务于下游决策记录（DDR）与规则库的转换，不改变本文档其余章节已有的抽取、证据绑定和置信度规则。非工程干预的实验记录（纯观测、纯表征、方法学验证等）不需要此标注。

```json
{
  "design_action": "M0|M1|M2|M3|M4|M5|M6|M7|M8|M9|M11",
  "design_action_rationale": "",
  "trigger_observation": "",
  "evidence_grading": "硬|软",
  "evidence_grading_rationale": "",
  "reason_nature": "机理推断|文献类比|现成可得|筛选得来|事后合理化存疑",
  "reason_nature_rationale": "",
  "generalizable_rule": null,
  "alternatives_considered": []
}
```

字段含义与判定纪律：

- `design_action`：这步改动对应的设计动作类别——M0 意图框定、M1 通路解析、M2 前体与还原力供给、M3 解除调控、M4 限速酶识别与工程、M5 竞争/旁路通量阻断、M6 表达平衡、M7 动态调控、M8 副产物与毒性管理、M9 发酵与过程、M11 集成筛选。无法确定时留空，不得为了填满字段而归到某个默认类别。
- `trigger_observation`：促成这一步改动的观察或推理，通常是上一步的实测结果或论文明确陈述的限制因素，不是论文摘要的笼统复述。参考反例：`"研究者敲除了 trpE"` 不合格；`"提高上游表达并未增产，提示存在反馈抑制"` 才是合格的触发描述。
- `evidence_grading`：硬 = 实测（结构、动力学、已验证的改造结果）或化学计量（理论得率、通量、基因必需性）；软 = 预测性工具输出（OptKnock 生长偶联预测、docking、ΔΔG、AlphaFold 结构预测等）。软证据必须在 `evidence_grading_rationale` 中注明"预测性，需实测确认"，不得与实测证据同权处理。
- `reason_nature`：如实反映论文陈述或暗示的改造理由，**默认不是"机理推断"**。只有论文文本明确给出机制性解释（反馈/前馈抑制、别构调控、结合位点、动力学参数、转录阻遏等）时才标"机理推断"；论文明确说"参照某文献做法"时标"文献类比"；论文明确说明是使用现成菌株、试剂盒、质粒库或 Keio 敲除库中已有的构建时标"现成可得"；论文明确来自随机诱变、定向进化或高通量筛选结果时标"筛选得来"；论文没有给出清晰的机制性理由、或给出的理由更像是对已有结果的事后解释而非驱动决策的原因时，如实标"事后合理化存疑"——这是允许且预期会出现的诚实结果，不是抽取失败，不得为了让这一步看起来"更有道理"而拔高成"机理推断"。
- `generalizable_rule`：只有当 `reason_nature` 为"机理推断"或"文献类比"时才允许填写这个可迁移到其他产物的启发式规则；`reason_nature` 为"现成可得"、"筛选得来"或"事后合理化存疑"时，此字段必须为 `null`——即使能编出一条听起来合理的规则，也不得填写。伪造出的机制性规则会污染下游规则库，其代价高于留空。
- `alternatives_considered`：论文中提到但被放弃的备选方案及放弃原因，没有则留空数组，不得编造。

任何字段无法从原文确定时留空或标记为空，不得为了让这个对象看起来完整而编造内容。

### 6. 绑定证据

每条证据至少包含：

- 原文摘录；
- 章节；
- 段落、图或表标识；
- 来源论文标识；
- 支持的结构化字段；
- 证据类型；
- 置信度。

优先级通常为：

```text
Methods / Protocol / Supplement
> Results / Figure / Table
> Abstract
> Introduction / Discussion
> References
```

参考文献条目只能证明“该来源被引用”，不能直接证明当前论文执行了其中的实验。

证据绑定必须同时通过三项检查：

1. **存在性**：摘录确实出现在可定位原文中；
2. **归属性**：摘录属于当前论文、某个被纳入研究或背景引用中的哪一主体；
3. **语义支持**：摘录支持目标字段的科学含义，而非仅包含相似词或单位。

证据只通过存在性、但归属或语义失败时，属于“错误归因风险”，不得标为 `reported`。

菌株字段的证据优先使用 Methods、菌株表、材料表、图注和补充材料。摘要或 Introduction 中的物种名称只能支持物种层级，通常不能单独支持具体菌株层级。

将结论拆成 `direct_observation`、`author_interpretation`、`model_inference` 和 `causally_validated`。作者使用 `likely/could/suggested/might` 的机制解释不得提升为已验证因果链。表达、ATP、产量或富集变化是观察；膜稳定性、通量重分配、磷酸化机制等若无直接干预验证，应标记为推断。

所有结论增加 `tested_scope` 与 `excluded_generalizations`。某质粒的额外拷贝在特定条件下未救援表型，只支持该构建和条件；不得排除其他剂量、表达水平、相关因子或环境。阈值陈述与统计显著性分开：例如“共同定量蛋白变化均未超过 1.16-fold”不能改写成“所有蛋白均无统计差异”。

把“未检测到有效读取/传播/表达”等表述绑定检测方法和检出限；不得改写为绝对零事件。`quantitative incorporation` 只绑定作者实际分析的纯化产物、位点和方法，不等于全细胞蛋白组 100% 准确、无误掺入或所有正交对无串扰。对病毒抗性等强结论增加 `escape_or_long_term_evolution_tested`，未做长期适应实验时明确为 `false`。

对统计方法只报告作者实际使用的程序与假设。bootstrap CI、`μ ± 2σ` 和正态假设下的近似 P 值应分别记录；不得合并解释成标准、校正后的假设检验。必要时标记 `authors_significance_heuristic`。

### 7. 评价质量

至少评价：

- 字段完整性；
- 证据覆盖率与来源质量；
- 实验逻辑完整性；
- 分组、变量和对照质量；
- 流程完整性；
- 可复现性；
- 方法学限制；
- 信息缺失风险；
- 解释和迁移风险。

额外评价菌株识别质量：

- 是否完成全文覆盖；
- 是否同时识别主目标、亲本、对照和工程株；
- 是否保留原始名称与归一化名称；
- 是否存在只凭物种名推断具体菌株的问题；
- 是否把参考文献菌株误绑定到当前论文；
- 菌株结论是否有直接证据和可复核推断链。

评分必须附理由和缺失项。不要把“所有已抽取字段都有证据”等同于“论文信息完整”；大量字段为 `unknown` 时，整体质量仍应降低。

把 QC 设为最终对象前的硬门控：

```text
若 evidence_supported == false：
    从 final_experimental_design 移除该值
    status 不得为 reported；confidence 不得高于 0.5
若 source_attribution_valid == false：
    从当前研究对象移除该值
    保留在正确的 included_study 或 background_citation 下
若 semantic_role_valid == false：
    移入 unresolved_parameters
    禁止用于实验计划
若 ArticleTypeGate 不是 primary experimental study：
    original_experimental_design = null
    使用文章类型专用 Schema
若出现 S4 级错误：
    整篇结果标记 REVIEW_REQUIRED
    禁止进入适配、工程计划和前端“可执行方案”展示
若存在公式冲突、关键培养条件缺失或补充材料缺失：
    概念性摘要可放行
    精确复现、菌株重建、文库再合成、采购清单、SOP 和自动 DBTL 必须阻断
```

主文将关键方法、最终序列/基因型、完整构建路线、引物、选择条件或分析流程指向 Supplementary Methods/Data，而附件当前不可用时，将依赖这些信息的用途直接标记 `blocked_pending_supplement`，不能仅列为普通 review。概念设计可继续，但必须列出缺失附件及每份附件阻断的具体字段。

Supplement 门控必须字段级执行，不能覆盖主图已支持的定性事实。主图可恢复系统身份、完整组合矩阵或每条件可见点数时照常抽取；只把精确序列、原始数值、检测限、重复类型、统计或未展示条件标为 `requires_supplement`。每个阻断项同时填写 `available_from_main_text_or_figure` 与 `still_missing`，防止过度阻断。

把“必需”分为 `constitutively_essential`、`conditionally_essential_under_selection` 和 `author-described_essential_role`。抗生素或其他选择使报告/抗性基因成为条件性必需时，必须记录选择条件和撤除选择后的状态；不得称为永久基因组必需性。

复杂化学、环化、切割、进化控制或多步装配可输出概念机制，但若主文只给示意图，必须把“概念路线”与“可执行反应机制/条件”分开；后者在缺少补充方法时保持阻断。

S4 错误包括：虚构实验组或对照、把非生物过程参数作为培养条件、跨研究拼接成不存在的实验、证据已判不支持仍输出为高置信 `reported`。

治理输出必须按用途分级，而不是只给全局 `blocking`：

```json
{
  "scientific_design_summary": "allowed|review|blocked", "mechanism_summary": "allowed|review|blocked",
  "exact_reproduction_protocol": "allowed|review|blocked", "strain_reconstruction": "allowed|review|blocked",
  "library_resynthesis": "allowed|review|blocked",
  "automated_DBTL_plan": "allowed|review|blocked"
}
```

### 8. 按条件扩展

进行多论文比较时：

- 对齐相同研究问题下的材料、干预、条件、测量与结果；
- 区分一致证据、互补证据和冲突证据；
- 不因研究系统不同而直接合并效应；
- 给出最值得复用的设计模式及其证据边界。

进行目标系统适配时：

- 明确可直接迁移、需要修改、不能迁移和证据不足的部分；
- 说明宿主差异、尺度差异、培养环境、检测体系和安全约束；
- K-12 专用工具只处理 K-12，不应用于骨材料、动物模型或其他无关系统。

生成工程计划时：

- 将证据支持与 AI 建议分栏；
- 给出目标、构建、培养、测量、判据、风险和验证步骤；
- 给出失败分支和下一轮迭代逻辑；
- 将计划状态标记为候选并送交治理。

### 9. 治理与恢复

使用工作流状态：

```text
CREATED → RUNNING → WAITING_REVIEW → COMPLETED
                  ↘ FAILED
```

内部工具状态使用：

```text
PENDING | RUNNING | SUCCESS | WARNING | FAILED |
BLOCKED | REVIEW_REQUIRED | SKIPPED
```

区分运行级与论文级状态。检索规范、跨论文比较、工程计划和前端视图属于运行级；
论文验证、PDF、解析文本、实验设计、证据和质量报告属于论文级。批量任务中一篇论文
失败不得回滚或阻断其他论文，除非失败论文是用户指定的必需证据源。

每个工具输出都保存为带 `artifact_id`、版本、输入哈希、生成工具、时间和 provenance
的 Artifact。Artifact 写入前必须同时通过 Schema 校验和该工具的语义自检；校验失败
的候选输出只能进入错误日志或复核区，不得覆盖最后一个有效版本。状态推进必须发生在
有效 Artifact 持久化之后，避免出现“状态成功但产物缺失”。

恢复遵循幂等原则：

1. 根据输入哈希和已有成功 Artifact 跳过未变化的已完成工具；
2. 从首个 `FAILED`、`BLOCKED`、`REVIEW_REQUIRED` 或缺少有效 Artifact 的工具继续；
3. 重试时保留旧版本、错误类别、尝试次数和本次变更输入，不原地改写审计记录；
4. 网络或临时解析错误可有限重试；身份验证失败、付费墙、关键补充材料缺失和来源内部
   冲突应转为明确的等待/复核状态，不得用猜测值“修复”；
5. PDF 获取失败时允许人工上传后续跑；单篇论文终止时保留终止原因并继续处理其余论文。

文件系统路径不得直接使用含 `: / \` 等字符的 DOI 或外部标识。分别保存原始
`paper_id` 与安全目录名；后者只用于存储，禁止由目录名反推论文身份。

人工复核应优先检查：

- `inferred` 字段；
- 低置信度证据；
- 参考文献误绑定风险；
- 多来源冲突；
- 高风险迁移建议；
- 候选工程计划。

## 统一输出

根据实际执行内容返回以下字段的适用子集：

```json
{
  "summary": {}, "article_type_gate": {},
  "literature_candidates": [], "validated_papers": [],
  "paper_target_strains": [], "experimental_designs": [],
  "review_synthesis": {}, "included_studies": [],
  "unresolved_parameters": [],
  "source_internal_inconsistencies": [], "evidence_map": {},
  "quality_report": {}, "cross_paper_comparison": {},
  "target_system_adaptation": {},
  "engineering_plan": {},
  "governance": {},
  "frontend_view": {},
  "artifacts": [],
  "tool_states": {},
  "tool_logs": [],
  "errors": []
}
```

不适用的阶段应标记为 `skipped` 并说明原因，不要以缺失目标为由把已经成功的论文抽取结果整体标记为失败。

## 面向用户的交付

先给结论，再给证据和限制。至少说明：

1. 处理了哪些论文及其类型；
2. AI 通读全文后识别出的目标物种、目标菌株、亲本株、对照株和工程株；
3. 抽取出哪些实验设计或设计模式；
4. 哪些菌株与实验字段属于原文事实，哪些属于归一化或推断；
5. 证据覆盖、缺失信息和质量风险；
6. 哪些工具被跳过以及原因；
7. 是否需要人工复核；
8. 完整 JSON、Markdown 报告或其他 Artifact 的保存位置。

不要把内部编号作为主要用户界面。只有在排查失败、解释审计链或开发模块时，才展示具体工具编号。

---
name: distill-biological-knowledge
description: 将教材、专著、指南、实验手册、权威数据库条目和高质量综述转化为证据可追溯、区分来源事实与模型推断、支持中英文展示并可供 Agent 检索、推理、审计的生物学知识对象——包括概念、机制、工程原则、决策规则、设计模式、验证策略和失败模式。能力包括来源验证、章节结构解析、抽取范围判断、基础知识抽取、条件化工程原则蒸馏、决策规则与决策树生成、设计模式/验证策略/失败模式抽取、证据绑定与硬门控审计、跨来源融合与冲突管理、与“论文实验设计抽取”产物的案例连接、质量治理、知识图谱与前端/Agent 检索适配。内部 Step01–13 仅是动态编排的执行步骤，不应作为独立 Skill 暴露给用户。
---

# 生物学知识蒸馏 (Biological Knowledge Distillation)

把本能力视为一个统一的、证据驱动、双语支持、由人类治理的生物学知识蒸馏系统。

上层 Agent 只调用一次"生物学知识蒸馏"，不要求用户选择或理解 Step01–13。

Step01–13 是内部可组合执行步骤，不是独立 Skill，也不是必须机械执行的固定流水线。系统根据输入来源、任务目标、知识层级和输出用途动态编排；实现见 `biological_knowledge_distillation/workflow/engine.py` 的 `_plan()`。

## 0. 与"论文实验设计抽取"的关系

现有能力"论文实验设计抽取"负责 `论文 → 实验设计案例（ExperimentalCase）`。本能力负责 `教材/专著/指南/手册/权威资料 → 原理与工程知识（EngineeringPrinciple 等）`。二者不是同一模块，但共享一个 `KnowledgeObject` 公共层（见 `framework/unified-schema.json`），使 Step11 能够在不修改论文事实的前提下把工程原则与论文案例连接起来。不要求、也不应在两个模块之间做大规模重构；只在必要处新增最小化的共享 Schema/适配器。

首次实现前，应先扫描现有 Agent 基础设施（`paper_experimental_design_extraction/workflow`、`storage`、`skills/registry.py`）并复用其状态机/Artifact/日志/Schema 校验设计，不重复发明——本仓库中的 `biological_knowledge_distillation/workflow` 就是该设计的移植版本，而非另一套实现。

## 1. 核心原则

1. **不做教材摘要。** 输出必须回答：原理是什么、为什么成立、什么条件下成立、什么时候不能用、如何验证、有哪些替代策略、证据来自哪里。绝不输出"本章介绍了……"式总结。
2. **区分知识类型。** 至少区分 Concept、Mechanism、Biological Rule、Engineering Principle、Decision Rule、Design Pattern、Validation Strategy、Failure Pattern、Constraint、Tradeoff、Experimental Method Principle、Measurement Principle，不同类型不用同一 Schema 强行压平。
3. **区分知识来源与知识结论。** 每条结论必须保留 `source_type`、`source_id`、`source_location`、`source_scope`、`source_authority`、`evidence_text`、`evidence_role`。教材是证据来源，不是最终知识对象本身。
4. **区分原文陈述与模型蒸馏。** 使用分层字段：`source_statement` → `normalized_fact` → `derived_principle` → `model_synthesis` → `agent_recommendation`。禁止把模型总结的规则描述为教材原文明确提出的规则。
5. **知识必须有适用条件。** 不输出无条件强规则（"提高表达量可以提高产量"），必须写成 IF/ONLY IF 形式的条件化陈述。
6. **保存反例和限制。** 每条规则尽量同时记录适用条件、不适用条件、失败原因、反例、潜在副作用、替代方案、所需验证。
7. **中英文双语，但不得为了双语扭曲来源。** 最低字段：`name_zh/name_en/definition_zh/definition_en`，并分别保存 `source_language`、`original_text`、`translated_text`、`translation_status`、`translation_confidence`。机器翻译不得冒充来源原文。
8. **人类治理。** 跨来源融合、设计模式、决策树、工程建议、冲突裁决、适用范围扩展，全部标记为模型归纳并支持人工确认。

### 1.1 KnowledgeObject 公共层

所有知识资产（Concept、Mechanism、EngineeringPrinciple、DecisionRule、DesignPattern、ValidationStrategy、FailurePattern……）都继承同一组字段，定义在 `framework/unified-schema.json#/$defs/knowledgeObjectBase`：

```text
id, type, name_zh, name_en, aliases_zh/en, statement{source_statement,
normalized_fact, derived_principle, model_synthesis, agent_recommendation},
scope{organism_scope, strain_scope, condition_scope, biological_scale,
pedagogical_simplification}, dbtl_stage[], evidence[], confidence{value,
band, source_authority, evidence_directness, cross_source_agreement,
expert_review_bonus, conflict_penalty, inference_distance_penalty,
rationale}, knowledge_status, derivation_type, relationships[],
provenance, requires_human_review, review_status
```

`论文实验设计抽取`的 `ExperimentalCase` 与本模块的 `EngineeringPrinciple` 是这个公共层的两个子类——这就是 Step11 论文案例连接能够成立的基础，而不需要发明第二套本体。

### 1.2 知识生命周期

```text
candidate → validated → human_approved → active → deprecated → superseded
```

新知识对象一律从 `candidate` 起步。只有 `evidence_supported == true` 且 `derivation_type` 为 `explicit_in_source`/`normalized_from_source` 时才可能进入 `validated`；`human_approved`/`active`/`deprecated`/`superseded` 只能由人工复核推进，Agent 不得自行把对象标记为 `active`。当新版本教材或原始研究修正了旧结论时，旧对象转 `superseded`，不得直接覆盖——保留旧对象与 `superseded_by` 指针。

### 1.3 置信度计算规则

`confidence` 不是拍脑袋的单一数字，必须可解释：

```text
confidence ≈ source_authority + evidence_directness + cross_source_agreement
             + expert_review_bonus − conflict_penalty − inference_distance_penalty
```

- **High**：多个权威来源一致 + 有直接证据 + 机制清晰 + 无冲突。
- **Medium**：单一来源 + 机制合理 + 缺少跨来源印证。
- **Low**：模型推断（`derivation_type=model_inference`）、类比迁移、尚无验证；Step09 的证据硬门控会把无法定位证据的对象强制封顶在低置信区间（实现中取 ≤0.3，见 `skills/step09_evidence_binding/skill.py`）。

### 1.4 不进入知识库的内容（Negative Extraction Scope）

默认不进入知识库，除非明确影响工程决策并有证据支持：

1. 历史介绍（"1970 年某科学家发现……"）；
2. 具体实验步骤参数（"37℃培养 16h"）——这属于 Protocol/SOP 范畴，不是 Engineering Principle；
3. 与工程决策无关的单纯事实列表（"E. coli 含 4000 多个基因"）；
4. 教材练习题的假设答案。

### 1.5 证据权重按用途而非来源类型固定排序

不是"教材 > 论文"或反之的固定顺序，而是按用途：

| 用途 | 权重更高的来源 |
|---|---|
| 基础定义 | 教材/专著/权威指南 |
| 工程效果（是否真的有效） | 实验论文（通过 Step11 连接） |
| 方法选择 | Protocol + 多篇论文 |
| 机制解释 | 教材 + 原始研究共同支持 |

教材内部证据优先级（用于同一来源内部裁决）：`定义框/正文明确陈述 > 图表和公式 > 章节总结 > 案例框 > 练习题 > 编辑者推论`；但机制图、代谢通路图、决策图本身可以是核心证据，不得因正文未逐项复述而忽略。

### 1.6 目标用户

本模块的主要使用者是**合成生物学科研 Agent**，不是学生、不是搜索引擎、不是教学系统。输出必须优化为 for AI reasoning（结构化、条件化、可组合），而不是 for human reading 的教学讲解；面向人类的自然语言总结只在"面向用户的交付"（第 8 节）中作为结论摘要出现。

## 2. 支持的输入

- **文档输入**：PDF、EPUB 转换文本、DOCX、Markdown、TXT、HTML、已清洗结构化文本、教材章节扫描件、图表/章节截图、合法可访问的在线资料。当前实现（Phase 1）只解析 Markdown 风格纯文本，见第 9 节 Phase 路线图。
- **书目信息输入**：ISBN、DOI、教材名称、作者、版本、出版社、年份、章节号、页码范围。
- **任务目标输入**：如"抽取本章所有代谢工程设计原则""抽取适用于 E. coli K-12 的知识""抽取基因敲除的决策规则""提取中英文教材中关于代谢瓶颈识别的共同原则""将教材知识与已有论文案例建立连接""生成前端'生物学知识'页面所需结构"。
- **已有中间产物**：已解析章节、已有 Knowledge Object、已有术语表、已有知识图谱节点、已有冲突报告、已有论文实验设计抽取结果（作为 `paper_case_artifacts` 传入）。

## 3. 任务层级判断（Level 1–5）

| 层级 | 输出 |
|---|---|
| Level1 源解析 | 文档类型、书目信息、章节结构、语言、页码、图表、公式、引用关系 |
| Level2 基础知识抽取 | 概念、定义、机制、实体、关系、条件、生物学事实 |
| Level3 工程知识蒸馏 | 工程原则、决策规则、设计模式、适用条件、限制、替代方案、验证策略、失败模式 |
| Level4 跨来源融合 | 同义知识合并、多来源支持、来源冲突、版本差异、中英文对齐、证据强度、适用范围差异 |
| Level5 知识中心适配 | 前端展示结构、API Schema、知识图谱节点和边、Agent 检索单元、论文案例连接、DBTL 阶段映射 |

未提供工程目标或目标菌株时，仍应完成 Level1–4；不得因缺少 E. coli K-12 目标而阻断一般生物学知识蒸馏（`skills/step01_task_contract/skill.py` 从不把空的 `target_organism` 默认为 K-12，只在 `notes` 中提示）。

## 4. 内部步骤编排

以下编号全部是内部执行步骤（命名为 `Step01`…`Step13`，代码中为 `step01_task_contract` 等目录名），不得命名/暴露为 `Skill01`…`Skill13`。

| Step | 内部职责 | 使用条件 |
|---|---|---|
| 01 | 建立知识蒸馏任务契约 | 所有新任务 |
| 02 | 识别与验证知识来源 | 所有新任务 |
| 03 | 解析文档结构（章节/段落/图/表/公式/定义框锚点） | 所有新任务 |
| 04 | 章节相关性与抽取范围判断 | 仅 Level1 时可跳过 |
| 05 | 基础生物学知识抽取（概念/定义/机制） | Level2 及以上 |
| 06 | 工程原则蒸馏 | Level3 及以上，或用户给出工程目标 |
| 07 | 决策规则与决策树生成 | 紧随 06 |
| 08 | 设计模式/验证策略/失败模式抽取 | 紧随 06/07 |
| 09 | 证据绑定与来源追踪（硬门控审计） | 05 或 06–08 执行后必须执行 |
| 10 | 跨来源融合、去重与冲突管理 | Level4 及以上，或用户要求融合且多来源 |
| 11 | 与论文实验设计抽取产物连接 | 用户要求且提供 `paper_case_artifacts` |
| 12 | 质量评价与人工复核（硬门控） | 09 执行后必须执行 |
| 13 | 知识图谱、Agent 检索接口与前端适配 | Level5，或用户要求前端/图谱输出 |

默认依赖关系（`workflow/engine.py::_plan`）：

```text
01 → 02 → 03
       │
       ├─ 仅 Level1：到此为止
       │
       └─ Level2+：04 → 05
                          │
                 ┌────────┴────────┐
                 │ 基础知识任务      │ 工程知识任务
                 │ （到此为止）      │ 06 → 07 → 08
                 └────────┬────────┘
                          ▼
                    09 证据绑定（硬门控）
                          │
             ┌────────────┴────────────┐
             │ Level4+ 或要求融合且多来源 │
             ▼                          │
        10 融合与冲突                    │
             │                          │
             └──────────┬───────────────┘
                要求论文连接则 → 11
                          │
                          ▼
                    12 QC（硬门控，只要产出过知识对象就执行）
                          │
                 Level5 或要求前端 → 13
```

不适用的步骤标记为 `SKIPPED` 并给出原因，不得因为后续步骤不适用就把前面已成功的结果判定为失败。

### Step01 任务契约

记录 `task_id`、原始 `user_request`、`input_sources`（分配稳定 `source_id`）、`target_domain/organism/strain/engineering_goal`、`requested_output_level`、`source_languages`、`output_languages`（默认 `["zh","en"]`）、`quality_requirement`、`requires_cross_source_fusion/paper_case_linking/frontend_adapter`、`requires_human_review`。不得默认目标菌株为 K-12；缺少工程目标只记录 note，不阻断流程。

### Step02 来源识别与验证

来源类型：`textbook | monograph | handbook | manual | guideline | database_entry | review_article | protocol | course_material | primary_research | unknown`。识别 `title/authors/edition/publisher/year/isbn/doi/chapter/page_range/source_language/authority_level/scope/limitations`。规则：不同版本不静默合并；无法验证版本标记 `unresolved_edition`；课程讲义不自动提升为权威教材（`authority_level` 封顶 `low_medium`）；综述中引用的原始研究与综述本身分开保存。

### Step03 文档结构解析

至少解析封面/版权页/目录/章节/小节/段落/定义框/例题案例框/图/图注/表/表注/公式/注释/术语表/参考文献/章节总结/练习题/附录，产出带 `block_id/chapter_id/section_path/page/reading_order/language/source_anchor` 的结构块。图、表、公式是正式知识来源，不是正文附属品；OCR 不确定内容需标记 `OCR_UNCERTAIN`（Phase 1 尚未实现图像解析，见第 9 节）。

### Step04 抽取范围识别

为每个章节/小节判断 `relevance_to_biological_knowledge/engineering_design/target_system`、`contains_concepts/mechanisms/decision_rules/design_patterns/validation_strategy/failure_modes`、`recommended_action ∈ {extract_full, extract_partial, metadata_only, skip}`。评分基于**内容关键词**而非标题，不得因标题不含"工程"二字就跳过；基因表达调控、酶动力学、代谢反馈、应激响应、膜转运、资源竞争、蛋白折叠、细胞生长负担、基因剂量效应、代谢物毒性、进化稳定性等主题即使标题平淡也应识别为高价值内容。

### Step05 基础生物学知识抽取

抽取 Concept/Mechanism/Definition/Process/Relationship/Constraint/Condition/Phenomenon。定义与机制分开保存；相关性与因果性分开（`causal_direction ∈ {positive, negative, unspecified}`）；普遍规律与物种特异规律分开——`organism_scope` 只在源文本中真的出现物种线索时才填写，找不到就留空，不得默认。教材简化模型标记 `pedagogical_simplification=true`。每条知识对象必须携带 `source_statements`（`block_id` + 原文摘录 + `source_anchor`），供 Step09 校验。

### Step06 工程原则蒸馏（最重要的一步）

从 Concept/Mechanism 中蒸馏 Engineering Principle，固定使用以下结构（不允许自由发挥）：

```text
IF     触发条件（trigger_conditions）
THEN CONSIDER   候选工程动作（recommended_actions）
BECAUSE         生物学依据（biological_basis，来自原文）
ONLY IF         前置条件（required_preconditions）
DO NOT GENERALIZE TO   禁止扩展的范围（如未标注物种，必须写明不得默认 E. coli K-12）
VALIDATE BY     验证方法（validation_requirements）
ALTERNATIVES    替代方案（alternatives）
```

**derivation_type 的判定纪律**：如果源句子本身已经包含推荐性措辞（"consider / may / 建议 / 可以"），标记 `normalized_from_source`；否则——也就是源文本只描述了机制，工程含义是模型自己推出来的——必须标记 `model_inference` 并强制 `requires_human_review=true`。禁止把"竞争支路会消耗前体"这类机制描述直接包装成"敲除竞争支路可以提高产量"式的无条件强规则；必须写成"当竞争支路显著消耗目标产物前体、且该支路不承担当前条件下必需生长功能时，可以考虑降低或阻断该支路；若存在生长缺陷风险，应优先比较弱化表达、CRISPRi、动态调控和条件性敲除"这样的条件化陈述。

### Step07 决策规则与决策树生成

只从 Engineering Principle 自身已有的 `required_preconditions`/`recommended_actions`/`alternatives` 构造分支——不额外杜撰判定条件。因为教材极少显式给出"先判断 X 再在 Y/Z 之间选择"的决策程序，所以**只要决策树不是来源明确给出的，就必须标记为模型归纳**（`derivation_type=model_inference`，`human_review_status=pending`）。每个分支必须有判定条件；不允许生成没有输入变量的空泛选择树；必须列出无法判定时需要补充的数据。

### Step08 设计模式、验证策略、失败模式抽取

Design Pattern 的 `canonical_structure` 取自原则的 `recommended_actions`，`applicable/non_applicable_conditions` 取自 `required_preconditions/contraindications`；Validation Strategy 的 `minimum_validation` 取自 `validation_requirements`；Failure Pattern 的 `trigger_conditions/observed_symptoms` 取自 `failure_conditions/possible_side_effects`。**不要只抽成功策略**——生长负担、代谢失衡、中间产物毒性、辅因子不足、蛋白错误折叠、质粒不稳定、表达泄漏、反馈抑制、转运限制、氧化还原失衡、进化逃逸、培养条件依赖、宿主背景差异等失败模式必须与设计模式同等优先保留。

### Step09 证据绑定与来源追踪（硬门控）

对每个知识对象执行三项检查：**存在性**（引用的 `block_id` 在解析结果中确实存在）、**归属性**（该 block 的 `source_id` 与对象自身来源一致）、**语义支持**（引用文本确实是该 block 原文的子串/直接对应，而不只是同单位数字凑巧出现）。硬门控：

```text
若无可定位证据: 不得标记为 reported / validated；confidence 封顶（实现中 ≤0.3）
若来源归属错误: 不计入当前对象，需人工复核
```

证据对象至少包含 `evidence_id/source_id/source_type/source_language/original_text/chapter/section/page/figure/table/source_anchor/supports_field/evidence_role/support_level/confidence`。`evidence_coverage`（总对象数、直接证据支持数、覆盖率、未支持对象列表）传入 Step12。

### Step10 跨来源融合、去重与冲突管理

只在**类型 + 归一化名称**匹配时才分组候选融合对象——语义相似度聚类是未来阶段能力，见第 9 节。**关键纪律**：同一来源内部因抽取路径不同（例如同一概念既从定义句又从机制句各生成一次）产生的用词差异是抽取器自身的重复，不是教材分歧，`merge_relation=related_but_distinct`，不生成 `source_conflicts`；只有当参与融合的对象来自 ≥2 个不同 `source_id` 且定义/物种范围/机制方向确实不同，才生成 `source_conflicts`（`conflict_type ∈ {definition, mechanism, condition_scope, version_update, organism_difference, strain_difference, condition_difference, textbook_simplification_vs_primary_research, translation_ambiguity, terminology_shift, genuine_authority_disagreement}`），并保留全部来源的 `source_specific_variants`，不得"多数来源一致就覆盖少数来源"。

### Step11 与论文实验设计抽取产物连接

`paper_case_artifacts` 视为不透明的 `ExperimentalCase` 形状字典，不假设其精确字段。只对 Engineering Principle / Design Pattern 尝试连接；用关键词重叠作为候选信号，`link_type ∈ {supports, instantiates, contradicts, extends, limits, alternative}` 依据结果文本中的成功/失败措辞粗略判定。**不得因为论文使用了某个基因敲除就自动证明整条工程原则**——每条链接固定低置信度并要求人工确认 `transferability`，只记录 `shared_entities/differences`，不修改论文事实本身。

### Step12 质量评价与人工复核（硬门控）

至少评价来源身份完整性、章节/图表覆盖、证据覆盖率、翻译质量、工程规则可操作性、决策树完整性、失败模式覆盖、跨来源一致性、模型推断比例。硬门控（`skills/step12_quality_governance/skill.py`）：

```text
若无可定位证据                → 不能标记为 source_reported（Step09 已封顶）
若适用条件缺失                → 不得直接进入 Agent 推荐规则（engineering_principle_retrieval=review）
若物种范围不明                → 不得默认适用于 E. coli K-12
若来源版本不明                → 标记 unresolved_edition
若模型生成决策树缺少依据       → 标记 candidate，仅供参考（decision_support=review）
若存在关键机制/定义冲突        → 阻断自动工程建议（automatic_DBTL_design=blocked）
若教材仅为教学简化模型         → 可用于概念解释，不得用于精确工程计划
```

用途治理矩阵（`allowed|review|blocked`）：`concept_explanation`、`mechanism_reasoning`、`engineering_principle_retrieval`、`decision_support`、`automatic_DBTL_design`、`exact_SOP_generation`。**本模块默认不负责生成精确 SOP**——`exact_SOP_generation` 恒为 `blocked`；精确实验参数仍需原始方法论文、Protocol、Supplement、实验室 SOP 和人工审核。

### Step13 知识图谱、Agent 检索接口与前端适配

知识图谱节点类型至少含 `Concept/Entity/Mechanism/EngineeringPrinciple/DecisionRule/DesignPattern/ValidationStrategy/FailurePattern/Constraint/ExperimentalCase/Source/Organism/Strain/Gene/Protein/Metabolite/Pathway/Phenotype/Method/Measurement`；关系类型至少含 `defines/explains/causes/inhibits/activates/requires/applies_to/not_recommended_for/alternative_to/validated_by/fails_when/mitigated_by/derived_from/supported_by/contradicted_by/instantiated_by/belongs_to_DBTL_stage`。

Agent 检索接口按目标/生物系统/菌株/基因/通路/表型/工程问题/失败症状/DBTL 阶段/证据等级/知识类型/适用条件/来源语言/来源权威性等维度检索，而不是只做关键词查教材。

前端"生物学知识 / Biological Knowledge"页面一级分类：概念与机制、工程原则、设计模式、决策规则、验证策略、失败模式、实验案例、知识图谱、来源与证据、冲突与人工复核。每张卡片默认显示名称、一句话定义、知识类型、适用系统、DBTL 阶段、置信度、证据数量、来源数量、是否存在冲突、是否经过人工确认；展开后显示 是什么/为什么/什么时候适用/什么时候不适用/推荐怎么做/需要先测什么/如何验证/可能怎么失败/替代方案/教材来源/论文案例/证据原文/版本和审计记录。来源必须可追溯到教材、版本、章节、页码、图表、原文摘录。

## 5. 统一输出

根据实际执行内容返回以下字段的适用子集（完整 Schema 见 `biological_knowledge_distillation/schema/output.schema.json`）：

```json
{
  "summary": {}, "task_contract": {},
  "validated_sources": [], "source_structure": {}, "extraction_scope": [],
  "biological_concepts": [], "biological_mechanisms": [],
  "engineering_principles": [], "decision_rules": [], "decision_trees": [],
  "design_patterns": [], "validation_strategies": [], "failure_patterns": [],
  "constraints_and_tradeoffs": [],
  "canonical_knowledge_objects": [], "cross_source_fusions": [], "source_conflicts": [],
  "paper_case_links": [],
  "knowledge_graph": {}, "quality_report": {}, "governance": {}, "frontend_view": {},
  "artifacts": [], "step_states": {}, "step_logs": [], "errors": []
}
```

不适用的步骤标记为 `{"status": "SKIPPED", "reason": "..."}`。不得因为某个后续步骤不适用，就把前面已经成功完成的结果判定为失败。

## 6. 状态、Artifact 与恢复机制

运行级状态：`CREATED → RUNNING → WAITING_REVIEW → COMPLETED`，或 `→ FAILED`。内部步骤状态：`PENDING | RUNNING | SUCCESS | WARNING | FAILED | BLOCKED | REVIEW_REQUIRED | SKIPPED`。

每个步骤的输出都保存为带 `artifact_id`（含输入哈希）、`version`、`source_ids`、`created_time`、`schema_version`、`provenance`、`validation_status` 的 Artifact（`workflow/artifacts.py`）。写入使用原子替换（`storage/artifact_store.py`），重试不覆盖旧版本；恢复根据输入哈希和已有成功 Artifact 跳过未变化的步骤，从首个 `FAILED/BLOCKED/REVIEW_REQUIRED` 或缺少有效 Artifact 的步骤继续。单个来源失败不阻断其他来源。

## 7. 错误分类

`SOURCE_IDENTITY_ERROR | UNRESOLVED_EDITION | ACCESS_BLOCKED | PARSING_ERROR | OCR_UNCERTAIN | STRUCTURE_LOSS | FIGURE_NOT_PARSED | TABLE_NOT_PARSED | EVIDENCE_NOT_FOUND | SEMANTIC_MISMATCH | SOURCE_ATTRIBUTION_ERROR | TRANSLATION_CONFLICT | VERSION_CONFLICT | ORGANISM_SCOPE_UNCERTAIN | STRAIN_SCOPE_UNCERTAIN | MECHANISM_CONFLICT | OVERGENERALIZATION_RISK | UNSUPPORTED_DECISION_RULE | KNOWLEDGE_DUPLICATION | FUSION_CONFLICT | PAPER_LINK_MISMATCH | SCHEMA_VALIDATION_ERROR | ARTIFACT_PERSISTENCE_ERROR | HUMAN_REVIEW_REQUIRED`

每个错误包含 `error_code/message/source_id/step/affected_objects/severity/recoverable/recommended_action`（`workflow/error_manager.py`）。

## 8. 面向用户的交付

先给结论，再给证据和限制。至少说明：

1. 处理了哪些来源及其类型（教材/专著/指南/手册……），版本是否可解析；
2. 抽取出哪些概念、机制、工程原则、决策规则、设计模式、验证策略、失败模式；
3. 哪些属于来源原文陈述，哪些属于归一化、哪些属于模型推断（`derivation_type`）；
4. 证据覆盖率、缺失信息和质量风险（`quality_report`）；
5. 哪些步骤被跳过以及原因；
6. 是否需要人工复核，以及具体待复核对象（`governance` + `review_items`）；
7. 若涉及论文案例连接，明确"论文实例化了原则的哪一部分"而不是"论文证明了整条原则"；
8. 完整 JSON/Artifact 的保存位置。

不要把内部步骤编号作为主要用户界面；只有在排查失败、解释审计链或开发模块时才展示具体 Step 编号。

## 9. 安全与科学边界

1. 不得把教材一般规律直接变成可执行湿实验 SOP；
2. 不得自动生成危险、受限制或缺少安全审查的实验方案；
3. 不得将真核机制默认迁移到原核系统；
4. 不得将其他菌种经验默认迁移到 E. coli K-12；
5. 不得将物种层知识自动提升为具体菌株事实；
6. 不得将教学简化图直接当作完整真实机制；
7. 不得把相关性改写为因果；
8. 不得把作者建议改写为已验证规则；
9. 不得把单一来源结论描述为领域共识；
10. 不得把模型生成的模式描述为教材明确提出；
11. 不得因多本教材重复出现而自动判定绝对正确；
12. 不得删除少数来源提出的重要限制；
13. 不得输出没有来源位置的"教材原文事实"；
14. 不得使用未经验证的自动翻译覆盖原文；
15. 不得在缺少补充条件时生成精确实验参数。

## 10. Phase 路线图（工程实现层面，供开发者参考）

当前仓库中的 `biological_knowledge_distillation/` 实现了 **Phase 1**：完整的 13 步编排、真实的证据硬门控、条件化工程原则蒸馏、跨来源融合与冲突区分、论文案例连接、质量治理、知识图谱/前端适配——13 项内部步骤全部有可运行代码和通过的测试，而不是只有 Prompt。Phase 1 的抽取逻辑刻意保持窄而可审计（正则/关键词规则，而非模型自由生成），详细已知限制见 `biological_knowledge_distillation/README.md`：无 PDF/OCR/图像解析、定义与机制抽取靠固定正则库、工程原则archetype 库固定为 5 种、融合仅按归一化名称匹配（无语义聚类）、版本感知融合尚未实现、双语翻译一致性检查尚未实现、论文连接是关键词重叠启发式。

后续阶段建议：

- **Phase 2**：扩充 Step05/06 的抽取模式库（参考 `论文实验设计抽取/skills/skill07_experiment_extraction/extractor/` 的拆分方式，把规则拆成独立 extractor 子模块）；加入 PDF/图像解析（Step03）；加入语义相似度聚类（Step10）。
- **Phase 3**：双语翻译一致性检查与 `translation_status/translation_confidence` 评分；知识图谱/Agent 检索的 API 层与前端页面（参考 `论文实验设计抽取/api` + `frontend`）。
- **Phase 4**：知识生命周期的人工复核工作流（`governance/review_service.py` 扩展）、跨版本知识演化追踪（`superseded_by` 链）。

各阶段之间不需要重新设计整体架构；`workflow/engine.py` 的 `_plan()` 和 `skills/registry.py` 已经支持未来插入/替换单个 Step 而不影响其余步骤。

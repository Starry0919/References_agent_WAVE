# 生物学知识蒸馏 Skill 完整实现 Prompt

你现在需要在现有项目中新增一个统一的 Agent Skill：

# 生物学知识蒸馏

英文名称：

```text
Biological Knowledge Distillation
```

建议 Skill 标识：

```yaml
name: distill-biological-knowledge
```

该能力用于把教材、专著、教学资料、权威知识库条目、指南、实验手册、方法规范和高质量综述中的生物学内容，转化为：

* 可验证的生物学概念；
* 可追溯的生物学机制；
* 可供 Agent 调用的工程原则；
* 条件化决策规则；
* 设计模式；
* 验证策略；
* 失败模式；
* 适用边界；
* 与论文实验案例建立连接的知识对象。

该能力不是普通的教材摘要工具，也不是问答型 RAG。

它的目标是：

> 将分散在教材和权威资料中的生物学知识，蒸馏为可供科研 Agent 检索、推理、组合、审计和复用的结构化知识资产。

---

# 一、开发前必须理解的现有项目约束

项目中已经存在一个统一能力：

```text
论文实验设计抽取
```

请先完整阅读现有文件：

```text
论文实验设计抽取_SKILL(1).md
```

该文件是本次实现的重要架构参考。

需要继承的不是论文专属 Schema，而是以下工程思想：

1. 对外只暴露一个统一能力。
2. 内部编号表示执行步骤，而不是多个独立 Skill。
3. 各步骤根据输入和任务动态编排，不要求机械执行全部步骤。
4. 每条事实必须绑定来源证据。
5. 明确区分来源事实、作者观点、模型归纳和 Agent 建议。
6. 缺失信息标记为 `unknown`，不得根据常识伪造。
7. 使用 Artifact、输入哈希、版本、provenance 和状态机保证可恢复性。
8. 存在冲突、证据不足或高风险推断时进入人工复核。
9. 最终输出必须适配上层 Agent、API 和前端。
10. 不允许把内部步骤编号作为用户主要交互界面。

注意：

本模块中的 Step01、Step02 等全部是：

```text
内部执行步骤
```

不是：

```text
独立 Skill
```

上层 Agent 只能调用一次：

```text
生物学知识蒸馏
```

不得要求用户选择具体步骤。

---

# 二、模块定位

## 2.1 模块名称

```text
生物学知识蒸馏
Biological Knowledge Distillation
```

## 2.2 模块与现有模块的关系

现有模块：

```text
论文实验设计抽取
```

主要负责：

```text
论文 → 实验设计案例
```

新增模块：

```text
生物学知识蒸馏
```

主要负责：

```text
教材、专著、指南、权威资料 → 原理、机制和工程知识
```

二者不得混为同一个模块。

推荐关系：

```text
知识源层
├── 教材
├── 专著
├── 指南
├── 实验手册
├── 权威知识库
├── 高质量综述
└── 实验论文

处理层
├── 生物学知识蒸馏
└── 论文实验设计抽取

知识资产层
├── Biological Concepts
├── Mechanisms
├── Engineering Principles
├── Decision Rules
├── Design Patterns
├── Validation Strategies
├── Failure Patterns
└── Experimental Cases
```

本次任务优先完成：

```text
生物学知识蒸馏
```

同时预留与“论文实验设计抽取”结果连接的接口。

不要在本次任务中大规模重构现有论文 Skill。

只有在必要时增加最小化的共享 Schema、接口或适配器。

---

# 三、核心设计原则

请把以下原则写入最终 Skill 文件。

## 3.1 不做教材摘要

错误输出：

```text
本章介绍了代谢工程的历史、方法和应用。
```

正确输出：

```text
当目标产物受到竞争支路消耗时，可考虑降低或阻断竞争支路通量；
但在竞争支路承担生长必需功能时，应优先使用动态调控、弱化表达
或条件性抑制，而不是直接永久敲除。
```

输出重点必须是：

* 原理是什么；
* 为什么成立；
* 在什么条件下成立；
* 什么时候不能使用；
* 如何验证；
* 有哪些替代策略；
* 证据来自哪里。

## 3.2 区分知识类型

至少区分以下对象：

```text
Concept
Mechanism
Biological Rule
Engineering Principle
Decision Rule
Design Pattern
Validation Strategy
Failure Pattern
Constraint
Tradeoff
Experimental Method Principle
Measurement Principle
```

不同类型不能使用完全相同的 Schema 强行压平。

## 3.3 区分知识来源和知识结论

来源可以是：

* 教材；
* 专著；
* 指南；
* 实验手册；
* 数据库条目；
* 综述；
* 原创论文；
* 模型归纳。

知识结论必须保留：

```text
source_type
source_id
source_location
source_scope
source_authority
evidence_text
evidence_role
```

教材是证据来源，不是最终知识对象本身。

## 3.4 区分原文陈述和模型蒸馏

至少使用以下层级：

```text
source_statement
normalized_fact
derived_principle
model_synthesis
agent_recommendation
```

禁止把模型总结出的规则描述为教材原文明确提出的规则。

## 3.5 知识必须有适用条件

不得输出没有条件限定的强规则，例如：

```text
提高目标基因表达可以提高产量。
```

必须改为条件化形式：

```text
当目标酶对通量具有显著控制作用，且底物、辅因子、折叠能力和下游
步骤不构成新的限制时，提高目标酶表达可能提高目标产物通量。
```

## 3.6 保存反例和限制

对每条规则尽量提取：

* 适用条件；
* 不适用条件；
* 失败原因；
* 反例；
* 潜在副作用；
* 替代方案；
* 所需验证。

## 3.7 中英文双语

知识对象必须支持中英文。

最低要求：

```json
{
  "name_zh": "",
  "name_en": "",
  "definition_zh": "",
  "definition_en": ""
}
```

但不得为了生成英文而扭曲中文来源，也不得把机器翻译冒充来源原文。

必须分别保存：

```text
source_language
original_text
translated_text
translation_status
translation_confidence
```

## 3.8 人类治理

模型生成的：

* 跨来源融合；
* 设计模式；
* 决策树；
* 工程建议；
* 冲突裁决；
* 适用范围扩展；

都必须标记为模型归纳，并支持人工确认。

---

# 四、支持的输入

统一入口应接受以下一种或多种输入。

## 4.1 文档输入

* PDF；
* EPUB 转换文本；
* DOCX；
* Markdown；
* TXT；
* HTML；
* 已清洗结构化文本；
* 教材章节扫描件；
* 图表或章节截图；
* 合法可访问的在线资料。

## 4.2 书目信息输入

* ISBN；
* DOI；
* 教材名称；
* 作者；
* 版本；
* 出版社；
* 年份；
* 章节号；
* 页码范围。

## 4.3 任务目标输入

例如：

* 抽取本章中所有代谢工程设计原则；
* 抽取适用于 E. coli K-12 的知识；
* 抽取基因敲除的决策规则；
* 抽取如何选择蛋白组、转录组、代谢组的验证策略；
* 提取中英文教材中关于代谢瓶颈识别的共同原则；
* 将教材知识与已有论文案例建立连接；
* 生成前端“生物学知识”页面所需结构。

## 4.4 已有中间产物

* 已解析章节；
* 已有 Knowledge Object；
* 已有术语表；
* 已有知识图谱节点；
* 已有冲突报告；
* 已有论文实验设计抽取结果。

---

# 五、任务层级判断

统一入口必须先判断用户需要的结果层级。

至少支持：

## Level 1：来源解析

输出：

* 文档类型；
* 书目信息；
* 章节结构；
* 语言；
* 页码；
* 图表；
* 公式；
* 引用关系。

## Level 2：基础知识抽取

输出：

* 概念；
* 定义；
* 机制；
* 实体；
* 关系；
* 条件；
* 生物学事实。

## Level 3：工程知识蒸馏

输出：

* 工程原则；
* 决策规则；
* 设计模式；
* 适用条件；
* 限制；
* 替代方案；
* 验证策略；
* 失败模式。

## Level 4：跨来源融合

输出：

* 同义知识合并；
* 多来源支持；
* 来源冲突；
* 版本差异；
* 中英文对齐；
* 证据强度；
* 适用范围差异。

## Level 5：知识中心适配

输出：

* 前端展示结构；
* API Schema；
* 知识图谱节点和边；
* Agent 检索单元；
* 论文案例连接；
* DBTL 阶段映射。

未提供工程目标时，可以完成 Level 1–4。

不得因为没有 E. coli K-12 目标而阻断一般生物学知识蒸馏。

---

# 六、内部步骤设计

以下编号全部是内部执行步骤。

不得命名为：

```text
Skill01
Skill02
```

必须命名为：

```text
Step01
Step02
```

或者：

```text
步骤01
步骤02
```

建议实现以下步骤。

---

## Step01：建立知识蒸馏任务契约

解析并记录：

```json
{
  "task_id": "",
  "user_request": "",
  "input_sources": [],
  "target_domain": [],
  "target_organism": [],
  "target_strain": [],
  "target_engineering_goal": [],
  "requested_output_level": [],
  "source_languages": [],
  "output_languages": ["zh", "en"],
  "quality_requirement": "",
  "requires_cross_source_fusion": false,
  "requires_paper_case_linking": false,
  "requires_frontend_adapter": false,
  "requires_human_review": false
}
```

要求：

1. 保留用户原始请求。
2. 明确目标知识领域。
3. 明确是否限定 E. coli K-12。
4. 明确需要基础知识还是工程知识。
5. 明确是否需要中英文双语。
6. 明确是否需要与论文案例连接。
7. 明确是否需要前端输出。
8. 不得默认目标菌株为 K-12。

---

## Step02：识别和验证知识来源

识别来源类型：

```text
textbook
monograph
handbook
manual
guideline
database_entry
review_article
protocol
course_material
primary_research
unknown
```

记录：

```json
{
  "source_id": "",
  "source_type": "",
  "title": "",
  "title_zh": "",
  "title_en": "",
  "authors_or_editors": [],
  "edition": "",
  "publisher": "",
  "publication_year": null,
  "isbn": [],
  "doi": "",
  "chapter": "",
  "page_range": "",
  "source_language": "",
  "access_type": "",
  "identity_verified": false,
  "verification_evidence": [],
  "authority_level": "",
  "scope": "",
  "limitations": []
}
```

注意：

1. 不同版本的教材不能静默合并。
2. 同一本教材不同版本需要分别保存。
3. 中文译本和英文原版必须建立版本关系。
4. 中文译本不能自动视为与最新英文版完全一致。
5. 无法验证版本时标记 `unresolved_edition`。
6. 课程讲义不能自动提升为权威教材。
7. 综述中引用的原始研究与综述本身必须分开。

---

## Step03：解析文档结构

建立稳定的章节和位置锚点。

至少解析：

* 封面；
* 版权页；
* 目录；
* 章节；
* 小节；
* 段落；
* 定义框；
* 例题或案例框；
* 图；
* 图注；
* 表；
* 表注；
* 公式；
* 注释；
* 术语表；
* 参考文献；
* 章节总结；
* 练习题；
* 附录。

结构对象示例：

```json
{
  "block_id": "",
  "block_type": "chapter|section|paragraph|figure|table|equation|box|summary|exercise|reference",
  "chapter_id": "",
  "section_path": [],
  "page_start": null,
  "page_end": null,
  "text": "",
  "figure_or_table_label": "",
  "reading_order": null,
  "language": "",
  "source_anchor": {}
}
```

要求：

1. 不得只依赖纯文本抽取。
2. 图、表、公式必须视为正式知识来源。
3. 对图示机制、通路图、决策树、流程图进行视觉解析。
4. 保留图中实体、箭头方向、激活、抑制和条件标签。
5. OCR 不确定内容必须标记。
6. 页码和章节锚点必须可回溯。

---

## Step04：章节相关性和抽取范围识别

并非整本教材所有内容都应进入工程知识库。

为每章或每节判断：

```json
{
  "section_id": "",
  "relevance_to_biological_knowledge": 0.0,
  "relevance_to_engineering_design": 0.0,
  "relevance_to_target_system": 0.0,
  "contains_concepts": false,
  "contains_mechanisms": false,
  "contains_decision_rules": false,
  "contains_design_patterns": false,
  "contains_validation_strategy": false,
  "contains_failure_modes": false,
  "recommended_action": "extract_full|extract_partial|metadata_only|skip",
  "reason": ""
}
```

不得因为章节标题不含“工程”就跳过。

例如以下内容可能具有很高的工程价值：

* 基因表达调控；
* 酶动力学；
* 代谢反馈；
* 应激响应；
* 膜转运；
* 资源竞争；
* 蛋白折叠；
* 细胞生长负担；
* 基因剂量效应；
* 代谢物毒性；
* 进化稳定性。

---

## Step05：基础生物学知识抽取

抽取以下对象：

```text
Biological Entity
Concept
Definition
Process
Mechanism
Relationship
Constraint
Condition
Phenomenon
Measurement
```

基础知识对象建议 Schema：

```json
{
  "knowledge_id": "",
  "knowledge_type": "concept|mechanism|process|relationship|constraint|phenomenon",
  "name_zh": "",
  "name_en": "",
  "aliases_zh": [],
  "aliases_en": [],
  "definition_zh": "",
  "definition_en": "",
  "entities": [],
  "relationships": [],
  "causal_direction": "",
  "conditions": [],
  "exceptions": [],
  "biological_scale": "molecular|pathway|cellular|population|process",
  "organism_scope": [],
  "strain_scope": [],
  "environment_scope": [],
  "source_statements": [],
  "status": "reported|normalized|inferred|unknown",
  "confidence": 0.0
}
```

要求：

1. 定义和机制分开。
2. 相关性与因果性分开。
3. 普遍规律与物种特异规律分开。
4. 体外体系与细胞内体系分开。
5. 真核和原核知识不得无条件混用。
6. 不同菌株背景不得无条件合并。
7. 教材简化模型需要标记 `pedagogical_simplification`。
8. 机制链每一条边都要有证据。

---

## Step06：工程原则蒸馏

这是本模块最重要的步骤之一。

从基础知识中蒸馏：

```text
Engineering Principle
```

Schema 建议：

```json
{
  "principle_id": "",
  "name_zh": "",
  "name_en": "",
  "principle_statement_zh": "",
  "principle_statement_en": "",
  "biological_basis": [],
  "engineering_objective": [],
  "trigger_conditions": [],
  "required_preconditions": [],
  "recommended_actions": [],
  "expected_effects": [],
  "possible_side_effects": [],
  "failure_conditions": [],
  "contraindications": [],
  "alternatives": [],
  "validation_requirements": [],
  "dbtl_stage": [],
  "organism_scope": [],
  "strain_scope": [],
  "evidence": [],
  "derivation_type": "explicit_in_source|normalized_from_source|cross_source_synthesis|model_inference",
  "confidence": 0.0,
  "requires_human_review": false
}
```

规则必须以条件化形式表达。

推荐结构：

```text
IF
条件与观察

THEN CONSIDER
候选工程动作

BECAUSE
生物学依据

ONLY IF
前置条件

DO NOT GENERALIZE TO
禁止扩展的范围

VALIDATE BY
验证方法

ALTERNATIVES
替代方案
```

严禁无条件输出：

```text
敲除竞争通路可以提高产量。
```

应输出：

```text
当竞争支路显著消耗目标产物前体，并且该支路不承担当前条件下的
必需生长功能时，可以考虑降低或阻断该支路；若存在生长缺陷风险，
应优先比较弱化表达、CRISPRi、动态调控和条件性敲除。
```

---

## Step07：决策规则和决策树生成

从教材显式规则或模型归纳中生成：

```text
Decision Rule
Decision Tree
```

Schema：

```json
{
  "decision_rule_id": "",
  "decision_topic": "",
  "question_zh": "",
  "question_en": "",
  "inputs": [],
  "decision_conditions": [],
  "branches": [],
  "recommended_option": [],
  "rejected_options": [],
  "reasoning_basis": [],
  "required_measurements": [],
  "uncertainty": [],
  "evidence": [],
  "derivation_type": "",
  "confidence": 0.0,
  "human_review_status": ""
}
```

示例：

```text
目标基因是否必需？
├── 是
│   ├── 是否需要降低而非完全失活？
│   │   ├── 是 → CRISPRi / 弱启动子 / 降解标签
│   │   └── 否 → 条件性敲除或补偿表达
└── 否
    ├── 是否担心长期进化逃逸？
    │   ├── 是 → 多位点设计与长期稳定性验证
    │   └── 否 → 常规敲除并验证表型
```

注意：

1. 如果决策树不是来源明确给出的，必须标记为模型归纳。
2. 每个分支必须有判定条件。
3. 不允许生成没有输入变量的空泛选择树。
4. 必须列出无法判定时需要补充的数据。
5. 不得把经验偏好描述为硬性生物学规律。

---

## Step08：设计模式、验证策略和失败模式抽取

### 8.1 设计模式

例如：

* Competitive Pathway Removal；
* Precursor Supply Enhancement；
* Cofactor Balancing；
* Dynamic Regulation；
* Burden Reduction；
* Stress Tolerance Engineering；
* Transport Engineering；
* Adaptive Laboratory Evolution；
* Orthogonal Control；
* Feedback-Resistant Enzyme Design。

Schema：

```json
{
  "pattern_id": "",
  "name_zh": "",
  "name_en": "",
  "problem_context": [],
  "design_intent": "",
  "canonical_structure": [],
  "biological_rationale": [],
  "applicable_conditions": [],
  "non_applicable_conditions": [],
  "common_variants": [],
  "known_tradeoffs": [],
  "validation_strategy_ids": [],
  "failure_pattern_ids": [],
  "supporting_principles": [],
  "supporting_sources": [],
  "supporting_paper_cases": [],
  "maturity": "candidate|reviewed|validated",
  "confidence": 0.0
}
```

### 8.2 验证策略

```json
{
  "validation_strategy_id": "",
  "target_claim": "",
  "minimum_validation": [],
  "recommended_validation": [],
  "orthogonal_validation": [],
  "negative_controls": [],
  "positive_controls": [],
  "time_scale": [],
  "readouts": [],
  "acceptance_criteria": [],
  "failure_interpretation": [],
  "limitations": [],
  "evidence": []
}
```

### 8.3 失败模式

```json
{
  "failure_pattern_id": "",
  "name_zh": "",
  "name_en": "",
  "trigger_conditions": [],
  "observed_symptoms": [],
  "possible_causes": [],
  "diagnostic_measurements": [],
  "mitigation_options": [],
  "prevention_options": [],
  "scope": [],
  "evidence": [],
  "confidence": 0.0
}
```

不要只抽成功策略。

教材中关于以下内容必须优先保留：

* 生长负担；
* 代谢失衡；
* 中间产物毒性；
* 辅因子不足；
* 蛋白错误折叠；
* 质粒不稳定；
* 表达泄漏；
* 反馈抑制；
* 转运限制；
* 氧化还原失衡；
* 进化逃逸；
* 培养条件依赖；
* 宿主背景差异。

---

## Step09：证据绑定与来源追踪

所有知识对象必须绑定证据。

证据对象至少包含：

```json
{
  "evidence_id": "",
  "source_id": "",
  "source_type": "",
  "source_language": "",
  "original_text": "",
  "translated_text": "",
  "chapter": "",
  "section": "",
  "page": "",
  "figure": "",
  "table": "",
  "equation": "",
  "source_anchor": {},
  "supports_field": "",
  "evidence_role": "definition|mechanism|condition|exception|recommendation|limitation|example",
  "subject_attribution": "",
  "support_level": "direct|partial|contextual|conflicting",
  "confidence": 0.0
}
```

证据检查至少包括：

1. 存在性；
2. 来源归属性；
3. 语义支持；
4. 适用范围；
5. 翻译一致性；
6. 版本一致性；
7. 图文一致性。

来源证据优先级不能简单照搬论文 Methods 优先级。

教材类来源应根据知识类型动态判断：

```text
定义框 / 正文明确陈述
> 图表和公式
> 章节总结
> 案例框
> 练习题
> 编辑者推论
```

但对机制图、代谢通路和决策图：

```text
图示可能是核心证据
```

不得因正文没有逐项重复而忽略。

---

## Step10：跨来源融合、去重和冲突管理

需要融合：

* 同一本书不同章节；
* 同一教材不同版本；
* 中文译本与英文原版；
* 不同教材；
* 教材与权威指南；
* 教材与综述；
* 教材知识与论文实验案例。

融合前必须区分：

```text
same_concept
broader_narrower
related_but_distinct
conflicting
translation_variant
version_update
organism_specific_variant
condition_specific_variant
```

融合后的 Knowledge Object 必须保留所有来源。

Schema：

```json
{
  "canonical_knowledge_id": "",
  "canonical_name_zh": "",
  "canonical_name_en": "",
  "merged_from": [],
  "merge_relation": "",
  "shared_core": [],
  "source_specific_variants": [],
  "organism_specific_variants": [],
  "condition_specific_variants": [],
  "conflicts": [],
  "unresolved_questions": [],
  "provenance": [],
  "fusion_confidence": 0.0,
  "review_status": ""
}
```

不得采用“多数来源一致就覆盖少数来源”的粗暴方式。

冲突类型至少包括：

* 定义冲突；
* 机制冲突；
* 条件范围冲突；
* 版本更新；
* 物种差异；
* 菌株差异；
* 培养条件差异；
* 教材简化与原始研究差异；
* 中文翻译歧义；
* 术语变化；
* 权威来源之间真实争议。

冲突对象：

```json
{
  "conflict_id": "",
  "topic": "",
  "claims": [],
  "possible_explanation": [],
  "impact_on_agent_use": "",
  "resolution_status": "resolved|partially_resolved|unresolved",
  "requires_human_review": true
}
```

---

## Step11：与论文实验设计案例连接

该步骤用于连接现有“论文实验设计抽取”产物。

不要直接修改论文事实。

连接对象：

```json
{
  "link_id": "",
  "knowledge_object_id": "",
  "paper_case_id": "",
  "link_type": "supports|instantiates|contradicts|extends|limits|alternative",
  "paper_experiment_id": "",
  "shared_entities": [],
  "shared_conditions": [],
  "differences": [],
  "transferability": "",
  "evidence": [],
  "confidence": 0.0
}
```

示例：

```text
工程原则：
竞争支路去除

论文案例：
E. coli BW25113 中删除 pta

关系：
instantiates

限制：
只在特定培养基和目标产物背景下验证，
不能推广为所有 E. coli 培养条件下均有效。
```

不得因为论文使用了某个基因敲除，就自动证明完整工程原则。

论文案例只能：

* 支持；
* 实例化；
* 扩展；
* 限制；
* 反驳；

某个知识对象。

---

## Step12：质量评价和人工复核

至少评价：

* 来源身份完整性；
* 章节覆盖；
* 图表覆盖；
* 证据覆盖率；
* 翻译质量；
* 定义完整性；
* 机制链完整性；
* 条件和边界完整性；
* 工程规则可操作性；
* 决策树完整性；
* 失败模式覆盖；
* 多来源一致性；
* 版本冲突；
* 物种和菌株适用性；
* 模型推断比例；
* 前端可用性；
* Agent 检索可用性。

质量报告示例：

```json
{
  "source_quality": {},
  "parsing_quality": {},
  "evidence_quality": {},
  "knowledge_completeness": {},
  "engineering_utility": {},
  "cross_source_consistency": {},
  "translation_quality": {},
  "risk_flags": [],
  "review_items": [],
  "overall_status": "PASS|PASS_WITH_WARNINGS|REVIEW_REQUIRED|BLOCKED"
}
```

设置硬门控：

```text
若无可定位证据：
    不能标记为 source_reported

若适用条件缺失：
    不得直接进入 Agent 推荐规则

若物种范围不明：
    不得默认适用于 E. coli K-12

若来源版本不明：
    标记 unresolved_edition

若中英文内容不一致：
    进入 translation_review

若模型生成决策树但缺少足够依据：
    标记 candidate，仅用于参考

若存在关键机制冲突：
    阻断自动工程建议

若教材仅给出教学简化模型：
    可以用于概念解释
    不得直接用于精确工程计划
```

用途治理：

```json
{
  "concept_explanation": "allowed|review|blocked",
  "mechanism_reasoning": "allowed|review|blocked",
  "engineering_principle_retrieval": "allowed|review|blocked",
  "decision_support": "allowed|review|blocked",
  "automatic_DBTL_design": "allowed|review|blocked",
  "exact_SOP_generation": "allowed|review|blocked"
}
```

注意：

本模块默认不负责生成精确 SOP。

教材知识可以支持：

* 设计逻辑；
* 方法选择；
* 验证策略；
* 风险识别。

但精确实验参数仍需：

* 原始方法论文；
* Protocol；
* Supplement；
* 实验室 SOP；
* 人工审核。

---

## Step13：知识图谱、Agent 接口和前端适配

### 13.1 知识图谱

节点类型至少包括：

```text
Concept
Entity
Mechanism
EngineeringPrinciple
DecisionRule
DesignPattern
ValidationStrategy
FailurePattern
Constraint
ExperimentalCase
Source
Organism
Strain
Gene
Protein
Metabolite
Pathway
Phenotype
Method
Measurement
```

关系类型至少包括：

```text
defines
explains
causes
inhibits
activates
requires
applies_to
not_recommended_for
alternative_to
validated_by
fails_when
mitigated_by
derived_from
supported_by
contradicted_by
instantiated_by
belongs_to_DBTL_stage
```

### 13.2 Agent 检索接口

Agent 不应只通过关键词查教材。

应支持以下检索维度：

* 目标；
* 生物系统；
* 菌株；
* 基因；
* 通路；
* 表型；
* 工程问题；
* 失败症状；
* DBTL 阶段；
* 证据等级；
* 知识类型；
* 适用条件；
* 来源语言；
* 来源权威性。

推荐接口：

```json
{
  "query": "",
  "query_type": "",
  "target_system": {},
  "engineering_context": {},
  "required_knowledge_types": [],
  "dbtl_stage": [],
  "evidence_threshold": "",
  "language": "zh|en|bilingual",
  "include_conflicts": true,
  "include_paper_cases": true,
  "include_failure_patterns": true
}
```

### 13.3 前端“生物学知识”页面

前端不应以教材文件列表为主。

建议页面名称：

```text
生物学知识
Biological Knowledge
```

内部呈现为：

```text
Biological Knowledge Center
```

页面一级分类：

```text
概念与机制
工程原则
设计模式
决策规则
验证策略
失败模式
实验案例
知识图谱
来源与证据
冲突与人工复核
```

每个知识对象卡片默认显示：

* 名称；
* 一句话定义；
* 知识类型；
* 适用系统；
* DBTL 阶段；
* 置信度；
* 证据数量；
* 来源数量；
* 是否存在冲突；
* 是否经过人工确认。

点击展开后显示：

```text
是什么
为什么
什么时候适用
什么时候不适用
推荐怎么做
需要先测什么
如何验证
可能怎么失败
替代方案
教材来源
论文案例
证据原文
版本和审计记录
```

来源必须可追溯到：

* 教材；
* 版本；
* 章节；
* 页码；
* 图表；
* 原文摘录。

---

# 七、统一执行流程

推荐内部路由：

```text
Step01 建立任务契约
        │
        ▼
Step02 来源识别与验证
        │
        ▼
Step03 文档结构解析
        │
        ▼
Step04 抽取范围识别
        │
        ├── 基础知识任务
        │      ▼
        │   Step05
        │
        └── 工程知识任务
               ▼
            Step05 → Step06 → Step07 → Step08
                                  │
                                  ▼
                              Step09 证据绑定
                                  │
                                  ▼
                              Step10 融合与冲突
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
             无论文案例需求                 需要论文连接
                    │                           │
                    │                       Step11
                    └─────────────┬─────────────┘
                                  ▼
                              Step12 QC
                                  │
                                  ▼
                              Step13 输出适配
```

编号只是内部跟踪。

上层只调用：

```text
生物学知识蒸馏
```

---

# 八、统一输出 Schema

建议输出以下适用子集：

```json
{
  "summary": {},
  "task_contract": {},
  "validated_sources": [],
  "source_structure": {},
  "extraction_scope": [],
  "biological_concepts": [],
  "biological_mechanisms": [],
  "engineering_principles": [],
  "decision_rules": [],
  "decision_trees": [],
  "design_patterns": [],
  "validation_strategies": [],
  "failure_patterns": [],
  "constraints_and_tradeoffs": [],
  "canonical_knowledge_objects": [],
  "cross_source_fusions": [],
  "source_conflicts": [],
  "paper_case_links": [],
  "knowledge_graph": {},
  "quality_report": {},
  "governance": {},
  "frontend_view": {},
  "artifacts": [],
  "step_states": {},
  "step_logs": [],
  "errors": []
}
```

不适用步骤标记：

```json
{
  "status": "SKIPPED",
  "reason": ""
}
```

不得因为某个后续步骤不适用，就把前面已经成功完成的结果判定为失败。

---

# 九、状态、Artifact 和恢复机制

沿用现有论文 Skill 的工程原则。

运行状态：

```text
CREATED
RUNNING
WAITING_REVIEW
COMPLETED
FAILED
```

内部步骤状态：

```text
PENDING
RUNNING
SUCCESS
WARNING
FAILED
BLOCKED
REVIEW_REQUIRED
SKIPPED
```

每个步骤必须产生版本化 Artifact：

```json
{
  "artifact_id": "",
  "artifact_type": "",
  "version": "",
  "input_hash": "",
  "source_ids": [],
  "generated_by_step": "",
  "created_at": "",
  "schema_version": "",
  "provenance": {},
  "validation_status": ""
}
```

要求：

1. Artifact 写入前执行 Schema 校验。
2. Artifact 写入前执行语义自检。
3. 状态成功必须发生在有效 Artifact 持久化之后。
4. 重试不能覆盖旧版本。
5. 输入未变化时支持幂等跳过。
6. 单个来源失败不得阻断其他来源。
7. 缺少关键页或附件时允许人工补充后恢复。
8. 所有模型融合都要保留输入对象和模型版本。
9. 人工修改必须形成新版本，不得静默覆盖模型结果。

---

# 十、错误分类

至少实现：

```text
SOURCE_IDENTITY_ERROR
UNRESOLVED_EDITION
ACCESS_BLOCKED
PARSING_ERROR
OCR_UNCERTAIN
STRUCTURE_LOSS
FIGURE_NOT_PARSED
TABLE_NOT_PARSED
EVIDENCE_NOT_FOUND
SEMANTIC_MISMATCH
SOURCE_ATTRIBUTION_ERROR
TRANSLATION_CONFLICT
VERSION_CONFLICT
ORGANISM_SCOPE_UNCERTAIN
STRAIN_SCOPE_UNCERTAIN
MECHANISM_CONFLICT
OVERGENERALIZATION_RISK
UNSUPPORTED_DECISION_RULE
KNOWLEDGE_DUPLICATION
FUSION_CONFLICT
PAPER_LINK_MISMATCH
SCHEMA_VALIDATION_ERROR
ARTIFACT_PERSISTENCE_ERROR
HUMAN_REVIEW_REQUIRED
```

错误必须包含：

```json
{
  "error_code": "",
  "message": "",
  "source_id": "",
  "step": "",
  "affected_objects": [],
  "severity": "",
  "recoverable": true,
  "recommended_action": ""
}
```

---

# 十一、必须实现的安全和科学边界

1. 不得把教材中的一般规律直接变成可执行湿实验 SOP。
2. 不得自动生成危险、受限制或缺少安全审查的实验方案。
3. 不得将真核机制默认迁移到原核系统。
4. 不得将其他菌种经验默认迁移到 E. coli K-12。
5. 不得将物种层知识自动提升为具体菌株事实。
6. 不得将教学简化图直接当作完整真实机制。
7. 不得把相关性改写为因果。
8. 不得把作者建议改写为已验证规则。
9. 不得把单一来源结论描述为领域共识。
10. 不得把模型生成的模式描述为教材明确提出。
11. 不得因多本教材重复出现而自动判定绝对正确。
12. 不得删除少数来源提出的重要限制。
13. 不得输出没有来源位置的“教材原文事实”。
14. 不得使用未经验证的自动翻译覆盖原文。
15. 不得在缺少补充条件时生成精确实验参数。

---

# 十二、测试要求

必须为该 Skill 建立系统测试。

## 12.1 单元测试

至少覆盖：

* 来源类型识别；
* 教材版本识别；
* 中文和英文来源识别；
* 章节解析；
* 图表锚点；
* 概念抽取；
* 机制关系抽取；
* 工程原则生成；
* 条件化规则生成；
* 适用范围识别；
* 失败模式抽取；
* 证据绑定；
* 翻译一致性；
* 去重；
* 冲突检测；
* 论文案例连接；
* Artifact 版本；
* 状态恢复；
* 前端 Schema。

## 12.2 负例测试

必须包含：

1. 将中文译本和不同英文版本错误合并；
2. 将教材举例当作普遍原则；
3. 将真核知识迁移到 E. coli；
4. 将物种知识提升为具体菌株事实；
5. 将“可能”改写为“必然”；
6. 将图中示意箭头改写为已验证因果；
7. 将章节总结当作完整机制；
8. 将练习题假设场景当作真实实验；
9. 将教材历史描述当作工程建议；
10. 将多个来源的不同条件拼接成不存在的统一规则；
11. 将模型生成决策树标为原文规则；
12. 忽略中文翻译与英文原版冲突；
13. 在没有证据页码时输出高置信结论；
14. 在缺少物种范围时默认 K-12；
15. 只提取成功策略，不提取限制和失败模式。

## 12.3 集成测试

至少准备以下测试集：

```text
英文合成生物学教材章节
中文合成生物学教材章节
英文代谢工程教材章节
中文代谢工程教材章节
E. coli 专著章节
基因工程实验手册章节
系统生物学机制章节
权威综述
包含复杂图表的教材章节
中英文对应版本章节
```

## 12.4 验收标准

至少满足：

* 所有知识对象可追溯；
* 中英文均可展示；
* 不同版本不被静默合并；
* 工程原则包含条件和边界；
* 决策规则包含输入和分支；
* 失败模式得到保留；
* 模型推断与来源原文严格分离；
* 知识对象能连接论文案例；
* 输出能供 Agent 检索；
* 输出能供前端展示；
* 失败可恢复；
* 人工审核有完整审计链；
* 全部测试通过；
* 不破坏现有论文实验设计抽取模块。

---

# 十三、建议的最终文件结构

请根据现有项目结构适配，不要机械照搬。

建议：

```text
biological_knowledge_distillation/
├── __init__.py
├── skill.md
├── orchestrator.py
├── contracts.py
├── schemas/
│   ├── task_contract.py
│   ├── source.py
│   ├── evidence.py
│   ├── concept.py
│   ├── mechanism.py
│   ├── engineering_principle.py
│   ├── decision_rule.py
│   ├── design_pattern.py
│   ├── validation_strategy.py
│   ├── failure_pattern.py
│   ├── fusion.py
│   ├── conflict.py
│   ├── paper_link.py
│   ├── governance.py
│   └── frontend.py
├── steps/
│   ├── step01_task_contract.py
│   ├── step02_source_validation.py
│   ├── step03_document_parsing.py
│   ├── step04_scope_selection.py
│   ├── step05_basic_knowledge_extraction.py
│   ├── step06_principle_distillation.py
│   ├── step07_decision_rule_generation.py
│   ├── step08_pattern_and_failure_extraction.py
│   ├── step09_evidence_binding.py
│   ├── step10_knowledge_fusion.py
│   ├── step11_paper_case_linking.py
│   ├── step12_quality_governance.py
│   └── step13_frontend_adapter.py
├── adapters/
│   ├── pdf_adapter.py
│   ├── markdown_adapter.py
│   ├── bilingual_adapter.py
│   ├── paper_extraction_adapter.py
│   └── knowledge_graph_adapter.py
├── services/
│   ├── artifact_service.py
│   ├── provenance_service.py
│   ├── terminology_service.py
│   ├── translation_service.py
│   ├── fusion_service.py
│   └── conflict_service.py
└── tests/
```

注意：

目录 `steps/` 中的文件是步骤实现，不是独立 Skill。

---

# 十四、最终 Skill 文件必须具备的头部

最终生成的 `SKILL.md` 建议以类似以下内容开头：

```yaml
---
name: distill-biological-knowledge
description: 将教材、专著、指南、实验手册、权威数据库条目和高质量综述转化为证据可追溯、支持中英文展示并可供 Agent 推理的生物学知识对象。能力包括来源验证、章节解析、概念与机制抽取、工程原则蒸馏、条件化决策规则、设计模式、验证策略、失败模式、跨来源融合、冲突管理、论文案例连接、知识图谱和前端适配。内部编号仅表示动态编排的执行步骤，不应作为独立 Skill 暴露给用户。
---
```

正文开头明确写：

```text
把本能力视为一个统一的、证据驱动、双语支持并由人类治理的
生物学知识蒸馏系统。

上层 Agent 只调用一次“生物学知识蒸馏”。

Step01–13 是内部可组合步骤，不是独立 Skill，也不是必须机械执行的
固定流水线。系统应根据输入来源、用户目标、知识类型和输出用途动态编排。
```

---

# 十五、最终交付要求

完成实现后，请输出：

## 15.1 架构审查

说明：

* 阅读了哪些现有文件；
* 如何复用了论文抽取模块的工程原则；
* 哪些部分共用；
* 哪些部分保持隔离；
* 为什么这些内部单元被称为 Step 而不是 Skill。

## 15.2 实现清单

列出：

* 新增文件；
* 修改文件；
* Schema；
* API；
* 数据库；
* 测试；
* 前端适配；
* 迁移脚本。

## 15.3 完整 Skill 文件

提供最终完整的：

```text
生物学知识蒸馏_SKILL.md
```

不能只给摘要或局部片段。

## 15.4 示例输出

至少提供三个完整示例：

1. 英文教材章节；
2. 中文教材章节；
3. 中英文教材融合并连接论文案例。

## 15.5 测试报告

包括：

* 测试数量；
* 通过数量；
* 失败数量；
* 覆盖的关键风险；
* 是否存在已知限制；
* 是否影响原有模块。

## 15.6 发布判断

给出：

```text
READY
READY_WITH_LIMITATIONS
NEEDS_REVISION
BLOCKED
```

并说明理由。

---

# 十六、实施纪律

1. 先检查现有仓库和现有 Skill，再编码。
2. 不要重新设计整个 Agent。
3. 不要破坏现有“论文实验设计抽取”。
4. 不要把步骤写成多个对外 Skill。
5. 不要只写 Prompt 而不实现 Schema、状态、Artifact 和测试。
6. 不要使用假数据宣称测试通过。
7. 不要伪造教材原文、页码、ISBN 或证据。
8. 测试材料缺失时，应建立 fixture 接口并明确说明。
9. 任何模型推断必须可审计。
10. 代码、Schema、Skill 文件和测试必须保持一致。
11. 所有对外输出优先使用用户能理解的模块名称，不展示内部编号。
12. 只有调试、审计或开发说明中才允许展示具体 Step 编号。

请现在开始执行：

1. 阅读现有项目和《论文实验设计抽取_SKILL(1).md》；
2. 给出简短架构判断；
3. 实现“生物学知识蒸馏”统一 Skill；
4. 建立 Step01–13 内部步骤；
5. 完成 Schema、治理、Artifact、恢复和测试；
6. 输出完整 Skill 文件及实现报告。


我重新审查了一遍上一版 Prompt。如果目标是：

> **直接交给 Claude Code，让它像实现“论文实验设计抽取”一样，把“生物学知识蒸馏”开发成正式 Agent Skill**

那么我的判断是：

**目前版本已经达到“可以交给 Claude 开始开发”的程度，但还没有达到“直接作为最终开发 Prompt，无需人工干预”的程度。**

原因不是方向错误，而是还有几个工程层面的缺口。

我逐项检查。

---

# 总体评价

## 当前版本：

| 维度           | 评价           |
| ------------ | ------------ |
| 战略定位         | ★★★★★        |
| 和论文抽取模块关系    | ★★★★★        |
| 知识抽取思想       | ★★★★★        |
| Schema设计     | ★★★★☆        |
| 工程实现指导       | ★★★★☆        |
| 测试要求         | ★★★★☆        |
| 直接交给Claude开发 | ⚠️ 可以，但建议再优化 |

---

# 最大的问题1：缺少“和现有论文实验设计Skill的统一知识协议”

这是我认为最需要补的一点。

现在：

论文模块：

输出：

```
Experimental Case
```

教材模块：

输出：

```
Engineering Principle
```

但是两个模块之间缺少一个共同语言。

未来会出现：

论文：

```
删除 pgi 提高产量
```

教材：

```
竞争通路去除原则
```

如何连接？

现在 Prompt 里说了：

> 建立连接

但是没有定义：

**连接协议。**

---

建议增加：

## Knowledge Object Common Layer

所有知识资产必须继承：

```yaml
KnowledgeObject:

id:

type:

name:

description:

scope:

organism:

strain:

condition:

dbtl_stage:

evidence:

confidence:

provenance:

relationships:
```

然后：

论文：

继承：

```
ExperimentalCase
```

教材：

继承：

```
EngineeringPrinciple
```

例如：

```
KnowledgeObject
      |
      |
      ├── EngineeringPrinciple
      |
      └── ExperimentalCase
```

这样未来：

Review、数据库、Protocol也可以接入。

---

# 最大的问题2：没有明确“知识生命周期”

你现在设计的是：

输入 → 抽取 → 输出

但是 Agent 长期运行需要：

知识不是一次生成。

应该增加：

## Knowledge Lifecycle

例如：

```
Draft

↓

Validated

↓

Human Reviewed

↓

Active

↓

Deprecated

↓

Superseded
```

原因：

教材会更新。

比如：

2020版教材：

认为某策略有效。

2026新研究：

发现限制。

怎么办？

不能覆盖。

应该：

```
Old Knowledge

↓

Updated Knowledge

↓

Superseded
```

---

建议加入：

```yaml
knowledge_status:

candidate

validated

human_approved

active

deprecated

superseded
```

---

# 最大的问题3：缺少“知识置信度计算逻辑”

现在有：

confidence字段。

但是Claude不知道怎么算。

建议增加：

Confidence来源：

```
Confidence =
Source Authority
+
Evidence Directness
+
Cross-source Agreement
+
Expert Review
-
Conflict Penalty
-
Inference Distance
```

不用要求精确公式。

但是需要：

规则。

例如：

## High Confidence

满足：

* 多个权威教材一致；
* 有原始实验支持；
* 机制明确。

---

## Medium

* 单教材；
* 机制合理；
* 缺少直接实验。

---

## Low

* 模型推断；
* 类比迁移；
* 尚无验证。

---

# 最大的问题4：缺少“不要抽什么”

现在写了很多禁止。

但是还不够明确。

我建议增加：

## Negative Extraction Scope

明确：

以下内容默认不进入知识库：

### 1. 历史介绍

例如：

```
1970年某科学家发现……
```

除非：

影响工程决策。

---

### 2. 实验步骤参数

例如：

```
37℃培养16h
```

不进入 Engineering Principle。

---

### 3. 单纯事实列表

例如：

```
E.coli含4000多个基因
```

除非用于工程决策。

---

### 4. 教材练习题答案

不能作为知识。

---

这个很重要。

否则Claude容易变成：

“教材总结机器人”。

---

# 最大的问题5：缺少“教材和论文权重关系”

这里非常关键。

未来 Agent 推理时：

教材不是永远高于论文。

例如：

教材：

```
Knockout A usually improves production
```

论文：

```
Knockout A caused severe growth defect
```

怎么办？

需要规则。

建议增加：

## Evidence Hierarchy

不是简单：

教材 > 论文。

而是：

不同用途不同权重。

例如：

### 基础定义：

教材权重高。

### 工程效果：

实验论文权重高。

### 方法选择：

Protocol + 多论文。

### 机制：

教材 + 原始研究。

---

# 最大的问题6：缺少“目标用户”

Claude开发时不知道这个模块服务谁。

建议明确：

Primary User:

```
Synthetic Biology Research Agent
```

不是学生。

不是搜索引擎。

不是教学系统。

---

因此：

输出应该优化：

```
for AI reasoning
```

而不是：

```
for human reading
```

---

# 最大的问题7：缺少一个真实Example

这是我认为最应该补的。

Claude Code非常需要Example。

建议加入：

## Example

输入：

```
Metabolic Engineering教材章节：

Feedback inhibition
```

输出：

不要：

```
反馈抑制是一种调控方式……
```

而应该：

```
Engineering Principle:

Feedback Resistance Engineering


Problem:

Target pathway limited by end-product inhibition


Design Pattern:

Modify feedback-sensitive enzyme


Applicable Condition:

Product accumulation inhibits first committed step


Engineering Actions:

1. mutate regulatory site
2. replace enzyme
3. introduce heterologous enzyme


Validation:

enzyme activity
metabolite concentration
production titer


Failure:

increased flux causes metabolic burden
```

这个例子会极大提高Claude实现质量。

---

# 最大的问题8：Step数量可能过早固定

13个Step很好。

但是我建议：

不要写死必须13个。

因为未来：

图片解析

视频课程

数据库

会增加。

建议改：

```
Initial implementation contains Step01-Step13.

The orchestrator must allow future insertion/removal.
```

否则以后扩展困难。

---

# 最大的问题9：需要明确技术实现边界

现在Prompt偏架构。

Claude Code可能会：

直接创建大量文件。

但是不知道：

是否接入现有：

* registry
* orchestrator
* artifact system
* memory system

建议增加：

一句：

> 首先扫描现有Agent架构，复用已有基础设施，不允许重复实现Artifact、Memory、Logging、Schema验证系统。

这个非常重要。

---

# 最大的问题10：缺少Release标准

论文Skill已经有：

测试通过。

这里也应该有：

```
READY

条件：

1. 可以处理PDF教材
2. 可以输出Knowledge Object
3. 可以绑定证据
4. 可以连接论文案例
5. 可以生成前端结构
6. 不破坏已有模块
7. 测试通过
```

---

# 我建议最终再加一个“Phase开发策略”

否则Claude可能一次性写太多。

建议：

## Phase 1

最小闭环：

```
PDF教材

↓

解析

↓

Concept

↓

Engineering Principle

↓

Evidence

↓

JSON输出
```

---

## Phase 2

增加：

```
Decision Rule

Design Pattern

Failure Pattern
```

---

## Phase 3

增加：

```
Knowledge Graph

Paper Link

Frontend Adapter
```

---

## Phase 4

增加：

```
Human Review

Versioning

Knowledge Evolution
```

---

# 最终判断

如果满分100：

现在Prompt：

**85分。**

可以开发。

但是作为你们 WAVE Agent 的核心知识层，我建议优化到：

**95分。**

必须补：

1. ✅ Knowledge Object统一协议
2. ✅ Knowledge Lifecycle
3. ✅ Confidence计算规则
4. ✅ Negative Extraction Scope
5. ✅ Evidence Hierarchy
6. ✅ 一个完整输入输出Example
7. ✅ Phase开发策略
8. ✅ 明确复用现有Agent基础设施
9. ✅ Release标准

补完以后，这个Prompt就可以直接给Claude Code。

而且我认为：

**“论文实验设计抽取” + “生物学知识蒸馏” + “知识融合层”**

会形成你们Agent真正区别于普通科研RAG Agent的核心架构。前者提供“案例经验”，后者提供“专家原则”，融合层提供“可迁移工程思维”。这三个部分组合起来，才接近一个合成生物学专家系统。

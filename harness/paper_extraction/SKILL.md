---
name: paper-experimental-design-extraction-skill07
description: Reconstruct experiment instances, biological objects, scoped parameters, claims, candidate evidence anchors, and engineering-decision candidates from one available scientific document. This runtime skill performs Skill07 only; it does not retrieve papers, verify evidence independently, score quality, compare papers, adapt designs, generate DBTL plans, govern workflows, or prepare frontend output.
---

## V3 canonical output order

`experiment_instances` is canonical scientific output. Build experiments before
`atomic_claims`. Each claim binds one experiment, scalar subject/predicate/object
and a candidate evidence slot. Atomicity follows biological and measurement
scope, not sentence splitting. The 16 `fields` and
`experimental_design_object` remain derived compatibility projections. Skill07
evidence is candidate only; ambiguity stays review-required.

# Skill07：单文献实验设计与工程决策抽取规则

## 0. 职责与交接边界

本技能只处理调用方提供的一篇已解析、已清洗文献。目标是完成语义重建，而不是全文摘要或关键词收集：

```text
Document
├── ArticleTypeGate
├── BiologicalObject
├── Experiment
│   ├── Intervention
│   ├── Condition
│   ├── Control
│   ├── ReplicateStructure
│   ├── Readout
│   ├── Analysis
│   └── Outcome
├── Claim
├── CandidateEvidenceAnchor
├── Conflict
└── DecisionCandidate
```

本技能不得执行或声称完成：

- 文献检索、DOI 校验、PDF 下载或全文获取；
- 独立证据验证、质量评分或工作流状态裁决；
- 跨论文比较、目标系统迁移或 K-12 适配；
- DBTL 方案、SOP、采购清单或可执行实验计划生成；
- Artifact 生命周期、缓存、重试、治理或前端呈现。

Skill07 只生成“候选证据锚点”；Skill08 才独立检查证据的存在性、归属性和语义支持。Skill07 只报告缺失、冲突和依赖；Skill09 或确定性校验器才计算质量并决定 `REVIEW_REQUIRED`、`BLOCKED` 等状态。不得自行宣告抽取结果已通过验证或审批。

调用方提供的运行时输出合同是结构 Schema 的唯一真相来源。本技能定义科学语义和抽取方法，不得用本文中的示例替代运行时合同，也不得添加合同外顶层字段。

## 1. 文档覆盖与 ArticleTypeGate

### 1.1 只基于实际可用内容

检查输入中实际存在的标题、摘要、Introduction、Methods/Experimental Procedures、Results、Discussion、图注、表格、补充材料及其索引。不得声称阅读了输入中没有提供、无法解析或只有链接的内容。

在合同允许的位置记录：

- `available_sections`：实际检查的章节；
- `available_modalities`：正文、图、表、补充材料、源数据或代码中实际可用的部分；
- `missing_or_unparsed`：缺失、截断、OCR 失败或未解析内容；
- `blocked_fields_or_uses`：这些缺失具体阻断的字段或用途。

只有输入真实包含图像或图表结构时才能声称视觉检查或逐格读取；只有图注文本时，只能抽取图注明确陈述的内容。

### 1.2 ArticleTypeGate 使用两个维度

先判定 `document_genre`：

- `primary_research`
- `review_article`
- `systematic_review`
- `meta_analysis`
- `protocol`
- `methods_paper`
- `case_report`
- `perspective`
- `other`

再分别判定：

- `contains_original_experiment`：是否包含当前作者实际实施的原创实验；
- `original_experiment_scope`：原创实验覆盖全文主体、局部验证、案例演示或无；
- `classification_evidence`：支持判定的文内证据；
- `classification_uncertainty`：混合文类或证据不足之处。

不得仅靠单一 `document_genre` 决定是否存在原创实验。Methods paper、data paper 或 protocol 可能包含当前作者的验证实验；review 也可能包含局部原创分析。只对实际存在且归属于当前研究的实验建立当前论文实验实例。

### 1.3 文章类型改变语义 Schema，不只是字段多少

- 原创实验：重建当前研究的实验实例、对象、参数和工程决策候选。
- 综述、系统综述、Meta 分析或教材：将实验归属到具体 `included_study`；不得虚构“本文自身”的实验组、条件或构建。
- Protocol：区分计划/规范值与已经实施、测量或验证的值。
- Methods paper：区分方法描述、性能验证和应用案例。
- Perspective：提取主张或建议时明确其不是已实施实验。

若运行时合同使用统一字段信封，不适用于该文类的核心字段按照合同编码，同时在 `notes` 中明确 `not_applicable` 语义，禁止把“非适用”写成“搜索不到”。

## 2. 来源主体、主张类型与目标系统隔离

### 2.1 两个正交维度

每个事实、主张和证据锚点分别标记：

1. 来源主体：
   - `current_article`
   - `included_study`
   - `background_citation`
2. 认识论/主张类型：
   - `direct_observation`
   - `author_interpretation`
   - `paper_claim`
   - `model_inference`
   - `causally_validated`

若运行时合同暂时把这些维度合并在 `source_attribution`，按合同输出，但语义上仍须分别判断，不得把 `author_inference` 当作来源论文，也不得把 `current_article` 自动当作直接观测。

引用条目只能证明来源被引用；Introduction 或 Discussion 对前人工作的复述不能证明当前作者实施了该实验。作者使用 `likely`、`could`、`suggested`、`might` 等表达时，不得提升为已验证机制。

### 2.2 论文系统与用户目标系统隔离

分别保存：

- `paper_biological_system` / `paper_target_strains`：文献实际研究的对象；
- `user_target_system`：调用方提供、供后续迁移使用的目标。

Skill07 不执行二者之间的迁移判断。用户目标系统不得影响对论文菌株、宿主、材料、实验条件或结论的抽取。

## 3. 生物对象与菌株解析

### 3.1 先建对象，再绑定实验

为每个可区分对象保留：

- 原文名称与标签 `paper_label`；
- `object_type`：organism、strain、cell_line、host、parent、control、engineered_strain、plasmid、construct、library、sample 或其他；
- `paper_name_raw`；
- `normalized_name`；
- `normalization_basis`：`document_internal`、`ontology_external` 或 `model_knowledge`；
- `identity_status`：`reported`、`normalized`、`inferred` 或 `unknown`；
- genotype、parent/child lineage、组合关系和实验角色；
- 候选证据锚点与解析依据 `resolution_rationale`。

`resolution_rationale` 只保存可审计的名称解析依据，不输出隐藏推理过程。

### 3.2 归一化纪律

- 原文只报告物种时，不得凭常识补成具体菌株。
- 原文报告 `MG1655` 时，可将标准化名称写为 `Escherichia coli K-12 MG1655`，但必须保留 raw name，并标明标准化依据；不得把归一化信息伪装为原文逐字报告。
- 只有论文内部谱系、材料表或可靠对象关系明确支持时，才能推断亲本或宿主关系。
- 组合构建、独立构建和候选构建不得合并；例如多个突变可能是同一组合株，也可能是多个单突变株，必须由原文对象关系决定。
- exact host、完整 genotype 或序列仅存在于未提供 Supplement 时，认识论状态保持 `unknown`，另记录 `dependency = requires_supplement`；不得把依赖状态当作字段状态。

## 4. 实验实例优先与文献级投影

### 4.1 Canonical truth

`experimental_design_object` 中的实验实例和对象关系是 canonical truth。运行时合同要求的 16 个核心字段只是兼容性的 document-level projection：

- `objective`
- `hypothesis`
- `strain`
- `genotype`
- `engineering_method`
- `experimental_groups`
- `controls`
- `culture_conditions`
- `medium`
- `dosage`
- `time`
- `replicates`
- `assay`
- `instruments`
- `analysis_methods`
- `outcomes`

不得为填充投影字段而跨实验、构建体、阶段或来源拼接。若同一字段在多个实例中存在不同值，保留实例级值及其 scope；投影使用合同允许的复数结构、明确摘要或冲突记录，不能伪造单一代表值。

### 4.2 实验实例结构

先实例化 `experiment_id`，再绑定：

- `parent_experiment_id` 或所属 campaign；
- biological objects / constructs；
- intervention；
- experimental groups 与 controls；
- process stage；
- conditions 与 materials；
- replicate structure；
- assay、instrument 与 analysis；
- observations、outcomes 与 claims；
- candidate evidence anchors；
- tested scope 与 unsupported extensions。

同一论文中的 initial design、revised design、implemented design 和 final verified product 必须分开。计划值、实际值和最终测量值使用不同 `value_role`，不得覆盖。

## 5. 语义抽取规则

### 5.1 参数对象

每个参数尽量绑定：

```text
raw_text
raw_value
raw_unit
parameter_type
process_step
material_or_system
experiment_id
value_role
scope
source_entity
candidate_source_location
epistemic_status
dependency
```

如需单位归一化，保留 raw value/unit；不得由模型用换算值覆盖原值。`normalized_value` 和 `normalized_unit` 只能作为派生候选，最终换算由确定性程序校验。

### 5.2 参数语义纪律

判断参数含义必须依赖对象、过程步骤、语法角色和局部上下文，不能只依赖单位或关键词。例如：

- `37 °C` 可能是培养、反应、热处理或仪器温度；
- `wt.%` 中的 `wt` 不是 wild type；
- glycerol 可能是碳源、保存剂、结合剂或洗脱组分；
- 年代、编号和版本号不是实验时长或剂量；
- OD、滴度、产率、得率、生产强度和相对倍数不是同一测量量；
- 未检出必须绑定检测方法和检出限，不能改写为绝对零事件。

无法确认语义角色时移入 unresolved/unknown，不得按最常见含义猜测。

### 5.3 范围与分母

所有比例、计数、阈值和成功率必须保留：

- numerator 与 denominator 的对象；
- process stage；
- success criterion；
- tested conditions；
- source location；
- 未覆盖的泛化范围。

例如 `12/16 successful` 不能脱离“什么对象在什么阶段按何种标准成功”而直接写成 75% 总成功率。总设计数不得复制为每个验证阶段的成功数。

对批量构建建立“对象 × 验证阶段”关系，按实际文献区分：`designed_or_encoded`、`expression_tested`、`condition_dependent`、`identity_confirmed`、`purified`、`free_product_confirmed`、`functional_or_cyclized`。未给逐项数据的单元格保持 unknown。

#### 5.3.1 Replicate taxonomy

不要把所有 `n` 都叫重复数。区分：

- `biological_replicates`
- `independent_culture_replicates`
- `technical_replicates`
- `recovered_colonies_or_clones`
- `independent_events_confirmed`
- `cells_or_fields_sampled`
- `representative_display`
- `unknown`

每个重复记录 `n`、独立性、适用实验/读数、来源和不确定性。图中点数、细胞数或克隆数不得自动当作 biological replicates。

### 5.4 跨模态冲突

只比较实际可用来源。发现数值、公式、身份、范围、方法、跨模态或来源归属冲突时，建立统一 Conflict 候选：

```text
field_or_object_path
conflict_type
candidate_values
candidate_sources
why_incompatible
reconciliation_status
required_review_or_attachment
```

不得用摘要覆盖 Methods，不得因“通常 Methods 更可靠”而静默丢弃 Results、图表或 Supplement 的冲突值。证据偏好必须按字段类型决定：方法参数优先定位 Methods/Supplement，结果优先 Results/Figure/Table/Source Data，作者解释优先 Discussion，研究目标优先 Abstract/Introduction；这只是查找启发，不是自动裁决规则。

主图已明确展示的定性事实可抽取；精确序列、原始计数、检出限、误差、统计或未展示条件继续记录为缺失依赖。不要因 Supplement 缺失而抹去主文已支持的事实。

### 5.5 工程决策标注（DDR 标注）

DDR 是“设计选择的候选记录”，不是所有实验记录。对每条可能的工程动作依次执行：

### Q1 — Intervention Gate

当前作者是否主动选择并施加了明确工程动作，例如敲除、过表达、点突变、异源表达、启动子/RBS 工程、回路构建、发酵条件调整或进化/筛选 campaign？纯测量、表征、docking、结构预测、WGS 解读和结果观察不通过 Q1。

### Q2 — Current-Study Gate

该动作是否由本文实施或选择？明确写为此前研究已构建、沿用既有菌株/元件或仅来自被引用研究的动作不通过 Q2。

### Q3 — Decisionhood Gate

该动作是否代表作者主动选择的设计方案，而不是纯测量、验证读数、结果观察或事后解释？一个工程动作不需要“引出未来步骤”才构成决策；论文的最后一个主动设计动作也可以通过 Q3。

三问全部通过时，分类为 `engineering_decision`。未通过时不得生成完整工程决策链，应按实际内容标记为 `validation`、`measurement`、`characterization`、`background` 或 `post_hoc_interpretation`。若运行时 enum 暂不支持更细分类，映射到合同允许值，并在 rationale 中保留真实语义。

### DDR 候选字段

对 `engineering_decision` 按运行时合同填写：

```text
decision_type
decision_type_rationale
design_action
design_action_rationale
trigger_observation
evidence_grading
evidence_grading_rationale
reason_nature
reason_nature_rationale
reason_nature_tags
generalizable_rule
alternatives_considered
strategy_categories
```

语义纪律：

1. `trigger_observation` 必须在时间或论证逻辑上先于工程动作，并有候选证据锚点。禁止用动作后的结果反推触发原因。
2. `design_action` 的 M0–M11 是兼容编码，不应混淆推理阶段与实际干预。无法确定动作码时留空，并在 rationale 中描述原文动作；不得默认归类。
3. `evidence_grading` 的“硬/软”只是遗留兼容字段，不等于科学证据强度。优先在 rationale 中明确 `evidence_basis_type`：`experimental_measurement`、`stoichiometric_constraint`、`literature_precedent`、`computational_prediction`、`structural_prediction`、`screening_result` 或 `author_assertion`。预测性依据必须注明需实测确认。
4. `reason_nature` 要区分：
   - 论文明确给出并在决策前成立的机制依据；
   - 明确的文献类比；
   - 资源现成可得；
   - 筛选或进化得来；
   - `rationale_not_reported`：论文没有报告理由；
   - `post_hoc_rationalization_uncertain`：论文在结果后给出但未证明其驱动决策的解释。
   若合同只接受旧中文枚举，`rationale_not_reported` 映射到允许值，并在 rationale 中明确“理由未报告”，不得把它误说成论文进行了事后合理化。
5. `generalizable_rule` 在 Skill07 中始终是 `rule_candidate` 的兼容槽位，不是已验证规则。只有工程决策、机制依据或明确文献类比、候选证据充分、tested scope 和 excluded scope 明确时才可填写；否则为 `null`。内容必须限制在本文实际测试范围，不得泛化到所有宿主、产品或条件。
6. `alternatives_considered` 只记录论文明确讨论或试验后放弃的备选方案及原因，没有则为空。
7. `strategy_categories` 是代谢/生物工程领域受控词表，而非通用科学本体。只按本步实际动作选择；无法归类时为空，不得按论文标题猜测。

## 6. 候选证据锚定：Skill07 → Skill08

Skill07 为每个 `reported` 或 `inferred` 候选提供：

- claim/field/object/decision 标识；
- 原文最小必要摘录；
- paragraph ID；
- 可用时的 section、page、figure、panel、table、supplement；
- 来源主体；
- 主张类型；
- 支持的字段路径；
- tested scope 与 excluded/unsupported generalizations。

候选锚点必须先满足三项语义检查：

1. **E1 Existence**：摘录确实存在于当前可定位输入；
2. **E2 Attribution**：摘录属于正确的研究主体；
3. **E3 Semantic Support**：摘录支持目标字段的科学含义，而非仅包含相似词或单位。

Skill07 只能提交候选判断，不得把自己的检查称为独立验证。Skill08 必须重新读取来源并验证 E1/E2/E3。只通过存在性而归属或语义失败的内容不得标成可靠 `reported`。

菌株优先从 Methods、菌株/材料表、图注和可用 Supplement 锚定；摘要或 Introduction 的物种名通常只能支持物种层级。结果类字段优先从 Results、Figure、Table 或 Source Data 锚定。字段相关的来源优先级不能替代逐条语义检查。

## 7. 状态、不确定性与依赖

状态维度必须分开：

```text
epistemic_status: reported | inferred | unknown | not_applicable
dependency: none | requires_full_text | requires_figure | requires_table | requires_supplement | requires_source_data
source_entity: current_article | included_study | background_citation
claim_type: direct_observation | author_interpretation | paper_claim | model_inference | causally_validated
```

若运行时合同当前只接受 `reported|inferred|unknown`：

- `not_applicable` 使用 `unknown` 编码，值为 null、证据为空，并在 notes 明确 `not_applicable`；
- 依赖信息写入合同允许的 notes/extensions，不得把 `requires_supplement` 填进 epistemic status；
- 不得为了兼容而丢失来源主体或主张类型的语义。

`inferred` 必须提供推断方法、依据和候选证据。无法从当前文献有限推出时必须是 `unknown`。冲突、OCR 不可靠、仅有摘要或关键材料缺失时，降低抽取可靠性并说明具体原因。

数值 confidence 若由运行时合同强制要求，只表示文本到字段及证据锚点的抽取可靠性，不是科学证据强度、统计概率或审批分数。不得因为结论符合常识而提高。

## 8. 提交前语义检查

在不输出隐藏思维过程的前提下，确认：

1. ArticleTypeGate 同时考虑文类和原创实验范围；
2. 论文生物系统未被用户目标系统替换；
3. 原始身份、归一化身份和归一化依据未混淆；
4. 实验实例先于文献级字段投影建立；
5. 参数、重复、分组、结果和证据均绑定到正确实例与 scope；
6. 不同研究主体、实验、构建、阶段、条件、单位及设计/实施/实测值未被拼接；
7. `reported` 有候选证据锚点，`inferred` 有推断依据，`unknown` 无猜测值；
8. 非适用、信息未知和 Supplement 依赖的维度未混用；
9. 冲突保留全部候选值和来源，未被静默裁决；
10. DDR 候选通过 Q1/Q2/Q3，触发原因没有由结果反推；
11. 非决策记录没有携带伪造的工程动作、理由或规则；
12. `generalizable_rule` 被视为有边界的单篇规则候选，而非已验证规则；
13. 没有声称完成 Skill08 证据验证、Skill09 质量评分或任何治理审批；
14. 最终 JSON 严格遵循调用方运行时合同，不添加合同外顶层字段。

我重新整合了一版 **Skill07 V3（Framework Alignment + Enhanced Reasoning版）**。

这版遵循原则：

1. **老师 Framework 中明确要求的内容优先保留**

   * 不改变 Skill07 的核心定位；
   * 保留老师定义的字段；
   * 保留 reported / unknown / inferred；
   * 保留字段级 provenance 接口；
   * 保留 No hallucination 原则。

2. **我之前增加但可能越界的内容进行降级处理**

   * DBTL Mapping → 删除（属于 Skill11 工程方案层）
   * Causal Chain → 保留为 optional extension（不是核心输出）
   * Mechanistic reasoning → 降级为 hypothesis support，不作为实验事实
   * Variable model → 保留为 optional extension（对后续K12迁移有价值）

3. **老师没有但对工程实现非常重要的内容保留**

   * Experiment workflow reconstruction
   * Control purpose
   * Variable relationship
   * Experiment grouping
   * Extraction metadata

最终定位：

> Skill07 = Experimental Design Extraction + Lightweight Knowledge Reconstruction
> 而不是完整工程设计生成器。

---

保存：

```text
skill07_experimental_design_extraction_implementation_prompt_v3.md
```

---

````markdown
# Skill07 Implementation Prompt


# 项目名称

论文实验设计抽取

Literature Experimental Design Extraction


---

# 当前任务


实现：

# Skill07：论文实验设计结构化抽取 Skill

Experimental Design Extraction Engine


---

# 任务目标


从 Skill06 输出的 Clean Scientific Document 中，

自动抽取论文中的实验设计方案。


输出：

结构化 Experimental Design Object。


目标：

将论文中的实验设计信息转换为：

- 可追溯
- 可验证
- 可复现
- 可用于后续K12适配分析

的结构化知识。


---

# 项目背景


完整Pipeline：


Skill01

用户需求解析与检索策略生成


↓

Skill02

文献自动检索


↓

Skill03

论文真实性验证


↓

Skill04

论文PDF获取


↓

Skill05

PDF结构化解析


↓

Skill06

Markdown科学文本清洗


↓

Skill07

实验设计结构化抽取

（当前）


↓

Skill08

实验设计原文证据绑定


↓

Skill09

实验设计质量评估


↓

Skill10

K12适配与实验比较


↓

Skill11

工程化实验方案生成


---

# Skill07定位


Skill07不是：

❌ 论文摘要生成器

❌ Methods章节复制器

❌ AI实验设计器


Skill07负责：

## Experimental Design Extraction


即：

从论文中恢复作者实际设计的实验方案。


---

# 核心原则


## 1. 论文事实优先


所有核心实验信息必须来自论文。


来源优先级：

1. Materials and Methods

2. Supplementary Methods

3. Results

4. Figure/Table legend


---

## 2. 禁止幻觉补全


如果论文没有提供：

必须输出：

unknown


禁止根据经验补充：


例如：

错误：

E.coli实验 → 默认37°C


错误：

gene knockout → 默认CRISPR


错误：

LC-MS → 默认某型号仪器


---

## 3. 区分事实和推断


每个字段必须包含状态：


reported

论文明确报道


unknown

论文没有提供


inferred

根据论文已有信息合理推断


---

# 输入 Input


来自：

Skill06 Scientific Markdown Cleaning


输入：

```json
{
"paper_id":"",

"title":"",

"clean_markdown_path":"",

"clean_json_path":"",

"sections":[],

"figures":[],

"tables":[]

}
````

---

# 输出 Output

生成：

## Experimental Design Object

---

# 数据结构

```json
{
"paper_id":"",

"experimental_design":{},

"field_metadata":{},

"extensions":{}
}
```

---

# 一、实验设计核心Schema

## 1. Experimental Objective

提取：

作者想解决的问题。

字段：

```json
{
"objective":"",
"source_location":"",
"status":"reported"
}
```

---

## 2. Scientific Hypothesis

提取：

作者实验设计背后的假设。

字段：

```json
{
"hypothesis":"",
"status":"reported|unknown|inferred"
}
```

注意：

如果论文没有明确提出：

不能生成。

---

## 3. Biological System

必须包含：

### Organism

例如：

Escherichia coli

---

### Strain

例如：

MG1655

BW25113

---

### Genotype

例如：

ΔgeneA

---

输出：

```json
{
"organism":"",
"strain":"",
"genotype":""
}
```

---

## 4. Engineering Method

提取：

基因或系统改造方式。

包括：

* knockout
* knockdown
* overexpression
* pathway engineering
* promoter engineering

以及：

target gene

construction method

construct information

如果不存在：

unknown

---

## 5. Experimental Groups

识别：

不同实验组。

例如：

```json
{
"groups":[

{
"name":"WT",

"type":"control"
},

{
"name":"mutant",

"type":"experimental"
}

]
}
```

---

## 6. Controls

不仅记录control名称。

同时记录：

control purpose

例如：

```json
{
"name":"wild type",

"purpose":
"baseline comparison"
}
```

---

## 7. Culture Conditions

提取实验条件。

包括：

* medium
* carbon source
* temperature
* time
* volume
* agitation
* OD
* induction condition

没有：

unknown

---

## 8. Dosage Information

包括：

* concentration
* amount
* induction level

例如：

IPTG 0.1 mM

---

## 9. Replication Information

必须提取：

* biological replicate
* technical replicate
* n value

例如：

```json
{
"biological_replicates":3,

"technical_replicates":2
}
```

---

## 10. Assay / Measurement

包括：

实验检测方法。

例如：

* growth assay
* metabolite measurement
* RNA-seq
* proteomics

---

## 11. Instrument Information

提取：

实验仪器。

例如：

* LC-MS
* GC-MS

如果论文未说明：

unknown

---

## 12. Data Analysis Methods

包括：

* software
* statistical method
* normalization
* threshold

---

## 13. Outcomes

区分：

### Observed Outcome

论文实际观察结果。

### Author Conclusion

作者解释。

禁止AI生成额外解释。

---

# 二、字段Metadata要求

每一个字段必须包含：

```json
{
"value":"",

"status":"reported",

"confidence":0,

"source_location":"",

"extraction_method":""
}
```

字段说明：

## source_location

包括：

* section
* paragraph
* figure
* table

---

## extraction_method

例如：

* rule_based
* semantic_extraction
* llm_extraction

---

# 三、实验流程重建（Extension）

为了支持后续K12适配，

增加：

experiment_workflow

但不替代核心Schema。

例如：

```json
{
"workflow":[

{
"stage":"strain construction",

"input":"",

"operation":"",

"output":""

}

]
}
```

---

# 四、变量关系分析（Extension）

用于辅助后续分析。

不是实验事实。

包括：

```json
{
"variables":{

"independent":[],

"dependent":[],

"controlled":[]

}
}
```

---

# 五、实验逻辑信息（Extension）

只记录论文明确逻辑。

例如：

```json
{
"design_logic":{

"question":"",

"hypothesis":"",

"measurement":"",

"expected_interpretation":""

}
}
```

如果没有：

unknown

---

# 六、禁止输出

Skill07禁止生成：

❌ AI优化方案

❌ 推荐实验方案

❌ K12迁移建议

❌ DBTL设计

❌ 新机制假设

这些属于：

Skill10 / Skill11

---

# 工程结构

创建：

skills/

skill07_experimental_design_extraction/

```
├── README.md

├── skill.py


├── extractor/


│
├── objective_extractor.py

├── hypothesis_extractor.py

├── strain_extractor.py

├── engineering_extractor.py

├── group_extractor.py

├── condition_extractor.py

├── measurement_extractor.py

├── outcome_extractor.py


├── extension/


│
├── workflow_builder.py

├── variable_analyzer.py

├── design_logic.py


├── schema.py

├── validator.py

├── logger.py

├── error_codes.py


├── tests/


│
├── test_objective.py

├── test_strain.py

├── test_condition.py

├── test_replicate.py

├── test_unknown.py

├── test_hallucination.py

├── test_workflow.py


└── examples/
```

---

# 工作流程

Step 1

读取Clean Document JSON

↓

Step 2

定位实验相关章节

↓

Step 3

抽取实验实体

↓

Step 4

生成Experimental Design Object

↓

Step 5

生成Extension信息

↓

Step 6

执行Self Check

↓

Step 7

输出结果

---

# Self Check机制

必须执行：

## Check 1

Schema完整性

检查：

required fields

---

## Check 2

来源完整性

检查：

字段是否有source_location。

---

## Check 3

状态一致性

reported：

必须有证据位置。

unknown：

不得填写value。

---

## Check 4

幻觉检测

检查：

是否新增论文不存在参数。

---

## Check 5

信息一致性

检查：

strain

gene

condition

group

是否内部冲突。

---

# Logging要求

输出：

```json
{
"skill_name":
"skill07_experimental_design_extraction",

"paper_id":"",

"fields_extracted":0,

"reported_fields":0,

"unknown_fields":0,

"inferred_fields":0,

"errors":[]
}
```

---

# Error Handling

## EXP001

输入文档不存在

处理：

failed

---

## EXP002

实验信息不足

处理：

partial_output

---

## EXP003

字段冲突

处理：

标记conflict

---

## EXP004

无法确定信息

处理：

unknown

---

# 测试要求

必须包含：

## Test 1

完整实验论文

验证：

完整抽取。

---

## Test 2

缺少培养条件

验证：

unknown。

---

## Test 3

多个实验组

验证：

group reconstruction。

---

## Test 4

多个replicate

验证：

replicate extraction。

---

## Test 5

Methods和Figure冲突

验证：

conflict记录。

---

## Test 6

幻觉测试

验证：

不会自动补参数。

---

# 后续接口

输出供：

Skill08

Evidence Binding

Skill09

Quality Evaluation

Skill10

K12 Adaptation

Skill11

Engineering Proposal

---

# 最终验收标准

Skill07完成后必须满足：

1. 严格符合Framework要求。

2. 完整抽取实验设计字段。

3. 支持实验逻辑辅助分析。

4. 支持workflow重建。

5. 所有字段可追溯。

6. unknown不补全。

7. 不生成AI实验方案。

8. 有完整日志。

9. 有错误处理。

10. 有测试。

---

# 注意事项

不要修改Framework核心Schema。

如果发现Schema不足：

创建：

schema_change_proposal.md

不要直接修改。

---

开始实现 Skill07。

```

---

这版相比上一版的关键调整：

|内容|处理|
|-|-|
|老师要求字段|完整保留|
|reported/unknown/inferred|恢复为核心状态|
|source_location/confidence/extraction_method|补齐|
|DBTL Mapping|删除|
|AI方案生成|删除|
|K12分析|删除|
|workflow reconstruction|保留为扩展|
|variable model|保留为扩展|
|causal reasoning|删除（避免越界）|
|control purpose|保留|
|replicate|补充|

这版我认为是目前最适合作为 **Codex实际开发输入** 的版本：既不会偏离老师给的 Agent 框架，又保留了你们未来做 Synthetic Biology DBTL Engineering OS 所需要的结构化能力。:contentReference[oaicite:1]{index=1}
```

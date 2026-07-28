我先说明一下：我已经读取了你上传的原版 Skill08 Prompt。

结合我们刚刚对 **Skill07 V3（Experimental Design Extraction Framework Alignment版）** 的修改，原 Skill08 有几个地方必须同步升级：

---

## 原 Skill08 的问题

原版 Skill08 假设：

```
Skill07
↓
Experimental Design Object
↓
绑定Evidence
```

但是现在 Skill07 输出已经升级为：

```
Experimental Design Object

+
Field Metadata

+
Experiment Workflow Extension

+
Variable Relationship Extension

+
Design Logic Extension
```

因此 Skill08 需要升级：

---

# 必须修改点

## 1. 输入结构需要更新

原：

```json
{
"experimental_design":{}
}
```

不够。

应该支持：

```json
{
"experimental_design":{},
"field_metadata":{},
"extensions":{
"workflow":{},
"variables":{},
"design_logic":{}
}
}
```

---

## 2. Evidence绑定范围扩大

原版只要求：

* strain
* gene
* culture condition
* assay

现在需要增加：

### Workflow Evidence

例如：

```
strain construction
↓
cultivation
↓
measurement
```

必须知道来自哪里。

---

### Variable Evidence

例如：

```
independent variable:
gene knockout
```

必须绑定原文。

---

### Design Logic Evidence

例如：

```
knocking out geneA reduces competing pathway
```

必须区分：

* reported
* inferred

不能直接作为事实。

---

## 3. Evidence状态需要和Skill07保持一致

原版：

```
reported
inferred
unknown
```

保持。

不要增加：

conflict

not_reported

因为Framework统一性更重要。

冲突单独作为：

evidence_conflict事件。

---

## 4. 增加 extraction_method

老师Framework要求：

每个字段：

* source location
* extraction method
* confidence
* status

所以Evidence Object需要增加：

```json
{
"value":"",
"status":"reported",
"confidence":0.95,
"source_location":"",
"extraction_method":""
}
```

---

## 5. Evidence不是证明“字段”，而是证明“知识单元”

升级：

从：

```
temperature → quote
```

变成：

```
Experimental Knowledge Unit

↓

Evidence
```

例如：

不是只绑定：

```
gene knockout
```

而是：

```
Engineering Strategy:

delete geneA
Purpose:

reduce competing pathway
Evidence:
Methods paragraph X
```

---

下面是优化后的完整 Codex Prompt。

---

# Skill08 V2 Implementation Prompt

````markdown
# Skill08 Implementation Prompt


# 项目名称

论文实验设计抽取

Literature Experimental Design Extraction


---

# 当前任务

实现：

## Skill08：实验设计原文证据绑定 Skill

Evidence Provenance Binding Engine


---

# 目标


将 Skill07 输出的：

Experimental Design Knowledge Object


转换为：

Evidence-linked Experimental Design Object


建立：

Experimental Knowledge Unit

↓

Original Evidence


之间的可追溯关系。


---

# Pipeline位置


Skill06

Clean Scientific Document


↓

Skill07

Experimental Design Extraction


↓

Skill08

Evidence Provenance Binding


↓

Skill09

Quality Evaluation



---

# Skill08定位


Skill08不是：

- 再次抽取实验设计
- 评价实验方案
- 修改实验方案


它负责：

## Evidence Provenance Layer


核心问题：

> 每一个实验设计字段和知识单元来自论文哪里？


---

# 核心原则


## 1. 每个字段必须可追溯


任何Experimental Design字段：

必须绑定：

- 原文位置
- 原文片段
- 来源类型
- 可信状态


---

## 2. Evidence优先于推理


没有原文支持：

不能认为是真实信息。


输出：

unknown


---

## 3. 状态体系必须统一


允许：

```text
reported

inferred

unknown
````

---

## reported

论文明确描述。

例如：

"Cells were cultured at 37°C"

---

## inferred

论文多个信息组合得到。

必须说明推理链。

---

## unknown

论文没有提供。

---

# 输入

来自：

Skill07

以及：

Skill06 Clean Document

Input:

```json
{
"experimental_design":{},

"field_metadata":{},

"extensions":{

"workflow":{},

"variables":{},

"design_logic":{}

},

"clean_document":{

"sections":[],

"figures":[],

"tables":[]

}

}
```

---

# 输出

生成：

## Evidence-linked Experimental Design Object

结构：

```json
{

"experimental_design":{},

"evidence_map":{},

"coverage":{},

"conflicts":[]

}
```

---

# Evidence Unit Schema

每一个字段必须转换为：

```json
{

"field":

"culture_temperature",


"value":

"37°C",


"status":

"reported",


"confidence":

0.98,


"evidence":{


"paper_id":"",

"section":"Methods",

"subsection":"Culture condition",

"paragraph":"3",

"page":"5",


"figure":null,


"table":null,


"quote":

"Cells were cultured at 37°C"


},


"extraction_method":

"semantic_matching"

}
```

---

# Evidence必须包含

## 1. Source Location

包括：

* paper_id
* section
* subsection
* paragraph
* page

---

## 2. Evidence Type

允许：

```text
text

figure

table

supplement
```

---

## 3. Original Quote

保存最小充分证据。

要求：

quote必须能够支持value。

---

## 4. Extraction Method

记录：

例如：

```text
keyword_matching

semantic_retrieval

llm_alignment
```

---

# Evidence绑定范围

必须覆盖：

## Core Experimental Design Fields

### Objective

### Hypothesis

### Organism

### Strain

### Genotype

### Engineering Method

### Experimental Groups

### Controls

### Culture Conditions

### Dosage

### Time

### Replicates

### Assay

### Instrument

### Data Analysis

### Outcomes

---

# Extension Evidence Binding

Skill07新增Extension也必须支持。

---

## 1. Workflow Evidence

例如：

```
strain construction

↓

cultivation

↓

measurement
```

每一步绑定来源。

---

## 2. Variable Evidence

例如：

Independent variable:

gene knockout

Dependent variable:

product concentration

必须绑定。

---

## 3. Design Logic Evidence

例如：

作者明确说明：

gene deletion reduces competing pathway

标记：

reported

如果只是推理：

inferred

---

# Evidence Matching Pipeline

Step1:

读取Skill07字段

↓

Step2:

定位相关章节

↓

Step3:

全文语义检索

↓

Step4:

生成候选Evidence

↓

Step5:

判断Evidence是否真正支持字段

↓

Step6:

生成Evidence Object

---

# Evidence判断规则

## 支持

原文直接包含：

value

---

## 部分支持

原文描述相关概念。

状态：

inferred

---

## 不支持

状态：

unknown

---

# Conflict处理

如果论文不同位置冲突：

例如：

Methods:

37°C

Figure:

30°C

不能自动选择。

输出：

```json
{
"conflict":{

"field":"temperature",

"sources":[]

}
}
```

---

# 禁止行为

禁止：

## 1

常识补全

E.coli

↓

37°C

错误。

---

## 2

技术自动补充

knockout

↓

CRISPR

错误。

---

## 3

机制自动生成

gene deletion

↓

metabolic flux increase

错误。

除非论文明确说明。

---

# 工程结构

```
skills/

skill08_evidence_binding/


├── README.md

├── skill.py


├── binder/


│
├── field_locator.py

├── evidence_retriever.py

├── evidence_validator.py

├── quote_extractor.py


├── extension/


│
├── workflow_binding.py

├── variable_binding.py

├── logic_binding.py


├── conflict/


│
├── conflict_detector.py


├── schema.py

├── validator.py

├── logger.py

├── error_codes.py


├── tests/


│
├── test_field_binding.py

├── test_workflow_binding.py

├── test_variable_binding.py

├── test_missing_evidence.py

├── test_conflict.py

├── test_unknown.py


└── examples/

```

---

# Self Check

Skill结束必须执行：

## Check1

Evidence Coverage

统计：

所有字段中：

有Evidence比例。

---

## Check2

Reported Validation

reported字段：

必须存在Evidence。

---

## Check3

Quote Validation

确认：

quote支持value。

---

## Check4

Unknown Validation

unknown字段：

不能存在value。

---

## Check5

Inference Validation

inferred：

必须保存reason。

---

## Check6

Extension Validation

workflow

variables

design_logic

是否都有来源。

---

# Logging

输出：

```json
{

"skill_name":

"skill08_evidence_binding",


"paper_id":"",


"fields_processed":0,


"evidence_found":0,


"unknown_fields":0,


"inferred_fields":0,


"conflicts":0,


"errors":[]

}
```

---

# Error Handling

## EVID001

Input missing

failed

---

## EVID002

Document unavailable

failed

---

## EVID003

Evidence not found

unknown

---

## EVID004

Conflict detected

record conflict

---

## EVID005

Quote insufficient

retry

---

# Retry策略

Evidence搜索：

最多3次。

Attempt1:

当前章节

Attempt2:

全文

Attempt3:

Figure/Table/Supplement

失败：

unknown

---

# 测试要求

## Test1

Methods明确参数

期待：

reported

---

## Test2

论文没有培养时间

期待：

unknown

---

## Test3

Workflow绑定

期待：

每一步Evidence

---

## Test4

Variable绑定

期待：

independent/dependent/control均有来源

---

## Test5

Design logic没有明确描述

期待：

inferred或unknown

---

## Test6

冲突检测

期待：

conflict记录

---

# 后续接口

输出供：

Skill09

Quality Evaluation

Skill10

K12 Adaptation

Skill11

Engineering Proposal

---

# 最终验收标准

Skill08完成后必须满足：

1. 所有实验字段可追溯。

2. Evidence绑定到原文。

3. reported必须有证据。

4. unknown不能补全。

5. inferred必须解释。

6. 支持workflow evidence。

7. 支持variable evidence。

8. 支持design logic evidence。

9. 有完整日志。

10. 有测试。

---

开始实现 Skill08。

```

---

## 这一版相比原版核心提升

|部分|原版|V2|
|-|-|-|
|绑定对象|字段|字段+知识单元|
|支持Skill07 V3|❌|✅|
|workflow evidence|❌|✅|
|variable evidence|❌|✅|
|design logic evidence|❌|✅|
|extraction_method|❌|✅|
|Framework一致性|一般|高|
|后续Skill09接口|弱|强|

这版和新的 Skill07 是匹配的。后续 Skill09 也应该基于这个 Evidence-linked Knowledge Object 重新调整。:contentReference[oaicite:1]{index=1}
```

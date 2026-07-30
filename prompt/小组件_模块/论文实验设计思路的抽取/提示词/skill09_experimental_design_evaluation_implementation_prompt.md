我已经读取了你上传的原版 **Skill09【实验设计质量评估】Prompt**。

结合前面已经完成的：

* Skill07 V3：**Experimental Design Extraction（实验设计结构化抽取）**
* Skill08 V2：**Evidence Provenance Binding（证据绑定）**

原版 Skill09 最大的问题是：

> 它仍然把 Skill07 当成“实验步骤抽取结果”，而不是现在新的“Experimental Design Knowledge Object”。

所以需要升级。

---

# 一、原 Skill09 的主要问题

## 问题1：评价维度不够匹配新版 Skill07

原版主要评价：

```
Completeness
Reproducibility
Evidence
Reliability
Design Standardization
```

这些没错。

但是 Skill07 V3 新增：

* hypothesis
* workflow
* variable relationship
* design logic

因此需要增加：

* Experimental Logic Quality
* Variable Definition Quality
* Workflow Completeness
* Design Traceability

否则：

Skill07抽取了更多知识，但是Skill09完全不评价。

---

# 问题2：评价对象需要升级

原版：

```text
Experimental Design Object
```

升级：

```text
Experimental Design Knowledge Object
```

评价的不只是：

“有没有培养条件”

而是：

“这个实验设计知识是否完整、可信、可迁移”。

---

# 问题3：不能评价论文价值

这一点原版正确。

继续保持：

不评价：

* novelty
* impact factor
* scientific importance

只评价：

抽取结果质量。

---

# 问题4：评分体系需要更加透明

原版：

Completeness 40%

Evidence 30%

Reproducibility 20%

Design 10%

这个太粗。

新版建议：

```text
Field Completeness          25%

Evidence Provenance         25%

Experimental Logic          15%

Reproducibility             15%

Method Description Quality  10%

Workflow Completeness       10%
```

---

# 问题5：Risk需要重新定义

原版：

* Replication Risk
* Transfer Risk
* Interpretation Risk

其中：

Transfer Risk属于Skill10。

不应该提前评价。

Skill09应该评价：

当前论文实验设计质量。

所以修改：

保留：

* Replication Risk
* Information Missing Risk
* Interpretation Risk

Transfer Risk移到Skill10。

---

下面是优化后的完整 Prompt。

---

# Skill09 V2 Implementation Prompt

````markdown
# Skill09 Implementation Prompt


# 项目名称

论文实验设计抽取

Literature Experimental Design Extraction


---

# 当前任务


实现：

## Skill09：实验设计知识质量评估 Skill

Experimental Design Knowledge Quality Evaluation Engine


---

# 目标


基于：

Skill07:

Experimental Design Knowledge Object


以及：

Skill08:

Evidence-linked Experimental Design Object


自动评估：

当前实验设计知识的：

- 完整性
- 可追溯性
- 可信度
- 可复现程度
- 设计逻辑质量
- 信息缺失风险


输出：

结构化 Evaluation Report。


---

# Pipeline位置


Skill07

Experimental Design Extraction


↓

Skill08

Evidence Provenance Binding


↓

Skill09

Knowledge Quality Evaluation


↓

Skill10

K12 Adaptation


↓

Skill11

Engineering Proposal


---

# Skill09定位


Skill09不是：

❌ 判断论文创新性

❌ 判断论文发表价值

❌ 判断实验结果真假

❌ 替代科研人员判断


Skill09负责：


> 判断当前抽取出的实验设计知识是否足够可信，是否适合作为后续工程分析输入。


---

# 输入


来自：


## Skill07


```json
{
"experimental_design":{},

"extensions":{

"workflow":{},

"variables":{},

"design_logic":{}

}
}
````

---

## Skill08

```json
{
"evidence_map":{},

"coverage":{},

"conflicts":[]
}
```

---

# 输出

生成：

## Experimental Design Evaluation Object

结构：

```json
{
"evaluation":{

"completeness":{},

"evidence_quality":{},

"logic_quality":{},

"reproducibility":{},

"workflow_quality":{},

"risks":{},

"overall_score":0

}
}
```

---

# Evaluation Dimension 1

# Field Completeness Assessment

评价：

实验设计字段是否完整。

检查：

## Biological System

* organism
* strain
* genotype

## Engineering

* modification method
* target
* construct

## Experimental Setup

* groups
* controls
* culture conditions

## Measurement

* assay
* instrument
* analysis

## Outcome

* results

输出：

```json
{
"score":0-100,

"missing_fields":[],

"reason":""
}
```

---

# Evaluation Dimension 2

# Evidence Provenance Quality

基于Skill08。

评价：

## Evidence Coverage

字段是否有来源。

---

## Evidence Quality

来源位置：

优先级：

Methods

>

Supplement

>

Figure/Table

>

Results

---

## Evidence Status

检查：

reported

必须有Evidence。

unknown

不能有value。

inferred

必须有reason。

输出：

```json
{
"grade":"A/B/C/D",

"coverage":0.95,

"issues":[]
}
```

---

# Evaluation Dimension 3

# Experimental Logic Quality

评价：

实验设计逻辑是否完整。

检查：

是否存在：

Research Question

↓

Hypothesis

↓

Intervention

↓

Measurement

↓

Outcome

输出：

```json
{
"logic_score":0-100,

"missing_components":[],

"reason":""
}
```

---

# Evaluation Dimension 4

# Variable Definition Quality

评价：

变量是否清晰。

检查：

## Independent Variables

例如：

gene knockout

---

## Dependent Variables

例如：

production level

---

## Controlled Variables

例如：

temperature

输出：

```json
{
"variable_quality":"good",

"issues":[]
}
```

---

# Evaluation Dimension 5

# Experimental Workflow Quality

评价：

实验流程是否完整。

检查：

例如：

Construction

↓

Cultivation

↓

Measurement

↓

Analysis

输出：

```json
{
"workflow_score":0-100,

"missing_steps":[]
}
```

---

# Evaluation Dimension 6

# Reproducibility Assessment

评价：

实验是否容易被复现。

等级：

## Low Difficulty

信息充分。

---

## Medium Difficulty

部分参数缺失。

---

## High Difficulty

关键步骤缺失。

考虑：

* strain
* protocol
* condition
* replicate
* measurement

输出：

```json
{
"level":"",

"reason":[]
}
```

---

# Evaluation Dimension 7

# Method Description Quality

评价：

方法描述规范性。

检查：

* control
* replicate
* assay
* validation
* statistical analysis

输出：

```json
{
"score":0-100,

"strengths":[],

"limitations":[]
}
```

---

# Missing Information Analysis

必须输出：

所有unknown字段。

格式：

```json
{
"missing_information":[

{
"field":"culture_volume",

"importance":"high"

}

]
}
```

---

# Risk Assessment

只评价实验设计质量风险。

包括：

## Replication Risk

无法复现实验。

---

## Information Missing Risk

关键字段缺失。

---

## Interpretation Risk

实验设计无法支持明确解释。

---

禁止：

评价K12迁移风险。

该部分属于Skill10。

---

# Overall Score

评分：

```text
Field Completeness        25%

Evidence Quality          25%

Experimental Logic        15%

Reproducibility           15%

Method Quality            10%

Workflow Quality          10%
```

输出：

```json
{
"overall_score":0,

"confidence":"high/medium/low",

"recommendation":
""
}
```

---

# 工程结构

```
skills/

skill09_experimental_design_evaluation/


├── README.md

├── skill.py


├── evaluators/


├── completeness.py

├── evidence_quality.py

├── logic_quality.py

├── variable_quality.py

├── workflow_quality.py

├── reproducibility.py

├── method_quality.py


├── scoring/


├── score_calculator.py


├── risk/


├── risk_detector.py


├── schema.py

├── validator.py

├── logger.py

├── error_codes.py


├── tests/


├── test_completeness.py

├── test_evidence_grade.py

├── test_logic_quality.py

├── test_unknown_handling.py

├── test_reproducibility.py

├── test_risk.py


└── examples/
```

---

# Workflow

Step 1

读取Skill07 Knowledge Object

↓

Step 2

读取Skill08 Evidence Object

↓

Step 3

计算字段完整性

↓

Step 4

评价Evidence质量

↓

Step 5

评价实验逻辑

↓

Step 6

评价workflow

↓

Step 7

评价复现难度

↓

Step 8

生成Evaluation Report

---

# Self Check

必须执行：

## Check 1

评分依据检查

每个score必须有reason。

---

## Check 2

Evidence一致性

大量unknown：

不能得到高Evidence等级。

---

## Check 3

逻辑一致性

没有hypothesis：

不能认为logic完整。

---

## Check 4

幻觉检查

不能评价不存在的信息。

---

## Check 5

字段覆盖检查

所有unknown进入missing list。

---

# Logging

```json
{
"skill_name":

"skill09_experimental_design_evaluation",

"paper_id":"",

"fields_evaluated":0,

"evidence_coverage":0,

"logic_score":0,

"workflow_score":0,

"overall_score":0,

"errors":[]
}
```

---

# Error Handling

## EVAL001

输入缺失

failed

## EVAL002

Evidence缺失

partial_evaluation

## EVAL003

无法评分

unknown_score

## EVAL004

数据冲突

conflict_report

---

# 测试要求

## Test1

完整实验设计

期待：

high score

---

## Test2

缺少Evidence

期待：

低Evidence等级

---

## Test3

缺少hypothesis

期待：

logic下降

---

## Test4

缺少replicate

期待：

reproducibility下降

---

## Test5

大量unknown

期待：

不能获得A级

---

# 后续接口

输出供：

Skill10:

K12 Adaptation

Skill11:

Engineering Proposal

需要：

* quality score
* evidence grade
* missing information
* reproducibility level
* design logic quality

---

# 最终验收标准

Skill09完成后必须满足：

1. 评价对象是Experimental Design Knowledge。

2. 不评价论文价值。

3. 基于Evidence评价。

4. 评价实验逻辑。

5. 评价workflow。

6. 评价复现难度。

7. 输出缺失信息。

8. 输出风险。

9. 不产生幻觉。

10. 有日志和测试。

---

开始实现 Skill09。

```

---

## 相比原版的核心变化

|模块|原Skill09|新版Skill09|
|-|-|-|
|评价对象|实验方案|实验设计知识|
|Evidence|只看覆盖率|增加可信度评价|
|Logic|无|新增|
|Variables|无|新增|
|Workflow|无|新增|
|Transfer Risk|存在|移到Skill10|
|评分|粗粒度|透明权重|
|适配Skill07 V3|❌|✅|

这一版和新的 Skill07、Skill08 已经形成闭环：

```

Skill07
提取实验设计知识

↓

Skill08
绑定证据

↓

Skill09
评价知识质量

```

后面 Skill10 才负责：

> 这个高质量实验设计是否适合迁移到 E.coli K-12。

这样整个模块的数据流会更加干净。:contentReference[oaicite:1]{index=1}
```

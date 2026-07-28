我已经读取了你上传的原版 **Skill13【前端展示适配】Prompt**。

结合前面已经完成的：

* Skill07 V3：Experimental Design Extraction
* Skill08 V2：Evidence Provenance Binding
* Skill09 V2：Experimental Design Knowledge Quality Evaluation
* Skill10 V2：K12 Adaptation & Engineering Design Space Analysis
* Skill11 V2：Evidence-driven DBTL Engineering Plan Generator
* Skill12 V2：AI Quality Control & Human Governance

Skill13需要进一步升级。

原版方向是正确的：

> 将最终实验方案转换成适合Agent前端展示的数据结构；默认展示简洁步骤，详情展开显示 What / Why / How / Evidence / Risk。

但是现在前面的模块已经增加了：

* Evidence provenance
* QC status
* Human review
* Audit trail
* AI proposal level

所以 Skill13 不应该只是“格式转换”。

它应该升级为：

> **Scientific Decision Interface Adapter（科研决策界面适配层）**

---

# 一、原 Skill13 需要优化的问题

---

## 问题1：输入不完整

原版输入：

```json
engineering_plan
evidence
quality_report
review_status
audit_trail
```

方向正确。

但是还缺少：

来自 Skill10：

* K12 compatibility
* transfer risk

来自 Skill09：

* confidence score
* quality grade

这些需要展示。

---

# 问题2：前端展示对象需要分层

原版：

```
Step Card
↓
What Why How
```

正确。

但是对于科研Agent：

需要三层：

```
Level 1:
Decision Summary

Level 2:
Experiment Steps

Level 3:
Scientific Reasoning Details
```

否则用户第一次打开页面仍然信息过载。

---

# 问题3：Why来源需要拆开

现在：

Why：

混合：

* 论文依据
* AI推理
* K12适配

应该拆：

```
Why based on literature

Why based on engineering analysis

Why AI recommendation
```

避免AI推理冒充论文依据。

---

# 问题4：Evidence展示需要支持可信等级

不仅显示：

quote。

应该显示：

```
Evidence confidence

Reported / Inferred

Source paper

```

---

# 问题5：Human Governance需要成为前端一级状态

因为你们定位：

Human-Governed System。

所以前端必须显示：

```
AI generated

AI verified

Human reviewed

Human approved
```

---

# 问题6：需要支持前端折叠逻辑

这一点你的原要求非常重要：

> 保留所有关键信息，但默认简洁，详细解释折叠。

需要明确：

后端输出：

collapsed_view

expanded_view

而不是让前端自己猜。

---

下面是优化后的完整 Prompt。

---

保存：

```text
skill13_frontend_adapter_implementation_prompt_v2.md
```

---

````markdown
# Skill13 Implementation Prompt


# 项目名称

论文实验设计抽取

Literature Experimental Design Extraction


---

# 当前任务


实现：

# Skill13

前端展示适配 Skill

Scientific Decision Interface Adapter


---

# 目标


将整个论文实验设计抽取Pipeline最终输出，

转换为：

适合Agent前端展示的数据结构。


目标：

让用户能够：

1. 快速理解实验方案。

2. 查看实验设计逻辑。

3. 查看证据来源。

4. 查看风险。

5. 查看AI与Human治理状态。


---

# Pipeline位置


Skill01-12

↓

Skill13

Frontend Adapter


---

# Skill13定位


Skill13不是：

❌重新总结实验方案

❌修改科研内容

❌生成新的实验设计


它负责：

## Presentation Transformation Layer


即：

Backend Scientific Object

↓

Human-readable Decision Interface


---

# 核心原则


# 1. 信息完整性不能损失


前端展示简化：

但是：

完整数据必须保留。


---

# 2. 三层展示结构


Frontend必须支持：

---

## Level 1

Decision Summary


用户第一次看到。


包含：

- 目标
- 推荐方案概览
- K12适配程度
- 可信度
- 审核状态


---

## Level 2

Experiment Steps


实验步骤卡片。


---

## Level 3

Scientific Reasoning Details


展开查看：

- What
- Why
- How
- Evidence
- Risk


---

# 3. 默认折叠


默认：

collapsed


展开：

expanded


后端必须提供：

两套数据。


---

# 输入


来自：


Skill11:

Engineering Plan


Skill08:

Evidence Binding


Skill09:

Quality Evaluation


Skill10:

K12 Adaptation


Skill12:

Governance


输入：


```json
{

"engineering_plan":{},

"k12_analysis":{},

"evidence":{},

"quality_report":{},

"governance":{},

"audit_trail":{}

}

````

---

# 输出

生成：

## Frontend Scientific Decision Object

结构：

```json
{

"summary_view":{},

"step_cards":[],

"detail_panels":[],

"evidence_view":{},

"risk_view":{},

"governance_view":{}

}

```

---

# Module 1

# Summary View

默认展示。

字段：

```json
{

"title":"",

"objective":"",

"target_system":"E.coli K12",

"strategy_summary":"",

"k12_compatibility":"",

"confidence":"",

"review_status":""

}

```

---

# Module 2

# Experiment Step Cards

每一步生成：

Card。

结构：

```json
{

"step_id":"",

"title":"",

"short_description":"",

"source_type":"",

"status":"",

"expandable":true

}

```

默认只显示：

title

short description

---

# Module 3

# Detail Panel

展开显示：

---

## What

实验做什么。

```json
{

"what":""

}

```

---

## Why

必须拆分：

### Literature Reason

论文依据。

---

### Engineering Reason

工程逻辑。

---

### AI Reason

AI提出原因。

---

结构：

```json
{

"literature_reason":[],

"engineering_reason":[],

"ai_reason":[]

}

```

---

## How

实验执行逻辑。

包括：

* input
* operation
* output
* parameters

---

# Module 4

# Evidence View

展示：

```json
{

"source_type":"",

"paper":"",

"section":"",

"quote":"",

"confidence":"",

"status":"reported/inferred"

}

```

---

# Module 5

# Quality View

展示Skill09结果。

包括：

* completeness
* evidence quality
* reproducibility
* confidence

---

# Module 6

# K12 Adaptation View

展示Skill10结果。

包括：

* compatibility
* transferability
* risks
* validation requirement

---

# Module 7

# Risk View

展示：

包括：

## Biological Risk

## Technical Risk

## Interpretation Risk

## Transfer Risk

结构：

```json
{

"risk_level":"",

"risks":[],

"mitigation":[]

}

```

---

# Module 8

# Governance View

展示Skill12。

必须显示：

状态：

```
AI Generated

AI Checked

Human Review Pending

Human Approved

```

---

字段：

```json
{

"qc_status":"",

"review_status":"",

"approval_required":false,

"audit_events":[]

}

```

---

# AI内容标识

所有AI生成内容：

必须携带：

```json
{

"source_type":

"literature"

}

```

或者：

```json
{

"source_type":

"AI_generated"

}

```

禁止混合。

---

# 多语言支持

支持：

中文

英文

字段国际化。

例如：

What

↓

是什么

Why

↓

为什么

How

↓

怎么做

---

# 工程结构

```
skills/

skill13_frontend_adapter/


├── README.md

├── skill.py


├── adapters/


│
├── summary_adapter.py

├── step_card_adapter.py

├── evidence_adapter.py

├── risk_adapter.py

├── governance_adapter.py


├── formatter/


│
├── collapsed_formatter.py

├── expanded_formatter.py


├── i18n/


│
├── zh.json

├── en.json


├── schema.py

├── validator.py

├── logger.py

├── error_codes.py


├── tests/


├── test_summary.py

├── test_expand.py

├── test_evidence_display.py

├── test_governance.py

├── test_language.py


└── examples/

```

---

# Workflow

Step1

读取Engineering Plan

↓

Step2

读取Evidence

↓

Step3

读取Quality

↓

Step4

读取K12 Analysis

↓

Step5

读取Governance

↓

Step6

生成Summary View

↓

Step7

生成Step Cards

↓

Step8

生成Expandable Details

↓

Step9

生成Frontend JSON

---

# Self Check

## Check 1

信息完整性

确认：

每个Step都有：

What

Why

How

---

## Check 2

Evidence保持

确认：

所有Evidence仍可追踪。

---

## Check 3

Source Separation

确认：

AI内容和论文内容分离。

---

## Check 4

Governance显示

确认：

Review状态存在。

---

## Check 5

Collapsed/Expanded一致

确认：

展开不会产生新内容。

---

# Logging

```json
{

"skill_name":

"skill13_frontend_adapter",

"steps":0,

"evidence_items":0,

"governance_status":"",

"language":"",

"errors":[]

}

```

---

# Error Handling

## UI001

缺少Engineering Plan

failed

---

## UI002

Evidence不存在

显示unknown

---

## UI003

AI内容未标记

block

---

## UI004

国际化字段缺失

warning

---

# 测试要求

## Test1

完整工程方案

期待：

Summary + Step Cards

---

## Test2

点击展开

期待：

What Why How

---

## Test3

AI Proposal

期待：

AI Generated标签

---

## Test4

Evidence缺失

期待：

unknown

---

## Test5

Human Approval

期待：

正确显示状态

---

## Test6

中英文切换

期待：

字段完整

---

# 后续接口

输出：

Frontend JSON API

供：

React Agent UI

---

# 最终验收标准

Skill13完成后必须：

1. 后端数据可直接展示。

2. 默认简洁。

3. 支持展开。

4. 支持What Why How。

5. Evidence可查看。

6. Risk可查看。

7. K12适配可查看。

8. Human治理状态可查看。

9. AI和论文事实严格分离。

10. 支持中英文。

11. 有日志。

12. 有测试。

---

开始实现 Skill13。

```

---

## 相比原 Skill13 的主要升级

|部分|原版|V2|
|-|-|-|
|定位|展示转换|科研决策界面|
|输入|Skill11为主|Skill08-12全链路|
|展示层级|Step Card|Summary→Step→Reasoning|
|Why|单一解释|论文/工程/AI拆分|
|Evidence|来源展示|可信等级展示|
|K12|无|加入|
|Human Governance|弱|一级展示|
|AI标识|无|强制|
|折叠逻辑|前端决定|后端定义|

---

这样13个Skill最终形成完整闭环：

```

Skill07
实验设计知识

↓

Skill08
证据链

↓

Skill09
可信评价

↓

Skill10
K12工程空间

↓

Skill11
DBTL工程方案

↓

Skill12
Human Governance

↓

Skill13
Scientific Decision Interface

```

这才符合你们最初的产品定位：

**Persistent, Traceable, Human-Governed DBTL Engineering System**

而不是一个“论文总结Agent”。
```

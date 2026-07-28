我已经读取了你上传的原版 **Skill11【工程化实验方案生成】Prompt**。

结合目前已经完成的：

* **Skill07 V3：Experimental Design Extraction**
* **Skill08 V2：Evidence Provenance Binding**
* **Skill09 V2：Experimental Design Knowledge Quality Evaluation**
* **Skill10 V2：K12 Adaptation & Engineering Design Space Analysis**

需要对 Skill11 做一次比较大的重新定位。

---

# 一、先评价原 Skill11

原版整体方向正确：

> 基于论文证据和 K12 适配结果生成工程化实验方案，并区分论文方案和 AI 优化方案。

这个核心思想必须保留。

但是有几个问题。

---

## 问题1：Skill11和Skill10边界不够清晰

原版：

Skill10：

K12比较

↓

Skill11：

生成方案

但是新版Skill10已经升级为：

```
Literature Knowledge

↓

K12 Engineering Design Space
```

因此Skill11不应该再做：

* 多论文比较
* 适配判断

它应该只做：

> 从候选设计空间中生成具体Engineering Plan。

---

## 问题2：DBTL Mapping需要重新设计

原版直接要求：

```
Design
Build
Test
Learn
```

这是正确的。

但是需要注意：

Skill11生成的是：

**Engineering Workflow**

不是：

实验报告。

所以：

Learn阶段不能写：

“发现机制”。

应该写：

* 数据反馈
* 模型更新
* 下一轮设计输入

---

## 问题3：AI优化方案需要更加严格

原版：

允许AI生成优化。

但是需要增加：

AI建议等级。

例如：

Level 1：

已有论文支持。

Level 2：

多篇论文组合。

Level 3：

工程推理假设。

否则前端展示时容易混淆。

---

## 问题4：缺少Human Approval接口

因为Skill12存在：

Human Governance。

所以Skill11输出必须包含：

```
approval_required
```

尤其：

AI-generated方案。

---

## 问题5：实验步骤结构需要更强

现在：

```
step
action
purpose
method
risk
```

还不够。

应该增加：

* input
* output
* evidence
* validation checkpoint

因为后续Agent前端需要展示。

---

# 二、Skill11 V2定位

升级为：

# Evidence-driven DBTL Engineering Plan Generator

流程：

```
Skill10

Candidate Design Space


↓

Skill11

Engineering Plan


↓

Skill12

Human Governance


↓

Skill13

Frontend Visualization
```

---

下面是优化后的完整 Codex Prompt。

---

保存：

```text
skill11_engineering_experiment_plan_generation_implementation_prompt_v2.md
```

---

````markdown
# Skill11 Implementation Prompt


# 项目名称

论文实验设计抽取

Literature Experimental Design Extraction


---

# 当前任务


实现：

# Skill11：
工程化实验方案生成 Skill

Evidence-driven DBTL Engineering Plan Generator


---

# 目标


基于：

Skill07:

Experimental Design Knowledge


Skill08:

Evidence Provenance


Skill09:

Quality Evaluation


Skill10:

K12 Engineering Design Space


生成：

面向 E.coli K-12 工程实践的 DBTL 实验方案。


---

# Pipeline位置


Skill07

Experimental Design Extraction


↓

Skill08

Evidence Binding


↓

Skill09

Quality Evaluation


↓

Skill10

K12 Adaptation


↓

Skill11

Engineering Plan Generation


↓

Skill12

AI Governance


↓

Skill13

Frontend Adapter



---

# Skill11定位


Skill11不是：

❌ 重新分析论文

❌ 重新判断K12适配

❌ 创造新的生物学知识

❌ 自动替代科研人员


Skill11负责：

> 将已有证据支持的候选设计转化为结构化工程实验计划。


---

# 核心原则


# 1. 双轨输出机制


所有方案必须分为：


---

# Track A

## Literature-derived Experimental Plan


论文已有实验。


特点：

- 有Evidence
- 可追溯
- 已报道


字段：


```json
{
"source_type":
"reported_in_literature"
}
````

---

# Track B

## AI-generated Engineering Proposal

AI提出优化。

例如：

组合多个论文策略。

特点：

不是事实。

必须包含：

* reasoning
* supporting evidence
* uncertainty

字段：

```json
{
"source_type":
"ai_generated_proposal"
}
```

---

# 2. AI建议等级

所有AI建议必须分类：

## Level 1

直接来自论文。

---

## Level 2

多篇论文组合。

---

## Level 3

工程假设。

必须Human Review。

---

# 输入

来自：

Skill10:

Candidate Design Space

Skill07:

Experimental Design Knowledge

Skill08:

Evidence Map

Skill09:

Quality Report

输入：

```json
{

"k12_design_space":{},

"experimental_designs":[],

"evidence":[],

"quality_reports":[]

}

```

---

# 输出

生成：

## Engineering Plan Object

结构：

```json
{

"objective":{},


"design_rationale":{},


"dbtl_plan":{},


"validation_plan":{},


"risks":{},


"alternatives":{},


"approval_status":{}

}

```

---

# Module 1

# Engineering Objective

定义：

工程目标。

包括：

* target phenotype
* organism
* strain

例如：

Improve metabolite production in E.coli K12

---

# Module 2

# Design Rationale

每个方案必须回答：

## What

设计什么？

---

## Why

为什么选择？

---

## Evidence

依据什么？

---

## Limitation

限制是什么？

输出：

```json
{

"what":"",

"why":"",

"evidence":[],

"limitations":[]

}

```

---

# Module 3

# DBTL Engineering Workflow

生成：

## Design

包括：

* target gene
* engineering strategy

---

## Build

包括：

* strain construction
* genetic modification

---

## Test

包括：

* phenotype assay
* molecular validation

---

## Learn

包括：

* data interpretation
* next iteration input

---

输出：

```json
{

"design":[],

"build":[],

"test":[],

"learn":[]

}

```

---

# Module 4

# Experimental Step Generation

每一步必须包含：

```json
{

"step_id":"",

"title":"",

"source_type":"",

"what":"",

"why":"",

"how":"",

"input":[],

"output":[],

"evidence":[],

"validation_checkpoint":"",

"risk":[]

}

```

---

# Module 5

# Experimental Detail Level

达到：

可用于实验规划。

包括：

## Strain

* host
* genotype

---

## Engineering

* modification
* target

---

## Culture

* medium
* condition
* time

---

## Measurement

* assay
* instrument
* analysis

---

未知：

unknown

---

# Module 6

# Validation Plan

生成：

## Primary Validation

验证目标表型。

---

## Secondary Validation

验证机制。

---

## Control Strategy

包括：

* WT
* mutant
* complemented strain

---

# Module 7

# Risk Analysis

包括：

## Biological Risk

例如：

strain background difference

---

## Technical Risk

例如：

construction failure

---

## Interpretation Risk

例如：

phenotype unclear

---

# Module 8

# Alternative Strategy

生成：

候选替代方案。

每个方案：

包括：

* advantage
* limitation
* evidence
* validation requirement

---

# Module 9

# Human Approval Interface

输出：

```json
{

"approval_required":true,

"reason":[]

}

```

规则：

## Paper-derived

可以自动通过。

## AI-generated Level2/3

必须Human Review。

---

# AI方案生成规则

允许：

## 组合已有证据

例如：

论文A：

gene knockout

论文B：

promoter optimization

生成：

组合验证方案。

---

禁止：

## 创造新gene target

## 创造实验参数

## 创造机制

除非：

明确标记：

hypothesis。

---

# 工程结构

```
skills/

skill11_engineering_plan/


├── README.md

├── skill.py


├── planner/


│
├── objective_builder.py

├── dbtl_mapper.py

├── workflow_generator.py


├── step/


│
├── experiment_step_generator.py


├── reasoning/


│
├── rationale_generator.py


├── validation/


│
├── validation_planner.py


├── risk/


│
├── risk_analyzer.py


├── approval/


│
├── approval_router.py


├── schema.py

├── validator.py

├── logger.py

├── error_codes.py


├── tests/


├── test_reported_plan.py

├── test_ai_proposal.py

├── test_source_separation.py

├── test_dbtl.py

├── test_approval.py


└── examples/

```

---

# Workflow

Step1

读取K12 Design Space

↓

Step2

选择候选策略

↓

Step3

生成Engineering Plan

↓

Step4

区分reported和AI proposal

↓

Step5

生成DBTL流程

↓

Step6

生成validation和risk

↓

Step7

生成approval状态

↓

Step8

Self Check

---

# Self Check

## Check 1

Source Separation

确认：

论文事实和AI建议分离。

---

## Check 2

Evidence Coverage

reported步骤必须有Evidence。

---

## Check 3

AI Proposal Validation

AI建议必须有：

reason

evidence

uncertainty

---

## Check 4

DBTL完整性

确认：

Design

Build

Test

Learn

---

## Check 5

Human Governance

确认：

高风险AI建议需要review。

---

# Logging

```json
{

"skill_name":

"skill11_engineering_plan",


"reported_steps":0,


"ai_steps":0,


"evidence_coverage":0,


"approval_required":false,


"errors":[]

}

```

---

# Error Handling

## PLAN001

输入不足

partial_output

---

## PLAN002

无Evidence支持

remove_proposal

---

## PLAN003

AI建议无法解释

reject

---

## PLAN004

DBTL不完整

warning

---

# 测试要求

## Test1

论文已有方案

期待：

reported_plan

---

## Test2

AI组合方案

期待：

ai_generated_proposal

---

## Test3

无Evidence建议

期待：

删除

---

## Test4

高风险方案

期待：

approval_required

---

## Test5

完整DBTL

期待：

Design Build Test Learn

---

# 后续接口

输出供：

Skill12:

Human Governance

Skill13:

Frontend Display

需要：

* concise steps
* expandable rationale
* evidence
* risks
* approval status

---

# 最终验收标准

Skill11完成后必须满足：

1. 可以生成工程实验方案。

2. 支持DBTL流程。

3. 区分论文事实和AI建议。

4. 所有reported内容可追溯。

5. AI建议有依据。

6. 输出实验步骤。

7. 输出Why。

8. 输出Risk。

9. 支持Human Approval。

10. 有日志和测试。

---

开始实现 Skill11。

```

---

## 这一版相比原版主要变化

|模块|原版|V2|
|-|-|-|
|输入|论文方案+K12|Skill07-10完整知识链|
|定位|方案生成|DBTL工程计划生成|
|AI建议|简单区分|三级治理|
|步骤结构|action/method|What Why How + Input Output|
|Evidence|有|强化为核心|
|Human Review|无|接入Skill12|
|DBTL|有|重新规范|
|前端适配|弱|直接支持Skill13|

---

现在 Skill07-11 的逻辑已经形成：

```

Skill07
论文实验设计知识

↓

Skill08
证据链

↓

Skill09
可信度评价

↓

Skill10
K12工程设计空间

↓

Skill11
DBTL工程方案

```

这条链路才是真正符合你们最初定位：

**Persistent, Traceable, Human-Governed DBTL Engineering System。**
```

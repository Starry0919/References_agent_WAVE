我已经读取了你上传的原版 **Skill10【K12适配与实验设计比较】Prompt**。

结合前面已经完成的：

* **Skill07 V3：Experimental Design Extraction**
* **Skill08 V2：Evidence Provenance Binding**
* **Skill09 V2：Experimental Design Knowledge Quality Evaluation**

需要对 Skill10 做一次重新定位。

---

# 一、先评价原 Skill10

原版整体方向是正确的：

目标：

> 将多个论文实验方案与 E.coli K-12 目标体系比较。

这个定位没有问题。

但是存在几个接口问题。

---

## 问题1：输入没有完全适配 Skill07 V3

原版默认：

```text
Experimental Design Object
```

但是现在 Skill07 输出：

```text
Experimental Design Knowledge Object

+
workflow

+
variables

+
design_logic
```

因此 Skill10 应该利用：

* experiment logic
* variable relationship
* workflow

而不是重新阅读实验步骤。

---

## 问题2：K12适配边界需要更严格

原版容易让AI产生：

> “这个方法适合K12”

这种过度推荐。

需要明确：

Skill10只能输出：

```text
Compatibility Analysis

不是 Decision
```

也就是：

输出：

“适配程度”

而不是：

“选择方案”。

最终选择交给：

Skill11 + Human Approval。

---

## 问题3：Recommendation Space需要修改

原版：

```text
candidate ranking
```

容易变成自动决策。

建议改成：

```text
candidate design space
```

即：

产生候选空间，不排序替代人。

---

## 问题4：缺少基于Skill09质量权重

现在：

论文A

论文B

论文C

直接比较。

但是：

低质量论文不能和高质量论文同等权重。

应该加入：

Skill09:

* evidence grade
* completeness score
* reproducibility

作为比较输入。

---

## 问题5：需要增加“目标一致性判断”

你要求：

> K12和目标相同，但方法不同，并列比较。

所以必须先判断：

两个论文是否：

same engineering objective

例如：

论文A：

提高乳酸产量

论文B：

提高蛋白表达

不能放一起比较。

需要增加：

Objective Similarity。

---

# 二、Skill10 V2最终定位

升级为：

# K12 Adaptation & Engineering Design Space Analysis Engine

不是：

论文比较器。

而是：

```
多个实验知识

↓

目标一致性筛选

↓

标准化比较

↓

K12适配分析

↓

迁移风险分析

↓

候选设计空间
```

---

下面是优化后的完整 Codex Prompt。

---

保存：

```text
skill10_k12_adaptation_comparison_implementation_prompt_v2.md
```

---

````markdown
# Skill10 Implementation Prompt


# 项目名称

论文实验设计抽取

Literature Experimental Design Extraction


---

# 当前任务


实现：

# Skill10：
K12适配与实验设计比较 Skill

K12 Adaptation & Engineering Design Space Analysis Engine


---

# 目标


针对：

E.coli K-12 工程体系


将多个论文中的实验设计知识进行：

1. 目标一致性判断

2. 实验策略标准化

3. K12适配分析

4. 工程迁移风险分析


最终生成：

K12 Engineering Design Space


---

# Pipeline


Skill07

Experimental Design Extraction


↓

Skill08

Evidence Provenance Binding


↓

Skill09

Experimental Design Quality Evaluation


↓

Skill10

K12 Adaptation Analysis


↓

Skill11

Engineering Experimental Proposal



---

# Skill10定位


Skill10不是：


❌ 自动选择最佳方案


❌ 生成最终实验方案


❌ 替代科研人员决策


❌ 修改论文实验事实


---

Skill10负责：

> 分析已有实验设计知识在目标K12体系中的适配可能性。


---

# 核心原则


## 1. Paper Fact 与 AI Analysis严格分离


必须区分：


## Literature Evidence


论文事实：

例如：

论文使用：

BL21(DE3)


---

## K12 Adaptation Analysis


AI分析：

例如：

BL21与K12背景不同，需要验证。


---

禁止：

把AI分析写成论文事实。


---

# 2. 不自动推荐


输出：

candidate design space


而不是：

best strategy。


---

# 3. 所有判断必须有依据


Compatibility:

必须基于：

- strain similarity
- engineering similarity
- evidence quality
- validation requirement


---

# 输入


来自：


## Skill07

Experimental Design Knowledge Object


## Skill08

Evidence Object


## Skill09

Quality Evaluation


输入：


```json
{

"experimental_designs":[],

"evidence_objects":[],

"quality_reports":[],

"target_system":{

"organism":"Escherichia coli",

"strain_family":"K-12"

}

}
````

---

# 输出

生成：

## K12 Adaptation Comparison Object

结构：

```json
{

"objective_clusters":[],

"comparison_matrix":[],

"k12_analysis":[],

"risk_assessment":[],

"candidate_design_space":[]

}
```

---

# Module 1

# Objective Similarity Analysis

首先判断论文是否属于同一工程目标。

例如：

同类：

提高目标产物

不同：

提高耐受性

输出：

```json
{

"objective_cluster":"",

"similarity_score":0-1

}

```

禁止：

不同目标强行比较。

---

# Module 2

# Experimental Strategy Normalization

统一不同论文表示。

比较：

## Engineering Goal

例如：

increase production

---

## Intervention

例如：

gene knockout

---

## Target

gene/pathway

---

## Mechanism

论文明确机制。

---

## Measurement

检测方法。

---

输出：

Comparison Matrix。

---

# Module 3

# Standardized Comparison Matrix

字段：

## Literature

* paper_id
* year

---

## Biological System

* organism
* strain
* genotype

---

## Engineering Strategy

* modification type
* target
* tool

---

## Experimental Design

* groups
* controls
* conditions

---

## Measurement

* assay
* instrument

---

## Quality

来自Skill09：

* evidence grade
* completeness
* reproducibility

---

# Module 4

# K12 Compatibility Analysis

目标：

评价论文方案迁移到K12可能性。

---

评价维度：

## Strain Similarity

比较：

论文菌株

↓

K12

考虑：

* genome background
* metabolism
* regulation

等级：

High

Medium

Low

---

## Engineering Tool Compatibility

例如：

某基因编辑方法是否适用于K12。

---

## Phenotype Transferability

评价：

表型是否依赖原菌株背景。

---

输出：

```json
{

"compatibility":"medium",

"reason":[]

}

```

---

# Module 5

# Engineering Transferability Assessment

分类：

## Direct Transfer

直接参考。

---

## Requires Optimization

需要优化。

---

## Requires Revalidation

需要重新验证。

---

输出：

```json
{

"transferability":"",

"validation_needed":[]

}

```

---

# Module 6

# Tradeoff Analysis

比较：

## Advantage

例如：

高产量

---

## Limitation

例如：

生长缺陷

---

## Engineering Complexity

例如：

构建步骤多

---

## Validation Requirement

例如：

需要omics验证

---

# Module 7

# Migration Risk Assessment

评价：

迁移风险。

包括：

## Biological Risk

菌株背景差异。

---

## Engineering Risk

构建失败风险。

---

## Measurement Risk

检测体系差异。

---

输出：

```json
{

"risk_level":"",

"risks":[]

}

```

---

# Module 8

# Candidate Design Space

注意：

不是推荐。

只是生成候选空间。

例如：

```json
{

"candidate_strategy":

"gene knockout strategy",


"supporting_evidence":"",

"k12_compatibility":"medium",

"validation_required":[]

}

```

---

# 不允许行为

禁止：

## 1

BL21有效

↓

自动认为K12有效。

---

## 2

高产量

↓

自动推荐。

---

## 3

缺少菌株信息

↓

补充菌株特点。

---

## 4

AI分析冒充论文结果。

---

# 工程结构

```
skills/

skill10_k12_adaptation/


├── README.md

├── skill.py


├── objective/


│
├── similarity.py


├── comparison/


│
├── normalizer.py

├── matrix_builder.py


├── adaptation/


│
├── strain_similarity.py

├── compatibility.py

├── transferability.py


├── risk/


│
├── migration_risk.py


├── candidate/


│
├── design_space_builder.py


├── schema.py

├── validator.py

├── logger.py

├── error_codes.py


├── tests/


├── test_objective_similarity.py

├── test_strain_analysis.py

├── test_transferability.py

├── test_risk.py

├── test_no_recommendation.py


└── examples/

```

---

# Workflow

Step1

读取多个实验设计知识对象

↓

Step2

目标聚类

↓

Step3

实验策略标准化

↓

Step4

比较矩阵生成

↓

Step5

K12适配分析

↓

Step6

迁移风险分析

↓

Step7

生成candidate design space

↓

Step8

Self Check

---

# Self Check

## Check 1

目标一致性

不同目标不能比较。

---

## Check 2

事实隔离

论文事实和AI分析分开。

---

## Check 3

Evidence检查

所有Compatibility判断必须有依据。

---

## Check 4

质量权重检查

低Evidence方案不能被过度推荐。

---

## Check 5

幻觉检查

未知信息必须unknown。

---

# Logging

```json
{

"skill_name":

"skill10_k12_adaptation",


"papers_processed":0,


"objective_clusters":0,


"comparisons_generated":0,


"k12_assessments":0,


"risks_identified":0,


"errors":[]

}

```

---

# Error Handling

## K12_001

目标体系缺失

request configuration

---

## K12_002

菌株信息缺失

unknown

---

## K12_003

目标不一致

exclude comparison

---

## K12_004

无法判断适配性

unknown

---

# 测试

## Test1

多个K12相关论文

期待：

比较矩阵。

---

## Test2

BL21迁移K12

期待：

risk。

---

## Test3

目标不同论文

期待：

不比较。

---

## Test4

缺少菌株信息

期待：

unknown。

---

## Test5

低Evidence论文

期待：

降低权重。

---

# 后续接口

输出供：

Skill11:

Engineering Experimental Proposal

需要：

* candidate strategies
* advantages
* limitations
* risks
* validation requirements

---

# 最终验收标准

Skill10完成后必须：

1. 支持多论文比较。

2. 支持目标一致性判断。

3. 支持K12适配分析。

4. 支持迁移风险分析。

5. 区分事实和AI分析。

6. 不自动替代科研决策。

7. 结合Skill09质量评价。

8. 输出candidate design space。

9. 有日志。

10. 有测试。

---

开始实现 Skill10。

```

---

## 这一版相比原版主要变化

|部分|原版|V2|
|-|-|-|
|比较对象|论文实验方案|实验设计知识|
|输入|Skill07|Skill07+08+09|
|K12适配|有|增强|
|质量权重|无|加入Skill09|
|目标一致性|无|新增|
|推荐|candidate ranking|candidate design space|
|迁移风险|简单|结构化|
|DBTL衔接|弱|强|

这样 Skill10 才真正成为：

```

Literature Knowledge Layer

```
    ↓
```

K12 Engineering Design Space

```
    ↓
```

Skill11 Engineering Proposal

```

之间的桥梁。:contentReference[oaicite:2]{index=2}
```

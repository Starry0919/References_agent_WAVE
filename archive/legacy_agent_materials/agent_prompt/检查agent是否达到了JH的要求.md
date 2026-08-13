下面是经过重新自检后的**最终版 Prompt**。

相比上一版，我做了以下调整：

* 删除了不属于老师 Work A 核心要求的强制开发项；
* 保留并强化老师最关注的：

  * DDR（Decision Design Record）
  * 决策链重建
  * 证据等级
  * 理由性质
  * 规则蒸馏
  * 防止事后合理化污染规则库
  * 理性设计边界
  * 人工策展 → 半自动扩展路线
* 要求 Claude **先审查，再修改**，避免破坏已有系统；
* 允许 Claude 自主优化代码，但必须说明每个修改对应老师设计文档哪一条要求。

你可以直接复制给 Claude Code。

---

```markdown
# Role

You are a senior AI system architect, synthetic biology knowledge engineer, and experienced full-stack engineer.

You are responsible for reviewing and upgrading the current project:

Repository:
References_agent_WAVE

Project goal:

Transform the current literature experimental design extraction system into a synthetic biology expert decision reverse-engineering system.

Your task is NOT simply:

"check whether the code works"

Your task is:

> Compare the current Work A implementation against the final synthetic biology expert Agent design document:
>
> "260718-合成生物专家 Agent 平台_设计思路.md"

Then identify missing capabilities and autonomously improve the implementation where necessary.

You should think like the engineer responsible for preparing this module for integration into a real synthetic biology rational design Agent.

---

# Important Scientific Understanding

First understand the fundamental difference:

The target system is NOT a paper summarization system.

It is NOT only extracting:

- which genes were modified
- which enzymes were overexpressed
- which experimental steps were performed


The target system should reconstruct:

How synthetic biology experts make engineering decisions.

The desired reasoning chain is:

```

Engineering objective

↓

Observed biological problem

↓

Hypothesis

↓

Evidence supporting the hypothesis

↓

Candidate engineering interventions

↓

Why one intervention was selected

↓

Implementation method

↓

Experimental validation

↓

Transferable engineering rule

```

The final output of Work A should become the foundation for:

- DDR (Decision Design Record)
- synthetic biology rule library
- future rational strain design Agent

---

# Phase 1 — Repository Understanding

Before modifying anything:

Inspect the complete repository.

Understand:

1. Project architecture

2. Current workflow

3. Existing extraction pipeline

4. Existing skills/modules

5. Prompt templates

6. Data schemas

7. JSON structures

8. Storage/database design

9. Frontend/backend interfaces if present

10. Existing tests


Create an internal understanding:

```

Current pipeline:

Input paper

↓

Processing

↓

Extraction steps

↓

Structured output

↓

Storage

↓

Frontend/API

```


Do not modify code during this phase.

---

# Phase 2 — Extract Work A Requirements From Design Document

Read:

260718-合成生物专家 Agent 平台_设计思路.md


Only focus on:

"工作 A：文献逆向工程"


Build a requirement checklist.

The checklist must include:

---

# Requirement 1

## The purpose of Work A

The system should extract:

NOT:

"experimental procedure"

BUT:

"expert decision trajectory"

A paper should be represented as:

```

What did researchers want to achieve?

↓

What limitation did they observe?

↓

What hypothesis did they propose?

↓

What evidence supported the hypothesis?

↓

What engineering decision did they make?

↓

How was it implemented?

↓

What was the outcome?

↓

What general principle can be reused?

````

---

# Requirement 2

## DDR (Decision Design Record)

Check whether the current implementation supports a Decision Design Record.

Each engineering decision should contain:

```json
{
"design_action":"",
"target":"",
"trigger":"",
"evidence":"",
"evidence_level":"",
"reason_type":"",
"alternative":"",
"implementation":"",
"result":"",
"rule":""
}
````

Meaning:

---

## design_action

What type of engineering action was performed?

Examples:

* feedback regulation removal
* enzyme engineering
* pathway balancing
* competitive pathway deletion
* fermentation optimization

---

## target

The biological target:

* gene
* enzyme
* pathway
* regulatory element
* culture condition

---

## trigger

The most important missing element.

It should answer:

"What observation caused researchers to make this decision?"

Example:

Incorrect:

```
Researchers mutated trpE.
```

Correct:

```
Increasing upstream pathway expression failed to improve production,
suggesting feedback inhibition limited pathway flux.
```

---

## evidence

Evidence must include:

* experimental evidence
* numerical results
* structural evidence
* kinetic evidence
* computational evidence

with source traceability.

---

## evidence_level

The system must distinguish:

HARD evidence:

Examples:

* experimentally validated engineering results
* measured production improvement
* kinetic parameters
* structural evidence

SOFT evidence:

Examples:

* FBA prediction
* OptKnock prediction
* docking
* AlphaFold
* FoldX

Soft evidence must never be treated as equivalent to experimental validation.

---

## reason_type

The system must distinguish:

```
mechanistic_reasoning

literature_analogy

available_resource

screening_based

post_hoc_explanation
```

Important:

The system MUST NOT force every engineering modification into a mechanistic explanation.

---

# Scientific Constraint: Avoid False Reasoning

Not every paper contains a clean decision chain.

Many engineering choices may come from:

* previous literature
* available strains
* existing libraries
* screening results
* empirical observations

The system must preserve this information honestly.

For example:

If a knockout was discovered through random screening:

Correct:

```
reason_type:
screening_based

rule_generation:
not allowed
```

Incorrect:

```
Gene X improves production because it regulates metabolism.
```

when the paper never demonstrated that.

Do not contaminate the rule library with invented explanations.

---

# Requirement 3

## Separate Paper Knowledge and Transferable Knowledge

The system must maintain two levels:

Layer 1:

Paper-specific DDR

Example:

```
Chen 2018

TrpE feedback mutation

Observed:
feedback inhibition

Action:
TrpE mutation

Result:
production increased
```

Layer 2:

Transferable engineering rule

Example:

```
For natural product production:

First inspect committed enzymes
for feedback inhibition.

Evidence:
multiple papers

Confidence:
high
```

Do not mix these two layers.

---

# Requirement 4

## Rule Distillation

The final goal of Work A is not only extracting papers.

It is building reusable synthetic biology knowledge.

Rules should only be generated when:

reason_type:

* mechanistic_reasoning

OR

* reliable literature analogy

Rules should NOT be generated from:

* screening_based
* available_resource
* post_hoc_explanation

---

# Requirement 5

## Evidence Traceability

Every DDR entry must be traceable to:

* paper
* section
* original evidence
* evidence type

Unsupported claims should not enter the knowledge base.

---

# Requirement 6

## Rational Design Scope

The system focuses on:

rational synthetic biology engineering decisions.

Do not treat:

* adaptive laboratory evolution
* random mutagenesis
* unexplained evolutionary outcomes

as equivalent to rational expert reasoning.

These can be recorded,
but should not generate mechanistic rules.

---

# Requirement 7

## Human Calibration Workflow

The design document proposes:

First:

3-5 manually curated high-quality papers

Then:

Independent extraction

↓

Comparison

↓

Annotation alignment

↓

Semi-automatic expansion

Do not optimize only for extraction quantity.

High-quality expert reasoning examples are more important.

---

# Phase 3 — Current System Evaluation

Now compare:

CURRENT IMPLEMENTATION

against:

TARGET REQUIREMENTS

Create:

```
Requirement

Current status

Evidence from code

Missing capability

Impact

Suggested improvement

Priority
```

Priority:

P0:
Core requirement missing

P1:
Important improvement

P2:
Optimization

---

# Phase 4 — Autonomous Improvement

After completing gap analysis:

Improve the implementation.

Rules:

---

## Rule 1

Do not rewrite the whole system.

Preserve:

* working workflow
* existing APIs
* existing extraction ability
* existing tests

---

## Rule 2

Prefer incremental upgrades.

Possible improvements:

* improve data schema
* add DDR fields
* add evidence classification
* add reason classification
* add rule extraction constraints
* improve validation
* improve output format

Only implement changes that improve alignment with Work A requirements.

---

## Rule 3

Every modification must include:

```
Modification:

Why needed:

Corresponding design requirement:

Impact:
```

---

# Suggested Improvements If Missing

## 1. DDR Schema Improvement

Ensure the structured output can represent:

```json
{
"paper_id":"",
"objective":"",
"design_action":"",
"target":"",
"trigger":"",
"evidence":[],
"evidence_level":"",
"reason_type":"",
"alternative":"",
"implementation":"",
"result":"",
"rule":"",
"confidence":""
}
```

---

## 2. Evidence Classification

Improve the system so evidence can be classified as:

```
HARD

SOFT

UNKNOWN
```

---

## 3. Reason Classification

Improve automatic classification:

```
mechanistic_reasoning

literature_analogy

available_resource

screening_based

post_hoc_explanation
```

---

## 4. Rule Generation Control

Ensure:

Only reliable reasoning generates reusable rules.

The system should be conservative.

It is better to output:

"No transferable rule generated"

than:

generate an incorrect biological principle.

---

# Phase 5 — Validation

After modification:

Run existing tests.

Add validation cases if possible.

Recommended cases:

## Case 1

A complete rational engineering paper.

Expected:

System extracts:

* trigger
* evidence
* engineering decision
* evidence level
* reusable rule

---

## Case 2

A screening-based engineering paper.

Expected:

System identifies:

screening_based

and does NOT generate mechanistic rule.

---

## Case 3

A computational prediction paper.

Expected:

Prediction marked as SOFT evidence.

---

# Phase 6 — Final Report

Generate:

```
WORK_A_ALIGNMENT_REPORT.md
```

Include:

## 1.

Current Work A architecture

## 2.

Requirement checklist

## 3.

Gap analysis

## 4.

Implemented improvements

## 5.

Modified files

## 6.

Before vs After comparison

## 7.

Remaining limitations

## 8.

Final evaluation:

Choose one:

NOT READY

PARTIALLY READY

READY FOR INTEGRATION

Explain the reasoning.

---

# Final Objective

Your final goal is:

Upgrade:

"Literature experimental design extraction system"

into:

"Synthetic biology expert decision reverse-engineering knowledge engine"

Do not optimize for generating more text.

Optimize for:

accurate reconstruction of expert biological reasoning.

Begin with repository inspection.

```

---

这一版相比上一版更符合老师文档的核心思想：

**不是让 Claude 做一个更强的论文总结器，而是让它把 Work A 变成“合成生物专家经验蒸馏系统”。**

执行后 Claude 应该首先给出 gap analysis，然后再修改代码，而不是一上来大规模重构。
```

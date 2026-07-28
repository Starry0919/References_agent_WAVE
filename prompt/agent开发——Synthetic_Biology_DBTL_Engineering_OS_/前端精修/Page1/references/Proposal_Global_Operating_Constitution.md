> **Relocation note (Spec Package normalization, 2026-07-23)**
>
> This file was originally stored at `Page1/03_Operating_Principles.md`. Its content is not a Page 1
> Interaction Spec. It is a discussion draft proposing a single, **cross-page / global** "Operating
> Constitution" document intended to be referenced by Page1, Page2, Page3, and Page4 alike (see the
> author's own closing note in the text below: "这份文档已经不再属于某个页面，而是整个项目唯一的
> Operating Constitution").
>
> Per Page Design Contract v1.2.0 §74 (Required Directory) and §75 (Spec Header), a page-specific
> package must contain `03_Interaction_Spec.md`, not a global constitution proposal. This file has
> therefore been moved here, verbatim and unmodified, so that:
>
> 1. the required `Page1/03_Interaction_Spec.md` slot can be created without ambiguity;
> 2. none of the original thinking is discarded;
> 3. the proposal remains available for a future Design_System-level DSR/ADR decision, should the
>    product/architecture owners choose to formalize a global Operating Constitution under
>    `Design_System/decisions/` per Contract §104.
>
> This document carries **no normative status** for Page 1 or any other page until adopted through
> the Contract's formal decision-record process. Nothing below this line has been edited.
>
> ---

我赞成直接提升，而且我建议**这是整个前端设计中唯一一份"不可修改"的文档**。

但是，我不会叫它 **Behavior_and_Interaction_Operating_Principles**。

因为它还是太偏 Interaction。

---

## 我建议最终命名

```
Design_System/

03_Operating_Principles.md
```

副标题：

```
The Operating Constitution of the Synthetic Biology DBTL Engineering OS
```

一句话：

> This document defines how the Operating System thinks, behaves, collaborates, evolves and governs itself.

这句话很重要。

因为以后：

Page1

Page2

Page3

Page4

全部都引用它。

---

# 为什么升级？

我们现在其实已经不是在设计网页。

而是在设计一个

**Scientific Operating System**

操作系统里面最重要的不是UI。

而是：

Operating Principles。

例如：

Linux

有POSIX

Apple

有Human Interface Guidelines

Material

有Design Principles

Kubernetes

有Design Proposal

我们的

也应该有

Operating Constitution。

---

# 我建议最终版目录（V5 Ultimate）

```
03_Operating_Principles.md

======================================================

PART I
SYSTEM PHILOSOPHY

00 Vision
01 System Identity
02 Scientific Philosophy
03 Human-Centered Philosophy
04 Product Principles

======================================================

PART II
OPERATING MODEL

05 Operating Model
06 Cognitive Model
07 Scientific Thinking Model
08 Decision Model
09 Trust Model

======================================================

PART III
SYSTEM BEHAVIOR

10 Behavioral Principles
11 Interaction Principles
12 Attention Model
13 Context Preservation
14 Progressive Disclosure

======================================================

PART IV
SCIENTIFIC OBJECT SYSTEM

15 Scientific Object Model
16 Object Lifecycle
17 Object Relationships
18 Object State Machine
19 Object Ownership

======================================================

PART V
HUMAN + AGENT

20 Agent Responsibility
21 Human Responsibility
22 Collaboration Model
23 Approval Model
24 Intervention Policy

======================================================

PART VI
WORKSPACE MODEL

25 Navigation Philosophy
26 Workspace Philosophy
27 Cross-page Continuity
28 Workspace Persistence

======================================================

PART VII
TRUST

29 Evidence-first Principle
30 Transparency Principle
31 Explainability Principle
32 Traceability Principle
33 Scientific Credibility

======================================================

PART VIII
INTERACTION LANGUAGE

34 Feedback Philosophy
35 Motion Philosophy
36 Notification Philosophy
37 Recovery Philosophy

======================================================

PART IX
EVOLUTION

38 Extension Rules
39 Forbidden Behaviors
40 Evolution Principles

======================================================

PART X
OPERATING CONSTITUTION
```

可以发现。

Interaction

已经只是其中一章。

整个系统真正表达的是：

Operating。

---

# 我建议升级点①

## PART I

System Philosophy

不要写：

Mission。

写：

为什么这个OS存在。

例如：

```
Scientific engineering is no longer limited by biological knowledge.

It is increasingly limited by the ability of humans to organize knowledge,
evaluate evidence, coordinate engineering decisions, and maintain trust across
iterative Design–Build–Test–Learn cycles.

The Synthetic Biology DBTL Engineering OS exists to become the operational layer
that coordinates these activities.

It does not replace scientists.

It augments scientific reasoning.

It does not automate decisions.

It makes better decisions possible.

Its purpose is to transform fragmented engineering activities into a persistent,
traceable, evidence-driven scientific operating system.
```

整个网站都有灵魂了。

---

# 我建议升级点②

## Operating Model

整个OS到底怎么运行。

例如：

```
Project

↓

Iteration

↓

Goal

↓

Knowledge

↓

Diagnosis

↓

Engineering Design

↓

Simulation

↓

Validation

↓

Learning

↓

Knowledge Update

↓

Next Iteration
```

以后所有页面围绕这个。

---

# 我建议升级点③

## Scientific Thinking Model

整个网站必须遵守科研人员脑回路。

例如：

```
Observe

↓

Understand

↓

Explain

↓

Predict

↓

Compare

↓

Decide

↓

Validate

↓

Learn
```

而不是：

```
Sidebar

↓

Page

↓

Button

↓

Dialog
```

这是两个层次。

---

# 我建议升级点④

## Scientific Object Model

整个网站真正运行的是：

Scientific Objects。

不是UI。

例如：

```
Project

Iteration

Objective

Hypothesis

Bottleneck

Engineering Proposal

Evidence

Paper

Knowledge

Rule

Experiment

Simulation

Protocol

Validation

Decision

Approval

Report
```

以后所有页面统一。

---

# 我建议升级点⑤

## Agent Responsibility

Agent不是万能。

例如：

Agent负责：

```
Understand

Retrieve

Summarize

Diagnose

Predict

Recommend

Explain
```

Agent永远不负责：

```
Approve

Execute

Modify Project

Override Human

Hide Evidence
```

整个网站不会跑偏。

---

# 我建议升级点⑥

## Human Responsibility

Human负责：

```
Review

Approve

Reject

Prioritize

Interpret

Own Scientific Decisions
```

以后Claude不会设计成自动Agent。

---

# 我建议升级点⑦

## Trust Model

Trust不是一句话。

应该拆开。

例如：

```
Trust

↓

Evidence

↓

Transparency

↓

Traceability

↓

Explainability

↓

Human Governance
```

以后整个产品气质都会不同。

---

# 我建议升级点⑧

## Motion Philosophy

Motion不是动画。

例如：

```
Expand

↓

Discover

Collapse

↓

Focus

Transition

↓

Continuity

Highlight

↓

Attention

Loading

↓

Expectation
```

Motion表达科学意义。

不是酷。

---

# 我建议升级点⑨

## Evolution Principles

以后任何新增功能。

必须满足：

```
Improve Scientific Understanding

OR

Improve Engineering Decision

OR

Improve Traceability

OR

Improve Human Governance
```

否则：

Reject。

以后Claude不会乱加。

---

# 最后一章

## Operating Constitution

这是整个项目最重要。

我建议直接固定。

```
The principles defined in this document are immutable.

Every page, component, workflow, animation, API integration,
interaction pattern and future feature must comply with this constitution.

The operating system shall always prioritize:

Scientific reasoning over automation.

Evidence over assumptions.

Transparency over convenience.

Human governance over autonomous execution.

Context preservation over interface simplification.

Trust over intelligence.

Traceability over efficiency.

Every interaction must strengthen scientific understanding.

Every object must remain explainable.

Every recommendation must remain reviewable.

Every engineering decision must remain attributable.

If a future feature violates any of these principles, the feature shall be rejected regardless of its technical feasibility.

The identity of the Synthetic Biology DBTL Engineering OS is therefore immutable:

Persistent.

Traceable.

Evidence-driven.

Human-governed.

Scientifically rigorous.

Collaborative.

Explainable.

Trustworthy.

The system exists not to replace scientists, but to become the operating environment in which scientists can make better engineering decisions.
```

---

# **这就是我认为的最终版（V6 Ultimate）。**

这份文档已经**不再属于某个页面**，而是整个项目唯一的**Operating Constitution（操作系统宪法）**。之后的所有设计文档都可以简化并引用它：

```
Design_System/
│
├── 01_Product_Principles.md
├── 02_Visual_System.md
├── ⭐ 03_Operating_Principles.md   ← 最高层规范（唯一行为宪法）
├── 04_Component_System.md
├── 05_Scientific_Object_Model.md
├── 06_API_Contracts.md
└── 07_Coding_Convention.md
```

我的建议是：**从这里开始，不再继续升级这一份文档。**后续所有时间都投入到具体页面（Page 1、Page 2……）的设计，因为这份《03_Operating_Principles.md》已经足够作为整个 Synthetic Biology DBTL Engineering OS 的最高设计约束与长期演进基石。

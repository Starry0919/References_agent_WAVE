我认为 **Page2（DBTL Engineering Workspace）** 的 **01_Product_Spec.md**，应该是整个网站最重要的一份 Product Spec。

原因很简单：

整个系统真正工作的地方，不是 Page1。

而是：

> **Page2 = Scientific Engineering Workspace**

它决定了：

整个 Agent 到底是不是一个真正的 **Engineering OS**。

---

但是，我觉得它**不能按照普通 Product Spec 去写**。

因为：

普通 Product Spec：

```text
Mission

Users

User Story

Goals

Features
```

对于Claude来说还是太浅。

---

我建议继续升级。

直接把 Product Spec 提升成：

# Engineering Workspace Product Constitution

它不是描述：

页面。

而是定义：

**Engineering Workspace 为什么存在。**

---

# 我建议最终目录

```text
01_Product_Spec.md

=====================================================

PART I
WORKSPACE IDENTITY

00 Vision
01 Mission
02 Scientific Position
03 Why This Workspace Exists

=====================================================

PART II
ENGINEERING PHILOSOPHY

04 Engineering Principles
05 DBTL Philosophy
06 Human + AI Philosophy
07 Scientific Decision Philosophy

=====================================================

PART III
PRODUCT PURPOSE

08 Primary Scientific Question
09 Primary User Goal
10 Workspace Responsibilities
11 Explicit Non-goals

=====================================================

PART IV
USERS

12 Personas
13 Jobs To Be Done
14 User Journey
15 Collaboration Model

=====================================================

PART V
ENGINEERING WORKFLOW

16 Engineering Lifecycle
17 Stage Responsibilities
18 Stage Inputs
19 Stage Outputs
20 Stage Success Criteria

=====================================================

PART VI
SCIENTIFIC OBJECT MODEL

21 Core Objects
22 Object Relationships
23 Object Lifecycle
24 Workspace Context

=====================================================

PART VII
DECISION MODEL

25 Decision Types
26 Evidence Model
27 Approval Model
28 Risk Model
29 Tradeoff Model

=====================================================

PART VIII
SUCCESS METRICS

30 Product Success
31 Scientific Success
32 User Success
33 Engineering Success

=====================================================

PART IX
BOUNDARIES

34 Dependencies
35 Non-goals
36 Failure Modes
37 Future Evolution

=====================================================

PART X
PRODUCT CONSTITUTION
```

---

# 第一部分

## Workspace Identity

建议不是：

Mission。

而是：

为什么世界上需要它。

例如：

```md
The DBTL Engineering Workspace is the primary operating environment of the Synthetic Biology DBTL Engineering Operating System.

Its purpose is not to execute isolated AI functions.

Its purpose is to support one continuous engineering decision from diagnosis to experimental validation.

The workspace persists scientific context, preserves evidence, and guides researchers through the complete DBTL lifecycle.
```

整个定位直接不同。

---

# 第二部分

## Engineering Philosophy

建议直接固定：

整个Workspace遵循：

```text
Diagnosis

↓

Design

↓

Simulation

↓

Scientific Critique

↓

Build/Test Plan
```

不是：

五个按钮。

而是：

一个Decision。

---

# 第三部分

## Primary Scientific Question

这是我认为必须新增。

整个页面：

唯一回答：

```text
How should this strain be engineered next?
```

不是：

展示很多东西。

而是：

帮助回答这一个问题。

以后Claude不会发散。

---

# 第四部分

## Workspace Responsibilities

建议直接固定：

负责：

```text
Diagnose

↓

Design

↓

Compare

↓

Evaluate

↓

Approve

↓

Generate Build/Test Plan
```

不负责：

```text
Knowledge Browsing

Project Dashboard

System Settings

Audit History
```

全部交给其它页面。

---

# 第五部分

## Jobs To Be Done

建议不要普通JTBD。

而是：

按角色。

例如：

PI：

```text
Understand

Approve

Reject
```

Researcher：

```text
Diagnose

Engineer

Compare

Iterate
```

Wet Lab：

```text
Receive

Build

Validate
```

Dry Lab：

```text
Simulate

Analyze

Improve
```

---

# 第六部分

## Engineering Lifecycle

建议固定：

```text
Observe

↓

Diagnose

↓

Hypothesize

↓

Design

↓

Simulate

↓

Evaluate

↓

Approve

↓

Build

↓

Test

↓

Learn
```

以后所有页面一致。

---

# 第七部分

## Stage Responsibilities

每个Stage：

固定：

例如：

Diagnosis：

输入：

```text
Observation

Dataset

Knowledge

```

输出：

```text
Bottleneck
```

Design：

输入：

```text
Bottleneck

Knowledge

Rules
```

输出：

```text
Engineering Proposal
```

Simulation：

输出：

```text
Prediction
```

Critique：

输出：

```text
Tradeoffs
```

Build/Test：

输出：

```text
Validated Plan
```

Claude以后不会乱。

---

# 第八部分

## Scientific Object Model

整个Workspace：

只围绕：

```text
Engineering Decision
```

其它：

都是附属。

例如：

```text
Engineering Decision

↓

Hypothesis

↓

Evidence

↓

Simulation

↓

Critique

↓

Approval

↓

Plan
```

而不是：

很多Card。

---

# 第九部分

## Decision Model

这是整个Agent最重要。

建议新增：

```text
Observation

↓

Evidence

↓

Diagnosis

↓

Proposal

↓

Simulation

↓

Comparison

↓

Approval

↓

Execution
```

Claude以后不会：

直接：

Diagnosis

↓

Execution。

---

# 第十部分

## Risk Model

任何Proposal：

必须：

展示：

```text
Expected Gain

↓

Scientific Risk

↓

Engineering Cost

↓

Confidence

↓

Evidence
```

以后：

整个Agent都有Tradeoff。

---

# 第十一部分

## Success Metrics

不是：

PV。

而是：

例如：

PI：

30秒。

知道：

```text
Current Bottleneck

↓

Current Proposal

↓

Current Risk

↓

Next Action
```

Researcher：

5分钟。

理解：

整个Decision。

---

# 第十二部分

## Failure Modes（新增）

这是Claude最容易遗漏。

例如：

失败：

包括：

```text
Wrong Diagnosis

↓

Weak Evidence

↓

No Approval

↓

No Traceability

↓

No Tradeoff

↓

Context Lost
```

以后Claude：

知道：

什么叫失败。

---

# 最后一章

## Product Constitution

建议固定：

```md
The DBTL Engineering Workspace is the primary scientific decision environment of the Synthetic Biology DBTL Engineering Operating System.

Its objective is not to display biological information.

Its objective is to guide one complete engineering decision.

Every interaction shall reduce scientific uncertainty.

Every recommendation shall remain reviewable.

Every engineering proposal shall remain traceable.

Every approval shall remain attributable.

The workspace shall preserve scientific context across the entire DBTL lifecycle.

The workspace shall never separate diagnosis, design, simulation, critique, and build planning into disconnected tools.

The engineering decision is the primary object.

Everything else exists to support that decision.
```

---

## 我的评价（相比当前 Page Design Contract）

如果按你们现在的框架，`01_Product_Spec.md` 已经足够好。

**但对于 Page2，我建议不要把它当成普通页面。**

它实际上是整个系统的**核心 Workspace**，因此 Product Spec 应该围绕：

* **Workspace Identity（为什么存在）**
* **Engineering Philosophy（工程哲学）**
* **Decision Model（决策模型）**
* **Scientific Object Model（科学对象模型）**
* **Engineering Lifecycle（完整 DBTL 生命周期）**

来组织，而不是围绕传统的“功能列表”。这样 Claude 在后续生成 UI、交互和代码时，会始终围绕**一个持续的工程决策过程**展开，而不会把 Page2 做成五个彼此独立的 AI 工具页面。

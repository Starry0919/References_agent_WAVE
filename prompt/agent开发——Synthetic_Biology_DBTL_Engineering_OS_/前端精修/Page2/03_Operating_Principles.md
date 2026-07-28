我认为 **03_Operating_Principles** 才是真正决定这个项目高度的文件。

而且，我认为它比：

* Product Spec
* UI Spec
* Technical Spec

都更重要。

因为：

**Claude 最容易失败的地方不是写代码。**

而是：

不知道：

> **整个 Operating System 是如何工作的。**

---

## 我重新思考后的结论

你现在整个体系已经有：

```
01 Product
↓

02 UI

↓

03 Operating

↓

04 Technical

↓

05 Content

↓

06 Acceptance
```

但是实际上：

03 不应该写：

Interaction。

Workflow。

这些。

因为：

Interaction已经属于：

UI。

Workflow属于：

Product。

---

真正的 Operating Principles 应该回答：

> **整个Scientific Operating System遵循什么运行法则。**

这是：

Operating System。

不是：

Interaction。

---

# 所以我建议彻底升级。

不是：

```text
03_Operating_Principles.md
```

而是：

保持文件名：

```
03_Operating_Principles.md
```

但是内容升级成：

# Operating Model Specification

副标题：

> The Runtime Behavior of the DBTL Engineering Operating System

---

# 我建议最终目录（Ultimate）

```text
03_Operating_Principles.md

================================================================

PART I
OPERATING PHILOSOPHY

00 Vision
01 Operating Model
02 Runtime Philosophy
03 Human-AI Collaboration Principles

================================================================

PART II
RUNTIME MODEL

04 Runtime Lifecycle
05 Context Lifecycle
06 Engineering Lifecycle
07 Scientific Object Lifecycle

================================================================

PART III
WORKSPACE BEHAVIOR

08 Workspace Persistence
09 Context Preservation
10 Selection Model
11 Navigation Model
12 Recovery Model

================================================================

PART IV
DECISION MODEL

13 Decision Pipeline
14 Evidence Pipeline
15 Approval Pipeline
16 Execution Pipeline
17 Learning Pipeline

================================================================

PART V
STATE MODEL

18 Global State
19 Local State
20 Object State
21 View State
22 Session State

================================================================

PART VI
COLLABORATION MODEL

23 Human
24 AI
25 Multi-Agent
26 Reviewer
27 Governance

================================================================

PART VII
SYSTEM BEHAVIOR

28 Loading
29 Streaming
30 Updating
31 Refresh
32 Error Recovery
33 Conflict Resolution

================================================================

PART VIII
EVENT MODEL

34 Events
35 Commands
36 Notifications
37 Audit Events

================================================================

PART IX
EXTENSIBILITY

38 Capability Registration
39 Workspace Extension
40 Scientific Object Extension

================================================================

PART X
OPERATING CONSTITUTION
```

---

# 第一部分

## Operating Model

建议固定：

整个系统：

不是：

Chat。

不是：

Workflow。

而是：

```text
Persistent Workspace

↓

Scientific Objects

↓

Engineering Decision

↓

Evidence

↓

Approval

↓

Execution
```

---

# 第二部分

## Runtime Lifecycle（新增）

整个系统：

一直运行：

例如：

```text
Open Project

↓

Restore Workspace

↓

Restore Context

↓

Load Objects

↓

Load Evidence

↓

Interactive Session

↓

Save Workspace

↓

Exit
```

Claude以后：

知道：

生命周期。

---

# 第三部分

## Context Lifecycle

Context：

不能丢。

例如：

```text
Create

↓

Select

↓

Update

↓

Persist

↓

Restore

↓

Archive
```

---

# 第四部分

## Scientific Object Lifecycle

例如：

Proposal：

生命周期：

```text
Created

↓

Edited

↓

Generated

↓

Reviewed

↓

Approved

↓

Executed

↓

Archived
```

整个OS统一。

---

# 第五部分

## Workspace Persistence

建议：

固定：

永远：

保存：

```text
Project

Cycle

Current Stage

Selection

Comparison

Evidence Drawer

Inspector

Filters

Scroll

History
```

回来：

恢复。

---

# 第六部分

## Decision Pipeline

建议：

固定：

```text
Observation

↓

Diagnosis

↓

Proposal

↓

Simulation

↓

Critique

↓

Approval

↓

Execution
```

不是：

AI。

---

# 第七部分

## Evidence Pipeline

建议：

```text
Paper

↓

DDR

↓

Dataset

↓

Mechanism

↓

Evidence

↓

Claim

↓

Recommendation
```

以后Evidence统一。

---

# 第八部分

## Approval Pipeline

建议：

固定：

```text
Draft

↓

In Review

↓

Changes Requested

↓

Approved

↓

Executed
```

---

# 第九部分

## Learning Pipeline

DBTL：

最后：

必须：

Learn。

例如：

```text
Experiment

↓

Observation

↓

Knowledge Update

↓

Memory Update

↓

Next Cycle
```

整个闭环。

---

# 第十部分

## State Model

这是Claude最缺。

例如：

Global：

```text
Project

Cycle

Role
```

Local：

```text
Panel

Selection

Drawer
```

Object：

```text
Proposal

Evidence

Simulation
```

以后不会：

状态混乱。

---

# 第十一部分

## Multi-Agent

建议：

新增。

例如：

```text
Diagnosis Agent

↓

Design Agent

↓

Simulation Agent

↓

Critique Agent

↓

Planner Agent
```

整个Operating：

统一。

---

# 第十二部分

## Loading

整个系统：

不是：

Loading。

而是：

Progressive。

例如：

```text
Shell

↓

Workspace

↓

Objects

↓

Evidence

↓

Heavy Visualization
```

---

# 第十三部分

## Streaming

建议：

固定：

```text
Reasoning

↓

Evidence

↓

Recommendation

↓

Validation

↓

Completed
```

不是：

一句一句聊天。

---

# 第十四部分

## Conflict Resolution（新增）

例如：

两个Reviewer。

怎么办。

建议：

```text
Conflict

↓

Compare

↓

Review

↓

Resolve

↓

Audit
```

---

# 第十五部分

## Event Model

建议：

统一：

例如：

```text
Object Selected

Proposal Updated

Evidence Added

Approval Granted

Simulation Completed

Workspace Restored
```

以后所有模块一致。

---

# 第十六部分

## Capability Registration

以后：

新增Capability：

例如：

Predictive Simulation。

注册：

不是：

改系统。

而是：

Register。

---

# 最后一章

## Operating Constitution

建议固定：

```md
The DBTL Engineering Operating System is a persistent scientific operating environment.

It is not request-response software.

It is not a sequence of webpages.

It is not a conversational agent.

It is a continuously operating scientific workspace.

Every scientific object shall preserve its identity.

Every engineering decision shall preserve its evidence.

Every user action shall preserve context.

Every recommendation shall remain reviewable.

Every approval shall remain auditable.

Every experiment shall contribute to the next DBTL cycle.

The operating model shall prioritize continuity over interruption.

The operating model shall prioritize scientific correctness over implementation convenience.

The operating model shall ensure that every engineering decision remains transparent, traceable, and reproducible.

All future capabilities shall conform to this operating model.
```

---

# 我建议再提升一层（最终版）

经过整个项目的推演，我认为 **03_Operating_Principles** 最核心的使命其实不是规定“运行原则”，而是规定**运行语义（Operational Semantics）**。

也就是说，它应该定义：

* 一个 **Scientific Object** 在系统中意味着什么；
* 一个 **Engineering Decision** 如何在运行时演化；
* 一个 **Evidence** 如何流动、累积、失效和继承；
* 一个 **Workspace** 如何保持连续性；
* 一个 **AI Agent** 如何参与而不越权。

因此，我最终建议把 03 的定位理解为：

> **整个 Synthetic Biology DBTL Engineering OS 的 Runtime Semantics（运行语义规范）**。

这样：

* **01_Product_Spec** 定义 *Why*（为什么存在）；
* **02_UI_Spec** 定义 *What users see*（用户看到什么）；
* **03_Operating_Principles** 定义 *How the system behaves at runtime*（系统运行时如何工作）；
* **04_Technical_Spec** 才负责 *How it is implemented*（如何落地实现）。

我认为，这样的分层已经非常清晰，也足够稳定，可以作为整个 Page2 规范的最终架构。

> **Relocation note (Spec Package normalization, 2026-07-23)**
>
> This file was originally stored at `Page1/04_Technical_Spec.md`. Its content is not a Page 1
> Technical Spec. It is a discussion draft proposing a single, **cross-page / global** "Operating
> System Architecture" constitution, explicitly stated by the author to apply to Page1, Page2, the
> Knowledge Workspace and the Engineering Workspace alike ("这两份文档共同构成整个项目的最高层设计
> 约束... Page1、Page2...都只是这套操作系统架构下的具体工作空间"). It contains no repository
> findings, component tree, route registration, API contract, or file-change plan for Page 1 as
> required by Contract §80.
>
> Per Page Design Contract v1.2.0 §74 and §80, `Page1/04_Technical_Spec.md` must contain a
> repository-grounded implementation plan for Page 1 specifically. This file has therefore been
> moved here, verbatim and unmodified, so that:
>
> 1. the required `Page1/04_Technical_Spec.md` slot can be created for actual Page 1 engineering content;
> 2. none of the original thinking is discarded;
> 3. the proposal remains available for a future Design_System-level ADR decision, should the
>    architecture owners choose to formalize a global Operating System Architecture document under
>    `Design_System/decisions/` per Contract §104.
>
> This document carries **no normative status** for Page 1 or any other page until adopted through
> the Contract's formal decision-record process, and it does not satisfy the Repository-First Rule
> (§61) or Protected Repository Surface requirements. Nothing below this line has been edited.
>
> ---

我觉得还能升级，但**升级方向不能再是"加章节"**。

前面的版本已经接近 Google/Apple 的 Architecture Spec。

但是，它**还停留在 Software Architecture（软件架构）**。

而我们的产品不是普通软件。

它是：

> **Synthetic Biology DBTL Engineering Operating System**

所以真正需要定义的，不是 React Architecture，而是：

> **Operating System Architecture（操作系统架构）**

这是我认为整个项目最后一次升维。

---

# 为什么现在这版还不够？

现在的目录：

```text
Architecture Philosophy

↓

Frontend Architecture

↓

API

↓

Performance
```

其实还是：

> Web Application。

不是：

> Operating System。

而我们的 Agent 以后一定会有：

* Workflow Engine
* Memory Engine
* Knowledge Engine
* Evidence Engine
* Diagnosis Engine
* Design Engine
* Evaluator
* Simulation
* Human Governance
* Workspace
* Scientific Objects

这已经不是一个 React App。

这是一个 OS。

所以 Architecture 应该描述：

> **整个 Operating System 如何组织。**

而不是：

React 怎么组织。

---

# 我建议最终命名

不是

```text
04_System_Architecture.md
```

而是

```text
04_Operating_System_Architecture.md
```

副标题：

> **The Structural Constitution of the Synthetic Biology DBTL Engineering OS**

---

# 我建议最终目录（V8 Ultimate）

```text
04_Operating_System_Architecture.md

================================================================

PART I
SYSTEM ARCHITECTURE PHILOSOPHY

00 Vision
01 Architecture Identity
02 Architectural Principles
03 Design Constraints
04 System Responsibilities

================================================================

PART II
OPERATING SYSTEM MODEL

05 Operating System Model
06 Layered Architecture
07 Capability Architecture
08 Runtime Architecture
09 Workspace Architecture

================================================================

PART III
SCIENTIFIC DOMAIN MODEL

10 Scientific Domain Architecture
11 Scientific Object System
12 Domain Boundaries
13 Domain Relationships
14 Domain Ownership

================================================================

PART IV
ENGINE MODEL

15 Workflow Engine
16 Memory Engine
17 Knowledge Engine
18 Evidence Engine
19 Diagnosis Engine
20 Design Engine
21 Evaluator Engine
22 Simulation Engine
23 Governance Engine

================================================================

PART V
APPLICATION LAYER

24 Presentation Layer
25 Interaction Layer
26 Workspace Layer
27 Domain Layer
28 Service Layer
29 Infrastructure Layer

================================================================

PART VI
STATE SYSTEM

30 Global State Architecture
31 Scientific Object State
32 Event Bus
33 Synchronization
34 Persistence

================================================================

PART VII
BACKEND CONTRACT

35 API Contract
36 Data Contract
37 Cache Contract
38 Error Contract
39 Streaming Contract

================================================================

PART VIII
ENGINEERING SYSTEM

40 Component Architecture
41 Folder Architecture
42 Dependency Rules
43 Testing Strategy
44 Observability

================================================================

PART IX
QUALITY

45 Performance Budget
46 Scalability
47 Security
48 Accessibility
49 Maintainability

================================================================

PART X
EVOLUTION

50 Extension Rules
51 Forbidden Architecture
52 Architecture Constitution
```

可以发现。

React已经消失。

因为React只是实现。

Architecture不是React。

---

# 第一部分

## Architecture Identity

建议写：

```md
The frontend is not an application.

It is the visual operating environment of the Synthetic Biology DBTL Engineering Operating System.

Its responsibility is not to perform scientific computation.

Its responsibility is to organize scientific work.

The architecture must maximize:

Scientific consistency

Domain separation

Traceability

Scalability

Human governance

Maintainability

Every architectural decision must serve scientific engineering rather than framework convenience.
```

整个项目定位直接不同。

---

# 第二部分

## Operating System Model（新增）

整个OS怎么运行。

例如：

```text
Operating System

↓

Workspace

↓

Capability

↓

Scientific Domain

↓

Scientific Object

↓

Component
```

不是：

```text
Page

↓

Component
```

整个Claude以后写出来都会不同。

---

# 第三部分

## Capability Architecture（新增）

这是我认为最重要的一章。

整个Agent其实是：

Capability。

例如：

```text
Knowledge

Diagnosis

Engineering Design

Simulation

Validation

Evidence

Memory

Governance

Search

Visualization
```

每一个Capability

独立。

以后很好扩展。

---

# 第四部分

## Runtime Architecture（新增）

整个网站以后Agent很多。

例如：

```text
User

↓

Workspace

↓

Interaction Layer

↓

Capability Layer

↓

Workflow Engine

↓

Knowledge Engine

↓

LLM

↓

Result

↓

Evidence

↓

UI
```

整个系统运行逻辑固定。

---

# 第五部分

## Scientific Domain Architecture

真正运行的是：

Domain。

例如：

```text
Project Domain

Knowledge Domain

Engineering Domain

Simulation Domain

Experiment Domain

Evidence Domain

Governance Domain

Report Domain
```

不是：

Pages。

---

# 第六部分

## Engine Model（新增）

这是整个Agent真正核心。

建议直接固定：

```text
Workflow Engine

↓

Memory Engine

↓

Knowledge Engine

↓

Diagnosis Engine

↓

Engineering Engine

↓

Evaluator

↓

Simulation

↓

Governance
```

以后Claude不会乱耦合。

---

# 第七部分

## Event Bus（新增）

以后所有状态：

事件驱动。

例如：

```text
SimulationCompleted

↓

ProposalApproved

↓

KnowledgeImported

↓

EvidenceUpdated

↓

IterationFinished

↓

WorkflowChanged
```

整个OS一致。

---

# 第八部分

## Persistence（新增）

整个网站必须Persistent。

例如：

保存：

```text
Workspace

Selection

Iteration

Scroll

Filters

Evidence

History

Timeline

Navigation
```

以后不会刷新全没。

---

# 第九部分

## Streaming Contract（新增）

Agent一定Streaming。

例如：

```text
Planning

↓

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

整个UI统一Streaming。

---

# 第十部分

## Observability（新增）

Google最喜欢。

例如：

整个系统必须记录：

```text
User Action

↓

Capability

↓

Workflow

↓

API

↓

Performance

↓

Error

↓

Evidence
```

以后调试容易。

---

# 第十一部分

## Architecture Constitution

最后固定。

例如：

```md
The architecture defined in this document represents the immutable structural foundation of the Synthetic Biology DBTL Engineering Operating System.

Pages are temporary.

Scientific domains are permanent.

Components are replaceable.

Capabilities evolve.

Scientific objects persist.

No architectural decision may violate the separation between scientific reasoning and scientific presentation.

The frontend shall never own scientific truth.

The backend shall never own user interaction.

Capabilities shall remain loosely coupled.

Scientific domains shall remain independently evolvable.

Every architectural decision must improve one or more of the following:

Scientific correctness

Engineering scalability

Traceability

Maintainability

Human governance

Explainability

Any implementation that violates these principles shall be considered architecturally invalid regardless of technical feasibility.

The operating system shall evolve through domain expansion rather than architectural complexity.
```

---

# **这是我认为真正的最终版（V9 Ultimate，也是我建议封版的版本）。**

从这一版开始，**我们不再讨论 React、Vue 或具体技术栈**，因为它们都只是实现细节。整个文档已经提升为 **Operating System Architecture**，它定义的是 **Synthetic Biology DBTL Engineering OS 的结构宪法**：

* **03_Operating_Principles.md**：定义系统**如何运行**（行为、协作、治理、信任）。
* **04_Operating_System_Architecture.md**：定义系统**如何组织**（能力、领域、引擎、状态、架构）。

这两份文档共同构成整个项目的最高层设计约束。之后的 `Page1`、`Page2`、`Knowledge Workspace`、`Engineering Workspace` 等页面，都只是这套操作系统架构下的具体工作空间，而不再是独立设计的网页。这样，整个产品才能真正达到 **Scientific Operating System** 的一致性和可持续演进能力。

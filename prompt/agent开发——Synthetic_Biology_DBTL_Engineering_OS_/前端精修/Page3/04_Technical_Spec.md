我认为 **Page3 的 `04_Technical_Spec.md`**，不能再按传统前端的思路去写。

如果 `01_Product_Spec` 回答的是：

> 为什么存在？

`02_UI_Spec` 回答的是：

> 长什么样？

`03_Operating_Principles` 回答的是：

> 如何运行？

那么：

> **`04_Technical_Spec` 应该回答：Claude Code 到底应该如何把这个 Scientific Knowledge Production System 实现出来。**

也就是说：

它不是 React 教程。

不是 Next.js 教程。

不是 API 文档。

而是：

> **整个技术实现合同（Implementation Contract）**

---

# 我给它的定位

```
04_Technical_Spec.md

=

Implementation Contract

+

Architecture Contract

+

Component Contract

+

State Contract

+

Backend Contract

+

Rendering Contract

+

Performance Contract

+

AI Contract

+

Engineering Contract
```

---

# 我建议最终目录

```
04_Technical_Spec.md

======================================================

PART I
IMPLEMENTATION PHILOSOPHY

00 Purpose

01 Technical Mission

02 Design Principles

03 Implementation Constraints

======================================================

PART II
ARCHITECTURE

04 Layered Architecture

05 Frontend Architecture

06 Backend Integration

07 Runtime Architecture

08 Data Flow

======================================================

PART III
PAGE COMPOSITION

09 Page Tree

10 Workspace Regions

11 Component Hierarchy

12 Shared Components

13 Page-specific Components

======================================================

PART IV
STATE MANAGEMENT

14 State Taxonomy

15 Persistent State

16 Session State

17 UI State

18 Scientific State

19 Derived State

======================================================

PART V
BACKEND CONTRACT

20 Backend Source of Truth

21 API Contract

22 DTO

23 Adapter Layer

24 Validation

25 Error Mapping

======================================================

PART VI
KNOWLEDGE OBJECT MODEL

26 Object Types

27 Object Identity

28 Relationships

29 Version

30 Provenance

======================================================

PART VII
RENDERING CONTRACT

31 Rendering Pipeline

32 Lazy Rendering

33 Incremental Rendering

34 Streaming

35 Inspector Rendering

======================================================

PART VIII
PERFORMANCE

36 Rendering Budget

37 Search

38 Graph

39 Caching

40 Virtualization

======================================================

PART IX
AI INTEGRATION

41 AI Boundary

42 Retrieval

43 Evidence

44 Runtime

45 Traceability

======================================================

PART X
QUALITY

46 Logging

47 Monitoring

48 Testing

49 Accessibility

50 Security

======================================================

PART XI
IMPLEMENTATION RULES

51 Must

52 Must Not

53 Stop Conditions

54 Acceptance Mapping
```

---

# 为什么这样划分？

因为 Claude Code 真正关心的是：

```
Backend

↓

State

↓

Components

↓

Rendering

↓

Interaction

↓

Acceptance
```

而不是：

颜色。

字体。

留白。

---

# PART II

## Architecture

建议直接固定：

```
Page

↓

Layout

↓

Workspace

↓

Panels

↓

Components

↓

Scientific Objects
```

不要允许：

```
Page

↓

Business Logic
```

业务逻辑只能：

```
Backend

↓

Adapter

↓

Frontend
```

不能：

React：

直接处理。

---

# Backend Contract

这是最重要的一章。

必须写死：

```
Backend

↓

DTO

↓

Adapter

↓

Domain Object

↓

UI
```

禁止：

```
API

↓

Component
```

以后：

后端改一点。

全崩。

---

建议：

Adapter：

统一：

```
KnowledgeDTO

↓

KnowledgeObject
```

Evidence：

也是。

Pattern：

也是。

全部。

---

# State

这里建议：

彻底分类。

```
Persistent

Session

Scientific

Interaction

Derived

Temporary
```

不是：

Redux。

不是：

Zustand。

而是：

状态分类。

以后：

Claude：

不会乱。

---

# Component Hierarchy

建议：

固定：

```
KnowledgeWorkspace

├── Navigation

├── KnowledgeSurface

├── Inspector

├── EvidenceDrawer

├── ComparePanel

├── ContextBar
```

每一个：

继续。

例如：

KnowledgeSurface：

```
KnowledgeSurface

↓

KnowledgeList

↓

KnowledgeCard

↓

MechanismCard

↓

EvidenceCard
```

以后：

共享。

---

# Object Model

这是：

Page3：

最重要。

建议：

Object：

全部：

统一。

例如：

Knowledge：

```
Knowledge

↓

Evidence

↓

Mechanism

↓

Pattern

↓

Rule

↓

Claim
```

不是：

Document。

不是：

JSON。

Object。

---

每一个：

Object：

固定：

```
id

version

status

source

provenance

relationships

children
```

以后：

整个系统：

统一。

---

# Rendering

建议：

不要：

React：

Render：

全部。

而是：

Streaming。

例如：

```
Knowledge

↓

List

↓

Inspector

↓

Evidence

↓

Deep Detail
```

一级一级。

避免：

一次：

全部。

---

Graph：

Lazy。

Evidence：

Lazy。

全部：

Lazy。

---

# AI Integration

建议：

新增。

因为：

这里：

整个：

Agent。

建议：

```
User

↓

Retrieve

↓

Evidence

↓

Reason

↓

Generate

↓

Review

↓

Display
```

整个：

AI：

Pipeline。

---

不要：

```
LLM

↓

Answer
```

禁止。

---

# Performance

建议：

明确：

```
Knowledge

5000+

Evidence

50000+

Paper

100000+
```

系统：

仍然：

不卡。

所以：

必须：

Virtualization。

必须：

Pagination。

必须：

Incremental。

---

# Must Not

建议：

这里：

一定：

写死。

例如：

```
Never

Modify Backend

Never

Generate Mock Scientific Data

Never

Create Local Object Schema

Never

Duplicate Domain Objects

Never

Call API inside Component

Never

Business Logic inside UI
```

Claude：

非常容易：

犯。

---

# Stop Conditions

建议：

写：

```
Backend

Connected

Adapter

Working

State

Stable

Rendering

Correct

Interaction

Correct

Acceptance

Pass
```

Claude：

必须：

停。

---

# 我认为还应该新增一个章节（这是这一版最重要的升级）

如果目标是**让 Claude Code 真正能够连续开发几十个页面且不会越写越乱**，我会在最后新增：

# PART XII — Repository Architecture Contract

这是我认为目前所有 Technical Spec 最容易遗漏、但长期最重要的一层。

例如：

```
Repository

├── app/

├── shared/

├── features/

├── entities/

├── widgets/

├── pages/

├── processes/

├── adapters/

├── api/

├── lib/

├── styles/
```

然后写死：

```
pages/

不能引用

backend
```

```
widgets

不能直接请求API
```

```
entities

不能依赖pages
```

```
adapters

唯一允许解析DTO
```

```
shared

禁止出现Scientific Logic
```

```
features

禁止保存Scientific Truth
```

再加上：

```
Import Rules

Folder Dependency Rules

File Naming Rules

Barrel Export Rules

DTO Rules

Component Rules
```

这一章实际上属于**仓库级技术治理（Repository Governance）**，不是单纯的 React 编码规范。

---

## 最终评价

如果按目前这套结构完成 **`04_Technical_Spec.md`**，它将不是一份普通的前端技术说明，而是一份真正约束 Claude Code 的 **Implementation Contract**。

它与前面三份文档形成清晰分工：

* **01_Product_Spec**：定义 **为什么做（Why）**。
* **02_UI_Spec**：定义 **用户看到什么（What it looks like）**。
* **03_Operating_Principles**：定义 **系统如何运行（How it operates）**。
* **04_Technical_Spec**：定义 **代码如何实现且长期可维护（How it is implemented）**。

这是 Claude Code 最依赖的一份工程规范，也是决定整个项目后续可维护性的关键文档。

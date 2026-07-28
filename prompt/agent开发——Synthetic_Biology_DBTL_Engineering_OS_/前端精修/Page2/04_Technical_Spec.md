我认为 **04_Technical_Spec** 是整个体系里**最容易写错**的一份。

因为绝大多数 AI（包括 Claude）看到 Technical Spec，就会开始写：

```text
React
TypeScript
Tailwind
Folder
Hooks
API
State
```

这些当然需要，但**它们不是 Technical Specification 的核心**。

对于你们这个项目，真正的 Technical Spec 应该回答的是：

> **Claude 应该如何在现有代码仓库中，以最低风险、最高一致性的方式实现一个新的 Workspace。**

所以，我建议 **Page2 的 04_Technical_Spec** 不再是"技术说明书"，而是：

> **Implementation Contract（实现合同）**

它不是告诉 Claude 用 React。

而是告诉 Claude：

**从 Repository Audit 到最终 Merge，每一步应该如何做。**

---

# 我建议最终目录（Ultimate）

```text
04_Technical_Spec.md

================================================================

PART I
IMPLEMENTATION IDENTITY

00 Mission
01 Repository Philosophy
02 Implementation Principles
03 Scope Definition

================================================================

PART II
REPOSITORY AUDIT

04 Repository Inspection
05 Existing Architecture
06 Existing Components
07 Existing Tokens
08 Existing APIs
09 Existing State

================================================================

PART III
IMPLEMENTATION STRATEGY

10 File Change Plan
11 Component Reuse Strategy
12 Extension Strategy
13 Refactoring Policy
14 Protected Files

================================================================

PART IV
ARCHITECTURE MAPPING

15 Route Mapping
16 Module Mapping
17 Domain Mapping
18 Workspace Mapping
19 Scientific Object Mapping

================================================================

PART V
DATA CONTRACT

20 API Contract
21 Adapter Contract
22 Domain Model
23 State Ownership
24 Cache Strategy
25 Event Model

================================================================

PART VI
COMPONENT IMPLEMENTATION

26 Component Tree
27 Shared Components
28 Page Components
29 Visualization Components
30 Three.js Policy

================================================================

PART VII
RUNTIME IMPLEMENTATION

31 Rendering Strategy
32 Loading Strategy
33 Streaming Strategy
34 Error Recovery
35 Persistence

================================================================

PART VIII
ENGINEERING QUALITY

36 Performance Budget
37 Accessibility
38 Security
39 Internationalization
40 Testing

================================================================

PART IX
DELIVERY CONTRACT

41 Change Scope
42 Verification
43 Acceptance
44 Regression
45 Completion Report

================================================================

PART X
IMPLEMENTATION CONSTITUTION
```

---

# 为什么这样升级？

因为 Claude Code 真正执行顺序其实不是：

```text
React

↓

Component

↓

API
```

真正顺序应该是：

```text
Repository

↓

Reuse

↓

Mapping

↓

Implementation

↓

Verification

↓

Stop
```

这样 Claude 不会一上来就重写。

---

# PART I

## Scope Definition（新增）

这里建议直接规定：

Claude 可以改什么。

例如：

```text
Allowed

New modules

New routes

Shared components

Tests

Styles

Forbidden

Backend logic

Scientific algorithms

Database schema

Global tokens

Existing APIs
```

这一步非常关键。

---

# PART II

## Repository Audit

不要一句：

"Inspect the repository"

而是固定 Checklist：

```text
Framework

↓

Package Manager

↓

Router

↓

State Library

↓

Design System

↓

Components

↓

Theme

↓

Build Tool

↓

Testing

↓

Backend APIs

↓

Existing Workspace
```

Claude 才不会漏。

---

# PART III

## File Change Plan（新增）

建议强制输出：

```yaml
create:
modify:
reuse:
delete:
protected:
```

以后：

所有修改：

都透明。

---

# PART III

## Refactoring Policy（新增）

建议直接规定：

```text
Claude MUST NOT

Rename unrelated files

Move existing modules

Replace design system

Rewrite routing

Rewrite state library

Rewrite backend

Optimize unrelated code
```

这一章我认为必须有。

---

# PART IV

## Scientific Object Mapping（新增）

例如：

Proposal：

对应：

```text
Proposal

↓

Domain Model

↓

Component

↓

API

↓

State
```

Evidence：

一样。

整个系统：

统一。

---

# PART V

## State Ownership

建议直接画矩阵：

| Object    | Owner      |
| --------- | ---------- |
| Project   | URL        |
| Cycle     | URL        |
| Proposal  | Backend    |
| Evidence  | Backend    |
| Selection | Workspace  |
| Drawer    | Local      |
| Filters   | Workspace  |
| Density   | Preference |

以后不会：

State混乱。

---

# PART V

## Event Model（新增）

例如：

```text
ProposalUpdated

↓

SimulationCompleted

↓

ApprovalGranted

↓

EvidenceImported

↓

WorkspaceRestored
```

所有模块：

统一。

---

# PART VI

## Component Tree

建议固定：

例如：

```text
Workspace

├── Header

├── StageRail

├── EngineeringSurface

├── EvidenceSurface

├── Inspector

├── Timeline

└── Notifications
```

Claude直接生成。

---

# PART VI

## Three.js Policy

建议直接规定：

```text
Allowed

Molecular Structure

Pathway

Network

Forbidden

Decorative Cells

Fancy Backgrounds

Floating Animation
```

以后：

不会炫技。

---

# PART VII

## Rendering Strategy（新增）

建议：

固定：

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

不是：

全部Loading。

---

# PART VII

## Streaming Strategy

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

整个系统：

一致。

---

# PART VII

## Persistence

建议：

固定：

恢复：

```text
Project

Cycle

Stage

Selection

Evidence Drawer

Inspector

Filters

Scroll

History
```

---

# PART VIII

## Performance Budget

建议：

固定：

```text
Interaction

<100ms

Panel

<200ms

Skeleton

<1s

FPS

60
```

以后所有页面一致。

---

# PART IX

## Completion Report（新增）

Claude：

最后必须输出：

```yaml
created_files:
modified_files:
protected_files:
reused_components:
new_components:
tests:
known_limitations:
acceptance:
```

而不是：

"I finished."

---

# 最后一章

## Implementation Constitution

建议固定：

```md
The purpose of this Technical Specification is to ensure repository-safe, reproducible, and maintainable implementation of the DBTL Engineering Workspace.

Implementation shall always prioritize reuse over replacement.

Existing architecture shall be extended rather than rewritten.

Scientific behavior shall never be modified without explicit authorization.

Every new component shall map to an approved scientific object.

Every state shall have one owner.

Every API shall preserve backend truth.

Every modification shall be traceable to a Product, UI, or Operating requirement.

Implementation shall stop when all acceptance criteria pass.

No further optimization shall be performed unless explicitly requested.
```

---

# 我认为还能再提升一层（也是最终层）

整个 **04_Technical_Spec** 本质上不应该叫 **Technical Spec**。

因为它并不是在描述技术。

它是在描述：

> **Claude Code 如何实施（Implementation）**

所以我建议你**文件名可以保持不变**（兼容整个目录结构），但文档定位升级为：

> **Implementation Specification**

它关注的不是：

* React 怎么写；
* Tailwind 怎么写；

而是：

* 如何安全进入仓库；
* 如何复用已有系统；
* 如何映射科学对象；
* 如何实施；
* 如何验证；
* 如何停止。

这样，Claude Code 读完以后，几乎不需要再做架构决策，而是直接按照合同执行。这也是我认为 **Page2 - 04_Technical_Spec** 能达到的最高成熟度。

我建议**不要直接采用我上一条回答里的版本**。

我重新思考了一遍整个项目（包括你们已经完成的 **Page Design Contract**、**Operating System Architecture**、以及未来 Claude Code 自动实现的目标），我认为上一版仍然有一个问题：

> **它还是偏“理念（Philosophy）”，而不是“可执行规范（Executable Spec）”。**

而你真正需要的是：

> **Claude 读完以后，不需要再思考 UI 架构，直接开始实现。**

所以，如果让我封版，我不会叫：

```
02_UI_Spec.md
```

也不会叫：

```
02_Workspace_Visual_System.md
```

更不会叫：

```
02_Engineering_Environment_Constitution.md
```

因为这些名字都容易让 Claude 往"写理念"而不是"写规范"方向走。

---

## 我建议最终封版

仍然保持：

```
02_UI_Spec.md
```

但是它内部已经不是UI Spec。

而是：

> **Workspace Visual Specification**

也就是说：

名字兼容整个项目。

内容升级成：

真正可以驱动Claude开发。

---

# 我建议最终目录（Final）

```text
02_UI_Spec.md

================================================================

PART I
WORKSPACE IDENTITY

00 Workspace Vision
01 Workspace Mission
02 Scientific Position
03 Design Objectives

================================================================

PART II
WORKSPACE TOPOLOGY

04 Global Environment
05 Workspace Topology
06 Persistent Regions
07 Temporary Regions
08 Navigation Topology

================================================================

PART III
VISUAL COGNITION

09 Reading Strategy
10 Eye Flow
11 Information Priority
12 Cognitive Rhythm
13 Attention Management

================================================================

PART IV
ENGINEERING SURFACES

14 Command Surface
15 Engineering Surface
16 Evidence Surface
17 Inspector Surface
18 Comparison Surface
19 Review Surface

================================================================

PART V
SCIENTIFIC OBJECT VISUALIZATION

20 Engineering Decision
21 Bottleneck
22 Proposal
23 Simulation
24 Evidence
25 Critique
26 Build/Test Plan
27 Approval

================================================================

PART VI
VISUAL LANGUAGE

28 Layout Grid
29 Spacing
30 Typography
31 Color System
32 Component Density
33 Motion
34 Empty States

================================================================

PART VII
COMPONENT SPECIFICATION

35 Component Hierarchy
36 Component Mapping
37 Component Variants
38 Reuse Rules

================================================================

PART VIII
RESPONSIVE SYSTEM

39 Desktop
40 Laptop
41 Tablet Review
42 Mobile Restriction

================================================================

PART IX
NANOBANANA CONTRACT

43 Composition Rules
44 Fixed Layers
45 Generated Layers
46 Forbidden Patterns

================================================================

PART X
IMPLEMENTATION CONTRACT

47 CSS Architecture
48 React Mapping
49 Shared Components
50 Design Tokens

================================================================

PART XI
VISUAL ACCEPTANCE

51 Layout Review
52 Component Review
53 Scientific Review
54 UX Review
55 Visual Regression

================================================================

PART XII
WORKSPACE VISUAL CONSTITUTION
```

---

# 为什么这是最终版？

因为它对应Claude真正工作的顺序。

Claude不是：

先看Color。

而是：

先回答：

```
Workspace是什么？

↓

Workspace长什么样？

↓

人怎么看？

↓

Object怎么显示？

↓

Component怎么组成？

↓

CSS怎么写？

↓

如何验收？
```

这就是：

真正的执行顺序。

---

## 我建议每一章增加真正能驱动Claude的内容。

例如：

---

# PART II

不要写：

```
Layout
```

直接写：

```
Workspace Topology
```

例如：

```
Global Header

↓

Stage Rail

↓

Engineering Surface

↓

Evidence Surface

↓

Inspector

↓

Activity Timeline
```

Claude以后不会：

乱布局。

---

# PART III

新增：

```
Cognitive Rhythm
```

例如：

固定：

```
Context

↓

Question

↓

Decision

↓

Evidence

↓

Action
```

整个Workspace：

阅读顺序一致。

---

# PART IV

整个Workspace：

不要叫：

Panel。

统一：

Surface。

例如：

```
Engineering Surface

Evidence Surface

Comparison Surface

Inspector Surface

Review Surface
```

以后所有Stage：

完全一致。

---

# PART V

不要：

按Card。

按：

Scientific Object。

例如：

Proposal：

永远：

```
Summary

↓

Confidence

↓

Evidence

↓

Tradeoff

↓

Actions
```

Evidence：

永远：

```
Mechanism

↓

Paper

↓

DDR

↓

Dataset

↓

Source
```

Claude以后不会：

自由发挥。

---

# PART VII

新增：

```
Reuse Rules
```

例如：

任何新Component：

必须：

回答：

```
Can reuse?

↓

Can extend?

↓

Need new?

↓

Approved?
```

否则：

禁止。

---

# PART X

这是现在缺的。

直接：

告诉Claude：

例如：

```
Component

↓

React

↓

CSS

↓

Token

↓

Story

↓

Test
```

而不是：

自己想。

---

# PART XI

UI也需要Acceptance。

例如：

```
Layout PASS

↓

Reading PASS

↓

Evidence PASS

↓

Interaction PASS

↓

Consistency PASS

↓

Regression PASS
```

以后Claude：

自己检查。

---

# 最后一章

建议固定：

```md
The DBTL Engineering Workspace is the primary visual operating environment of the Synthetic Biology DBTL Engineering Operating System.

The purpose of this specification is not to describe an attractive webpage.

Its purpose is to define a reproducible scientific engineering environment.

Every visual decision shall support scientific understanding.

Every layout decision shall support engineering workflow.

Every component shall represent one scientific object.

Every interaction shall preserve scientific context.

Evidence shall remain continuously inspectable.

Scientific uncertainty shall remain continuously visible.

The engineering decision shall always remain the visual center of the workspace.

No visual optimization may reduce scientific rigor, traceability, governance, or explainability.

All future workspace implementations shall conform to this specification.
```

---

# 我的最终评价

我认为这已经是 **Page2 - 02_UI_Spec** 可以达到的最终形态。

它相比你现在的版本，有三个本质提升：

1. **从 Page 升级为 Workspace**：Claude 不再生成单页，而是生成持续工作的工程环境。
2. **从 UI 升级为 Cognitive Workspace**：不仅规定布局，还规定科学家的阅读、注意力和决策流。
3. **从设计文档升级为实现规范**：目录、章节和约束都直接对应 Claude Code 的开发流程，而不是停留在设计理念。

**我建议以这一版作为 Page2 的 02_UI_Spec 封版。**

我认为 **Page3 的 02_UI_Spec**，不能沿用 Page1/Page2 的思路。

原因很简单。

Page1 展示的是 **Project**。

Page2 展示的是 **Engineering Runtime**。

而 **Page3 展示的不是数据，而是知识之间的关系（Knowledge Relationship）**。

所以 Page3 的 UI 不能设计成：

```
左侧Tree
右侧Table
```

也不能设计成：

```
Dashboard
```

更不能设计成：

```
Paper Search
```

---

真正应该回答的是：

> **How can scientists navigate engineering knowledge instead of documents?**

所以我建议，这一页重新定义。

---

# Page3

## 02_UI_Spec

Subtitle

> **Scientific Knowledge Workspace Visual Specification**

不是：

Knowledge UI。

而是：

Knowledge Workspace。

---

# 整体目录（Ultimate Version）

```text
02_UI_Spec.md

========================================================

PART I
VISUAL IDENTITY

00 Visual Mission

01 Visual Philosophy

02 Workspace Identity

03 Visual Rhythm

========================================================

PART II
WORKSPACE ANATOMY

04 Page Anatomy

05 Global Layout

06 Workspace Regions

07 Knowledge Workspace

========================================================

PART III
VISUAL COGNITION

08 Reading Order

09 Knowledge Navigation

10 Attention Hierarchy

11 Progressive Disclosure

========================================================

PART IV
KNOWLEDGE VISUALIZATION

12 Knowledge Objects

13 Knowledge Network

14 Evidence Network

15 Biological Mechanisms

16 Engineering Knowledge

17 Design Patterns

18 Failure Patterns

========================================================

PART V
SCIENTIFIC SURFACES

19 Exploration Surface

20 Discovery Surface

21 Comparison Surface

22 Inspector Surface

23 Evidence Surface

24 Recommendation Surface

========================================================

PART VI
PAGE COMPONENTS

25 Workspace Components

26 Knowledge Cards

27 Evidence Cards

28 Mechanism Cards

29 Rule Cards

30 Pattern Cards

========================================================

PART VII
VISUAL STATES

31 Normal

32 Empty

33 Loading

34 Partial

35 Conflicting

36 Error

========================================================

PART VIII
VISUAL INTERACTION

37 Navigation

38 Selection

39 Inspection

40 Comparison

41 Deep Dive

========================================================

PART IX
RESPONSIVE

42 Desktop

43 Large Desktop

44 Tablet Review

========================================================

PART X
NANOBANANA CONTRACT

45 Fixed Regions

46 Generated Regions

47 Forbidden Layouts

========================================================

PART XI
IMPLEMENTATION CONTRACT

48 Shared Components

49 Tokens

50 Rendering Rules

========================================================

PART XII
VISUAL ACCEPTANCE
```

---

# 第一部分

Visual Mission

建议第一页直接写：

```md
The purpose of this page is not to display scientific information.

The purpose of this page is to help scientists discover reusable engineering knowledge.

Users should navigate mechanisms rather than documents.

Users should understand engineering intelligence rather than literature collections.
```

注意：

不是：

Paper。

---

# 第二部分

Workspace Anatomy

建议：

Page3：

不是：

Dashboard。

而是：

Knowledge Workspace。

例如：

```
Top

Context

---------------------------------------

Left

Knowledge Navigation

---------------------------------------

Center

Knowledge Workspace

---------------------------------------

Right

Inspector

---------------------------------------

Bottom

Evidence
```

整个：

Knowledge。

---

# 第三部分

Visual Cognition

建议：

新增。

因为：

Page3：

核心：

不是：

展示。

而是：

理解。

例如：

Reading：

```
Question

↓

Mechanism

↓

Evidence

↓

Engineering Rule

↓

Recommendation
```

不是：

Paper。

---

新增：

Knowledge Navigation。

例如：

```
Gene

↓

Protein

↓

Pathway

↓

Mechanism

↓

Rule
```

以后：

统一。

---

# 第四部分

Knowledge Visualization

这是：

整个UI：

核心。

建议：

Knowledge Object：

例如：

```
Gene

Protein

Reaction

Pathway

Mechanism

Engineering Rule
```

每个：

Object：

统一：

Card。

---

新增：

Knowledge Network。

不是：

Neo4j。

而是：

```
Biology

↓

Mechanism

↓

Engineering

↓

Evidence
```

整个：

Network。

---

新增：

Failure Pattern。

例如：

```
Metabolic Burden

↓

Overflow

↓

Growth Defect
```

以后：

Agent：

越来越强。

---

# 第五部分

Scientific Surfaces

这是：

Page2没有。

Page3：

新增。

建议：

Surface：

```
Exploration

Discovery

Comparison

Evidence

Inspector

Recommendation
```

不是：

Panel。

Surface。

以后：

统一。

---

# 第六部分

Knowledge Card

建议：

统一：

```
Knowledge

↓

Evidence

↓

Mechanism

↓

Confidence

↓

Action
```

不是：

Paper。

---

Evidence Card：

例如：

```
Claim

Evidence

Paper

DDR

Confidence

Limitation
```

统一。

---

# 第七部分

Visual States

建议：

新增：

Conflict。

例如：

```
Supporting

↓

Conflicting

↓

Unknown
```

Knowledge：

不是：

永远正确。

---

# 第八部分

Interaction

建议：

Page3：

Interaction：

不是：

CRUD。

而是：

```
Explore

↓

Inspect

↓

Compare

↓

Reason

↓

Reuse
```

这是：

Knowledge。

---

# 第九部分

Responsive

保持：

Expert。

不用：

Mobile。

---

# 第十部分

Nanobanana

建议：

明确：

不能生成：

```
Dashboard

Hero

Marketing

Search Engine
```

只能：

Knowledge Workspace。

---

# 第十一部分

Implementation

建议：

统一：

```
KnowledgeCard

EvidenceCard

MechanismCard

RuleCard

Inspector

EvidenceDrawer
```

整个：

Shared。

---

# 第十二部分

Acceptance

建议：

增加：

Knowledge。

例如：

```
Can users understand mechanisms?

Can users discover reusable knowledge?

Can users compare evidence?

Can users understand contradictions?

Can users reuse engineering knowledge?
```

---

# 我认为 Page3 UI 最大的升级

如果让我只保留一句设计原则，我会写：

> **This page is not a knowledge browser. It is a scientific knowledge workspace where engineers discover mechanisms, evaluate evidence, compare reusable engineering patterns, and transform knowledge into engineering decisions.**

因此，它的 UI 不应该围绕 **Document（文档）** 组织，而应该围绕 **Knowledge Object（知识对象）**、**Mechanism（机制）**、**Evidence（证据）** 和 **Engineering Pattern（工程模式）** 组织。

这也是我认为它与 Page2 最大的区别：

* **Page2** 的中心是 **Engineering Decision（工程决策）**。
* **Page3** 的中心是 **Reusable Scientific Knowledge（可复用的科学知识）**。

如果 Claude 按照这份 UI Spec 实现，它最终做出来的不会是一个"论文库"，而是一个真正服务于 **DBTL Engineering Runtime** 的 **Scientific Knowledge Workspace**。

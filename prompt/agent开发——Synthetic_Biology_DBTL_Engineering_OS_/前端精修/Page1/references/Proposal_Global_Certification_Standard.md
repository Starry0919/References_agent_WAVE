> **Relocation note (Spec Package normalization, 2026-07-23)**
>
> This file was originally stored at `Page1/05_Acceptance_Spec.md`. Its content is not a Page 1
> Acceptance Spec in the format required by Contract §82 (Acceptance Record: `criterion_id /
> requirement / priority / test_method / expected / actual / evidence / status / owner /
> remediation`). It is a discussion draft proposing a single, **cross-page / global** "System
> Certification Standard" and a full `Design_System/` reorganization (`Constitution/`,
> `Specifications/`, `Certification/`), explicitly not scoped to Page 1 alone.
>
> Per Contract §74 and §82, `Page1/06_Acceptance_Spec.md` must contain testable, page-specific
> acceptance gates for Page 1. This file has therefore been moved here, verbatim and unmodified, so
> that:
>
> 1. the required `Page1/06_Acceptance_Spec.md` slot can be created in the Contract's Acceptance
>    Record format;
> 2. none of the original thinking is discarded;
> 3. the proposal remains available for a future Design_System-level DSR/ADR decision, should the
>    product owners choose to formalize a global Certification Standard under
>    `Design_System/decisions/` per Contract §104.
>
> Several individual criterion ideas in this draft (e.g. the "Product Certification" and "Scientific
> Certification" question lists) are genuinely reusable and have been migrated — reformatted into
> proper Acceptance Records, and marked `DEFERRED` pending owner sign-off — into the new
> `Page1/06_Acceptance_Spec.md`. This file remains the verbatim original for full traceability. It
> carries **no normative status** on its own until adopted through the Contract's formal
> decision-record process. Nothing below this line has been edited.
>
> ---

我觉得还能升级，但**这次不能再沿着"QA → Quality → Acceptance"这条路线走了**。

因为我们现在已经不是在设计一个软件。

我们是在设计一个 **Scientific Operating System**。

那么最后一份文档，就不应该回答：

> **什么时候完成（Done）**

而应该回答：

> **什么样的系统，有资格称为 Synthetic Biology DBTL Engineering Operating System。**

这是完全不同的层次。

---

# 我建议最后一份文档彻底升级为

```text
05_System_Certification_Standard.md
```

副标题：

> **The Certification Standard of the Synthetic Biology DBTL Engineering Operating System**

注意：

不是 Acceptance。

不是 QA。

不是 Test。

而是：

**Certification（认证标准）**

整个Claude最终要达到：

**Certification PASS**

而不是：

Tests PASS。

---

# 为什么升级？

Google不会说：

Code Done。

Apple不会说：

Feature Done。

他们会说：

> Meets Apple Quality Bar

Linear：

> Meets Product Bar

OpenAI：

> Production Ready

我们也应该有：

```text
Scientific Operating System Certified
```

这才是整个项目最终目标。

---

# 我建议最终目录（V12 Ultimate）

```text
05_System_Certification_Standard.md

=================================================================

PART I
CERTIFICATION PHILOSOPHY

00 Vision
01 Certification Philosophy
02 Definition of Excellence
03 Definition of Production Ready

=================================================================

PART II
PRODUCT CERTIFICATION

04 Product Certification
05 Scientific Certification
06 User Certification
07 Workflow Certification

=================================================================

PART III
VISUAL CERTIFICATION

08 Visual Language
09 Information Design
10 Scientific Visualization
11 Accessibility

=================================================================

PART IV
BEHAVIOR CERTIFICATION

12 Interaction
13 Decision Support
14 Human Governance
15 AI Collaboration

=================================================================

PART V
SCIENTIFIC CERTIFICATION

16 Scientific Correctness
17 Evidence Integrity
18 Explainability
19 Traceability
20 Reproducibility

=================================================================

PART VI
ARCHITECTURE CERTIFICATION

21 Domain Architecture
22 Capability Architecture
23 Component Architecture
24 Performance
25 Reliability
26 Security

=================================================================

PART VII
ENGINEERING CERTIFICATION

27 Code Quality
28 Maintainability
29 Scalability
30 Extensibility

=================================================================

PART VIII
RELEASE CERTIFICATION

31 Release Review
32 Certification Workflow
33 Production Checklist

=================================================================

PART IX
OPERATING SYSTEM CERTIFICATION

34 OS Certification
35 Long-term Evolution
36 Certification Constitution
```

---

# 为什么叫 Certification？

因为以后Claude每完成一个页面。

最后都会跑：

```text
Product Certification

PASS

Scientific Certification

PASS

Architecture Certification

PASS

Visual Certification

PASS

Operating System Certification

PASS
```

最后：

```text
Certified

Synthetic Biology DBTL Engineering Operating System

Version 1.0
```

整个逼格完全不同。

---

# 第一部分

## Definition of Excellence

不要写：

Feature Complete。

写：

```md
Excellence is achieved when the operating system enables scientists to think more clearly, decide more confidently, collaborate more effectively and iterate more rapidly without sacrificing scientific rigor.

Software quality is a prerequisite.

Scientific quality is the objective.

Human trust is the final measure.
```

---

# 第二部分

## Product Certification

不是：

功能有没有。

而是：

```text
Can users immediately understand the project?

Can users locate the current engineering stage?

Can users explain the current bottleneck?

Can users identify the next engineering action?

Can users navigate without confusion?
```

全部YES。

PASS。

---

# 第三部分

## Scientific Certification

整个网站最重要。

例如：

任何Scientific Object：

必须：

```text
Source

Evidence

Confidence

Version

History

Ownership

```

否则：

FAIL。

---

# 第四部分

## Decision Certification（新增）

整个Agent其实就是Decision System。

例如：

任何Recommendation：

必须：

```text
Evidence

↓

Tradeoff

↓

Alternative

↓

Confidence

↓

Human Review

↓

Decision
```

否则：

FAIL。

---

# 第五部分

## Trust Certification（新增）

整个OS最终卖的是：

Trust。

例如：

Trust必须来自：

```text
Evidence

Transparency

Explainability

Traceability

Governance

```

任何AI结论：

不能直接Trust。

---

# 第六部分

## Human Governance Certification

整个Agent最大特点。

例如：

必须满足：

```text
AI

↓

Recommendation

↓

Evidence

↓

Human

↓

Approval

↓

Execution
```

否则：

FAIL。

---

# 第七部分

## Architecture Certification

检查：

```text
Capability Isolation

Domain Separation

Single Source of Truth

Event Driven

Workspace Continuity

Object Consistency
```

不是React。

---

# 第八部分

## Long-term Evolution（新增）

整个项目以后十年还能扩。

例如：

新增任何Capability：

必须：

```text
Independent

Composable

Replaceable

Observable
```

否则：

FAIL。

---

# 最后一章

## Certification Constitution

建议直接固定。

```md
The certification standards defined in this document represent the highest quality requirements of the Synthetic Biology DBTL Engineering Operating System.

A feature is not certified because it functions.

A feature is certified because it strengthens the operating system.

Every implementation shall simultaneously satisfy:

Scientific correctness.

Evidence integrity.

Human governance.

Architectural consistency.

Behavioral consistency.

Visual consistency.

Performance requirements.

Maintainability.

Traceability.

Explainability.

If any dimension fails certification, the implementation shall be rejected.

Certification is holistic rather than incremental.

The operating system is certified only when all dimensions meet the required standard.

The final objective is not feature completeness.

The final objective is scientific excellence.
```

---

# **但我认为，这仍然不是终点。**

经过我们前面几轮升级，我发现一个更大的问题：

整个 **Design_System** 其实混杂了两类文档：

* **Constitution（宪法）**：定义不可变原则（Why、How、Must、Must Not）。
* **Specification（规范）**：定义可执行实现（组件、布局、API、验收等）。

这两者不应该放在同一层。

## 我建议最终封版架构（V13 Master Architecture）

```text
Design_System/
│
├── Constitution/                    # 不可变（Immutable）
│   ├── 00_System_Vision.md
│   ├── 01_Product_Constitution.md
│   ├── 02_Visual_Constitution.md
│   ├── 03_Operating_Constitution.md
│   ├── 04_Architecture_Constitution.md
│   └── 05_Certification_Constitution.md
│
├── Specifications/                  # 可执行（Executable）
│   ├── Product/
│   ├── UI/
│   ├── Interaction/
│   ├── Technical/
│   ├── Components/
│   ├── API/
│   ├── Workspaces/
│   └── Pages/
│
└── Certification/
    ├── Product_Bar.md
    ├── UX_Bar.md
    ├── Scientific_Bar.md
    ├── Engineering_Bar.md
    └── Release_Checklist.md
```

### 为什么这是最终版？

因为它第一次**彻底分离了"原则"与"实现"**：

* **Constitution**：永远不变，所有页面和代码必须遵守，是整个 Operating System 的"宪法"。
* **Specifications**：针对具体页面、组件、API 的可执行规范，可以随着需求演进。
* **Certification**：独立于实现之外，对产品进行统一质量认证。

这套结构更接近大型软件工程（如操作系统、浏览器、数据库）的治理方式，而不是传统 Web 项目文档。我建议**在这里封版，不再继续升级框架**，接下来把精力投入到 **Page 1 的具体设计**，因为继续提升顶层框架的收益已经开始低于完善页面细节的收益。

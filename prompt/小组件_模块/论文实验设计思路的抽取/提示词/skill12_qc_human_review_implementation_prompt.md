我已经读取了你上传的原版 **Skill12【AI自检与人工复核并行】Prompt**。

结合前面已经完成的：

* **Skill07 V3：Experimental Design Extraction**
* **Skill08 V2：Evidence Provenance Binding**
* **Skill09 V2：Experimental Design Knowledge Quality Evaluation**
* **Skill10 V2：K12 Adaptation & Engineering Design Space Analysis**
* **Skill11 V2：Evidence-driven DBTL Engineering Plan Generator**

Skill12需要进行一次**接口级优化**。

原版整体方向正确：

> 自动QC + Human Review + Audit Trail + 非阻塞Pipeline

这一点必须保留。

但是现在前面的Skill已经升级，所以Skill12需要从：

> “检查AI输出是否正确”

升级为：

> **DBTL Engineering Governance Layer（DBTL工程治理层）**

---

# 一、原Skill12需要优化的问题

---

## 问题1：输入范围需要明确

原版：

> 支持Skill01-Skill11全部Artifact

这个方向正确。

但是没有区分：

不同阶段检查重点不同。

例如：

### Skill03论文验证

检查：

* DOI真实性
* 元数据一致性

### Skill07实验设计抽取

检查：

* 字段完整性
* Evidence覆盖

### Skill11工程方案

检查：

* reported/AI proposal隔离
* Human approval需求

所以需要：

增加：

## Skill-specific QC Rules

---

## 问题2：QC不应该只是通用检查

原版：

* schema
* provenance
* completeness
* logic
* hallucination

正确。

但是对于现在系统：

需要增加：

### Evidence Integrity Check

检查：

Evidence是否支持claim。

---

### Source Separation Check

检查：

论文事实

↓

AI建议

是否混淆。

---

### Engineering Safety Check

检查：

AI是否生成：

未经证据支持的实验方案。

---

## 问题3：Human Review需要和Skill11结合

Skill11新增：

```text
AI-generated proposal level
Level1
Level2
Level3
```

所以Skill12需要规定：

---

Level1:

自动通过。

---

Level2:

建议审核。

---

Level3:

必须审核。

---

## 问题4：Audit Trail需要更强

原版：

记录：

user/time/action/change

正确。

但是还缺少：

* before artifact
* after artifact
* reason
* related evidence

否则无法追踪科研决策。

---

## 问题5：需要增加“继续运行策略”

原版：

non-blocking。

但是实际Agent需要：

不同状态：

```
PASS
继续

WARNING
继续+记录

REVIEW_REQUIRED
继续但标记

BLOCKED
暂停当前artifact

```

否则：

“不中断”会变成完全忽略错误。

---

下面是优化后的完整 Prompt。

---

保存：

```text
skill12_qc_human_review_implementation_prompt_v2.md
```

---

````markdown
# Skill12 Implementation Prompt


# 项目名称

论文实验设计抽取

Literature Experimental Design Extraction


---

# 当前任务


实现：

# Skill12：
AI质量控制与人工治理 Skill


AI Quality Control & Human Governance Engine


---

# 目标


建立整个论文实验设计抽取系统的治理层。


负责：

1. 自动质量检查

2. 风险识别

3. 人工审核任务生成

4. 非阻塞式Human-in-the-loop流程

5. Audit Trail记录


保证：

AI产生的科研知识：

可追踪

可解释

可审核

可纠错


---

# Pipeline位置


Skill01

需求解析


↓

Skill02

文献检索


↓

Skill03

论文验证


↓

Skill04

PDF获取


↓

Skill05

PDF解析


↓

Skill06

文本清洗


↓

Skill07

实验设计抽取


↓

Skill08

Evidence绑定


↓

Skill09

质量评估


↓

Skill10

K12适配


↓

Skill11

工程方案生成


↓

Skill12

治理层


↓

Skill13

前端展示


---

# Skill12定位


Skill12不是：

❌重新分析论文

❌重新生成实验方案

❌替代科研人员判断


Skill12负责：

## Governance Layer


回答：

1. 当前Artifact是否可信？

2. 是否需要人工关注？

3. 是否允许进入下一阶段？

4. 谁修改过什么？


---

# 核心设计原则


# 1. 自动检查与人工审核并行


禁止：

AI输出

↓

等待人工

↓

继续


---

正确：

AI输出

↓

Automatic QC

↓

生成Review Task

↓

Pipeline继续

↓

Human Review

↓

Audit记录



---

# 2. 不同Artifact不同QC规则


Skill12必须支持：

Skill-specific QC。


---

例如：

Skill07：

检查：

- schema
- unknown
- hallucination


Skill08：

检查：

- evidence coverage
- quote support


Skill11：

检查：

- reported/AI separation
- approval requirement


---

# 输入


来自Skill01-Skill11。


统一结构：

```json
{

"skill_name":"",

"artifact_id":"",

"artifact_type":"",

"artifact_content":{},

"provenance":{},

"quality_report":{},

"previous_validation":[]

}

````

---

# 输出

生成三个对象：

---

# 1. QC Report

```json
{

"qc_report":{

"schema_check":{},

"evidence_check":{},

"logic_check":{},

"hallucination_check":{},

"source_separation_check":{},

"final_status":""

}

}

```

---

# 2. Human Review Task

```json
{

"review_task":{

"task_id":"",

"artifact_id":"",

"priority":"",

"reason":"",

"issues":[],

"suggested_action":"",

"status":"pending"

}

}

```

---

# 3. Audit Event

```json
{

"audit_event":{

"event_type":"",

"artifact_id":"",

"timestamp":"",

"actor":"",

"before":"",

"after":"",

"reason":""

}

}

```

---

# QC模块

---

# 1. Schema Integrity Check

检查：

* required fields
* datatype
* structure

失败：

schema_warning

---

# 2. Provenance Check

检查：

所有reported信息：

必须有：

* evidence
* source_location

否则：

REVIEW_REQUIRED

---

# 3. Evidence Support Check

检查：

Evidence是否真正支持claim。

例如：

claim:

gene knockout improves production

但是quote:

only describes knockout construction

不能认为支持。

---

# 4. Completeness Check

检查：

关键字段缺失。

例如：

strain unknown

输出：

missing_information

---

# 5. Logic Consistency Check

检查：

内部逻辑。

例如：

Skill07:

knockout experiment

但是：

没有strain

warning

---

# 6. Hallucination Check

检测：

* 未报道参数
* 自动补实验条件
* 新机制解释

---

# 7. Source Separation Check

检查：

论文事实：

reported

AI建议：

AI-generated proposal

不能混合。

---

# 8. Engineering Safety Check

针对Skill11。

检查：

AI是否：

* 新增gene target
* 新增实验参数
* 新增机制

没有明确标记：

block

---

# QC状态体系

允许：

## PASS

无需人工。

继续。

---

## WARNING

存在轻微问题。

继续。

记录。

---

## REVIEW_REQUIRED

需要人工查看。

Pipeline继续。

---

## BLOCKED

当前artifact不能进入下一阶段。

---

# Human Review机制

建立：

Review Queue。

结构：

```json
{

"task_id":"",

"artifact_id":"",

"priority":"",

"reason":"",

"issues":[],

"created_time":"",

"status":"pending"

}

```

---

# Review状态

```text
pending

in_review

approved

rejected

revision_required

closed

```

---

# Human操作

支持：

## Approve

接受。

---

## Reject

拒绝。

---

## Modify

修改。

必须保存：

before

after

---

## Comment

添加说明。

---

# Skill11特殊治理规则

读取：

AI proposal level。

---

Level1:

已有论文支持。

自动通过。

---

Level2:

多论文组合。

建议Review。

---

Level3:

工程假设。

必须Human Approval。

---

# Audit Trail

所有事件记录：

包括：

* AI生成
* QC结果
* 人工修改
* 审核决定

结构：

```json
{

"event_type":"",

"artifact_id":"",

"actor":"AI/Human",

"timestamp":"",

"action":"",

"before":"",

"after":"",

"reason":"",

"evidence":[]

}

```

---

# 不允许行为

禁止：

## 1

删除历史结果。

---

## 2

覆盖原始AI输出。

---

## 3

AI伪造Human approval。

---

## 4

Human修改Evidence事实。

Evidence优先。

---

# 工程结构

```
skills/

skill12_qc_human_governance/


├── README.md

├── skill.py


├── qc/


│
├── schema_checker.py

├── provenance_checker.py

├── evidence_checker.py

├── completeness_checker.py

├── logic_checker.py

├── hallucination_checker.py

├── source_checker.py


├── review/


│
├── review_queue.py

├── review_task.py

├── review_state.py


├── audit/


│
├── audit_logger.py

├── event_store.py


├── rules/


│
├── skill_rules.py


├── schema.py

├── validator.py

├── logger.py

├── error_codes.py


├── tests/


├── test_schema.py

├── test_evidence.py

├── test_nonblocking.py

├── test_audit.py

├── test_ai_proposal.py


└── examples/

```

---

# Workflow

Step1

接收Artifact

↓

Step2

识别Skill类型

↓

Step3

加载QC规则

↓

Step4

执行自动检查

↓

Step5

生成QC Report

↓

Step6

判断Review需求

↓

Step7

创建Review Task

↓

Step8

Pipeline继续

↓

Step9

Human反馈

↓

Step10

写Audit Trail

---

# Self Check

## Check1

QC覆盖率

所有Artifact是否检查。

---

## Check2

Review Task完整性

必须包含：

reason

artifact

priority

---

## Check3

Audit完整性

所有修改：

before/after

---

## Check4

Non-blocking验证

人工未完成：

系统仍运行。

---

## Check5

Permission验证

AI不能approve自己。

---

# Logging

```json
{

"skill_name":

"skill12_qc_human_governance",

"artifact_id":"",

"qc_status":"",

"review_required":false,

"review_task_id":"",

"audit_event_id":"",

"errors":[]

}

```

---

# Error Handling

## GOV001

QC失败

warning

---

## GOV002

Review创建失败

retry

---

## GOV003

Audit失败

critical

---

## GOV004

非法审批

reject

---

## GOV005

AI伪造Human Approval

block

---

# 测试要求

## Test1

完整实验方案

PASS

---

## Test2

reported字段无Evidence

REVIEW_REQUIRED

---

## Test3

AI proposal Level3

Human Approval Required

---

## Test4

人工修改字段

保存before/after

---

## Test5

人工未审核

Pipeline继续

---

## Test6

AI伪造approve

失败

---

# 后续接口

输出给：

Skill13

需要：

* QC status
* Review status
* Audit timeline
* Confidence

---

# 最终验收标准

Skill12完成后必须：

1. 支持全Pipeline治理。

2. 自动QC。

3. 人工审核非阻塞。

4. 支持Artifact级追踪。

5. 支持Evidence检查。

6. 支持AI方案治理。

7. 完整Audit Trail。

8. 防止AI伪造审批。

9. 有日志。

10. 有测试。

---

开始实现 Skill12。

```

---

## 相比原版核心升级

|部分|原Skill12|V2|
|-|-|-|
|定位|QC + Review|完整Governance Layer|
|QC规则|通用|Skill-specific|
|Evidence检查|有|增强|
|Skill11治理|无|增加|
|AI Proposal管理|无|增加|
|Audit|基础|科研决策级|
|状态流转|简单|PASS/WARNING/REVIEW/BLOCKED|
|Human Approval|通用|风险分级|

---

这样 Skill07-12 的逻辑现在形成：

```

Skill07
实验设计知识

↓

Skill08
证据可信

↓

Skill09
质量评价

↓

Skill10
K12迁移分析

↓

Skill11
工程方案

↓

Skill12
治理与审核

```

这个版本更符合你们最初定义的：

**Persistent, Traceable, Human-Governed DBTL Engineering System**

因为真正的科研Agent不仅要“生成方案”，还必须知道：

- 为什么可信；
- 哪里不确定；
- 谁批准过；
- 哪些地方需要人介入。
```

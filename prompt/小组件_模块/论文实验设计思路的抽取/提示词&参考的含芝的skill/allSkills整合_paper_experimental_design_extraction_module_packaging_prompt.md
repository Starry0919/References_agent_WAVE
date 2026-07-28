这个大模块 Prompt 和前面 13 个 Skill 的 Prompt 不一样。

前面：

> 一个 Skill = 一个独立能力模块

现在：

> **论文实验设计抽取 = 一个可被 Agent 调用的完整 Capability Module**

它需要解决的问题不是“实现某个功能”，而是：

1. 如何封装13个Skill；
2. 如何定义统一输入输出；
3. 如何被 Agent Workflow 调用；
4. 如何支持异步运行；
5. 如何支持中断恢复；
6. 如何支持人工审核；
7. 如何支持未来替换LLM/API；
8. 如何形成独立插件。

因此这个 Prompt 应该交给 Codex：

> 在13个Skill全部完成后，将它们包装成一个独立 Agent Module。

---

建议文件名：

```text
paper_experimental_design_extraction_module_packaging_prompt.md
```

---

# Codex Prompt

```markdown
# Module Packaging Implementation Prompt


# 项目名称

论文实验设计抽取


Literature Experimental Design Extraction Module


---

# 当前任务


将已经实现完成的：

Skill01-Skill13


组合成为一个完整、独立、可调用的Agent模块。


模块名称必须固定为：

# 论文实验设计抽取


英文：

Literature Experimental Design Extraction Module


---

# 背景


当前系统已经具备：

Skill01

用户需求解析与检索策略生成


Skill02

文献自动检索


Skill03

论文真实性验证


Skill04

论文PDF获取


Skill05

PDF结构化解析


Skill06

Markdown科学文本清洗


Skill07

实验设计结构化抽取


Skill08

实验设计原文证据绑定


Skill09

实验设计质量评估


Skill10

K12适配与实验设计比较


Skill11

工程化实验方案生成


Skill12

AI自检与人工复核并行


Skill13

前端展示适配


---

# 目标


构建：

一个统一入口、统一状态管理、统一数据协议的Agent Capability。


最终Agent只需要调用：

论文实验设计抽取


即可完成完整Workflow。


---

# 模块定位


该模块不是：

论文阅读工具。


不是：

实验方案生成器。


而是：

> Evidence-driven, Human-governed Experimental Design Knowledge Extraction System


负责：

从论文到工程实验方案的完整知识链转换。


---

# 总体架构


最终结构：


```

论文实验设计抽取

|

├── Input Layer

|

├── Workflow Orchestrator

|

├── Skill Pipeline

|

├── Data Contract Layer

|

├── Quality Control Layer

|

├── Human Review Layer

|

├── Output Adapter Layer

|

└── API Interface Layer

````


---

# 一、统一模块入口


创建：

```text
paper_experimental_design_extraction/
````

目录：

```
paper_experimental_design_extraction/


├── README.md


├── module.py


├── config.py


├── schema/


├── workflow/


├── skills/


├── governance/


├── api/


├── storage/


├── logs/


├── tests/


└── examples/

```

---

# 二、统一入口 Interface

必须提供：

## execute()

作为Agent唯一调用入口。

接口：

```python
execute(
    request,
    options
)
```

---

# 输入 Input Schema

统一输入：

```json
{

"task_id":"",

"user_request":"",


"target_system":{

"organism":"",

"strain":""

},


"literature_source":{

"type":
"auto_search/upload",

"files":[],

"doi":[]

},


"requirements":{

"target_phenotype":"",

"engineering_goal":"",

"time_range":"",

"quality_requirement":""

},


"mode":{

"automatic":true,

"human_review":true

}

}
```

---

# 输入模式

支持两种入口：

## Mode 1

AI自动检索

输入：

关键词/目标。

流程：

Skill01

↓

Skill02

---

## Mode 2

人工上传论文

输入：

PDF/DOI。

跳过：

Skill02

进入：

Skill03以后流程。

---

# 三、Workflow Orchestrator

创建：

workflow_engine

负责：

Skill01-13调度。

---

支持：

## Sequential Execution

默认：

```
Skill01

↓

Skill02

↓

...

↓

Skill13
```

---

## Resume Execution

支持：

中断恢复。

例如：

Skill08失败。

恢复：

从Skill08重新执行。

---

## Partial Execution

支持：

只运行部分流程。

例如：

已有PDF：

从Skill05开始。

---

# 四、Skill Registry

创建：

skill_registry

统一管理：

```json
{

"skill_name":"",

"version":"",

"input_schema":"",

"output_schema":"",

"status":""

}

```

---

# 五、统一Artifact系统

所有Skill输出必须成为Artifact。

结构：

```json
{

"artifact_id":"",

"skill_name":"",

"version":"",

"created_time":"",

"content":{},


"provenance":{}

}
```

---

Artifact类型：

```
LiteratureSearchArtifact


PaperValidationArtifact


PDFArtifact


CleanDocumentArtifact


ExperimentalDesignArtifact


EvidenceArtifact


EvaluationArtifact


K12AdaptationArtifact


EngineeringPlanArtifact


QCArtifact


FrontendArtifact

```

---

# 六、统一状态机

整个Workflow使用：

```
CREATED


↓

RUNNING


↓

WAITING_REVIEW


↓

COMPLETED


↓

FAILED

```

---

Skill级状态：

```
PENDING

RUNNING

SUCCESS

WARNING

FAILED

BLOCKED

REVIEW_REQUIRED

```

---

# 七、统一错误处理

所有Skill错误进入：

Error Manager

格式：

```json
{

"error_id":"",

"skill":"",

"type":"",

"message":"",

"retryable":true

}

```

---

错误分类：

```
INPUT_ERROR

PARSER_ERROR

EVIDENCE_ERROR

SCHEMA_ERROR

MODEL_ERROR

HUMAN_REVIEW_ERROR

SYSTEM_ERROR

```

---

# 八、统一日志系统

必须记录：

## Workflow Log

```json
{

"task_id":"",

"start_time":"",

"end_time":"",

"status":""

}

```

---

## Skill Execution Log

```json
{

"skill":"",

"input_artifact":"",

"output_artifact":"",

"duration":"",

"errors":[]

}

```

---

## Audit Log

记录：

* AI生成
* AI修改
* Human审核
* Human修改

---

# 九、LLM Provider抽象

禁止Skill直接调用LLM。

统一：

LLM Adapter

接口：

```python
generate(
prompt,
context,
schema
)
```

支持：

* Kimi-K3
* GPT
* Claude
* 本地模型

---

# 十、Agent调用接口

提供：

## REST API

例如：

POST

```
/api/paper-experimental-design/run
```

---

请求：

```json
{

"user_request":

"寻找提高E.coli K12产量的方法"

}
```

---

返回：

```json
{

"task_id":"",

"status":"running"

}
```

---

查询：

GET

```
/api/paper-experimental-design/status/{task_id}
```

---

结果：

GET

```
/api/paper-experimental-design/result/{task_id}

```

---

# 十一、最终输出统一Schema

最终输出：

Paper Experimental Design Report

结构：

```json
{

"summary":{},


"literature_candidates":[],

"validated_papers":[],

"experimental_designs":[],

"evidence_map":{},


"quality_report":{},


"k12_comparison":{},


"engineering_plan":{},


"governance":{},


"frontend_view":{}

}

```

---

# 十二、Frontend Adapter接口

最终直接提供：

frontend_view

供React Agent使用。

包含：

* Summary
* Step Cards
* What
* Why
* How
* Evidence
* Risk
* Review Status

---

# 十三、Human Governance集成

人工审核不能阻塞Workflow。

支持：

```
AI生成

↓

QC

↓

Review Queue

↓

继续运行

↓

Human反馈写入Audit

```

---

# 十四、配置系统

提供：

config.yaml

包含：

```yaml

llm:

provider:

kimi


workflow:

retry:

3


review:

enabled:

true


logging:

level:

INFO

```

---

# 十五、测试要求

必须包含：

## End-to-End Test

输入：

用户目标

输出：

完整实验方案。

---

## Upload Test

上传PDF。

验证：

PDF进入流程。

---

## DOI Test

输入DOI。

验证：

论文验证。

---

## Failure Recovery Test

模拟Skill失败。

验证：

恢复。

---

## Human Review Test

验证：

人工审核不阻塞。

---

## API Test

验证：

Agent调用。

---

# 十六、最终README要求

README必须说明：

1.

模块用途。

2.

输入格式。

3.

输出格式。

4.

13个Skill关系。

5.

API调用方式。

6.

如何接入Agent。

7.

如何替换LLM。

---

# 最终验收标准

完成后：

必须满足：

1. 13个Skill成为一个独立模块。

2. 模块名称：

论文实验设计抽取。

3. 有统一入口。

4. 有统一Input Schema。

5. 有统一Output Schema。

6. 支持Agent调用。

7. 支持API调用。

8. 支持Human Review。

9. 支持Audit Trail。

10. 支持失败恢复。

11. 支持未来模型替换。

12. 支持前端展示。

---

开始实现：

论文实验设计抽取 Module Packaging。

```

---

这一步完成后，你们的结构会从：

```

13个Skill集合

```

升级成：

```

Agent Capability Module

```
    ↓
```

论文实验设计抽取

```
    ↓
```

可被任何Agent调用

````

也就是说，未来在你的 Synthetic Biology DBTL Engineering OS 里面，不再需要知道 Skill07、Skill08、Skill09 的存在。

上层 Agent 只需要调用：

```python
paper_experimental_design_extraction.execute()
````

即可。

这才符合你们之前设计的 **Agent Skill → Module → System Capability** 三层架构。

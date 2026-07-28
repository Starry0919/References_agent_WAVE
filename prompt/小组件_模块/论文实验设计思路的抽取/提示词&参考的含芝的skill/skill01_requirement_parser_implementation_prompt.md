下面这份 Prompt 是给 **Codex 直接执行 Skill1 开发** 的版本。

我会假设 Codex：

* 不知道之前聊天背景；
* 不知道为什么要做这个模块；
* 只知道当前仓库文件；
* 需要自己读取 framework 里面已经定义好的 schema。

所以 Prompt 会包含：

1. 项目背景；
2. Skill1定位；
3. 不允许做什么；
4. 输入输出要求；
5. 自检机制；
6. 日志；
7. 测试；
8. 文件位置；
9. 验收标准。

建议保存为：

```
skill01_requirement_parser_implementation_prompt.md
```

然后交给 Codex。

---

````markdown
# Skill01 Implementation Prompt

# 项目名称

论文实验设计抽取（Literature Experimental Design Extraction）


---

# 当前任务

实现 Skill01：

## 用户需求解析与检索策略生成 Skill

目标：

将用户输入的自然语言科研需求，转换为标准化、结构化、可执行的文献检索任务。

该 Skill 是整个“论文实验设计抽取”模块的入口。

当前不要实现后续 Skill：

- 文献检索
- DOI验证
- PDF下载
- PDF解析
- 实验设计抽取

只负责：

用户需求理解 → 检索策略生成。


---

# 项目背景

该模块最终目标：

构建一个可审计、可追踪、低幻觉的科研文献实验设计提取系统。


完整流程：

User Research Question

↓

Skill01 Requirement Parsing

↓

Skill02 Literature Retrieval

↓

Skill03 Citation Validation

↓

Skill04 PDF Acquisition

↓

Skill05 PDF Parsing

↓

Skill06 Markdown Cleaning

↓

Skill07 Experimental Design Extraction

↓

Skill08 Evidence Binding

↓

Skill09 Quality Evaluation

↓

Skill10 K12 Transfer Analysis

↓

Skill11 Engineering Proposal

↓

Skill12 QC + Human Review

↓

Skill13 Frontend Adapter


Skill01 是整个Pipeline的入口。


---

# 开发原则（必须遵守）


## 1. 不允许LLM直接输出自由文本作为最终结果

所有输出必须符合统一Schema。


读取：

framework/unified-schema.json


如果Schema已经定义相关对象：

必须复用。

禁止重新设计新的、不兼容的数据结构。


---

## 2. 禁止幻觉补全


如果用户没有提供：

- organism
- strain
- phenotype
- engineering goal

不能根据常识补充。


必须输出：

unknown


或者：

null


例如：

用户：

“找提高产量的方法”


不能自动认为：

organism = E.coli


必须：

organism:
unknown


---

## 3. 所有字段必须有状态


每个解析字段需要记录：

- value
- source
- confidence
- extraction_status


例如：

```json
{
"value":"E.coli K12",
"source":"user_input",
"confidence":1.0,
"status":"reported"
}
````

允许状态：

reported

unknown

inferred

needs_clarification

其中：

inferred必须谨慎使用。

---

# Skill01功能定义

## 输入 Input

用户自然语言科研需求。

例如：

```
寻找近5年利用E.coli K12基因敲除提高琥珀酸产量的高影响力论文
```

或者：

```
我想研究某代谢通路优化方法
```

---

# 输出 Output

生成：

## Research Intent Object

以及：

## Literature Search Specification

---

# 输出必须包含字段

## 1. Research Objective

研究目标。

例如：

```json
{
"objective":
"increase succinate production"
}
```

---

## 2. Organism

有机体。

字段：

* organism_name
* taxonomy_level

例如：

```json
{
"organism":"Escherichia coli"
}
```

---

## 3. Strain

菌株。

例如：

K-12

MG1655

BW25113

如果没有：

unknown

---

## 4. Engineering Objective

工程目标。

例如：

* knockout
* overexpression
* pathway optimization
* metabolic engineering
* protein engineering

---

## 5. Target Phenotype

目标表型。

例如：

* production increase
* growth improvement
* stress tolerance

---

## 6. Engineering Method

例如：

* gene knockout
* CRISPR
* CRISPRi
* adaptive evolution
* plasmid engineering

---

## 7. Search Keywords

自动生成：

Primary keywords

Secondary keywords

Synonyms

例如：

Primary:

"E.coli K12"

"succinate production"

Secondary:

"metabolic engineering"

"gene knockout"

---

## 8. Inclusion Criteria

生成文献纳入标准。

例如：

* publication year
* organism match
* engineering relevance
* experimental validation
* peer reviewed

---

## 9. Exclusion Criteria

例如：

* review only
* no experimental data
* unrelated organism

---

## 10. Time Range

例如：

2020-2026

如果用户未指定：

输出：

default_policy

不要直接假设。

---

## 11. Literature Quality Requirement

例如：

* journal impact
* citation
* experimental evidence level

---

# Skill内部架构要求

实现时必须包含：

```
skill01_requirement_parser/


├── README.md

├── skill.py

├── schema.py

├── validator.py

├── logger.py

├── tests/

│   ├── test_normal.py
│   ├── test_missing_information.py
│   ├── test_ambiguous_request.py
│   └── test_hallucination_prevention.py

└── examples/

```

---

# Skill执行流程

内部流程：

User Input

↓

Input Normalization

↓

Scientific Intent Extraction

↓

Missing Information Detection

↓

Search Strategy Generation

↓

Schema Validation

↓

Self Check

↓

Output

---

# Self Check机制

Skill运行结束后必须自动检查：

## Check 1

Schema完整性

检查：

所有required字段是否存在。

---

## Check 2

幻觉检查

检查：

是否出现用户没有提供来源的信息。

例如：

用户没有说菌株。

输出：

E.coli K12

必须失败。

---

## Check 3

逻辑一致性

例如：

Engineering method:

gene knockout

但：

phenotype:

protein folding

需要提示。

---

## Check 4

检索可执行性

检查：

生成的keywords是否足够用于下一步检索。

---

# Logging要求

每次运行必须记录：

```json
{
"skill_name":
"skill01_requirement_parser",

"timestamp":

"input":

"output":

"model":

"validation_result":

"errors":

"confidence":

}
```

日志保存位置：

logs/

---

# Error Handling

定义错误。

至少包含：

REQ001

用户需求为空

REQ002

需求过于模糊

REQ003

无法解析研究目标

REQ004

Schema validation failed

REQ005

Hallucination detected

---

# 测试要求

必须提供测试。

## Test 1 正常输入

输入：

寻找E.coli K12基因敲除提高乙醇产量的论文

期待：

正确解析：

organism

strain

engineering method

phenotype

---

## Test 2 信息缺失

输入：

寻找提高产量的方法

期待：

organism:

unknown

strain:

unknown

不能补充E.coli。

---

## Test 3 模糊需求

输入：

找一些代谢工程论文

期待：

needs_clarification

---

## Test 4 幻觉测试

输入：

研究某未知菌株

期待：

不生成具体菌株。

---

# 与后续Skill接口

输出必须能够直接被：

Skill02 Literature Retrieval

调用。

Skill02需要的数据：

* keywords
* inclusion criteria
* exclusion criteria
* organism
* strain
* engineering objective
* phenotype
* quality requirement

---

# 最终验收标准

完成后必须满足：

1. Skill01可以独立运行。

2. 输出符合统一Schema。

3. 不产生未来源信息。

4. 所有字段具有状态。

5. 有完整日志。

6. 有失败处理。

7. 有测试案例。

8. 输出可以直接传递给Skill02。

---

# 注意

不要修改：

framework/

中的核心设计。

如果发现Schema不足：

不要直接修改。

先提出：

Schema change proposal

等待确认。

---

开始实现 Skill01。

```

---

这版 Prompt 有一个关键点：**限制 Codex 不要“自作主张扩展系统”**。

因为现在你们这个项目已经进入架构阶段，最大风险不是不会写，而是：

- Skill1自己造一套schema；
- Skill2接不上；
- 后面13个Skill全部返工。

所以这里明确：

> 发现Schema不足 → 提交proposal，不允许直接改framework。

这和你们原始 agent-harness 的设计理念是一致的：**模块可以进化，但不能静默破坏已有契约。**
```

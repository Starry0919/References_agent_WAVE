下面是 **Skill06【Markdown科学文本清洗】** 的 Codex 工程开发 Prompt。

这个 Skill 很容易被误解成“格式美化”，但在你们整个系统里，它实际上是：

> **Scientific Markdown Normalization Layer（科学文本标准化层）**

它的任务不是让 Markdown 好看，而是：

**把 MinerU 输出的“机器解析文本”转换成 LLM 可以稳定理解、后续实验设计抽取可以准确读取的标准科研文档。**

核心原则：

* 不改变论文科学含义；
* 不删除实验细节；
* 不总结；
* 不推理；
* 只做结构修复和文本标准化；
* 所有修改必须可追踪（before → after）。

---

保存：

```text
skill06_markdown_cleaning_implementation_prompt.md
```

---

````markdown
# Skill06 Implementation Prompt

# 项目名称

论文实验设计抽取
(Literature Experimental Design Extraction)


---

# 当前任务

实现：

## Skill06：Markdown科学文本清洗 Skill

Scientific Markdown Cleaning & Normalization


目标：

将 Skill05 输出的结构化 Markdown 文档，
转换为适合LLM理解和后续实验设计抽取的标准科研Markdown。


输入：

Structured Markdown Document


输出：

Clean Scientific Markdown


---

# 项目背景


完整Pipeline：


Skill01
用户需求解析

↓

Skill02
文献自动检索

↓

Skill03
论文真实性验证

↓

Skill04
论文PDF获取

↓

Skill05
PDF结构化解析

↓

Skill06
Markdown科学文本清洗 ← 当前任务

↓

Skill07
论文实验设计结构化抽取


---

# Skill06定位


Skill06不是Markdown格式美化工具。


它负责：

## Scientific Text Normalization Layer


目标：

提高LLM对论文结构、实验方法、图表关系的理解能力。


---

# 当前Skill负责


✅ 删除PDF解析噪声

✅ 修复Markdown结构

✅ 修复表格

✅ 保留论文章节结构

✅ 保留Figure/Table编号

✅ 保留引用关系

✅ 修复解析错误

✅ 生成清洗质量报告

✅ 输出Clean Document Artifact


---

# 当前Skill不负责


❌ 实验设计总结

❌ 论文摘要生成

❌ 方法解释

❌ 科学推理

❌ 删除实验细节


---

# 核心原则


# 1. 科学内容不可改变原则


清洗只能改变：

格式

结构

解析错误


不能改变：

实验参数

数值

单位

条件

结论


---

例如：


原文：

"Cells were cultured at 37 °C for 12 h."


不能变成：

"Cells were cultured overnight."


因为丢失：

temperature

time


---

# 2. 保留所有可用于实验复现的信息


必须保留：

- concentration
- volume
- time
- temperature
- rpm
- OD value
- strain name
- gene name
- instrument parameter


---

# 3. 所有修改必须可追踪


必须保存：

Before

↓

After


例如：

```json
{
"original":"Table broken",

"cleaned":"Table reconstructed",

"reason":"markdown parsing error"
}
````

---

# 输入 Input

来自：

Skill05 Document Artifact

例如：

```json
{
"paper_id":"xxx",

"markdown_path":"",

"structure_map":{},

"figure_map":{},

"table_map":{}
}
```

---

# 输出 Output

生成：

## Clean Document Artifact

包含：

---

# 1. Clean Markdown

```json
{
"clean_markdown_path":""
}
```

---

# 2. Structure Preservation Report

记录：

```json
{
"sections_preserved":true,

"missing_sections":[]
}
```

---

# 3. Modification Log

记录所有修改：

```json
{
"changes":[

{
"type":"table_fix",

"location":"Methods Table 1",

"reason":"broken markdown"

}

]
}
```

---

# 4. Cleaning Quality Report

例如：

```json
{
"noise_removed":120,

"tables_fixed":5,

"figures_preserved":12,

"citations_preserved":true,

"confidence":0.95
}
```

---

# 5. Markdown → JSON结构化转换


完成Markdown科学清洗后，
必须额外生成对应JSON格式文件。


原因：

Markdown用于：

- 人工阅读
- LLM上下文理解


JSON用于：

- Agent模块之间的数据传递
- 字段级访问
- Evidence绑定
- 前端展示
- Audit Trail记录


因此：

Clean Document Artifact必须同时包含：

1. clean_document.md

2. clean_document.json


---

# JSON输出要求


JSON必须保留：


## Document Metadata


```json
{
"paper_id":"",
"title":"",
"parser":"",
"cleaner_version":""
}
Section Structure

保存论文层级：

{
"sections":[

{
"id":"methods",

"title":"Materials and Methods",

"level":1,

"content":""
}

]
}
Paragraph Object

每个段落独立编号：

{
"paragraph_id":"methods_p003",

"text":"Cells were cultured at 37°C",

"section":"Methods"
}
Figure Object
{
"figure_id":"Figure 1",

"caption":"",

"related_paragraphs":[]
}
Table Object
{
"table_id":"Table 1",

"title":"",

"content":[]
}
Citation Object
{
"citation_id":"ref15",

"text":"",

"target_reference":""
}
Cleaning Metadata

记录：

{
"cleaning_history":[

{
"operation":"remove_footer",

"location":"page3",

"reason":"pdf artifact"
}

]
}
Markdown与JSON一致性检查

必须执行：

Check 1

Markdown章节数量

=

JSON sections数量

Check 2

Markdown Figure数量

=

JSON figure数量

Check 3

Markdown Table数量

=

JSON table数量

Check 4

文本内容一致性

JSON不能修改Markdown科学内容。

最终：

Clean Document Artifact:

{
"markdown_path":"clean_document.md",

"json_path":"clean_document.json"
}

---

另外，我建议**Skill05也应该同步调整**。

因为：

Skill05现在：


PDF → Markdown


应该升级为：


PDF
↓
MinerU

Document Intermediate Representation

↓

markdown
+
structure.json


原因：

Skill05负责“结构恢复”，Skill06负责“清洗”。

如果Skill05不输出结构JSON，Skill06只能重新解析Markdown，浪费一次解析。

---

最终推荐架构：


Skill04
PDF Artifact

    ↓

Skill05
PDF Structure Reconstruction

输出:
├── raw.md
├── document_structure.json

    ↓

Skill06
Scientific Cleaning

输入:
├── raw.md
├── structure.json

输出:
├── clean.md
├── clean.json

    ↓

Skill07
Experimental Extraction

读取:
clean.json

---

# 清洗任务详细要求

# 1. 页眉页脚删除

删除：

* journal header
* page number
* copyright footer
* repeated DOI footer

但是：

不要删除：

* reference DOI
* article information

---

# 2. Markdown章节修复

保证：

```markdown
# Introduction

## Results

## Methods

### Strain construction
```

结构正确。

---

# 3. 表格修复

MinerU常见问题：

* 列错位
* 单元格断裂
* markdown pipe错误

需要：

恢复：

|column1|column2|

结构。

---

禁止：

把表格转成一句话。

---

# 4. Figure处理

必须保留：

Figure编号

例如：

```markdown
Figure 1.
```

Caption。

正文引用：

"shown in Figure 1"

必须保持。

---

# 5. Table处理

必须保留：

Table编号

标题

内容

---

# 6. Citation关系保持

例如：

原文：

[15]

不能删除。

---

保留：

* inline citation
* reference list

---

# 7. 特殊科研格式处理

保持：

## 基因名称

例如：

Δgene

knockout

CRISPRi

---

## 单位

保持：

μL

mM

°C

rpm

OD600

---

## 数值

不能修改：

0.5 mM

500 μL

---

# 8. OCR错误修复

允许修复：

* 字符错误
* 断词
* 编码错误

例如：

"cultu re"

↓

"culture"

---

但是：

不能改变专业词。

---

# 工程结构

创建：

```
skills/

skill06_markdown_cleaning/


├── README.md


├── skill.py


├── cleaners/


│
├── header_footer_cleaner.py

├── markdown_formatter.py

├── table_repair.py

├── citation_preserver.py

├── scientific_term_checker.py



├── diff/


│
├── change_tracker.py



├── validator.py


├── schema.py


├── logger.py


├── error_codes.py


├── tests/


│
├── test_header_remove.py

├── test_table_repair.py

├── test_figure_preserve.py

├── test_citation_preserve.py

├── test_scientific_value_preserve.py


└── examples/
```

---

# 工作流程

## Step 1

读取Document Artifact

↓

## Step 2

验证输入完整性

↓

## Step 3

Markdown解析

↓

## Step 4

执行清洗规则

↓

## Step 5

生成修改diff

↓

## Step 6

质量检查

↓

## Step 7

输出Clean Document Artifact

---

# Self Check机制

Skill完成后必须执行：

## Check 1

章节保持检查

比较：

before structure

after structure

不能大量丢失。

---

## Check 2

Figure/Table保持检查

数量不能异常下降。

---

## Check 3

科学数字保护检查

检查：

数字

单位

浓度

时间

是否被改变。

---

## Check 4

Citation检查

确认：

引用没有消失。

---

## Check 5

幻觉检查

确认：

没有新增论文不存在的信息。

---

# Logging要求

记录：

```json
{
"skill_name":
"skill06_markdown_cleaning",

"paper_id":"",

"input_markdown":"",

"output_markdown":"",

"changes_count":0,

"tables_fixed":0,

"figures_preserved":0,

"errors":[]
}
```

保存：

logs/

---

# Error Handling

定义：

## CLEAN001

Markdown为空

处理：

failed

---

## CLEAN002

结构严重损坏

处理：

partial_output

---

## CLEAN003

表格无法恢复

处理：

保留原始表格

记录warning

---

## CLEAN004

科学内容变化风险

处理：

stop modification

---

## CLEAN005

编码错误

处理：

UTF-8 repair

---

# Retry策略

清洗失败：

最多3次。

尝试：

1.

规则清洗

2.

结构修复

3.

fallback parser

---

# 测试要求

必须实现：

## Test 1

普通论文Markdown

期待：

成功清洗。

---

## Test 2

页眉页脚污染

期待：

删除。

---

## Test 3

复杂Methods表格

期待：

恢复。

---

## Test 4

Figure/Table引用

期待：

保持。

---

## Test 5

实验参数保护测试

输入：

37°C

12h

500 μL

输出：

完全一致。

---

## Test 6

禁止幻觉测试

要求：

不能新增实验信息。

---

# 与后续Skill接口

输出必须支持：

Skill07 Experimental Design Extraction

Skill07输入：

Clean Document Artifact

包含：

* clean_markdown_path
* structure_map
* figure_map
* table_map
* modification_log

---

# 最终验收标准

Skill06完成后必须满足：

1. 能读取Skill05输出。

2. 能生成标准科研Markdown。

3. 保留论文结构。

4. 保留Figure/Table。

5. 保留引用。

6. 修复解析错误。

7. 不改变科学内容。

8. 所有修改有记录。

9. 有完整日志。

10. 有测试。

---

# 注意事项

不要修改framework核心Schema。

如果发现：

CleanDocumentArtifact不足：

创建：

schema_change_proposal.md

不要直接修改。

---

开始实现 Skill06。

```

---

这个 Skill 完成后，你们的文献处理链会变成：

```

Skill04
PDF Artifact
|
↓
Skill05
Document Reconstruction
|
↓
Skill06
Scientific Markdown Normalization
|
↓
Skill07
Experimental Design Extraction

```

其中 Skill06 的价值在于：

**它不是为了让Markdown更漂亮，而是减少LLM在实验设计抽取阶段因为PDF解析噪声导致的误读。**

尤其你们后面要求抽取：

- 培养基组成；
- 基因敲除方式；
- 浓度；
- 时间；
- 温度；
- 仪器参数；
- 重复数；

这些细节，绝大部分错误来源不是模型能力，而是前面的文档结构损坏。所以 Skill06 是整个系统准确率的关键基础层。
```

下面是 **Skill05【PDF结构化解析】** 的 Codex 工程开发 Prompt。

这个 Skill 是整个流程从“文件管理”进入“科学文本理解”的关键节点。

它的定位不是：

> PDF转Markdown脚本

而是：

> Scientific Document Reconstruction Engine（科学文献结构重建引擎）

因为后面的 Skill06（Markdown清洗）、Skill07（实验设计抽取）都依赖这里输出的结构。

核心要求：

* 使用 MinerU 等 PDF parsing 工具；
* 最大程度恢复论文结构；
* 保留 Figure/Table/Supplement/Citation；
* 不破坏科学信息；
* 记录解析过程；
* 输出标准 Document Artifact；
* 解析失败不能静默继续。

---

保存为：

```text
skill05_pdf_structure_parsing_implementation_prompt.md
```

---

````markdown
# Skill05 Implementation Prompt

# 项目名称

论文实验设计抽取
(Literature Experimental Design Extraction)


---

# 当前任务

实现：

## Skill05：PDF结构化解析 Skill

Scientific PDF Structure Reconstruction


目标：

将 Skill04 输出的可信 PDF Artifact，
转换为适用于LLM科学理解的结构化 Markdown 文档。


该Skill负责：

PDF

↓

Structured Markdown


并最大程度恢复：

- 论文章节结构
- Figure
- Table
- References
- Supplement信息
- 文本层级关系


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
PDF结构化解析 ← 当前任务

↓

Skill06
Markdown科学清洗

↓

Skill07
实验设计结构化抽取


---

# Skill05定位


Skill05不是简单文件转换。


它负责：

## Scientific Document Reconstruction Layer


输入：

可信PDF Artifact


输出：

结构化科学文档对象。


---

# 当前Skill负责


✅ 调用MinerU等PDF解析工具

✅ PDF文本提取

✅ Markdown生成

✅ 章节恢复

✅ Figure/Table识别

✅ Caption关联

✅ Reference区域识别

✅ Supplement识别

✅ 解析质量评估

✅ 输出Document Artifact


---

# 当前Skill不负责


❌ Markdown清洗

（Skill06负责）


❌ 实验设计抽取

（Skill07负责）


❌ 科学内容总结


❌ 修改论文内容


---

# 核心原则


# 1. 原文优先原则


PDF中的信息必须原样保留。


禁止：

- 改写实验描述
- 总结章节
- 删除细节


---

# 2. 结构恢复优先


目标不是漂亮Markdown。


目标：

让LLM理解论文结构。


---

# 3. 不确定不补全


如果PDF中：

无法识别章节

无法识别Figure

无法识别Table


输出：

unknown


禁止LLM猜测。


---

# 输入 Input


来自：

Skill04 Paper Artifact


示例：


```json
{
"paper_id":"xxx",

"title":"xxx",

"pdf_path":
"papers/example/original.pdf",

"checksum":
"sha256xxx",

"status":
"verified"
}
````

---

# 输出 Output

生成：

## Document Artifact Object

---

# 1. Document Metadata

```json
{
"paper_id":"",
"pdf_path":"",
"parser":"MinerU",
"parser_version":"",
"parse_time":""
}
```

---

# 2. Markdown Artifact

包含：

```json
{
"markdown_path":"",
"markdown_content":"",
}
```

---

# 3. Structure Map

必须保存论文结构。

例如：

```json
{
"sections":[

{
"title":"Introduction",
"type":"section"
},

{
"title":"Materials and Methods",
"type":"section"
}

]
}
```

---

# 4. Figure Map

必须保存：

```json
{
"figures":[

{
"id":"Figure 1",

"caption":"",

"location":"",

"related_text":""

}

]
}
```

---

# 5. Table Map

例如：

```json
{
"tables":[

{
"id":"Table 1",

"caption":"",

"location":""

}

]
}
```

---

# 6. Reference Map

保存：

```json
{
"references":[],
"citation_links":[]
}
```

---

# 7. Parsing Quality Report

例如：

```json
{
"text_extraction_quality":0.95,

"table_quality":0.8,

"figure_quality":0.9,

"missing_content":[]
}
```

---

# PDF解析流程

## Step 1

读取Paper Artifact

↓

## Step 2

验证PDF checksum

↓

## Step 3

调用MinerU

↓

## Step 4

生成Markdown

↓

## Step 5

恢复结构

↓

## Step 6

生成Figure/Table索引

↓

## Step 7

质量检查

↓

## Step 8

输出Document Artifact

---

# MinerU要求

优先使用：

MinerU

如果不可用：

支持替代parser adapter。

例如：

* PyMuPDF
* GROBID

但必须记录：

parser_type

---

# 工程结构

创建：

```
skills/

skill05_pdf_structure_parsing/


├── README.md


├── skill.py


├── parsers/


│
├── mineru_parser.py

├── pymupdf_parser.py

├── parser_interface.py


├── reconstruction/


│
├── section_reconstructor.py

├── figure_extractor.py

├── table_extractor.py

├── citation_extractor.py


├── artifact/


│
├── document_manager.py


├── validator.py


├── schema.py


├── logger.py


├── error_codes.py


├── tests/


│
├── test_mineru_success.py

├── test_section_detection.py

├── test_figure_detection.py

├── test_table_detection.py

├── test_corrupted_pdf.py


└── examples/

```

---

# 章节恢复要求

必须尽可能识别：

## 一级结构

通常包括：

* Abstract

* Introduction

* Results

* Discussion

* Materials and Methods

* Methods

* References

---

## 二级结构

例如：

Methods

↓

2.1 Strain construction

↓

2.2 Culture conditions

---

# Figure处理要求

必须保留：

Figure编号

*

Caption

*

正文引用关系

例如：

正文：

"as shown in Fig.2"

需要建立关联。

---

# Table处理要求

必须：

* 保留表格内容
* 保留标题
* 保留编号

不能简单转成普通文本。

---

# Supplement处理要求

如果存在：

识别：

* Supplementary Methods
* Supplementary Figures
* Supplementary Tables

并单独标记。

---

# Self Check机制

Skill完成后必须执行：

## Check 1

PDF完整性

确认：

输入checksum一致。

---

## Check 2

Markdown存在

确认：

输出文件非空。

---

## Check 3

章节完整性

检查：

是否存在主要章节。

---

## Check 4

Figure/Table数量一致性

比较：

PDF识别数量

vs

Markdown数量

---

## Check 5

科学信息损失检测

检查：

是否大量空白。

---

# Logging要求

记录：

```json
{
"skill_name":
"skill05_pdf_structure_parsing",

"paper_id":"",

"parser":"MinerU",

"parser_version":"",

"input_pdf_checksum":"",

"output_markdown_path":"",

"figures_detected":0,

"tables_detected":0,

"errors":[]
}
```

保存：

logs/

---

# Error Handling

定义：

## PARSE001

PDF无法读取

处理：

failed

---

## PARSE002

MinerU不可用

处理：

fallback parser

---

## PARSE003

Markdown为空

处理：

retry

---

## PARSE004

结构恢复失败

处理：

输出partial_result

---

## PARSE005

Figure/Table解析失败

处理：

记录missing_content

---

# Retry策略

解析失败：

最多3次。

尝试：

1.

MinerU重新运行

2.

调整参数

3.

fallback parser

---

# 测试要求

必须实现：

## Test 1

正常论文PDF

期待：

生成Markdown

---

## Test 2

包含Figure/Table论文

期待：

正确识别

---

## Test 3

复杂Methods论文

期待：

章节恢复

---

## Test 4

损坏PDF

期待：

failed

---

## Test 5

Supplement论文

期待：

Supplement独立记录

---

# 与后续Skill接口

输出必须支持：

Skill06 Markdown Cleaning

Skill06输入：

Document Artifact

包括：

* markdown_path
* structure_map
* figure_map
* table_map
* reference_map

---

# 最终验收标准

Skill05完成后必须满足：

1. 能处理Skill04输出PDF。

2. 能调用MinerU。

3. 输出结构化Markdown。

4. 保留论文章节。

5. 保留Figure/Table。

6. 保留引用关系。

7. 支持Supplement。

8. 有解析质量报告。

9. 有日志。

10. 有测试。

---

# 注意事项

不要修改framework核心Schema。

如果发现：

DocumentArtifact Schema不足：

创建：

schema_change_proposal.md

不要直接修改。

---

开始实现 Skill05。

```

---

这个 Skill 做完以后，你们整个模块会形成一个非常清晰的分层：

```

Skill01
科研需求理解

Skill02
寻找论文

Skill03
确认论文是真的

Skill04
管理论文文件

Skill05
理解论文结构

Skill06
优化LLM可读性

Skill07
提取实验设计

```

其中 Skill05 是一个非常关键的“桥梁层”。

如果 Skill05 只是简单 `pdf → md`，后面的实验设计抽取质量会直接下降；如果 Skill05 做成 Document Reconstruction Layer，后续 Skill07 才有可能达到你要求的“具体到实验条件、剂量、时间、重复数、仪器参数”的精度。
```

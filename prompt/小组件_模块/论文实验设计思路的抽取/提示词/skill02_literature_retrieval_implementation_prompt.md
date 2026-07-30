下面是 **Skill02【文献自动检索】** 的 Codex 工程开发 Prompt。

这一版默认 Codex：

* 不知道之前聊天背景；
* 不知道 Skill01 做了什么；
* 不知道为什么需要 Kimi-K3；
* 不知道整个模块架构；

所以我把完整上下文、边界、接口、工程要求全部写进去。

注意：这个 Skill **不是让LLM直接“搜索论文”**，而是设计一个**Literature Retrieval Engine**：

* Skill01 输出检索规范；
* Skill02负责调用不同检索源；
* Kimi-K3负责 query expansion、排序、相关性判断；
* 外部数据库负责事实返回；
* 输出进入 Skill03 DOI真实性验证。

---

建议保存：

```
skill02_literature_retrieval_implementation_prompt.md
```

---

````markdown
# Skill02 Implementation Prompt

# 项目名称

论文实验设计抽取
(Literature Experimental Design Extraction)


---

# 当前任务

实现：

## Skill02：文献自动检索 Skill


目标：

根据 Skill01 输出的标准化文献检索规范，
自动从多个科研数据库中检索候选论文，
并生成结构化候选论文列表。


该 Skill 是：

Research Intent

↓

Literature Candidate Discovery

之间的桥梁。


---

# 项目背景


本模块最终目标：

构建一个可审计、可追踪、低幻觉的科研文献实验设计提取系统。


完整流程：

Skill01
用户需求解析与检索策略生成

↓

Skill02
文献自动检索

↓

Skill03
论文真实性验证

↓

Skill04
PDF获取

↓

Skill05
PDF解析

↓

Skill06
Markdown清洗

↓

Skill07
实验设计抽取


---

# 当前Skill边界


Skill02只负责：

✅ 根据检索规范寻找候选论文

✅ 多数据库检索

✅ 论文元数据收集

✅ 初步相关性排序

✅ 输出候选列表


不负责：

❌ DOI真实性最终验证

❌ PDF下载

❌ 实验设计分析

❌ 判断论文实验质量

❌ 判断论文是否适合K12


这些属于后续Skill。


---

# 核心设计原则


## 1. 外部数据库负责事实


禁止：

LLM生成论文。


例如：

错误：

"Kimi认为可能存在这篇论文"


正确：

数据库返回：

title
doi
authors
journal
year


LLM只能：

- 生成query
- 扩展关键词
- 进行相关性排序


---

# 2. 不允许幻觉论文


任何论文必须来自：

真实检索源。


必须保存：

source


例如：

```json
{
"title":"xxx",
"source":"PubMed"
}
````

---

# 3. 支持多来源检索

必须设计Adapter架构。

不要把代码写死。

推荐：

```text
Literature Retrieval Engine


        |
        |
 -----------------------------
 |       |        |          |
PubMed Crossref EuropePMC CNKI
 |
Scholar
 |
WebOfScience
```

---

# 支持检索来源

第一阶段支持：

## PubMed

医学、生物领域核心。

---

## Crossref

DOI和出版信息。

---

## Europe PMC

生命科学全文和摘要。

---

## Google Scholar

通过Adapter设计。

注意：

可能存在访问限制。

必须支持：

unavailable状态。

---

## Web of Science

设计接口。

如果没有API：

返回：

not_configured

---

## CNKI

中文数据库接口。

如果无法访问：

记录：

not_available

---

# LLM使用要求

使用：

Kimi-K3 API

用途：

## 1. Query Expansion

例如：

输入：

gene knockout improve succinate production

生成：

synonyms:

* deletion
* knockout mutant
* metabolic engineering

---

## 2. Search Query Ranking

判断：

哪个query优先。

---

## 3. Candidate Relevance Scoring

根据：

* organism match
* strain match
* engineering method match
* phenotype match
* publication quality

生成：

relevance_score

---

# 不允许：

Kimi直接生成：

* DOI
* title
* journal

所有论文事实必须来自数据库。

---

# 输入 Input

来自：

Skill01

对象：

Literature Search Specification

例如：

```json
{
"organism":"Escherichia coli",
"strain":"K12",
"phenotype":"increase succinate production",
"engineering_method":"gene knockout",
"keywords":[
"E.coli K12",
"succinate",
"knockout"
]
}
```

---

# 输出 Output

生成：

## Literature Candidate Object

每篇论文：

必须包含：

---

## Basic Metadata

```json
{
"title":"",
"doi":"",
"authors":[],
"journal":"",
"year":""
}
```

---

## Source Information

必须：

```json
{
"retrieval_source":
"PubMed",

"retrieval_time":"",

"query_used":""
}
```

---

## Matching Information

包括：

```json
{
"organism_match":true,

"strain_match":true,

"phenotype_match":true,

"engineering_match":true
}
```

---

## Ranking

```json
{
"relevance_score":0.92,

"ranking_reason":"..."
}
```

---

## Validation State

由于Skill03负责验证：

这里不能判断真实。

只能：

```json
{
"citation_validation_status":
"pending"
}
```

---

# 输出Schema要求

必须读取：

framework/unified-schema.json

如果已有：

LiteratureCandidate

必须复用。

禁止重新设计。

---

# 推荐工程结构

创建：

```
skills/

skill02_literature_retrieval/


├── README.md

├── skill.py


├── adapters/

│
├── pubmed_adapter.py

├── crossref_adapter.py

├── europepmc_adapter.py

├── scholar_adapter.py

├── wos_adapter.py

├── cnki_adapter.py



├── query/

│
├── query_expander.py


├── ranking/

│
├── relevance_ranker.py



├── schema.py


├── validator.py


├── logger.py


├── tests/


│
├── test_pubmed.py

├── test_crossref.py

├── test_query_expansion.py

├── test_no_hallucination.py


└── examples/

```

---

# 工作流程

## Step 1

读取Skill01输出

↓

## Step 2

检查输入Schema

↓

## Step 3

生成检索query

↓

## Step 4

调用数据库Adapter

↓

## Step 5

合并结果

↓

## Step 6

去重

依据：

* DOI
* PMID
* title similarity

↓

## Step 7

Kimi-K3相关性评分

↓

## Step 8

Schema验证

↓

## Step 9

输出候选论文列表

---

# 去重要求

同一论文可能来自：

PubMed

Crossref

EuropePMC

必须合并。

优先级：

DOI

>

PMID

>

Title similarity

---

# Self Check机制

Skill运行结束必须检查：

## Check 1

来源真实性

每篇论文：

必须有retrieval_source。

没有：

失败。

---

## Check 2

幻觉检测

检查：

是否存在：

没有数据库来源的论文。

如果：

删除。

---

## Check 3

Schema完整性

检查：

title

source

year

authors

---

## Check 4

Query质量

检查：

query是否覆盖：

organism

phenotype

engineering method

---

## Check 5

重复检查

同一DOI不能重复输出。

---

# Logging要求

每次运行记录：

```json
{
"skill_name":
"skill02_literature_retrieval",

"timestamp":"",

"input_reference":
"skill01_output",

"search_sources":[
"PubMed",
"Crossref"
],

"queries_used":[],

"papers_found":0,

"errors":[],

"model_used":
"Kimi-K3"
}
```

保存：

logs/

---

# Error Handling

定义错误。

至少：

## RET001

Skill01输入缺失

---

## RET002

数据库不可访问

处理：

降级其他数据库。

---

## RET003

API限制

记录：

rate_limit

---

## RET004

没有检索结果

返回：

empty_result

不是失败。

---

## RET005

LLM query expansion失败

fallback：

使用原始关键词。

---

# 测试要求

必须提供测试。

---

# Test 1 正常检索

输入：

E.coli K12 gene knockout succinate production

期待：

返回论文列表。

---

# Test 2 多数据库合并

同一论文：

PubMed

Crossref

验证：

只输出一次。

---

# Test 3 数据库失败

模拟：

PubMed unavailable

期待：

继续Crossref。

---

# Test 4 无结果

输入：

不存在研究方向。

期待：

empty_result

不能生成假论文。

---

# Test 5 幻觉测试

关闭数据库。

要求：

LLM不能生成论文。

---

# 与后续Skill接口

输出必须直接支持：

Skill03 Citation Validation

Skill03需要：

* title
* doi
* authors
* journal
* year
* retrieval_source

---

# 最终验收标准

Skill02完成后必须满足：

1. 支持多数据库Adapter。

2. Kimi-K3只负责query和ranking。

3. 不生成虚假论文。

4. 所有论文来自真实source。

5. 输出符合统一Schema。

6. 支持人工上传入口的数据兼容。

7. 有完整日志。

8. 有错误处理。

9. 有测试案例。

---

# 注意事项

不要修改framework核心Schema。

如果发现：

LiteratureCandidate Schema不足。

请创建：

schema_change_proposal.md

不要直接修改。

---

开始实现 Skill02。

```

---

这一版和 Skill1 最大区别：

Skill1 是 **理解用户意图**；

Skill2 是 **连接真实世界文献数据库**。

所以这里我特别强调了：

> Kimi 不能创造论文，只能辅助检索。

否则后面 Skill3 DOI 验证会变成“给幻觉擦屁股”，整个系统可信性会崩。
```

下面是 **Skill03【论文真实性验证】** 的 Codex 工程开发 Prompt。

这个 Skill 在整个模块里面非常关键，它不是简单“查 DOI”，而是一个 **Citation Validation Gate（文献真实性验证门）**。

核心思想：

* Skill02 可以产生候选论文；
* Skill03 负责阻止虚假引用进入后续流程；
* 任何 DOI、标题、作者、期刊、年份不一致，都必须被捕获；
* 不能让 LLM “相信自己找到的论文”。

因此 Prompt 中我特别强化：

1. **Crossref / PubMed 等外部来源为事实来源**
2. **LLM不能生成 DOI**
3. **最多3次修复尝试**
4. **失败必须留下 Audit Trail**
5. **不能验证通过的论文禁止进入 Skill04**

---

保存为：

```text
skill03_citation_validation_implementation_prompt.md
```

---

````markdown
# Skill03 Implementation Prompt

# 项目名称

论文实验设计抽取
(Literature Experimental Design Extraction)


---

# 当前任务

实现：

## Skill03：论文真实性验证 Skill

Citation Validation Gate


目标：

对 Skill02 输出的候选论文进行真实性和身份一致性验证。

确保进入后续 PDF 下载流程的论文：

- DOI真实存在
- DOI对应正确论文
- 标题一致
- 作者一致
- 期刊一致
- 年份一致


---

# 项目背景


完整Pipeline：

Skill01
用户需求解析与检索策略生成

↓

Skill02
文献自动检索

↓

Skill03
论文真实性验证  ← 当前任务

↓

Skill04
论文PDF获取

↓

Skill05
PDF解析


Skill03 是整个文献进入系统前的第一个强验证Gate。


---

# 当前Skill边界


Skill03负责：

✅ DOI真实性检查

✅ DOI metadata获取

✅ DOI与论文信息匹配

✅ 错误DOI修正尝试

✅ 失败记录

✅ 输出验证结果


不负责：

❌ PDF下载

❌ 实验设计抽取

❌ 判断论文科学价值

❌ 判断论文是否适合K12


---

# 核心原则


## 1. 外部数据库是真实来源


允许使用：

- Crossref
- PubMed
- Europe PMC
- DOI resolver


作为事实来源。


---

## 2. LLM不能创造事实


禁止：

LLM生成：

- DOI
- title
- authors
- journal


LLM只能辅助：

- 判断匹配程度
- 生成重新检索query


---

## 3. 不确定必须保留


如果无法验证：

不能猜。


返回：

unknown

或：

failed


---

# 输入 Input


来自：

Skill02 Literature Retrieval


对象：

Literature Candidate Object


示例：


```json
{
"title":
"Engineering Escherichia coli for succinate production",

"doi":
"10.xxxx/example",

"authors":
[
"Author A"
],

"journal":
"Nature Biotechnology",

"year":
2024,

"retrieval_source":
"Crossref"
}
````

---

# 输出 Output

生成：

## Citation Validation Object

字段：

---

# 1. Original Candidate

保存原始输入。

```json
{
"original_title":"",
"original_doi":"",
"original_source":""
}
```

---

# 2. DOI Validation Result

状态：

```text
verified

mismatch

not_found

retrying

failed
```

---

# 3. DOI Metadata

来自数据库：

```json
{
"doi":"",
"title":"",
"authors":[],
"journal":"",
"year":""
}
```

---

# 4. Matching Report

必须逐字段比较。

例如：

```json
{
"title_match":true,

"author_match":true,

"journal_match":true,

"year_match":true
}
```

---

# 5. Final Decision

允许：

```text
accepted

rejected

needs_review
```

规则：

accepted:

全部核心字段匹配。

rejected:

3次修正失败。

needs_review:

部分字段无法确认。

---

# 验证逻辑

执行流程：

## Step 1

读取候选论文。

↓

## Step 2

检查DOI格式。

↓

## Step 3

调用DOI数据库。

↓

## Step 4

获取真实metadata。

↓

## Step 5

字段匹配。

↓

## Step 6

判断结果。

↓

## Step 7

失败时重新搜索。

↓

## Step 8

输出Validation Object。

---

# DOI验证规则

## DOI存在性

检查：

DOI resolver

Crossref

结果：

存在：

continue

不存在：

retry

---

# 标题匹配

不能要求完全字符串一致。

需要考虑：

* 大小写
* 标点
* 特殊字符

允许：

minor_difference

---

# 作者匹配

检查：

第一作者

以及：

作者列表重叠程度。

---

# 期刊匹配

检查：

journal名称标准化。

例如：

Nature Biotechnology

Nature Biotech.

---

# 年份匹配

允许：

±1年误差。

记录：

year_difference

---

# DOI修正机制

如果验证失败：

最多：

3次 retry

流程：

Attempt 1:

使用原标题搜索。

Attempt 2:

使用：

title + first author

Attempt 3:

使用：

title keywords + journal

---

如果仍失败：

状态：

failed

论文终止进入：

Skill04

---

# 重新检索要求

重新检索只能调用：

真实数据库。

例如：

Crossref API

PubMed

禁止：

LLM直接输出新的DOI。

---

# 工程结构

创建：

```
skills/

skill03_citation_validation/


├── README.md


├── skill.py


├── validator/


│
├── doi_validator.py

├── metadata_matcher.py

├── retry_searcher.py



├── adapters/


│
├── crossref_client.py

├── pubmed_client.py

├── europepmc_client.py



├── schema.py


├── logger.py


├── error_codes.py


├── tests/


│
├── test_valid_doi.py

├── test_wrong_doi.py

├── test_metadata_mismatch.py

├── test_retry_logic.py

├── test_failure_case.py


└── examples/

```

---

# Self Check机制

Skill运行结束必须执行：

## Check 1

DOI来源检查

问题：

这个DOI来自哪里？

必须：

database_source

---

## Check 2

Metadata一致性检查

检查：

title

authors

journal

year

---

## Check 3

幻觉检测

如果：

没有数据库返回结果

不能accepted。

---

## Check 4

Retry检查

确认：

失败是否最多3次。

不能无限循环。

---

## Check 5

状态检查

accepted:

必须全部验证。

failed:

必须有failure_reason。

---

# Logging要求

每次运行记录：

```json
{
"skill_name":
"skill03_citation_validation",

"timestamp":"",

"input_paper_id":"",

"original_doi":"",

"validation_attempts":3,

"sources_checked":[
"Crossref",
"PubMed"
],

"final_status":"",

"errors":[],

"human_review_required":false
}
```

保存：

logs/

---

# Error Handling

定义：

## DOI001

DOI格式错误

处理：

retry

---

## DOI002

DOI不存在

处理：

重新搜索

---

## DOI003

Metadata mismatch

处理：

retry

---

## DOI004

数据库不可访问

处理：

fallback其他source

---

## DOI005

3次验证失败

处理：

reject

---

# 测试要求

必须实现：

---

# Test 1

正确DOI

输入：

真实论文DOI

期待：

accepted

---

# Test 2

不存在DOI

输入：

随机DOI

期待：

retry

最终：

failed

---

# Test 3

错误DOI对应另一篇论文

例如：

title A

DOI B

期待：

mismatch

---

# Test 4

标题轻微不同

期待：

accepted

---

# Test 5

数据库不可访问

期待：

fallback

---

# Test 6

LLM幻觉测试

模拟：

LLM提供不存在DOI

期待：

不能accepted

---

# 与后续Skill接口

输出必须支持：

Skill04 PDF Acquisition

Skill04只接受：

final_status:

accepted

的论文。

---

# 最终验收标准

完成后必须满足：

1. 所有论文真实性经过数据库验证。

2. DOI与论文身份一致。

3. LLM不能创造论文信息。

4. 最多3次retry。

5. 失败论文不能进入下一阶段。

6. 所有失败原因可追溯。

7. 输出符合统一Schema。

8. 有完整日志。

9. 有测试案例。

---

# 注意事项

不要修改framework核心Schema。

如果发现：

CitationValidation Object不足：

创建：

schema_change_proposal.md

等待确认。

---

开始实现 Skill03。

```

---

这个 Skill 比 Skill02 更应该被当作 **Gate**，原因是后续：

- PDF 下载；
- MinerU解析；
- 实验设计抽取；

全部建立在“这篇论文是真的”这个前提上。

如果这里不严，后面所有实验设计提取都会被污染。这个设计也符合你上传的 agent-harness 审计里强调的原则：**来源验证失败必须留下审计记录，而不是让错误信息继续流转。** :contentReference[oaicite:0]{index=0}
```

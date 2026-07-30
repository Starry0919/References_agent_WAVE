下面是 **Skill04【论文PDF获取】** 的 Codex 工程开发 Prompt。

这个 Skill 和前面三个不同，它开始进入**文件资产管理层（Paper Artifact Management）**。

核心不是简单写一个下载脚本，而是建立：

> DOI验证通过的论文 → 可追溯 PDF Artifact → 后续 MinerU 解析输入

必须保证：

* PDF来源明确；
* 文件没有损坏；
* 版本可追踪；
* checksum 可验证；
* 人工上传 PDF 和自动下载 PDF 最终进入同一个流程；
* 不允许“有一个pdf文件就认为是正确论文”。

---

建议保存：

```text
skill04_pdf_acquisition_implementation_prompt.md
```

然后交给 Codex。

---

````markdown
# Skill04 Implementation Prompt

# 项目名称

论文实验设计抽取
(Literature Experimental Design Extraction)


---

# 当前任务

实现：

## Skill04：论文PDF获取 Skill

Paper PDF Acquisition & Artifact Management


目标：

根据 Skill03 已验证通过的论文 DOI，
自动获取对应 PDF 文件，
并建立完整的论文文件资产管理体系。


同时支持：

用户人工上传 PDF

两种入口最终进入统一 Paper Artifact 流程。


---

# 项目背景


本模块完整Pipeline：


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
论文PDF获取 ← 当前任务

↓

Skill05
PDF结构化解析

↓

Skill06
Markdown清洗

↓

Skill07
实验设计抽取


---

# Skill04定位


Skill04不是简单下载工具。

它负责：

## Paper Artifact Layer


管理：

论文身份

↓

文件实体

↓

版本

↓

来源

↓

完整性


确保后续所有解析均基于：

可信PDF Artifact。


---

# 当前Skill负责


✅ DOI论文PDF获取

✅ PDF来源记录

✅ 文件保存

✅ 文件完整性检查

✅ checksum生成

✅ PDF版本管理

✅ 用户上传PDF接入

✅ 输出标准Paper Artifact Object


---

# 当前Skill不负责


❌ DOI真实性验证

（Skill03负责）


❌ PDF内容解析

（Skill05负责）


❌ Markdown生成


❌ 实验设计抽取



---

# 核心原则


# 1. 只接受验证通过论文


输入必须来自：

Skill03


只有：

citation_validation_status:

accepted


才能自动下载。


---

如果：

failed

或：

rejected


禁止进入下载流程。


---

# 2. 文件来源必须可追踪


任何PDF必须记录：

来源：

- DOI自动下载
- 用户上传
- 数据库下载


不能出现：

unknown source


---

# 3. PDF文件不能只看存在


必须验证：


- 文件大小
- MIME类型
- PDF header
- checksum


防止：

HTML错误页面伪装成PDF。


---

# 4. 不修改原始文件


原始PDF：

immutable


任何转换：

生成新artifact。


---

# 输入 Input


来自：

Skill03 Citation Validation


对象：

Citation Validation Object


示例：


```json
{
"title":
"Engineering Escherichia coli",

"doi":
"10.xxxx",

"final_status":
"accepted",

"journal":
"Nature Biotechnology",

"year":
2024
}
````

---

# 同时支持人工上传入口

用户上传：

```text
paper.pdf
```

需要生成：

Manual Upload Artifact

不需要重新验证DOI。

但是：

记录：

source_type:

manual_upload

---

# 输出 Output

生成：

## Paper Artifact Object

必须包含：

---

# 1. Paper Identity

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

# 2. File Information

```json
{
"file_name":"",

"path":"",

"size_bytes":"",

"mime_type":"application/pdf"
}
```

---

# 3. Source Information

```json
{
"source_type":
"doi_download",

"source_url":"",

"download_time":""
}
```

source_type允许：

* doi_download

* publisher_download

* repository_download

* manual_upload

---

# 4. Integrity Information

必须包含：

```json
{
"checksum_algorithm":
"sha256",

"checksum_value":""
}
```

---

# 5. Processing Status

状态：

```text
pending

downloading

downloaded

verified

failed
```

---

# 文件目录设计

建议：

```text
paper_artifacts/


├── papers/


│
├── {paper_id}/


│
├── original.pdf

├── metadata.json

├── checksum.txt

└── artifact.log
```

---

# 工程结构

创建：

```text
skills/

skill04_pdf_acquisition/


├── README.md


├── skill.py


├── downloader/


│
├── doi_downloader.py

├── publisher_downloader.py

├── repository_downloader.py



├── uploader/


│
├── manual_upload_handler.py



├── artifact/


│
├── artifact_manager.py

├── checksum.py

├── metadata.py



├── validator/


│
├── pdf_validator.py



├── schema.py


├── logger.py


├── error_codes.py


├── tests/


│
├── test_download_success.py

├── test_manual_upload.py

├── test_corrupted_pdf.py

├── test_html_instead_pdf.py

├── test_checksum.py


└── examples/

```

---

# 下载策略

自动下载优先级：

## Level 1

Publisher PDF

↓

## Level 2

开放数据库：

例如：

Europe PMC

PMC

↓

## Level 3

其他合法来源

如果失败：

不能生成假文件。

返回：

download_failed

---

# DOI下载流程

Step 1:

读取citation validation

↓

Step 2:

检查status

↓

Step 3:

生成下载任务

↓

Step 4:

尝试来源

↓

Step 5:

保存PDF

↓

Step 6:

验证PDF

↓

Step 7:

生成checksum

↓

Step 8:

创建Paper Artifact

---

# PDF完整性验证

必须检查：

## Check 1

文件存在

---

## Check 2

扩展名

.pdf

---

## Check 3

Magic Header

必须：

%PDF

---

## Check 4

文件大小

不能：

0 bytes

---

## Check 5

Checksum

生成：

SHA256

---

# Self Check机制

Skill运行结束必须执行：

## Check 1

身份一致性

PDF Artifact中的metadata

必须对应输入论文。

---

## Check 2

文件完整性

检查：

PDF是否损坏。

---

## Check 3

来源完整性

必须有：

source_type

---

## Check 4

Checksum存在

没有checksum：

失败。

---

## Check 5

后续兼容性

确认：

Skill05可以读取该Artifact。

---

# Logging要求

每次运行记录：

```json
{
"skill_name":
"skill04_pdf_acquisition",

"timestamp":"",

"paper_id":"",

"doi":"",

"source_type":"",

"download_attempts":0,

"file_path":"",

"checksum":"",

"status":"",

"errors":[]
}
```

保存：

logs/

---

# Error Handling

定义：

## PDF001

DOI未验证

处理：

reject

---

## PDF002

下载失败

处理：

retry

---

## PDF003

文件为空

处理：

delete and retry

---

## PDF004

不是PDF文件

例如：

HTML error page

处理：

reject

---

## PDF005

Checksum失败

处理：

重新下载

---

## PDF006

用户上传文件损坏

处理：

要求重新上传

---

# Retry策略

下载失败：

最多：

3次

每次记录：

attempt number

source

error

---

# 测试要求

必须实现：

---

## Test 1

正常DOI下载

期待：

生成Artifact

---

## Test 2

人工上传PDF

期待：

进入同一Artifact流程

---

## Test 3

错误下载地址返回HTML

期待：

检测失败

---

## Test 4

损坏PDF

期待：

reject

---

## Test 5

Checksum验证

修改文件后：

必须发现变化

---

## Test 6

未通过DOI验证论文

期待：

禁止下载

---

# 与后续Skill接口

输出必须支持：

Skill05 PDF Structure Parsing

Skill05只需要：

Paper Artifact Object

包括：

file_path

checksum

metadata

---

# 最终验收标准

Skill04完成后必须满足：

1. 支持自动下载。

2. 支持人工上传。

3. 两种入口统一Artifact。

4. PDF来源可追踪。

5. 文件完整性验证。

6. checksum记录。

7. 支持失败重试。

8. 不生成假文件。

9. 输出符合统一Schema。

10. 有完整日志和测试。

---

# 注意事项

不要修改framework核心Schema。

如果发现：

PaperArtifact Schema不足：

创建：

schema_change_proposal.md

不要直接修改。

---

开始实现 Skill04。

```

---

这个 Skill 的重点是把“论文 PDF”从一个普通文件升级成：

```

Paper Identity
+
Digital Artifact
+
Provenance
+
Integrity

```

这一步做好之后，后面的：

- MinerU解析；
- Markdown清洗；
- 实验设计抽取；

才有可靠输入。

否则后面即使LLM抽取能力再强，也可能是在错误PDF、版本错误PDF或者损坏PDF上工作。
```

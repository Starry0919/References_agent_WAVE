# WAVE 文献获取与发现管线审计

> 审计日期：2026-08-12  
> 审计范围：研究问题输入、检索、候选合并、DOI 核验、PDF 获取、存储、MinerU 解析、Markdown 清洗、实验设计抽取、证据绑定、知识表示与 DDR 入库。  
> 审计方式：静态代码追踪、配置与运行产物盘点、只读的需求解析诊断、三个参考 ZIP 的代码级检查。  
> 约束：本次仅审计与设计；未修改生产代码、数据库、Schema、运行配置或现有数据。

## Executive Summary

WAVE **已经具备可运行的小批量端到端主链**，并非从零开始：`Skill01` 到 `Skill13` 覆盖需求解析、文献检索、引文核验、PDF 获取、MinerU/PyMuPDF 解析、结构化清洗、实验设计抽取、证据绑定、质量评价、K-12 迁移、工程方案、人工复核和前端适配。生产服务通过工作流引擎调用这条链路，并把完成的抽取结果转换为 DDR 知识记录。

但它目前更接近“最多 8 篇的一次性抽取工作流”，还不是稳定、可审计、可扩展的文献发现基础设施。最重要的结论是：

1. **发现能力存在但召回面窄。** 自动检索通常只调用 PubMed、Crossref、Europe PMC；OpenAlex 和 Semantic Scholar 只参与 PDF 位置发现，Google Scholar、Web of Science、CNKI 适配器是不可用占位实现。没有统一接入 OpenAlex 搜索，也没有跨来源缓存和限流协调。
2. **目标问题的查询生成存在实证缺口。** 对“提高 E. coli K-12 色氨酸产量”做只读解析时，`Skill01` 能识别物种与 K-12，却不能把“色氨酸”映射为 `tryptophan`，也没有可靠识别产量提升目标；因此英文数据库检索词会漏掉关键目标概念。其原因可直接追到产品/表型词表与查询拼接规则，而不是搜索 API 本身。
3. **排序不足以可靠区分高相关代谢工程论文和临床/食品污染论文。** 确定性排序只使用标题、期刊和作者字符串，不使用摘要；硬编码的工程词与偏好期刊只能提供弱信号，也没有领域负向特征。
4. **引文核验严格但偏脆弱。** DOI/题名/作者/期刊/年份的多策略核验是亮点，但所有核心字段必须同时匹配，缺失元数据容易进入人工复核或被拒绝；候选与来源仍按串行路径执行，没有结果缓存。
5. **PDF 获取覆盖多种合法来源，但缺少“下载内容就是目标论文”的身份闸门。** 当前校验主要检查 PDF 文件头、EOF/MIME；没有对 PDF 内题名/DOI、页数、最小体积和可解析性做统一验证，也没有跨论文的全局 DOI/checksum 去重。网络响应整包读入内存，缺少统一重试、退避、大小上限和每来源速率策略。
6. **MinerU、清洗、抽取与证据链是最成熟的部分。** MinerU 有本地运行时和 PyMuPDF 回退；`Skill06` 输出结构化 clean JSON；`Skill07` 有模型、语义契约、Schema 和缓存；`Skill08/09` 继续绑定证据与评估质量。历史运行数据表明，模型抽取才是端到端耗时主体。
7. **入库触发存在架构缺陷。** DDR 保存发生在前端轮询 `GET /tasks/{task_id}` 看见完成状态时，而不是工作流完成事件中；无人继续轮询就可能不入库。自动保存也没有在转换函数入口明确要求人工复核通过。相同 DOI/归一化题名覆盖同一 JSON 记录，没有完整版本历史。
8. **推荐 Option C，但以渐进式边界重构落地。** 建议形成四个明确模块：Discovery、Acquisition、Paper Processing、Knowledge Extraction；实现上升级现有 `Skill01-04` 的契约与执行机制，保留较成熟的 `Skill05-13`，避免再造一个单体 `Skill00` 或推倒重写。

结论等级：**当前适合受控的小批量研究辅助，不适合作为无人值守的大规模、合规、可重复发现管线。**

## Current Architecture

### 1. 生产入口与编排

- `harness/paper_extraction/service.py:137-170` 把 `auto_search`、`upload`、`doi`、`textbook` 请求转换为统一工作流输入。
- `harness/paper_extraction/service.py:173-205` 会把同项目此前上传的论文作为后续自动检索的手工候选补入。
- `harness/paper_extraction/service.py:232-273` 创建运行，强制把论文数限制在 1–8，并注入 `Skill05/06/07` 的生产执行器与缓存。
- `harness/paper_extraction/vendor/paper_experimental_design_extraction/skills/registry.py:4-7` 注册 `Skill01-13`。
- `harness/paper_extraction/vendor/paper_experimental_design_extraction/workflow/engine.py:238-253` 决定不同输入模式的执行计划；自动检索默认走 `Skill01-09`，只有满足 K-12 和结果层级条件时才继续迁移/工程设计阶段。
- `harness/paper_extraction/vendor/paper_experimental_design_extraction/workflow/engine.py:142-167` 定义各阶段输入，`engine.py:211-237` 把阶段输出写入共享上下文并形成逐篇 fan-out。

### 2. 主链路

```mermaid
flowchart LR
    U["研究问题 / DOI / 上传 PDF"] --> S1["Skill01 需求解析"]
    S1 --> S2["Skill02 多源检索、去重、排序"]
    S2 --> S3["Skill03 引文与 DOI 核验"]
    S3 --> S4["Skill04 PDF 获取与制品登记"]
    U -. 上传分支 .-> S4
    S4 --> S5["Skill05 MinerU / PyMuPDF"]
    S5 --> S6["Skill06 Markdown 与结构清洗"]
    S6 --> S7["Skill07 实验设计抽取"]
    S7 --> S8["Skill08 证据绑定"]
    S8 --> S9["Skill09 质量评价"]
    S9 --> K["可选 Skill10-13"]
    K --> API["任务完成"]
    API -->|"GET 轮询副作用"| DDR["DDR JSON 知识库"]
```

详细的真实分支、输入输出和旁路见 `LITERATURE_PIPELINE_CURRENT_FLOW.md`。

### 3. 与主链并存的旁路

`harness/evidence_retrieval/crossref_adapter.py:108-117` 和 `:230-248` 提供另一套 Crossref 检索与 DOI 解析；它被知识/生成相关 API 使用，返回书目元数据而非全文。这条“知识页检索”旁路与 `Skill02/03` 的多源发现没有共享候选模型、缓存或来源状态，因此仓库内实际存在两套 Crossref 客户端和两套检索语义。

## Existing Capabilities

### 1. 需求理解与查询生成

- `harness/paper_extraction/vendor/skills/skill01_requirement_parser/skill.py:35-46` 有 E. coli、K-12、BW、MG 等别名/菌株规则。
- `harness/paper_extraction/vendor/skills/skill01_requirement_parser/skill.py:60-69` 有部分方法学中英映射。
- `harness/paper_extraction/vendor/skills/skill01_requirement_parser/skill.py:298-328` 生成概念组与最多若干组合查询。
- `harness/paper_extraction/vendor/skills/skill01_requirement_parser/skill.py:330-332` 默认指定 PubMed、Crossref、Europe PMC。
- `harness/paper_extraction/vendor/skills/skill02_literature_retrieval/query/query_expander.py:4-30` 可选 Kimi 扩展，并有确定性回退。

### 2. 多源检索、合并与排序

- `harness/paper_extraction/vendor/skills/skill02_literature_retrieval/skill.py:77-108` 对来源与查询发起实际检索，并保留来源失败状态。
- `harness/paper_extraction/vendor/skills/skill02_literature_retrieval/skill.py:167-205` 按 DOI、PMID、归一化题名做去重；题名近似阈值约为 0.94。
- `harness/paper_extraction/vendor/skills/skill02_literature_retrieval/skill.py:207-228` 可对排名前部候选用 Kimi 并发重排。
- PubMed、Crossref、Europe PMC 适配器都调用真实公开 API；候选保留来源与检索 provenance。

### 3. DOI 与引文核验

- `harness/paper_extraction/vendor/skills/skill03_citation_validation/validator/retry_searcher.py:5-16` 依次尝试 DOI、题名+作者、题名关键词+期刊。
- `harness/paper_extraction/vendor/skills/skill03_citation_validation/skill.py:87-165` 区分 accepted、rejected、needs_review，而不是简单真假二元值。
- `harness/paper_extraction/vendor/skills/skill03_citation_validation/validator/metadata_matcher.py:15-39` 同时比较题名、作者、期刊和年份，能拦截明显幻觉或元数据错配。

### 4. PDF 发现、下载与制品管理

- `harness/paper_extraction/vendor/skills/skill04_pdf_acquisition/skill.py:46-48` 顺序尝试 OpenAlex、Europe PMC、Unpaywall、Semantic Scholar、出版商、机构仓储和 DOI 内容协商。
- `harness/paper_extraction/vendor/skills/skill04_pdf_acquisition/validator/pdf_validator.py:6-18` 检查 PDF 头、尾和 MIME。
- `harness/paper_extraction/vendor/skills/skill04_pdf_acquisition/artifact/artifact_manager.py:20-56` 记录 checksum、版本和来源，并在同一 `paper_id` 下避免重复制品写入。
- 支持上传文件直接进入解析分支，也会保存失败/推迟状态，不把所有失败都伪装成成功。

### 5. 解析、清洗、抽取与证据化

- `harness/paper_extraction/vendor/skills/skill05_pdf_parser/skill.py:67-75` 以 MinerU 为主、MinerU pipeline 模式重试、PyMuPDF 为回退；`:104-160` 输出质量与部分成功警告。
- `harness/paper_extraction/vendor/skills/skill05_pdf_parser/parsers/mineru_parser.py` 调用本地 MinerU 可执行文件；本机审计时 `D:\MinerU` 与对应可执行文件均存在。
- `harness/paper_extraction/vendor/skills/skill06_markdown_cleaner/skill.py:28-77` 做确定性结构清洗并校验结果；`:103-118` 输出 Markdown、clean JSON、章节/段落/图/表/引文映射。
- `harness/paper_extraction/pipeline_cache.py` 及 `service.py:208-229` 为 PDF 解析和清洗建立内容键缓存。
- `harness/paper_extraction/opus_extractor.py:22-54` 配置模型、内容缓存和并发；`:123-135` 消费 clean JSON，并通过 Schema 与语义契约校验抽取输出。
- 工作流继续调用 `Skill08` 证据绑定和 `Skill09` 质量评价，形成可追溯的实验设计结果。

### 6. 知识表示与去重

- `harness/paper_extraction/ddr_converter.py:307-441` 把抽取结果转换为包含元数据、decision chain、reasoning、graph、logic 和 rule provenance 的 DDR 2.0 JSON。
- `ddr_converter.py:394-407`、`:1601-1625` 按 DOI、其次归一化题名查重。
- `ddr_converter.py:1709-1725` 原子式写入本地知识目录，并可选触发 Git 同步。
- `ddr_converter.py:1826-1887` 提供任务级自动保存入口。

## Missing Capabilities

### 1. 发现与召回

| 能力 | 当前状态 | 缺口 |
|---|---|---|
| PubMed | 已实现并默认调用 | 无 API key/统一速率预算；只返回有限元数据 |
| Crossref | 已实现，且仓库有两套客户端 | 重复实现、语义不一致；自动检索适配器不使用摘要 |
| Europe PMC | 已实现并默认调用 | 与 PubMed 结果高度重叠，缺少来源配额策略 |
| OpenAlex 搜索 | 未接入 `Skill02` | 只在 `Skill04` 做 OA PDF 位置发现 |
| Semantic Scholar 搜索 | 未接入 | 只在下载阶段查询 OA PDF |
| Google Scholar | 占位适配器 | 明确报“需批准 provider”，实际不可用 |
| Web of Science | 占位适配器 | 未配置 |
| CNKI | 占位适配器 | 不可用 |
| 本地 DDR | 可查询 | 没有作为自动发现候选与外部检索统一合并 |

此外，没有前向/后向引文扩展、相似论文扩展、补充材料发现、预印本—正式发表版本归并和查询覆盖度停止条件。

### 2. 目标语义与查询编译

`harness/paper_extraction/vendor/skills/skill01_requirement_parser/skill.py:249-267` 对英文生化目标与中文词的处理不对称。只读诊断“提高 E. coli K-12 色氨酸产量”得到的关键词仍是中文片段，查询没有稳定包含 `tryptophan`，产量提升目标也未形成可靠 phenotype/objective。缺少：

- 产物本体与同义词：色氨酸、L-色氨酸、L-tryptophan、tryptophan、Trp；
- 菌株层次：E. coli、E. coli K-12、MG1655、W3110、BW25113 及衍生工业菌株；
- 目标层次：titer、yield、productivity、production、biosynthesis、overproduction；
- 工程机制层次：metabolic engineering、pathway engineering、feedback resistance、transport engineering、cofactor engineering、adaptive laboratory evolution；
- 来源特定查询编译，而不是把同一 Boolean 字符串直接交给不同 API。

### 3. 相关性判断

`harness/paper_extraction/vendor/skills/skill02_literature_retrieval/ranking/relevance_ranker.py:19-44` 的确定性得分只看题名、期刊、作者字符串和少量工程词；没有摘要、MeSH、关键词、引用关系或全文特征。年份得分围绕 2020–2026 硬编码，服务请求也在 `service.py:143-150` 固定同一窗口。缺少：

- 对“E. coli K-12 + L-tryptophan + 生产/代谢工程”的强制核心概念覆盖；
- 对临床感染、食品污染、宿主免疫、诊断等负向领域信号；
- 召回与精排分层、可解释特征、分数校准和人工标注评测集；
- 对无摘要候选的不确定性表达，而不是用期刊偏好代替相关性。

### 4. 获取正确性、鲁棒性与合规

- `harness/paper_extraction/vendor/skills/skill04_pdf_acquisition/downloader/base.py` 一次性读完整响应，缺少流式下载、最大体积、统一重试/退避、每域限速和熔断。
- `pdf_validator.py:6-18` 只确认“像 PDF”，不能确认“是这篇 PDF”；缺少 PDF 文本中的 DOI/题名身份匹配、页数与可解析性门槛。
- `artifact_manager.py:20-56` 的去重范围是同一 `paper_id`，没有全局 DOI/checksum 索引，可能先重复下载再发现相同内容。
- Unpaywall 依赖邮箱但当前环境未配置；出版商/仓储下载器也没有从服务层获得可用 URL 配置。
- 没有许可类型、OA 状态、访问方式、条款依据和下载时间的统一合规账本。

### 5. 执行、状态与可观测性

- `service.py:240-243` 硬限制每次最多 8 篇。
- 检索、核验和 PDF 来源尝试以串行为主，缓存只覆盖 `Skill05/06/07`。
- 没有阶段级持久队列、每来源全局并发控制、跨任务 GPU/模型背压和单篇可独立重试的 durable job。
- 既有 `PAPER_EXTRACTION_SCALABILITY_AUDIT.md:106-136` 指出发现/核验/下载无等价缓存；`:265` 指出没有持久阶段队列和全局 GPU 背压。该文档是历史审计证据，不替代本次代码事实。
- 同一审计的历史成功样本显示 `Skill07` 约占端到端 wall time 的 94%，MinerU cache miss 中位约 71.9 秒，而成功的非缓存 `Skill07` 中位约 12.14 分钟；样本是历史运行观测，不应被当成正式基准。

### 6. 入库与治理

- `harness/api/paper_extraction.py:204-211` 在查询任务状态时调用 `ensure_task_saved_as_evidence`，入库依赖 GET 轮询副作用。
- `ddr_converter.py:1826-1887` 自动保存完成任务中的结果，但入口没有明确把人工审批状态作为硬前置条件。
- 同 DOI/题名命中后更新同一记录，缺少不可变版本历史、来源快照和重处理 lineage。
- DDR JSON、本地文件索引与可选 Git 同步适合小规模，但全库扫描查重和每次保存触发同步不适合高吞吐。

## Reference Skills Evaluation

### `literature-search.zip`

**可复用价值**

- `scripts/search_openalex.py:21-48` 是无 key 的 OpenAlex 标准库客户端，包含 429 退避与三次重试。
- `scripts/search_openalex.py:125-186` 支持年份、引用数、类型、分页和排序；这正是当前 `Skill02` 缺失的 OpenAlex 搜索来源。
- `scripts/search_crossref.py:185-201` 有简单重试；输出字段包含 DOI、摘要、引用数和 BibTeX 等候选信息。
- `SKILL.md:81-82` 明确建议 DOI 后题名去重，与 WAVE 的候选归并方向一致。

**不能直接复用的原因**

- 两个脚本是 CLI/JSON 工具，不实现 WAVE 的适配器协议、结构化来源状态、任务日志、缓存或工作流检查点。
- OpenAlex 默认按引用数排序（`search_openalex.py:131`），参考说明自己也承认这会召回高引但不相关的综述；生产应显式用相关性或两阶段排序。
- User-Agent 邮箱是占位值（`search_openalex.py:27`、`search_crossref.py:26`）。
- `search_crossref.py:225-230` 去重的是 BibTeX key 冲突，不是跨来源论文实体去重。
- Skill 文档把最终相关性与资格判断交给人工，不能直接满足 WAVE 自动候选排序需求。

**结论：**复用 API 调用、分页、退避和字段映射思路；重写为 `Skill02` 的 OpenAlex adapter，并接入统一候选契约、缓存、速率策略和评测。

### `论文下载.zip`

**可复用价值**

- `batch_download_papers.py:145-264` 汇总 OpenAlex、Crossref、PMC/Europe PMC、Unpaywall、Semantic Scholar 的合法 OA 地址发现。
- `batch_download_papers.py:408-450` 记录逐层尝试与最终来源；`:600-610` 输出失败报告。
- `fast_download_papers.py:87-183` 将 PMC 作为快速合法 OA 通道，并用 semaphore 控制异步并发。
- “已存在跳过、失败清单、手工补齐”是值得移植的操作模式。

**禁止或不建议复用的部分**

- `SKILL.md:155-195` 指示使用 Sci-Hub 镜像；这带来版权、许可、安全和可持续性风险，**不得进入 WAVE 生产设计**。
- `SKILL.md:151`、`batch_download_papers.py:367-374` 使用 cloudscraper 绕过站点保护；`:266-349` 大量猜测出版商 URL。这些做法脆弱，可能违反服务条款，也可能下载到错误内容。
- `fast_download_papers.py:122-181` 默认 50 并发且 `ssl=False`；没有按域限速、重试预算或服务条款控制。
- `batch_download_papers.py:238` 的 Unpaywall 邮箱是 `test@example.com`。
- `batch_download_papers.py:104-112`、`:351-376` 只靠 MIME/文件头判断，整包响应写内存；没有目标论文身份校验。
- 文档要求先用 Crossref 核对题名，但实际下载函数 `download_one` 没有执行题名匹配；文档承诺和代码不一致。

**结论：**仅移植合法 OA 来源发现、尝试日志、失败分类与人工回退思想；不得直接引入 Sci-Hub、反爬绕过、TLS 关闭、出版商 URL 猜测或固定 50 并发。

### `论文清洗2.0.zip`

**可复用价值**

- `SKILL.md:12-20` 强调原始文件不可变、不得改写学术内容、保留表格/公式，适合作为 QA 原则。
- `SKILL.md:206-216` 的变更计数和不确定项报告可转化为清洗 provenance/质量报告。

**不能作为生产清洗器的原因**

- `SKILL.md:46-64` 要求人完整通读，`:82-107`、`:111-188` 要求逐处 Read/Edit 和手工重排，无法批量、重放或稳定测试。
- `SKILL.md:68-88` 删除图片链接，`:92-107` 把图注移出原上下文；这会破坏 WAVE 的图像引用、位置锚点和证据映射。
- 它只产出一个人工修改的 Markdown，没有 `Skill06` 已有的 clean JSON、段落/图/表/引文映射、验证报告和缓存键。
- 手工修复断词与合并句子包含较高语义变更风险，也难以形成确定性 provenance。

**结论：**不替换 `Skill06`；只把“原文不可变、学术内容不改写、清洗变更报告”吸收进未来 QA 规范。

## Gap Analysis

| 维度 | 当前成熟度 | 主要证据 | 目标差距 |
|---|---|---|---|
| 需求解析 | 中 | 有物种/菌株规则和查询生成 | 产品本体、中英同义词、目标与机制概念缺失 |
| 文献发现 | 中低 | 3 个真实默认来源 | OpenAlex/S2 未搜索；旁路不统一；无引文扩展 |
| 去重与排序 | 中低 | DOI/PMID/题名去重，可选 Kimi | 无统一论文实体；摘要未进入确定性排序；无校准评测 |
| DOI 核验 | 中 | 多策略、多数据库、三态结果 | 串行、无缓存、缺失元数据时过严 |
| PDF 获取 | 中 | 多种 OA locator、制品 checksum | 无身份校验、流式/限速/重试/全局去重与许可账本 |
| PDF 解析 | 中高 | MinerU 双模式 + PyMuPDF 回退 | 回退结构质量不等价；GPU 全局背压不足 |
| Markdown 清洗 | 高 | 确定性 clean JSON 与映射 | 需更强变更 provenance 和图表完整性测试 |
| 设计抽取/证据 | 中高 | Schema、语义契约、缓存、Skill08/09 | 长上下文成本高；需分段/分层抽取评测 |
| 知识入库 | 中低 | DDR 2.0、DOI/题名去重 | GET 副作用、审批门、版本历史、索引与事务性不足 |
| 可扩展性 | 低 | checkpoint、局部并发 | 8 篇上限、无 durable stage queue/全局背压 |

### E. coli K-12 / L-tryptophan 专项判断

当前管线能找到“标题同时显式包含 E. coli、K-12、tryptophan、production/metabolic engineering”的论文，但对中文研究问题和隐式机制召回不稳。它也没有足够特征自动把下列类别稳定分开：

- **高相关：**K-12 或近缘底盘中的 L-tryptophan 生物合成、反馈抗性、转运、前体/辅因子优化、ALE、产量/得率/生产强度数据；
- **中相关：**其他 E. coli 菌株或其他芳香族氨基酸工程，可作为迁移证据；
- **低相关：**临床分离株、食品污染、致病性、宿主 tryptophan 代谢、检测方法，仅因标题出现 E. coli/tryptophan 而命中。

必须先补齐查询本体、摘要元数据和显式正负相关特征，再谈扩大下载规模；否则只是更快地获取噪声。

## Recommended Architecture

推荐 **Option C：模块化重构**，但以兼容式升级现有技能落地：

1. **Literature Discovery Module**：承接并升级 `Skill01-03`。内部区分 Intent Model、Query Planner、Source Adapters、Candidate Entity Resolution、Recall Ranker、Precision Ranker、Citation Resolver。
2. **Acquisition Module**：升级 `Skill04`。内部区分 Access Resolver、Policy/License Gate、Downloader、Content Identity Validator、Artifact Registry。
3. **Paper Processing Module**：保留 `Skill05-06` 的外部契约，补充全局资源调度、图表完整性和分级回退质量。
4. **Knowledge Extraction Module**：保留 `Skill07-13`，把 DDR 保存改为完成事件驱动、幂等事务，并增加审批门和版本 lineage。

不建议 Option A 的原因：只修补现有检索与下载实现，无法解决候选实体、合规策略、身份验证、入库事件和跨任务调度的边界混乱。  
不建议纯 Option B 的原因：单独增加一个 `Skill00` 容易把需求理解、检索、排序、核验和下载继续堆成单体，并与现有 `Skill01-04` 重复。  
Option C 不要求立即改 DB 或推倒重写；先定义版本化契约和适配层，即可逐步迁移。

目标设计详见 `LITERATURE_DISCOVERY_DESIGN_RECOMMENDATION.md`。

## Implementation Priority

### P0：正确性与治理门槛

1. 建立产品/菌株/目标/机制的双语规范化本体，首先覆盖 L-tryptophan 专项。
2. 引入来源特定 Query Compiler；为每个查询保存规范化 intent、编译文本、来源、时间与版本。
3. 统一候选论文实体，加入摘要、关键词、MeSH、OA/版本状态和完整 provenance；合并两套 Crossref 客户端的公共契约。
4. 建立召回粗排 + 摘要精排，并明确临床/污染等负向信号；用人工标注专项集评估 Recall@K、Precision@K、nDCG。
5. 在保存 PDF 前后执行 DOI/题名身份校验、页数/体积/可解析性检查；失败不得进入“已获取”。
6. 把 DDR 保存从 GET 轮询副作用迁到任务完成事件；保证幂等，并显式定义人工审批/自动保存政策。
7. 禁止 Sci-Hub、反爬绕过和无授权抓取；记录许可、来源 URL、访问方式和政策决策。

### P1：覆盖度、鲁棒性与成本

1. 将 OpenAlex 作为正式搜索 adapter；评估后再接 Semantic Scholar 搜索。
2. 增加每来源缓存、速率限制、指数退避、熔断和结构化错误分类。
3. PDF 使用流式临时文件下载、大小限制、原子提交和全局 DOI/checksum 去重。
4. 增加引文扩展、相似论文、预印本—正式版归并和补充材料清单。
5. 为 MinerU/PyMuPDF 回退质量、图表/引文映射和抽取分段策略建立回归集。
6. 统一任务级 telemetry：候选漏斗、来源成功率、去重率、核验率、下载率、解析率、抽取成本、入库结果。

### P2：规模化

1. 引入按论文/阶段拆分的 durable queue、租约、幂等键和死信队列。
2. 为每域 HTTP、MinerU/GPU 和模型调用设置跨任务全局并发与背压。
3. 用对象存储保存不可变原始 PDF/解析制品，以数据库索引候选、制品、版本和 lineage。
4. 在受控基准与容量测试通过后，再提高 8 篇限制。

## Risks

| 风险 | 影响 | 当前触发点 | 缓解 |
|---|---|---|---|
| 查询语义遗漏 | 漏掉关键论文 | 中文“色氨酸”未映射 tryptophan | 双语本体、专项查询回归测试 |
| 噪声高相关 | 临床/污染论文占据前排 | 排序不看摘要且无负向特征 | 摘要精排、领域负向特征、标注集 |
| 错 PDF | 抽取错误论文并污染知识库 | 仅校验 PDF 格式 | DOI/题名内容身份闸门 |
| 合规/版权 | 法律、声誉和安全风险 | 参考下载 Skill 的 Sci-Hub/反爬建议 | OA/授权来源 allowlist 与政策账本 |
| 来源封禁 | 批量任务不稳定 | 缺少全局每域限速 | token bucket、退避、熔断、联系人配置 |
| 重复成本 | 重复下载、解析或模型抽取 | 只有后半段缓存，去重域局部 | 全局实体/制品/结果幂等键 |
| 入库丢失 | 任务完成但知识未保存 | GET 轮询副作用 | 完成事件/outbox + 幂等消费者 |
| 未审批知识污染 | 低质量记录自动可见 | auto-save 与审批门未强绑定 | 分层状态：draft/reviewed/published |
| 历史不可追溯 | 重跑覆盖旧知识 | 同 DOI/题名更新同一文件 | 不可变版本 + current pointer |
| 规模雪崩 | HTTP、GPU、模型资源耗尽 | 无 durable queue/全局背压 | 分阶段队列、租约、配额和预算 |

## Next Step Recommendation

下一步不是立即增加下载器，而是做一个**不改变现有 Schema 的 P0 设计验证冲刺**：

1. 建立 50–100 篇的 E. coli K-12 / L-tryptophan 金标准候选集，包含高、中、低相关和临床/食品污染负样本。
2. 固化 10–20 条中英文研究问题回归用例，验证 intent 与来源查询必须包含哪些核心概念。
3. 定义 `DiscoveryCandidate vNext`、`AcquisitionArtifact vNext` 和完成事件的版本化契约草案。
4. 用现有管线与改进后的离线原型做对照，只测 Recall@K、Precision@K、去重正确率、DOI 核验率、正确 PDF 率和单位有效论文成本。
5. 评测通过后，先接 OpenAlex 搜索与 PDF 身份闸门，再迁移入库触发；最后才考虑扩大批量。

这一路径最大限度保留 `Skill05-13` 的既有投资，同时先修复会直接污染召回、下载正确性和知识库可信度的根因。

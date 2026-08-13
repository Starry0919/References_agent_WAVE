# WAVE Literature Discovery & Acquisition Audit

审计日期：2026-08-12。范围涵盖真实代码、调用链、数据模型、三个参考 ZIP，以及本轮新增实现前后的差距。既有详细审计可参见 `LITERATURE_ACQUISITION_PIPELINE_AUDIT.md` 与 `LITERATURE_PIPELINE_CURRENT_FLOW.md`。

## Current architecture

| 环节 | 状态 | 代码证据 | 输入/输出、调用与持久化 | 主要限制 |
|---|---|---|---|---|
| 研究需求解析 | REAL/PARTIAL | `harness/paper_extraction/vendor/skills/skill01_requirement_parser/skill.py` | workflow 调用；输出 intent/query strategy | 中文色氨酸未稳定规范为 tryptophan；时间窗偏硬编码 |
| 自动检索 | REAL/PARTIAL | `.../skill02_literature_retrieval/skill.py` | PubMed/Crossref/Europe PMC → candidates | 来源/查询串行；摘要不进入确定性排序；无缓存 |
| DOI/引文核验 | REAL | `.../skill03_citation_validation/skill.py` | candidates → accepted/rejected/review | 严格但串行；无缓存 |
| PDF 获取 | REAL/PARTIAL | `.../skill04_pdf_acquisition/skill.py` | accepted/upload → paper artifacts | 格式校验弱于论文身份校验；无全局下载去重 |
| MinerU/PyMuPDF | REAL | `.../skill05_pdf_parser/skill.py` | PDF → document artifact | fallback 结构质量不等价 |
| Markdown 清洗 | REAL | `.../skill06_markdown_cleaner/skill.py` | document → clean Markdown/JSON/maps | 已较成熟 |
| 实验设计/证据 | REAL | `harness/paper_extraction/opus_extractor.py`、Skill08/09 | clean JSON → extraction/evidence/quality | 模型成本高 |
| DDR | REAL/PARTIAL | `harness/paper_extraction/ddr_converter.py` | completed task → DDR JSON | 保存由 GET task 轮询副作用触发 |
| 独立 Crossref 知识检索 | REAL | `harness/evidence_retrieval/crossref_adapter.py` | Knowledge/Generation API → metadata | 与 Skill02 候选池不统一 |

生产服务 `harness/paper_extraction/service.py:232-273` 将各输入模式汇入同一工作流，并把每批限制为最多 8 篇。工作流计划位于 `harness/paper_extraction/vendor/paper_experimental_design_extraction/workflow/engine.py:238-258`。DDR 保存副作用位于 `harness/api/paper_extraction.py:204-211`。

## Current model capacity

现有 Skill 输出分散承载 DOI、PMID、题名、作者、期刊、年份、来源、排序和制品信息，但没有一个稳定的跨来源 canonical candidate contract 同时表达：OpenAlex ID、query provenance、完整 source records、分项相关性、OA/获取状态与失败原因。因此本轮没有改数据库，而是在新模块中增加 Pydantic contract 与 JSON manifest，避免破坏既有 Schema。

## Agent integration decision

选择 **service + future workflow-node boundary**，而非新增单体 Skill00：

- discovery/acquisition 需要独立缓存、来源故障隔离、下载状态和批量预算，适合后端 service；
- 现有 runtime 已由 WorkflowEngine 编排，成熟入口是 Skill04 的 manual upload 分支；
- 本轮以 handoff manifest 和兼容 payload 接通，不修改脏工作树中的核心生产编排；
- 后续可把 service 包装为 workflow node/skill adapter，内部 contract 不变。

## Reference ZIP distillation

| Component | Existing WAVE | Reference | Reuse | Adapt | Reject | Reason |
|---|---|---|---|---|---|---|
| OpenAlex search | Skill02 缺失 | `literature-search.zip!scripts/search_openalex.py` | API/分页/429 思路 | 是 | CLI contract | 参考有重试；默认引用数排序及占位邮箱不适合生产 |
| Crossref search | 已有两套 | `search_crossref.py` | 重试/字段映射思路 | 少量 | 直接复制 | 需统一 WAVE provenance/cache；参考去重是 BibTeX key |
| arXiv source | 当前无 | `download_arxiv_source.py` | 暂无 | 可选后续 | 作为主来源 | 与生物工程正式论文核心场景不互补 |
| OA locator | Skill04 已有 | `论文下载.zip` 多来源 resolver | PMC/OA locator/失败报告思想 | 是 | — | 合法 OA 路径值得吸收 |
| 高并发下载 | 局部串行 | 50 并发 async/thread | bounded 设计思想 | 必须重做 | 固定 50、`ssl=False` | 无按域预算，易触发封禁 |
| PDF 校验 | header/EOF/MIME | `%PDF`/最小大小 | 最小体积思想 | 是 | 仅文件头 | 不能确认目标论文身份 |
| Sci-Hub/反爬 | 无 | ZIP 文档建议 Sci-Hub/cloudscraper | 否 | 否 | 是 | 版权、条款、安全与维护风险 |
| 清洗 | Skill06 结构化、确定性 | `论文清洗2.0.zip` 人工 Read/Edit | 原文不可变/报告原则 | QA 规范 | 生产清洗器 | 删除图片、移动图注会破坏证据锚点且不可批量重放 |

三个 ZIP 均可访问且已检查实际脚本/Skill 文档，没有假定其行为。未复制整个 Skill，也没有引入其凭据、硬编码路径、Sci-Hub、cloudscraper 或 Playwright 绕过。

## Gap analysis before implementation

1. 缺少统一 scientific request、query record、candidate 和 relevance contract。
2. 中文/生物概念扩展不足，菌株 lineage 与 exact host 未分开。
3. 缺少 OpenAlex discovery；现有 OpenAlex 仅作 PDF locator。
4. 排名主要由题名/期刊/作者和少量词决定，无法解释科学资格。
5. relevance 与 availability 容易概念混淆。
6. PDF 获取缺少独立状态机、流式上限、确定性文件名与 handoff manifest。
7. 没有 K-12/L-tryptophan 正反例和可重复 live benchmark。

## Architecture decision

采用既有设计报告中的 Option C，但本轮只实现可回滚的最小纵切：

```text
ScientificLiteratureRequest
→ bounded query families
→ OpenAlex + Crossref adapters
→ normalized source records
→ conservative identity resolution
→ explainable tier assessment
→ lawful OA acquisition
→ validated immutable PDF
→ handoff manifest
→ existing upload/Skill04→Skill13 path
```

拒绝：重写 Skill01-13、直接修改数据库、把 LLM 作为唯一筛选器、自动抓取 Google Scholar、Sci-Hub、反爬绕过，以及为了 UI 展示重做前端。

## Remaining audit findings

- 当前 tiering 是保守 metadata eligibility，不等于阅读全文后的最终科学判断。
- K-12、MG1655、W3110、BW25113 被明确分为 exact/derivative evidence，不宣称完全等价。
- `fulltext_availability` 是独立维度，不进入 scientific score。
- 生产完成事件入库、不可变 DDR 版本、全局队列与背压仍未在本轮修改。

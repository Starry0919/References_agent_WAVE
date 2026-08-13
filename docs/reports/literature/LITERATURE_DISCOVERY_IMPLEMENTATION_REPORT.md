# Literature Discovery Implementation Report

## Architecture and scope

实现了独立 `harness.literature_discovery` service layer。它不替换现有 Skill01-13，不修改数据库或前端；通过 manifest 生成现有 `build_request`/upload 分支可接受的 payload。

## Files added

- `harness/literature_discovery/__init__.py`
- `harness/literature_discovery/models.py`
- `harness/literature_discovery/query.py`
- `harness/literature_discovery/adapters.py`
- `harness/literature_discovery/identity.py`
- `harness/literature_discovery/relevance.py`
- `harness/literature_discovery/acquisition.py`
- `harness/literature_discovery/service.py`
- `scripts/run_literature_discovery_benchmark.py`
- `tests/literature_discovery/test_core.py`
- 四份 Markdown 报告与 `literature_discovery_benchmark_k12_tryptophan.json`

## Existing files modified

无。仓库已有大量用户未提交变更；本轮刻意避免修改核心生产文件和无关内容。

## Canonical contracts

`models.py` 新增：

- `ScientificLiteratureRequest`：物种、lineage、strain aliases、规范产品、别名、目标、domains 与预算；
- `SearchQueryRecord`：文本、family、rationale、source、timestamp；
- `PaperCandidate`：DOI/PMID/PMCID/OpenAlex ID、书目、摘要、OA hints、全部 source records、relevance、acquisition；
- `RelevanceAssessment`：六个科学维度、独立 availability、host relation、tier、score、reason codes、rationale；
- `AcquisitionRecord`：状态、URL、本地路径、SHA-256、大小与失败原因。

全部是 additive Pydantic contract，没有数据库迁移。

## Query generation

生成六个有界 family：exact objective、metabolic engineering、strain lineage、pathway intervention、fermentation/bioprocess、recall expansion。每来源均有稳定 query ID、理由和预算；Crossref 使用公共搜索子集，日期作为 adapter 参数，不无限组合。

## Adapters

- OpenAlex：真实 API、relevance 排序、日期过滤、OA location、倒排摘要恢复、原始 provenance；
- Crossref：真实 API、journal article filter、合法 select 字段、摘要清理、PDF link hints、原始 provenance；
- 共同传输层：timeout、有限重试、429/5xx 退避、`Retry-After` 感知、来源故障隔离。

首轮 benchmark 暴露 Crossref 不支持 `subtype` select 的 400；已移除并新增测试，最终两个来源均 60 hits、零错误。

## Identity resolution

按 DOI exact → PMID/PMCID/OpenAlex ID → normalized title exact → 0.965 保守 fuzzy title。合并时保留所有 `SourceRecord` 与 OA URL，不做激进 merge。

## Relevance

混合确定性评价拆分 organism、strain、product、engineering、production objective、experimental evidence；availability 不计入科学得分。输出 Tier 1–4/Exclude 与 reason codes。

benchmark spot check 促成两次收紧：

1. `improved/increased` 不再当作定量生产证据；
2. Tier 2 要求标题级目标产品并具标题工程/生产或实验信号；5-hydroxytryptophan、indole、succinate 等相邻目标标记 `OTHER_PRODUCT_TARGET`。

## Acquisition

- relevance 与 acquisition 分离；
- 只使用候选 OA URLs，缺失时按 DOI 查询 OpenAlex OA location；
- 流式写临时文件、50 MiB 上限、30 秒 timeout；
- 检查 content type、PDF signature、最小 1 KiB、HTML masquerading 和 `%%EOF`；
- 按 DOI/candidate 生成确定性文件名，已有合法文件直接复用；
- 原子 replace、SHA-256、结构化失败状态。

没有加入 Sci-Hub、cloudscraper、TLS 禁用、出版商 URL 猜测或无界并发。

## Integration

`handoff_manifest()` 同时输出：

- 丰富 paper identity/relevance/provenance/processing state；
- 每篇一个 `existing_pipeline_payload`，其中 `files` 是现有 `WorkflowEngine` 所需的路径字符串。

测试实际调用 `harness.paper_extraction.service.build_request` 验证 payload 契约。获取成功的 PDF 可走现有 upload → Skill04 artifact → MinerU → cleaner → Skill07-13，不重写后半链。

本轮没有自动提交长耗时抽取任务，避免 benchmark 结果未经人工确认直接写入 DDR；manifest 明确标为 `ready_for_existing_ingest`。

## Cache, idempotency and batch posture

- discovery result 使用 request + query + contract 的内容哈希 JSON cache；
- DOI/title 去重发生在下载前；
- PDF 以确定性文件名与 SHA-256 复用；
- query/result budget 有上界，来源失败不终止整体；
- 当前同步执行适合最小实现，未来可不改 contract 地放入阶段队列与 bounded concurrency。

## Backward compatibility

没有修改现有 API、Schema、DB 或 Skill output。新模块仅被 benchmark/tests 显式调用；生产迁移可先 shadow run，再增加 workflow wrapper。

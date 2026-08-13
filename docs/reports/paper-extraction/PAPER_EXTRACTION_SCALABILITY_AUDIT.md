# Paper Extraction Scalability Audit

审计日期：2026-08-12  
审计范围：当前工作树中的 `harness/paper_extraction`、其 vendored 13-skill workflow、API、前端轮询、DDR 转换与持久化。  
最高约束：**任何优化只有在 Extraction Quality(new) >= current baseline 时才可进入生产。**

## Executive Summary

1. 当前不是严格的“7 步”。一次已提交任务最多执行 **13 个编排技能阶段**；从提交到前端可持久展示，还存在 3 个未纳入 workflow timing 的后处理阶段（结果摘要/翻译、DDR 转换与持久化、可选 Git 同步）。因此本报告采用 **16 个实际执行阶段**；上传本身是条件性 pre-stage，不计入 16。
2. 最大瓶颈是 Skill07 全文科学推理抽取。历史可用的 15 个“成功、非缓存、单篇上传”样本中，它占已记录 wall time 的 **94.00%**；PDF 解析占 **5.92%**，其他已记录阶段合计不足 0.1%。
3. 当前架构不适合直接稳定处理 1000 篇。它可以做小批量异步运行，但缺少 durable queue、全局 MinerU 资源门、逐论文失败隔离、批次级状态表、可靠 token/retry/cache telemetry；每个 API 请求还被限制为最多 8 篇。
4. 最大的安全提速空间是：完善测量；消除重复下载；保留并强化内容寻址缓存；按阶段 checkpoint；失败只重试当前论文当前阶段；受控的 paper-level 并发；把翻译和 DDR 保存从 GET 轮询副作用中移出。这些都不改变科学抽取语义。
5. 最大质量风险是把长上下文简单裁成 Methods-only、直接换小模型、忽略 Supplement、或把分段 Map→Reduce 当成等价于全文跨章节推理。上述方案未经 Golden Benchmark 一律 **NOT SAFE FOR PRODUCTION**。
6. 第一轮推荐：先建立 10/30/50 篇受控基线和结构化 telemetry；随后做零质量风险的缓存、失败隔离、durable queue、全局资源门与幂等持久化。模型/Prompt/section routing 变更必须放到 Golden Benchmark 之后。

## Audit Basis and Confidence

### 代码事实

- API 入口：`harness/api/paper_extraction.py:96-215`。
- 请求构造、任务注册、恢复与 executor 注入：`harness/paper_extraction/service.py:49-273`。
- 13-stage 计划、逐阶段 checkpoint 与论文级并发：`harness/paper_extraction/vendor/paper_experimental_design_extraction/workflow/engine.py:13-279`。
- 任务级线程池：`.../api/task_manager.py:5-20`。
- Skill07 模型调用、缓存、重试、修复和 validator：`harness/paper_extraction/opus_extractor.py:21-49, 101-218, 295-386, 619-852`。
- Parse/Clean cache：`harness/paper_extraction/pipeline_cache.py:26-116`。
- DDR 转换和保存：`harness/paper_extraction/ddr_converter.py:289-427, 1566-1706, 1785-1867`。
- 前端 3 秒轮询：`frontend/src/pages/paperExtraction/PaperExtractionPage.tsx:43-60`。

### 历史运行痕迹（不是受控 benchmark）

- 34 个 checkpoint：19 COMPLETED，15 FAILED。
- 历史 Skill07 model 均为 `kimi-k3`；当前 `.env` 也配置 `PAPER_EXTRACTION_MODEL=kimi-k3`。
- 现存 17 个成功 extraction cache 提供 token 记录；34 个 checkpoint 提供 stage duration。
- 这些运行跨越过代码/Prompt/cache-key 版本，且主要为单篇 upload，不能作为生产 SLA，只能作为瓶颈证据和 benchmark 设计依据。

### 当前有效配置与源码默认值

| Setting | 当前 `.env` | 源码默认值 | 审计含义 |
|---|---:|---:|---|
| task workers | 4 | 2 | 最多 4 个 workflow 同时运行 |
| parallel items/stage | 8 | 4 | 单任务最多 8 篇并行进入 05-09 |
| concurrent model calls | 6 | 4 | 进程全局模型流上限 6 |
| Skill07 timeout | 3600 s | 900 s | 单次长尾可达 1 小时 |
| Skill07 attempts | 5 | 3 | 最坏网络重试可累计数小时 |
| retry delay | 30 s | 10 s | 线性等待，不是 exponential backoff |
| model | kimi-k3 | claude-sonnet-4.6 | `opus_extractor.py` 文件名不能证明实际使用 Opus |

## 1. Current End-to-End Architecture

```text
Frontend / API client
  -> POST upload (conditional, base64 JSON -> local PDF)
  -> POST task
  -> in-memory TaskManager ThreadPool (4 configured workers)
     -> Skill01 requirement parse
     -> Skill02 retrieval (auto_search only)
     -> Skill03 citation validation (auto_search / DOI)
     -> Skill04 PDF acquisition or upload verification
     -> [per-paper fan-out]
        Skill05 MinerU -> PyMuPDF fallback
        Skill06 deterministic cleaning
        Skill07 full-document LLM extraction + deterministic gates
        Skill08 deterministic evidence binding
        Skill09 deterministic quality evaluation
     -> [aggregate, conditional]
        Skill10 K-12 transfer
        Skill11 engineering proposal
     -> Skill12 QC/human-review governance
     -> Skill13 frontend adapter (engineering_plan only)
  -> checkpoint.json / report
  -> GET polling builds extraction summary
     -> optional cached title-translation LLM
     -> when COMPLETED: convert each paper to DDR and save
        -> optional background git add/commit/pull/push per saved DDR
  -> frontend rendering
```

所有 source routes 在 Skill04 后汇合。Upload 跳过 Skill02/03；DOI 跳过 Skill02；`extract` 结果跳过 Skill10/11/13，但仍执行 Skill12。

## 2. Nominal 7 Steps vs Actual Runtime Stages

| Nominal step | Actual stages |
|---|---|
| 输入 | API intake/upload + Skill01 |
| 定位/验证 | Skill02 + Skill03 |
| PDF 获取 | Skill04 |
| PDF 转换 | Skill05 |
| 清洗/预处理 | Skill06 |
| 实验设计抽取 | Skill07 |
| 验证/DDR/知识/前端 | Skill08-13 + summary/translation + DDR persistence + optional Git sync |

因此 nominal 第 7 步实际包含 9 个执行阶段，且其中两个阶段由 GET 轮询触发，不在 workflow timing 中。

## 3. Stage-by-Stage Audit

### S01 Requirement parsing

- Where: `vendor/skills/skill01_requirement_parser/skill.py:132-455`。
- Input/Output: 用户要求与 constraints -> research intent、检索策略、review reasons。
- Execution: 同步、确定性、CPU；历史 median 5.4 ms，p95 60.4 ms（n=34）。
- Parallelism: paper NO；stage pipeline PARTIAL；intra-paper NO。
- Cache: 可按 canonical request hash 缓存，但收益极小。
- LLM/Opus: L0 deterministic；不需要 LLM/Opus。
- Risk: LOW。保持 Python。

### S02 Literature retrieval（auto_search only）

- Where: `skill02_literature_retrieval/skill.py:28-298`；HTTP adapters 在 `adapters/base.py:20-22`。
- Input/Output: research intent/query -> candidates + source status + ranking annotations。
- Execution: 外部网络为主。sources 和 queries 的主循环串行；每个 HTTP timeout 20 s。可选 Kimi 做一次 query expansion，并对 top candidates 以 6 threads 做语义重排（`skill.py:178-223`）。
- Historical: 仅 2 个样本，163.6-205.6 s；样本不足。
- Parallelism: paper N/A；stage pipeline PARTIAL；intra-query YES，但当前只对 Kimi ranking 并行。
- Cache: query+filters+source+retrieval-code-version+date-window；metadata response 应有 TTL。当前无统一 cache。
- LLM: query expansion/relevance 为 L1，已有 deterministic fallback；不需要 Opus。
- Safe candidate: 并行独立 metadata sources、连接复用、response cache、限流器。不得以 cache 过期数据替代 DOI 最终验证。

### S03 Citation validation（auto_search / DOI）

- Where: `skill03_citation_validation/skill.py:25-262`；Crossref/PubMed/Europe PMC clients。
- Input/Output: candidates/DOIs -> accepted/rejected + audit trail。
- Execution: 网络 I/O；candidate、strategy、client 三层大体串行；每次 HTTP timeout 20 s。
- Historical: 2 个样本，21.0-25.2 s。
- Parallelism: paper YES；stage pipeline YES；intra-paper PARTIAL（多个 metadata source 可并发后合并）。
- Cache: DOI metadata、PMID mapping、validation result（含 source timestamp/version）。
- LLM/Opus: L0 deterministic matching；不需要。
- Quality: 并发和缓存 LOW；减少验证源 HIGH。

### S04 PDF acquisition / upload verification

- Where: `skill04_pdf_acquisition/skill.py:34-205`；downloaders `:46-49`。
- Input/Output: accepted candidates/manual files -> verified PDF artifact + SHA-256 + attempts。
- Execution: network/disk。论文循环串行（`:80-98`），每篇的最多 7 个 downloader 也串行（`:141-191`），单 fetch timeout 30 s。可选 Doubao 只负责下载源排序。
- Historical: upload-heavy median 117 ms，p95 85.8 s，max 257.4 s；不能代表批量下载。
- Duplicate evidence: 33 个 PDF 文件只有 20 个 unique SHA-256，已有 13 个内容重复文件。原因是 ArtifactManager 只在相同 `paper_id` 目录内去重。
- Parallelism: paper YES；stage pipeline YES；intra-paper PARTIAL（metadata resolution 可并行，实际二进制下载应 winner-takes-all 并及时取消）。
- Cache: DOI/PMID -> resolved URL；ETag/Last-Modified；PDF checksum；global checksum index。当前没有跨 paper_id 下载 cache。
- LLM: Doubao source ordering 属 L1 且非必要；deterministic fallback 已存在。禁用前要验证不会降低 PDF acquisition success/coverage。
- Quality: 并行和内容去重 LOW；减少合法来源 HIGH。

### S05 PDF parse / MinerU

- Where: `skill05_pdf_parser/skill.py:45-180`；`parsers/mineru_parser.py:10-56`。
- Input/Output: verified PDF -> markdown、sections、figures、tables、references、quality report。
- Execution: MinerU local subprocess，timeout 1800 s；计划可能尝试 requested mode、pipeline、PyMuPDF fallback。GPU/CPU/RAM/disk-bound。
- Historical cache miss median 71.9 s、p95 131.0 s（n=20）；cache hit median 11.6 ms（n=14）。
- Parallelism: paper YES；stage pipeline YES；intra-paper NO/UNKNOWN。当前 per-stage 8、task 4，理论可同时启动 32 个 MinerU subprocess，但没有 process-wide MinerU semaphore。
- Cache: 已按 `pdf_checksum + parse_policy + skill_version` 缓存，且检查引用路径仍存在。
- LLM/Opus: L0 parser，不需要。
- Critical resource risk: 本机 RTX 5070 Laptop GPU 8 GB；32 个 MinerU 并发极可能 OOM/争用。实际安全并发必须通过 10-paper resource benchmark 决定，初始建议全局 1-2，而不是沿用 item concurrency 8。

### S06 Markdown cleaning

- Where: `skill06_markdown_cleaner/skill.py:28-193` 及 cleaners/json_builder。
- Input/Output: DocumentArtifact -> clean JSON with paragraphs/anchors/figures/tables。
- Execution: 本地 deterministic CPU/disk。
- Historical cache miss median 121.2 ms、p95 144.8 ms（n=20）；hit median 28.9 ms。
- Parallelism: paper YES；stage pipeline YES；intra-paper不必要。
- Cache: 已按完整 document JSON + cleaner version 缓存。key 很大但语义正确；可改为 upstream content hash + version。
- LLM/Opus: L0，不需要。
- Quality: 继续保留 citation/structure checks；不要以激进清洗删内容。

### S07 Experimental design extraction

- Where: `harness/paper_extraction/opus_extractor.py:21-852`。vendored deterministic Skill07 被 executor override（`service.py:252-256`）。
- Input/Output: 一篇完整 clean document -> fields、experiment instances、extensions、DDR annotations、candidate evidence anchors。
- Execution: 将 system prompt + SKILL + full clean JSON + full JSON Schema 写入临时 prompt，调用 Poe Code CLI subprocess。每篇最多 5 次 transport attempt（当前配置），validation 失败再做 1 次 full-document repair。全局 semaphore=6。
- Historical successful non-cache Skill07: median 12.14 min，p95 40.11 min（n=15）；对应成功 end-to-end median 13.28 min、p95 40.12 min。cache hit median 46.2 ms（n=5）。
- Historical failures: 34 runs 中 13 个在 Skill07 transport/config 失败；这是版本混合的历史痕迹，不是稳定失败率，但足以否定“当前已具生产可靠性”。最长 Skill07 log 10.26 h。
- Parallelism: paper YES（stage item limit 8、model global 6）；stage pipeline 仅靠多个 task 间接实现；intra-paper PARTIAL/EXPERIMENTAL。
- Cache: 已包含 document content、model string、SKILL、system prompt、schema、runtime contract、validator version。缺点：model string 不是 provider immutable model revision；缓存成功结果不保留最初 cache-miss timing；失败不缓存是正确的。
- LLM class: L3 deep scientific reasoning。必须高能力模型；但 **没有代码证据表明必须 Opus**。当前实际为 Kimi-K3，源码默认 Sonnet 4.6。Opus/任一替代模型都必须在同一 Golden Benchmark 上比较。
- Quality: full-context 是当前 baseline。任何 section routing、压缩、Map→Reduce 或小模型 cascade 都是 benchmark-gated。

### S08 Evidence binding

- Where: `skill08_evidence_binding/skill.py:28-312`。
- Input/Output: Skill07 candidate fields + clean document -> independently quote-matched evidence map、conflicts、downgraded unknowns。
- Execution: deterministic CPU text matching；per-paper parallel。
- Historical median 264.7 ms，p95 391.5 ms（n=21）。2 个历史 task 因 quote insufficiency 失败。
- Cache: 可按 `skill07_output_hash + clean_document_hash + binder_version`；当前无 cache。
- LLM/Opus: L0 deterministic。不得移回 LLM。
- Quality: 这是核心 quality gate；不可为提速删除。

### S09 Quality evaluation

- Where: `skill09_quality_evaluation/skill.py:21-135`。
- Input/Output: extraction + evidence -> missing/conflict/coverage/quality report。
- Execution: deterministic CPU；median 72.1 ms，p95 112.5 ms（n=19）。
- Cache: output hashes + evaluator version。
- LLM/Opus: L0；不需要。
- Quality: 不可删；可扩展为生产 acceptance gate。

### S10 K-12 transfer（conditional aggregate）

- Where: `skill10_k12_transfer/skill.py:25-117`；engine `_inputs:160-167`。
- Input/Output: all papers' design/evidence/quality -> target-system comparison。
- Execution: deterministic aggregate；单请求、当前不并行。
- Cache: ordered set of upstream hashes + target-system + version。
- LLM/Opus: 当前不需要。
- Quality: 大批量时需避免把 zip 截断造成 paper/evidence/quality 错位。

### S11 Engineering proposal（conditional aggregate）

- Where: `skill11_engineering_proposal/skill.py:27-153`。
- Input/Output: K-12 design space + evidence -> candidate DBTL plans/governance flags。
- Execution: deterministic templates/logic；单请求。
- Cache: upstream hashes + target + version。
- LLM/Opus: 当前不需要。
- Quality: 维持 literature-reported 与 AI-level proposal 分层。

### S12 QC / human-review governance

- Where: `skill12_qc_human_review/skill.py:23-157`；fan-out construction `engine.py:168-204`。
- Input/Output: Skill07-11 artifacts -> per-artifact QC + review tasks + worst-status aggregate。
- Execution: deterministic，但 `_PARALLEL_SKILLS` 不包含 Skill12，因此约 `3N+2` 个 artifacts 串行。每个 item 完成都会重写完整 checkpoint。
- Historical single-paper median 159.8 ms，p95 223 ms。
- Parallelism: paper/artifact YES in principle；当前 NO。需要先解决共享 state/checkpoint 合并。
- Cache: artifact hash + checker version。
- LLM/Opus: L0；不需要。
- Scale risk: 大 N 时重复序列化完整状态形成近似 O(N²) I/O amplification。

### S13 Frontend adapter（engineering_plan only）

- Where: `skill13_frontend_adapter/skill.py:20-81`。
- Input/Output: plan/K12/evidence/quality/governance -> frontend cards。
- Execution: deterministic，单请求。
- Cache: upstream report hash + locale + adapter version。
- LLM/Opus: 不需要。

### S14 Result summary and title translation（未计时）

- Where: GET handler `harness/api/paper_extraction.py:163-215`；summary `result_summary.py:203+`；translation `harness/translation/service.py:114-169`。
- Execution: 每次 poll 读取并解析完整 checkpoint；title 可能触发 cached LLM translation，文档注明单次 15-30 s。
- Parallelism/cache: translation 已内容寻址；summary 没有 checkpoint mtime/result cache。
- LLM: translation 是 L1 UI concern，不需要 Opus，也不应阻塞 3 秒 status poll。
- Safe fix: status endpoint 只返回状态；summary/versioned view 单独读取；翻译异步或 completion 后 batch。

### S15 DDR conversion and persistence（未计时、由 GET 触发）

- Where: `paper_extraction.py:196-211`；`ddr_converter.py:1806-1867`。
- Execution: COMPLETED poll 同步调用；逐论文扫描整个 DDR directory 做 task-index、DOI/title dedupe、ID allocation、cross-paper rule similarity，然后直接写 JSON。
- Idempotency: 已用 `(task_id,paper_index)` 和 DOI/title 尽力去重，但没有跨请求锁/事务；ID allocation 先 scan 后 write，有并发重复 ID 风险；写入非 atomic。
- Complexity: 多处 directory scan；随 DDR 数增长可接近 O(N² × rules)。
- LLM/Opus: 不需要。
- Safe fix: 从 GET 移至 durable completion job；SQLite/Postgres unique keys；atomic upsert；索引 DOI/title/rule tokens。

### S16 Optional Git sync（未计时）

- Where: `knowledge_sync.py:35-86`。
- Execution: 每保存一个 DDR 启动 daemon thread，执行 git add/commit/pull/push，单 git call timeout 30 s。
- Scale risk: 千篇时可产生大量 threads/commits/concurrent Git operations；失败仅日志告警，进程退出可丢未完成同步。
- LLM/Opus: 不需要。
- Safe fix: 批次结束合并提交，或完全从 extraction transaction 解耦。

## 4. Current Concurrency Model

```text
TaskManager: up to 4 workflows
  each workflow: stages are sequential
    Skill05-09: up to 8 items in ThreadPoolExecutor
      Skill07: process-wide semaphore caps model calls at 6
      Skill05: no process-wide MinerU cap (theoretical 4 x 8 subprocesses)
```

结论：已经有 paper-level concurrency，但没有显式的 stage queue；所谓 pipeline parallelism 只来自不同 tasks 恰好处在不同阶段。模型有全局门，MinerU 没有。当前最危险的不是并发不足，而是 **不同资源共用一个 item concurrency、GPU parser 无全局背压**。

## 5. Cache & Recompute Audit

| Artifact | Current | Required key / policy | Finding |
|---|---|---|---|
| DOI metadata | no unified cache | DOI + source + API/schema version + fetched_at/TTL | repeated network work |
| resolved PDF URL | no | DOI + source + fetched_at/TTL | repeated resolution |
| downloaded PDF | per-paper-id local dedupe only | DOI/URL + ETag; global `pdf_sha256` index | 13/33 PDF files duplicate by hash |
| MinerU output | yes | pdf_sha256 + parse_policy + parser/skill version | good; add global resource telemetry |
| cleaned document | yes | parsed artifact hash + cleaner version | good; current key serializes full object |
| section split | embedded in clean artifact | cleaner/sectioner version | reusable |
| extraction | yes | clean content + model + prompt/skill/schema/validator versions | strong; add immutable provider model revision |
| evidence binding | no | extraction hash + clean hash + binder version | safe cache candidate |
| validation | no | upstream hashes + validator version | safe cache candidate |
| DDR conversion | idempotent scan, no cache | extraction/evidence/quality hashes + converter/schema version | use upsert/index |
| translation | yes | text + locale + model | good, but move off polling path |

如果只改 downstream prompt：PDF download、parse、clean 都不应重跑。若只改 Skill08/09/DDR：Skill07 也不应重跑。建议统一 provenance envelope：`paper_id, doi, pdf_sha256, parser_version, cleaner_version, prompt_version, skill_version, schema_version, validator_version, model_provider, model_id, model_revision`。

## 6. LLM / Opus Necessity Audit

| Call point | Class | Decision |
|---|---|---|
| Skill02 query expansion | L1 | smaller model or deterministic fallback; no Opus |
| Skill02 relevance rerank | L1 | smaller model; limit to ambiguous top set; no Opus |
| Skill04 downloader ordering | L1 | likely deterministic; verify acquisition recall before disabling |
| Skill07 design reconstruction | L3 | high-capability model required; Opus not proven |
| Skill07 schema repair | L2/L3 | only after deterministic validation; retain evidence context |
| UI title translation | L1 | small translation model or async service; no Opus |
| Schema/enums/required/normalization/evidence existence | L0 | Python/JSON Schema, as current validators mostly do |

`opus_extractor.py` 是历史命名。当前生产配置是 Kimi-K3，源码 fallback 是 Sonnet 4.6。正确问题不是“全流程是否必须 Opus”，而是 Skill07 的哪些质量维度需要哪一能力档。只有相同文档、相同 schema、盲审的 Golden Benchmark 能回答。

Model cascade 可做 prototype：fast model -> deterministic schema/evidence/quality gates -> uncertain/fail -> high-capability model。但 PASS gate 必须证明对遗漏关键实验逻辑、跨章节因果、Supplement 依赖和 hallucination 有足够召回；否则 **NOT SAFE FOR PRODUCTION**。

## 7. Prompt & Token Audit

### 静态上下文

| Component | chars | rough tokens (chars/4，仅估算) |
|---|---:|---:|
| Skill07 SKILL | 10,946 | 2,736 |
| system prompt | 4,644 | 1,161 |
| JSON Schema | 6,994 | 1,748 |
| static subtotal | 22,584 | 5,645 |

20 个 clean-document 样本平均 159,929 chars，范围 95,706-212,297 chars，粗略约 24k-53k tokens。现存成功 cache 的真实 token telemetry：input median 59,098、p95 73,980；可信 output（排除 3 个明显异常的 35/64/70 记录）median 17,163、p95 31,567。

结论：latency 主要来自 full-document long context 和长结构化输出，不是 system prompt 单独造成。SKILL 与 system prompt 在证据、unknown、article type、DDR gate 上存在语义重复，但直接删除可能降低一致性，必须 benchmark。

Repair prompt 再次携带完整 SKILL、schema、document 和 candidate output，可能接近第二次完整调用。优先尝试 deterministic safe normalization 和局部 JSON repair；任何减少科学上下文的 repair 方案需要质量测试。

Telemetry defect：token 存在 result `metrics`，但 workflow artifact/checkpoint 只保存 output+provenance，未保存 metrics；因此 cache 外的失败尝试、repair token 和 retry token 无法可靠汇总。另有 3 个成功 cache 的 output token 记录明显异常，应修正 CLI parser 并记录 raw usage schema/version。

## 8. PDF / MinerU Audit

- MinerU 3.4.4 从 `D:\MinerU`（默认）本地运行；当前 shell 未设置 `MINERU_ROOT`，因此依赖该硬编码默认目录。
- 解析计划可能重复调用同一个 pipeline mode（requested mode 默认 pipeline，随后又 pipeline），失败时会重复昂贵尝试。
- fallback PyMuPDF 保证可用性，但结构/图表质量可能下降，必须把 parser/mode 纳入 quality strata。
- 本机：24 cores、31.4 GB RAM（审计时 free 8.6 GB）、RTX 5070 Laptop 8 GB、D: free 184.6 GB。硬件快照不是生产配置。
- 20 个 unique clean docs 对应当前 parse/cache corpus；parsed artifacts 286.38 MB，约 14.3 MB/unique paper。

安全优化：全局 MinerU semaphore、GPU/RAM telemetry、模型 warm-up、避免重复 mode、checksum cache、parse failure local retry。不要把 fallback 结果静默当作与 MinerU 同质量。

## 9. Supplementary Information Audit

当前系统 **没有独立 Supplement acquisition pipeline**。Skill05 只能把主 PDF 内标题含 supplement 的 section 建索引；下载器不发现或下载 supplementary PDF/DOCX/XLSX/source data，clean document 也没有独立 supplements collection。Skill07 validator 只阻止“无 supplement 却声称检查过”的虚假覆盖。

这是当前质量缺口，不是可用于提速的裁剪。未来必须把 supplement 作为一等 artifact：发现 -> 合法下载 -> 类型专用解析 -> parent-paper linkage -> checksum/version -> evidence anchors。任何 benchmark 的分层都必须包含有 Supplement 的论文。

## 10. Failure / Retry / Resume / Idempotency Audit

### Paper 738 当前会发生什么

- 若在 Skill07 失败，同 stage 的其他论文仍会执行完；但 engine 随后把整个 workflow 标记 FAILED，并停止 Skill08+。因此其余成功论文也无法完成 evidence/quality/governance。
- upstream Skill05/06 cache 会保留；以同 task resume 可跳过成功 stages，但失败 stage 会整体重新构造输入并再跑，已成功的同-stage papers 只能依赖 extraction cache 避免模型重算。
- 没有 durable per-paper-stage row；只有一个大 checkpoint。无法自然表达“738 failed, 739 succeeded, retry only 738”。

### Retry

- Skill07 transport retry 当前最多 5 次、delay 30/60/90/120 s；这不是 exponential backoff+jitter。
- 每次最长 3600 s，加一次 schema repair，理论单篇可占用约 6 小时；历史出现 10.26 h stage。
- metadata/PDF adapters 主要依赖逐源 fallback，无统一 retry budget/rate-limit wait telemetry。

### Idempotency

- Skill05-07 content cache 基本幂等。
- S04 对相同内容但不同 paper_id 会重复保存。
- task registry 的 load-modify-save 无显式进程锁，多并发 submit 可能 lost update；多进程部署更不安全。
- DDR 的 scan-allocate-write 无事务或 unique constraint；并发 completion polls 可能冲突。
- GET 具有写副作用，不符合易推理的 HTTP/read idempotency。

## 11. Profiling Plan

新增 additive structured event，不改变业务 output：

```json
{
  "task_id": "...", "paper_id": "...", "doi": "...",
  "stage": "skill07_experiment_extraction", "attempt": 1,
  "queued_ms": 0, "service_ms": 0, "total_ms": 0,
  "pdf_size_mb": 0, "markdown_chars": 0,
  "input_tokens": 0, "output_tokens": 0,
  "model_provider": "", "model": "", "model_revision": "",
  "cache_hit": false, "retry_count": 0, "rate_limit_wait_ms": 0,
  "status": "", "failure_stage": "", "error_type": "",
  "cpu_peak_pct": 0, "ram_peak_mb": 0, "gpu_peak_mb": 0
}
```

必须同时记录 discovery、metadata validation、download、parse、clean、route、LLM、validation、evidence、quality、DDR、persistence、translation；记录 queue wait 与 service time，避免把限流等待误算为模型推理。append-only JSONL/SQLite 均可，不能继续把指标只埋在易丢的 result metrics 中。

## 12. Benchmark Plan

### Dataset strata

- 短/长论文；复杂 Methods；多实验实例；多图/表；扫描/OCR 困难；review/methods/protocol；有独立 Supplement PDF/DOCX/XLSX；跨 Methods/Results/Figure 才能重建逻辑；输出短/长。
- 固定 PDF bytes 与 checksum，人工记录 critical evidence units。

### A — 10 papers

- 目的：验证 instrumentation、单机安全 MinerU concurrency、cache cold/warm、provider rate limit。
- 运行：serial cold；current config cold；warm cache；故障注入（1 个 corrupt PDF、1 个 LLM timeout）。

### B — 30 papers

- 目的：估计 variability、retry、context/token relation、p90/p95、质量一致性。
- 运行：至少两次重复；concurrency 1/2/4/6；记录 provider RPM/TPM。

### C — 50 papers

- 目的：初步 batch soak；断进程后 resume；磁盘增长；queue fairness；DDR 并发 upsert。
- 运行：冷 cache、50% warm cache、混合 source route。

所有报告给 mean/median/p50/p90/p95/max、papers/hour、error rate、first-pass success、cache hit、token/paper、retry/paper。不得只给平均数。

## 13. Historical Bottleneck Ranking

成功、非缓存、单篇 upload 样本 n=15 的 logged-time breakdown：

| Stage | Share | Status |
|---|---:|---|
| Skill07 LLM extraction | 94.00% | measured historical |
| Skill05 PDF parsing | 5.92% | measured historical |
| all other logged stages | 0.08% | measured historical |

P0：LLM long context/long output、transport reliability、failure-local retry。  
P1：MinerU resource control、download duplication、durable per-paper state。  
P2：polling translation、DDR O(N²) scans、Git sync、small deterministic stages。

Amdahl：把 parse 加快 10x，理论总加速仅 `1/(0.94+0.0592/10+0.0008)=1.056x`；把 Skill07 加快 2x 则约 `1/(0.94/2+0.06)=1.887x`。exact-version extraction cache hit 从 12.14 min 降到约 46 ms，收益巨大且不损质量。

## 14. Optimization Matrix

| Stage | Current behavior | Bottleneck | Parallel? | Cache? | Must LLM? | Must Opus? | Estimated benefit | Quality risk |
|---|---|---|---|---|---|---|---|---|
| Retrieval | serial source/query I/O + optional Kimi | network | YES | missing | L1 optional | NO | up to source-count latency overlap | LOW |
| Citation | serial candidates/sources | network | YES | missing | NO | NO | workload-dependent 2-4x | LOW |
| PDF | serial papers + sources | network | YES | incomplete | L1 advisor optional | NO | workload-dependent; duplicate network eliminated | LOW |
| MinerU | per-paper parallel, no global GPU cap | GPU/RAM | bounded | yes | NO | NO | cache hit ~6,000x historical; safe parallelism TBD | LOW if identical output |
| Clean | fast local | none | yes | yes | NO | NO | negligible cold; warm reuse | LOW |
| Skill07 | full context, retry/repair | LLM/token/rate limit | yes, global 6 | yes | L3 | UNKNOWN | paper concurrency near linear until TPM/RPM; model changes TBD | HIGH for semantic changes |
| Evidence/quality | deterministic | small CPU | yes | missing | NO | NO | minor latency, major reliability | LOW |
| QC | serial 3N+2 and checkpoint rewrite | serialization | possible | missing | NO | NO | material only at large N | LOW |
| Summary/translation | synchronous GET side effect | hidden LLM | yes | translation yes | L1 | NO | remove 15-30 s cold poll stall | LOW |
| DDR | directory scans + non-atomic write | DB/I/O | unsafe today | partial | NO | NO | O(N²)->indexed O(N log N)/O(N) | LOW with parity tests |

## 15. Quality Risk Matrix and Veto

| Candidate | Risk | Production decision |
|---|---|---|
| content-addressed cache with full version key | LOW | accept after parity test |
| I/O concurrency / queue / checkpoint | LOW | accept after deterministic output comparison |
| failure-local retry | LOW | accept; improves completion without changing output |
| smaller model cascade | HIGH | benchmark only |
| high-recall section routing | HIGH | benchmark only |
| intra-paper Map→Reduce | HIGH | prototype only |
| Methods-only | UNACCEPTABLE | reject |
| lossy truncation | UNACCEPTABLE | reject |
| skip Supplement | UNACCEPTABLE | reject |
| remove evidence/DDR reasoning fields | UNACCEPTABLE | reject |

Veto: speed↑ quality↓ => REJECT；speed↑ quality same => candidate；speed↑ quality↑ => HIGH PRIORITY；speed↓ quality materially↑ => 单独评估。

## 16. Golden Benchmark Strategy

仓库现有 `harness/golden_set` 是 diagnosis/safety/model-domain cases，不是论文抽取 gold。桌面 `agent抽取结果` 中可见 13 个 extraction bundles，但抽样记录明确 `human_review_status: pending`；其中 10 个与“待人工审核”目录逐文件 hash 相同。因此当前 **没有可证明已人工批准的 extraction Golden Benchmark**。

建议冻结 30-50 篇：PDF+supplements checksum、article type、experiment inventory、关键字段、逐字段 evidence、DDR decision gates、conflicts、review corrections。至少指标：field completeness、evidence correctness/coverage、design action、trigger、reason nature、alternatives、implementation、result/rule correctness、hallucination、provenance、human acceptance。关键字段不得只用宏平均；设置 per-paper hard veto。

## 17. 500 / 1000 / 5000-paper Projection

### Assumptions

- 采用历史成功非缓存 end-to-end median **13.28 min/paper**；不含 independent Supplement acquisition、未计时 translation/DDR/Git、失败重试和 provider throttling。
- worker 理想情况下代表可持续的独立 paper slots；当前有效模型 cap 是 6，所以不改配置时 10/20/50 workers 都不会超过 current。
- 公式：`wall_hours = N * 13.28 / (60 * effective_workers)`；`effective_workers <= provider_RPM/TPM and safe_MinerU_capacity`。

| Papers | Serial | Current cap=6 | 10 ideal | 20 ideal | 50 ideal |
|---:|---:|---:|---:|---:|---:|
| 500 | 110.7 h | 18.4 h | 11.1 h | 5.5 h | 2.2 h |
| 1000 | 221.3 h | 36.9 h | 22.1 h | 11.1 h | 4.4 h |
| 5000 | 1106.7 h | 184.4 h | 110.7 h | 55.3 h | 22.1 h |

Stress view：若按历史成功 p95 40.12 min/paper，cap=6 时 500/1000/5000 分别约 55.7/111.4/557.2 h，仍未计失败重试。

Token formula（历史 Kimi cache）：median input 59,098、可信 median output 17,163。1000 篇约 59.1M input + 17.2M output tokens；5000 篇约 295.5M + 85.8M。实际需加 repair/retry。成本=`input_tokens*input_price + output_tokens*output_price + retry/repair usage`；本报告不猜价格。

磁盘粗估：当前 unique corpus 的 PDF+parsed+clean+checkpoint/cache 约 20 MB/paper 量级；5000 篇可达约 100 GB，保留多次 parse attempts、images 和重复 task checkpoints 时更高。必须定义 retention/compaction，而不是依赖 D: 当前 184.6 GB free。

## 18. Recommended Architecture

```text
Durable Paper/Stage Store (unique DOI, pdf_sha256, versioned artifacts)
        |
        v
Metadata Queue -> Download Workers -> Parse Queue -> MinerU Workers (global GPU cap)
                                           |
                                           v
Clean Workers -> Extract Queue -> LLM Workers (RPM/TPM semaphore)
                                  | PASS deterministic gates
                                  v
Evidence -> Quality -> QC -> DDR transactional upsert
                                  |
                                  v
                         Frontend read model / metrics

Each row: QUEUED/RUNNING/SUCCEEDED/FAILED/RETRYING, attempt, artifact hash.
Retry resumes at the failed paper-stage only.
```

Option A conservative: measurement、cache、dedupe、resource semaphore、failure-local retry、resume。首选。  
Option B pipeline architecture: durable queues + independent stage state。千篇规模前必须。  
Option C cascade: fast model -> validator/confidence -> high-capability fallback。仅 Golden Benchmark 通过后。

## 19. Safe Immediate Improvements

1. 持久化完整 metrics（tokens、attempts、cache hit、queue/rate-limit wait）。
2. 全局 MinerU semaphore 与 CPU/RAM/GPU telemetry；先测后定并发。
3. DOI/PDF global index 与 checksum dedupe；不改变 PDF bytes。
4. 将 per-paper-stage 状态独立持久化；失败只重试该 paper-stage。
5. 将 translation、DDR save、Git sync 从 GET poll 解耦。
6. DDR 用事务 upsert/unique DOI/title key；atomic write 作为过渡。
7. metadata/download async I/O + host/provider rate limiter。
8. 修正 usage parser 与历史异常 token telemetry。

## 20. Experimental Improvements Requiring Benchmark

- High-recall section routing：Methods、Results、figures/tables、Supplement 全覆盖，并保留 introduction/discussion 中设计动机候选；准入指标是 critical-evidence recall 不低于 full-context baseline。
- Map→Reduce：按 experiment/section 抽取，再用 full evidence index 做一致性 merge。必须测 cross-section causal loss、duplicate steps、scope fragmentation。
- Prompt 去重/compact schema：只在 schema validity、field completeness、evidence recall、DDR correctness 全部不降时接受。
- Model cascade / alternate high-capability model。
- Provider-native asynchronous batch。当前代码仅支持同步 Poe Code CLI；所查阅的 Poe 官方 Usage/Rate Limit 文档没有证实本调用路径存在离线 Batch endpoint，因此状态为 **requires current provider verification**。官方资料：[Usage API](https://creator.poe.com/docs/resources/usage-api)、[Rate Limits](https://creator.poe.com/api-reference/rate-limits)。

## 21. Explicitly Rejected Optimizations

- 只读 Methods。
- 丢弃 Results、Figure legends、Tables、Discussion design rationale。
- 不下载/不解析 Supplement 以节省时间。
- 固定字符/token 截断全文。
- 直接把 Kimi/高能力模型换成小模型。
- 删除 evidence、reason、alternatives、implementation、rule、provenance 字段。
- validator 失败后接受“看起来差不多”的 JSON。
- 为追求并发把 MinerU 无限制扩到 32 processes。

以上在质量等价被证明前均为 **NOT SAFE FOR PRODUCTION**。

## 22. Prioritized Roadmap

### P0 — Measurement now

- Change: structured profiling、usage/retry/cache telemetry、10-paper benchmark。
- Benefit: 建立真实 baseline；定位 provider vs context vs parse。
- Risk: LOW；additive only。
- Acceptance: output hashes/semantic outputs 不变；所有 fields 可汇总 p50/p90/p95。

### P1 — Zero-quality-risk speedup

- Change: download dedupe、all deterministic caches、failure-local retry、global MinerU/model/resource limits、move GET side effects。
- Benefit: exact rerun 可近即时；避免重复网络/parse；失败不拖垮 whole batch。
- Risk: LOW。
- Acceptance: same inputs/version produce identical extraction/evidence/DDR；crash/resume test passes。

### P2 — Before thousand-paper production

- Change: durable queue、per-paper-stage DB、transactional DDR、observability dashboard、retention、30/50-paper soak。
- Benefit: horizontal scaling、resume、operator visibility。
- Risk: LOW-MEDIUM engineering risk。
- Acceptance: 50-paper forced-crash soak；no duplicate/lost papers；p95 and error budget met；cache/provenance intact。

### P3 — Benchmark-gated optimization

- Change: routing、Map→Reduce、prompt compaction、model cascade、provider batch。
- Benefit: potentially 2-5x throughput/cost improvement; exact value unknown。
- Risk: HIGH scientific quality risk。
- Acceptance: Golden Benchmark quality >= baseline on every hard-gated dimension；human blind review non-inferior。

## Final Answer: Strict No-Quality-Regression Route to 1000 Papers

### Phase 0 — Measurement

冻结当前 Kimi/full-context/validator pipeline；补齐 telemetry；跑 10/30/50 篇 cold/warm benchmarks。没有可重复的质量与 p95 baseline，不改变模型或上下文。

### Phase 1 — Zero-quality-risk speedup

保留 Skill07 科学语义；做 DOI/PDF/checksum dedupe、parse/clean/extraction/versioned cache、全局资源门、失败局部重试、异步后处理。验收是逐字段/逐证据/DDR 输出与 baseline 等价，且 crash resume 不重跑成功 upstream。

### Phase 2 — Benchmark-gated optimization

建立人工审核 Golden Benchmark 后，分别实验 section routing、compact prompt、Map→Reduce、model cascade。任何 quality 维度下降即否决，不能用平均分掩盖关键论文失败。

### Phase 3 — Production-scale batch architecture

使用 durable stage queues 和 per-paper-stage state；LLM 以 provider RPM/TPM 控制，MinerU 以 GPU/RAM 控制；DDR 事务 upsert；dashboard 展示 queued/downloading/parsing/extracting/validating/completed/failed/retrying、papers/hour、p50/p95、error、cache hit、tokens/cost。1000 篇以可恢复吞吐为目标，而不是把单篇 latency 强行压到最低。

## Modified Files / Instrumentation / Tests

- 新增本审计报告与机器可读 audit JSON。
- 未修改生产代码、Prompt、SKILL、schema 或 extraction output。
- 未加入 instrumentation；只读取现有 checkpoints/cache、代码和本机资源快照。
- 因无生产代码改动，未运行全量 extraction/DDR tests；机器可读 JSON 将单独做 JSON parse/schema-shape sanity check。


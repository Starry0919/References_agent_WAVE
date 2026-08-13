# Skill07 Performance and Quality Audit

审计日期：2026-08-12  
审计对象：当前工作树中的 Skill07 Experimental Design Extraction runtime  
最高约束：**Extraction Quality(new) >= Extraction Quality(current baseline)**  
任务性质：只读架构与历史数据审计；未修改生产 Prompt、`SKILL.md`、Schema、模型或抽取逻辑。

## Executive Summary

### 1. 为什么 Skill07 慢？

Skill07 每篇论文通过 Poe Code CLI 向当前部署模型 `kimi-k3` 发出一次长上下文、长输出、L3 科学推理请求。请求同时包含 System Prompt、完整 Skill07、语义契约、JSON Schema、额外约束和完整 clean-document JSON；输出通常也是数万 token 的实验实例、证据锚点和 DDR 结构。模型调用失败时最多进行 5 次 transport attempt，确定性验证失败时还能再发送一次更大的全文 repair 请求。

当前代码只记录整个 Skill07 stage wall time 和最终 token usage，不能把 CLI 启动、进程内 semaphore 等待、provider queue、首 token 等待、模型推理和输出传输拆开。因此这些子项必须标为 `UNKNOWN`，不能凭经验分配比例。

### 2. 最大瓶颈是什么？

最大瓶颈是 CLI 内部的远端模型请求整体，而不是本地 JSON、Prompt builder 或 validator：

- 16 个成功、非缓存、单篇历史样本：median **754,570 ms（12.58 min）**，p95 **1,982,258 ms（33.04 min）**，max **2,406,585 ms（40.11 min）**。
- Skill07 占这些样本全部已记录 stage wall time 的 aggregate **93.75%**。
- 本地只读微基准：Prompt build median 36.50 ms；JSON serialize 0.72 ms；normalize 0.67 ms；validator 19.62 ms；临时 cache JSON write 1.50 ms。
- 5 个 cache-hit 单篇样本 median **46.22 ms**。

本地工作即使全部消失，对冷启动中位延迟也几乎没有影响。真正需要测量的是 semaphore wait、CLI/provider latency、time-to-first-token、generation duration、重试和 repair。

### 3. 哪些优化安全？

可以直接进入 P0 的是不会改变科学输入或模型语义的工作：

- 增加分段 telemetry，不记录论文正文或密钥；
- 保留内容寻址 cache，并补齐 provider 与 immutable model revision；
- 将 parse error、确定性可修复字段和科学语义失败分层；
- 对 JSON fence、包裹文本、缺少纯派生字段做本地修复；
- 把 transport retry、repair 原因和每次 attempt 的耗时持久化；
- 建立 10/30/50 篇 Golden Benchmark 与人工盲审流程。

### 4. 哪些优化风险高？

以下方案未经 Golden Benchmark 不得生产启用：

- Methods-only 或任何固定章节裁剪；
- 忽略 Figure legends、Tables、Discussion 或 Supplement；
- 直接替换 `kimi-k3`；
- 用模型自报 confidence 或“通过 Schema”作为 cascade 接受条件；
- 将实验抽取改成摘要任务；
- 按章节 Map-Reduce 后假定其与全文跨章节推理等价；
- 删除 rationale、alternatives、implementation、result、rule 或证据字段。

### 5. 最大理论加速空间在哪里？

- 对重复论文，成功 cache hit 已把约 12.58 min 降到约 46 ms；这是最大、已验证且无质量损失的加速，但不改善首次抽取。
- 对冷抽取，当前文档表示存在显著重复：20/20 个 clean document 的每个 `paragraphs[].text` 都逐字存在于对应 `sections[].content`。保留段落、section metadata、figures/tables 和未锚定残余内容，同时不重复发送 section content，理论上可将当前 Prompt 字符数中位数减少 **36.42%**。这只是候选表示法，必须经过 Golden Benchmark，不能直接上线。
- Repair prompt 中位数是 primary prompt 的 **128.06%**。若未来 repair 频繁，分级 repair 可避免第二次全文调用；但现有 17 个成功 cache record 的 `schema_repair_attempts` 全为 0，当前不能宣称实际节省比例。
- Section routing、Map-Reduce 和 model cascade 可能带来更大冷抽取加速，但质量风险最高，理论收益必须用公式和实测 pass rate 计算，不能预先承诺。

## Audit Basis and Confidence

### 代码事实

- API 提交：`harness/api/paper_extraction.py:132-134`。
- 请求编排和 Skill07 executor 注入：`harness/paper_extraction/service.py:232-268`。
- 逐阶段执行、论文级并发和 checkpoint：`workflow/engine.py:30-145`。
- Skill06→07 与 Skill07→08 handoff：`workflow/engine.py:157-158`。
- Prompt、CLI、cache、validation、repair：`harness/paper_extraction/opus_extractor.py:57-999`。
- Skill07 语义规则：`harness/paper_extraction/SKILL.md`。
- System Prompt：`harness/paper_extraction/prompts/experimental_design_system_prompt.md`。
- Schema：`harness/paper_extraction/schemas/skill07_output.schema.json`。

### 测量样本

- 34 个带 Skill07 log 的 checkpoint。
- 16 个成功、非缓存、单篇样本；5 个成功 cache-hit 单篇样本。
- 20 个现存 Skill06 clean-document cache artifact。
- 17 个成功 Skill07 extraction cache record。
- 所有历史 provenance model 均为 `kimi-k3`。
- 历史样本跨越过代码、Prompt 和 cache-key 版本，不是受控 benchmark，也不是 SLA。

### 模型配置事实

`opus_extractor.py` 的未配置默认值是 `claude-sonnet-4.6`，但项目 `.env` 明确设置 `PAPER_EXTRACTION_MODEL=kimi-k3`，`harness/config.py` 在启动时加载该文件。现有 provenance 也全部记录 `kimi-k3`。因此本审计的实际 baseline model 是 **Kimi-K3**，文件名 `opus_extractor.py` 不代表实际使用 Opus。

# 1. Current Skill07 Architecture

## 1.1 真实调用链

```text
User / Frontend
  -> POST paper-extraction task
  -> service.build_request
  -> TaskManager background workflow
  -> WorkflowEngine sequential stages
  -> Skill05 parsed DocumentArtifact
  -> Skill06 clean_document_artifact
  -> per-paper Skill07 executor override
       -> source JSON load + InputDocumentGate
       -> content-addressed cache lookup
       -> Prompt construction
       -> process-wide model semaphore
       -> Poe Code CLI subprocess
       -> kimi-k3 primary extraction
       -> result.json / marker JSON parse
       -> additive safe normalization
       -> Schema + semantic + evidence + graph + DDR validation
       -> optional full-document repair call
       -> cache write + provenance
  -> Skill08 receives Skill07 output + the same clean document
       -> independent deterministic evidence binding
  -> Skill09 quality evaluation
  -> optional K-12 / engineering / governance stages
  -> completed result may be converted to DDR outside Skill07
```

Skill07 本身不会调用 `ddr_converter.py`。它只产生 DDR annotation candidates；完成任务后的 API/持久化路径才做 DDR 转换。

## 1.2 输入的真实数据结构

Workflow 传给 Skill07 的请求只有：

```json
{"clean_document_artifact": "<Skill06 envelope>"}
```

`_source_document` 优先读取 envelope 的 `clean_json_path`。实际送入模型的是 JSON 对象，不是 PDF，也不是单独的 Markdown 字符串。20 个现存 clean JSON 全部包含：

- `document_metadata: object`
- `sections: array`
- `paragraphs: array`
- `figures: array`
- `tables: array`
- `citations: array`
- `cleaning_metadata: object`

具体覆盖：

- `sections` 和 `paragraphs`：20/20 非空；
- `figures`：20/20 有 metadata/caption，但 0/20 有 `image_path|image|visual_available`，所以 baseline 不是视觉模型逐图审计；
- `tables`：9/20 非空；
- `citations`：3/20 非空；
- 顶层 `supplements`：0/20 存在。部分主文段落/section label 会提及 Supplement，但没有独立补充文件对象。

因此“完整全文”在当前系统中的准确含义是：**完整的已解析、已清洗文本结构和可用图表元数据**。它不保证包含实际图像、源数据或独立 Supplement 文件。Prompt 中已经要求模型不得声称读取不可用模态。

## 1.3 Prompt 构成

一次 primary call 的实际文本是：

```text
System Prompt
+ CLI security/file-output wrapper
+ JSON(
     task/version
     semantic contract
     full SKILL.md
     output contract / selected YAML rules
     full JSON Schema
     extra requirements
     request context
     document manifest
     full clean document
   )
```

Repair call 重新包含 semantic contract、完整 Skill、Schema、document manifest 和完整 document，并额外加入 validation failures 与 candidate output。

## 1.4 输出及生成责任

### 必须由 LLM 完成的 L2/L3 内容

- article type 与 original-experiment scope 的语义判断；
- biological object 身份、谱系与实验角色绑定；
- experiment instance grouping 和跨章节对象归属；
- intervention、control、condition、replicate、readout、outcome 的语义抽取；
- source attribution、claim type、reported/inferred/unknown 判断；
- candidate evidence anchor 的科学语义选择；
- design action、trigger、rationale、alternatives 和 bounded rule candidate；
- 冲突识别及不同实验/阶段/构建体不合并判断。

### 可以由 Python 派生或后处理的内容

- 稳定 ID、hash、provenance、cache metadata；
- JSON 结构恢复、别名规范化、纯派生 manifest；
- 单位换算候选（必须保留 raw value/unit，当前尚未统一实现）；
- 从完整 canonical experiment graph 生成 document-level projection，前提是先定义无歧义投影规则；当前仍由模型同时生成 graph 与 projection。

### Validator 可以生成的内容

Validator 只能生成 check result、失败详情、计数和 review request。它可以验证 Schema、枚举、空值不变量、candidate evidence anchor existence、DDR gate 和 scope，但不能生成实验事实、理由、证据或规则。

# 2. Runtime Latency Breakdown

## 2.1 当前可测项

| Component | Basis | Median | p95 | Status |
|---|---|---:|---:|---|
| Total Skill07 cold wall time | 16 historical single-paper successes | 754,570 ms | 1,982,258 ms | MEASURED |
| Total Skill07 cache hit | 5 historical single-paper hits | 46.22 ms | — | MEASURED |
| Source JSON parse | 20 clean docs, local microbenchmark | 0.421 ms | 0.873 ms | MEASURED |
| Prompt construction | 20 clean docs | 36.502 ms | 55.409 ms | MEASURED |
| Prompt JSON serialization | 20 clean docs | 0.721 ms | 1.382 ms | MEASURED |
| API/CLI process startup | not instrumented | UNKNOWN | UNKNOWN | NOT SEPARABLE |
| Local semaphore wait | not instrumented | UNKNOWN | UNKNOWN | NOT SEPARABLE |
| Provider queue wait | not exposed | UNKNOWN | UNKNOWN | NOT SEPARABLE |
| Time to first token | `subprocess.run(capture_output=True)` | UNKNOWN | UNKNOWN | NOT SEPARABLE |
| Model inference/generation | no provider phase telemetry | UNKNOWN | UNKNOWN | NOT SEPARABLE |
| Output transfer | no streaming timestamps | UNKNOWN | UNKNOWN | NOT SEPARABLE |
| Output JSON parse | 17 cached outputs | 0.198 ms | 0.409 ms | MEASURED |
| Safe normalization | 17 cached outputs | 0.668 ms | 1.414 ms | MEASURED |
| Deterministic validation | 17 outputs | 19.615 ms | 26.192 ms | MEASURED |
| Cache JSON write | temp-dir benchmark, 17 results | 1.502 ms | 2.660 ms | MEASURED |
| Repair | no repair in 17 successful records | UNKNOWN | UNKNOWN | NOT OBSERVED |

这些微基准来自当前机器的顺序只读/临时文件测试，不是生产并发 SLA。不同样本不能做精确相减，但量级足以证明本地处理不是分钟级瓶颈。

## 2.2 当前 instrumentation 缺口

当前 stage log 只有总 `duration`；token usage 只保存在成功结果/cache 中；成功 transport attempt 数没有持久化；provider queue 和 model inference 不可见。建议未来增加以下不含正文的事件：

```text
source_load_ms
input_gate_ms
cache_lookup_ms / cache_hit
prompt_build_ms
prompt_chars_by_component
prompt_serialize_ms
local_semaphore_wait_ms
cli_spawn_ms
cli_time_to_first_byte_ms
cli_total_ms
provider_queue_ms (only if provider exposes it)
input_tokens / cached_input_tokens / output_tokens
attempt_number / retry_category / retry_delay_ms
result_file_read_ms / marker_parse_ms
normalization_ms
validation_ms_by_check
repair_class / repair_prompt_chars / repair_ms
cache_write_ms
```

若 CLI/provider 不提供 queue/inference 明细，必须继续标为 `UNKNOWN`，不能用总时间伪造拆分。

# 3. Token / Context Breakdown

## 3.1 当前 Prompt 字符测量

对 20 个现存 clean document 按当前 `_build_prompt` 和 CLI wrapper 构造请求：

| Component | Median chars | Median share of total |
|---|---:|---:|
| Full document JSON | 160,637 | 83.0% |
| Full Skill07 instructions | 11,335 JSON-encoded | 5.86% |
| Runtime JSON Schema | 6,039 compact JSON | 3.12% |
| Semantic contract | 5,908 JSON-encoded | 3.05% |
| System Prompt | 4,643 | 2.40% |
| Extra constraints/context/manifest/key overhead | 4,461 | 2.30% |
| CLI wrapper | 554 | 0.29% |
| **Total** | **193,576** | **100%** |

总字符范围 124,720–239,328，p95 236,481。最大 token 来源明确是 document。

## 3.2 历史 token telemetry

- input tokens：n=17，median 59,098，p95 69,811，max 73,980；
- output token telemetry 中 3 条与 44–75k 字符输出明显不一致，视为 telemetry anomaly；
- 排除 `<1000` 的 3 条异常后，credible output tokens：n=14，median 17,697，p95 27,460，max 31,567。

这些是历史 Prompt 版本的实测 token，不应当作当前新契约 Prompt 的精确 token 数；当前字符测量才对应当前代码。没有 tokenizer/provider usage 的当前受控 run，因此当前 token 估算应保留不确定性。

## 3.3 文档内部重复

文档 JSON 中位数组成：

- `paragraphs`：约 51.85%；
- `sections`：约 44.09%；
- `figures`：约 3.53%；
- 其余 metadata/tables/citations：很小。

20/20 文档中，每个 `paragraphs[].text` 都逐字存在于对应 `sections[].content`。如果仅删除 `sections[].content`，保留 section metadata 与全部 paragraphs，当前 Prompt 字符中位数理论减少 36.42%（范围 30.65%–39.48%）。但是 section content 可能还包含未被 paragraph builder 独立表达的 Markdown、图像占位或表格残余，因此生产方案必须保留并校验 residual fragments，而不是直接删字段。

# 4. LLM Call Necessity Audit

| Call | Purpose | Need LLM? | Need high capability? | Full context? | Optimization |
|---|---|---|---|---|---|
| Primary extraction | 重建实验实例、对象、因果/决策链、候选证据和 DDR | YES | YES, L3 | baseline YES | 保持 baseline；先测量，再验证无损文档表示、高召回 routing 或 cascade |
| Transport retry | 网络/CLI 失败后重复同一 primary | YES if no durable result | same as primary | YES | 分类错误；仅对 transient failure 重试；记录 attempt；检查 durable result 后避免重复 |
| Schema/semantic repair | 修复未通过 deterministic validation 的 candidate | SOMETIMES | 取决于失败类型 | currently YES | JSON/local-derived errors 本地修；缺字段 targeted repair；科学歧义才 full reasoning repair |
| Other Skill07 calls | 无应用级 Call C | N/A | N/A | N/A | Poe Code 内部行为对应用不透明，应通过 CLI telemetry确认 |

Title translation、Skill02 query expansion 等其他模型调用不属于 Skill07。

# 5. Prompt Optimization Audit

## KEEP IN PROMPT

- 文献事实、作者解释、model inference 和 causally validated 的边界；
- 当前论文与引用研究的归属区分；
- experiment-instance-first、对象/参数/scope 绑定；
- 跨章节 trigger→action→result 的时序纪律；
- 不得将不同实验、构建体、阶段和单位拼接；
- Figure/Table/Supplement 是正式证据源且缺失时不得假装读取；
- Q1/Q2/Q3、rule candidate 边界、alternatives 不得编造；
- Skill07 candidate 与 Skill08 verified 的交接边界。

这些是模型生成科学内容时必须遵守的语义，不可只留给事后 validator。

## MOVE TO PYTHON

- JSON 是否可解析；
- required keys、类型、enum membership；
- `unknown -> null/empty evidence` 等可确定性表达的不变量；
- evidence ID 是否存在；
- contract/rules/schema version 与 hash；
- cache identity、provenance、check count；
- 可机械派生的 document manifest、稳定 ID、别名 canonicalization；
- 纯格式 fence/前后文本/换行修复。

这些项目多数已经在 Python 中验证；Prompt 中无需多段重复解释实现细节。

## SHARED

- 模型必须知道目标 Schema 才能生成，Python 必须再次验证；
- 模型必须知道 reported/inferred/unknown 语义，Python 必须验证可表达的空值/证据条件；
- 模型必须知道 rule eligibility 和 scope，Python 必须硬门禁；
- 模型必须选择 candidate anchors，Skill08 必须独立验证。

System Prompt、完整 Skill、semantic contract、`requirements` 和 `output_contract` 对 article gate、状态、证据角色、DDR、scope 与提交检查存在明显语义重复。固定非文档内容只占当前 Prompt 约 17%，即便全部删除也不可能解决 12 分钟级瓶颈；而全部删除会损害质量。正确做法是建立 clause-to-validator traceability，在 benchmark 中逐条合并重复表述，而不是直接压缩。

# 6. Context Reduction Analysis

## 6.1 为什么当前需要全文

实验设计并不只在 Methods：

| Information | Common sources | Why cross-section context matters |
|---|---|---|
| objective / initial trigger | Abstract, Introduction, early Results | 决策动机经常早于具体实现 |
| design action | Methods, Results, figure legends | 工程动作可能首次在 Results/图注出现 |
| rationale / mechanism | Introduction, Results, Discussion | 必须区分事前依据与事后解释 |
| implementation parameters | Methods, tables, Supplement | 精确条件、构建和重复信息常在附件 |
| result / effect | Results, figures, tables | Methods 不能提供最终 outcome |
| alternatives / failure-driven revision | Results, Discussion | 需要跨实验阶段连接失败与后续动作 |
| evidence attribution | 全文及 references | 需要区分当前研究和引用研究 |

17 个历史成功输出的候选 locator 广义遍历得到 1,562 次可解析 paragraph-anchor occurrence：Results 548，Methods 301，Discussion 39，Introduction 30，Abstract 10，Supplement-labeled 7，另有 627 次落在无法可靠归类的具体编号 section。还有 117 次 locator 使用了非 canonical/未解析形式。该统计会重复计算同一 anchor，且受历史版本和 section label 质量影响，但足以否定 Methods-only：已明确归类的非 Methods anchors 数量超过 Methods。

## 6.2 当前 full-context 的质量缺口

- 没有实际 figure image，只有 caption/metadata；
- 没有独立 `supplements` artifact；
- sections 与 paragraphs 重复导致 token/attention 浪费；
- section labels 不总能可靠归类；
- nested experimental object 中存在一些非 canonical locator，当前字段级 validator 不一定覆盖所有嵌套 locator。

因此下一阶段既要降低冗余，也要提升真正的图表/Supplement 覆盖，不能把“减少 token”等同于“删掉模态”。

# 7. Section Routing Feasibility

## 7.1 值得 prototype，但不可直接生产

建议测试 **High-Recall Evidence Routing**，而不是“只读 Methods”：

```text
Full parsed document
  -> lossless canonical content index
  -> multi-query candidate retrieval by extraction facet
  -> section headers + selected paragraphs + adjacency windows
  -> all linked figure/table legends
  -> supplement index/content when available
  -> references linked by selected claims
  -> coverage manifest and omitted-region digest
  -> L3 extraction
  -> deterministic validation + Skill08
  -> uncertainty/coverage gate
  -> fallback to full-context baseline
```

候选 retrieval 必须分别覆盖 action、trigger、rationale、objects、implementation、controls、replicates、readouts、results、alternatives、conflicts 和 rule scope，不能用一个通用摘要 query。

## 7.2 必须保护的风险

- 跨章节因果链被切断；
- Results 中首次出现的设计动作被漏掉；
- Discussion 的事后解释被误标为事前 rationale；
- Figure legend/Table 的分组与结果丢失；
- Supplement 中精确构建/参数/重复结构丢失；
- 综述中的 included-study attribution 被 references 裁剪破坏；
- retriever 与 extractor 出现相关错误，validator 仍可能“结构通过”。

## 7.3 Prototype acceptance

Routing 只能在 paired Golden Benchmark 上晋级。Critical Evidence Recall、wrong-attribution、critical hallucination 和 experiment grouping 不得差于 full-context baseline；任一 paper 的关键证据回忆下降都触发 HOLD。初期应 shadow-run，不替代 baseline。

# 8. Map-Reduce Feasibility

候选设计：

```text
Map A: Methods / implementation candidates
Map B: Results / outcomes / revisions
Map C: figures + tables + captions
Map D: Supplement / exact parameters
Map E: Introduction + Discussion / pre-vs-post rationale
Reduce: global experiment/object/decision synthesis with original anchors
```

优势：map 可并行；每个 context 更短；局部 evidence recall 容易单独测量。

主要风险：

- 同一实验被多个 map 重复实例化；
- strain/construct identity 在 map 间漂移；
- trigger、action 和 result 被分散，reduce 反向编造因果；
- map 的局部解释冲突；
- reduce 输入包含大量重复中间 JSON，token 未必下降；
- 更多模型调用提高总成本、provider queue 和部分失败概率。

结论：适合 P2 研究，不是首选优化。必须用全局 object registry、稳定 anchor、conflict-preserving reduce 和 full-context fallback；不能把 map 输出当摘要直接拼接。

# 9. Model Cascade Feasibility

## 9.1 能力分层

| Level | Skill07 work |
|---|---|
| L0 deterministic | Schema、required fields、anchor existence、enum、hash、cache、provenance |
| L1 semantic | section/genre candidate classification、retrieval query、locator normalization |
| L2 reasoning | experiment grouping、object binding、跨段条件与结果归属 |
| L3 scientific reasoning | 设计逻辑重建、trigger 与 post-hoc 区分、evidence vs speculation、rationale、alternatives、bounded rule |

Skill07 的核心价值在 L2/L3。当前证据不能证明某个特定品牌模型是唯一选择，也不能证明 fast model 足以完成 L3。

## 9.2 安全 cascade 设计

```text
Candidate model
  -> deterministic validator
  -> Skill08 evidence binding
  -> coverage / omission / attribution risk detector
  -> optional model disagreement check
  -> calibrated acceptance gate
       PASS -> random human audit + retain provenance
       FAIL/UNCERTAIN -> baseline high-capability full-context extraction
```

Schema pass、无 repair 和模型自报 confidence 都不能单独作为 PASS，因为它们检测不到静默遗漏和科学上合理但错误的内容。

理论期望延迟：

```text
E[T] = T_fast + (1 - pass_rate) * T_baseline + T_validation
```

只有实际 `pass_rate`、质量 gate false-accept rate 和两模型延迟被 30/50 篇 benchmark 测得后，才能计算收益。未经 benchmark 不换模型。

# 10. Repair Optimization

## 10.1 当前行为

- marker parser 已容忍代码 fence、短前后文本和终端换行包装；
- result file 非法 JSON 会被当成 CLI error，随后重新执行完整 primary transport attempt；
- additive normalization 能补 contract/applicability/evidence-role 等兼容字段；
- 其他 Schema/semantic failure 触发一次 full-document repair；
- repair 再次发送全文和完整规则，并附 candidate output。

17 个成功 cache record 都没有 schema repair。映射到 clean doc 的 17 个样本中：primary JSON chars median 193,209；repair median 243,507；repair 是 primary 的 median 128.06%。

## 10.2 推荐分层

1. **Parse repair（L0）**：fence、前后文本、合法 JSON 片段、转义、截断诊断；本地处理，不重新请求模型。
2. **Derived-field repair（L0）**：contract version、candidate role、manifest、稳定 ID、可确定性 alias；本地处理并记录 action。
3. **Targeted extraction repair（L2/L3）**：明确缺失的少数字段，发送原 candidate、失败规则和相关原文窗口；必须保留 anchor 与 scope。
4. **Scientific/full repair（L3）**：experiment grouping、归属、冲突、trigger/rationale 等全局失败，才发送全文。

Targeted repair 本身可能丢失跨章节上下文，属于 benchmark-gated。任何局部 repair 失败或风险 gate 不确定时回退 current full repair。

# 11. Cache Audit

| Required identity | Current state | Risk |
|---|---|---|
| paper identity | 不显式包含；以 clean-document content bytes 代替 | 同内容跨 identity 复用通常安全，但 paper identity provenance 不能仅靠 key 恢复 |
| document hash/content | YES | 内容变化会失效 |
| System Prompt | SHA-256 bytes included | 安全 |
| SKILL | SHA-256 bytes included | 安全 |
| Schema | SHA-256 bytes included | 安全 |
| semantic contract/rules | SHA-256 bytes included | 安全 |
| validator/runtime contract | version string included | 安全，依赖开发者正确 bump |
| prompt-builder extra constraints | **源码本身不在 key** | `_build_prompt.requirements` 改变但相关版本未 bump 时可能错误复用 |
| model name | string included (`kimi-k3`) | 只是 mutable alias |
| model provider/endpoint | NO | 同名模型切 provider 可能错误复用 |
| immutable model revision | NO | provider 更新 alias 后可能复用旧输出 |
| decoding/reasoning parameters | 未显式包含 | CLI/provider 默认变化可能错误复用 |

当前 Schema、Skill、System Prompt、contract 和 rules 变化不会错误复用。主要缺口是 prompt builder code/strategy、provider、immutable revision 和 inference settings。建议 v2 cache identity 增加：

```text
provider_id
provider_endpoint_class
immutable_model_revision
inference_profile_hash
prompt_builder_version/hash
context_strategy + router_version
repair_strategy_version
```

成功 cache 可复用、失败不缓存是正确策略。cache record 应保留首次 cold-run telemetry，cache hit 不应覆盖原始 timing。

# 12. Benchmark Design

## 12.1 Frozen corpus

建立 50 篇冻结语料，10/30/50 是同一 corpus 的递增子集。允许类别重叠，但必须覆盖：

- 长论文与短论文；
- 多实验、多菌株、多构建体；
- 复杂跨章节设计逻辑；
- Figure/Table 密集；
- Supplement 丰富且精确参数依赖附件；
- Methods 不完整或分散；
- review/methods/protocol 与 primary research 混合文类；
- OCR/section-label 较差；
- 含失败驱动迭代、alternatives 和 post-hoc rationale；
- 无可泛化 rule 的负样本。

### 10 篇：快速实验

- 冻结 current baseline output、raw source、clean artifact、Prompt/cache/model provenance；
- 双人标注关键实验实例、对象、字段、证据、DDR 与禁止推断；
- 用于淘汰明显损害质量的 prompt dedup、lossless document view、repair routing 原型；
- 每个 variant 至少重复 2 次以观察非确定性。

### 30 篇：稳定性

- 增加长文、多实验、Supplement、综述/Methods paper 和 parser 质量边界；
- paired blind review；
- 至少 3 次运行或足够重复用于估计 output variance；
- 测量 fallback/cascade pass rate、repair rate、provider errors 与 per-paper regression。

### 50 篇：生产模拟

- cold cache 与 warm cache 分开；
- 按计划并发度运行，测 provider queue、限流、tail latency 和失败隔离；
- 完整保存 token、call、repair、Skill08/09 与 reviewer decision；
- 任何关键质量回归、无法解释的 locator 丢失或 Supplement 漏检均阻止上线。

## 12.2 标注单元

- experiment instance；
- biological object / construct；
- field value + epistemic status + applicability；
- candidate evidence anchor + attribution + semantic support；
- decision action + trigger + rationale + alternatives；
- implementation + result；
- bounded rule candidate + tested/excluded scope；
- explicit missing/conflict/dependency；
- hallucinated claim 或错误合并。

# 13. Quality Gate

Baseline 与 optimized 必须用同一 source artifact、同一评审 rubric、盲审和 paired comparison。

| Dimension | Metric | Production gate |
|---|---|---|
| Completeness | gold field/experiment weighted recall | point estimate不得低于 baseline；任一 critical omission 需裁决 |
| Evidence correctness | E1 existence、E2 attribution、E3 semantic support precision | 不得下降；wrong attribution 零容忍 |
| Evidence coverage | gold claims with valid anchor | 不得下降 |
| Experiment grouping | split/merge/object-binding errors | critical error 不得增加 |
| Scientific reasoning | action、trigger、rationale、alternatives、implementation、result、rule 分项 rubric | 每项不得低于 baseline |
| Hallucination | unsupported values/causes/rules per paper | critical hallucination 不得增加；目标为降低 |
| Human acceptance | accept / minor edit / major edit / reject | accept rate 不得下降，major/reject 不得增加 |
| Governance | Skill07 candidate/Skill08 verified boundary | 零越权 |
| Performance | wall time、tokens、calls、repair、tail latency | 只在全部质量 gate 通过后比较 |

统计上使用 paired bootstrap confidence interval 展示不确定性。若质量差值的置信区间跨入负区间，状态是 **HOLD / evidence insufficient**，不是自动 PASS。不能用平均提升抵消某篇论文的 critical hallucination、错误来源归属或关键 Supplement 丢失。

# 14. Optimization Matrix

| Proposal | Speed Benefit | Quality Risk | Recommendation |
|---|---|---|---|
| 分段 telemetry | 无直接加速；使瓶颈可测 | LOW | P0，立即设计 |
| 保留/强化 content cache | 重复论文约 12.58 min→46 ms | LOW | P0 |
| provider/revision/prompt-builder cache identity | 避免错误复用 | LOW | P0 |
| 本地 JSON/derived-field repair | 避免无意义全文重试 | LOW | P0；保持 provenance |
| transient retry 分类与 durable-result recovery | 降低最坏 5× 重复调用 | LOW | P0 |
| lossless document representation dedup | median Prompt chars 理论 -36.42% | LOW–MEDIUM | P1 Golden Benchmark；保留 residual fragments |
| Prompt clause 去重 | 固定部分最多约 17%，实际收益更小 | MEDIUM | P1；逐 clause benchmark |
| Targeted field repair | repair 场景可显著省 token | MEDIUM–HIGH | P1；现有 repair rate 不足以证明收益 |
| High-recall section routing + full fallback | 潜在显著 | HIGH | P1 prototype/shadow；不得 Methods-only |
| Fast-model cascade | 取决于 pass rate | HIGH | P1/P2；不得以 Schema/self-confidence 放行 |
| Direct API/native structured output | 可能减少 CLI overhead，当前 overhead UNKNOWN | MEDIUM | P1 测量；同模型同 benchmark |
| Section Map-Reduce | 可能并行 | HIGH | P2 research only |
| 增加 paper-level 并发 | 提升 throughput，不降低单篇推理时间 | LOW–MEDIUM | load test 后调整；受 provider 全局门限制 |
| Methods-only | token 大幅下降 | CRITICAL | REJECT |
| 忽略 Supplement/Figure | token 下降 | CRITICAL | REJECT |
| 未 benchmark 直接换模型 | UNKNOWN | CRITICAL | REJECT |

# 15. Recommended Skill07 v2 Architecture

只设计，不在本次实现：

```text
Clean Document Artifact
  -> lossless canonical content store
       paragraphs as single text copy
       section hierarchy metadata
       figure/table/supplement artifacts
       residual-fragment preservation
  -> versioned context strategy
       BASELINE: full canonical context
       EXPERIMENTAL: high-recall routed bundle
  -> immutable model/provider/inference profile
  -> primary L3 extraction
  -> repair classifier
       local parse/derived repair
       targeted repair (benchmark-gated)
       full scientific repair fallback
  -> deterministic schema/semantic/DDR validator
  -> Skill08 independent evidence binding
  -> Skill09 quality gate
  -> routing/cascade risk gate
       uncertain -> full-context baseline rerun
  -> versioned cache + complete telemetry + human review
```

核心原则：context optimization 是可版本化策略；full-context baseline 始终保留为 fallback；任何 routed/cascade output 都不能绕过 Skill08/09；model revision、context strategy 和 repair strategy 全部进入 cache/provenance。

# 16. Roadmap

## P0：无质量风险优化

1. 增加细粒度、无正文 telemetry；建立当前 Kimi-K3 frozen baseline。
2. 完善 cache identity：provider、immutable revision、inference profile、prompt-builder/context strategy。
3. 持久化每个 transport attempt、retry category、repair cause 和 cold timing。
4. 将纯 JSON/derived-field 错误本地修复；科学失败继续 full repair。
5. 建立 10 篇 gold set、标注规范和盲审工具。

## P1：必须通过 Benchmark

1. 设计保留 residual fragments 的 canonical document dedup；先做 10 篇 paired test。
2. 对重复 Prompt clauses 做逐项 ablation，不删除科学不变量。
3. 设计 targeted repair，失败自动回退全文。
4. High-recall routing shadow-run；用 30 篇测试 evidence recall 和 silent omission。
5. 在同一 30/50 篇 benchmark 上测试 direct API、structured output 与候选 model cascade。

## P2：长期架构优化

1. 真正接入 figure image、table structure、independent Supplement artifacts。
2. 研究 anchor-preserving Map-Reduce 和全局 object registry。
3. 建立 provider-independent model evaluation、calibrated risk gate 和持续 drift benchmark。
4. 将 50 篇生产模拟纳入 release gate；监控长尾、质量漂移、cache provenance 和 reviewer acceptance。

## Final Safety Check

- [x] 没有把降低质量的方案直接建议进入生产。
- [x] 没有推荐 Methods-only。
- [x] 没有忽略 Supplement、figures 或 tables。
- [x] 没有未经 benchmark 推荐替换 Kimi-K3。
- [x] 没有把科学推理简化为摘要。
- [x] 所有数字来自代码、现存 artifact/checkpoint/cache 或明确标注的本地微基准。
- [x] 不可拆分的 provider/CLI 时间均标为 UNKNOWN。
- [x] 未修改生产逻辑。


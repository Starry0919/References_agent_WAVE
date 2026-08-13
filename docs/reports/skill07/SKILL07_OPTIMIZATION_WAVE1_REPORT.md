# Skill07 Performance Optimization Wave 1 Report

日期：2026-08-12  
硬约束：`Quality(candidate) >= Quality(current production baseline)`  
运行模式：shadow / staged benchmark；**Production behavior changed? NO**

## Executive Summary

1. 已实现：统一 baseline manifest、可恢复 candidate harness、无损 canonical transformer、residual preservation、repair classifier/local parse repair、high-recall routing prototype、anchor-preserving Map-Reduce plan、fail-closed cascade framework、强化 cache identity、结构化科学 comparator、bounded concurrency/failure isolation、人工复核队列。
2. 已 benchmark：Stage 0 对现有 19 篇全部完成 representation-only；Stage 1 复用被新任务中止前已落盘的 5 个完整 Kimi-K3 baseline/canonical pairs。没有为填表继续盲目调用全部 candidate×19。
3. 被拒绝直接生产：Methods-only、忽略图表/Supplement、有损截断、未验证模型替换，以及用结构相似度代替人工科学真值。
4. 可晋级：**本轮没有任何 LLM candidate 通过非劣效证据门禁**。Canonical 的表示层实现通过无损门禁，但抽取层只达到 `HOLD_FOR_MORE_BENCHMARK`。
5. 当前最优低风险组合是 `G_SAFE_COMBINED = Canonical + local deterministic repair + cache hardening + telemetry`，但仍为 HOLD，不能进入生产默认路径。
6. 19 篇 canonical 字符减少 median **30.68%**，范围 **22.16%–34.55%**；19/19 exact round-trip，0 个 section fallback。
7. 5 个 smoke pairs 中，canonical median latency **1,446.0 s**，baseline **991.6 s**，即本轮 canonical 反而约慢 **45.8%**。输入 token median 从 **133,291** 降至 **105,707**（约 **20.7%**），但 repair/输出和 provider 方差吞噬了输入收益。
8. 按单调用 median 粗略换算，baseline 3.63 papers/hour，canonical 2.49 papers/hour；这不是 batch concurrency=1/2/4 的受控 throughput 测量。受中断与 provider 长尾影响，batch throughput 标为 `NOT_MEASURED`。
9. 是否有质量下降：自动结构 comparator 在 5/5 pairs 中都发现 experiment/evidence/source-location 差异；状态方向混合（canonical 有时通过而 baseline 失败，也有相反情况）。这不足以证明 canonical 下降，也绝不支持非劣效，必须人工审阅并重复运行。
10. 距离 1000 篇生产：还缺 Skill07 人工 gold、至少 10 篇完整受控 paired benchmark、重复运行以量化 Kimi-K3 方差、真实 Supplement/figure artifact 链路、稳定 provider telemetry、durable queue、受控 1/2/4 throughput test 与 canary/rollback。

## 1. Baseline Freeze

生成 `skill07_baseline_manifest.json`，冻结 19 篇同一来源集：

- 19/19 映射到原始 PDF，并记录 PDF SHA-256；
- 记录 clean document path/hash/version；
- 记录 System Prompt、Skill、Schema hash 和 validator version；
- provider=`poe_code_cli`，model=`kimi-k3`；immutable model revision 与 reasoning profile 当前 `UNKNOWN`；
- 16/19 找到历史 extraction cache；其余 baseline output path 明确为空，不伪造；
- 记录历史 latency/token（有则写入）、review status 和完整 candidate-isolated cache identity。

Baseline 始终保持当前生产行为；本轮没有修改 production executor、Prompt、Skill 或 Schema。

## 2. Golden Benchmark Harness

新增 `tools/run_skill07_wave1.py` 与公共组件 `tools/skill07_wave1.py`：

- deterministic artifact discovery 和 19 篇 freeze；
- Stage 0 全量、Stage 1 smoke、Stage 2/3 gate；
- candidate-specific output/cache identity；
- 已有结果复用、transport failure 可单独重试、每论文失败隔离；
-统一 latency、tokens、repair、validation 和结构差异输出；
- 自动生成 JSON、CSV 和 human-review queue。

上一轮长跑被本任务替换时，两个 benchmark 根进程及其子进程被终止；已落盘结果保留。Wave 1 复用了 5 个完整 pair，避免重复额度消耗。

## 3. Candidate B — Canonical

`tools/canonical_document_transformer.py` 实现单一正文来源：

- section 保存 ID、title、level、hierarchy、paragraph IDs；
- paragraph 保存 ID、section ID、position、text；
- `section.content - ordered paragraph text` 保存为带位置的 `residual_content`；
- residual 可保存 Markdown、图像/表格占位、公式、列表、parser fragment；
- 不可安全顺序匹配时保留完整 section fallback；
- canonical 可精确恢复原 clean JSON。

Stage 0：19/19 exact round-trip；paragraph/section/figure/table/citation 均保持；0 fallback；字符压缩 median 30.68%。当前 measured set 没有独立 Supplement artifact，因此不能声称覆盖真实 Supplement，只保留未来字段和 residual。

Stage 1 的 5 pairs：baseline succeeded 2/5，canonical succeeded 3/5；两侧几乎都经历一次 full repair。状态不稳定且 5/5 有结构 hard flags。结论：`HOLD_FOR_MORE_BENCHMARK`。

## 4. Candidate C — Repair

实现 repair taxonomy：

- `R0_PARSE_ERROR` → deterministic local JSON recovery；
- `R1_STRUCTURAL_ERROR` → local normalization，失败回退全文；
- `R2_MISSING_FIELD` → targeted repair candidate，失败回退全文；
- `R3_LOCAL_SEMANTIC_ERROR` → targeted repair candidate，失败回退全文；
- `R4_SCIENTIFIC_REASONING_ERROR` → existing full-context repair。

本轮只实际验证 deterministic classifier/local parse repair；targeted LLM repair 未运行，避免在没有 gold 时引入静默科学退化。决定：`HOLD_FOR_MORE_BENCHMARK`。

## 5. Candidate D — High-Recall Routing

实现 fail-closed shadow router：保留 Abstract、Introduction、Methods、Results、Discussion、Supplement-labeled sections、所有未知章节，以及全部 figures/tables/citations。它不是 Methods-only。

Coverage report 明确记录 selected/unselected content 和各模态覆盖；没有人工 gold 时 `critical_evidence_recall=UNKNOWN_WITHOUT_GOLD`。无法证明关键 evidence recall，因此决定：`HOLD_FOR_MORE_BENCHMARK`，未调用 LLM。

## 6. Candidate E — Map-Reduce

实现 anchor-preserving plan，将 objective/trigger、methods/implementation、results/phenotype、figures/tables、Supplement、evidence candidates 分流，并要求 reduce 使用全局 object registry、原始 anchors、conflict preservation 与 trigger-before-action validation。

内置检查 experiment fragmentation、duplicate instances、lost causal chain、wrong cross-section linkage、missing alternatives/failure iteration 和 rule degradation。未进行昂贵 LLM run；决定：`NOT_RUN`。

## 7. Candidate F — Cascade

实现 fail-closed cascade gate。候选即使 Schema 通过，只要缺 Skill08 independent verification 或 human/gold correctness，均回退 `kimi-k3`。仓库没有另一个已验证的合法 fast model/config，也没有可靠 confidence calibration。

决定：`FRAMEWORK_READY_BUT_NOT_VALIDATED`，没有假装替换 baseline。

## 8. Candidate G — Safe Combined

组合仅包含：Canonical、local deterministic repair、cache hardening、telemetry。Routing、Map-Reduce 和 cascade 未自动加入。

组件测试通过，但 Canonical 的 extraction non-inferiority 证据不足，决定：`HOLD_FOR_MORE_BENCHMARK`。

## 9. Telemetry Findings

Shadow harness 记录每次 subprocess total、attempt、repair duration、input/output tokens、prompt chars、status 和错误类别。底层仍不暴露：

- provider request start：`NOT OBSERVABLE`；
- provider queue：`NOT OBSERVABLE`；
- provider-side inference：`NOT OBSERVABLE`；
- time to first output：当前 `subprocess.run(capture_output=True)` 下 `NOT OBSERVABLE`。

没有读取、输出或写入 API key/Authorization。Secret scan 对交付 JSON/CSV/MD 零命中。先前已存在 credential exposure risk，仍建议 rotation；本报告不复述任何凭证。

## 10. Cache Findings

Shadow cache identity 覆盖：paper ID、source document hash、representation version、Prompt hash、Skill hash、Schema hash、validator version、provider、model、model parameters 和 candidate ID。Canonical 不可能错误复用 baseline；模型/representation/candidate 变化均改变 key。

当前生产仍缺 immutable provider model revision、完整 inference profile 和 prompt-builder source hash；这些应在未来 feature-flag migration 前补齐。

## 11. Concurrency Findings

Harness 支持 bounded workers、per-paper isolation、resume 和 transport retry。已有 smoke run 使用 concurrency=4；为额度敏感和质量优先，本轮没有再重复跑 1/2/4 全套，因此 papers/hour/p50/p90/p95 batch 指标为 `NOT_MEASURED`。

5-pair 单调用 median 仅作观察：baseline 991.6 s，canonical 1,446.0 s。当前不应扩大并发来掩盖单调用回归和质量不确定性。

## 12. Scientific Quality Comparison

Comparator 不使用 BLEU/ROUGE。它比较 experiment IDs、object/strain/construct binding、evidence IDs/source locations、design action、trigger、reason、alternatives、implementation、result 和 rule candidate。

Hard flags 只表示“值得人审的结构变化”，不等于 candidate 错误。5/5 pairs 均存在 baseline-only experiment/evidence/location 项；同时部分 canonical 有新增项。由于 baseline 自身 3/5 validation_failed，不能把 baseline 当科学真值。

## 13. Human Review Queue

仓库检测到 Skill08 verification gold annotation，但未找到覆盖本轮 19 篇的 Skill07 approved extraction/gold。已生成 `HUMAN_REVIEW_QUEUE.md`，只列：baseline-only/candidate-only experiment、evidence、reasoning 与 rule 差异，减少人工负担。

## 14. Candidate Ranking

详见 `skill07_candidate_matrix.csv`：

| Candidate | Quality Gate | Input Reduction | Median Latency | Throughput | Risk | Decision |
|---|---|---:|---:|---:|---|---|
| A Baseline | BASELINE | 0% | 991.6 s | 3.63/h observed-equivalent | unstable/repair | BASELINE |
| B Canonical | representation PASS; extraction insufficient | 30.68% | 1,446.0 s | 2.49/h observed-equivalent | 5-pair structural flags | HOLD_FOR_MORE_BENCHMARK |
| C Repair | framework tested; targeted LLM not run | 30.68% | NOT_MEASURED | NOT_MEASURED | semantic repair unvalidated | HOLD_FOR_MORE_BENCHMARK |
| D Routing | gold coverage unavailable | UNKNOWN | NOT_MEASURED | NOT_MEASURED | critical recall unknown | HOLD_FOR_MORE_BENCHMARK |
| E Map-Reduce | framework only | UNKNOWN | NOT_RUN | NOT_RUN | fragmentation | NOT_RUN |
| F Cascade | no validated fast model/gate | 30.68% | NOT_MEASURED | NOT_MEASURED | false accept | FRAMEWORK_READY_BUT_NOT_VALIDATED |
| G Safe Combined | components pass; extraction insufficient | 30.68% | NOT_MEASURED | NOT_MEASURED | B not cleared | HOLD_FOR_MORE_BENCHMARK |

## 15. Promote / Hold / Reject Decisions

- `HIGH_PRIORITY_PROMOTE`: none。
- `PROMOTE_CANDIDATE`: none。
- `HOLD_FOR_MORE_BENCHMARK`: B, C, D, G。
- `FRAMEWORK_READY_BUT_NOT_VALIDATED`: F。
- `NOT_RUN`: E LLM prototype。
- `REJECT`: Methods-only、有损 truncation、忽略 Figure/Table/Supplement、未 benchmark 模型替换、用自动相似度冒充真值。

## 16. Recommended Production Migration Plan

当前不迁移。满足以下条件后才创建 feature flag：

```text
SKILL07_OPTIMIZATION_MODE=baseline   # default
SKILL07_OPTIMIZATION_MODE=canonical # shadow/canary only
```

顺序：完成 10 篇 paired repeats + Skill08/gold/human adjudication → hard gates 全过 → shadow 100%/write 0% → 小比例 canary → cache/provenance 验证 → rollback rehearsal → 才考虑默认切换。任何 critical omission、unsupported claim、wrong attribution、provenance regression 或 Schema regression 均立即回滚 baseline。

## 17. Remaining Risks

- 当前没有 Skill07 gold；自动比较不能决定科学真值。
- Kimi-K3 非确定性和 full repair 噪声可能大于 representation 差异。
- 当前 clean documents 没有独立 Supplement，也没有实际 figure visual；这是质量缺口，不是可利用的压缩理由。
- provider queue/TTFT/inference 不可观测。
- 5 pairs 不足以做非劣效统计；Stage 2 至少 10 篇且需要重复运行。
- 1000 篇 throughput 不能由单调用 median 线性保证，还受 provider rate limit、durable scheduling、失败恢复和人工审核容量限制。

## Added / Modified Files

Added：

- `tools/canonical_document_transformer.py`
- `tools/benchmark_skill07_canonical_representation.py`（前序 shadow prototype，结果被本轮复用）
- `tools/skill07_wave1.py`
- `tools/run_skill07_wave1.py`
- `tests/paper_extraction/test_skill07_wave1.py`
- `skill07_baseline_manifest.json`
- `skill07_optimization_wave1_results.json`
- `skill07_candidate_matrix.csv`
- `HUMAN_REVIEW_QUEUE.md`
- `SKILL07_OPTIMIZATION_WAVE1_REPORT.md`
- `artifacts/skill07_wave1/stage0/*`

Modified production files：none。  
Production behavior changed? **NO**。

## Supplement Quality Gap

19 篇 measured clean artifacts 均没有独立 Supplement artifact。Canonical 保留任何现有 Supplement 引用、section text、figures/tables 和 residual，但不能声称读取未提供的真实附件。未来 Supplement downloader/parser 必须成为 canonical content store 的独立模态入口，并纳入 evidence recall 与 cache identity。


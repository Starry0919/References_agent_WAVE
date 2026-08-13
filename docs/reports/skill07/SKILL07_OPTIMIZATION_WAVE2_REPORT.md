# Skill07 Optimization Wave 2 Final Promotion Benchmark

日期：2026-08-12  
最终决定：**HOLD**  
Production default changed：**NO**

## Executive Summary

1. 实际调用链是 `poe_code_cli`；源码默认 `claude-sonnet-4.6`，`.env` 配置、解析后的运行时模型和 Wave 1 实际 CLI `--model` 参数均为 `kimi-k3`。供应商内部解析后的模型及不可变 revision 不可观测，记为 `UNKNOWN`。
2. Wave 1 provenance **不完全正确**：运行实际使用 `kimi-k3`，但历史 baseline manifest 将源码默认 `claude-sonnet-4.6` 写成模型与 cache identity。历史文件已保留，不能作为合格复用身份。
3. 本轮新增 fail-closed provenance gate、纠正清单、秘密安全序列化、两层语义对齐器、稳定 gold ID/review 模板、A/G×重复隔离矩阵、repair-aware telemetry 合同、bounded concurrency/retry/failure-isolation 工具与测试。
4. 对 5 个 Wave 1 完整历史配对重新对齐：`FORMAT_ONLY=0`、`SEMANTICALLY_EQUIVALENT=0`、`POTENTIALLY_MEANINGFUL=0`、`CRITICAL_SCIENTIFIC_DIFFERENCE=19`、`AMBIGUOUS_REQUIRES_HUMAN=47`。这是确定性分类，不是科学真值；旧的“5/5 全部 hard flag”已被更细粒度结果替代。
5. 独立 gold 尚未建立，状态为 `AWAITING_HUMAN_ADJUDICATION`。Codex 未将 A 或 G 冒充 gold。
6. 已基于 clean-document 结构、既有配对状态、长度、图表、段落及 Methods/Results 特征选择 10 篇 core gold papers；另 9 篇保留为结构/回归集。
7. A vs gold：`AWAITING_HUMAN`。
8. G vs gold：`AWAITING_HUMAN`。
9. 是否存在关键 G 回归：`UNKNOWN`；19 个自动关键差异仍待结合原文裁决。
10. G token 变化：Wave 2 `NOT_MEASURED`；仅保留 Wave 1 非受控历史结果（input token median 约 -20.7%），不作晋级证据。
11. First-pass latency change：`NOT_MEASURED`。
12. Repair rate/cost change：`NOT_MEASURED`。
13. Total latency change：Wave 2 `NOT_MEASURED`；Wave 1 历史观测约 +45.8%，因缺乏完整分段 telemetry 不归因。
14. Throughput c=1/2/4：全部 `NOT_MEASURED`。科学质量硬门未完成，额外吞吐调用不能解决该门槛。
15. G 最终决定：**HOLD**。
16. 原因：provenance 工程门已修复且预检通过，但独立人工 gold 与关键差异裁决仍缺失。按 Stop Rule E，不能伪造 gold；在此状态下开展 pilot、60-run 重复和 concurrency 扩展无法证明质量非劣。

## Wave1 Validity Review

Wave 1 的 representation 结果仍有效：19/19 exact lossless round-trip、0 fallback section、字符中位减少 30.68%。但其 baseline manifest 的模型字段来自源码默认，不是运行时解析值。5 个完成配对确实记录了 `model=kimi-k3`，因此历史抽取本身可作为待复核材料，但不能按旧 manifest/cache identity 当成完全受控的晋级实验。

## Runtime Model/Provider Provenance

| Surface | Observed value |
|---|---|
| Source-code default | `claude-sonnet-4.6` |
| `.env` model selector | `kimi-k3` |
| Resolved runtime config | `kimi-k3` |
| Actual CLI argument | `--model kimi-k3` |
| Provider/tool | `poe_code_cli` / Poe Code CLI |
| Provider-resolved model | `UNKNOWN` |
| Immutable revision | `UNKNOWN` |
| Seed/temperature | `NOT_AVAILABLE` |

每个 Wave 2 invocation identity 包含 provider、model/alias、运行时解析、CLI、可见参数、prompt/SKILL/schema/validator hash、representation、candidate、source hash、run ID 与时间戳。任何 manifest/cache/runtime 不一致均返回 `BENCHMARK_BLOCKED_PROVENANCE_MISMATCH`。秘密字段被 fail-closed 排除；未输出 `.env` 全文。

## Corrected Baseline Manifest

`skill07_wave2_baseline_manifest.json` 保留历史 manifest 路径，逐篇记录 drift、纠正后的 `kimi-k3` runtime identity、独立 cache identity 和 gate 结果。19 篇预检均通过。历史 `skill07_baseline_manifest.json` 未被重写。

## Semantic Alignment Design

Layer 1 仅规范比较用 ID：大小写、空格、`-/_` 和数字前导零；原 ID 保留，`EXP1` 不会匹配 `EXP10`。Layer 2 使用对象、干预、条件、readout、结果及 evidence anchors 形成科学签名。先确定性 ID 匹配，再做保守签名匹配；相近候选没有足够 margin 时输出 `AMBIGUOUS_REQUIRES_HUMAN`，不强配。

对齐后比较 experiment grouping、对象绑定、intervention、condition、result 和 evidence。自动 comparator 明确标记 `automated_scientific_truth=false`。

## Comparator Validation

测试覆盖：`EXP-01≈EXP1`、`EXP1≠EXP10`、对象格式变化、真实 intervention 改变、evidence locator 改变与歧义不强配。历史配对重算得到 19 critical 和 47 ambiguous；格式项不会进入人工队列。

## Gold Selection

10 篇 core 的选择及结构特征见 `skill07_gold_selection.md`。选择不依赖文件名，覆盖既有 A/G 配对并补充短/长、图表、段落与章节结构差异。由于 source artifacts 的自动特征不能可靠证明“failure→adjustment→success”等科学内容，该覆盖项保持待人工确认。

## Human Gold/Adjudication Status

状态：`AWAITING_HUMAN_ADJUDICATION`。`skill07_gold_review.json` 为每篇使用稳定 `GOLD-Pxx`，要求审阅者建立 `GOLD-Pxx-Eyyy`，且模型 experiment ID 只能作为来源参考。需要填写对象、干预、trigger、condition、implementation、result、rationale、alternatives、evidence、rule/scope、provenance、ambiguity 与 reviewer notes。

人工队列自动剔除格式/语义等价项，只保留实验增删、对象/干预/结果/evidence 变化和歧义对齐。Source evidence 通过 paragraph anchors 与对应 clean document 定位；不伪造原文结论或 reviewer choice。

## Pilot Benchmark

`NOT_RUN_AWAITING_HUMAN_GOLD`。计划中的 2 papers × A/G × 2 repetitions 已在 CSV 中预留隔离槽位，但没有模型调用。原因不是 provenance 失败，而是当前无法执行独立质量判定；继续调用只会产生更多待裁决的 A/G 输出。

## 10-Paper Paired Benchmark

计划 10 × A/G × 3 = 60，完成 0。所有行显式标为 `NOT_RUN_AWAITING_HUMAN_GOLD`，没有把 Wave 1 的非重复历史运行伪装为 Wave 2 primary runs。

## Repeated-Run Stability

`NOT_MEASURED`。重复槽位、run/candidate/representation/cache 隔离合同已经生成并测试；待 gold 第一轮裁决后按 pilot → repetition 1 → repetitions 2/3 执行。

## Repair-Aware Performance

统一 telemetry 合同包含 prompt build、provider/CLI、first pass、validation、local/targeted/full repair、total wall、first-pass/final status、repair class/count、input chars/tokens 与 output tokens。不可观测项必须为 `UNKNOWN`。本轮没有运行，因此所有性能变化为 `NOT_MEASURED`。

## Quality vs Gold

A 和 G 均为 `AWAITING_HUMAN`。critical experiment/evidence recall、binding、trigger/action、result、rationale、rule scope、unsupported claims、hallucination 与 provenance 质量指标均不得推断。当前不存在可用于声明 G 非劣的 gold 分母。

## Concurrency 1/2/4

三层均 `NOT_MEASURED`。基础设施已有 bounded semaphore、有限 retry、failure isolation 测试；但按 staged stop rule，必须先建立有效质量 benchmark。并发只证明吞吐，不证明科学质量。

## A vs G Decision Matrix

| Dimension | A_BASELINE | G_SAFE_COMBINED | Gate |
|---|---|---|---|
| Critical experiment recall | AWAITING_HUMAN | AWAITING_HUMAN | HARD |
| Critical evidence recall | AWAITING_HUMAN | AWAITING_HUMAN | HARD |
| Biological binding accuracy | AWAITING_HUMAN | AWAITING_HUMAN | HARD |
| Trigger/action correctness | AWAITING_HUMAN | AWAITING_HUMAN | HARD |
| Result correctness | AWAITING_HUMAN | AWAITING_HUMAN | HARD |
| Unsupported claims | AWAITING_HUMAN | AWAITING_HUMAN | HARD |
| Provenance integrity | PASS after correction | PASS preflight | HARD |
| First-pass success | NOT_MEASURED | NOT_MEASURED | reliability |
| Full repair rate | NOT_MEASURED | NOT_MEASURED | reliability |
| Input tokens | NOT_MEASURED | NOT_MEASURED | performance |
| First-pass latency | NOT_MEASURED | NOT_MEASURED | performance |
| Total latency | NOT_MEASURED | NOT_MEASURED | performance |
| Run-to-run stability | NOT_MEASURED | NOT_MEASURED | reliability |
| Throughput c=1 | NOT_MEASURED | NOT_MEASURED | operational |
| Throughput c=2 | NOT_MEASURED | NOT_MEASURED | operational |
| Throughput c=4 | NOT_MEASURED | NOT_MEASURED | operational |

## Final G Decision

**HOLD**。这是命名明确的证据缺口，不是泛化的“需要更多研究”：必须完成 10 篇 source-grounded 人工 gold，优先裁决 19 个关键差异和 47 个歧义；随后才能运行 2-paper pilot 和第一轮 10-paper A/G。任何确认的新关键 G 回归立即触发 `REJECT`；无回归后才进行 repetitions 2/3 与 throughput。

## Shadow/Canary Plan if promoted

本轮未晋级，计划仅作为未来条件路径：baseline-default → isolated shadow → gold/reviewer gate → bounded canary → rollback review → possible production promotion。每阶段按 candidate/cache identity 隔离；回滚始终返回 A baseline。Wave 2 不切换生产默认。

## Remaining Risks

- 供应商内部 resolved model/revision 不可观测，必须持续标记 `UNKNOWN`。
- 语义签名匹配不能代替 source-grounded 人工裁决。
- Supplement/figure/table 的真实证据完整性仍取决于现有 clean document artifacts。
- Wave 1 性能结果未分离 first pass 与 repair，不能解释 token 减少但延迟增加的因果。
- 尚无重复稳定性及 c=1/2/4 受控吞吐证据。

## Deliverables and Self-check

- `skill07_wave2_results.json`
- `skill07_wave2_baseline_manifest.json`
- `skill07_semantic_alignment_report.json`
- `skill07_gold_selection.md`
- `skill07_gold_review.json`
- `skill07_A_vs_G_paired_benchmark.csv`
- `skill07_concurrency_benchmark.csv`
- `SKILL07_WAVE2_HUMAN_REVIEW_QUEUE.md`
- `tools/skill07_wave2.py`、`tools/run_skill07_wave2.py`
- `tests/paper_extraction/test_skill07_wave2.py`

最终自检：实际 runtime identity 已捕获；mismatch fail closed；历史 manifest 保留；秘密不序列化；ID 格式不再自动产生科学失败；真实 intervention/evidence 差异不被归一化；gold 独立于 A/G；pilot 未越过人工 gold 硬门；D/E/F 未产生 LLM 调用；最终决定恰为 `HOLD`；production default unchanged。

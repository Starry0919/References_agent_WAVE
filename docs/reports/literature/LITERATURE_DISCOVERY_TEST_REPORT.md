# Literature Discovery Test Report

## Commands and results

| Command | Result | Interpretation |
|---|---|---|
| `python -m pytest tests/literature_discovery -q` | 11 passed in 0.33s（最终） | 新核心逻辑通过 |
| `python -m pytest tests/literature_discovery tests/paper_extraction/test_unified_extraction.py tests/paper_extraction/test_pdf_identity_extraction.py tests/paper_extraction/test_pdf_parser_fallback.py tests/paper_extraction/test_markdown_cleaner.py -q` | 34 passed in 1.19s | handoff 邻接的获取/解析/清洗链通过 |
| `python -m pytest tests/literature_discovery tests/evidence_retrieval tests/server tests/paper_extraction -q` | 173 passed, 1 warning in 7.66s | 相关后端主路径无新增 regression |
| `python -m pytest --collect-only -q tests` | 673 tests collected | 主测试规模 |
| `python -m pytest -q` | 304s timeout，无最终结果 | 不记 PASS/FAIL；未得到失败栈 |
| `python -m pytest tests -q` | 304s timeout，无最终结果 | 同上；全量套件超出工具时间窗 |

warning 是 FastAPI TestClient 关于 `httpx`/`httpx2` 的既有弃用警告，与本轮代码无关。

## Coverage by behavior

- request normalization 与 K-12 derivative distinction；
- 六类 bounded query、query ID、rationale、source tracking；
- OpenAlex adapter normalization/abstract/provenance；
- Crossref 合法 select 参数回归；
- DOI exact 与保守题名 dedup；
- Tier 1/2 分层和 reason codes；
- review 不得成为 direct experimental evidence；
- 八类必需反例不进入 Tier 1；
- 5-hydroxytryptophan、indole 和 abstract-only 误判回归；
- source failure graceful degradation；
- invalid/HTML PDF rejection；
- acquisition idempotent reuse；
- handoff manifest 与现有 `build_request` 契约。

## Defects found during testing/benchmark

1. 初版用 `bytes.casefold()` 导致 PDF 校验异常；改为 `lower()`。
2. 初版把 `improved` 当实验指标，导致 pathway supporting paper 误进 Tier 1；已要求定量/发酵证据。
3. Crossref `select=subtype` 导致 live 400；已移除并回归测试。
4. 初版 handoff 的 `files` 是对象列表，而现有 workflow 要求路径字符串；已修正并调用真实 `build_request` 验证。
5. live spot check 暴露 biofilm/基础代谢和相邻产品 false positive；已收紧 title/product gate。

## Regression assessment

相关 173 项测试全部通过，没有观察到新增 regression。由于全量 673 项运行两次均超时，不能声称整个仓库测试全绿，也没有证据将 timeout 归因于本轮实现。

## Blocked/remaining tests

- 没有在 benchmark 中自动启动 MinerU+Skill07 的长耗时完整抽取；已有邻接集成测试和 handoff contract 验证。
- 尚未做 100/1000 candidate 容量测试、进程崩溃恢复或真实 API 限流演练。
- live metadata 的人工金标准尚不足以计算 Recall@K/nDCG；本轮只做 Top-20 spot check。

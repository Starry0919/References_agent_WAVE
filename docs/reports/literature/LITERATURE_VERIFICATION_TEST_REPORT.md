# Literature Verification Test Report

## Results

- `python -m pytest tests/literature_discovery tests/literature_verification -q`：16 passed。
- `python -m pytest tests/literature_discovery tests/literature_verification tests/paper_extraction tests/evidence_retrieval -q`：203 passed，1 个既有 FastAPI TestClient 弃用 warning，21.37s。

## Covered

Resolver：PMC priority、source dedup、Unpaywall CONFIG_REQUIRED、Semantic Scholar graceful failure。Acquisition：既有 invalid/HTML/corrupt PDF、idempotent reuse、handoff 测试继续覆盖。Identity：wrong metadata PDF 不可被当 verified。Verifier：exact K-12、explicit derivative pattern、unresolved E. coli、wrong/adjacent product、review、implemented vs future intervention、quantitative result、model/enzyme boundary。Gold：pending gate、confusion matrix 与 ranking metric basic path。

## Live classification

真实 API smoke 与 acquisition/shadow benchmark 不是 unit test；网络/rate limit 失败单独报告，不算生产 regression。

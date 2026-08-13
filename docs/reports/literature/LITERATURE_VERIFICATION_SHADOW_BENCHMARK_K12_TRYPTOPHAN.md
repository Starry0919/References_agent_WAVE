# Literature Verification Shadow Benchmark — K-12 / L-tryptophan

模式：`shadow_no_ddr_write`。输入上一轮 Top-20 metadata candidates；只有本地可用全文进入 verifier。

| Outcome | Count |
|---|---:|
| fulltext verified/supporting | 1 |
| downgraded/rejected with fulltext | 0 |
| DATA_REQUIRED（无已核验全文） | 19 |

唯一可验证全文为 `10.1007/s00449-021-02630-7`：metadata Tier 2；全文 judge 为 supporting/direct 边界中的可用工程证据（以机器 JSON 的具体 verdict 为准）。其余 19 篇保持 DATA_REQUIRED，不根据标题或摘要补齐。

| Paper group | Metadata | Fulltext | Change | Reason |
|---|---|---|---|---|
| `10.1007/s00449-021-02630-7` | Tier 2 | verified engineering verdict | verified | 有本地全文与可定位 host/product/intervention/result spans |
| 其余 Top-20 | Tier 2/3/background | DATA_REQUIRED | acquisition/data required | 没有已核验全文，未推测 |

机器制品 `literature_verification_shadow_benchmark_k12_tryptophan.json` 保留逐篇 metadata tier、fulltext verdict、change、reason 与全部 spans。当前样本不足以评价 promotion/downgrade 率；它证明 gate 会拒绝在无全文时伪造结论。

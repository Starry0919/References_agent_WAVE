# Literature Evidence Verification v1 Implementation Report

`harness/literature_verification/verifier.py` 是 Skill07/08 之前的 conservative gate。输入 candidate + PDF-derived text/clean document，输出 metadata assessment（原样保留）、document hash、publication classification、host/product/intervention/validation spans 和 Scientific Judge。

每个 span 含字符 start/end、quote、section 与 match。Host 区分 K12_EXACT、K12_DERIVATIVE_EXPLICIT、ECOLI_UNRESOLVED、NON_ECOLI；产品显式排除 5-HTP、serotonin、indole production、shikimate production。Future/proposed intervention 不算 implemented；review、model-only、enzyme-only 不得成为 direct evidence。

Direct 硬门：全文 host/lineage、目标产品、实际 intervention、定量/培养验证、可定位 span、非 review、非纯模型/体外酶。缺证据降级或 DATA_REQUIRED，不推测补齐。

Shadow 边界：verifier 回答“是否值得进入抽取链”；Skill07/08 继续回答进入后结构化 claim 与证据是否正确。`literature_verification_shadow_benchmark_k12_tryptophan.json` 明确 `shadow_no_ddr_write`，没有自动写 DDR。

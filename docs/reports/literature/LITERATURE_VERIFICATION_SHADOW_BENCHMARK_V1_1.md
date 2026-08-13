# Literature Verification Shadow Benchmark v1.1

`shadow_no_ddr_write`保持。当前可用PDF 5篇；fallback parser均可恢复文本/DOI，但缺section/table/figure结构，导致verifier多为MECHANISTIC/BACKGROUND边界。Top-20中无全文者继续DATA_REQUIRED，未以metadata补齐。

Parser→Verification Impact：结构退化会把实施/数值证据落入`other` section，无法满足IMPLEMENTED/measured硬门；这验证了canonical section provenance对judge稳定性的必要性。MinerU仍为PRIMARY，PyPDF fallback结果必须降级复核。

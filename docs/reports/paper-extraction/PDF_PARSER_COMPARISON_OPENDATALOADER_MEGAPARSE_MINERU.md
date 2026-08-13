# PDF Parser Comparison

| Parser | License/runtime | Structure/provenance | Benchmark | Decision |
|---|---|---|---|---|
| MinerU + Skill05/06 | Existing local runtime | Markdown, sections, figures, tables, references, clean JSON/maps | existing production path; not re-run expensively | PRIMARY unchanged |
| PyPDF/PyMuPDF fallback | existing dependency/local | page text; weak headings/tables/figures | 5 PDFs succeeded | FALLBACK |
| OpenDataLoader PDF | Apache-2.0 v2+; Java 11+/Python; local CPU; hybrid optional | JSON element type, page, bbox, headings/tables/images; Markdown | two pip installs exceeded 304s; unavailable | BENCHMARK_ONLY pending isolated install |
| MegaParse | Apache-2.0; Python≥3.11, Poppler, Tesseract; vision requires OpenAI/Anthropic | Markdown-oriented; structured output roadmap/in construction | not run: dependency/API boundary | STUDY_ONLY |

OpenDataLoader 源码/README显示 fast local Java mode具 XY-Cut++、element bbox/page和 batch API，每次 convert 会启动 JVM，宜批量调用；hybrid/OCR增加本地后端复杂度。它最可能改善 anchor，但未完成本机运行，不能评为 fallback。MegaParse包含 unstructured/vision 等后端，vision成本与不确定性不适合默认生产，且其 README 要求 API key、Poppler、Tesseract。

5篇 fallback benchmark：全部非空、DOI可恢复；但 canonical section均退化为一个 Document，tables/figures均为0，验证结果受结构缺失影响。详见 `PDF_PARSER_BENCHMARK_RESULTS.json`。结论：不切换 MinerU；OpenDataLoader在隔离环境安装成功后做 SHADOW PARSER；MegaParse仅研究。

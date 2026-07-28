# Skill02 Literature Retrieval

多来源文献候选检索引擎。只收集数据库或人工上传入口返回的事实，不验证 DOI、不下载 PDF、不分析实验质量。

## Supported adapters

- PubMed、Crossref、Europe PMC：可执行 HTTP 适配器。
- Google Scholar：显式 `unavailable` 占位适配器。
- Web of Science：未配置时返回 `not_configured`。
- CNKI：未配置时返回 `not_available`。
- ManualUpload：兼容人工提供的候选元数据，并明确记录来源。

## Contract

- 输入：Skill01 的 `research_intent`，可选 `retrieval_strategy`、sources、limit 和 manual_candidates。
- 输出：统一 Schema 的 `candidates`；匹配、排序和检索上下文存入 `candidate_annotations`。
- 去重：DOI > PMID > 规范化标题相似度。
- 排序：默认确定性字段匹配；配置 `KIMI_API_KEY` 后可启用 Kimi-K3，仅允许扩展 query 和评分，不允许产生论文元数据。
- 错误：RET001–RET005 映射统一 `EDX-*`；单源失败降级，全部失败才进入人工评审。
- 日志：默认写入模块 `logs/skill02_literature_retrieval.jsonl`。

运行测试：`python -m unittest discover -s tests -v`

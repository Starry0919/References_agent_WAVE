# Schema change proposal

状态：待确认；未修改 `framework/`。

当前 `LiteratureCandidate` 缺少 retrieval_time、query_used、逐项匹配、relevance_score、ranking_reason 和 `citation_validation_status=pending`。建议在下一 minor 版本新增 `literatureCandidateAnnotation`，并为 citation validation 增加 `pending`。

当前实现保持核心候选严格兼容统一 Schema：校验状态使用现有 `unknown`，扩展字段放在输出的 `candidate_annotations[paper_id]`。


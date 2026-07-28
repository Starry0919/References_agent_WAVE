# Schema change proposal

状态：待确认；未修改 `framework/`。

统一 `citation_validation.status` 当前只允许 `valid/invalid/conflict/unknown`，无法直接表达 `verified/mismatch/not_found/retrying/failed`、最终决定、规范元数据、逐字段匹配和审计链。

建议下一 minor 版本增加 `CitationValidationResult`，并保留现有简化状态作为 gate 索引。当前实现将完整对象放入 `validation_results`，核心候选继续严格使用现有状态。


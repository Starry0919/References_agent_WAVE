# Schema change proposal

状态：待确认；未修改 `framework/`。

统一 Schema 没有 CleanDocumentArtifact，无法表达 Markdown+JSON 双制品、段落 ID、Figure/Table/Citation 索引、修改 diff 和清洗质量。

建议新增 `CleanDocumentArtifact`，引用现有 ArtifactRef，并定义 cleaning_history。当前实现通过 Skill06 自有接口提供完整对象。


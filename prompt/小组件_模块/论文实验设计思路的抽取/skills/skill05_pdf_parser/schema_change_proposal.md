# Schema change proposal

状态：待确认；未修改 `framework/`。

统一 `Document` 目前只包含 artifacts、parse_status 和 section_index，无法表达 Markdown 内容、Figure/Table/Reference/Supplement map、解析质量和尝试审计。

建议下一 minor 版本新增 `ScientificDocumentArtifact`，内部引用现有 `Document` 和 `ArtifactRef`。当前实现保持 `document` 兼容，完整信息放在 `document_artifact`。


# Schema change proposal

状态：待确认；未修改 `framework/`。

统一 `ArtifactRef` 缺少 Paper Identity、file_name/path/size、source_type/source_url/download_time、checksum_algorithm、处理状态和下载审计。

建议新增 `PaperArtifact`，内部引用现有 `ArtifactRef`，并规定 source_type 与 processing_status 枚举。当前实现的 `artifacts` 保持统一 Schema 兼容，完整信息位于 `paper_artifacts`。


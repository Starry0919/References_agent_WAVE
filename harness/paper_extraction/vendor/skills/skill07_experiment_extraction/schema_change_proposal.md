# Schema change proposal

状态：待确认；未修改 `framework/`。

统一 `experimentFields` 缺少 organism、control purpose、workflow、variable model、design logic 和 conflict 表达；且 Skill07 阶段尚未生成最终页码级 EvidenceRecord。

建议：

- 新增 `BiologicalSystem`、`ExperimentalDesignExtension` 和 `FieldConflict`；
- 支持 provisional evidence ID，由 Skill08 解析为最终 EvidenceRecord；
- 保留现有 16 个核心字段不变。

当前实现通过 Skill07 自有输出承载扩展，核心 `fields` 继续兼容统一 Schema。


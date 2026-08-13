# Schema change proposal

状态：待确认；未修改 `framework/`。

统一 `EvidenceRecord` 可表达核心证据，但缺少 evidence_type、检索尝试审计和 extension knowledge unit 绑定。建议新增 `EvidenceBindingAudit` 与 `EvidenceLinkedExtension`。

当前实现保持 `literature_experiment` 严格兼容；扩展证据、coverage 和 binding_audit 放在 Skill08 自有输出。


# Skills 工程约定

本目录只包含 Skill1–Skill13 的规格、接口契约和测试占位，不包含实现逻辑。

所有 Skill 必须遵循：

- `../framework/unified-schema.json`
- `../framework/error-codes.md`
- `../framework/README.md` 中的统一调用/返回信封、日志、溯源和人工评审规范

接口状态统一为：`succeeded`、`succeeded_with_warnings`、`needs_review`、`retryable_failure`、`terminal_failure`、`cancelled`。


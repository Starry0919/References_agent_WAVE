# Schema change proposal: Research Intent metadata

状态：待确认；本提案未修改 `framework/`。

## Gap

当前统一 `researchIntent` 将 organism、strain、phenotype 和 engineering_objective 定义为标量，将 keywords/criteria 定义为数组；无法原生表达每字段的 source、confidence 和 `needs_clarification` 状态，也未定义 time range、engineering method 和 literature quality requirement。

## Proposed compatible direction

下一次统一 Schema minor 版本可新增：

- `researchIntentField`：value/source/confidence/status
- `literatureSearchSpecification`
- `timeRange`（explicit/relative/default_policy）
- `searchKeywordGroups`
- 状态 `needs_clarification`

为避免静默破坏，当前 Skill01：

1. 原样输出兼容的 `research_intent`；
2. 在 Skill 自有接口输出 `field_metadata`；
3. 在 `retrieval_strategy.search_specification` 暂存新增结构。

待批准统一 Schema 变更后再提供显式迁移器，不覆盖已有记录。

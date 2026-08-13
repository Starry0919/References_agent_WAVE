# Skill13：科研决策界面适配

将 Skill08–12 输出转换为 React/Agent UI 可直接消费的只读 JSON。该层不重新总结、分析或修改科研内容。

## 展示层级

1. `summary_view`：目标、策略、K-12 适配、可信度和治理状态。
2. `step_cards`：默认折叠的简洁步骤。
3. `detail_panels`：What、三路 Why、How、Evidence、Risk。

同时提供明确的 `collapsed_view` 与 `expanded_view`。完整输入保存在 expanded source payload，确保展示裁剪不造成数据损失。

## 来源与治理

文献内容显示为 `literature`，AI 内容显示为 `AI_generated`。未标记内容返回 UI003 并阻断转换。Skill13 只显示治理状态；审批操作仍由 Skill12 处理。

支持 `zh` 和 `en`。缺失 Evidence 显示 `unknown` 并产生 UI002 警告。

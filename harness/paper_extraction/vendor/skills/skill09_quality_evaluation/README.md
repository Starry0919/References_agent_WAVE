# Skill09：实验设计知识质量评价

对 Skill07/Skill08 产生的实验设计知识进行确定性、可解释评价。它评价的是“当前抽取知识是否完整、可追溯和足以复现”，不评价论文创新性、期刊价值、科学重要性或实验结果真假，也不评价 K12 迁移风险。

## 接口

输入必须包含 `skill08_output`；可选 `skill07_output` 和 `scoring_policy_version`。输出包含符合统一模式的 `quality_evaluation`、详细 `evaluation_report` 和逐项 `score_details`。详细扩展结构见 `schema_change_proposal.md`。

## 评分

总分为：字段完整性 25% + 证据质量 25% + 实验逻辑 15% + 可复现性 15% + 方法描述 10% + 工作流 10%。变量定义单独报告但不重复计入总分。所有分数均为 0–100，必须附理由。

## 依赖与约束

- 遵循 `framework/unified-schema.json` 和统一错误、日志、溯源及人工复核约定。
- 仅使用输入中存在的信息；`unknown` 不得被推断为已报告。
- `reported` 必须有证据；大量 unknown 时证据等级不能为 A/B。
- 缺少 hypothesis 必须降低逻辑分。

## 错误与日志

`EVAL001` 输入缺失；`EVAL002` 证据缺失（部分评价）；`EVAL003` 无法评分；`EVAL004` 数据冲突。JSONL 日志记录 paper_id、评价字段数、证据覆盖、逻辑/工作流/总分、状态和错误。

## 测试

覆盖完整案例、证据缺失、缺少假设、unknown 处理、缺少重复、风险检测、无效输入与恢复。运行：`python -m unittest discover -s tests -p "test_*.py"`。

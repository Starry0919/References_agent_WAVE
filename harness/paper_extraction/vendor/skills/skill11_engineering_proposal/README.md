# Skill11：证据驱动 DBTL 工程计划

把 Skill10 的无排名候选空间转换为结构化 DBTL 计划。它不重新比较论文、不重新判断 K-12 适配，也不创造生物学知识。

## 双轨输出

- Track A：每个候选对应一个 `reported_in_literature` 计划，所有实际内容必须携带证据。
- Track B：只有同一目标簇内至少两个有证据候选时，才可生成 `ai_generated_proposal` Level 2 组合验证建议。它必须包含 reasoning、uncertainty、证据和人工审批。

每一步包含 What、Why、How、输入、输出、证据、验证检查点和风险。未知参数以 `unknown` 表示。

## DBTL 与治理

计划必须包含 Design、Build、Test、Learn。Learn 仅描述数据反馈、计划更新和下一轮输入，不声称发现机制。Level 2/3 AI 建议及高风险、不完整计划必须人工审核。

错误码：`PLAN001` 输入不足；`PLAN002` 无证据建议被删除；`PLAN003` 无法解释的 AI 建议被拒绝；`PLAN004` DBTL 不完整。日志采用 JSONL。

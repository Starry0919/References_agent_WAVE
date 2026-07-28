# Skill01 Requirement Parser

把自然语言科研需求转换为统一 `ResearchIntent` 和可执行检索策略。当前实现是确定性的规则解析器，不调用 LLM，也不执行检索。

## Contract

- **Input schema**：`{"user_request": non-empty string, "constraints": object?}`。
- **Output schema**：`research_intent` 复用统一 Schema；`field_metadata` 为每个字段保存 value/source/confidence/status；`retrieval_strategy` 提供概念组、时间范围、质量要求、通用布尔查询和推荐数据源。
- **Dependencies**：仅 Python 标准库；统一 Schema 和统一错误码。
- **Self-check**：ResearchIntent 类型完整；unknown 字段不带推断值；元数据与字段值一致；查询词只来自用户输入或显式规范化映射。
- **Logging**：通过可注入 logger 输出统一结构化事件；保存输入/输出哈希、Skill 版本、状态和耗时，不写原始请求。
- **Error handling**：无效输入返回 `EDX-VAL-001`；内部异常返回 `EDX-SYS-001`；所有结果使用统一返回信封。
- **Human review**：目标和生物对象均缺失、或纳入/排除条件冲突时返回 `needs_review`。

## Usage

```python
from implementation import RequirementParser

result = RequirementParser().execute({
    "user_request": "检索通过代谢工程提高 E. coli K-12 琥珀酸产量的实验研究"
})
```

`research_intent` 和 `retrieval_strategy` 可直接传入 Skill02。统一 Schema 的扩展建议见 `SCHEMA_CHANGE_PROPOSAL.md`。


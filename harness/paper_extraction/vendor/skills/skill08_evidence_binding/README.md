# Skill08 Evidence Provenance Binding

把 Skill07 的 provisional evidence ID 绑定为最终、可审计的 EvidenceRecord，不重新抽取或评价实验方案。

## Binding strategy

1. 精确解析 `candidate:{paragraph_id}`。
2. 若失效，在全文段落中按值检索。
3. 最后检索 Figure/Table/Supplement。

每轮和失败原因均记录。reported 字段必须有支持其值的原文；否则降级 unknown。页码不可得时为 null，禁止猜测。

EvidenceRecord 包含 paper、artifact SHA-256、section/paragraph/figure/table、最小充分 quote、quote SHA-256、抽取器与版本。Workflow、variables 和 design logic 也绑定来源；冲突独立保存。

运行测试：`python -m unittest discover -s tests -v`


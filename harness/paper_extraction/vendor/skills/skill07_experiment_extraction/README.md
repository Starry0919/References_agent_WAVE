# Skill07 Experimental Design Extraction

从 Skill06 Clean JSON/Markdown 中恢复论文作者实际报告的实验设计。当前实现为保守的规则与上下文抽取，不生成 AI 实验方案。

## Evidence and status

- `reported`：值来自明确段落，并带 `candidate:{paragraph_id}` provisional evidence ID。
- `unknown`：值为 null、证据为空；不会依据 E. coli、knockout、LC-MS 等常识补参数。
- `inferred`：核心字段默认禁用；只允许在 policy 明确开启时使用，且必须引用来源与理由。
- Skill08 将 provisional evidence ID 绑定到页、段落、图、表的最终 EvidenceRecord。

Methods、Supplementary Methods、Results、Figure/Table legend 按优先级检索。冲突不静默解决，而是进入 `conflicts` 和人工评审。

运行测试：`python -m unittest discover -s tests -v`


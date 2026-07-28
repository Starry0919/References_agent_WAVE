# Skill03 Citation Validation Gate

通过 Crossref、PubMed、Europe PMC 等外部事实源验证候选论文身份。只有 `accepted_candidates` 可以进入 Skill04。

## Rules

- 验证 DOI 格式和存在性。
- 比较标题、第一作者及作者重叠、期刊和年份（允许 ±1 年）。
- 最多三次数据库尝试：原 DOI、标题+第一作者、标题关键词+期刊。
- 数据库未返回元数据时绝不接受。
- LLM 不参与 DOI 或书目信息生成。
- 单源故障会切换其他数据源；全部不可用时进入人工评审。

完整验证过程保存在 `validation_results`；统一候选的 `citation_validation` 映射为 valid/invalid/conflict/unknown。

运行测试：`python -m unittest discover -s tests -v`


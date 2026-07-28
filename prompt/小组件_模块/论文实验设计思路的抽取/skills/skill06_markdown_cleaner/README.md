# Skill06 Scientific Markdown Cleaning

把 Skill05 的机器解析 Markdown 规范化为 Markdown + JSON 双制品。只修复噪声和结构，不总结、推断或改写科学内容。

## Safety

- 页眉页脚仅按页边界和保守规则删除。
- 标题修复只调整 `#` 层级，不改标题文字。
- 表格修复只补 Markdown 分隔符、统一列数；无法确定时保留原文并告警。
- 数字、单位、温度、时间、浓度、转速、OD、基因符号、Figure/Table 编号和 citations 均受保护。
- 每项变化记录 original、cleaned、位置、类型和原因。
- 受保护 token 前后不一致时返回 `CLEAN004`，不发布清洗制品。

输出 `clean_document.md` 与 `clean_document.json`，可直接供 Skill07 使用。

运行测试：`python -m unittest discover -s tests -v`


# Skill05 Scientific PDF Structure Reconstruction

将 Skill04 的 verified Paper Artifact 转换为结构化 Markdown、章节/图/表/引用/Supplement 索引和质量报告，不清洗、总结或改写论文内容。

## MinerU

- 已适配 `D:\MinerU\.venv\Scripts\mineru.exe` 3.4.4。
- 默认 `pipeline`，离线本地模型。
- 显式 `mode=hybrid` 时先用 `hybrid-engine --effort medium`；失败后降级 pipeline。
- 第三次尝试可用 PyMuPDF；未安装时明确记录不可用。
- 解析输出保存到模块 `document_artifacts/`，不写回或修改原始 PDF。

## Gate

输入必须是 Skill04 `processing_status=verified` 的 Paper Artifact，且文件 SHA-256 必须与记录一致。输出中的 `document` 兼容统一 Schema，完整结构位于 `document_artifact`。

运行测试：`python -m unittest discover -s tests -v`


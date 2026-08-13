# 论文实验设计抽取部分交付说明

## 给老师的简要说明

本系统对所有论文使用同一套固定的抽取代码与提示词。每篇论文变化的是输入全文、命中的证据位置、字段值、冲突和未知项，并不会为每篇论文临时生成一套新代码或新 system prompt。

当前生产链路为：

```text
service.py
  -> opus_extractor.py
  -> prompts/experimental_design_system_prompt.md
  -> SKILL.md（详细领域规则）
  -> 单篇论文结构化 JSON
```

## 文件职责

- `opus_extractor.py`：生产环境实际使用的模型抽取执行器，包括文献载入、提示词组装、模型调用、结果解析、缓存、重试、输出归一化与 provenance。
- `experimental_design_system_prompt.md`：独立、固定、可版本管理的 system prompt。
- `SKILL.md`：更详细的领域规则和完整 13 阶段流程说明；抽取调用只执行其中的 Skill07。
- `service.py`：主 Agent 如何把上传 PDF、DOI 和自动检索三种入口统一接到同一个抽取器。

仓库中另有 `vendor/skills/skill07_experiment_extraction/`，它是早期的确定性规则抽取器。当前生产服务没有调用该规则版，因此不应把它与现在的模型抽取主链路混为一谈。

## 固定项与逐篇变化项

固定项：抽取器代码、system prompt、领域技能说明、JSON Schema、模型配置和质量规则。

逐篇变化项：清洗后的论文全文、论文元数据、段落/图/表定位信息、抽取值、证据 ID、置信度、冲突、未知字段和最终结果哈希。

## 复现提示

默认抽取模型由环境变量 `PAPER_EXTRACTION_MODEL` 控制；未配置时使用代码中的默认模型。模型传输由 Poe Code CLI 完成，因此仅复制代码并不能在另一台机器上直接运行，还需要 Python 项目依赖、Node.js、Poe Code CLI 与对应 API 配置。交付材料的主要目的，是供方法审阅、版本归档与后续工程复用。

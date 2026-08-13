# WAVE Agent Platform 交付说明

WAVE（Westlake AI Virtual Cell）是面向合成生物工程设计的持久化、可追溯、人工治理 DBTL Agent 系统。

## 核心能力

- Agent 编排、工具调用和持久会话
- Design–Build–Test–Learn 工作流与状态门控
- 文献实验设计抽取、DDR、Evidence 和 Rule Distillation
- Bottleneck Diagnosis、Engineering Design 与 Virtual Cell
- Scientific Evaluation、Critic、版本账本和人工审批
- React/TypeScript 前端与 FastAPI 后端

## 主要入口

- 后端入口：`main.py`
- 后端核心：`harness/`
- DBTL 工作流：`workflows/`
- 知识资产：`knowledge/`
- 前端：`frontend/`
- 测试：`tests/`
- 完整运行说明：`README.md`

本文件夹最初是从主工程复制出的独立代码包。2026-08-11 已完成完整归档整合：活动代码仍保持上述根目录结构，其他研发 prompt、参考资料、历史状态快照和独立工程分别保存在 `project_assets/` 与 `archive/`，Git 历史保存在本目录 `.git/`。详见 `docs/CONSOLIDATION_REPORT_2026-08-11.md`。

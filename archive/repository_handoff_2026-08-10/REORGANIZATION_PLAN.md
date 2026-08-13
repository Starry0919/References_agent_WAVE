# Reorganization Plan

## 决策摘要

本次采取 documentation-first 的零迁移方案。原因是主工程已有模块化结构，移动收益小于路径破坏风险，并且 Git 工作区在任务开始前并不干净。

## 评估过的移动

### Proposal 1

Original:

`agent/agent-harness/agent-harness/harness/api/`

Target:

`backend/api/`

Reason:

使 API 在仓库根目录更显眼。

Risk:

高。需要修改 Python package/import、服务入口、测试和资源路径。本次不执行。

### Proposal 2

Original:

`agent/agent-harness/agent-harness/frontend/`

Target:

`frontend/`

Reason:

缩短前端路径。

Risk:

中高。涉及启动脚本、后端静态资源路径、构建输出和开发文档。本次不执行。

### Proposal 3

Original:

`agent/vEcoli/`

Target:

`vEcoli/`

Reason:

让虚拟细胞工程成为根目录一级模块。

Risk:

高。该目录是独立工程并含自身版本控制与环境约定。本次不执行。

### Proposal 4

Original:

根目录的 `*_state/` 与 `*_result.json`

Target:

`data/runs/`

Reason:

集中阶段结果。

Risk:

中。可能被复现脚本、研究记录或人工流程按原路径引用。本次不执行。

## 实际计划

- 保持所有既有文件和目录原位。
- 新增审计、总览、架构、环境、整理日志、交接和最终报告。
- 不修改 import、配置、启动脚本或业务代码。
- 用后端导入、pytest 收集和前端生产构建验证当前工程基线。

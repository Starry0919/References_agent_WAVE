# WAVE Agent Platform Project Structure

## 1. 项目简介

WAVE（Westlake AI Virtual Cell）是一个面向 AI 辅助合成生物学工程设计的 **Persistent, Traceable, Human-Governed DBTL Engineering System**。

本仓库同时保存主 Agent 平台、实验设计抽取组件、虚拟细胞参考工程、知识与提示词资产，以及阶段性运行结果。为保证现有 import、配置路径、脚本和历史证据可复现，本次交付不改变现有代码文件的位置或内容。

## 2. 当前仓库结构

```text
References_agent_WAVE/
├── README.md                         # 仓库简要说明
├── CHANGELOG.md                      # 变更记录
├── PROJECT_STRUCTURE.md              # 本结构说明
├── HANDOFF_NOTES.md                  # 交接说明与完整性声明
├── agent/
│   ├── agent-harness/
│   │   └── agent-harness/            # WAVE Agent Platform 主工程
│   │       ├── harness/              # 后端核心与 API
│   │       ├── workflows/            # DBTL 工作流定义
│   │       ├── knowledge/            # 知识资产
│   │       ├── frontend/             # Web 前端
│   │       ├── tests/                # 自动化测试
│   │       ├── docs/                 # 主工程文档
│   │       ├── scripts/              # 辅助脚本
│   │       ├── tools/                # 工具实现
│   │       ├── workspace/            # 工作区数据
│   │       ├── workflow_runs/        # 工作流运行记录
│   │       ├── main.py               # 后端入口
│   │       └── README.md             # 主工程运行说明
│   ├── vEcoli/                       # 虚拟细胞参考/仿真工程
│   ├── prompt/                       # Agent 相关提示词
│   └── 初步使用_help/                # 使用帮助
├── prompt/                            # 设计文档、提示词与实验设计抽取组件
├── reference/                         # 论文、工具和参考资料
├── output/                            # 阶段性输出
├── *_state/                           # 可复现运行状态快照
├── *_result.json                      # 阶段性运行结果
└── test/                              # 仓库级测试预留目录
```

## 3. 核心模块

### Backend

主后端位于 `agent/agent-harness/agent-harness/`。

```text
harness/
├── api/                       # HTTP / WebSocket API
├── orchestrator/              # Agent 编排与任务协调
├── workflow/                  # 工作流运行机制
├── memory/                    # 持久记忆与项目上下文
├── evidence_retrieval/        # 证据检索
├── knowledge_distillation/    # 知识与规则蒸馏
├── paper_extraction/          # 论文实验设计提取
├── engineering_design/        # 工程设计生成与决策
├── scientific_evaluation/     # 科学评价与治理
├── evaluation/                # 通用评价逻辑
├── diagnosis/                 # 瓶颈诊断
├── experiments/               # 实验记录
├── projects/                  # 项目管理
├── cell_state/                # 细胞状态表达
└── virtual_cell/              # 虚拟细胞集成
```

顶层 `workflows/` 保存 DBTL 及相关业务工作流，`knowledge/` 保存知识资产，数据库与工作区状态保留在主工程根目录及 `workspace/` 中。

### Frontend

前端位于 `agent/agent-harness/agent-harness/frontend/`，源码在 `frontend/src/`，由 Vite/TypeScript 构建。页面、组件、API 调用和可视化实现均以该目录当前代码为准。

### Knowledge / Evidence / Skills

- 知识：`agent/agent-harness/agent-harness/knowledge/`
- 证据检索：`agent/agent-harness/agent-harness/harness/evidence_retrieval/`
- 规则与知识蒸馏：`agent/agent-harness/agent-harness/harness/knowledge_distillation/`
- 实验设计抽取：`agent/agent-harness/agent-harness/harness/paper_extraction/`
- 科学评价：`agent/agent-harness/agent-harness/harness/scientific_evaluation/`
- 设计资料与独立组件：`prompt/小组件_模块/论文实验设计思路的抽取/`

### Evaluation and Tests

- 后端评价：`harness/evaluation/`、`harness/evaluation_metrics/`、`harness/scientific_evaluation/`
- 测试：`agent/agent-harness/agent-harness/tests/`
- Golden set：`agent/agent-harness/agent-harness/harness/golden_set/`

## 4. 运行方式

请以主工程说明 `agent/agent-harness/agent-harness/README.md` 为准。主入口为 `agent/agent-harness/agent-harness/main.py`；前端依赖与命令定义在 `agent/agent-harness/agent-harness/frontend/package.json`。

运行前应在本地配置环境变量，避免将 `.env` 中的本地凭据复制到外部环境。

## 5. 结构设计说明

当前目录包含多个具有自身依赖和路径约定的工程。若仅移动文件而不修改 import、配置和脚本，主平台与参考工程可能无法运行。因此本次以文档化模块边界完成安全整理，不进行机械式目录迁移。后续若要统一为全新的 `backend/`、`frontend/`、`data/`、`skills/` 布局，应作为独立重构任务执行，并配套修改路径与完整回归测试。

# Current Repository Analysis

审计日期：2026-08-10

## 1. 当前目录结构

```text
References_agent_WAVE/
├── agent/
│   ├── agent-harness/agent-harness/   # WAVE 主平台
│   │   ├── harness/                    # 后端领域模块与 API
│   │   ├── workflows/                  # Agent/DBTL 工作流
│   │   ├── knowledge/                  # DDR 与知识资产
│   │   ├── frontend/                   # React/Vite 前端
│   │   ├── tests/                      # 后端测试
│   │   ├── docs/                       # 主工程规格与文档
│   │   ├── tools/                      # 外部工具
│   │   ├── scripts/                    # 运行辅助脚本
│   │   ├── workspace/                  # 持久化工作区
│   │   ├── workflow_runs/              # 工作流运行记录
│   │   └── main.py                     # 服务入口
│   ├── vEcoli/                         # 独立虚拟细胞参考工程
│   ├── prompt/                         # Agent 提示词
│   └── 初步使用_help/                  # 使用资料
├── prompt/                             # 设计文档、提示词、实验设计抽取组件
├── reference/                          # 论文和第三方参考工具
├── output/                             # 阶段输出
├── *_state/                            # 运行状态快照
├── *_result.json                       # 运行结果
├── README.md
└── CHANGELOG.md
```

## 2. 模块识别

### Agent 核心

- 编排：`harness/orchestrator/`
- 工作流控制与规划：`harness/workflow/`、`workflows/`
- 推理与生成：`harness/llm_generation/`、工作流阶段实现
- 工具调用：`harness/tools/`、顶层 `tools/`
- 持久记忆：`harness/memory/`、`harness/projects/`

### Knowledge 系统

- DDR/知识库：`knowledge/`
- Evidence：`harness/evidence_retrieval/`
- Rules：`harness/knowledge_distillation/` 及各 workflow gate
- Literature extraction：`harness/paper_extraction/`

### Backend

- API：`harness/api/` 与 `harness/server.py`
- Services：各领域目录中的 service/controller/loop 实现
- Database：项目账本、工作区数据库与各模块 repository/store 实现

### Frontend

- React/TypeScript 源码：`frontend/src/`
- 页面、组件、API 调用和可视化均在该源码树中
- Vite 构建配置：`frontend/vite.config.ts`

### Experimental Design

- 论文抽取：`harness/paper_extraction/`
- 工程设计：`harness/engineering_design/`
- 科学评审：`harness/scientific_evaluation/`
- 独立研发组件：`prompt/小组件_模块/论文实验设计思路的抽取/`

### Tests

- 后端测试：`tests/`，本次可收集 548 项
- 前端测试入口：`frontend/package.json` 中的 `vitest run`

## 3. 审计结论

主工程内部已经形成清晰的领域模块边界。将它机械迁移到新的 `backend/` 层会同时影响 Python import、资源定位、数据库路径、脚本、测试与前端代理配置。当前工作区还存在审计前就已有的修改、删除标记和未跟踪文件。基于“优先保证可运行”和“不覆盖已有修改”，本次不迁移现有代码，只通过交付文档建立清晰导航。

## 4. 可清理但未删除的内容

发现虚拟环境、`node_modules`、构建产物、缓存、日志和数据库 WAL/SHM 文件。这些均未自动删除，交付负责人应先确认离线运行与历史复现需求。

# WAVE Agent Platform Handoff Notes

## 交付范围

本次交付整理遵循“代码不动，只整理，让接收者能够快速看懂”的原则。已完成仓库盘点和模块说明；没有移动、重命名、删除或修改任何既有代码及配置文件。

当前版本已具备 Agent 编排、DBTL 项目账本、知识与证据、诊断、工程设计、虚拟细胞、科学评审、人工治理和前端展示模块。本次验证确认后端核心可导入、548 项测试可收集、前端生产构建成功；全量测试在 120 秒工具上限内未完成，建议交付机器延长时间复跑。

## 主要入口

- 主平台：`agent/agent-harness/agent-harness/`
- 后端入口：`agent/agent-harness/agent-harness/main.py`
- 后端核心：`agent/agent-harness/agent-harness/harness/`
- 工作流：`agent/agent-harness/agent-harness/workflows/`
- 前端：`agent/agent-harness/agent-harness/frontend/`
- 主工程说明：`agent/agent-harness/agent-harness/README.md`
- 实验设计抽取资料与组件：`prompt/小组件_模块/论文实验设计思路的抽取/`
- 虚拟细胞参考工程：`agent/vEcoli/`

## 本次变更

### MOVE

无。现有模块依赖相对路径、import、配置和运行脚本；在禁止修改代码的约束下移动会造成运行风险。

### RENAME

无。

### ADD

- `PROJECT_STRUCTURE.md`
- `HANDOFF_NOTES.md`

## 当前工作区注意事项

执行整理前，Git 工作区已经存在未提交的修改、删除标记和未跟踪文件。本次没有覆盖或回退这些用户变更。

仓库还包含以下本地或生成型内容，交付前可由项目负责人确认后另行处理：

- Python 虚拟环境：`.venv/`、`.venv_win/`
- Node 依赖与构建产物：`node_modules/`、`dist/`、`.next/`
- 缓存：`__pycache__/`、`.pytest_cache/`
- 日志：`*_stdout.log`、`*_stderr.log`
- 数据库临时文件：`*.db-shm`、`*.db-wal`
- 嵌套备份或版本控制目录：`.git-backup/`、`agent/vEcoli/.git/`

上述内容没有自动删除。若通过移动硬盘交付，建议先确认哪些运行环境和结果快照必须随包保留，再制作副本进行清理。

## 安全与复现提醒

- 主工程目录中存在 `.env`。对外移交前请人工检查其中是否含 API Key、Token、密码或内网地址。
- 运行结果 JSON、数据库和工作流记录可能包含研究过程数据，交付范围应由项目负责人确认。
- `reference/` 中包含第三方资料或工具副本，分发前应确认许可证和共享权限。

## 完整性声明

```text
Code modification: NONE
Code deletion: NONE
Logic change: NONE
Only folder organization: NO (documentation-only, because safe moves were not possible without code changes)
Existing file relocation: NONE
New handoff documentation: YES
```

## 未来开发建议

- 首先维护证据、状态机和人工 gate 的语义稳定性，再扩展模型能力。
- 新增底盘或模型适配器时同步增加适用域、失败路径与 benchmark。
- 若未来要改为根目录 `backend/frontend` 布局，请在独立分支完成路径迁移和完整回归测试，不要与业务功能开发混合。

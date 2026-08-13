# WAVE Environment

## 1. 版本要求与本次验证环境

- Python：项目要求 3.10+；本次现有 Windows 虚拟环境为 3.12.10
- Node.js：本次为 24.16.0
- npm：本次为 11.13.0
- 后端：FastAPI、Uvicorn、Pydantic、SQLAlchemy、OpenAI-compatible client 等
- 前端：React 18、TypeScript、Vite、Vitest、Recharts 等

依赖的权威清单位于：

- `agent/agent-harness/agent-harness/pyproject.toml`
- `agent/agent-harness/agent-harness/requirements.txt`
- `agent/agent-harness/agent-harness/frontend/package.json`

## 2. 后端安装与启动

在 `agent/agent-harness/agent-harness/` 中创建并激活 Python 3.10+ 虚拟环境，安装项目依赖，然后复制 `.env.example` 为 `.env` 并填写所选模型供应商配置。

```bash
python main.py
```

可按主工程 README 使用 `--host`、`--port`、`--reload`。

## 3. 前端安装与启动

在 `agent/agent-harness/agent-harness/frontend/` 中执行：

```bash
npm install
npm run dev
```

生产构建：

```bash
npm run build
```

## 4. 数据库与持久化

项目使用 SQLite 项目账本和工作区/运行记录。数据库、WAL/SHM 与工作流目录可能包含研究状态；复制、清理或重置前应先备份并确认交付范围。

## 5. 配置说明

`.env.example` 提供基础变量示例。主工程 README 还说明 `LLM_PROVIDER`、模型名、base URL、API key、最大步骤和工具超时等配置。不要把真实密钥写入交付文档或公开仓库。

## 6. 验证命令

```bash
python -c "import main; import harness"
python -m pytest --collect-only -q
python -m pytest -q
cd frontend && npm run build
```

本次全量 pytest 在自动化命令的 120 秒限制内未完成，不能据此判定失败；建议在交付机器上给予更长时间重新运行。

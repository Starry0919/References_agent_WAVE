# Handoff Notes

> 2026-08-11 consolidation update: this directory is now the repository root. The research prompts, references, standalone vEcoli project, historical results, former runtime state, and Git history that were excluded from the original copy have been preserved under `project_assets/`, `archive/`, and `.git/`. See `docs/CONSOLIDATION_REPORT_2026-08-11.md`. The original exclusion list below describes the 2026-08-10 copy baseline only.

## 本交付包包含

- WAVE 主平台后端源码
- 前端源码及依赖清单
- 知识、工作流、工具和必要运行资产
- 内置 Poe Code CLI（`.poe-code-cli/`），供实验设计抽取与知识蒸馏调用
- 自动化测试
- 项目规格与交付说明

## 原始复制包曾排除（现已归档或重新生成）

- 主工程之外的 prompt、reference、vEcoli 和阶段结果
- `.env` 真实环境变量文件
- Python 虚拟环境
- `node_modules`、前端构建产物和缓存
- 日志、SQLite 运行数据库、WAL/SHM
- 工作流运行记录、workspace 数据和论文解析中间产物

## 环境与启动

要求 Python 3.10+。在本目录创建虚拟环境并安装 `requirements.txt` 或当前项目；复制 `.env.example` 为 `.env` 后填写自己的模型配置。

```bash
python main.py
```

前端：

```bash
cd frontend
npm install
npm run build
npm run dev
```

## 验证基线

- Python 核心导入：通过
- pytest：可收集 548 项测试
- 前端生产构建：通过
- 全量 pytest：此前在 120 秒工具时限内未完成，建议在交付机器上延长时间运行

## 完整性声明

本交付包通过复制生成；原工程未移动。源码内容和内部目录结构保持不变，没有修改业务逻辑、Agent workflow、API 行为或数据库 schema。

`POE_CODE_CLI_DIR` 必须保持为 `.poe-code-cli`。不要单独移动该目录，否则实验设计抽取第 07 步会因找不到 `launcher.mjs` 而失败。

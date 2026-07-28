# 论文实验设计抽取

Literature Experimental Design Extraction Module

一个统一入口、证据驱动、人工治理的实验设计知识转换 Capability。上层 Agent 无需了解 Skill01–13，只需调用 `paper_experimental_design_extraction.execute()`。

## 能力边界

模块把用户目标、自动检索结果或上传论文转换为：候选文献、验证结果、实验设计知识、原文证据、质量评价、K-12 候选设计空间、DBTL 工程计划、治理状态和前端 JSON。

它不会把 AI 分析伪装成论文事实，不会自动批准 AI 方案，也不会用低证据信息生成可执行计划。

## Python 入口

```python
from paper_experimental_design_extraction import execute

request = {
    "task_id": "task-001",
    "user_request": "提取论文实验设计并分析 E. coli K-12 适配性",
    "target_system": {
        "organism": "Escherichia coli",
        "strain": "K-12"
    },
    "literature_source": {
        "type": "upload",
        "files": [r"D:\papers\paper.pdf"],
        "doi": []
    },
    "requirements": {
        "target_phenotype": "",
        "engineering_goal": "",
        "time_range": "",
        "quality_requirement": ""
    },
    "mode": {
        "automatic": True,
        "human_review": True
    }
}

result = execute(request)
```

自动检索时使用 `type: auto_search` 并提供用户目标。DOI 入口使用 `type: upload`，把 DOI 放入 `doi` 数组。

自动 DOI 下载默认按 5 篇小批量运行，并优先查询 OpenAlex OA location。可调整：

```python
result = execute(request, {
    "pdf_download_policy": {
        "max_candidates": 10,
        "paper_ids": ["paper:target-id"]
    }
})
```

可选环境变量为 `OPENALEX_API_KEY` 和 `UNPAYWALL_EMAIL`。系统只下载开放获取或调用方有权访问的响应，不包含 Sci-Hub、反爬绕过或付费墙规避。

## 输出

输出符合 `schema/output.schema.json`：

- `summary`
- `literature_candidates`
- `validated_papers`
- `experimental_designs`
- `evidence_map`
- `quality_report`
- `k12_comparison`
- `engineering_plan`
- `governance`
- `frontend_view`
- `artifacts`
- `skill_states`、`skill_logs` 和标准化 `errors`

## Skill 流程

```text
01 Requirement → 02 Retrieval → 03 Citation → 04 PDF
→ 05 Parse → 06 Clean → 07 Extract → 08 Evidence
→ 09 Evaluate → 10 K-12 → 11 DBTL Plan
→ 12 Governance → 13 Frontend
```

上传 PDF 会跳过 Skill02/03；DOI 会跳过 Skill02，从 Skill03 验证。Skill05–09 对每篇论文分别运行，Skill10 起聚合为多论文分析。

## 部分运行和恢复

```python
execute(request, {
    "start_skill": "skill07_experiment_extraction",
    "end_skill": "skill09_quality_evaluation",
    "initial_context": {...},
    "state_dir": r"D:\module-state"
})

execute(request, {
    "resume": True,
    "state_dir": r"D:\module-state"
})
```

每个 Skill 输出都会成为 Artifact，并在 `<state_dir>/<task_id>/checkpoint.json` 原子保存。恢复时已成功、警告或待审的步骤不会重跑。

## 状态和人工治理

工作流状态为 `CREATED / RUNNING / WAITING_REVIEW / COMPLETED / FAILED`。人工待审不会阻止 Skill13 生成界面；当前 Artifact 是否允许推进由 Skill12 governance 决定。

## REST API

安装可选依赖：

```powershell
python -m pip install fastapi uvicorn
python -m paper_experimental_design_extraction.api.run_server
```

接口：

- `POST /api/paper-experimental-design/run`
- `GET /api/paper-experimental-design/status/{task_id}`
- `GET /api/paper-experimental-design/result/{task_id}`

POST 异步返回 `task_id` 和 `running` 状态。

## Agent 集成

Agent 可以直接导入 `execute`，或使用 `TaskManager` 异步提交。测试和宿主系统可通过 `options["executors"]` 注入 Skill 执行器，替换网络、存储或模型依赖。

## LLM 替换

所有未来模型接入应实现 `llm.LLMAdapter.generate(prompt, context, schema)`。默认适配器禁用模型调用；现有确定性 Skill 不直接依赖模块级 LLM。可为 Kimi、GPT、Claude 或本地模型实现适配器并通过宿主注入。

## 测试

```powershell
python -m unittest discover -s paper_experimental_design_extraction/tests -p "test_*.py"
```

覆盖端到端、上传、DOI、失败恢复、非阻塞人审和异步 API。

# WAVE Architecture

## 1. 系统整体架构

```text
User / Researcher
        ↓
Frontend (React/Vite)
        ↓ HTTP / WebSocket
FastAPI + Agent Orchestrator
        ↓
Planning / Workflow State Machine / Tool Calling
        ↓
Knowledge Retrieval ←→ DDR / Literature / Rules
        ↓
Evidence Validation + Model Applicability
        ↓
Diagnosis → Engineering Design → Simulation
        ↓
Scientific Evaluation / Critic / Comparison
        ↓
Human Review Gate
        ↓
Versioned Ledger / Memory / Next DBTL Cycle
```

## 2. Agent Workflow

Agent 行为由编排器、工作流状态、结构化契约和 gate 共同约束。工具执行结果、失败类型、等待用户和审批状态被显式记录，而不是仅保存在模型上下文中。

## 3. Knowledge Architecture

```text
Literature
   ↓
Experimental Design Extraction
   ↓
DDR / Curated Knowledge
   ↓
Rule Distillation + Evidence Links
   ↓
Diagnosis and Engineering Decisions
   ↓
Experiment Outcomes / Knowledge Claims
```

知识资产位于 `knowledge/`，检索、蒸馏、论文抽取和知识晋升分别由对应的 `harness/` 领域模块实现。

## 4. Evidence Architecture

证据系统保存来源、适用条件、支持/反对/一致等关系、模型计算状态和审阅轨迹。系统明确区分 general knowledge、具体论文证据、真实模型输出、not computed 与 unavailable，避免用缺失值伪装结论。

## 5. DBTL Architecture

```text
Design: diagnosis, strategy portfolio, candidate evaluation
  ↓
Build: human-approved design version and construct plan
  ↓
Test: experiment plan, ingestion, QC, observation
  ↓
Learn: outcome classification, hypothesis revision, knowledge claim
  └──────────────────────────────→ next Design cycle
```

## 6. Frontend / Backend 关系

前端通过 FastAPI 路由读取项目、工作流、证据、设计、评审和时间线状态，并通过 WebSocket 接收会话事件。后端是状态与治理规则的权威来源；前端负责呈现和触发明确的用户操作，不替代后端 gate。

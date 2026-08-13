# WAVE Architecture

```text
User Request
    ↓
Frontend / FastAPI
    ↓
Agent Orchestrator
    ↓
Planning + Workflow State Machine + Tool Calling
    ↓
Knowledge Retrieval (Literature / DDR / Rules)
    ↓
Evidence Validation + Model Applicability
    ↓
Diagnosis → Engineering Design → Simulation
    ↓
Scientific Evaluation / Critic
    ↓
Human Review Gate
    ↓
Versioned Ledger / Memory / Next DBTL Cycle
```

## 代码边界

- `harness/orchestrator/`：Agent 编排
- `harness/workflow/`：工作流控制与 gate
- `harness/evidence_retrieval/`：证据检索
- `harness/knowledge_distillation/`：规则与知识蒸馏
- `harness/paper_extraction/`：论文实验设计抽取
- `harness/diagnosis/`：瓶颈诊断
- `harness/engineering_design/`：工程设计
- `harness/virtual_cell/`：虚拟细胞与模型适配
- `harness/scientific_evaluation/`：科学评审与治理
- `harness/api/`：后端 API
- `frontend/src/`：页面、组件、API 调用和可视化

后端是状态、证据和治理规则的权威来源；前端负责展示及触发明确的用户操作。

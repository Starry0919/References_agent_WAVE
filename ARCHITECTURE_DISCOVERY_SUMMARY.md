# WAVE Architecture Discovery Summary

## 当前真实架构

WAVE 不是单一聊天 Agent。当前工作树包含四类控制机制：自由工具调用的 LLM 会话、程序化 WorkflowController、Scientific Runtime、跨领域 Unified Orchestrator；后者连接证据、诊断、工程设计、科学评审、虚拟细胞、实验与学习模块。

核心持久化也不是单一数据库：会话 trace 使用 JSONL，workflow 使用 JSON checkpoint，长期项目/DBTL 使用 SQLAlchemy 项目账本和领域表。人工 gate 存在于 workflow、诊断、设计、科学评审和模型更新中。

## 一级模块与状态

| 模块 | 状态 |
|---|---|
| Interaction/API | IMPLEMENTED, WIRED, TESTED, UI_EXPOSED；旧聊天为 LEGACY |
| Runtime/Orchestration | IMPLEMENTED, WIRED, TESTED；统一编排产品闭环 PARTIAL |
| Evidence/Knowledge | IMPLEMENTED, WIRED, TESTED, UI_EXPOSED；表示体系分散 |
| Project Memory/DBTL | IMPLEMENTED, WIRED, TESTED；Build 与外部实验集成 PARTIAL |
| Diagnosis | IMPLEMENTED, WIRED, TESTED, UI_EXPOSED |
| Engineering Design | IMPLEMENTED, WIRED, TESTED, UI_EXPOSED；部分查询/闭环 PARTIAL |
| Scientific Evaluation | IMPLEMENTED, WIRED, TESTED；独立 UI PARTIAL |
| World Model/Virtual Cell | IMPLEMENTED, WIRED, TESTED；真实模型覆盖 PARTIAL |
| Metrics/Golden Set | IMPLEMENTED, WIRED, TESTED；UI PARTIAL |

## 主关系

`UI/API -> runtime/orchestrator -> evidence -> diagnosis -> engineering design -> scientific evaluation -> experiment/simulation -> learning/knowledge update`。ProjectEvent 账本提供长期审计；human gate 可暂停或拒绝推进。Virtual Cell/World Model 提供模型证据，但未证明所有任务强制经过它们。

## 后续最值得可视化的主题

1. 系统边界与外部世界。
2. 四种 runtime/control plane 的职责与调用关系。
3. Evidence-to-Diagnosis-to-Design-to-Evaluation 科学决策链。
4. 持久 DBTL 与受治理的知识反馈。
5. React 页面到 API/服务的映射。
6. World Model、Virtual Cell、残差与模型更新治理。

不应提前决定最终图数；上述只是候选主题。

## 绘图前必须保留的歧义

- 多控制器边界和入口选择规则分散。
- JSONL、JSON checkpoint、SQL ledger 等多种“记忆”并存。
- DDR、KnowledgeClaim、Hypothesis、paper objects、world-model entities 缺少统一 ontology 证据。
- 前端能力表仍把 orchestrator、virtual cell、evaluation、learning、experiments 等标为 partial。
- Build/Test 的真实实验执行、LIMS 和库存系统处于系统外或仅有引用字段。
- 全量 pytest 本次 60 秒超时；只能证明测试代码存在，不能声称全部通过。

详见 `ARCHITECTURE_DISCOVERY_REPORT.md`；机器可读事实见 `ARCHITECTURE_MAP.json`。

# WAVE Project Overview

## 1. 项目简介

WAVE（Westlake AI Virtual Cell）是面向合成生物工程设计的持久化、可追溯、人工治理 DBTL 系统。

## 2. 项目定位

WAVE 不是普通的 LLM 对话封装。它把模型生成置于结构化工作流、证据约束、模型适用性检查、科学评审、版本化账本和人工审批之中，使建议能够被解释、审查和复现。

## 3. Agent 平台目标

- 将自然语言工程目标转换为结构化任务和可审计决策。
- 在 Design–Build–Test–Learn 循环中保存上下文、证据和版本谱系。
- 区分已计算、不可用、证据不足和人工批准等状态，避免伪造确定性。
- 连接文献、DDR、规则、虚拟细胞模型和实验结果。

## 4. 核心能力

- Agent orchestration、tool calling 与持久会话
- DBTL workflow 和状态门控
- Literature/experimental design extraction
- DDR、Evidence、Rule Distillation 与 Knowledge Claims
- Bottleneck Diagnosis 与 Engineering Design
- Virtual Cell/FBA 模型适用性及仿真
- Scientific Evaluation、Critic、Pareto 比较与 Human Gate
- React 前端、项目时间线、谱系和审计展示

## 5. 当前完成模块

主工程位于 `agent/agent-harness/agent-harness/`。后端领域模块、API、前端、工作流、知识库和测试均已落地；当前测试套件可收集 548 项，前端可完成生产构建。

## 6. 后续扩展方向

- 增加更多底盘、产物和模型适配器，并明确适用域。
- 扩充专家审阅后的 DDR、golden set 与评估基准。
- 将实验数据接入、质量控制和知识晋升流程进一步自动化。
- 在独立重构分支中评估根目录扁平化，并配套完整回归测试。

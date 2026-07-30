# Changelog

All notable changes to this project will be documented in this file.

# Changelog

All notable changes to this project will be documented in this file.

## [2026-07-30] Agent-Harness Update

### Added

#### Frontend
- **AgentTracePanel** (`frontend/src/pages/evidence/components/AgentTracePanel.tsx`) — Agent 推理过程追踪面板，展示 LLM 提取过程中的中间步骤与决策路径
- **CalibrationPanel** (`frontend/src/pages/evidence/components/CalibrationPanel.tsx`) — 提取校准面板，支持人工标注修正与自动校准反馈
- **EvidenceGraphModal** (`frontend/src/pages/evidence/components/EvidenceGraphModal.tsx`) — 证据关系图谱弹窗，可视化论文间证据引用网络
- **EvidenceProvenancePanel** (`frontend/src/pages/evidence/components/EvidenceProvenancePanel.tsx`) — 证据溯源面板，追踪结论到原始文献的完整链路
- **ExperimentalDesignPanel** (`frontend/src/pages/evidence/components/ExperimentalDesignPanel.tsx`) — 实验设计面板，结构化展示提取的实验方案
- **ExperimentalStepCard** (`frontend/src/pages/evidence/components/ExperimentalStepCard.tsx`) — 实验步骤卡片，展示单步实验操作与参数
- **PaperHeader** (`frontend/src/pages/evidence/components/PaperHeader.tsx`) — 论文头部信息组件，聚合标题、作者、期刊、DOI 等元数据

#### Backend — Paper Extraction
- **calibration.py** — 提取校准模块，支持基于人工反馈的自校准与置信度修正
- **rule_distillation.py** — 规则蒸馏模块，从标注数据中提取可复用的提取规则
- **translation/service.py** — 论文翻译服务，支持中英双语互译与术语标准化

#### Backend — API
- **translation.py** (`harness/api/translation.py`) — 翻译 REST API，暴露翻译、术语查询等接口

#### Knowledge Base
- **DDR-006/007** (`knowledge/ddr_database/`) — 新增"利用合成机器提升碳得率"相关 DDR 知识条目（2 条）

#### Documentation
- **WORK_A_ALIGNMENT_REPORT.md** — Work A 对齐报告，记录当前实现与需求目标的差距分析

#### Tests
- **test_calibration.py** — 提取校准模块单元测试
- **test_reasoning_view.py** — 推理视图构建器测试
- **test_result_summary.py** — 结果摘要生成测试
- **test_rule_distillation.py** — 规则蒸馏模块测试
- **test_translation_service.py** — 翻译服务测试

### Changed

#### Frontend
- `PaperEvidenceDetailPage.tsx` — 接入 AgentTracePanel、CalibrationPanel、EvidenceGraphModal 等新组件
- `KnowledgePage.tsx` — 优化知识条目展示布局
- `PaperExtractionPage.tsx` — 增强提取结果交互
- `PaperResultTabs.tsx` — 新增校准与溯源标签页

#### Backend
- `opus_extractor.py` — 集成 calibration 与 rule_distillation 能力
- `ddr_converter.py` — 增强对 schema_v2 新字段的处理
- `reasoning_view.py` — 支持多层级推理链展示
- `result_summary.py` — 优化跨论文结果聚合逻辑

### Removed
- 无破坏性删除

---

## [2026-07-29] Agent-Harness Update

### Added

#### Frontend
- **PaperEvidenceDetailPage** (`frontend/src/pages/evidence/PaperEvidenceDetailPage.tsx`) — 论文证据详情页面，支持展示单篇论文的提取结果与推理链
- **ReasoningStepCard** (`frontend/src/pages/evidence/components/ReasoningStepCard.tsx`) — 可折叠的推理步骤卡片组件，用于可视化论文提取的逐层推理过程
- **PaperResultTabs** (`frontend/src/pages/paperExtraction/PaperResultTabs.tsx`) — 论文提取结果多标签页组件，支持在摘要、实验设计、证据链等视图间切换

#### Backend — Paper Extraction
- **ddr_converter.py** — DDR（Design-Decision-Rule）格式转换器，将论文提取结果转换为标准化知识条目
- **pipeline_cache.py** — 流水线级缓存管理，支持按论文哈希缓存中间提取结果，减少重复 LLM 调用
- **reasoning_view.py** — 推理视图构建器，将 LLM 提取结果组织为结构化推理链
- **result_summary.py** — 提取结果聚合与摘要生成，支持多论文交叉汇总

#### Backend — Evidence Retrieval
- **evidence_grading.py** — 证据质量评分模块，基于相关性、可信度、可复现性对文献证据进行多维度打分

#### Knowledge Base
- **DDR-005_tryptophan_chen_zeng.json** — 新增色氨酸代谢通路 Chen & Zeng 文献的 DDR 知识条目
- **schema_v2.json** — DDR 知识条目 Schema v2，扩展了 `confidence_score`、`contradiction_flags`、`experimental_conditions` 等字段

#### Tests
- **test_ddr_converter.py** — DDR 转换器单元测试，覆盖正常转换、缺失字段回退、格式校验等场景
- **test_pdf_identity_extraction.py** — PDF 身份提取测试，验证 DOI/标题/作者识别准确率

### Changed

#### Frontend
- `KnowledgePage.tsx` — 集成新的证据评分展示，支持按质量筛选知识条目
- `paperExtraction/PaperExtractionPage.tsx` — 接入 PaperResultTabs，优化提取结果展示
- `router.tsx` — 新增 `/evidence/:paperId` 路由
- `evidence.ts`、`paperExtraction.ts` — API 客户端同步后端新接口

#### Backend — Core APIs
- `harness/api/generation.py` — 支持 reasoning chain 生成模式
- `harness/api/paper_extraction.py` — 新增 `pipeline_cache` 与 `ddr_convert` 调用点
- `harness/llm_generation/client.py` — 优化多轮对话上下文管理，减少 token 溢出

#### Backend — Paper Extraction Pipeline
- `opus_extractor.py` — 接入 reasoning_view 与 result_summary，输出更结构化的提取结果
- `paper_extraction/service.py` — 增加缓存命中逻辑与 DDR 转换后处理
- `skill04_pdf_acquisition/artifact/metadata.py` — 增强 PDF 元数据解析，支持更多 DOI 格式
- `skill04_pdf_acquisition/skill.py` — 支持批量 PDF 异步获取
- `skill05_pdf_parser/skill.py` — 改进 Markdown 分段策略，降低表格误解析率
- `skill06_markdown_cleaner/skill.py` — 新增引用去重与格式标准化规则
- `skill08_evidence_binding/skill.py` — 支持跨段落证据关联
- `skill09_quality_evaluation/skill.py` — 接入 evidence_grading 评分体系

#### Backend — Workflow Engine
- `paper_experimental_design_extraction/workflow/engine.py` — 支持缓存优先执行路径
- `paper_experimental_design_extraction/api/task_manager.py` — 新增任务级重试与降级策略

#### Knowledge Base
- `biological_rules/rules.json` — 补充色氨酸代谢通路调控规则
- `DDR-001~004` — 按 schema_v2 升级字段格式

### Removed
- 无破坏性删除

### Infrastructure
- `.gitignore` — 新增排除规则：
  - `paper_artifacts/**/*.pdf`（论文 PDF 不上传）
  - `storage/extraction_cache/`、`storage/pipeline_cache/`（运行时缓存）
  - `agent-harness - 副本/`（本地备份目录）

---

## [2026-07-28] Initial Release

### Added
- 初始提交：包含完整的合成生物学 Agent Harness 框架
- 前端 React + TypeScript + Tailwind CSS 界面
- 后端 FastAPI 服务层
- 论文提取（Paper Extraction）、证据检索（Evidence Retrieval）、瓶颈诊断（Bottleneck Diagnosis）、工程设计（Engineering Design）等核心模块
- Golden Set 评测体系
- vEcoli 虚拟细胞适配器（外部仓库引用）

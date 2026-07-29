# Changelog

All notable changes to this project will be documented in this file.

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

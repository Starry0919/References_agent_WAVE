# Final Closure Wave Implementation Report — 2026-08-12

STATUS: PARTIAL

核心优化闭环已完成；唯一未通过项是外部 LLM 在线结构化生成测试连续两次返回 schema-invalid 并触发 fallback。该失败未被伪装成 PASS，也未影响确定性生产路径。

## What changed

- Quantitative Semantic Role 接管 legacy extractor projection；混合上下文按 clause 分类，错误角色被隔离为 `LEGACY_UNVERIFIED`。
- 所有生产候选生成统一要求真实 `Observation → EngineeringProblem → HypothesisVersion → DiagnosisFinding`；缺失时返回 `DATA_REQUIRED/DIAGNOSIS_REQUIRED`。
- 编排器诊断路径现在实际生成 immutable `DiagnosisFinding`，不是只生成 decision id。
- `transition_candidate` 成为候选决策状态唯一写入口；`status/readiness` 仅为兼容投影。人类选择先于验证计划，完整计划先于 build-ready。
- `EvidenceNeed` 接受证据后追加新的 immutable `HypothesisVersion`，记录 before/after graph、支持/反驳 delta 和停止原因。
- Historical Prior 不再进入 evidence links；明确标注 `PRIOR / not_evidence / requires_fulltext_experiment_verification`。
- FailureCase recall 进入生产 portfolio ranking，context mismatch 衰减或归零。
- 候选科学状态 API/UI 展示诊断发现、QC/溯源、EvidenceNeed、先验、模型评估、验证计划、真实状态及下一动作。
- 修复编排器学习阶段错误选择 portfolio 第一个候选的问题，改为选择实际 governed+built 候选。
- 旧名 `iML1515.xml` 的运行时模型实际为 iJO1366；注册信息、规模和限制已按运行时真值更正。

## Changed files (主要)

- `harness/paper_extraction/quantitative_roles.py`, `harness/paper_extraction/opus_extractor.py`
- `harness/diagnosis/findings.py`, `harness/orchestrator/adapters.py`, `harness/orchestrator/service.py`
- `harness/engineering_design/portfolio_service.py`, `decision_state.py`, `evaluation_service.py`, `decision.py`, `failure_recall.py`, `governance_service.py`, `build_test_planner.py`, `outcome_service.py`
- `harness/evidence_retrieval/dynamic_loop.py`, `harness/api/engineering_design.py`
- `harness/virtual_cell/registry.py`, `harness/diagnosis/model_adapters/gem_fba_iml1515.py`
- `frontend/src/api/engineeringDesign.ts`, `frontend/src/pages/design/CandidateDetailDrawer.tsx`
- 对应 reference-optimization、orchestrator、golden-set、simulation、virtual-cell 与前端测试。

## Closure status

| Item | Status |
|---|---|
| P0-2 quantitative legacy projections | PASS |
| P0-3 DiagnosisFinding enforcement | PASS |
| P0-4 candidate state source of truth | PASS |
| P0-5 candidate/product/condition FBA | PASS；模型身份更正为 iJO1366 |
| P0-6 EvidenceNeed → HypothesisVersion | PASS |
| P1 Historical Prior boundary | PASS |
| P1 Failure recall ranking | PASS |
| P1 frontend/backend scientific state | PASS |

## Scientific behavior changes

文本充分性声明不再代替实验观测；文献频率不再充当实验效力；模型文件名不再覆盖运行时模型身份；候选不能从 generated 跳到 selected/build-ready；失败记忆只影响匹配上下文中的排序。

## Replay summary

五类 replay 均完成，详见 `FINAL_CLOSURE_WAVE_REPLAY_REPORT_2026-08-12.md`。

## Regression summary

后端 821 collected：819 passed、1 skipped、1 external-live failed。前端 50/50 passed；typecheck 与 production build passed。详见 regression report。

## Remaining blockers

- 外部结构化 LLM provider 健康检查可用，但两次真实调用均未产生 schema-valid hypothesis payload；系统正确 fallback。需要 provider/prompt 兼容性或外部服务恢复后重跑。
- SWIG 与 Starlette deprecation warnings 非本轮引入的关键回归。

## Human-only blockers

真实项目进入 `human_selection_pending` 后仍必须由独立人类作选择；未伪造 HumanApproval。

## Can this optimization wave be closed?

核心 production-integrated 优化可以关闭；全仓 release gate 因一个外部在线测试未通过，状态保持 PARTIAL。

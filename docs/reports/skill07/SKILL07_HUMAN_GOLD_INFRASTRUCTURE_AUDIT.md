# Skill07 Human Gold Infrastructure Audit

日期：2026-08-12；生产行为变更：NO。

## Discovered implementation and artifacts

- Wave 2：报告、结果、纠正 manifest、semantic alignment、10-paper selection、review JSON、66-item queue、paired/concurrency matrices 均存在。
- Source：10 篇均可从纠正 manifest 解析到 `clean_document.json`；包含 paragraphs、sections、figures、tables、citations 等稳定锚点。
- Candidates：历史 A/G 仅覆盖 5 个完整 pair；其他论文必须显式表示 candidate unavailable，不能补造。
- Skill07 contract：生产 schema/validator 位于 `harness/paper_extraction`；本任务不改生产抽取行为。
- Platform：FastAPI routers + React/Vite frontend；已有 paper extraction 页面与一般 golden-set API，但没有 Skill07 source-first Gold 工作流。
- Existing review：DDR calibration 支持两份抽取记录和冲突检测，但数据粒度、冻结语义与本任务不兼容，仅复用独立记录原则。

## Current contracts and artifact relationships

Wave 2 manifest 连接 benchmark paper ID、paper ID、PDF/clean-document fingerprint；selection 固定 GOLD-P01..P10；alignment report 保存历史 A/G 比较；review/queue 是 Silver review aids。它们都不是 Gold。

## Missing pieces

- Experiment、Atomic Claim、Evidence 的机器 schema 与跨引用验证。
- 全文覆盖声明、G0-G7 gate、严格 human tier/state transition。
- 10 篇 source index、union inventory、空白双标注者 draft 与完整 review package。
- source-first UI/API、missed experiment、merge/split/parent-child、claim/evidence editor。
- 独立 annotator storage、agreement、reconciliation/adjudication history。
- immutable release、hash verification、read-only frozen scoring。
- candidate-vs-frozen-Gold alignment/scoring 和非补偿 hard gates。

## Reuse versus new implementation

复用 FastAPI/React、Wave 2 stable mapping、clean-document anchors、semantic comparator 和 candidate artifacts。新增隔离目录 `benchmarks/skill07_human_gold/`、CLI/service、专用 router/workbench、schemas/tests。原始 Wave 2 文件只读。

## Compatibility and migration risks

- 历史 A/G 结构并非 Gold schema，只作为 candidate context，禁止直接迁移 tier。
- 仅 5 篇有完整 A/G pair；其余缺失必须可见。
- paragraph/page/figure 可用性不均；validator 只在 locator 可解析时验证，不可用 Supplement 必须显式 `UNAVAILABLE`。
- Frozen release 不引用 mutable draft；修订必须新版本。
- 前端新增路由/API，不改变既有 paper extraction 页面或生产 Skill07 default。

## Exact implementation plan

1. 建立三套 JSON Schema、治理枚举、stable-ID 与 G0-G7 validator。
2. 生成固定 10 篇 source-first packages，导入全部 66 unresolved items，并构建不限于 disagreement 的 union inventory。
3. 增加 FastAPI CRUD/validation endpoints 与 React workbench，按角色隔离保存，支持 HUMAN_ADDED、merge/split/link、claim/evidence。
4. 实现 open-set agreement、categorical agreement、reconciliation/adjudication package。
5. 实现 fail-closed freeze、semantic versions、manifest hashes、tamper verification/readiness。
6. 实现仅消费 verified frozen release 的 A/G scoring，包括 one-to-many/many-to-one 和 hard gates。
7. 运行 schema/workflow/freeze/scoring/regression tests并生成操作指南、规格与状态报告。

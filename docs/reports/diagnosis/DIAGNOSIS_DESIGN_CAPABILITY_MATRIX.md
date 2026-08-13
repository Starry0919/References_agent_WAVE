# Diagnosis → Engineering Design Capability Matrix

审计日期：2026-08-12  
目标项目：`PROJ-3f77f638302b`  
状态口径：**PASS** = 目标项目中已有真实产出且被消费；**PARTIAL** = Schema/逻辑/API 存在，但项目数据、科学接地或闭环不完整；**MISSING** = 关键能力或项目产出不存在。

| Capability | Status | Evidence | Gap |
|---|---|---|---|
| Problem Map | PARTIAL | Diagnosis Workbench 展示 ranked problems、leading/alternative、evidence for/against、falsifier、engineering consequence；项目有 4 个假设 | 无 Observation、无项目匹配测量、无显式 Finding 实体；主要仍是“假设集合 + UI 组织” |
| Evidence provenance | PARTIAL | `EvidenceItem`/`EvidenceLink` 有 source reference、relation、quality、directness；项目有 12 条 `expert_rule → DDR-001` links | 全部为 low/indirect rule transfer；0 measured、0 literature、0 model-linked、0 contradicts；condition match 为 unknown |
| Hypothesis competition | PASS | 每个有效会话有 4 个机制竞争项；2 leading、2 alternatives-not-excluded；有 ranking、prediction、falsifier | 排序信号高度同质，前三项均 low/indirect；缺少反向证据和实际判别实验 |
| Quantitative grounding | PARTIAL | 模型 adapter 与 FBA 执行逻辑存在；项目有 1 条真实 optimal FBA 记录 | 该记录属于另一诊断会话，使用 `e_coli_core` biomass objective；未约束 L-tryptophan、未进入 Design handoff；yield/growth impact/FVA/omics 未接地 |
| Candidate generation | PASS | `EDP-78ae7989000f` 有 2 strategies、3 candidates；候选包含 diagnosis hypothesis refs、mechanistic rationale、evidence links | 仅 1 个生产性干预候选；部分 action 组合的具体范围与 build context 未解析 |
| Evaluator | PARTIAL | 9 个 evaluator、hard constraints、Pareto/selection logic、API 与前端读路径存在；152 个 Diagnosis/Design 测试通过 | 目标项目 `design_evaluations=0`；因此项目级 Generate→Evaluate→Reject→Rank→Select 未发生 |
| Selection | MISSING | Schema/decision logic 能返回 selected/rejected/nondominated set | 项目 portfolio decision 为 null，3 个 candidate 全为 proposed，0 selected、0 rejected、0 human approval |
| Validation planning | MISSING | BuildTestPackage schema、planner、API、ValidationEvaluator 存在 | 项目 build/test package、diagnostic test、experiment plan/run、validation plan、outcome 全为 0 |
| Diagnosis → Design traceability | PARTIAL | DesignProject 记录 diagnosis session/decision/version；handoff 含 supported hypotheses 与 unresolved alternatives；candidate evidence links 指向 hypothesis IDs | 没有独立 `DiagnosisFinding.id → CandidateIntervention.diagnosis_ids` 契约；依赖 heterogeneous evidence links 和 source version，映射不够强类型化 |
| Alternatives and exclusion | PARTIAL | Diagnosis 保留 2 个 unresolved alternatives；Design 记录 7 类未生成策略的排除理由；有 information-gain candidate | 没有候选级 evaluator rejection；排除主要发生在 strategy generation，而非验证后的淘汰 |
| Evidence calibration | PARTIAL | Diagnosis UI 明示 RULE_TRANSFER 为 soft；EvidenceEvaluator 区分 evidence tiers | Design 中 `historical_precedent` 可映射为 curated knowledge，且 design prior 有 0.858 分值；项目缺少 condition/applicability 验证，存在先验过强风险 |
| Coverage completeness | PARTIAL | Workbench 检查 pathway、precursor、cofactor、regulation、enzyme、competition、toxicity、process 并标记未评估 | 项目真实输出主要覆盖 pathway/precursor/central flux；cofactor、regulation、enzyme、toxicity、process 没有项目特异结果 |
| Rule/DDR retrieval | PASS | 项目策略包含 ACT、DDR、RULE 引用和 applicability/exclusion 信息；可追溯到来源 ID | 规则迁移尚未由本项目测量或模型确认，不可视为因果事实或硬证据 |
| Observation → validation scaffold | PARTIAL | UI 和 Schema 支持 observation、mechanism、intervention、validation；候选含 causal chain 和 falsifiers | 项目 Observation=0、diagnostic tests=0、BuildTestPackage=0，实际链条从“规则假设”开始并停在 proposed candidate |

## 六层能力判定摘要

| Area | Schema | Logic | API connected | Real data populated | Frontend consumed | Validated |
|---|---|---|---|---|---|---|
| Diagnosis | PASS | PASS | PASS | PARTIAL | PASS | PASS（实现测试）；PARTIAL（项目科学接地） |
| Evidence | PASS | PASS | PASS | PARTIAL | PASS | PARTIAL |
| Quantitative models | PASS | PASS | PASS | PARTIAL | PASS（可用性/缺失态） | PARTIAL |
| Design generation | PASS | PASS | PASS | PASS | PASS | PASS（生成阶段） |
| Evaluator | PASS | PASS | PASS | MISSING | PASS（空态/读取路径） | PASS（实现测试）；MISSING（项目执行） |
| Selection | PASS | PASS | PASS | MISSING | PASS（空态） | MISSING（项目执行） |
| Validation planning | PASS | PASS | PASS | MISSING | PARTIAL | PASS（实现测试）；MISSING（项目执行） |


# WAVE Agent 参考资料逐项研读、现状比对与优化路线图

日期：2026-08-12  
对象：当前 `WAVE_Agent_Platform` 代码、运行产物与验收报告  
参考资料：既有分析文档、SynBioGPT2 论文、ELISER 论文、ELISER GitHub、专家思维教程与资源地图

外部仓库核对版本：`emarquzz/ELISER-StrainDesignDB`，HEAD `9c58b1011ea97ab91459cceecaf8ee570845f92d`（2026-08-12 访问）。

## 0. 结论先行

WAVE 不需要照搬 SynBioGPT2 或 ELISER。当前 WAVE 已经在以下方面明显超过两份参考工作：版本化证据账本、竞争假设、反证关系、判别实验、失败分类、条件匹配、人工审批、科学评审、可恢复 DBTL 状态和原子主张层。

真正的问题是：这些能力大量以“模块已存在”的形式分散在系统中，却没有稳定串成一条默认、强制、可验收的专家决策链。当前最重要的升级不是继续增加模块，而是完成四个闭环：

1. **文献类型识别 → 正确抽取器 → 正确下游路由**；
2. **Evidence Gap → 定向补检索 → 再评价 → 停止**；
3. **Observation → DiagnosisFinding → Candidate → 定量评估 → 淘汰/选择 → ValidationPlan**；
4. **实验结果 → 假设更新 → 成功/失败记忆 → 可校准 Design Prior**。

本次最关键的新发现来自一次真实回放：两篇参考论文被当前论文抽取管线成功解析后，系统把 SynBioGPT2 的系统评测参数 `n=120`、`2 min` 等误识别为湿实验重复数和培养时间，并进一步生成 K-12 工程建议；最终 `skill13_frontend_adapter` 因来源标签错误失败。自动 QC 为 `REVIEW_REQUIRED`，发现 23 个未知字段，发布状态为 `blocked`。这说明 WAVE 虽然已经实现文献分类与九类路由，但它尚未成为论文抽取和工程建议的强制门控层。

## 1. 研读方法与证据边界

本次同时核对了：

- 当前代码中的 `harness/evidence_retrieval`、`harness/diagnosis`、`harness/engineering_design`、`harness/learning`、`harness/paper_extraction`；
- 当前真实状态报告，尤其是 `LITERATURE_PIPELINE_CURRENT_FLOW.md`、`DIAGNOSIS_DESIGN_FINAL_ACCEPTANCE_REPORT.md` 和 `PAPER_EXTRACTION_E2E_RELEASE_GATE.md`；
- 两份 PDF 的完整结构化正文与关键方法、结果、限制；
- ELISER GitHub 的实际目录、输出 CSV、RDF/Turtle 和 README，而不只依据论文描述；
- 使用现有实验设计提取技能对两份 PDF 做端到端回放。

需要明确：SynBioGPT2 的 91.67% 准确率/完整度和 93.5% 策略重构率是作者在其自建基准上的报告结果，不应直接视为 WAVE 可复现结果；ELISER 的频次与共现是历史先验，不等于因果效力或组合协同。

## 2. 参考资料一：既有《WAVE Agent参考资料研读与架构优化分析》

### 2.1 文档判断正确的部分

既有分析抓住了四个正确方向：

- 从置信度循环升级为“决策链上哪个节点缺证据”；
- 从 Paper 作为知识单位升级为 Engineering Action / Design Pattern；
- 在 Evidence 与 Engineering Design 之间加入机制与策略综合层；
- 用判断性实验、反预测和停止条件区分“会回答”与“会做科学”。

这些判断仍然有效，尤其是 `Constraint → Intervention → Expected causal chain → Counter-prediction → Discriminating experiment` 这一主轴。

### 2.2 相对当前代码已经过时的部分

文档中的不少“建议新增”能力，当前已经有代码实现：

| 既有建议 | 当前实际状态 | 判断 |
|---|---|---|
| 竞争约束假设 | `HypothesisVersion`、四类机制假设、支持/反对证据、falsifier | 已实现，需项目观测接地 |
| 最小判别实验 | `test_selector`、discriminating predictions、information gain | 已实现，目标项目未执行 |
| Failure Memory | `FailureCase`、9 类失败、QC 与技术失败隔离 | 已实现，需跨项目统计与召回 |
| Historical Prior | `historical_priors`、`design_prior`、DDR/Rule memory | 已实现小规模版本，尚非大样本统计先验 |
| Counterfactual | 独立 counterfactual evaluator/service | 已实现，未成为默认必经阶段 |
| Tool-grounded Design | 真实 cobrapy FBA adapter | 已实现核心代谢演示，未对候选和产物目标定量接地 |
| Evidence condition matching | 8 维 context match 与 downgrade | 已实现，但元数据缺失常导致 `insufficient_metadata` |
| Evidence source separation | Atomic Scientific Claim、reported/inferred/predicted 分离 | 已实现，仍需入口路由统一 |

因此，下一阶段不应再以“增加 Step 10.5”作为唯一表述，而应把它升级为贯穿诊断、设计和评审的强类型 `Engineering Intelligence Core`，并强制消费已有模块的输出。

## 3. 参考资料二：SynBioGPT2

### 3.1 论文的真实贡献

SynBioGPT2 的核心不是普通多 Agent，而是三件事的组合：

1. 段落级 BM25 + 领域 BERT，并用 RRF 融合；
2. 主 Agent 将复杂任务拆为瓶颈、辅因子、竞争通量等子问题；
3. 每个子问题执行检索—生成—自评—补查询循环，作者使用 LLM Judge 与 token log-probability 聚合分数，阈值 0.8，最多 8 轮。

它的 120 个任务覆盖 factual extraction、multi-hop reasoning、comprehensive/explanatory 和 counterfactual。论文同时给出两个重要负面结论：外部上下文过多时，DeepSeek-R1 的 counterfactual 表现反而下降；自动生成的组合策略没有体内实验验证，且系统尚不能执行定量稳态模拟。

### 3.2 与 WAVE 的精确比对

| 能力 | SynBioGPT2 | 当前 WAVE | WAVE 应吸收什么 |
|---|---|---|---|
| 动态问题分解 | 运行时生成子查询 | 诊断/设计状态机和假设结构完整，但证据检索服务主要是查找、匹配和核验 | 从未解决假设节点自动生成 `EvidenceNeed` |
| 补检索循环 | 低于阈值继续检索，最多 8 轮 | 有诊断循环、设计循环、评审循环，但没有统一 evidence-gap retrieval loop | 让“缺什么证据”控制查询与停止，而不是固定次数 |
| 混合检索 | 段落级 BM25+BERT+RRF | 论文解析有段落和证据定位；自动发现排序主要基于题名/元数据，尚非全文段落混合检索 | 建立 section-aware paragraph index 与 lexical/semantic fusion |
| 结构化专家 Prompt | 16 元素模板 | WAVE 有更强的 Pydantic schema、Gate 和评审规则 | 保留 schema 权威，不照搬 prompt-only 控制 |
| Counterfactual benchmark | 明确四类任务之一 | evaluator 已实现，但当前目标项目未运行 | 将其加入发布门，而非可选工具 |
| 定量模型 | 不支持 FBA | WAVE 已有真实 cobrapy | 把优势变成 candidate-specific、product-specific 定量证据 |
| 治理与可追溯 | 论文强调事实约束，但持久治理较弱 | 版本账本、人工 gate、原子 claim 更强 | 不退回“一个 confidence 数字” |

### 3.3 不应照搬的部分

- 不固定复制 `0.8` 或 8 轮；不同 claim criticality、证据成本和实验风险应有不同停止条件。
- token log-probability 不是科学置信度，最多作为模型不稳定信号。
- Expansion Factor 只衡量生成宽度，不能衡量新颖性、可行性或安全性。
- 不把更多上下文等同于更好推理，应增加 Evidence Budget Manager，控制相关性、互补性、矛盾和上下文密度。

## 4. 参考资料三：ELISER 论文

### 4.1 数据与方法事实

ELISER 从约 152,921 篇初始 PubMed 记录出发，经分类减少到 20,108，去除约 20% 综述后为 16,130，最终成功抽取 15,798 篇。全文获取率约 50%；其余依赖题名与摘要。它用 NCBI Taxonomy、ChEBI、UniProt、KEGG Ortholog、EC、MetaNetX/BiGG 进行跨来源标准化，并把基因操作方向分为 Positive、Negative、Other。

论文最有价值的工程洞见是：跨宿主、跨产品频繁被操作的往往是中央碳代谢分支点；真正区分设计的常常不是“哪个基因”，而是操作方向与上下文。共现分析得到 8 个模块，包括莽草酸/芳香族氨基酸、削弱乙酸发酵、糖酵解转向 PPP 等。

### 4.2 论文自己承认的限制

ELISER 不能可靠地区分：

- 同一论文中的多个 strain design；
- 成功与失败设计；
- 培养基、温度、pH；
- titer、yield、productivity；
- 工程化酶变体改名；
- 同篇出现的基因究竟属于同一组合还是不同实验。

所以 `co-occurrence ≠ synergy`，`frequent target ≠ effective target`，`paper contains gene ≠ gene belongs to best strain`。

### 4.3 与 WAVE 的精确比对

WAVE 当前的实验实例、证据定位、原子 claim、设计版本、FailureCase 和条件匹配，理论上正好可以解决 ELISER 的主要粒度缺陷。但 WAVE 的工程记忆规模仍很小，缺少 ELISER 这种能计算宿主—产物—操作方向—模块频次的大样本底座。

最合理的融合不是把 ELISER CSV 当作“推荐数据库”，而是把它作为低精度、高覆盖的 `HistoricalPriorSource`：

```text
ELISER coarse record
  → entity normalization
  → host/product/gene/direction prior
  → source-quality + extraction-granularity flags
  → WAVE paper-level re-verification when selected
  → experiment-instance claim/evidence
  → candidate prior (never direct recommendation)
```

先验至少应按 `P(intervention direction | host, product class, pathway module, condition knownness, time window)` 表达，并保留样本数、年代、全文可得性、抽取来源和不确定性。

## 5. 参考资料四：ELISER GitHub

### 5.1 实际可复用资产

仓库提供 MIT License、完整 notebooks/scripts、ChEBI 原始表、LASER 种子、文章分类模型、UniProt/KEGG/BiGG 映射过程、约 3.3 MB 的 CSV 和 RDF/Turtle 输出。实际流水线目录清楚地分为初始化、文章分类、全文/实体抽取和基因修饰分析，适合作为 WAVE 的离线批量 ETL 参考。

### 5.2 不能直接生产接入的原因

实际 CSV 只有：

```text
PMID;Title;Year;Organism;Product;Genes_and_modifications
```

实际 TTL 主要只有 `from_publication`、`produces`、`uses_organism`、`up-regulates`、`down-regulates`、`modified`。它没有实验实例、条件、结果、证据片段、抽取置信度和版本治理。抽样还能看到实体噪声，例如把限制性内切酶名或泛化词识别为基因、产物名粘连、同一基因同时出现正负方向等。

此外，GitHub README 描述的 Articles/Entities/Gene Modifications 三表及 `evidence_text/confidence` 比实际发布 CSV 更丰富，说明文档 schema 与当前发布制品存在漂移；某个 LASER README 还把代谢工程 LASER 错写成半导体设备数据库。WAVE 可以借鉴其开放和可复现性，但必须增加制品契约测试、schema 版本、数据字典一致性测试和 release manifest。

## 6. 参考资料五：专家思维教程与资源地图

教程的核心价值不在资源列表，而在专家决策顺序：

```text
目标与边界
→ 当前状态与观测
→ 多个约束假设
→ 支持/反对证据
→ 可干预机制
→ 完整因果链与反预测
→ 最小判别实验
→ 定量/工具检验
→ 决策与停止条件
→ 实验结果后的学习
```

当前 WAVE 的对象模型基本覆盖了这条链，但 `DIAGNOSIS_DESIGN_FINAL_ACCEPTANCE_REPORT.md` 已证明实际目标项目没有完成：Observation=0、evaluation=0、selected/rejected=0、ValidationPlan=0，唯一 FBA 还是核心 biomass objective，未模拟色氨酸目标或候选干预。因此教程带来的最重要要求是：**不能以模块存在替代项目级闭环完成**。

## 7. WAVE 当前优势、部分能力与真实缺口

| 维度 | 已经较强 | 仍然不足 |
|---|---|---|
| 证据治理 | AtomicClaim、支持/反对关系、condition match、不可变账本、人工审批 | 入口路由与下游 gate 割裂；真实 Gold 仍不足 |
| 诊断 | 四类竞争假设、反预测、判别实验、belief update | Data Sufficiency 未强制验证项目 Observation；证据单一 |
| 设计 | portfolio、9 个 evaluator、Pareto、counterfactual、Build/Test Planner | evaluator/selection/validation 未成为默认必经链路 |
| 定量模型 | 真实 cobrapy FBA，诚实标注 vEcoli/kinetic unavailable | 仅核心模型演示，缺 candidate/product/condition-specific 模拟 |
| 文献 | 多源发现、PDF 解析、证据绑定、分类路由 v2 | 上传型论文绕过分类门控；检索不是段落级动态补检索 |
| 记忆学习 | FailureCase、HypothesisVersion、LearningCycle、KnowledgeClaim 晋升 | 缺大样本 historical prior、跨项目校准和负结果主动召回 |
| 评测 | 多套 benchmark、回放、release gate、sealed holdout 思路 | ExperimentInstance/DDR human Gold 不足，整体仍为 PARTIAL |

## 8. 优化路线图

### P0-1：把文献分类路由变成下游执行门控

**问题**：分类 v2 已有 `PRIMARY_EXPERIMENTAL_ROUTE`、`REVIEW_SYNTHESIS_ROUTE`、`MODEL_ROUTE`、`METHOD_ROUTE`、`RESOURCE_ROUTE`、`SOFTWARE_ROUTE`、`BENCHMARK_ROUTE` 等，但上传 PDF 当前跳过发现与分类，直接进入实验设计抽取。

**方案**：在 Skill05/06 得到结构化全文后、Skill07 之前执行全文精化分类，并生成强类型 `LiteratureExecutionPlan`：

- primary experimental → ExperimentInstance extractor → Evidence → 可选 transfer/design；
- review → Mechanism/strategy synthesis，禁止伪装为 paper-reported experiment；
- method/software/benchmark → architecture/evaluation extractor；
- resource/database → dataset/schema/provenance extractor；
- conflict/unknown → human review，不得进入 K-12 proposal。

**验收**：本次两篇参考 PDF 不再产生培养时间、重复数或 K-12 湿实验建议；两篇分别进入 BENCHMARK/METHOD 与 RESOURCE/DATABASE 路由。

### P0-2：实现 Evidence Gap Driven Retrieval

新增 `EvidenceNeed`：

```text
need_id, decision_node_id, claim_or_hypothesis_id,
question_type, missing_relation, required_source_type,
required_context, criticality, stop_rule, status
```

循环为：候选机制链 → coverage/contradiction/context/quantity 检查 → 生成最小 EvidenceNeed → 路由到论文/数据库/模型/工程记忆 → 更新 claim graph → 再评估。

停止条件应综合：关键 claim 已覆盖、剩余 gap 对决策不敏感、新信息边际收益低、预算上限或需要人工/实验，而不是固定 8 轮。

### P0-3：强制 Evaluate → Reject/Rank → Human Select → ValidationPlan

把当前已有 evaluator、Pareto、counterfactual 和 Build/Test Planner 设为 governed required stages。没有 evaluator 结果不得显示“推荐”；没有 selected candidate 不得进入 planning；没有 controls、replicates、conditions、readouts、units、decision rule、failure signature 的 ValidationPlan 不得进入 build-ready。

### P0-4：Observation grounding 与候选特异定量模型

Data Sufficiency Gate 必须验证项目范围的 Observation ID、QC、条件、时间点和 baseline reference 真实存在。模型层从 `e_coli_core + biomass` 升级为与目标产物、培养基、碳源和候选干预一致的 GEM；至少持久化 baseline vs candidate 的 growth、product flux、FVA、关键通量、infeasibility、模型版本和假设。

### P1-1：建设两层 Historical Engineering Memory

- **Bronze prior**：导入 ELISER CSV/TTL，保留粗粒度、噪声和来源限制；只参与召回与先验排序。
- **Gold/Silver instance memory**：由 WAVE 重新核验全文，形成 Publication → ExperimentInstance → StrainVariant → InterventionSet → Condition → Outcome → Evidence。

对共现模块计算时间、宿主、产物、方向和全文可得性分层统计。Design Prior 必须与 evidence strength、project applicability、mechanistic plausibility 分开呈现。

### P1-2：把 Mechanism Synthesis 固化为强类型对象

新增不可变 `DiagnosisFinding`：observation refs、constraint hypothesis、causal graph、support/against、confidence derivation、unresolved alternatives、engineering consequence、validation need。候选保存 `diagnosis_finding_ids`，形成可查询的 Observation→Finding→Intervention→Evaluation trace。

### P1-3：段落/表格/图注感知的混合检索

索引单元至少区分 title、abstract、methods、results、discussion、table、figure_caption、supplement、database_record、DDR、engineering_rule。BM25 负责基因/突变/数值/菌株，dense 负责机制语义，RRF 或学习排序融合；Results 与 Methods 的权重和可主张范围必须高于 Discussion 推测。

### P1-4：定量信息的语义角色与单位系统

不能只抽取数字，必须绑定：数值—单位—对象—菌株版本—条件—时间点—测量类型—统计角色。增加防串线规则，区分 system benchmark 的 `n=120`、运行耗时 `2 min` 与湿实验 replicate/time；对 titer/yield/productivity 和 batch/fed-batch 建立显式类型。

### P1-5：重新设计专家 Agent benchmark

至少覆盖：

- factual/quantitative extraction；
- experiment-instance attribution；
- multi-hop causal reasoning；
- counterfactual context change；
- competing-constraint ranking；
- evidence deletion sensitivity；
- contradiction handling；
- candidate-specific FBA consistency；
- falsifiability/validation plan；
- failure-result belief update；
- temporal holdout 与后发表论文回测。

核心指标不是单一 answer accuracy，而是 critical false support、claim coverage、attribution precision/recall、calibration、selection regret、validation discriminability 和 evidence-cost efficiency。

### P2：工程与产品完善

1. 建立数据 release manifest、schema version、哈希、依赖版本和 README—制品契约测试。
2. 统一 Literature Discovery、Paper Extraction、Knowledge UI 三套旁路，复用候选、缓存、来源状态与 provenance。
3. 将 GET 轮询触发 DDR 入库改为工作流完成事件驱动，并保留不可变版本链。
4. 建立 Context Budget Manager，避免“检索越多越好”。
5. 前端明确显示：事实、归纳、模型预测、AI 假设、历史先验；同时显示未完成的 required next action。
6. 对延迟、token、模型调用和检索轮次做项目级预算与收益审计。

## 9. 推荐实施顺序与阶段验收

### 第一阶段：2 周，修正错误路由与伪实验

- 接通全文分类 → LiteratureExecutionPlan → 下游 gate；
- 加 system benchmark/resource paper 回归集；
- 修正来源标签导致的 frontend adapter failure；
- 禁止非 primary experimental 文献进入 K-12 proposal。

验收：本次两份 PDF 全链路完成且不生成伪湿实验字段。

### 第二阶段：3–4 周，完成项目级专家闭环

- Observation-grounded gate；
- 强制 evaluator、selection、counterfactual、ValidationPlan；
- 建立 typed DiagnosisFinding；
- 用一个色氨酸项目完成 candidate-specific GEM/FBA 回放。

验收：目标项目出现真实 Observation、evaluation、selected/rejected、ValidationPlan 和 baseline-vs-candidate quantitative result。

### 第三阶段：4–6 周，动态证据与工程记忆

- EvidenceNeed 与动态补检索；
- ELISER Bronze import；
- 选 30–50 个芳香族氨基酸案例做 WAVE instance-level Gold/Silver；
- 建 Design Prior calibration 与负结果召回。

验收：对留出项目，动态检索比单次检索减少关键证据缺口；prior 不会在 context mismatch 时提升为直接证据。

### 第四阶段：持续，封闭评测与发布门

- 扩展 human ExperimentInstance/DDR Gold；
- 时间切分与 sealed holdout；
- critical false support 必须为零或低于预设阈值；
- 只有完整项目闭环和 human-reviewed Gold 达标后，Release Gate 才从 PARTIAL 升为 PASS。

## 10. 最值得保留的设计原则

1. **Prior 不是 Recommendation。**
2. **一致不等于支持，缺失不等于阴性。**
3. **模块存在不等于项目完成。**
4. **证据必须绑定具体实验实例与上下文。**
5. **推荐必须能被反预测和判别实验推翻。**
6. **定量模型结果必须说明模型域、边界条件和适用性。**
7. **失败实验先做数据与执行归因，再进入生物学学习。**
8. **Agent 的价值不是生成更多方案，而是更快排除错误方案并选择信息增益最高的下一步。**

## 11. 本次自动提取回放状态

- 处理 PDF：2；解析/清洗成功：2；实验设计对象生成：2。
- 证据检查：12 个 reported claims 均带 evidence reference。
- 自动 QC：`REVIEW_REQUIRED`；23 个 unknown values。
- 最终状态：`FAILED`，错误位于 `skill13_frontend_adapter`，原因是 AI/literature content 缺少有效 source label。
- 治理：review pending、publication blocked；任何自动生成的工程方案都不应视为已批准或可执行计划。

该失败不是本次分析的旁枝，而是最直接的产品证据：当前 schema 和证据 gate 能发现问题，但前置任务类型识别与路由不足，导致系统先生成了不该生成的对象，再在末端阻断。优化方向应从“末端纠错”前移到“入口正确分流”。

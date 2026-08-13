# Skill07 → Skill08 Handoff 正式技术审计报告

审计日期：2026-08-12  
审计范围：`harness/paper_extraction/` 中 Skill07、Skill08、调度器、artifact、schema、provenance、DDR/规则知识层与相关测试  
执行约束：本轮只审计，不重构 Skill08；除本报告外未修改代码。

## 1. 执行结论

| 问题 | 结论 | 核心原因 |
|---|---|---|
| Q1：Skill08 是否是真正独立的 Evidence Verification Engine？ | **NO** | 它会重新读取 clean document 并生成新 EvidenceRecord，具备独立检索的雏形；但只有定位存在性与字符串包含式支持检查，没有实验归属验证和真正语义蕴含验证，并且会修复 Skill07 schema、改写事实字段和 epistemic state。 |
| Q2：Skill07 → Skill08 是否可安全进入 Knowledge Representation？ | **NO** | handoff 丢失 Skill07 的准入标志和 artifact 身份；多论文索引可能错配；Skill08 provenance 不足；DDR 自动入库直接读取 Skill07 输出而非 Skill08 verified artifact；规则候选可继续蒸馏。 |

当前架构不是“完全没有验证”，而是一个**局部独立、边界不安全、验证深度不足的 evidence binder**。在进入知识表示层前应设置硬门禁。

## 2. 当前真实数据流

```text
CleanDocumentArtifact (Skill06)
    ├── clean_document_artifact ─────────────────────────────┐
    └── Skill07 / Poe-Code-CLI 抽取                           │
            ↓                                                │
       Result envelope                                       │
       {status, output, provenance,                           │
        eligible_for_evidence_verification}                   │
            ↓ WorkflowEngine._update_context()                │
       仅保留 output 到 context.skill07                       │
       provenance 另存到 context.skill07_provenance           │
       status / eligibility / artifact_id 未进入 handoff       │
            ↓ WorkflowEngine._inputs()                        │
       zip(context.skill07, context.skill06)                  │
            ↓                                                │
       Skill08 {skill07_output, clean_document_artifact} ←────┘
            ↓
       deepcopy(fields) 后检索、字符串匹配、状态改写
            ↓
       EvidenceArtifact
       {literature_experiment, evidence_linked_design,
        evidence_map, coverage, conflicts}
            ↓
       Skill09 / Skill10 / Skill11 / Skill12 / frontend

并行旁路：
WorkflowEngine._report().experimental_designs = context.skill07
            ↓
ensure_task_saved_as_evidence()
            ↓
DDR Knowledge Representation（直接使用 Skill07，而非 Skill08）
            ↓
rule_distillation（可生成 pending rule）
```

关键实现证据：

- Skill07 明确输出 `eligible_for_evidence_verification`：成功为 `true`，验证失败或输入失败为 `false`（`opus_extractor.py:833-877, 958-993`）。
- 工作流只把每个 result 的 `output` 收入 context，并把 provenance 单独存储（`workflow/engine.py:211-217`）。
- Skill08 输入仅由 `skill07_output` 与 clean artifact 组成，不含状态、eligibility 或 Skill07 artifact ref（`workflow/engine.py:157-159`）。
- 最终报告公开的 `experimental_designs` 直接来自 Skill07（`workflow/engine.py:268-271`）。
- DDR 自动保存同样直接遍历 `experimental_designs`（`ddr_converter.py:1851-1885`），并未要求 Skill08 verified artifact。

## 3. 输入输出 schema 审计

### 3.1 Skill07

Skill07 已形成三层合同：

- runtime schema：`schemas/skill07_output.schema.json`；
- semantic contract：`contracts/skill07_semantic_contract.md`；
- deterministic rules：`contracts/skill07_validation_rules.yaml`。

其中已经明确：

- `status ∈ {reported, inferred, unknown}`，applicability 为独立维度；
- `field_metadata.evidence_role` 必须为 `candidate`；
- Skill07 不得输出 verified/approved evidence；
- `generalizable_rule` 只是 `single_paper_rule_candidate`；
- Skill08 应执行 existence、attribution、semantic-support 三类独立检查。

这是正确且清晰的上游冻结语义。

### 3.2 Handoff

当前没有正式 Handoff schema。实际传输形态只是：

```json
{
  "skill07_output": {},
  "clean_document_artifact": {}
}
```

`skill08/interface.json:5-11` 只要求两个 generic object，没有约束：

- Skill07 contract/schema/validation-rules version；
- Skill07 status 与 `eligible_for_evidence_verification`；
- source Skill07 artifact id/hash；
- paper identity 一致性；
- candidate evidence role；
- validation report/self-check。

因此接口层无法拒绝一个结构部分正确、语义验证失败或来源错配的输入。

### 3.3 Skill08

Skill08 输出接口只列出五个宽泛对象（`interface.json:13-21`），没有可执行的独立 JSON Schema，也没有定义：

- `verification_status` 的受控词表；
- candidate anchor → verified evidence 的关系；
- 原始 claim/epistemic state 的不可变副本；
- attribution verdict；
- verified/unsupported/unresolved/conflicted 的区分；
- DDR candidate 的验证结果；
-完整 provenance 链。

结论：Skill07 schema 已升级，但 Skill08 与 Handoff schema 尚未同步，存在明显 contract drift。

## 4. 职责边界审计

### 4.1 符合边界的部分

- Skill08 确实重新读取 clean JSON，构造自己的文档索引，而不是直接相信 Skill07 的 evidence id（`skill.py:44-56`）。
- 它优先解析 candidate id，失败后检索全文、图表和 supplement（`evidence_retriever.py:10-34`）。
- 它生成新的 EvidenceRecord、locator、quote hash 和 clean artifact hash（`skill.py:95-109, 230-249`）。
- 它不会直接写回磁盘上的 Skill07 artifact；`deepcopy` 避免了 Python 对象原地覆盖（`skill.py:57`）。

### 4.2 越界部分

1. **Schema repair 越界。** 对裸值自动包装，并把非空裸值定义成 `reported`（`skill.py:58-70`）。Skill08 因而替 Skill07 猜测 epistemic state，而不是拒绝非法 handoff。
2. **事实与状态改写越界。** 找不到支持时将原字段整体替换为 `{value:null,status:unknown}`（`skill.py:78-93`）。这不是 verification verdict，而是覆盖候选事实。
3. **workflow 事实改写。** 无 evidence 时把 reported step 改为 unknown，并清空 operation（`extension/workflow_binding.py:1-12`）。
4. **变量再推断。** 变量状态无论上游为何均被重设为 `inferred` 或 `unknown`，并可能清空值（`extension/variable_binding.py:7-22`）。这已进入知识抽取/推断职责。
5. **design logic 改写。** 无绑定 evidence 时清空 question/hypothesis/measurement（`extension/logic_binding.py:1-16`）。

正确做法应是保留 Skill07 candidate 原貌，另附 Skill08 的 verification verdict；不应把“未验证”伪装成“上游从未知道”。

## 5. Evidence Ontology 审计

Skill07 已显式声明 evidence role 为 `candidate`（schema `fieldMetadata.evidence_role`；semantic contract 第 4 节）。Skill08 虽生成新的 `ev_XXXXX` 记录，但输出中没有 `evidence_role: verified` 或 `verification_status`，也没有保存 candidate anchor 与 verified evidence 的逐条映射。

当前只能从“记录由 Skill08 生成”推断其意图是 verified；机器无法从 schema 证明这一点。与此同时，`extraction.method` 命名为 `provisional_id_then_semantic_retrieval`（`skill.py:243-248`），但实现只做 lexical substring matching，“semantic”命名高于实际能力。

结论：**概念文档区分了 candidate/verified，运行时 artifact 没有严格表达该区分。**

## 6. Evidence Verification 深度

| 层级 | 当前能力 | 判定 |
|---|---|---|
| Level 1：Existence | candidate paragraph id 可在 clean document index 中解析；生成 evidence id 后 validator 检查引用可解析（`evidence_retriever.py:10-19`; `validator.py:13-15`）。但 fallback 检索得到的任意文本命中也会被接受。 | **部分达到** |
| Level 2：Attribution | EvidenceRecord 写入当前 paper/artifact id，但没有验证 candidate source attribution、paper identity、experiment id、current article vs background citation，也没有检查段落是否属于对应 ExperimentInstance。 | **未达到** |
| Level 3：Semantic entailment | `supports_value` 把结构递归拆成字符串原子，要求各原子是 quote 的子串或少量 alias；没有否定、比较方向、单位、条件范围、主体、因果关系、实验归属或蕴含判断（`evidence_validator.py:11-56`）。 | **未达到；仅弱 lexical support** |

综合等级：**Level 1（部分）+ lexical support heuristic**，不能宣称 Level 2 或 Level 3。

额外风险：复杂字段中的每个字典值都会成为 atom。即使词都出现在若干 quote 的拼接文本中，也不能证明这些词共同支持同一个 claim；反之，合理释义因未逐字出现会被误降级。

## 7. Epistemic State 审计

Skill07 合同正确区分 `reported / inferred / unknown`，并把 `not_applicable` 放在独立 `applicability_status` 中（Skill07 schema `:84-112`；semantic contract 第 5 节）。

Skill08 的问题：

- `reported → unknown`：直接覆盖字段，且没有独立 verification status（`skill.py:89-93`）；
- bare value → reported：对非法 schema 猜测状态（`skill.py:65-70`）；
- inferred field：也进入相同检索流程，但 output validator 的 quote-support 检查只覆盖 `reported`（`validator.py:16-20`），没有验证 inference method/rationale 与 evidence 是否相容；
- 新建的 `unknown_field()` 没有 `applicability_status` 和 `inference`（`schema.py:18-23`），与当前 Skill07 field schema 发生漂移；
- 成功绑定后把 `extraction_method` 改为 `hybrid`（`skill.py:108-109`），而 Skill07 schema 允许值中没有 `hybrid`，且它混淆了“候选抽取方法”与“验证方法”。

结论：epistemic state **未被不可变保留**，且验证结果与知识状态未正交建模。

## 8. DDR Handoff 审计

Skill07 的 DDR annotation 已包含 decision type、Q1/Q2/Q3 gate、reason nature 和单篇 rule candidate，并由 Skill07 validator 做候选层规则检查。这部分属于候选知识抽取，语义清晰。

Skill08 当前：

- 不读取或验证 `experimental_design_object.experiments[].ddr_annotation`；
- 不验证 Q1/Q2/Q3 所引用的当前论文证据；
- 不验证“论文是否报告该 decision”，也不产生 DDR verification verdict；
- 不会直接把 candidate 改名成 verified rule，但其输出也没有携带候选 DDR 的验证结果。

更严重的是，知识层绕开 Skill08：`ensure_task_saved_as_evidence()` 从 workflow report 的 `experimental_designs`（Skill07）直接构建并自动保存 DDR（`ddr_converter.py:1851-1885`）。随后 `/rules/distill?write=true` 可把符合启发式条件的 DDR rule 写入规则库，状态虽为 `pending`，但其来源不是 Skill08 verified evidence（`rule_distillation.py:75-131`; API `paper_extraction.py:317-325`）。

结论：**DDR candidate 没有经过 Skill08 evidence verification 就能进入 Knowledge Representation。** 人工复核提示和 `pending` 状态降低了风险，但不能替代入口硬门禁。

## 9. Provenance 连续性审计

| 必需项 | 当前状态 |
|---|---|
| `source_skill07_artifact_id` | **缺失** |
| `source_skill07_hash` | **缺失**；`input_hash` 是整个 Skill08 request hash，不是稳定、显式的 Skill07 artifact hash |
| `skill08_version` | **部分具备**；字段名为 `skill_version` |
| `verification_rules_version` | **缺失** |
| `verification_timestamp` | **缺失**；构造器有 clock，但未写入 result/evidence |
| clean document artifact id/hash | **具备**（`skill.py:53-54, 198-203`） |
| candidate → verified 映射 | **缺失** |

Workflow artifact 自己有 `artifact_id/version/created_time/content/provenance`（`workflow/artifacts.py:11-18`），但它是在 Skill08 完成后才生成；Skill08 请求中没有上游 Skill07 artifact ref，所以无法回答“这条 verified evidence 来自哪个确切 Skill07 artifact”。

## 10. Failure Handling 与调度门禁

### 10.1 明确问题

- Skill07 验证失败返回 `needs_review + output + eligible=false`（`opus_extractor.py:958-975`）。工作流只在 terminal/retryable/cancelled 时停止，`needs_review` 继续执行（`workflow/engine.py:42-51`）。
- Handoff 不传 eligibility；Skill08 也不检查，所以 schema/semantic invalid 的 Skill07 输出可被 Skill08“修复”后继续。
- workflow 将 `needs_review` 映射为 `REVIEW_REQUIRED`，但运行结束仍标记 `COMPLETED`，注释明确其为 advisory（`workflow/engine.py:52-64`; `state.py:1-4`）。

### 10.2 多论文错配风险（P0）

`_update_context()` 使用 `[r["output"] for r in results if output is not None]` 压缩列表（`workflow/engine.py:211-217`），Skill08 再用 `zip(context.skill07, context.skill06)`（`:157-159`）。若论文 A 的 Skill07 返回 `needs_review + output=None`，而论文 B 成功，则 B 的 Skill07 输出会移到索引 0 并与 A 的 clean document 配对。Skill08 随后可能从错误论文检索词面相似证据，造成跨论文 evidence contamination。

### 10.3 Review 状态继续向下游

Skill08 只有降级字段占全部字段超过 25% 或冲突超过 2 个才标记 `needs_review`（`skill.py:156-187`）；单个关键字段失败仍可 `succeeded_with_warnings`。Skill09、Skill10、Skill11 仍会消费这些输出。最终 Skill12 的 review 状态不阻断完成态。

## 11. Skill08 Contract Layer 评估

当前 `contracts/` 只有 Skill07 contract/rules，没有：

- `contracts/skill08_evidence_contract.md`；
- `contracts/skill08_validation_rules.yaml`。

两者**必须新增**，原因不是文档完整性，而是当前 Skill08 的以下关键语义没有单一、可执行来源：verification verdict、Level 1/2/3 标准、epistemic immutability、candidate/verified linkage、attribution、DDR 验证边界、failure severity 和 Knowledge gate。

Prompt 或 README 不能替代 validator。现有 `README.md` 还存在明显乱码，不能作为可靠合同来源。

## 12. 测试覆盖审计

现有测试覆盖了：Skill07 contract validator、成功/失败时 eligibility 标志、默认计划包含 Skill08、结果摘要消费 Skill08 fields、DDR/规则转换的一些行为。

未发现针对 Skill08 engine 的专门测试目录或以下边界测试：

- eligibility=false 必须阻断；
- Skill07 status/schema/semantic invalid 必须阻断；
- source Skill07 artifact/hash 连续性；
- candidate/verified role 与映射；
- reported/inferred/unknown/applicability 不被覆盖；
- current article/background citation attribution；
- experiment-level attribution；
-否定、方向、单位、范围和主体的 semantic entailment；
- 多论文一个无输出时不发生 zip 错配；
- 未 verified 的 DDR/rule candidate 不得进入 Knowledge Layer。

因此现有测试能证明 Skill07 门禁标志被生成，不能证明该门禁被调度器执行。

## 13. 风险排序

| 优先级 | 风险 | 影响 |
|---|---|---|
| P0 | Handoff 丢弃 eligibility/status，且多论文列表压缩后 zip | invalid candidate 可进入验证；严重时将 B 论文 claim 绑定到 A 论文原文 |
| P0 | DDR 自动入库绕开 Skill08 verified artifact | 未验证 candidate 可成为持久化知识和规则蒸馏来源 |
| P0 | Skill08 覆盖 Skill07 值和 epistemic state | provenance 与科学语义被污染，无法区分“原本未知”与“验证失败” |
| P1 | 无 Level 2 attribution 与真正 Level 3 entailment | 背景引用、错误实验、同词反义句均可能被视为支持 |
| P1 | 缺少 source Skill07 artifact/hash、规则版本和时间戳 | verified evidence 无法审计回确切候选 artifact |
| P1 | 无 Skill08 contract/rules/schema | 行为由实现细节定义，后续继续漂移 |
| P1 | DDR annotation 完全未验证 | Q1/Q2/Q3、reason nature、rule candidate 只停留在模型候选层 |
| P2 | 25% 阈值按所有字段而非关键字段 | 单个关键字段（如 strain/control/outcome）失败可能仅告警 |
| P2 | Skill08 专门边界测试缺失 | 关键污染路径无法通过 CI 防回归 |

## 14. Q1 / Q2 / Q3

### Q1：Skill08 是否是真正独立 Evidence Verification Engine？

**NO。**

它独立重读 clean document 并生成新 evidence record，因此不是纯粹转发器；但目前本质上是“候选定位 + 词面绑定 + 字段改写器”。它没有达到 attribution validation 与 semantic entailment validation，也没有以独立 verdict 保存上游 epistemic state，且承担了 schema repair、变量再推断和事实清空等 Skill07 职责。

### Q2：Skill07 → Skill08 是否可以安全进入 Knowledge Representation？

**NO。**

阻塞因素：

1. 调度器未执行 Skill07 eligibility gate；
2. 多论文 handoff 存在索引错配和跨论文污染风险；
3. Skill08 artifact 无法追溯到确切 Skill07 artifact；
4. candidate/verified 与 verification status 没有机器可判定的 schema；
5. Skill08 未验证 DDR annotation；
6. DDR 自动保存路径直接使用 Skill07 输出，绕过 Skill08；
7. Skill08 只达到部分 Level 1，无法支撑“verified knowledge”语义。

### Q3：下一阶段最高优先级 Top 5

1. **建立不可绕过的 Handoff Gate。** 传递完整 Skill07 result envelope 与 artifact ref；只接受 `status ∈ {succeeded, succeeded_with_warnings}`、`eligible=true`、required self-check 全通过、schema/contract version 兼容的输入。按 `paper_id/artifact_id` join，禁止压缩列表后按位置 zip。
2. **冻结非变异验证模型。** Skill08 不再修改 Skill07 candidate；输出 `{candidate_ref, original_value, original_epistemic_status, verification_status, verified_evidence_ids, failure_reason}`。未验证应是 `unsupported/unresolved/conflicted`，不是把上游改成 `unknown`。
3. **实现并版本化 Skill08 Contract。** 新增 `skill08_evidence_contract.md`、`skill08_validation_rules.yaml` 和严格 output schema，明确 candidate/verified ontology、E1/E2/E3、attribution、DDR 边界、关键字段失败策略和 Knowledge admission policy。
4. **把验证提升到至少 Level 2，并为 Level 3 建立保守判定。** 强制校验 paper/section/experiment/source attribution；语义验证要处理主体、否定、数值与单位、比较方向、条件范围和因果强度。无法可靠判定时进入 review，不得标记 verified。
5. **封闭 Knowledge/DDR 旁路并补齐 provenance + tests。** DDR 仅从通过门禁的 Skill08 verified artifact 构建；记录 `source_skill07_artifact_id/hash`、Skill08/version、verification-rules/version、timestamp 和 candidate→verified 映射；加入错配、epistemic immutability、DDR/rule gate 等回归测试。

## 15. Knowledge Admission 最低验收条件

在 Q2 改为 YES 前，至少应同时满足：

- Handoff schema 校验与 eligibility 硬门禁已生效；
- 每份 Skill08 artifact 可反查唯一 Skill07 artifact 与 clean document artifact；
- 所有 candidate 原值和 epistemic/applicability state 保持不可变；
- 每个 claim 有显式 verification status，verified 必须通过 existence + attribution + semantic-support；
- DDR candidate 有单独验证结果，rule candidate 不会被 Skill08 晋升为 rule；
- DDR/Knowledge 写入只接受合格的 Skill08 artifact；
- 多论文关联按稳定 identity 完成，不依赖压缩后的数组位置；
- 关键边界均有自动化测试并进入 CI。


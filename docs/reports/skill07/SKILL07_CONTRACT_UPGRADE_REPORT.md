# Skill07 Contract Architecture Upgrade Report

完成日期：2026-08-12  
目标：把 Skill07 从“Prompt + Schema + 分散 Python 判断”升级为带版本、可审计、可确定性验证的科学抽取契约运行时。

## 1. 修改前架构

Skill07 的科学语义分散在 System Prompt、`SKILL.md`、JSON Schema、`opus_extractor.py` 与 `ddr_converter.py` 中：

- JSON Schema 同时承担结构与部分语义约束，但没有契约版本。
- `unknown` 与 `not_applicable` 没有独立机器状态。
- `evidence_ids` 未显式声明为 Skill07 candidate，嵌套对象也可能误写 verified。
- `reason_nature` 在 Python 中存在多份不完整硬编码枚举。
- 规则候选缺少“工程决策 + tested scope + excluded scope”的完整门禁。
- `self_check.score` 容易被误解为科学质量评分。
- cache/provenance 不包含语义契约和验证规则版本。

详细审计见 `SKILL07_ARCHITECTURE_AUDIT.md`。

## 2. 修改后架构

```text
System Prompt + full Skill07 rules + semantic contract + runtime schema
                              |
                              v
                      model candidate output
                              |
                              v
                additive legacy normalization
                              |
                              v
              JSON Schema structural validation
                              |
                              v
          YAML-driven deterministic semantic validation
             | epistemic/applicability separation
             | candidate evidence role integrity
             | article/graph/coverage integrity
             | DDR decision and bounded-rule gates
                              |
                              v
              cache + versioned/hash provenance
                              |
                              v
                 Skill08 independent verification
```

JSON Schema 只负责可静态表达的结构约束；`skill07_validation_rules.yaml` 成为机器枚举与跨字段语义规则的单一事实来源；Python 负责执行这些确定性规则；语义契约文档负责定义科学对象和边界。

## 3. 新增文件

- `SKILL07_ARCHITECTURE_AUDIT.md`：重构前的数据流、漂移点与兼容策略审计。
- `harness/paper_extraction/contracts/__init__.py`：契约运行时公共接口。
- `harness/paper_extraction/contracts/runtime.py`：YAML 加载、fail-closed 自检、理由值规范化。
- `harness/paper_extraction/contracts/skill07_semantic_contract.md`：版本化科学语义契约。
- `harness/paper_extraction/contracts/skill07_validation_rules.yaml`：版本化机器验证规则。
- `tests/paper_extraction/test_skill07_contract.py`：7 项契约架构测试。
- `SKILL07_CONTRACT_UPGRADE_REPORT.md`：本报告。

## 4. 修改文件

- `harness/paper_extraction/schemas/skill07_output.schema.json`
  - Schema ID 升级至 2.1.0。
  - 新增顶层 `contract_version`。
  - 每个科学字段新增 `applicability_status`。
  - `field_metadata.evidence_role` 固定为 `candidate`。
- `harness/paper_extraction/opus_extractor.py`
  - 注入并记录语义契约与规则版本。
  - cache identity 纳入契约/规则内容哈希。
  - 语义、evidence、DDR 验证改由 YAML 规则驱动。
  - 新增 verified evidence 禁止门禁和完整规则候选 scope 门禁。
  - legacy 输出采用加法式保守迁移。
  - `self_check` 改为计数与关键失败清单。
- `harness/paper_extraction/ddr_converter.py`
  - `reason_nature` 有效值、别名与规则资格统一读取 YAML。
  - 旧中文值继续兼容，规则判断使用 canonical value。
- `tests/paper_extraction/test_unified_extraction.py`
  - fixture 和断言升级到新契约。
- `pyproject.toml`、`requirements.txt`
  - 显式声明 `PyYAML>=6.0`。

## 5. Ontology 设计

语义契约区分五类核心对象：

1. biological object：宿主、菌株、构建体、遗传元件及其身份/谱系；
2. experiment：独立实验实例、干预、条件、对照、读出和结果；
3. claim：reported、inferred、unknown 的知识状态；
4. evidence：Skill07 只生成 candidate anchor，Skill08 才能生成 verified evidence；
5. decision/rule：工程决策与验证/测量/背景分离，单篇论文最多产生有边界的 rule candidate。

`applicability_status = applicable | not_applicable | uncertain` 与 `status = reported | inferred | unknown` 正交。`not_applicable` 必须保持 `unknown + null + empty evidence`，因此不会伪装成“已知不存在”，也不会污染普通未知状态。

理由性质采用 canonical machine vocabulary：

- `mechanistic_inference`
- `literature_analogy`
- `resource_available`
- `screening_derived`
- `evolution_derived`
- `rationale_not_reported`
- `post_hoc_rationalization_uncertain`

旧中文枚举通过 YAML alias 映射继续兼容。

## 6. Validator 设计

验证规则在加载时 fail closed：缺少关键段、版本不匹配或 canonical 理由集合不完整会直接报错，不会静默降级。

主要确定性门禁：

- epistemic：reported 必须有值、candidate evidence 与定位；inferred 必须有方法、理由、支持证据和定位；unknown 必须为空。
- applicability：not_applicable 不改变知识状态；uncertain 只允许 unknown。
- evidence：Skill07 全树禁止 `verified|approved` 角色以及 `verified_evidence_id(s)` 键。
- DDR：decision type、Q1/Q2/Q3 gate 和 reason nature 从 YAML 读取。
- rule candidate：仅允许 `engineering_decision`，理由必须是 mechanism/analogy，同时必须有非空 tested scope 与 excluded scope。
- provenance：记录 semantic contract/rules 的版本与 SHA-256；任一内容变化都会使 cache key 失效。
- self-check：输出 `required_checks`、`passed`、`failed`、`critical_failures`，不再输出伪质量 `score`。

## 7. 测试结果

- 聚焦契约与统一抽取测试：`21 passed`。
- 完整 paper-extraction 回归：`123 passed, 1 warning`，包括原有 116 项和新增 7 项。
- 最终契约测试复跑：`7 passed`。
- 修改模块静态编译：通过。
- 全仓 `python -m pytest -q`：在 124 秒执行上限内未完成，未产生提前失败输出；因此不声明全仓套件通过。

新增测试覆盖：

1. `not_applicable` 与 `unknown` 正交；
2. YAML、validator、DDR converter 的 `reason_nature` 枚举一致；
3. rule candidate 缺 tested/excluded scope 必须失败；
4. Skill07 candidate evidence 不可标记 verified；
5. provenance 包含契约/规则版本和哈希；
6. `self_check` 不含 score；
7. legacy 输出仅做加法式、保守迁移。

## 8. 已知限制

- 本次保留完整 `SKILL.md` 注入。Skill07 的 core、DDR、parameter、evidence 规则存在跨章节依赖；在没有按论文类型和实验复杂度分层的质量基准前条件加载，可能漏掉意外出现的实验或参数规则，违背“科学真实性优先”。契约/规则版本化先消除了语义漂移，Prompt 拆分留给可量化基准阶段。
- 嵌套 `experimental_design_object` 为保持历史输出兼容仍较宽松；关键不变量由递归语义验证器兜底。
- 字段名 `evidence_ids` 为兼容保留，角色通过 `field_metadata.evidence_role=candidate` 和全树 verified 禁止门禁明确。
- 旧输出若只有 `unknown` 而没有明确不适用说明，会迁移为 `applicability_status=uncertain`，不会猜测为 not_applicable。
- 未执行真实外部模型的端到端论文抽取；本次验证覆盖本地契约、规范化、验证、缓存和回归行为。

## 9. 下一阶段建议

1. 建立按论文类型、实验数量、参数密度分层的 golden set，对 full Skill 注入与 `core + routed modules` 做召回率、证据正确率和 token 成本对照。
2. 在质量无下降后拆分 `SKILL07_core_rules.md`、`SKILL07_DDR_rules.md`、`SKILL07_parameter_rules.md`，并把加载模块列表纳入 provenance/cache key。
3. 为 `experimental_design_object` 建立版本化子 Schema，逐步把当前递归语义门禁前移为结构约束，但保留 Python 跨字段验证。
4. 在 Skill08 handoff 中显式生成 candidate→verified 映射表，并加入跨阶段契约测试。
5. 在无外部服务的 CI profile 中固定 paper-extraction 套件，在较长时限的集成 profile 中完成全仓回归。


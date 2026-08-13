# Skill07 Human Gold Annotation Guidelines

Gold 只能由明确的人类标注、独立复核和裁决建立。A、G、Codex、deterministic comparator 和 Silver union 都不是 Gold。先阅读 source；初次判断完成前保持 A/G 隐藏。

## ExperimentInstance decision rules

ExperimentInstance 是具有可辨识对象、操作/暴露、条件与预期 readout 的执行单元。仅有背景描述、分析解释或普通 Methods 步骤不是独立实验。改变 strain/construct 后在同一设计中测量结果通常是一项实验；科学问题、操作链或 assay 独立时可分开。多阶段工程 campaign 用 parent/subexperiment；相同干预的条件矩阵可作为 experiment series。边界无法可靠决定时选 `UNCERTAIN`，不得为了匹配 A/G 强行拆并。

合并：科学对象、干预、目标 readout 和因果问题相同，仅为重复条件/描述。分拆：存在独立干预、对象、验证问题或可独立支持的结果。父子：子 assay/迭代服务于 campaign，但本身有独立执行和 readout。重复 Methods 步骤不得自动拆成实验。

## Action, observation and interpretation

- action：实际实施的构建、处理、培养、选择或测定；implemented 不等于 measured。
- observation：仪器/assay 直接读数；`MEASURED`。
- analysis：统计、归一化或计算；派生值标为 `CALCULATED`。
- author interpretation：作者明确解释；不得改写为直接测量。
- reviewer interpretation/inference：人工推断，必须保持相应 epistemic status。
- rationale/rule：为什么做与可迁移结论；scope 只能覆盖来源支持范围。

相关或共现不能标为 causal，除非来源明确提供干预和因果支持。负结果区分 no significant difference、below detection、below quantification、failed experiment 和 null result；不得改写成数值零或“无效”。

## Evidence policy

Direct evidence 直接陈述/显示 claim；supporting context 只提供对象或方法背景；indirect 需多个锚点联合；insufficient 不能支持 claim。每个 critical directly-reported claim 必须绑定可验证 evidence。允许多 paragraph、figure/table/caption、Methods+Results 的 `MULTI_ANCHOR`。Supplement 被引用但缺失时设置 `availability=UNAVAILABLE`，不得猜测内容。摘录保持短小并保存 fingerprint。

## Workflow

1. ANNOTATOR_A/B 各自 source-first 建立完整 inventory，包含 A/G 均遗漏的实验。
2. 创建 atomic claims，再绑定 evidence；解决或显式标记 granularity/object ambiguity。
3. 勾选 `SOURCE_COVERAGE_REVIEW_COMPLETE`，验证并提交独立复核。
4. ADJUDICATOR 查看 source、两份版本、diff/evidence，不预选赢家；记录 rationale、changed fields 和 prior revisions。
5. 仅 G0-G7 全部通过后创建新版本 frozen release。任何修订不得覆盖旧 release。

Workbench：`/skill07-gold`。CLI 示例：

```powershell
python tools/build_skill07_gold_packages.py
python tools/skill07_gold_cli.py validate-draft GOLD-P01 --role ANNOTATOR_A
python tools/skill07_gold_cli.py agreement GOLD-P01
python tools/skill07_gold_cli.py adjudication GOLD-P01
python tools/skill07_gold_cli.py readiness
python tools/skill07_gold_cli.py freeze skill07-gold-v1.0.0 --actor ADJUDICATOR-001
python tools/skill07_gold_cli.py verify skill07-gold-v1.0.0
```

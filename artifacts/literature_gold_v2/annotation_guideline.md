# Literature Verification Gold Annotation Guideline

状态：`GOLD_PENDING_HUMAN_ANNOTATION`。机器判断、seed fixtures 和本轮 spot check 均不得冒充 human gold。

两位标注者独立填写 `literature_verification_gold_template.json` 的 A/B 区；看到分歧后才由第三人填写 `adjudicated`。标注者必须查看正确全文并记录页码/section/原文证据。

## Labels

- `identity_correct`：PDF DOI/题名/作者与候选一致。
- `host_relation`：`K12_EXACT`、`K12_DERIVATIVE_EXPLICIT`、`ECOLI_NON_K12`、`ECOLI_UNRESOLVED`、`NON_ECOLI`。不能凭常识推定 lineage。
- `target_product_correct`：L-tryptophan 是实际工程目标，而非底物、前体、旁产物或背景词。
- `primary_research`：本文实施实验；review、纯模型、引用他人结果均为 false。
- `engineering_intervention_present`：本文实际实施 knockout/overexpression/promoter/attenuator/transport/precursor/cofactor/ALE/process intervention。
- `experimental_validation_present`：有本文 measured titer/yield/productivity/fold-change 或明确培养对照结果。
- `eligibility_label`：以上身份、host/product、实际 intervention、实验验证与 primary research 都满足才为 true。
- `relevance_grade`：direct/supporting/mechanistic/background/not_eligible/data_required。

证据不足填 null/unknown；不得根据标题猜 strain，根据 review 引用猜实验，或因有 PDF 推断科学相关。评价脚本 `harness/literature_verification/gold.py` 可计算 confusion matrix、precision/recall/F1/specificity、Precision@K 与 nDCG；在无 adjudicated gold 时只返回 pending。

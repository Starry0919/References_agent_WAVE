# Calibration Runner Report

运行：`python scripts/run_literature_verification_calibration.py --gold literature_verification_gold_batch_v1.json`。

当前输出`GOLD_PENDING_HUMAN_ANNOTATION`、labeled=0，不伪报指标。完成人工裁决后现有runner计算confusion matrix、precision/recall/F1/specificity与已有ranking metrics。Threshold字段已参数化；完整kappa、threshold sweep与slice输出仍是P0后续加固项。

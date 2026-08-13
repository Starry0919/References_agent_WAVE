# PDF Identity v1.1 Calibration Report

v1.1将单一 SequenceMatcher升级为 DOI exact 0.50、title token recall 0.30、author overlap 0.10、venue 0.06、year 0.04。阈值参数化：VERIFIED≥0.72、PROBABLE≥0.48；其余 REVIEW_REQUIRED/INSUFFICIENT。明确其他 DOI + 极低标题重合构成硬冲突并 MISMATCH。

现有10篇 acquisition manifest中5个 PDF、2 VERIFIED、3 INSUFFICIENT/待复核。样本没有人工 identity gold，因此不宣称 accuracy；threshold 保持保守并等待标注校准。
